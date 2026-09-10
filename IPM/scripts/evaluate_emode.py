#!/usr/bin/env python3
"""Evaluate the replanned e-mode size × B × power scans."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import summarize_pair  # noqa: E402
from generate_csns_configs import (  # noqa: E402
    EMODE_B_GS,
    EMODE_SIG10_B_GS,
    POWERS_KW,
    SIZE_MM,
    emode_csv_name,
)

BEAMS = (
    ("injection", "Injection 80 MeV"),
    ("extraction", "Extraction 1.6 GeV"),
)
B_LABELS = {
    0: "B = 0",
    250: "B = 250 G",
    1000: r"B = 0.1 T (1000 G)",
}


def emode_paths(emode_dir: Path, beam: str, sigma_mm: int, power_kw: int, b_gs: int):
    on = emode_dir / emode_csv_name(beam, sigma_mm, power_kw, b_gs, True)
    off = emode_dir / emode_csv_name(beam, sigma_mm, 100, b_gs, False)
    return on, off


def collect_size_rows(emode_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for beam, _title in BEAMS:
        for power_kw in POWERS_KW:
            for b_gs in EMODE_B_GS:
                for sigma_mm in SIZE_MM:
                    on, off = emode_paths(emode_dir, beam, sigma_mm, power_kw, b_gs)
                    row = summarize_pair(on, off, f"{beam}_electrons", b_gs)
                    if row is None:
                        continue
                    row["beam"] = beam
                    row["power_kw"] = power_kw
                    row["sigma_x_mm"] = sigma_mm
                    rows.append(row)
    return rows


def collect_sig10_rows(emode_dir: Path, bscan5_dir: Path, sig10_dir: Path) -> list[dict]:
    """10 mm injection expansion vs B, all powers (100 kW from the fine scan)."""
    rows: list[dict] = []
    for power_kw in POWERS_KW:
        for b_gs in EMODE_SIG10_B_GS:
            on, off = emode_paths(emode_dir, "injection", 10, power_kw, b_gs)
            if not on.is_file() or not off.is_file():
                if power_kw == 100 and b_gs == 1000:
                    on = sig10_dir / "csns_injection_electrons_sig10_sc_on.csv"
                    off = sig10_dir / "csns_injection_electrons_sig10_sc_off.csv"
                elif power_kw == 100 and b_gs <= 250:
                    on = bscan5_dir / f"csns_injection_electrons_sig10_b{b_gs}G_sc_on.csv"
                    off = bscan5_dir / f"csns_injection_electrons_sig10_b{b_gs}G_sc_off.csv"
            row = summarize_pair(on, off, "injection_electrons_sig10", b_gs)
            if row is None:
                continue
            row["beam"] = "injection"
            row["power_kw"] = power_kw
            row["sigma_x_mm"] = 10
            rows.append(row)
    return rows


def plot_size_grid(
    rows: list[dict],
    plot_dir: Path,
    value_key: str,
    ylabel: str,
    filename: str,
    diagonal: bool = False,
) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13.6, 8.0), sharex=True, sharey=True)
    lims = np.array(SIZE_MM, dtype=float)
    for row_i, (beam, beam_title) in enumerate(BEAMS):
        for col_i, b_gs in enumerate(EMODE_B_GS):
            ax = axes[row_i, col_i]
            for power_kw in POWERS_KW:
                series = sorted(
                    (
                        r
                        for r in rows
                        if r["beam"] == beam
                        and r["b_gs"] == b_gs
                        and r["power_kw"] == power_kw
                    ),
                    key=lambda r: r["sigma_x_mm"],
                )
                if not series:
                    continue
                ax.plot(
                    [r["sigma_x_mm"] for r in series],
                    [r[value_key] for r in series],
                    "o-",
                    ms=3.0,
                    lw=1.1,
                    label=f"{power_kw} kW",
                )
            if diagonal:
                ax.plot(lims, lims, "k--", lw=0.9, label="obtained = true")
            else:
                ax.axhline(0.0, color="0.5", lw=0.8)
            ax.set_title(f"{beam_title}, {B_LABELS[b_gs]}")
            ax.grid(True, alpha=0.3)
            if row_i == 1:
                ax.set_xlabel("True beam size [mm]")
            if col_i == 0:
                ax.set_ylabel(ylabel)
            if row_i == 0 and col_i == 0:
                ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(plot_dir / filename, dpi=150)
    print(f"Wrote {plot_dir / filename}")


def plot_sig10_power(rows: list[dict], plot_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for power_kw in POWERS_KW:
        series = sorted(
            (r for r in rows if r["power_kw"] == power_kw),
            key=lambda r: r["b_gs"],
        )
        if not series:
            continue
        ax.plot(
            [r["b_gs"] for r in series],
            [r["expansion_vs_no_sc_pct"] for r in series],
            "o-",
            ms=4.0,
            lw=1.2,
            label=f"{power_kw} kW",
        )
    ax.axhline(0.0, color="0.5", lw=0.8)
    ax.axhline(-1.0, color="0.7", ls="--", lw=0.7)
    ax.axhline(1.0, color="0.7", ls="--", lw=0.7)
    ax.set_xlabel("B [G]")
    ax.set_ylabel("profile expansion vs no SC [%]")
    ax.set_title("Injection 80 MeV, e− (10×8 mm)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_emode_sig10_power.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_emode_sig10_power.png'}")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emode-dir", default="output/emode", type=Path)
    parser.add_argument("--bscan5-dir", default="output/bscan5", type=Path)
    parser.add_argument("--sig10-dir", default="output", type=Path)
    parser.add_argument("--plot-dir", default="plots", type=Path)
    parser.add_argument("--summary", default="output/csns_emode_summary.csv")
    parser.add_argument("--summary-sig10", default="output/csns_emode_sig10_summary.csv")
    args = parser.parse_args()
    args.plot_dir.mkdir(parents=True, exist_ok=True)

    size_rows = collect_size_rows(args.emode_dir)
    sig10_rows = collect_sig10_rows(args.emode_dir, args.bscan5_dir, args.sig10_dir)

    if size_rows:
        plot_size_grid(
            size_rows,
            args.plot_dir,
            "expansion_vs_no_sc_pct",
            "Expansion vs no SC [%]",
            "csns_emode_expansion.png",
        )
        plot_size_grid(
            size_rows,
            args.plot_dir,
            "sigma_sc_on_mm",
            "Obtained beam size [mm]",
            "csns_emode_obtained.png",
            diagonal=True,
        )
    if sig10_rows:
        plot_sig10_power(sig10_rows, args.plot_dir)

    write_csv(Path(args.summary), size_rows)
    write_csv(Path(args.summary_sig10), sig10_rows)

    print()
    print("E-mode size scan at σ_x = 3, 10, 20 mm:")
    for beam, beam_title in BEAMS:
        for b_gs in EMODE_B_GS:
            for sigma_mm in (3, 10, 20):
                bits = []
                for power_kw in POWERS_KW:
                    hit = [
                        r
                        for r in size_rows
                        if r["beam"] == beam
                        and r["b_gs"] == b_gs
                        and r["power_kw"] == power_kw
                        and r["sigma_x_mm"] == sigma_mm
                    ]
                    if hit:
                        bits.append(
                            f"{power_kw}kW {hit[0]['expansion_vs_no_sc_pct']:+.2f}%"
                            f" → {hit[0]['sigma_sc_on_mm']:.2f} mm"
                        )
                if bits:
                    print(f"  {beam_title}, {B_LABELS[b_gs]}, {sigma_mm} mm: " + ", ".join(bits))
    print("10 mm injection e− vs B:")
    for power_kw in POWERS_KW:
        series = sorted(
            (r for r in sig10_rows if r["power_kw"] == power_kw),
            key=lambda r: r["b_gs"],
        )
        if not series:
            continue
        bits = [f"{r['b_gs']}G {r['expansion_vs_no_sc_pct']:+.2f}%" for r in series]
        print(f"  {power_kw} kW: " + ", ".join(bits))

    if not size_rows and not sig10_rows:
        raise SystemExit("No e-mode replan outputs found")


if __name__ == "__main__":
    main()
