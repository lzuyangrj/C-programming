#!/usr/bin/env python3
"""Evaluate e-mode B-scans vs power and ion-mode beam-size scans vs power."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import summarize_pair  # noqa: E402
from generate_csns_configs import B_SCAN5_GS, ION_SPECIES, POWERS_KW, SIZE_MM  # noqa: E402

E_FAMILIES = (
    ("injection_electrons", "Injection 80 MeV, e− (25×20 mm)"),
    ("extraction_electrons", "Extraction 1.6 GeV, e− (10×8 mm)"),
)
ION_BEAMS = (
    ("injection", "Injection 80 MeV"),
    ("extraction", "Extraction 1.6 GeV"),
)


def emode_paths(base: Path, power_dir: Path, family: str, b_gs: int, power_kw: int):
    off = base / f"csns_{family}_b{b_gs}G_sc_off.csv"
    if power_kw == 100:
        on = base / f"csns_{family}_b{b_gs}G_sc_on.csv"
    else:
        on = power_dir / f"csns_{family}_p{power_kw}kW_b{b_gs}G_sc_on.csv"
    return on, off


def ion_paths(size_dir: Path, beam: str, slug: str, sigma_mm: int, power_kw: int):
    on = size_dir / f"csns_{beam}_{slug}_s{sigma_mm}mm_p{power_kw}kw_sc_on.csv"
    off = size_dir / f"csns_{beam}_ions_s{sigma_mm}mm_p100kw_sc_off.csv"
    return on, off


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bscan-dir", default="output/bscan5", type=Path)
    parser.add_argument("--power-dir", default="output/bscan5_power", type=Path)
    parser.add_argument("--size-dir", default="output/ionsize", type=Path)
    parser.add_argument("--plot-dir", default="plots", type=Path)
    parser.add_argument("--summary-b", default="output/csns_bscan_power_summary.csv")
    parser.add_argument("--summary-size", default="output/csns_ionsize_summary.csv")
    args = parser.parse_args()
    args.plot_dir.mkdir(parents=True, exist_ok=True)

    brow: list[dict] = []
    for family, _title in E_FAMILIES:
        for power_kw in POWERS_KW:
            for b_gs in B_SCAN5_GS:
                on, off = emode_paths(args.bscan_dir, args.power_dir, family, b_gs, power_kw)
                row = summarize_pair(on, off, family, b_gs)
                if row is None:
                    continue
                row["power_kw"] = power_kw
                brow.append(row)

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.6), sharey=True)
    for ax, (family, title) in zip(axes, E_FAMILIES):
        for power_kw in POWERS_KW:
            series = sorted(
                (r for r in brow if r["family"] == family and r["power_kw"] == power_kw),
                key=lambda r: r["b_gs"],
            )
            if not series:
                continue
            ax.plot(
                [r["b_gs"] for r in series],
                [r["expansion_vs_no_sc_pct"] for r in series],
                "-",
                lw=1.3,
                label=f"{power_kw} kW",
            )
        ax.axhline(0.0, color="0.5", lw=0.8)
        ax.set_title(title)
        ax.set_xlabel("B [G]")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("profile expansion vs no SC [%]")
    fig.tight_layout()
    fig.savefig(args.plot_dir / "csns_bscan_power_expansion.png", dpi=150)
    print(f"Wrote {args.plot_dir / 'csns_bscan_power_expansion.png'}")

    srow: list[dict] = []
    for beam, _title in ION_BEAMS:
        for slug, _rest, label in ION_SPECIES:
            for power_kw in POWERS_KW:
                for sigma_mm in SIZE_MM:
                    on, off = ion_paths(args.size_dir, beam, slug, sigma_mm, power_kw)
                    row = summarize_pair(on, off, f"{beam}_{slug}", 1000)
                    if row is None:
                        continue
                    row["power_kw"] = power_kw
                    row["sigma_x_mm"] = sigma_mm
                    row["species"] = label
                    row["slug"] = slug
                    srow.append(row)

    fig, axes = plt.subplots(2, 3, figsize=(13.6, 8.0), sharex=True, sharey=True)
    for row_i, (beam, beam_title) in enumerate(ION_BEAMS):
        for col_i, (slug, _rest, label) in enumerate(ION_SPECIES):
            ax = axes[row_i, col_i]
            for power_kw in POWERS_KW:
                series = sorted(
                    (
                        r
                        for r in srow
                        if r["slug"] == slug
                        and r["family"] == f"{beam}_{slug}"
                        and r["power_kw"] == power_kw
                    ),
                    key=lambda r: r["sigma_x_mm"],
                )
                if not series:
                    continue
                ax.plot(
                    [r["sigma_x_mm"] for r in series],
                    [r["expansion_vs_no_sc_pct"] for r in series],
                    "o-",
                    ms=3.0,
                    lw=1.1,
                    label=f"{power_kw} kW",
                )
            ax.set_title(f"{beam_title}, {label}")
            ax.grid(True, alpha=0.3)
            if row_i == 1:
                ax.set_xlabel("True beam size [mm]")
            if col_i == 0:
                ax.set_ylabel("Expansion vs no SC [%]")
            if row_i == 0 and col_i == 0:
                ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(args.plot_dir / "csns_ionsize_expansion.png", dpi=150)
    print(f"Wrote {args.plot_dir / 'csns_ionsize_expansion.png'}")

    fig, axes = plt.subplots(2, 3, figsize=(13.6, 8.0), sharex=True, sharey=True)
    lims = np.array(SIZE_MM, dtype=float)
    for row_i, (beam, beam_title) in enumerate(ION_BEAMS):
        for col_i, (slug, _rest, label) in enumerate(ION_SPECIES):
            ax = axes[row_i, col_i]
            for power_kw in POWERS_KW:
                series = sorted(
                    (
                        r
                        for r in srow
                        if r["slug"] == slug
                        and r["family"] == f"{beam}_{slug}"
                        and r["power_kw"] == power_kw
                    ),
                    key=lambda r: r["sigma_x_mm"],
                )
                if not series:
                    continue
                ax.plot(
                    [r["sigma_x_mm"] for r in series],
                    [r["sigma_sc_on_mm"] for r in series],
                    "o-",
                    ms=3.0,
                    lw=1.1,
                    label=f"{power_kw} kW",
                )
            ax.plot(lims, lims, "k--", lw=0.9, label="obtained = true")
            ax.set_title(f"{beam_title}, {label}")
            ax.grid(True, alpha=0.3)
            if row_i == 1:
                ax.set_xlabel("True beam size [mm]")
            if col_i == 0:
                ax.set_ylabel("Obtained beam size [mm]")
            if row_i == 0 and col_i == 0:
                ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(args.plot_dir / "csns_ionsize_obtained.png", dpi=150)
    fig.savefig(args.plot_dir / "csns_ionsize_sigma.png", dpi=150)
    print(f"Wrote {args.plot_dir / 'csns_ionsize_obtained.png'}")
    print(f"Wrote {args.plot_dir / 'csns_ionsize_sigma.png'}")

    if brow:
        path = Path(args.summary_b)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(brow[0].keys()))
            writer.writeheader()
            writer.writerows(brow)
        print(f"Wrote {path}")
    if srow:
        path = Path(args.summary_size)
        with path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(srow[0].keys()))
            writer.writeheader()
            writer.writerows(srow)
        print(f"Wrote {path}")

    print()
    print("E-mode |Δ| at B=250 G:")
    for family, title in E_FAMILIES:
        for power_kw in POWERS_KW:
            hit = [
                r
                for r in brow
                if r["family"] == family and r["power_kw"] == power_kw and r["b_gs"] == 250
            ]
            if hit:
                print(
                    f"  {title}, {power_kw} kW: {hit[0]['expansion_vs_no_sc_pct']:+.2f}% "
                    f"(σ {hit[0]['sigma_sc_off_mm']:.2f} → {hit[0]['sigma_sc_on_mm']:.2f} mm)"
                )
    print("Ion-mode expansion at σ_x = 3, 10, 20 mm:")
    for beam, beam_title in ION_BEAMS:
        for slug, _rest, label in ION_SPECIES:
            for sigma_mm in (3, 10, 20):
                bits = []
                for power_kw in POWERS_KW:
                    hit = [
                        r
                        for r in srow
                        if r["family"] == f"{beam}_{slug}"
                        and r["power_kw"] == power_kw
                        and r["sigma_x_mm"] == sigma_mm
                    ]
                    if hit:
                        bits.append(
                            f"{power_kw}kW {hit[0]['expansion_vs_no_sc_pct']:+.1f}%"
                            f" → {hit[0]['sigma_sc_on_mm']:.2f} mm"
                        )
                if bits:
                    print(f"  {beam_title} {label}, {sigma_mm} mm: " + ", ".join(bits))

    if not brow and not srow:
        raise SystemExit("No extended-scan outputs found")


if __name__ == "__main__":
    main()
