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
from scipy.constants import atomic_mass, c, e, epsilon_0

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
    ax.set_ylim(0, 430)
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
    t_gen = rng.normal(TRAIN[beam]["gen_center"], sig_t, n)
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--particles", type=int, default=30000, help="ions per reduced-model case")
    args = ap.parse_args()
    plot_conf()
    PLOTS.mkdir(exist_ok=True)

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


if __name__ == "__main__":
    main()
