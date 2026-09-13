#!/usr/bin/env python3
"""Two-root inversion of CSNS ion-mode widths from one identified species.

For a fixed bunch charge and cage voltage the collected width of an
identified residual-gas ion (H₂O⁺ or N₂⁺) has a minimum at σ₀*(P). A
measured width above that minimum therefore has two candidate sizes: a
small root σ_S ≤ σ₀* (the core hypothesis) and a large root σ_L ≥ σ₀*
(the painted-beam hypothesis). Both are returned. The magnet is not
installed, so the electron mode is read at B = 0, where its width is
itself space-charge biased and not a size on its own; it confirms a
root by consistency: each ion root predicts a B = 0 electron width
from the electron table at the same (N, V), and the root whose
prediction matches the measured electron width is kept. The second
identified species is an independent check, because a wrong root of
H₂O⁺ and a wrong root of N₂⁺ do not agree while the right roots do.

Summary CSVs only; no Virtual-IPM runs. Leave-one-out on the 1 mm
Block B (injection) and aligned I2 (extraction) tables.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from plot_conf import load_summary, plot_conf
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
PLOTS = ROOT / "plots"

SPECIES = (("ions", r"H$_2^+$"), ("h2o_ions", r"H$_2$O$^+$"), ("n2_ions", r"N$_2^+$"))
WORKING = (("h2o_ions", r"H$_2$O$^+$"), ("n2_ions", r"N$_2^+$"))
COLORS = {"ions": "b", "h2o_ions": "r", "n2_ions": "g"}
MARKERS = {"h2o_ions": "o", "n2_ions": "^"}
POWERS = (100, 200, 300, 500)
EMODE_B_GS = 0
EMODE_MARGIN_PCT = 5.0
EMODE_ACCEPT_PCT = 10.0
WALL_FRAC = 0.995
WALL_SIGMA_MM = 40.0


def _f(row: dict, key: str) -> float:
    return float(row[key])


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def injection_size_table() -> dict[tuple[str, int], dict[str, np.ndarray]]:
    """σ_0, σ_m, Δ, frac for injection Block B at B = 0, keyed (species, P)."""
    rows = load_summary(OUT / "csns_imode_size_summary.csv")
    out: dict[tuple[str, int], dict[str, np.ndarray]] = {}
    for slug, _lab in SPECIES:
        for power in (100, 200, 300, 400, 500):
            pts = sorted(
                (
                    _f(r, "sigma_x_mm"),
                    _f(r, "sigma_sc_on_mm"),
                    _f(r, "expansion_vs_no_sc_pct"),
                    _f(r, "detected_frac_on"),
                )
                for r in rows
                if r["species"] == slug
                and r["beam"] == "injection"
                and r["b_gs"] == 0
                and r["power_kw"] == power
            )
            if not pts:
                continue
            a = np.array(pts, float)
            out[(slug, power)] = dict(sigma0=a[:, 0], sigmam=a[:, 1], delta=a[:, 2], frac=a[:, 3])
    return out


def extraction_aligned_table() -> dict[tuple[str, int], dict[str, np.ndarray]]:
    """Aligned extraction I1/I2 at B = 0, 25 kV, centred, keyed (species, P)."""
    rows = load_summary(OUT / "csns_v2_summary.csv")
    out: dict[tuple[str, int], dict[str, np.ndarray]] = {}
    for slug, _lab in SPECIES:
        for power in (20, 50, 80, 100, 150, 200, 250, 300, 400, 500):
            pts = []
            for r in rows:
                if r.get("species") != slug or r.get("beam") != "extraction":
                    continue
                if r.get("b_gs") != 0 or r.get("power_kw") != power:
                    continue
                if int(r.get("voltage_kv") or 25) != 25:
                    continue
                if float(r.get("dx_mm") or 0) != 0 or float(r.get("dy_mm") or 0) != 0:
                    continue
                if r.get("block") not in ("I1", "I2"):
                    continue
                pts.append(
                    (
                        _f(r, "sigma_mm"),
                        _f(r, "sigma_sc_on_mm"),
                        _f(r, "expansion_vs_no_sc_pct"),
                        _f(r, "detected_frac_on"),
                    )
                )
            if len(pts) < 3:
                continue
            # unique σ_0 (I1/I2 overlap): keep the first
            uniq: dict[float, tuple] = {}
            for p in sorted(pts):
                uniq.setdefault(p[0], p)
            a = np.array(list(uniq.values()), float)
            out[(slug, power)] = dict(sigma0=a[:, 0], sigmam=a[:, 1], delta=a[:, 2], frac=a[:, 3])
    return out


def emode_size_table(beam: str, power: int, b_gs: int = EMODE_B_GS) -> dict[str, np.ndarray] | None:
    """Electron-mode σ_e(σ₀) at the field used to confirm the root (B = 0 until the magnet exists)."""
    rows = load_summary(OUT / "csns_emode_size_summary.csv")
    pts = sorted(
        (_f(r, "sigma_x_mm"), _f(r, "sigma_sc_on_mm"), _f(r, "expansion_vs_no_sc_pct"))
        for r in rows
        if r["beam"] == beam and r["b_gs"] == b_gs and r["power_kw"] == power
    )
    if len(pts) < 3:
        return None
    a = np.array(pts, float)
    return dict(sigma0=a[:, 0], sigmam=a[:, 1], delta=a[:, 2])


# ----------------------------------------------------------------------------
# two-root invert
# ----------------------------------------------------------------------------


def _branch_root(x_sigmam: np.ndarray, y_sigma0: np.ndarray, sigma_m: float) -> float:
    """Monotone-cubic invert of one branch; NaN outside the tabulated range."""
    order = np.argsort(x_sigmam)
    x, y = np.asarray(x_sigmam, float)[order], np.asarray(y_sigma0, float)[order]
    _, idx = np.unique(np.round(x, 9), return_index=True)
    x, y = x[idx], y[idx]
    if len(x) < 2 or sigma_m < x[0] - 1e-9 or sigma_m > x[-1] + 1e-9:
        return float("nan")
    if len(x) == 2:
        return float(np.interp(sigma_m, x, y))
    return float(PchipInterpolator(x, y)(sigma_m))


def fold_of(sigma0: np.ndarray, sigmam: np.ndarray) -> tuple[float, float, float]:
    """(σ₀*, σ_m,min) on the grid and the parabola-vertex σ₀ through the
    three lowest points (used when a measured width lies below the grid
    minimum, i.e. the beam is at the fold)."""
    imin = int(np.argmin(sigmam))
    lo, hi = max(imin - 1, 0), min(imin + 1, len(sigma0) - 1)
    idx = list(range(lo, hi + 1))
    vert = float(sigma0[imin])
    if len(idx) == 3:
        c = np.polyfit(sigma0[idx], sigmam[idx], 2)
        if c[0] > 0:
            vert = float(np.clip(-c[1] / (2 * c[0]), sigma0[lo], sigma0[hi]))
    return float(sigma0[imin]), float(sigmam[imin]), vert


def two_roots(sigma_m: float, sigma0: np.ndarray, sigmam: np.ndarray) -> tuple[float, float, float]:
    """Return (σ_S, σ_L, σ_fold) for a measured width on one species' table.

    σ_S is the root on σ₀ ≤ σ₀* (σ_m falls with σ₀), σ_L the root on
    σ₀ ≥ σ₀* (σ_m rises with σ₀). Either is NaN if the width is outside
    that branch's tabulated range. σ_fold is the vertex estimate to use
    when both are NaN because σ_m is below the tabulated minimum.
    """
    imin = int(np.argmin(sigmam))
    small = _branch_root(sigmam[: imin + 1], sigma0[: imin + 1], sigma_m)
    large = _branch_root(sigmam[imin:], sigma0[imin:], sigma_m)
    _s0, _sm, vert = fold_of(sigma0, sigmam)
    return small, large, vert


def select_root(
    small: float,
    large: float,
    fold: float,
    sigma_e: float,
    te_small: float,
    te_large: float,
) -> tuple[float, str, float]:
    """Keep the root whose predicted electron width matches the measured one.

    te_small / te_large are the B = 0 electron widths the electron table
    predicts for each root (NaN if the root lies outside that table).
    Returns (σ₀, branch, margin) with margin = |te_small − te_large| / σ_e
    in percent (NaN when only one prediction exists).
    """
    if np.isnan(small) and np.isnan(large):
        return fold, "fold", float("nan")
    if np.isnan(small):
        return large, "large", float("nan")
    if np.isnan(large):
        return small, "small", float("nan")
    ms = abs(te_small - sigma_e) if np.isfinite(te_small) else np.inf
    ml = abs(te_large - sigma_e) if np.isfinite(te_large) else np.inf
    margin = 100 * abs(te_small - te_large) / sigma_e if np.isfinite(te_small) and np.isfinite(te_large) else float("nan")
    if not np.isfinite(te_small) and not np.isfinite(te_large):
        return fold, "undecided", margin
    # only one root inside the electron table: accept it if it matches,
    # otherwise the other (unchecked) root is the consistent one
    if not np.isfinite(te_large):
        if ms <= EMODE_ACCEPT_PCT / 100 * sigma_e:
            return small, "small", margin
        return large, "large*", margin
    if not np.isfinite(te_small):
        if ml <= EMODE_ACCEPT_PCT / 100 * sigma_e:
            return large, "large", margin
        return small, "small*", margin
    if ms <= ml:
        return small, "small", margin
    return large, "large", margin


def _emode_predictor(emode: dict, exclude: float | None):
    """Monotone-cubic B = 0 electron width versus σ₀, with one grid point
    removed for the leave-one-out test; NaN outside the tabulated range."""
    s0, se = emode["sigma0"], emode["sigmam"]
    if exclude is not None:
        m = ~np.isclose(s0, exclude)
        s0, se = s0[m], se[m]
    f = PchipInterpolator(s0, se, extrapolate=True)
    step = float(np.min(np.diff(s0)))
    lo, hi = float(s0.min()) - step, float(s0.max()) + step

    def predict(x: float) -> float:
        # at most one grid step of extrapolation beyond the electron table
        if not np.isfinite(x) or x < lo - 1e-9 or x > hi + 1e-9:
            return float("nan")
        return float(f(x))

    return predict


def leave_one_out_two_roots(sigma0: np.ndarray, sigmam: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(sigma0)
    small = np.full(n, np.nan)
    large = np.full(n, np.nan)
    fold = np.full(n, np.nan)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        small[i], large[i], fold[i] = two_roots(sigmam[i], sigma0[m], sigmam[m])
    return small, large, fold


def _slope_at(sigma0: np.ndarray, sigmam: np.ndarray, s: float) -> float:
    """Central-difference dσ_m/dσ₀ at σ₀ = s (NaN if s is a grid end)."""
    i = int(np.argmin(np.abs(sigma0 - s)))
    if i == 0 or i == len(sigma0) - 1 or abs(sigma0[i] - s) > 1e-6:
        return float("nan")
    return float((sigmam[i + 1] - sigmam[i - 1]) / (sigma0[i + 1] - sigma0[i - 1]))


def invert_case(beam: str, power: int, slug: str, a: dict, emode: dict | None) -> dict:
    """Leave-one-out two-root invert of one (ring, power, species) table."""
    s0, sm, fr = a["sigma0"], a["sigmam"], a["frac"]
    # lost: ions hit the cage (not inverted). near-wall: everything is
    # collected but the width is within ~2.75 sigma of the 110 mm half-cage.
    lost = fr < WALL_FRAC
    near_wall = (sm > WALL_SIGMA_MM) & ~lost
    wall = lost
    small, large, fold_loo = leave_one_out_two_roots(s0, sm)
    fold_s0, fold_sm, fold_vertex = fold_of(s0, sm)
    n = len(s0)
    se = np.full(n, np.nan)
    te_small = np.full(n, np.nan)
    te_large = np.full(n, np.nan)
    margin = np.full(n, np.nan)
    pick = np.full(n, np.nan)
    which = np.empty(n, dtype=object)
    for i in range(n):
        if emode is None:
            # no electron data: nearest root to the true size (upper bound only)
            se[i] = s0[i]
            te_small[i], te_large[i] = small[i], large[i]
        else:
            se[i] = float(np.interp(s0[i], emode["sigma0"], emode["sigmam"]))
            predict = _emode_predictor(emode, s0[i])
            te_small[i] = predict(small[i])
            te_large[i] = predict(large[i])
        pick[i], which[i], margin[i] = select_root(
            small[i], large[i], fold_loo[i], se[i], te_small[i], te_large[i]
        )
    res = 100 * (pick / s0 - 1)
    base = np.array([str(w).rstrip("*") for w in which], dtype=object)
    other = np.where(base == "small", large, np.where(base == "large", small, np.nan))
    cost = 100 * np.abs(other / s0 - 1)
    truth = np.where(s0 < fold_s0 - 0.5, "small", np.where(s0 > fold_s0 + 0.5, "large", "fold"))
    correct = np.array(
        [
            (t == "fold") or (str(w).rstrip("*") == t) or (w in ("fold", "undecided"))
            for t, w in zip(truth, which)
        ]
    )
    interior = (s0 >= s0.min() + 0.5) & (s0 <= (19.5 if beam == "injection" else 20.5))
    ok = interior & ~wall
    near_fold = np.abs(s0 - fold_s0) <= 1.01
    return dict(
        beam=beam,
        power=power,
        slug=slug,
        sigma0=s0,
        sigmam=sm,
        frac=fr,
        wall=wall,
        lost=lost,
        near_wall=near_wall,
        sigma_e=se,
        te_small=te_small,
        te_large=te_large,
        margin=margin,
        small=small,
        large=large,
        fold_loo=fold_loo,
        pick=pick,
        which=which,
        res=res,
        cost=cost,
        correct=correct,
        ok=ok,
        interior=interior,
        near_fold=near_fold,
        fold_s0=fold_s0,
        fold_sm=fold_sm,
        fold_vertex=fold_vertex,
        slope10=_slope_at(s0, sm, 10.0),
        emode_delta10=(
            float(np.interp(10.0, emode["sigma0"], emode["delta"])) if emode is not None else float("nan")
        ),
        emode_table=emode,
    )


def build_cases(inj: dict, ext: dict) -> dict[tuple[str, int, str], dict]:
    cases: dict[tuple[str, int, str], dict] = {}
    for beam, table in (("injection", inj), ("extraction", ext)):
        for power in POWERS:
            em = emode_size_table(beam, power)
            for slug, _lab in WORKING:
                if (slug, power) not in table:
                    continue
                cases[(beam, power, slug)] = invert_case(beam, power, slug, table[(slug, power)], em)
    return cases


# ----------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------


def _stat(values: np.ndarray, mask: np.ndarray) -> tuple[float, float, int]:
    v = np.abs(values[mask & np.isfinite(values)])
    if v.size == 0:
        return float("nan"), float("nan"), 0
    return float(np.median(v)), float(np.max(v)), int(v.size)


def case_row(c: dict) -> dict:
    s0 = c["sigma0"]
    i10 = int(np.argmin(np.abs(s0 - 10)))
    ok = c["ok"]
    small_b = ok & (s0 < c["fold_s0"] - 0.5)
    large_b = ok & (s0 > c["fold_s0"] + 0.5)
    away = ok & ~c["near_fold"]
    med_all, max_all, n_all = _stat(c["res"], ok)
    med_s, max_s, n_s = _stat(c["res"], small_b)
    med_l, max_l, n_l = _stat(c["res"], large_b)
    med_a, max_a, n_a = _stat(c["res"], away)
    med_nf, max_nf, n_nf = _stat(c["res"], ok & c["near_fold"])
    return dict(
        beam=c["beam"],
        power_kw=c["power"],
        species=c["slug"],
        fold_mm=c["fold_s0"],
        fold_sm_mm=c["fold_sm"],
        sm10_mm=float(c["sigmam"][i10]),
        small10_mm=float(c["small"][i10]),
        large10_mm=float(c["large"][i10]),
        se10_mm=float(c["sigma_e"][i10]),
        te_small10_mm=float(c["te_small"][i10]),
        te_large10_mm=float(c["te_large"][i10]),
        margin10_pct=float(c["margin"][i10]),
        margin_min_pct=(
            float(np.nanmin(c["margin"][ok])) if np.isfinite(c["margin"][ok]).any() else float("nan")
        ),
        margin_med_pct=(
            float(np.nanmedian(c["margin"][ok])) if np.isfinite(c["margin"][ok]).any() else float("nan")
        ),
        n_lowmargin=int((ok & (c["margin"] < EMODE_MARGIN_PCT)).sum()),
        n_undecided=int((ok & (c["which"] == "undecided")).sum()),
        n_unconfirmed=int((ok & np.array([str(w).endswith("*") for w in c["which"]])).sum()),
        pick10_mm=float(c["pick"][i10]),
        which10=str(c["which"][i10]),
        res10_pct=float(c["res"][i10]),
        wall10=bool(c["wall"][i10]),
        near10=bool(c["near_wall"][i10]),
        frac10=float(c["frac"][i10]),
        slope10=c["slope10"],
        emode_delta10_pct=c["emode_delta10"],
        n_ok=n_all,
        n_correct=int((c["correct"] & ok).sum()),
        med_pct=med_all,
        max_pct=max_all,
        med_small_pct=med_s,
        max_small_pct=max_s,
        n_small=n_s,
        med_large_pct=med_l,
        max_large_pct=max_l,
        n_large=n_l,
        med_away_pct=med_a,
        max_away_pct=max_a,
        n_away=n_a,
        med_fold_pct=med_nf,
        max_fold_pct=max_nf,
        n_fold=n_nf,
        cost_min_pct=float(np.nanmin(c["cost"][ok])) if np.isfinite(c["cost"][ok]).any() else float("nan"),
        n_wall=int(c["wall"].sum()),
        n_near=int(c["near_wall"].sum()),
        lost_sizes=[float(s) for s in s0[c["lost"]]],
        near_sizes=[float(s) for s in s0[c["near_wall"]]],
        n_grid=int(len(s0)),
    )


def species_cross_check(cases: dict, beam: str, power: int) -> dict | None:
    """Agreement of the right roots and disagreement of the wrong roots
    between H₂O⁺ and N₂⁺ (leave-one-out, inside the cage, grid interior)."""
    kw, kn = (beam, power, "h2o_ions"), (beam, power, "n2_ions")
    if kw not in cases or kn not in cases:
        return None
    w, n = cases[kw], cases[kn]
    s0 = w["sigma0"]
    if len(s0) != len(n["sigma0"]) or not np.allclose(s0, n["sigma0"]):
        return None

    def split(c: dict) -> tuple[np.ndarray, np.ndarray]:
        right = np.where(s0 < c["fold_s0"], c["small"], c["large"])
        wrong = np.where(s0 < c["fold_s0"], c["large"], c["small"])
        return right, wrong

    rw, ww = split(w)
    rn, wn = split(n)
    ok = w["ok"] & n["ok"] & ~w["near_fold"] & ~n["near_fold"]
    dr = 100 * np.abs(rw / rn - 1)
    dw = 100 * np.abs(ww / wn - 1)
    m = ok & np.isfinite(dr) & np.isfinite(dw)
    if not m.any():
        return None
    return dict(
        beam=beam,
        power_kw=power,
        n=int(m.sum()),
        right_med_pct=float(np.median(dr[m])),
        right_max_pct=float(np.max(dr[m])),
        wrong_med_pct=float(np.median(dw[m])),
        wrong_min_pct=float(np.min(dw[m])),
    )


# ----------------------------------------------------------------------------
# plots
# ----------------------------------------------------------------------------


def _panel_curves(ax, beam: str, power: int, table: dict, cases: dict, show_legend: bool) -> None:
    ax.plot([0, 30], [0, 30], "k--", lw=0.7)
    if ("ions", power) in table:
        h2 = table[("ions", power)]
        ax.plot(h2["sigma0"], h2["sigmam"], "-", color="b", lw=0.8, alpha=0.6, label=r"H$_2^+$")
    ymax = 0.0
    for slug, lab in WORKING:
        c = cases.get((beam, power, slug))
        if c is None:
            continue
        s0, sm, lost, near = c["sigma0"], c["sigmam"], c["lost"], c["near_wall"]
        full = ~lost & ~near
        ax.plot(s0, sm, "-", color=COLORS[slug], lw=1.2)
        ax.plot(s0[full], sm[full], MARKERS[slug], color=COLORS[slug], ms=4.5, label=lab)
        if near.any():
            ax.plot(s0[near], sm[near], MARKERS[slug], color=COLORS[slug], ms=4.5, fillstyle="none")
        if lost.any():
            ax.plot(s0[lost], sm[lost], MARKERS[slug], color="0.6", ms=4.5, fillstyle="none")
        ymax = max(ymax, float(sm.max()))
    c = cases.get((beam, power, "n2_ions"))
    if c is not None:
        em = c.get("emode_table")
        if em is not None:
            ax.plot(em["sigma0"], em["sigmam"], "-", color="k", lw=1.0)
            ax.plot(em["sigma0"], em["sigmam"], "+", color="k", ms=5, mew=1.0, label=r"e-mode, $B=0$")
        i10 = int(np.argmin(np.abs(c["sigma0"] - 10)))
        sm10 = float(c["sigmam"][i10])
        if not c["lost"][i10]:
            ax.axhline(sm10, color="g", ls=":", lw=0.9)
            sS, sL, _ = two_roots(sm10, c["sigma0"], c["sigmam"])
            if np.isfinite(sS):
                ax.plot([sS], [sm10], "s", color="k", ms=6, fillstyle="none", mew=1.2)
                ax.annotate(r"$\sigma_S$", (sS, sm10), xytext=(-14, 6), textcoords="offset points", fontsize=9)
            if np.isfinite(sL):
                ax.plot([sL], [sm10], "s", color="k", ms=6, mew=1.2)
                ax.annotate(r"$\sigma_L$", (sL, sm10), xytext=(4, 6), textcoords="offset points", fontsize=9)
            if em is not None:
                # the e-mode check: measured σ_e of the 10 mm beam against the
                # electron widths the two ion roots predict
                predict = _emode_predictor(em, None)
                ax.axhline(c["sigma_e"][i10], color="k", ls=":", lw=0.9)
                for root, fs in ((sS, "none"), (sL, "full")):
                    te = predict(root)
                    if np.isfinite(te):
                        ax.plot([root], [te], "D", color="k", ms=5, fillstyle=fs, mew=1.0)
    ax.set_xlim(2.5, 20.5)
    top = min(65.0, max(22.0, 1.08 * ymax))
    ax.set_ylim(0, top)
    ax.set_title(rf"{power}\,\mathrm{{kW}}", fontsize=12)
    if show_legend:
        ax.legend(fontsize=8, loc="upper left", ncol=1)


def _panel_roots(ax, beam: str, power: int, cases: dict, show_legend: bool) -> None:
    ax.plot([0, 30], [0, 30], "k--", lw=0.7)
    for slug, lab in WORKING:
        c = cases.get((beam, power, slug))
        if c is None:
            continue
        s0, wall = c["sigma0"], c["wall"]
        col, mk = COLORS[slug], MARKERS[slug]
        # grid ends are extrapolations under leave-one-out and are not drawn
        inner = c["interior"]
        g = ~wall & inner
        w = wall & inner
        ax.plot(s0[g], c["small"][g], mk, color=col, ms=5, fillstyle="none", label=rf"{lab} $\sigma_S$")
        ax.plot(s0[g], c["large"][g], mk, color=col, ms=5, label=rf"{lab} $\sigma_L$")
        if w.any():
            ax.plot(s0[w], c["small"][w], mk, color="0.6", ms=5, fillstyle="none")
            ax.plot(s0[w], c["large"][w], mk, color="0.6", ms=5)
        sel = g & np.isfinite(c["pick"])
        near = sel & c["near_wall"]
        ax.plot(s0[sel & ~near], c["pick"][sel & ~near], "o", color="k", ms=9, fillstyle="none", mew=0.9,
                label="e-mode confirmed" if slug == "n2_ions" else None)
        if near.any():
            ax.plot(s0[near], c["pick"][near], "o", color="k", ms=9, fillstyle="none", mew=0.9, ls="", alpha=0.45)
    c = cases.get((beam, power, "n2_ions"))
    if c is not None:
        ax.axvline(c["fold_s0"], color="0.5", ls=":", lw=0.8)
    ax.set_xlim(2.5, 20.5)
    ax.set_ylim(0, 30)
    if show_legend:
        ax.legend(fontsize=7, loc="upper left", ncol=2, columnspacing=0.6, handletextpad=0.3)


def plot_cases(beam: str, table: dict, cases: dict) -> Path:
    """2 x 4 per-power case figure: σ_m(σ₀) with both roots of the 10 mm
    width and the B = 0 electron curve (top); leave-one-out σ_S / σ_L with
    the root confirmed by the electron width (bottom)."""
    fig, axes = plt.subplots(2, 4, figsize=(13.4, 7.0), sharex=True)
    for j, power in enumerate(POWERS):
        _panel_curves(axes[0, j], beam, power, table, cases, show_legend=(j == 0))
        _panel_roots(axes[1, j], beam, power, cases, show_legend=(j == 0))
        axes[1, j].set_xlabel(r"true $\sigma_0$ [mm]")
        for row in (0, 1):
            axes[row, j].text(
                0.97, 0.05, f"({'abcdefgh'[row * 4 + j]})", transform=axes[row, j].transAxes,
                ha="right", va="bottom", fontsize=11,
            )
    axes[0, 0].set_ylabel(r"collected $\sigma_m$ [mm]")
    axes[1, 0].set_ylabel(r"root $\sigma_S$, $\sigma_L$ [mm]")
    for ax in axes.ravel():
        ax.tick_params(labelsize=11)
    fig.tight_layout(w_pad=0.6, h_pad=0.4)
    path = PLOTS / f"csns_imode_inversion_{beam}_cases.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_selected_power(cases: dict, power: int) -> Path:
    """One power per figure: residual of the root confirmed by the B = 0
    electron width (a: injection, b: extraction) and the electron margin
    |T_e(σ_S) − T_e(σ_L)| / σ_e that separated the two hypotheses
    (c: injection, d: extraction)."""
    fig, axes = plt.subplots(1, 4, figsize=(13.4, 3.7))
    for j, beam in enumerate(("injection", "extraction")):
        ax, axm = axes[j], axes[2 + j]
        for slug, lab in WORKING:
            c = cases.get((beam, power, slug))
            if c is None:
                continue
            s0, res, mg = c["sigma0"], c["res"], c["margin"]
            mk = MARKERS[slug]
            inner = c["interior"] & np.isfinite(res) & ~c["lost"]
            g = inner & ~c["near_wall"]
            w = inner & c["near_wall"]
            ax.plot(s0[g], res[g], mk, color=COLORS[slug], ms=6, label=lab)
            if w.any():
                ax.plot(s0[w], res[w], mk, color=COLORS[slug], ms=6, fillstyle="none")
            gm = inner & np.isfinite(mg)
            axm.plot(s0[gm & ~c["near_wall"]], mg[gm & ~c["near_wall"]], mk, color=COLORS[slug], ms=6, label=lab)
            if (gm & c["near_wall"]).any():
                axm.plot(s0[gm & c["near_wall"]], mg[gm & c["near_wall"]], mk,
                         color=COLORS[slug], ms=6, fillstyle="none")
            axm.axvline(c["fold_s0"], color=COLORS[slug], ls=":", lw=0.8)
            ax.axvline(c["fold_s0"], color=COLORS[slug], ls=":", lw=0.8)
        ax.axhline(0, color="k", lw=0.6)
        ax.axhspan(-2, 2, color="0.90", zorder=0)
        ax.set_xlim(2.5, 20.5)
        ax.set_ylim(-15, 15)
        ax.set_xlabel(r"true $\sigma_0$ [mm]")
        ax.set_title("injection" if beam == "injection" else "extraction", fontsize=12)
        ax.text(0.04, 0.95, f"({'ab'[j]})", transform=ax.transAxes, va="top", fontsize=11)
        axm.axhline(EMODE_MARGIN_PCT, color="k", ls=":", lw=0.8)
        axm.set_yscale("log")
        axm.set_ylim(0.2, 200)
        axm.set_xlim(2.5, 20.5)
        axm.set_xlabel(r"true $\sigma_0$ [mm]")
        axm.set_title("injection" if beam == "injection" else "extraction", fontsize=12)
        axm.text(0.04, 0.95, f"({'cd'[j]})", transform=axm.transAxes, va="top", fontsize=11)
    axes[0].set_ylabel(r"confirmed-root residual [\%]")
    axes[2].set_ylabel(r"e-mode margin [\%]")
    axes[0].legend(fontsize=9, loc="lower right")
    for ax in axes:
        ax.tick_params(labelsize=11)
    fig.suptitle(rf"{power}\,\mathrm{{kW}}", fontsize=13, y=1.0)
    fig.tight_layout(w_pad=0.8)
    path = PLOTS / f"csns_imode_inversion_selected_{power}kw.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------
# outputs
# ----------------------------------------------------------------------------


def write_table(cases: dict) -> Path:
    path = OUT / "csns_imode_inversion.csv"
    keys = [
        "beam",
        "power_kw",
        "species",
        "sigma0_mm",
        "sigmam_mm",
        "detected_frac",
        "lost",
        "near_wall",
        "sigma_e_b0_mm",
        "root_small_mm",
        "root_large_mm",
        "te_small_mm",
        "te_large_mm",
        "emode_margin_pct",
        "selected_mm",
        "selected_branch",
        "residual_pct",
        "pick_correct",
    ]

    def fmt(v) -> str:
        if isinstance(v, (bool, np.bool_)):
            return "1" if v else "0"
        if isinstance(v, str):
            return v
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            return ""
        return f"{float(v):.4g}" if abs(float(v)) < 1e-2 else f"{float(v):.3f}"

    with path.open("w") as fh:
        fh.write(",".join(keys) + "\n")
        for (beam, power, slug), c in sorted(cases.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
            for i, s in enumerate(c["sigma0"]):
                row = dict(
                    beam=beam,
                    power_kw=power,
                    species=slug,
                    sigma0_mm=float(s),
                    sigmam_mm=float(c["sigmam"][i]),
                    detected_frac=float(c["frac"][i]),
                    lost=bool(c["lost"][i]),
                    near_wall=bool(c["near_wall"][i]),
                    sigma_e_b0_mm=float(c["sigma_e"][i]),
                    root_small_mm=float(c["small"][i]),
                    root_large_mm=float(c["large"][i]),
                    te_small_mm=float(c["te_small"][i]),
                    te_large_mm=float(c["te_large"][i]),
                    emode_margin_pct=float(c["margin"][i]),
                    selected_mm=float(c["pick"][i]),
                    selected_branch=str(c["which"][i]),
                    residual_pct=float(c["res"][i]),
                    pick_correct=bool(c["correct"][i]),
                )
                fh.write(",".join(fmt(row[k]) for k in keys) + "\n")
    return path


def _p(v: float, nd: int = 2) -> str:
    return "—" if not np.isfinite(v) else f"{v:.{nd}f}"


def print_report(cases: dict) -> None:
    print("Two-root invert (identified H2O+ / N2+), leave-one-out; B = 0 e-mode width confirms the root by consistency.")
    print("lost = frac<0.995 (excluded); near-wall = σm>40 mm (kept, flagged); interior = grid interior; near-fold = |σ0-σ0*| ≤ 1 mm")
    print(
        "beam power species | fold σ0* σm,min | 10 mm: σm σS σL | σe Te(σS) Te(σL) margin → pick (res) slope | "
        "n_ok correct undecided low-margin(<5%) margin min/med | med/max all | med/max small | med/max large | away-from-fold med/max | fold±1 med/max | wrong-pick min cost | lost | near"
    )
    for key in sorted(cases, key=lambda k: (k[0] != "injection", k[1], k[2])):
        r = case_row(cases[key])
        print(
            f"  {r['beam']:10s} {r['power_kw']:3d} {r['species']:8s} | "
            f"{r['fold_mm']:4.1f} {r['fold_sm_mm']:6.2f} | "
            f"{r['sm10_mm']:6.2f} {_p(r['small10_mm'])} {_p(r['large10_mm'])} | {r['se10_mm']:.2f} {_p(r['te_small10_mm'])} {_p(r['te_large10_mm'])} {_p(r['margin10_pct'], 0)}% → "
            f"{_p(r['pick10_mm'])} ({r['which10']}, {r['res10_pct']:+.2f}%)"
            f"{' LOST' if r['wall10'] else (' near-wall' if r['near10'] else '')} frac={r['frac10']:.4f} slope={_p(r['slope10'])} | "
            f"{r['n_ok']:2d} {r['n_correct']:2d} und={r['n_undecided']} unc={r['n_unconfirmed']} low={r['n_lowmargin']} {_p(r['margin_min_pct'],1)}/{_p(r['margin_med_pct'],0)} | {_p(r['med_pct'])}/{_p(r['max_pct'])} | "
            f"{_p(r['med_small_pct'])}/{_p(r['max_small_pct'])} (n={r['n_small']}) | "
            f"{_p(r['med_large_pct'])}/{_p(r['max_large_pct'])} (n={r['n_large']}) | "
            f"{_p(r['med_away_pct'])}/{_p(r['max_away_pct'])} (n={r['n_away']}) | "
            f"{_p(r['med_fold_pct'])}/{_p(r['max_fold_pct'])} (n={r['n_fold']}) | "
            f"{_p(r['cost_min_pct'], 1)}% | lost {r['n_wall']} {r['lost_sizes']} | near {r['n_near']} {r['near_sizes']}"
        )
    print("Species cross-check (right roots agree / wrong roots disagree), away from fold, inside cage:")
    for beam in ("injection", "extraction"):
        for power in POWERS:
            x = species_cross_check(cases, beam, power)
            if x is None:
                continue
            print(
                f"  {beam:10s} {power:3d} kW: right med {x['right_med_pct']:.2f}% max {x['right_max_pct']:.2f}% ; "
                f"wrong med {x['wrong_med_pct']:.1f}% min {x['wrong_min_pct']:.1f}%  (n={x['n']})"
            )
    print(f"e-mode B = {EMODE_B_GS} G at 10 mm (Δ vs no-SC, %):")
    for beam in ("injection", "extraction"):
        print("  " + beam + ": " + ", ".join(
            f"{p} kW {cases[(beam, p, 'n2_ions')]['emode_delta10']:+.2f}" for p in POWERS if (beam, p, "n2_ions") in cases
        ))


def main() -> None:
    plot_conf()
    PLOTS.mkdir(exist_ok=True)
    inj = injection_size_table()
    ext = extraction_aligned_table()
    cases = build_cases(inj, ext)
    print("wrote", write_table(cases))
    print("wrote", plot_cases("injection", inj, cases))
    print("wrote", plot_cases("extraction", ext, cases))
    for power in POWERS:
        print("wrote", plot_selected_power(cases, power))
    print_report(cases)


if __name__ == "__main__":
    main()
