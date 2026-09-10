#!/usr/bin/env python3
"""Evaluate the replanned e-mode scans: 0–300 G / 5 G B-scans and σ_x size scans."""

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
    EMODE_BSCAN_GS,
    EMODE_REF_BEAMS,
    EMODE_SIZE_B_GS,
    POWERS_KW,
    SIZE_MM,
    emode_csv_name,
    link_existing_emode_outputs,
)

BEAM_TITLES = {"injection": "Injection 80 MeV", "extraction": "Extraction 1.6 GeV"}


def b_label(b_gs: int) -> str:
    return "B = 0.1 T (1000 G)" if b_gs == 1000 else f"B = {b_gs} G"


def ref_title(beam: str, sigma_mm: int) -> str:
    sy = round(sigma_mm * 0.8)
    return f"{BEAM_TITLES[beam]}, e− ({sigma_mm}×{sy} mm)"


def emode_paths(emode_dir: Path, beam: str, sigma_mm: int, power_kw: int, b_gs: int):
    on = emode_dir / emode_csv_name(beam, sigma_mm, power_kw, b_gs, True)
    off = emode_dir / emode_csv_name(beam, sigma_mm, 100, b_gs, False)
    return on, off


def collect(emode_dir: Path, beam: str, sigma_mm: int, power_kw: int, b_gs: int) -> dict | None:
    on, off = emode_paths(emode_dir, beam, sigma_mm, power_kw, b_gs)
    row = summarize_pair(on, off, f"{beam}_electrons", b_gs)
    if row is None:
        return None
    row["beam"] = beam
    row["power_kw"] = power_kw
    row["sigma_x_mm"] = sigma_mm
    return row


def collect_bscan_rows(emode_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for beam, sigma_mm in EMODE_REF_BEAMS:
        for power_kw in POWERS_KW:
            for b_gs in EMODE_BSCAN_GS:
                row = collect(emode_dir, beam, sigma_mm, power_kw, b_gs)
                if row is not None:
                    rows.append(row)
    return rows


def collect_size_rows(emode_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for beam in ("injection", "extraction"):
        for power_kw in POWERS_KW:
            for b_gs in EMODE_SIZE_B_GS:
                for sigma_mm in SIZE_MM:
                    row = collect(emode_dir, beam, sigma_mm, power_kw, b_gs)
                    if row is not None:
                        rows.append(row)
    return rows


def threshold_1pct(series: list[dict]) -> int | None:
    """Smallest B after which |Δ| stays below 1% for the rest of the grid."""
    series = sorted(series, key=lambda r: r["b_gs"])
    thr = None
    for r in reversed(series):
        if abs(r["expansion_vs_no_sc_pct"]) < 1.0:
            thr = r["b_gs"]
        else:
            break
    return thr


def plot_bscan(rows: list[dict], plot_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.6), sharey=True)
    for ax, (beam, sigma_mm) in zip(axes, EMODE_REF_BEAMS):
        for power_kw in POWERS_KW:
            series = sorted(
                (
                    r
                    for r in rows
                    if r["beam"] == beam
                    and r["sigma_x_mm"] == sigma_mm
                    and r["power_kw"] == power_kw
                ),
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
        ax.axhspan(-1.0, 1.0, color="0.85", alpha=0.5, lw=0)
        ax.set_title(ref_title(beam, sigma_mm))
        ax.set_xlabel("B [G]")
        ax.set_xlim(EMODE_BSCAN_GS[0], EMODE_BSCAN_GS[-1])
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("profile expansion vs no SC [%]")
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_emode_bscan300.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_emode_bscan300.png'}")

    # Zoom on the ±3% band to show the tail 150–300 G.
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.6), sharey=True)
    for ax, (beam, sigma_mm) in zip(axes, EMODE_REF_BEAMS):
        for power_kw in POWERS_KW:
            series = sorted(
                (
                    r
                    for r in rows
                    if r["beam"] == beam
                    and r["sigma_x_mm"] == sigma_mm
                    and r["power_kw"] == power_kw
                    and r["b_gs"] >= 150
                ),
                key=lambda r: r["b_gs"],
            )
            if not series:
                continue
            ax.plot(
                [r["b_gs"] for r in series],
                [r["expansion_vs_no_sc_pct"] for r in series],
                "o-",
                ms=3,
                lw=1.2,
                label=f"{power_kw} kW",
            )
        ax.axhline(0.0, color="0.5", lw=0.8)
        ax.axhline(-1.0, color="0.6", ls="--", lw=0.8)
        ax.axhline(1.0, color="0.6", ls="--", lw=0.8)
        ax.set_ylim(-3.0, 3.0)
        ax.set_title(ref_title(beam, sigma_mm))
        ax.set_xlabel("B [G]")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("profile expansion vs no SC [%]")
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_emode_bscan300_tail.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_emode_bscan300_tail.png'}")


