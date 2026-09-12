#!/usr/bin/env python3
"""Compare the CSNS Virtual-IPM results with published IPM scaling models.

Electron mode: the 1 % guiding-field thresholds from Block A are compared with
the minimum-field fit of Vilsmeier, Sapinski and Storey, PRAB 22, 052801 (2019),
Eq. (8) with the Gaussian-bunch coefficients of their Table III.

Ion mode: the 0 G expansions from Blocks A and C are compared with a reduced
line-charge kick model in the spirit of Shiltsev, NIM A 986 (2021) 164744:
ions start at rest, feel the uniform cage field E_y and the transverse field of
the Gaussian bunch train (2D Gaussian line charge, no x-feedback on the field),
and are counted when they reach the collector.  The same bunch timing as the
Virtual-IPM configs is used, including the ~125 ns lag between the generation
bunch and the first tracking bunch at extraction.

Outputs plots/csns_review_emode_bmin.png and plots/csns_review_imode_model.png.
Only summary CSVs are read; no particle CSVs and no Virtual-IPM runs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import atomic_mass, c, e, epsilon_0, m_e

from plot_conf import load_summary, plot_conf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
PLOTS = ROOT / "plots"

GAP_M = 0.231
CAGE_HALF_X = 0.110
N_100KW = 7.8e12
BETA = {"injection": 0.3885, "extraction": 0.9292}
SIGMA_T_NS = {"injection": 120.0, "extraction": 20.0}
# Arrival times (s) of the tracking-train bunch centres at z = 0 and the centre
# of the ion-generation window, as produced by generate_csns_configs.py.
TRAIN = {
    "injection": dict(arrivals=(480e-9, 1460e-9, 2440e-9), gen_center=480e-9),
    "extraction": dict(arrivals=(204.6e-9, 613.8e-9, 1023.0e-9, 1432.2e-9), gen_center=80e-9),
}
SPECIES = (("ions", "H₂⁺", 2), ("h2o_ions", "H₂O⁺", 18), ("n2_ions", "N₂⁺", 28))

# Vilsmeier et al. Eq. (8), Gaussian bunch (Table III): B in T, N in 1e12,
# sigma_z in ns, sigma_t in mm.
VILS = dict(a=0.613, b=0.590, c=1.082, d=0.105, e=0.967, f=0.038)


def b_min_1pct(n12: float, sz_ns: float, st_mm: float) -> float:
    p = VILS
    return n12 ** p["a"] / (sz_ns ** p["b"] * st_mm ** p["c"]) * p["d"] + p["f"] / st_mm ** p["e"]


def emode_thresholds() -> dict[tuple[str, int], dict[int, float]]:
    rows = load_summary(OUT / "csns_emode_bscan300_summary.csv")
    out: dict[tuple[str, int], dict[int, float]] = {}
    keys = sorted({(r["beam"], r["sigma_x_mm"]) for r in rows})
    for beam, sig in keys:
        for power in sorted({r["power_kw"] for r in rows}):
            pts = sorted(
                (r["b_gs"], r["expansion_vs_no_sc_pct"])
                for r in rows
                if r["beam"] == beam and r["sigma_x_mm"] == sig and r["power_kw"] == power
            )
            thr = None
            for i, (b, _) in enumerate(pts):
                if all(abs(v) <= 1.0 for _, v in pts[i:]):
                    thr = b
                    break
            out.setdefault((beam, sig), {})[power] = thr if thr is not None else np.nan
    return out


def plot_emode(thresholds: dict) -> Path:
    fig, ax = plt.subplots()
    powers = np.array([100, 200, 300, 400, 500])
    labels = {
        ("injection", 25): "inj. 25 mm",
        ("extraction", 10): "ext. 10 mm",
        ("injection", 10): "inj. 10 mm",
    }
    for (beam, sig), lab in labels.items():
        if (beam, sig) not in thresholds:
            continue
        thr = [thresholds[(beam, sig)].get(p, np.nan) for p in powers]
        (line,) = ax.plot(powers, thr, marker="o", ls="none", label=lab + " (Virtual-IPM)")
        n12 = N_100KW * powers / 100 / 1e12
        fit = b_min_1pct(n12, SIGMA_T_NS[beam], sig) * 1e4
        fit_beta = b_min_1pct(n12 / BETA[beam], SIGMA_T_NS[beam], sig) * 1e4
        ax.plot(powers, fit, ls="--", color=line.get_color(), lw=1.2)
        ax.plot(powers, fit_beta, ls=":", color=line.get_color(), lw=1.2)
    ax.plot([], [], ls="--", color="k", lw=1.2, label="PRAB 22, 052801 Eq. (8)")
    ax.plot([], [], ls=":", color="k", lw=1.2, label=r"Eq. (8) with $N/\beta$")
    ax.set_xlabel("Beam power [kW]")
    ax.set_ylabel("1% guiding-field threshold [G]")
    ax.set_xlim(50, 550)
    ax.set_ylim(0, 340)
    ax.legend(fontsize=10, loc="upper left", ncol=1)
    path = PLOTS / "csns_review_emode_bmin.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def kick_model(
    n_p: float,
    beam: str,
    sigma: float,
    mass_u: float,
    voltage: float,
    n: int,
    rng: np.random.Generator,
    dt: float = 1e-9,
    t_max: float = 3e-6,
    gen_center: float | None = None,
) -> float:
    """Return sigma_detected / sigma - 1 for the reduced line-charge model."""
    beta = BETA[beam]
    sig_t = SIGMA_T_NS[beam] * 1e-9
    arrivals = TRAIN[beam]["arrivals"]
    mass = mass_u * atomic_mass
    e_y = voltage / GAP_M
    y_det = -GAP_M / 2
    x = rng.normal(0, sigma, n)
    y = rng.normal(0, sigma, n)
    t_gen = rng.normal(TRAIN[beam]["gen_center"] if gen_center is None else gen_center, sig_t, n)
    vx = np.zeros(n)
    vy = np.zeros(n)
    acc = e * e_y / mass
    kick = e**2 * n_p / (2 * np.pi * epsilon_0 * beta * c * mass)
    norm = 1.0 / (np.sqrt(2 * np.pi) * sig_t)
    alive = np.ones(n, bool)
    x_final = np.full(n, np.nan)
    t = 0.0
    while t < t_max and alive.any():
        born = alive & (t_gen <= t)
        if born.any():
            lam = sum(np.exp(-0.5 * ((t - tb) / sig_t) ** 2) for tb in arrivals) * norm
            r2 = x[born] ** 2 + y[born] ** 2
            g = (1 - np.exp(-r2 / (2 * sigma**2))) / r2
            vx[born] += kick * lam * dt * x[born] * g
            vy[born] += kick * lam * dt * y[born] * g - acc * dt
            x[born] += vx[born] * dt
            y[born] += vy[born] * dt
            hit = born & (y <= y_det)
            x_final[hit] = x[hit]
            alive &= ~hit
        t += dt
    ok = ~np.isnan(x_final) & (np.abs(x_final) < CAGE_HALF_X)
    return float(x_final[ok].std() / sigma - 1)


def plot_imode(n_particles: int) -> Path:
    rng = np.random.default_rng(1)
    bscan = load_summary(OUT / "csns_imode_bscan_summary.csv")
    volt = load_summary(OUT / "csns_imode_voltage_summary.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.14, top=0.92, wspace=0.28)

    families = [("injection", 25), ("injection", 10), ("extraction", 10)]
    markers = {"ions": "o", "h2o_ions": "s", "n2_ions": "^"}
    sims, models = [], []
    for slug, lab, mass_u in SPECIES:
        xs, ys = [], []
        for beam, sig in families:
            sim = [
                r["expansion_vs_no_sc_pct"]
                for r in bscan
                if r["species"] == slug
                and r["beam"] == beam
                and r["sigma_x_mm"] == sig
                and r["power_kw"] == 100
                and r["b_gs"] == 0
            ]
            if not sim:
                continue
            model = kick_model(N_100KW, beam, sig * 1e-3, mass_u, 25e3, n_particles, rng) * 100
            xs.append(model)
            ys.append(sim[0])
        ax1.plot(xs, ys, marker=markers[slug], ls="none", label=lab)
        sims += ys
        models += xs
    lim = max(sims + models) * 1.1
    ax1.plot([0, lim], [0, lim], ls="--", color="grey", lw=1)
    ax1.set_xlabel("Line-charge kick model [%]")
    ax1.set_ylabel("Virtual-IPM expansion [%]")
    ax1.set_title("0 G, 100 kW, three reference beams", fontsize=12)
    ax1.legend(fontsize=11)

    voltages = np.array([5, 10, 15, 20, 25, 30])
    for slug, lab, mass_u in SPECIES:
        sim = [
            next(
                r["expansion_vs_no_sc_pct"]
                for r in volt
                if r["species"] == slug and r["voltage_kv"] == v and r["power_kw"] == 100 and r["b_gs"] == 0
            )
            for v in voltages
        ]
        model = [kick_model(N_100KW, "injection", 10e-3, mass_u, v * 1e3, n_particles, rng) * 100 for v in voltages]
        (line,) = ax2.plot(voltages, sim, marker=markers[slug], ls="none", label=lab + " (Virtual-IPM)")
        ax2.plot(voltages, model, ls="-", lw=1.2, color=line.get_color())
    ax2.plot([], [], ls="-", color="k", lw=1.2, label="kick model")
    ax2.set_xlabel("Cage voltage [kV]")
    ax2.set_ylabel("Expansion vs no-SC [%]")
    ax2.set_title("inj. 10 mm, 100 kW, 0 G", fontsize=12)
    ax2.set_yscale("log")
    ax2.set_yticks([50, 100, 200, 400])
    ax2.set_yticklabels(["50", "100", "200", "400"])
    ax2.yaxis.set_minor_formatter(plt.NullFormatter())
    ax2.legend(fontsize=10)

    path = PLOTS / "csns_review_imode_model.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def write_model_table(n_particles: int) -> Path:
    """Write as-run vs aligned-generation expansions for the 0 G / 100 kW cases."""
    rng = np.random.default_rng(1)
    bscan = load_summary(OUT / "csns_imode_bscan_summary.csv")
    volt = load_summary(OUT / "csns_imode_voltage_summary.csv")
    rows: list[dict] = []
    families = [("injection", 25), ("injection", 10), ("extraction", 10)]
    for slug, lab, mass_u in SPECIES:
        for beam, sig in families:
            sim = next(
                (
                    r["expansion_vs_no_sc_pct"]
                    for r in bscan
                    if r["species"] == slug
                    and r["beam"] == beam
                    and r["sigma_x_mm"] == sig
                    and r["power_kw"] == 100
                    and r["b_gs"] == 0
                ),
                None,
            )
            as_run = kick_model(N_100KW, beam, sig * 1e-3, mass_u, 25e3, n_particles, rng) * 100
            aligned = None
            if beam == "extraction":
                aligned = kick_model(
                    N_100KW, beam, sig * 1e-3, mass_u, 25e3, n_particles, rng, gen_center=204.6e-9
                ) * 100
            rows.append(
                {
                    "species": lab,
                    "beam": beam,
                    "sigma_mm": sig,
                    "voltage_kv": 25,
                    "timing": "as-run",
                    "model_pct": round(as_run, 2),
                    "virtual_ipm_pct": None if sim is None else round(sim, 2),
                    "aligned_model_pct": None if aligned is None else round(aligned, 2),
                }
            )
        for v in (5, 10, 15, 20, 25, 30):
            sim = next(
                (
                    r["expansion_vs_no_sc_pct"]
                    for r in volt
                    if r["species"] == slug and r["voltage_kv"] == v and r["power_kw"] == 100 and r["b_gs"] == 0
                ),
                None,
            )
            model = kick_model(N_100KW, "injection", 10e-3, mass_u, v * 1e3, n_particles, rng) * 100
            rows.append(
                {
                    "species": lab,
                    "beam": "injection",
                    "sigma_mm": 10,
                    "voltage_kv": v,
                    "timing": "as-run",
                    "model_pct": round(model, 2),
                    "virtual_ipm_pct": None if sim is None else round(sim, 2),
                    "aligned_model_pct": "",
                }
            )
    path = OUT / "csns_imode_kick_model.csv"
    keys = ["species", "beam", "sigma_mm", "voltage_kv", "timing", "model_pct", "virtual_ipm_pct", "aligned_model_pct"]
    with path.open("w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join("" if r[k] is None else str(r[k]) for k in keys) + "\n")
    return path


def _electron_tof(voltage_kv: float) -> float:
    """Time of flight of an electron born at the cage centre, uniform field."""
    field = voltage_kv * 1e3 / GAP_M
    return float(np.sqrt(2 * (GAP_M / 2) * m_e / (e * field)))


def scaling_checks() -> list[dict]:
    """Remaining literature checks that need only the summary CSVs.

    1. Fine C: the zero crossings of the e-mode expansion vs B are spaced by
       ΔB = π m_e / (e · ToF) if the distortion is the cyclotron phase of a
       transverse kick applied at the start of the flight (ω_c ToF = nπ).
    2. Block B: the SC-off broadening at 0 G is the initial-velocity smear
       σ_v (added in quadrature); compared with the f/σ_t^e term of PRAB 22.
    3. Ion Block B: h − 1 vs σ₀ power law (impulsive kick ⇒ σ₀⁻²,
       Shiltsev continuous regime ⇒ σ₀⁻¹·⁵).
    4. Ion Block D: Δy = ±5 mm changes the drift length d; the impulsive
       model predicts σ_m² − σ₀² ∝ τ₂² ∝ d.
    """
    rows: list[dict] = []
    fine = load_summary(OUT / "csns_emode_voltage_fine_summary.csv")
    print("Fine C zero-crossing spacing of Δ(B) [G] vs π m_e/(e·ToF), inj 10 mm, 100 kW:")
    for volt in (10, 15, 20, 25, 30):
        pts = sorted(
            (r["b_gs"], r["expansion_vs_no_sc_pct"])
            for r in fine
            if r["power_kw"] == 100 and r["voltage_kv"] == volt and 5 <= r["b_gs"] <= 300
        )
        b = np.array([p[0] for p in pts], float)
        y = np.array([p[1] for p in pts], float)
        zeros = [
            b[i] - y[i] * (b[i + 1] - b[i]) / (y[i + 1] - y[i])
            for i in range(len(b) - 1)
            if y[i] * y[i + 1] < 0
        ]
        spacing = float(np.mean(np.diff(zeros))) if len(zeros) > 1 else np.nan
        tof = _electron_tof(volt)
        pred = np.pi * m_e / (e * tof) * 1e4
        rows.append(dict(check="fineC_zero_spacing", voltage_kv=volt, tof_ns=tof * 1e9, sim=spacing, pred=pred))
        print(f"  {volt:2d} kV: ToF {tof*1e9:4.2f} ns  sim {spacing:5.1f} G ({len(zeros)} zeros)  pred {pred:5.1f} G")

    size = load_summary(OUT / "csns_emode_size_summary.csv")
    print("Block B SC-off smear σ_v = σ₀·√((σ_off/σ₀)² − 1) at 0 G, 100 kW [mm], and PRAB f/σ_t^e [G]:")
    for beam in ("injection", "extraction"):
        sv = []
        for r in size:
            if r["beam"] == beam and r["power_kw"] == 100 and r["b_gs"] == 0:
                ratio = r["sigma_sc_off_mm"] / r["sigma_initial_mm"]
                sv.append(r["sigma_initial_mm"] * np.sqrt(max(ratio**2 - 1, 0)))
        tof = _electron_tof(25)
        v_rms = np.mean(sv) * 1e-3 / tof
        ekin = 0.5 * m_e * v_rms**2 / e
        rows.append(dict(check="blockB_sigma_v", beam=beam, sim=float(np.mean(sv)), pred=np.nan, ekin_ev=ekin))
        print(f"  {beam:10s}: σ_v = {np.mean(sv):.2f} ± {np.std(sv):.2f} mm  → v_rms {v_rms:.2e} m/s, {ekin:.1f} eV per axis")
    for st in (3, 10, 20, 25):
        print(f"  f/σ_t^e at σ_t = {st:2d} mm: {VILS['f'] / st ** VILS['e'] * 1e4:5.0f} G")

    isize = load_summary(OUT / "csns_imode_size_summary.csv")
    print("Ion Block B exponent of (h − 1) vs σ₀ (5–20 mm, 0 G, 100 kW):")
    for slug, label, _ in SPECIES:
        for beam in ("injection", "extraction"):
            pts = [
                (r["sigma_x_mm"], r["expansion_vs_no_sc_pct"])
                for r in isize
                if r["species"] == slug and r["beam"] == beam and r["b_gs"] == 0
                and r["power_kw"] == 100 and 5 <= r["sigma_x_mm"] <= 20
            ]
            k = np.polyfit(np.log([p[0] for p in pts]), np.log([p[1] for p in pts]), 1)[0]
            rows.append(dict(check="ionB_exponent", species=slug, beam=beam, sim=float(k), pred=-2.0))
            print(f"  {label:5s} {beam:10s}: σ₀^{k:+.2f}")

    ioff = load_summary(OUT / "csns_imode_offset_summary.csv")
    print("Ion Block D Δy = ±5 mm (0 G, 100 kW): sim vs σ_m² − σ₀² ∝ d:")
    for slug, label, _ in SPECIES:
        for beam in ("injection", "extraction"):
            sel = {
                r["dy_mm"]: r["expansion_vs_no_sc_pct"]
                for r in ioff
                if r["species"] == slug and r["beam"] == beam and r["b_gs"] == 0
                and r["power_kw"] == 100 and r["dx_mm"] == 0
            }
            h0 = 1 + sel[0] / 100
            preds = {}
            for dy in (-5, 5):
                d_ratio = (GAP_M / 2 + dy * 1e-3) / (GAP_M / 2)
                preds[dy] = 100 * (np.sqrt(1 + (h0**2 - 1) * d_ratio) - 1)
                rows.append(dict(check="ionD_dy", species=slug, beam=beam, dy_mm=dy, sim=sel[dy], pred=preds[dy]))
            print(
                f"  {label:5s} {beam:10s}: dy −5 sim {sel[-5]:5.1f} pred {preds[-5]:5.1f} | "
                f"0: {sel[0]:5.1f} | dy +5 sim {sel[5]:5.1f} pred {preds[5]:5.1f} %"
            )
    return rows


def _zero_crossings(b: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Linear interpolation of B where Δ changes sign."""
    zeros = [
        b[i] - y[i] * (b[i + 1] - b[i]) / (y[i + 1] - y[i])
        for i in range(len(b) - 1)
        if y[i] * y[i + 1] < 0
    ]
    return np.asarray(zeros, float)


