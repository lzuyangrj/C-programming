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
from evaluate_bscan import load_xy, stats, summarize_pair  # noqa: E402
from generate_csns_configs import (  # noqa: E402
    EMODE_BSCAN_GS,
    EMODE_CHECK_POWERS_KW,
    EMODE_OFFSET_B_GS,
    EMODE_OFFSET_BEAMS,
    EMODE_OFFSETS_MM,
    EMODE_REF_BEAMS,
    EMODE_SIZE_B_GS,
    EMODE_VOLT_B_GS,
    EMODE_VOLTAGES_KV,
    POWERS_KW,
    SIZE_MM,
    emode_csv_name,
    link_existing_emode_outputs,
    offset_csv_name,
    volt_csv_name,
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


def add_centroids(row: dict, on: Path, off: Path) -> dict:
    """Add centroid (mean x) columns; needed for the offset block."""
    xi_on, xf_on, _, _ = load_xy(on)
    _, xf_off, _, _ = load_xy(off)
    row["mean_initial_mm"] = stats(xi_on)["mean"]
    row["mean_sc_on_mm"] = stats(xf_on)["mean"]
    row["mean_sc_off_mm"] = stats(xf_off)["mean"]
    row["centroid_shift_vs_no_sc_mm"] = row["mean_sc_on_mm"] - row["mean_sc_off_mm"]
    return row


def collect_voltage_rows(emode_dir: Path) -> list[dict]:
    """Block C plus the 25 kV baseline from Block A (10 mm injection)."""
    rows: list[dict] = []
    for v_kv in (*EMODE_VOLTAGES_KV, 25):
        for power_kw in EMODE_CHECK_POWERS_KW:
            for b_gs in EMODE_VOLT_B_GS:
                if v_kv == 25:
                    on, off = emode_paths(emode_dir, "injection", 10, power_kw, b_gs)
                else:
                    on = emode_dir / volt_csv_name(v_kv, power_kw, b_gs, True)
                    off = emode_dir / volt_csv_name(v_kv, 100, b_gs, False)
                row = summarize_pair(on, off, "injection_electrons_sig10", b_gs)
                if row is None:
                    continue
                row["voltage_kv"] = v_kv
                row["power_kw"] = power_kw
                rows.append(row)
    return rows


def collect_offset_rows(emode_dir: Path) -> list[dict]:
    """Block D plus the centred baseline from Block A (10 mm inj. and ext.)."""
    rows: list[dict] = []
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        for dx, dy in ((0, 0), *EMODE_OFFSETS_MM):
            for power_kw in EMODE_CHECK_POWERS_KW:
                for b_gs in EMODE_OFFSET_B_GS:
                    if (dx, dy) == (0, 0):
                        on, off = emode_paths(emode_dir, beam, 10, power_kw, b_gs)
                    else:
                        on = emode_dir / offset_csv_name(beam, dx, dy, power_kw, b_gs, True)
                        off = emode_dir / offset_csv_name(beam, dx, dy, 100, b_gs, False)
                    row = summarize_pair(on, off, f"{beam}_electrons", b_gs)
                    if row is None:
                        continue
                    add_centroids(row, on, off)
                    row["beam"] = beam
                    row["dx_mm"] = dx
                    row["dy_mm"] = dy
                    row["power_kw"] = power_kw
                    rows.append(row)
    return rows


def plot_voltage(rows: list[dict], plot_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.6), sharey=True)
    for ax, power_kw in zip(axes, EMODE_CHECK_POWERS_KW):
        for v_kv in sorted({r["voltage_kv"] for r in rows}):
            series = sorted(
                (r for r in rows if r["voltage_kv"] == v_kv and r["power_kw"] == power_kw
                 and r["b_gs"] <= 300),
                key=lambda r: r["b_gs"],
            )
            if not series:
                continue
            ax.plot(
                [r["b_gs"] for r in series],
                [r["expansion_vs_no_sc_pct"] for r in series],
                "o-",
                ms=3.5,
                lw=1.2,
                label=f"{v_kv} kV ({v_kv * 1e3 / 0.231 / 1e3:.0f} kV/m)",
            )
        ax.axhline(0.0, color="0.5", lw=0.8)
        ax.axhspan(-1.0, 1.0, color="0.85", alpha=0.5, lw=0)
        ax.set_title(f"Injection 80 MeV, e− (10×8 mm), {power_kw} kW")
        ax.set_xlabel("B [G]")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, title="cage voltage")
    axes[0].set_ylabel("profile expansion vs no SC [%]")
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_emode_voltage.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_emode_voltage.png'}")