def plot_size_grid(
    rows: list[dict],
    plot_dir: Path,
    value_key: str,
    ylabel: str,
    filename: str,
    diagonal: bool = False,
) -> None:
    ncol = len(EMODE_SIZE_B_GS)
    fig, axes = plt.subplots(2, ncol, figsize=(3.4 * ncol + 1.0, 8.0), sharex=True, sharey=True)
    lims = np.array(SIZE_MM, dtype=float)
    for row_i, beam in enumerate(("injection", "extraction")):
        for col_i, b_gs in enumerate(EMODE_SIZE_B_GS):
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
            ax.set_title(f"{BEAM_TITLES[beam]}, {b_label(b_gs)}", fontsize=9)
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
    parser.add_argument("--plot-dir", default="plots", type=Path)
    parser.add_argument("--summary-b", default="output/csns_emode_bscan300_summary.csv")
    parser.add_argument("--summary-size", default="output/csns_emode_size_summary.csv")
    args = parser.parse_args()
    args.plot_dir.mkdir(parents=True, exist_ok=True)

    link_existing_emode_outputs(args.emode_dir, verbose=False)
    b_rows = collect_bscan_rows(args.emode_dir)
    size_rows = collect_size_rows(args.emode_dir)

    if b_rows:
        plot_bscan(b_rows, args.plot_dir)
    if size_rows:
        plot_size_grid(
            size_rows,
            args.plot_dir,
            "expansion_vs_no_sc_pct",
            "Expansion vs no SC [%]",
            "csns_emode_size_expansion.png",
        )
        plot_size_grid(
            size_rows,
            args.plot_dir,
            "sigma_sc_on_mm",
            "Obtained beam size [mm]",
            "csns_emode_size_obtained.png",
            diagonal=True,
        )
    write_csv(Path(args.summary_b), b_rows)
    write_csv(Path(args.summary_size), size_rows)

    print()
    print("B-scan: |Δ| < 1% thereafter (G), and Δ at 300 G:")
    for beam, sigma_mm in EMODE_REF_BEAMS:
        bits = []
        for power_kw in POWERS_KW:
            series = [
                r
                for r in b_rows
                if r["beam"] == beam and r["sigma_x_mm"] == sigma_mm and r["power_kw"] == power_kw
            ]
            if not series:
                continue
            thr = threshold_1pct(series)
            at300 = [r for r in series if r["b_gs"] == 300]
            tail = f"{at300[0]['expansion_vs_no_sc_pct']:+.2f}%@300G" if at300 else "n/a@300G"
            bits.append(f"{power_kw}kW thr={thr if thr is not None else '>300'}G {tail}")
        if bits:
            print(f"  {ref_title(beam, sigma_mm)}: " + "; ".join(bits))
    print("Size scan at σ_x = 3, 10, 20 mm (obtained σ, mm):")
    for beam in ("injection", "extraction"):
        for b_gs in EMODE_SIZE_B_GS:
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
                            f"{power_kw}kW {hit[0]['sigma_sc_on_mm']:.2f}"
                            f" ({hit[0]['expansion_vs_no_sc_pct']:+.1f}%)"
                        )
                if bits:
                    print(f"  {BEAM_TITLES[beam]}, {b_label(b_gs)}, {sigma_mm} mm: " + ", ".join(bits))

    if not b_rows and not size_rows:
        raise SystemExit("No e-mode replan outputs found")


if __name__ == "__main__":
    main()