def plot_cyclotron(rows: list[dict]) -> Path:
    """Two-panel cyclotron-phase check: Δ(B) zeros and their √V spacing."""
    fine = load_summary(OUT / "csns_emode_voltage_fine_summary.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    ax1.axhspan(-1.0, 1.0, color="0.90", zorder=0)
    ax1.axhline(0, color="k", lw=0.6)
    for volt, color in ((10, "b"), (25, "r")):
        pts = sorted(
            (r["b_gs"], r["expansion_vs_no_sc_pct"])
            for r in fine
            if r["power_kw"] == 100 and r["voltage_kv"] == volt and r["b_gs"] <= 300
        )
        b = np.array([p[0] for p in pts], float)
        y = np.array([p[1] for p in pts], float)
        tof = _electron_tof(volt)
        d_b = np.pi * m_e / (e * tof) * 1e4
        for n in range(1, int(300 / d_b) + 1):
            ax1.axvline(n * d_b, color=color, lw=0.9, ls=":", alpha=0.7)
        ax1.plot(
            b,
            y,
            "-",
            color=color,
            lw=1.6,
            label=rf"{volt:d}\,kV ($\tau={tof*1e9:.1f}$\,ns)",
        )
        zeros = _zero_crossings(b[b >= 5], y[b >= 5])
        ax1.plot(zeros, np.zeros_like(zeros), "o", color=color, ms=5, zorder=5)
    ax1.plot([], [], "k:", lw=0.9, label=r"predicted zeros $n\pi m_e/(e\tau)$")
    ax1.set_xlabel(r"$B$ [G]")
    ax1.set_ylabel(r"$\Delta$ [\%]")
    ax1.set_ylim(-15, 35)
    ax1.set_xlim(0, 300)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top", ha="left")
    ax1.legend(fontsize=11, loc="upper right")

    sel = [r for r in rows if r["check"] == "fineC_zero_spacing"]
    v = np.array([r["voltage_kv"] for r in sel], float)
    ax2.plot(v, [r["sim"] for r in sel], "o", color="r", ms=7, label="Virtual-IPM spacing")
    vv = np.linspace(5, 32, 100)
    ax2.plot(
        vv,
        [np.pi * m_e / (e * _electron_tof(x)) * 1e4 for x in vv],
        "k--",
        lw=1.2,
        label=r"$\pi m_e/(e\tau)\propto\sqrt{V}$",
    )
    ax2.set_xlabel("cage voltage [kV]")
    ax2.set_ylabel(r"spacing of $\Delta(B)$ zeros [G]")
    ax2.set_xlim(5, 32)
    ax2.set_ylim(20, 65)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top", ha="left")
    ax2.legend(fontsize=11, loc="lower right")
    fig.tight_layout()
    path = PLOTS / "csns_review_emode_cyclotron.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def evaluate_imode_voltage_1kv(n_particles: int) -> list[dict]:
    """Kick-model Δ(V) at 1 kV steps, 0 G, injection 10 mm, 100 kW.

    Virtual-IPM Block C anchors the 5 kV grid. B is not scanned: ion
    cyclotron phase is ω_c τ ≲ 1 rad even at 0.1 T, so Δ(V) is the
    relevant ion-mode lever.
    """
    rng = np.random.default_rng(1)
    volt = load_summary(OUT / "csns_imode_voltage_summary.csv")
    voltages = list(range(5, 31))
    rows: list[dict] = []
    for slug, lab, mass_u in SPECIES:
        sim_by_v = {
            int(r["voltage_kv"]): float(r["expansion_vs_no_sc_pct"])
            for r in volt
            if r["species"] == slug and r["power_kw"] == 100 and r["b_gs"] == 0
        }
        for v in voltages:
            model = kick_model(N_100KW, "injection", 10e-3, mass_u, v * 1e3, n_particles, rng) * 100
            sim = sim_by_v.get(v)
            rows.append(
                dict(
                    species=slug,
                    species_label=lab,
                    voltage_kv=v,
                    model_pct=round(model, 2),
                    virtual_ipm_pct="" if sim is None else round(sim, 2),
                )
            )
            mark = f"  VIPM {sim:6.1f}%" if sim is not None else ""
            print(f"  {lab:5s} {v:2d} kV  model {model:6.1f}%{mark}")
    path = OUT / "csns_imode_voltage_1kv.csv"
    keys = ["species", "species_label", "voltage_kv", "model_pct", "virtual_ipm_pct"]
    with path.open("w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join(str(r[k]) for k in keys) + "\n")
    print("wrote", path)
    return rows


def plot_imode_voltage_scan(rows: list[dict]) -> Path:
    """Fig. 9: ion-mode expansion versus cage voltage for the three species."""
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    colors = {"ions": "b", "h2o_ions": "r", "n2_ions": "g"}
    markers = {"ions": "o", "h2o_ions": "s", "n2_ions": "^"}
    for slug, lab, _mass in SPECIES:
        sel = [r for r in rows if r["species"] == slug]
        ax.plot(
            [r["voltage_kv"] for r in sel],
            [r["model_pct"] for r in sel],
            "-",
            color=colors[slug],
            lw=1.6,
            label=lab,
        )
        vipm = [r for r in sel if r["virtual_ipm_pct"] != ""]
        ax.plot(
            [r["voltage_kv"] for r in vipm],
            [r["virtual_ipm_pct"] for r in vipm],
            markers[slug],
            color=colors[slug],
            ms=7,
            zorder=5,
        )
    ax.plot([], [], "k-", lw=1.6, label=r"kick model ($1$\,kV steps)")
    ax.plot([], [], "ko", ms=7, label="Virtual-IPM")
    ax.set_xlabel("cage voltage [kV]")
    ax.set_ylabel(r"$\Delta$ [\%]")
    ax.set_xlim(4, 31)
    ax.set_xticks(range(5, 31, 5))
    ax.set_ylim(0, 420)
    ax.legend(fontsize=12, loc="upper right")
    fig.tight_layout()
    path = PLOTS / "csns_imode_voltage.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def write_checks_table(rows: list[dict]) -> Path:
    path = OUT / "csns_review_scaling_checks.csv"
    keys = ["check", "beam", "species", "voltage_kv", "dy_mm", "tof_ns", "ekin_ev", "sim", "pred"]
    with path.open("w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join("" if r.get(k) is None else str(r.get(k)) for k in keys) + "\n")
    return path


def _delta_from_drift(h0: float, dy_mm: float) -> float:
    """σ_m² − σ₀² ∝ d: predicted Δ(%) after a vertical offset dy."""
    d_ratio = (GAP_M / 2 + dy_mm * 1e-3) / (GAP_M / 2)
    return 100.0 * (np.sqrt(1.0 + (h0**2 - 1.0) * d_ratio) - 1.0)


def plot_orbit_offset_emode() -> Path:
    """Electron-mode Δ versus Δy (Fine D) and Δx (Block D) at 100 kW."""
    fine = load_summary(OUT / "csns_emode_offset_fine_summary.csv")
    coarse = load_summary(OUT / "csns_emode_offset_summary.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    ax1.axhspan(-1.0, 1.0, color="0.90", zorder=0)
    ax1.axhline(0, color="k", lw=0.6)
    style = {
        ("injection", 0): dict(color="b", ls="--", label=r"inj.\ $0\,\mathrm{G}$"),
        ("injection", 300): dict(color="b", ls="-", label=r"inj.\ $300\,\mathrm{G}$"),
        ("extraction", 0): dict(color="r", ls="--", label=r"ext.\ $0\,\mathrm{G}$"),
        ("extraction", 300): dict(color="r", ls="-", label=r"ext.\ $300\,\mathrm{G}$"),
    }
    for beam, b_gs in (("injection", 0), ("injection", 300), ("extraction", 0), ("extraction", 300)):
        pts = sorted(
            (r["dy_mm"], r["expansion_vs_no_sc_pct"])
            for r in fine
            if r["beam"] == beam
            and r["power_kw"] == 100
            and r["b_gs"] == b_gs
            and r["dx_mm"] == 0
        )
        ax1.plot([p[0] for p in pts], [p[1] for p in pts], lw=1.6, **style[(beam, b_gs)])
    ax1.set_xlabel(r"$\Delta y$ [mm] (away from collector)")
    ax1.set_ylabel(r"$\Delta$ [\%]")
    ax1.set_xlim(-10.5, 10.5)
    ax1.set_ylim(-55, 50)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=11, loc="lower right")

    ax2.axhspan(-1.0, 1.0, color="0.90", zorder=0)
    ax2.axhline(0, color="k", lw=0.6)
    for beam, color, lab in (("injection", "b", r"inj.\ $300\,\mathrm{G}$"), ("extraction", "r", r"ext.\ $300\,\mathrm{G}$")):
        pts = sorted(
            (r["dx_mm"], r["expansion_vs_no_sc_pct"])
            for r in coarse
            if r["beam"] == beam
            and r["power_kw"] == 100
            and r["b_gs"] == 300
            and r["dy_mm"] == 0
        )
        ax2.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=color, lw=1.6, ms=7, label=lab)
    ax2.set_xlabel(r"$\Delta x$ [mm]")
    ax2.set_ylabel(r"$\Delta$ [\%]")
    ax2.set_xlim(-0.5, 10.5)
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_xticks([0, 5, 10])
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    ax2.legend(fontsize=11, loc="upper right")
    fig.tight_layout()
    path = PLOTS / "csns_orbit_offset_emode.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_orbit_offset_imode() -> Path:
    """Ion-mode Δ versus Δy and Δx at B = 0, 100 kW (no B scan)."""
    inj = load_summary(OUT / "csns_imode_offset_summary.csv")
    v2 = load_summary(OUT / "csns_v2_summary.csv")
    ext = [
        r
        for r in v2
        if r.get("block") == "I1"
        and r.get("beam") == "extraction"
        and r.get("power_kw") == 100
        and r.get("b_gs") == 0
        and float(r.get("sigma_mm") or 0) == 10
        and int(r.get("voltage_kv") or 0) == 25
    ]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    colors = {"ions": "b", "h2o_ions": "r", "n2_ions": "g"}
    markers = {"ions": "o", "h2o_ions": "s", "n2_ions": "^"}
    dy_line = np.linspace(-5.5, 5.5, 80)
    for slug, lab, _mass in SPECIES:
        color, mk = colors[slug], markers[slug]
        ipts = sorted(
            (r["dy_mm"], r["expansion_vs_no_sc_pct"])
            for r in inj
            if r["species"] == slug
            and r["beam"] == "injection"
            and r["power_kw"] == 100
            and r["b_gs"] == 0
            and r["dx_mm"] == 0
        )
        epts = sorted(
            (r["dy_mm"], r["expansion_vs_no_sc_pct"])
            for r in ext
            if r["species"] == slug and r["dx_mm"] == 0
        )
        ax1.plot([p[0] for p in ipts], [p[1] for p in ipts], mk, color=color, ms=7, label=lab)
        if epts:
            ax1.plot([p[0] for p in epts], [p[1] for p in epts], mk, color=color, ms=7, fillstyle="none")
        if ipts:
            h0 = 1.0 + next(p[1] for p in ipts if p[0] == 0) / 100.0
            ax1.plot(dy_line, [_delta_from_drift(h0, y) for y in dy_line], "-", color=color, lw=1.3)
        if epts:
            h0e = 1.0 + next(p[1] for p in epts if p[0] == 0) / 100.0
            ax1.plot(dy_line, [_delta_from_drift(h0e, y) for y in dy_line], "--", color=color, lw=1.1)
    ax1.plot([], [], "k-", lw=1.2, label=r"$\sigma_m^2-\sigma_0^2\propto d$ (inj.)")
    ax1.plot([], [], "k--", lw=1.1, label=r"aligned ext.")
    ax1.set_xlabel(r"$\Delta y$ [mm] (away from collector)")
    ax1.set_ylabel(r"$\Delta$ [\%]")
    ax1.set_xlim(-6, 6)
    ax1.set_xticks([-5, 0, 5])
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=10, loc="lower right")

    for slug, lab, _mass in SPECIES:
        color, mk = colors[slug], markers[slug]
        ipts = sorted(
            (r["dx_mm"], r["expansion_vs_no_sc_pct"])
            for r in inj
            if r["species"] == slug
            and r["beam"] == "injection"
            and r["power_kw"] == 100
            and r["b_gs"] == 0
            and r["dy_mm"] == 0
        )
        epts = sorted(
            (r["dx_mm"], r["expansion_vs_no_sc_pct"])
            for r in ext
            if r["species"] == slug and r["dy_mm"] == 0
        )
        ax2.plot([p[0] for p in ipts], [p[1] for p in ipts], mk + "-", color=color, ms=7, lw=1.4, label=lab)
        if epts:
            ax2.plot([p[0] for p in epts], [p[1] for p in epts], mk + "--", color=color, ms=7, lw=1.2, fillstyle="none")
    ax2.set_xlabel(r"$\Delta x$ [mm]")
    ax2.set_ylabel(r"$\Delta$ [\%]")
    ax2.set_xlim(-0.5, 10.5)
    ax2.set_xticks([0, 5, 10])
    ax2.set_ylim(0, 120)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    ax2.legend(fontsize=11, loc="upper right")
    fig.tight_layout()
    path = PLOTS / "csns_orbit_offset_imode.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--particles", type=int, default=30000, help="ions per reduced-model case")
    ap.add_argument("--checks-only", action="store_true", help="only print the scaling checks (no plots, no model)")
    ap.add_argument(
        "--imode-voltage",
        action="store_true",
        help="only evaluate the 1 kV ion-mode voltage scan (no Virtual-IPM runs)",
    )
    ap.add_argument(
        "--orbit-offset",
        action="store_true",
        help="only plot closed-orbit offset figures (summary CSVs, no Virtual-IPM runs)",
    )
    args = ap.parse_args()
    plot_conf()
    PLOTS.mkdir(exist_ok=True)

    if args.orbit_offset:
        print("wrote", plot_orbit_offset_emode())
        print("wrote", plot_orbit_offset_imode())
        return

    if args.imode_voltage:
        print("Ion-mode Δ(V), 1 kV steps, 0 G, injection 10 mm, 100 kW:")
        vrows = evaluate_imode_voltage_1kv(args.particles)
        print("wrote", plot_imode_voltage_scan(vrows))
        return

    checks = scaling_checks()
    print("wrote", write_checks_table(checks))
    print("wrote", plot_cyclotron(checks))
    if args.checks_only:
        return

    thr = emode_thresholds()
    print("E-mode 1% thresholds [G] vs PRAB 22, 052801 Eq. (8):")
    for (beam, sig), by_power in sorted(thr.items()):
        for power, b in sorted(by_power.items()):
            n12 = N_100KW * power / 100 / 1e12
            fit = b_min_1pct(n12, SIGMA_T_NS[beam], sig) * 1e4
            fit_b = b_min_1pct(n12 / BETA[beam], SIGMA_T_NS[beam], sig) * 1e4
            print(f"  {beam:10s} {sig:2d} mm {power:3d} kW: sim {b:5.0f} G   fit {fit:4.0f} G   fit(N/β) {fit_b:4.0f} G")
    print("wrote", plot_emode(thr))
    print("wrote", plot_imode(args.particles))
    print("wrote", write_model_table(args.particles))


if __name__ == "__main__":
    main()
