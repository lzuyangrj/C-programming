#!/usr/bin/env python3
"""Evaluate e-mode guiding-B scan: 0–250 G in 5 G steps."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import load_xy, stats, summarize_pair  # noqa: E402

B_SCAN5_GS = tuple(range(0, 251, 5))
PROFILE_GS = (0, 50, 100, 150, 200, 250)
FAMILIES = [
    ("injection_electrons", "Injection 80 MeV, e− (25×20 mm)"),
    ("extraction_electrons", "Extraction 1.6 GeV, e− (10×8 mm)"),
    ("injection_electrons_sig10", "Injection 80 MeV, e− (10×8 mm)"),
]
ION_SIG10 = "injection_ions_sig10"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output/bscan5", type=Path)
    parser.add_argument("--ion-dir", default="output/bscan", type=Path)
    parser.add_argument("--plot-dir", default="plots", type=Path)
    parser.add_argument("--summary", default="output/csns_bscan5_summary.csv")
    args = parser.parse_args()
    plot_dir = args.plot_dir
    plot_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    missing = 0
    for key, _title in FAMILIES:
        for b_gs in B_SCAN5_GS:
            stem = f"csns_{key}_b{b_gs}G"
            row = summarize_pair(
                args.output_dir / f"{stem}_sc_on.csv",
                args.output_dir / f"{stem}_sc_off.csv",
                key,
                b_gs,
            )
            if row is None:
                missing += 1
                continue
            rows.append(row)

    if not rows:
        raise SystemExit(f"No completed fine B-scan pairs in {args.output_dir}")

    by_family = {key: [] for key, _ in FAMILIES}
    for row in rows:
        by_family[row["family"]].append(row)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.5))
    for key, title in FAMILIES:
        series = sorted(by_family[key], key=lambda r: r["b_gs"])
        if not series:
            continue
        b = [r["b_gs"] for r in series]
        axes[0].plot(b, [r["expansion_vs_no_sc_pct"] for r in series], "-", lw=1.4, label=title)
        axes[1].plot(b, [r["sigma_sc_on_mm"] for r in series], "-", lw=1.4, label=f"{title}, SC on")
        axes[1].plot(
            b,
            [r["sigma_sc_off_mm"] for r in series],
            "--",
            lw=1.0,
            alpha=0.7,
            label=f"{title}, SC off",
        )
    axes[0].axhline(0.0, color="0.5", lw=0.8)
    axes[0].set_xlabel("B [G]")
    axes[0].set_ylabel("profile expansion vs no SC [%]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=7)
    axes[1].set_xlabel("B [G]")
    axes[1].set_ylabel("σ_x [mm]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_bscan5_expansion.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_bscan5_expansion.png'}")

    fig, axes = plt.subplots(3, 6, figsize=(19.0, 9.2))
    drawn_legend = False
    for row, (key, title) in enumerate(FAMILIES):
        for col, b_gs in enumerate(PROFILE_GS):
            ax = axes[row, col]
            stem = f"csns_{key}_b{b_gs}G"
            on_path = args.output_dir / f"{stem}_sc_on.csv"
            off_path = args.output_dir / f"{stem}_sc_off.csv"
            if not on_path.is_file() or not off_path.is_file():
                ax.set_title(f"{title}\n{b_gs} G (missing)", fontsize=8)
                continue
            xi_on, xf_on, _, nd_on = load_xy(on_path)
            _, xf_off, _, nd_off = load_xy(off_path)
            if nd_on == 0 and nd_off == 0:
                ax.set_title(f"{title}\n{b_gs} G (no DETECTED)", fontsize=8)
                continue
            stacked = np.concatenate([a for a in (xf_on, xf_off, xi_on) if a.size])
            lim = float(np.nanmax(np.abs(stacked))) if stacked.size else 1.0
            edges = np.linspace(-lim * 1.05, lim * 1.05, 81)
            ax.hist(xi_on, bins=edges, histtype="step", linewidth=1.1, label="initial", color="0.45")
            ax.hist(xf_off, bins=edges, histtype="step", linewidth=1.5, label="no space charge")
            ax.hist(xf_on, bins=edges, histtype="step", linewidth=1.5, label="with space charge")
            s_off = stats(xf_off)["rms"]
            s_on = stats(xf_on)["rms"]
            expansion = 100.0 * (s_on / s_off - 1.0) if s_off else float("nan")
            ax.set_title(
                f"{title}\n{b_gs} G: σ_off={s_off:.2f}, σ_on={s_on:.2f} ({expansion:+.1f}%)",
                fontsize=8,
            )
            ax.set_xlabel("x [mm]", fontsize=8)
            ax.grid(True, alpha=0.3)
            if not drawn_legend:
                ax.legend(fontsize=7)
                ax.set_ylabel("counts")
                drawn_legend = True
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_bscan5_electron_profiles.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_bscan5_electron_profiles.png'}")

    ion_rows = []
    for b_gs in (0, 50, 100, 200, 250):
        stem = f"csns_{ION_SIG10}_b{b_gs}G"
        row = summarize_pair(
            args.ion_dir / f"{stem}_sc_on.csv",
            args.ion_dir / f"{stem}_sc_off.csv",
            ION_SIG10,
            b_gs,
        )
        if row is not None:
            ion_rows.append(row)
            rows.append(row)

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {summary_path}")
    print()
    print(
        f"{'family':<28} {'B[G]':>6} {'σ_off':>8} {'σ_on':>8} "
        f"{'Δ%':>8} {'det_on':>8}"
    )
    for row in rows:
        if row["family"] != ION_SIG10 and row["b_gs"] not in PROFILE_GS:
            continue
        print(
            f"{row['family']:<28} {row['b_gs']:6d} "
            f"{row['sigma_sc_off_mm']:8.3f} "
            f"{row['sigma_sc_on_mm']:8.3f} "
            f"{row['expansion_vs_no_sc_pct']:7.2f}% "
            f"{row['detected_frac_on']:8.3f}"
        )
    if ion_rows:
        print("\nInjection H₂⁺ at σ = 10×8 mm (coarse B scan):")
        for row in ion_rows:
            print(
                f"  {row['b_gs']:3d} G  expansion {row['expansion_vs_no_sc_pct']:+.2f}%  "
                f"σ {row['sigma_sc_off_mm']:.3f} → {row['sigma_sc_on_mm']:.3f} mm"
            )
    if missing:
        print(f"\n({missing} e-mode pair(s) missing)")


if __name__ == "__main__":
    main()
