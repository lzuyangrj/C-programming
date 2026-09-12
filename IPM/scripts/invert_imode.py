#!/usr/bin/env python3
"""Invert CSNS ion-mode widths using the Virtual-IPM look-up (I2 / Block B).

σ_m(σ_0) is not one-to-one: it has a minimum, so a single ToF peak has two
roots. The H₂⁺/N₂⁺ ratio is monotonic and selects a unique σ_0. This script
builds that correction from the existing summary CSVs (no Virtual-IPM runs).
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


def invert_ratio(
    ratio: float, sigma0: np.ndarray, sm_a: np.ndarray, sm_b: np.ndarray
) -> float:
    """Invert a monotonic σ_m^A / σ_m^B versus σ_0 (leave-one-out safe)."""
    r = sm_a / sm_b
    # ratio falls with σ_0 for H2+/N2+
    if r[0] < r[-1]:
        sigma0, r = sigma0[::-1], r[::-1]
    return float(_interp(r, sigma0)(ratio))


def leave_one_out_ratio(sigma0: np.ndarray, sm_h2: np.ndarray, sm_n2: np.ndarray) -> np.ndarray:
    rec = np.full_like(sigma0, np.nan, dtype=float)
    for i in range(len(sigma0)):
        mask = np.ones(len(sigma0), bool)
        mask[i] = False
        if mask.sum() < 3:
            continue
        rec[i] = invert_ratio(sm_h2[i] / sm_n2[i], sigma0[mask], sm_h2[mask], sm_n2[mask])
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
    s0 = tab["ions"]["sigma0"]
    for slug, lab in SPECIES:
        ax1.plot(tab[slug]["sigma0"], tab[slug]["sigmam"], "o-", color=COLORS[slug], lw=1.5, ms=5, label=lab)
    ax1.axhline(
        tab["ions"]["sigmam"][np.argmin(np.abs(s0 - 10))],
        color="b",
        ls=":",
        lw=0.9,
        label=r"$\sigma_m=19.16$\,mm ($10$\,mm $\mathrm{H}_2^+$)",
    )
    ax1.set_xlabel(r"true $\sigma_0$ [mm]")
    ax1.set_ylabel(r"collected $\sigma_m$ [mm]")
    ax1.set_xlim(2.5, 20.5)
    ax1.set_ylim(12, 30)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=11, loc="upper right")

    ratio = tab["ions"]["sigmam"] / tab["n2_ions"]["sigmam"]
    ax2.plot(s0, ratio, "ko-", lw=1.5, ms=5)
    ax2.set_xlabel(r"true $\sigma_0$ [mm]")
    ax2.set_ylabel(r"$\sigma_m(\mathrm{H}_2^+)/\sigma_m(\mathrm{N}_2^+)$")
    ax2.set_xlim(2.5, 20.5)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    fig.tight_layout()
    path = PLOTS / "csns_imode_inversion_curves.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_recover(inj: dict, ext: dict) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8))
    h2 = inj[("ions", 100)]
    n2 = inj[("n2_ions", 100)]
    s0 = h2["sigma0"]
    large = leave_one_out_large(s0, h2["sigmam"])
    two = leave_one_out_ratio(s0, h2["sigmam"], n2["sigmam"])
    ax1.plot([2, 21], [2, 21], "k--", lw=0.8)
    ax1.plot(s0, h2["sigmam"], "s", color="0.55", ms=6, label=r"uncorrected $\sigma_m$")
    ax1.plot(s0, large, "o", color="b", ms=6, label=r"single-species, large root")
    ax1.plot(s0, two, "^", color="r", ms=7, label=r"$\mathrm{H}_2^+/\mathrm{N}_2^+$ ratio")
    ax1.set_xlabel(r"true $\sigma_0$ [mm]")
    ax1.set_ylabel(r"recovered $\sigma_0$ [mm]")
    ax1.set_xlim(2.5, 20.5)
    ax1.set_ylim(2.5, 30)
    ax1.text(0.03, 0.96, r"(a)", transform=ax1.transAxes, va="top")
    ax1.legend(fontsize=10, loc="upper left")

    # residuals of the two-species invert vs power (injection)
    for power, mk in ((100, "o"), (200, "s"), (300, "^")):
        if ("ions", power) not in inj or ("n2_ions", power) not in inj:
            continue
        a, b = inj[("ions", power)], inj[("n2_ions", power)]
        rec = leave_one_out_ratio(a["sigma0"], a["sigmam"], b["sigmam"])
        wall = (a["frac"] < 0.995) | (a["sigmam"] > 40.0)
        good = ~np.isnan(rec)
        ax2.plot(
            a["sigma0"][good & ~wall],
            100 * (rec[good & ~wall] / a["sigma0"][good & ~wall] - 1),
            mk,
            color="b",
            ms=6,
            label=rf"{power}\,kW",
        )
        if wall.any():
            ax2.plot(
                a["sigma0"][good & wall],
                100 * (rec[good & wall] / a["sigma0"][good & wall] - 1),
                mk,
                color="0.6",
                ms=6,
                fillstyle="none",
            )
    ax2.axhline(0, color="k", lw=0.6)
    ax2.axhspan(-2, 2, color="0.90", zorder=0)
    ax2.set_xlabel(r"true $\sigma_0$ [mm]")
    ax2.set_ylabel(r"two-species residual [\%]")
    ax2.set_xlim(2.5, 20.5)
    ax2.set_ylim(-15, 15)
    ax2.text(0.03, 0.96, r"(b)", transform=ax2.transAxes, va="top")
    ax2.legend(fontsize=10, loc="upper right", ncol=2)
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
        "sigmam_h2_mm",
        "sigmam_n2_mm",
        "ratio",
        "rec_large_mm",
        "rec_ratio_mm",
        "residual_ratio_pct",
        "frac_h2",
    ]
    rows = []
    for beam, table in (("injection", inj), ("extraction", ext)):
        for power in sorted({p for (_s, p) in table}):
            if ("ions", power) not in table or ("n2_ions", power) not in table:
                continue
            h2, n2 = table[("ions", power)], table[("n2_ions", power)]
            # align on common σ_0
            s0 = np.array(sorted(set(h2["sigma0"]) & set(n2["sigma0"])))
            if len(s0) < 4:
                continue
            sm_h = _interp(h2["sigma0"], h2["sigmam"])(s0)
            sm_n = _interp(n2["sigma0"], n2["sigmam"])(s0)
            fr = _interp(h2["sigma0"], h2["frac"])(s0)
            large = leave_one_out_large(s0, sm_h)
            two = leave_one_out_ratio(s0, sm_h, sm_n)
            for i, s in enumerate(s0):
                rows.append(
                    dict(
                        beam=beam,
                        power_kw=power,
                        sigma0_mm=round(float(s), 2),
                        sigmam_h2_mm=round(float(sm_h[i]), 3),
                        sigmam_n2_mm=round(float(sm_n[i]), 3),
                        ratio=round(float(sm_h[i] / sm_n[i]), 4),
                        rec_large_mm="" if np.isnan(large[i]) else round(float(large[i]), 3),
                        rec_ratio_mm="" if np.isnan(two[i]) else round(float(two[i]), 3),
                        residual_ratio_pct=""
                        if np.isnan(two[i])
                        else round(100 * (float(two[i]) / float(s) - 1), 3),
                        frac_h2=round(float(fr[i]), 3),
                    )
                )
    with path.open("w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join(str(r[k]) for k in keys) + "\n")
    return path


def report_stats(inj: dict, ext: dict) -> None:
    h2, n2 = inj[("ions", 100)], inj[("n2_ions", 100)]
    s0 = h2["sigma0"]
    two = leave_one_out_ratio(s0, h2["sigmam"], n2["sigmam"])
    large = leave_one_out_large(s0, h2["sigmam"])
    err = 100 * (two / s0 - 1)
    print("Injection 100 kW, 25 kV, B = 0:")
    print(f"  H2+ σ_m minimum {h2['sigmam'].min():.2f} mm at σ0 = {s0[h2['sigmam'].argmin()]:.0f} mm")
    print(f"  two-species |residual| : median {np.nanmedian(np.abs(err)):.2f} %  "
          f"max {np.nanmax(np.abs(err)):.2f} %")
    print(f"  large-root |error| for σ0<=8 mm : "
          f"{np.nanmedian(np.abs(100*(large[s0<=8]/s0[s0<=8]-1))):.1f} % median")
    i10 = int(np.argmin(np.abs(s0 - 10)))
    print(
        f"  worked example σ0=10 mm: σm(H2+)={h2['sigmam'][i10]:.2f}  "
        f"σm(N2+)={n2['sigmam'][i10]:.2f}  ratio={h2['sigmam'][i10]/n2['sigmam'][i10]:.3f}  "
        f"rec={two[i10]:.2f} mm  large={large[i10]:.2f} mm"
    )
    for power in (200, 300, 400, 500):
        a, b = inj[("ions", power)], inj[("n2_ions", power)]
        rec = leave_one_out_ratio(a["sigma0"], a["sigmam"], b["sigmam"])
        wall = (a["frac"] < 0.995) | (a["sigmam"] > 40.0)
        good = ~np.isnan(rec) & ~wall
        if good.any():
            e = 100 * (rec[good] / a["sigma0"][good] - 1)
            print(f"  {power} kW inside-cage two-species |res| median {np.median(np.abs(e)):.2f} %  "
                  f"n={good.sum()}  wall={int(wall.sum())}")
        else:
            print(f"  {power} kW: no inside-cage two-species recovery (wall)")
    if ("ions", 100) in ext and ("n2_ions", 100) in ext:
        a, b = ext[("ions", 100)], ext[("n2_ions", 100)]
        rec = leave_one_out_ratio(a["sigma0"], a["sigmam"], b["sigmam"])
        e = 100 * (rec / a["sigma0"] - 1)
        print("Aligned extraction 100 kW:")
        print(f"  two-species |res| median {np.nanmedian(np.abs(e)):.2f} %  max {np.nanmax(np.abs(e)):.2f} %")
        print(f"  H2+ σ_m: " + ", ".join(f"{s:.0f}→{m:.1f}" for s, m in zip(a["sigma0"], a["sigmam"])))


def main() -> None:
    plot_conf()
    PLOTS.mkdir(exist_ok=True)
    inj = injection_size_table()
    ext = extraction_aligned_table()
    report_stats(inj, ext)
    print("wrote", write_table(inj, ext))
    print("wrote", plot_curves(inj))
    print("wrote", plot_recover(inj, ext))


if __name__ == "__main__":
    main()
