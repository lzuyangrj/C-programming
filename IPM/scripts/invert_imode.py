#!/usr/bin/env python3
"""Invert CSNS ion-mode widths from one identified residual-gas species.

The ToF spectrum identifies the peak (H₂O⁺ or N₂⁺). That species' Block B /
I2 table is then inverted on the physical branch σ₀ ≥ σ₀*(P) (the minimum
of σ_m). H₂⁺ is shown only as the poorly conditioned alternative. No
Virtual-IPM runs; summary CSVs only.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d

from plot_conf import load_summary, plot_conf
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
PLOTS = ROOT / "plots"

SPECIES = (("ions", r"H$_2^+$"), ("h2o_ions", r"H$_2$O$^+$"), ("n2_ions", r"N$_2^+$"))
COLORS = {"ions": "b", "h2o_ions": "r", "n2_ions": "g"}


def _f(row: dict, key: str) -> float:
    return float(row[key])


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


def _interp(x: np.ndarray, y: np.ndarray) -> interp1d:
    return interp1d(x, y, kind="linear", bounds_error=False, fill_value=np.nan)


def single_species_roots(sigma_m: float, sigma0: np.ndarray, sigmam: np.ndarray) -> list[float]:
    """Roots of σ_m(σ_0) = sigma_m on a tabulated curve."""
    roots: list[float] = []
    for i in range(len(sigma0) - 1):
        y0, y1 = sigmam[i] - sigma_m, sigmam[i + 1] - sigma_m
        if y0 == 0:
            roots.append(float(sigma0[i]))
        elif y0 * y1 < 0:
            roots.append(float(sigma0[i] - y0 * (sigma0[i + 1] - sigma0[i]) / (y1 - y0)))
    return roots


def invert_large_root(sigma_m: float, sigma0: np.ndarray, sigmam: np.ndarray) -> float:
    """Shiltsev-style start-from-σ_m: the root on the large-σ₀ branch."""
    roots = single_species_roots(sigma_m, sigma0, sigmam)
    imin = int(np.argmin(sigmam))
    large = [r for r in roots if r >= float(sigma0[imin]) - 0.05]
    return max(large) if large else float("nan")


def invert_identified(sigma_m: float, sigma0: np.ndarray, sigmam: np.ndarray) -> float:
    """Invert an identified-species table on σ₀ ≥ σ₀* (minimum of σ_m).

    σ_m increases with σ₀ on that branch, so the interpolant is unique.
    A measured width that only exists on the small-σ₀ side returns NaN.
    """
    imin = int(np.argmin(sigmam))
    smin = float(sigma0[imin])
    m = sigma0 >= smin - 1e-9
    x, y = np.asarray(sigmam[m], float), np.asarray(sigma0[m], float)
    order = np.argsort(x)
    x, y = x[order], y[order]
    _, idx = np.unique(np.round(x, 6), return_index=True)
    x, y = x[idx], y[idx]
    if len(x) < 2 or sigma_m < x[0] - 1e-9 or sigma_m > x[-1] + 1e-9:
        return float("nan")
    return float(np.interp(sigma_m, x, y))


def leave_one_out_identified(sigma0: np.ndarray, sigmam: np.ndarray) -> np.ndarray:
    rec = np.full_like(sigma0, np.nan, dtype=float)
    for i in range(len(sigma0)):
        mask = np.ones(len(sigma0), bool)
        mask[i] = False
        rec[i] = invert_identified(sigmam[i], sigma0[mask], sigmam[mask])
    return rec


def leave_one_out_large(sigma0: np.ndarray, sigmam: np.ndarray) -> np.ndarray:
    rec = np.full_like(sigma0, np.nan, dtype=float)
    for i in range(len(sigma0)):
        mask = np.ones(len(sigma0), bool)
        mask[i] = False
        rec[i] = invert_large_root(sigmam[i], sigma0[mask], sigmam[mask])
    return rec


def plot_curves(inj: dict) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    tab = {slug: inj[(slug, 100)] for slug, _ in SPECIES}
    s0 = tab["n2_ions"]["sigma0"]
    for slug, lab in SPECIES:
        ax1.plot(tab[slug]["sigma0"], tab[slug]["sigmam"], "o-", color=COLORS[slug], lw=1.5, ms=5, label=lab)
    i10 = int(np.argmin(np.abs(s0 - 10)))
    ax1.axhline(tab["h2o_ions"]["sigmam"][i10], color="r", ls=":", lw=0.9)
    ax1.axhline(tab["n2_ions"]["sigmam"][i10], color="g", ls=":", lw=0.9)
    ax1.set_xlabel(r"true $\sigma_0$ [mm]")
    ax1.set_ylabel(r"collected $\sigma_m$ [mm]")
    ax1.set_xlim(2.5, 20.5)
    ax1.set_ylim(12, 30)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=11, loc="upper right")

    ax2.plot([2, 21], [2, 21], "k--", lw=0.8)
    for slug, lab in (("h2o_ions", r"H$_2$O$^+$"), ("n2_ions", r"N$_2^+$")):
        rec = leave_one_out_identified(tab[slug]["sigma0"], tab[slug]["sigmam"])
        ax2.plot(
            tab[slug]["sigma0"],
            rec,
            "o",
            color=COLORS[slug],
            ms=6,
            label=lab,
        )
    ax2.set_xlabel(r"true $\sigma_0$ [mm]")
    ax2.set_ylabel(r"recovered $\sigma_0$ [mm]")
    ax2.set_xlim(2.5, 20.5)
    ax2.set_ylim(2.5, 21)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    ax2.legend(fontsize=11, loc="upper left")
    fig.tight_layout()
    path = PLOTS / "csns_imode_inversion_curves.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_extraction(ext: dict) -> Path:
    """Two-panel aligned-extraction invert: σ_m(σ₀) and leave-one-out recover."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    tab100 = {slug: ext[(slug, 100)] for slug, _ in SPECIES if (slug, 100) in ext}
    if "h2o_ions" not in tab100 or "n2_ions" not in tab100:
        path = PLOTS / "csns_imode_inversion_extraction.png"
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return path
    for slug, lab in SPECIES:
        if slug not in tab100:
            continue
        ax1.plot(
            tab100[slug]["sigma0"],
            tab100[slug]["sigmam"],
            "o-",
            color=COLORS[slug],
            lw=1.5,
            ms=5,
            label=lab,
        )
    s0 = tab100["n2_ions"]["sigma0"]
    i10 = int(np.argmin(np.abs(s0 - 10)))
    ax1.axhline(tab100["h2o_ions"]["sigmam"][int(np.argmin(np.abs(tab100["h2o_ions"]["sigma0"] - 10)))],
                color="r", ls=":", lw=0.9)
    ax1.axhline(tab100["n2_ions"]["sigmam"][i10], color="g", ls=":", lw=0.9)
    ax1.set_xlabel(r"true $\sigma_0$ [mm]")
    ax1.set_ylabel(r"collected $\sigma_m$ [mm]")
    ax1.set_xlim(2.5, 20.5)
    ax1.set_ylim(11, 29)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=11, loc="upper right")

    ax2.plot([2, 21], [2, 21], "k--", lw=0.8)
    n2 = tab100["n2_ions"]
    h2o = tab100["h2o_ions"]
    rec_n2 = leave_one_out_identified(n2["sigma0"], n2["sigmam"])
    rec_h2o = leave_one_out_identified(h2o["sigma0"], h2o["sigmam"])
    ax2.plot(n2["sigma0"], n2["sigmam"], "s", color="0.55", ms=6, label=r"uncorrected $\mathrm{N}_2^+$")
    ax2.plot(h2o["sigma0"], rec_h2o, "o", color="r", ms=6, label=r"identified $\mathrm{H}_2\mathrm{O}^+$")
    ax2.plot(n2["sigma0"], rec_n2, "^", color="g", ms=7, label=r"identified $\mathrm{N}_2^+$")
    ax2.set_xlabel(r"true $\sigma_0$ [mm]")
    ax2.set_ylabel(r"recovered $\sigma_0$ [mm]")
    ax2.set_xlim(2.5, 20.5)
    ax2.set_ylim(2.5, 28)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    ax2.legend(fontsize=10, loc="lower right")
    fig.tight_layout()
    path = PLOTS / "csns_imode_inversion_extraction.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_extraction_power(ext: dict) -> Path | None:
    """Identified-species residual versus σ₀ at extraction powers that have a table."""
    powers = sorted({p for (slug, p) in ext if slug in ("h2o_ions", "n2_ions")})
    # Only quote tables with a 1 mm-class grid; the coarse I2 5 mm
    # powers are kept in the CSV but are not a 0.2% invert.
    usable = [
        p
        for p in powers
        if ("h2o_ions", p) in ext
        and ("n2_ions", p) in ext
        and len(ext[("n2_ions", p)]["sigma0"]) >= 10
    ]
    if not usable:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    for slug, color in (("h2o_ions", "r"), ("n2_ions", "g")):
        for power, mk in zip(usable, ("o", "s", "^", "D", "v", "P", "X")):
            a = ext[(slug, power)]
            rec = leave_one_out_identified(a["sigma0"], a["sigmam"])
            wall = (a["frac"] < 0.995) | (a["sigmam"] > 40.0)
            good = ~np.isnan(rec)
            lab = rf"{power}\,kW" if slug == "n2_ions" else None
            ax.plot(
                a["sigma0"][good & ~wall],
                100 * (rec[good & ~wall] / a["sigma0"][good & ~wall] - 1),
                mk,
                color=color,
                ms=6,
                label=lab,
            )
            if (good & wall).any():
                ax.plot(
                    a["sigma0"][good & wall],
                    100 * (rec[good & wall] / a["sigma0"][good & wall] - 1),
                    mk,
                    color="0.6",
                    ms=6,
                    fillstyle="none",
                )
    ax.plot([], [], "o", color="r", ms=6, label=r"$\mathrm{H}_2\mathrm{O}^+$")
    ax.plot([], [], "o", color="g", ms=6, label=r"$\mathrm{N}_2^+$")
    ax.axhline(0, color="k", lw=0.6)
    ax.axhspan(-2, 2, color="0.90", zorder=0)
    ax.set_xlabel(r"true $\sigma_0$ [mm]")
    ax.set_ylabel(r"identified-species residual [\%]")
    ax.set_xlim(2.5, 20.5)
    ax.set_ylim(-15, 15)
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    fig.tight_layout()
    path = PLOTS / "csns_imode_inversion_extraction_power.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_recover(inj: dict, ext: dict) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    n2 = inj[("n2_ions", 100)]
    h2o = inj[("h2o_ions", 100)]
    s0 = n2["sigma0"]
    rec_n2 = leave_one_out_identified(s0, n2["sigmam"])
    rec_h2o = leave_one_out_identified(h2o["sigma0"], h2o["sigmam"])
    ax1.plot([2, 21], [2, 21], "k--", lw=0.8)
    ax1.plot(s0, n2["sigmam"], "s", color="0.55", ms=6, label=r"uncorrected $\mathrm{N}_2^+$")
    ax1.plot(h2o["sigma0"], rec_h2o, "o", color="r", ms=6, label=r"identified $\mathrm{H}_2\mathrm{O}^+$")
    ax1.plot(s0, rec_n2, "^", color="g", ms=7, label=r"identified $\mathrm{N}_2^+$")
    ax1.set_xlabel(r"true $\sigma_0$ [mm]")
    ax1.set_ylabel(r"recovered $\sigma_0$ [mm]")
    ax1.set_xlim(2.5, 20.5)
    ax1.set_ylim(2.5, 30)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=10, loc="upper left")

    for slug, color in (("h2o_ions", "r"), ("n2_ions", "g")):
        for power, mk in ((100, "o"), (200, "s"), (300, "^")):
            if (slug, power) not in inj:
                continue
            a = inj[(slug, power)]
            rec = leave_one_out_identified(a["sigma0"], a["sigmam"])
            wall = (a["frac"] < 0.995) | (a["sigmam"] > 40.0)
            good = ~np.isnan(rec)
            lab = None
            if slug == "n2_ions":
                lab = rf"{power}\,kW"
            ax2.plot(
                a["sigma0"][good & ~wall],
                100 * (rec[good & ~wall] / a["sigma0"][good & ~wall] - 1),
                mk,
                color=color,
                ms=6,
                label=lab,
            )
            if (good & wall).any():
                ax2.plot(
                    a["sigma0"][good & wall],
                    100 * (rec[good & wall] / a["sigma0"][good & wall] - 1),
                    mk,
                    color="0.6",
                    ms=6,
                    fillstyle="none",
                )
    ax2.plot([], [], "o", color="r", ms=6, label=r"$\mathrm{H}_2\mathrm{O}^+$")
    ax2.plot([], [], "o", color="g", ms=6, label=r"$\mathrm{N}_2^+$")
    ax2.axhline(0, color="k", lw=0.6)
    ax2.axhspan(-2, 2, color="0.90", zorder=0)
    ax2.set_xlabel(r"true $\sigma_0$ [mm]")
    ax2.set_ylabel(r"identified-species residual [\%]")
    ax2.set_xlim(2.5, 20.5)
    ax2.set_ylim(-15, 15)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    ax2.legend(fontsize=9, loc="upper right", ncol=2)
    fig.tight_layout()
    path = PLOTS / "csns_imode_inversion_recover.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def write_table(inj: dict, ext: dict) -> Path:
    path = OUT / "csns_imode_inversion.csv"
    keys = [
        "beam",
        "power_kw",
        "sigma0_mm",
        "sigmam_h2o_mm",
        "sigmam_n2_mm",
        "rec_h2o_mm",
        "rec_n2_mm",
        "residual_h2o_pct",
        "residual_n2_pct",
        "frac_n2",
    ]
    rows = []
    for beam, table in (("injection", inj), ("extraction", ext)):
        for power in sorted({p for (_s, p) in table}):
            if ("h2o_ions", power) not in table or ("n2_ions", power) not in table:
                continue
            h2o, n2 = table[("h2o_ions", power)], table[("n2_ions", power)]
            s0 = np.array(sorted(set(h2o["sigma0"]) & set(n2["sigma0"])))
            if len(s0) < 4:
                continue
            sm_w = _interp(h2o["sigma0"], h2o["sigmam"])(s0)
            sm_n = _interp(n2["sigma0"], n2["sigmam"])(s0)
            fr = _interp(n2["sigma0"], n2["frac"])(s0)
            rec_w = leave_one_out_identified(s0, sm_w)
            rec_n = leave_one_out_identified(s0, sm_n)
            for i, s in enumerate(s0):
                rows.append(
                    dict(
                        beam=beam,
                        power_kw=power,
                        sigma0_mm=round(float(s), 2),
                        sigmam_h2o_mm=round(float(sm_w[i]), 3),
                        sigmam_n2_mm=round(float(sm_n[i]), 3),
                        rec_h2o_mm="" if np.isnan(rec_w[i]) else round(float(rec_w[i]), 3),
                        rec_n2_mm="" if np.isnan(rec_n[i]) else round(float(rec_n[i]), 3),
                        residual_h2o_pct=""
                        if np.isnan(rec_w[i])
                        else round(100 * (float(rec_w[i]) / float(s) - 1), 3),
                        residual_n2_pct=""
                        if np.isnan(rec_n[i])
                        else round(100 * (float(rec_n[i]) / float(s) - 1), 3),
                        frac_n2=round(float(fr[i]), 3),
                    )
                )
    with path.open("w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join(str(r[k]) for k in keys) + "\n")
    return path


def report_stats(inj: dict, ext: dict) -> None:
    print("Injection 100 kW, 25 kV, B = 0, identified-species invert:")
    for slug, lab in (("ions", "H2+"), ("h2o_ions", "H2O+"), ("n2_ions", "N2+")):
        t = inj[(slug, 100)]
        s0, sm = t["sigma0"], t["sigmam"]
        rec = leave_one_out_identified(s0, sm)
        e = 100 * (rec / s0 - 1)
        i10 = int(np.argmin(np.abs(s0 - 10)))
        m = (s0 >= 8) & np.isfinite(e)
        print(
            f"  {lab}: min σm={sm.min():.2f} mm at σ0={s0[sm.argmin()]:.0f} mm; "
            f"σ0=10 σm={sm[i10]:.2f} rec={rec[i10]:.2f} mm ({e[i10]:+.2f}%); "
            f"σ0=8–20 med|e|={np.median(np.abs(e[m])):.2f}% max={np.max(np.abs(e[m])):.2f}%"
        )
    for power in (200, 300, 400, 500):
        for slug, lab in (("h2o_ions", "H2O+"), ("n2_ions", "N2+")):
            a = inj[(slug, power)]
            rec = leave_one_out_identified(a["sigma0"], a["sigmam"])
            wall = (a["frac"] < 0.995) | (a["sigmam"] > 40.0)
            good = ~np.isnan(rec) & ~wall
            if good.any():
                e = 100 * (rec[good] / a["sigma0"][good] - 1)
                print(
                    f"  {power} kW {lab} inside-cage |res| median {np.median(np.abs(e)):.2f}%  "
                    f"n={int(good.sum())}  wall={int(wall.sum())}  "
                    f"min@{a['sigma0'][a['sigmam'].argmin()]:.0f} mm"
                )
            else:
                print(f"  {power} kW {lab}: no inside-cage recovery (wall)")
    if ("h2o_ions", 100) in ext and ("n2_ions", 100) in ext:
        print("Aligned extraction 100 kW, 25 kV, B = 0, identified-species invert:")
        for slug, lab in (("ions", "H2+"), ("h2o_ions", "H2O+"), ("n2_ions", "N2+")):
            if (slug, 100) not in ext:
                continue
            t = ext[(slug, 100)]
            s0, sm = t["sigma0"], t["sigmam"]
            rec = leave_one_out_identified(s0, sm)
            e = 100 * (rec / s0 - 1)
            i10 = int(np.argmin(np.abs(s0 - 10)))
            imin = int(np.argmin(sm))
            m = (s0 >= float(s0[imin])) & np.isfinite(e) & (s0 >= 8) & (s0 <= 20)
            print(
                f"  {lab}: min σm={sm[imin]:.2f} mm at σ0={s0[imin]:.0f} mm; "
                f"σ0=10 σm={sm[i10]:.2f} rec={rec[i10]:.2f} mm ({e[i10]:+.2f}%); "
                f"σ0=8–20 on branch med|e|="
                f"{np.median(np.abs(e[m])) if m.any() else float('nan'):.2f}% "
                f"max={np.max(np.abs(e[m])) if m.any() else float('nan'):.2f}% "
                f"n={int(m.sum())}  grid={','.join(f'{s:.0f}' for s in s0)}"
            )
        for power in sorted({p for (s, p) in ext if s == "n2_ions" and p != 100}):
            for slug, lab in (("h2o_ions", "H2O+"), ("n2_ions", "N2+")):
                if (slug, power) not in ext:
                    continue
                a = ext[(slug, power)]
                rec = leave_one_out_identified(a["sigma0"], a["sigmam"])
                wall = (a["frac"] < 0.995) | (a["sigmam"] > 40.0)
                good = ~np.isnan(rec) & ~wall
                if good.any():
                    e = 100 * (rec[good] / a["sigma0"][good] - 1)
                    print(
                        f"  {power} kW {lab} inside-cage |res| median {np.median(np.abs(e)):.2f}%  "
                        f"n={int(good.sum())}  wall={int(wall.sum())}  "
                        f"min@{a['sigma0'][a['sigmam'].argmin()]:.0f} mm"
                    )
                else:
                    print(f"  {power} kW {lab}: no inside-cage recovery (wall)")


def main() -> None:
    plot_conf()
    PLOTS.mkdir(exist_ok=True)
    inj = injection_size_table()
    ext = extraction_aligned_table()
    report_stats(inj, ext)
    print("wrote", write_table(inj, ext))
    print("wrote", plot_curves(inj))
    print("wrote", plot_recover(inj, ext))
    print("wrote", plot_extraction(ext))
    pwr = plot_extraction_power(ext)
    if pwr is not None:
        print("wrote", pwr)


if __name__ == "__main__":
    main()