def plot_offset(rows: list[dict], plot_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.2), sharex=True)
    for col, (beam, _sigma) in enumerate(EMODE_OFFSET_BEAMS):
        for dx, dy in ((0, 0), *EMODE_OFFSETS_MM):
            for power_kw, ls in zip(EMODE_CHECK_POWERS_KW, ("-", "--")):
                series = sorted(
                    (
                        r
                        for r in rows
                        if r["beam"] == beam
                        and r["dx_mm"] == dx
                        and r["dy_mm"] == dy
                        and r["power_kw"] == power_kw
                    ),
                    key=lambda r: r["b_gs"],
                )
                if not series:
                    continue
                label = f"dx={dx:+d}, dy={dy:+d} mm, {power_kw} kW"
                xs = [r["b_gs"] for r in series]
                axes[0, col].plot(
                    xs, [r["expansion_vs_no_sc_pct"] for r in series], "o" + ls, ms=3.5, lw=1.1, label=label
                )
                axes[1, col].plot(
                    xs, [r["centroid_shift_vs_no_sc_mm"] for r in series], "o" + ls, ms=3.5, lw=1.1, label=label
                )
        axes[0, col].set_title(f"{BEAM_TITLES[beam]}, e− (10×8 mm)")
        axes[0, col].axhline(0.0, color="0.5", lw=0.8)
        axes[1, col].axhline(0.0, color="0.5", lw=0.8)
        axes[1, col].set_xlabel("B [G]")
        for ax in axes[:, col]:
            ax.set_xscale("symlog", linthresh=300)
            ax.set_xticks(EMODE_OFFSET_B_GS)
            ax.set_xticklabels([str(b) for b in EMODE_OFFSET_B_GS])
            ax.grid(True, alpha=0.3)
    axes[0, 0].set_ylabel("profile expansion vs no SC [%]")
    axes[1, 0].set_ylabel("centroid shift vs no SC [mm]")
    axes[0, 0].legend(fontsize=6.5, ncol=2)
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_emode_offset.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_emode_offset.png'}")


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
    parser.add_argument("--summary-voltage", default="output/csns_emode_voltage_summary.csv")
    parser.add_argument("--summary-offset", default="output/csns_emode_offset_summary.csv")
    args = parser.parse_args()
    args.plot_dir.mkdir(parents=True, exist_ok=True)

    link_existing_emode_outputs(args.emode_dir, verbose=False)
    b_rows = collect_bscan_rows(args.emode_dir)
    size_rows = collect_size_rows(args.emode_dir)
    v_rows = collect_voltage_rows(args.emode_dir)
    o_rows = collect_offset_rows(args.emode_dir)
    if v_rows:
        plot_voltage(v_rows, args.plot_dir)
    if o_rows:
        plot_offset(o_rows, args.plot_dir)
    write_csv(Path(args.summary_voltage), v_rows)
    write_csv(Path(args.summary_offset), o_rows)

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

    print("Cage voltage (inj. 10 mm): Δ at 0 G / 100 G / 200 G / 300 G:")
    for v_kv in sorted({r["voltage_kv"] for r in v_rows}):
        for power_kw in EMODE_CHECK_POWERS_KW:
            pick = {
                r["b_gs"]: r["expansion_vs_no_sc_pct"]
                for r in v_rows
                if r["voltage_kv"] == v_kv and r["power_kw"] == power_kw
            }
            if pick:
                vals = " / ".join(f"{pick[b]:+.1f}%" if b in pick else "n/a" for b in (0, 100, 200, 300))
                print(f"  {v_kv} kV, {power_kw} kW: {vals}")
    print("Beam offset: Δσ and centroid shift at 100 G / 300 G / 0.1 T:")
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        for dx, dy in ((0, 0), *EMODE_OFFSETS_MM):
            for power_kw in EMODE_CHECK_POWERS_KW:
                pick = {
                    r["b_gs"]: r
                    for r in o_rows
                    if r["beam"] == beam
                    and r["dx_mm"] == dx
                    and r["dy_mm"] == dy
                    and r["power_kw"] == power_kw
                }
                if pick:
                    vals = " / ".join(
                        f"{pick[b]['expansion_vs_no_sc_pct']:+.1f}% {pick[b]['centroid_shift_vs_no_sc_mm']:+.2f}mm"
                        if b in pick
                        else "n/a"
                        for b in (100, 300, 1000)
                    )
                    print(f"  {BEAM_TITLES[beam]} dx={dx:+d} dy={dy:+d}, {power_kw} kW: {vals}")

    if not b_rows and not size_rows and not v_rows and not o_rows:
        raise SystemExit("No e-mode replan outputs found")


if __name__ == "__main__":
    main()
