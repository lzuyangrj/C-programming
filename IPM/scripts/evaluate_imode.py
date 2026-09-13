#!/usr/bin/env python3
"""Evaluate the ion-mode A–D matrix (round beams; H₂⁺ / H₂O⁺ / N₂⁺)."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import load_xy, stats, summarize_pair  # noqa: E402
from plot_conf import load_summary, plot_conf  # noqa: E402
from generate_csns_configs import (  # noqa: E402
    IMODE_B_GS,
    IMODE_CHECK_POWERS_KW,
    IMODE_OFFSET_BEAMS,
    IMODE_OFFSETS_MM,
    IMODE_REF_BEAMS,
    IMODE_FINE_DX_MM,
    IMODE_FINE_DY_MM,
    IMODE_FINE_VOLTAGES_KV,
    IMODE_VOLTAGES_KV,
    ION_SPECIES,
    POWERS_KW,
    SIZE_MM,
    imode_csv_name,
    imode_offset_csv_name,
    imode_volt_csv_name,
)

BEAM_TITLES = {"injection": "Injection 80 MeV", "extraction": "Extraction 1.6 GeV"}
SPECIES_SLUGS = [slug for slug, _rest, _label in ION_SPECIES]
SPECIES_LABELS = {slug: label for slug, _rest, label in ION_SPECIES}


def b_label(b_gs: int) -> str:
    return "B = 0.1 T (1000 G)" if b_gs == 1000 else f"B = {b_gs} G"


def off_path(imode_dir: Path, species: str, beam: str, sigma_mm: int, b_gs: int) -> Path:
    """SC-off is H₂⁺ @ 100 kW, shared across species."""
    return imode_dir / imode_csv_name("ions", beam, sigma_mm, 100, b_gs, False)


def collect_ref(
    imode_dir: Path, species: str, beam: str, sigma_mm: int, power_kw: int, b_gs: int
) -> dict | None:
    on = imode_dir / imode_csv_name(species, beam, sigma_mm, power_kw, b_gs, True)
    off = off_path(imode_dir, species, beam, sigma_mm, b_gs)
    row = summarize_pair(on, off, f"{beam}_{species}", b_gs)
    if row is None:
        return None
    row["species"] = species
    row["species_label"] = SPECIES_LABELS[species]
    row["beam"] = beam
    row["power_kw"] = power_kw
    row["sigma_x_mm"] = sigma_mm
    return row


def add_centroids(row: dict, on: Path, off: Path) -> dict:
    xi_on, xf_on, _, _ = load_xy(on)
    _, xf_off, _, _ = load_xy(off)
    row["mean_initial_mm"] = stats(xi_on)["mean"]
    row["mean_sc_on_mm"] = stats(xf_on)["mean"]
    row["mean_sc_off_mm"] = stats(xf_off)["mean"]
    row["centroid_shift_vs_no_sc_mm"] = row["mean_sc_on_mm"] - row["mean_sc_off_mm"]
    return row


def collect_voltage_rows(imode_dir: Path) -> list[dict]:
    rows: list[dict] = []
    voltages = tuple(dict.fromkeys((*IMODE_FINE_VOLTAGES_KV, *IMODE_VOLTAGES_KV)))
    for species in SPECIES_SLUGS:
        for v_kv in voltages:
            for power_kw in IMODE_CHECK_POWERS_KW:
                for b_gs in IMODE_B_GS:
                    on = imode_dir / imode_volt_csv_name(species, v_kv, power_kw, b_gs, True)
                    off = imode_dir / imode_volt_csv_name("ions", v_kv, 100, b_gs, False)
                    row = summarize_pair(on, off, f"injection_{species}_s10x10", b_gs)
                    if row is None:
                        continue
                    row["species"] = species
                    row["species_label"] = SPECIES_LABELS[species]
                    row["voltage_kv"] = v_kv
                    row["power_kw"] = power_kw
                    rows.append(row)
    return rows


def collect_offset_rows(imode_dir: Path) -> list[dict]:
    rows: list[dict] = []
    offsets = {(0, 0), *IMODE_OFFSETS_MM}
    offsets |= {(0, dy) for dy in IMODE_FINE_DY_MM}
    offsets |= {(dx, 0) for dx in IMODE_FINE_DX_MM}
    for species in SPECIES_SLUGS:
        for beam, _sigma in IMODE_OFFSET_BEAMS:
            for dx, dy in sorted(offsets):
                for power_kw in IMODE_CHECK_POWERS_KW:
                    for b_gs in IMODE_B_GS:
                        if (dx, dy) == (0, 0):
                            on = imode_dir / imode_csv_name(
                                species, beam, 10, power_kw, b_gs, True
                            )
                            off = off_path(imode_dir, species, beam, 10, b_gs)
                        else:
                            on = imode_dir / imode_offset_csv_name(
                                species, beam, dx, dy, power_kw, b_gs, True
                            )
                            off = imode_dir / imode_offset_csv_name(
                                "ions", beam, dx, dy, 100, b_gs, False
                            )
                        row = summarize_pair(on, off, f"{beam}_{species}", b_gs)
                        if row is None:
                            continue
                        add_centroids(row, on, off)
                        row["species"] = species
                        row["species_label"] = SPECIES_LABELS[species]
                        row["beam"] = beam
                        row["dx_mm"] = dx
                        row["dy_mm"] = dy
                        row["power_kw"] = power_kw
                        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {path}")


def plot_ref_b(rows: list[dict], plot_dir: Path) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(14.0, 11.0), sharey=True)
    for row_i, species in enumerate(SPECIES_SLUGS):
        for col_i, (beam, sigma_mm) in enumerate(IMODE_REF_BEAMS):
            ax = axes[row_i, col_i]
            for power_kw in POWERS_KW:
                series = sorted(
                    (
                        r
                        for r in rows
                        if r["species"] == species
                        and r["beam"] == beam
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
                    "o-",
                    ms=5,
                    lw=1.2,
                    label=f"{power_kw} kW",
                )
            ax.axhline(0.0, color="0.5", lw=0.8)
            ax.set_title(
                f"{SPECIES_LABELS[species]}, {BEAM_TITLES[beam]}\n({sigma_mm}×{sigma_mm} mm)",
                fontsize=9,
            )
            ax.set_xticks(IMODE_B_GS)
            ax.set_xticklabels([str(b) for b in IMODE_B_GS])
            ax.grid(True, alpha=0.3)
            if row_i == 0 and col_i == 0:
                ax.legend(fontsize=7)
            if row_i == 2:
                ax.set_xlabel("B [G]")
            if col_i == 0:
                ax.set_ylabel("Expansion vs no SC [%]")
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_imode_bscan.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_imode_bscan.png'}")


def plot_size_obtained(rows: list[dict], plot_dir: Path) -> None:
    fields = (0, 1000)
    fig, axes = plt.subplots(3, 2, figsize=(9.0, 10.0), sharex=True, sharey=True)
    lims = np.array(SIZE_MM, dtype=float)
    for row_i, species in enumerate(SPECIES_SLUGS):
        for col_i, b_gs in enumerate(fields):
            ax = axes[row_i, col_i]
            for beam, ls in zip(("injection", "extraction"), ("-", "--")):
                series = sorted(
                    (
                        r
                        for r in rows
                        if r["species"] == species
                        and r["beam"] == beam
                        and r["b_gs"] == b_gs
                        and r["power_kw"] == 100
                    ),
                    key=lambda r: r["sigma_x_mm"],
                )
                if not series:
                    continue
                ax.plot(
                    [r["sigma_x_mm"] for r in series],
                    [r["sigma_sc_on_mm"] for r in series],
                    ls + "o",
                    ms=3,
                    lw=1.1,
                    label=BEAM_TITLES[beam],
                )
            ax.plot(lims, lims, "k:", lw=0.9)
            ax.set_title(f"{SPECIES_LABELS[species]}, {b_label(b_gs)}", fontsize=9)
            ax.grid(True, alpha=0.3)
            if row_i == 2:
                ax.set_xlabel("True σ [mm]")
            if col_i == 0:
                ax.set_ylabel("Obtained σ [mm]")
            if row_i == 0 and col_i == 0:
                ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_imode_size_obtained.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_imode_size_obtained.png'}")


def aligned_extraction_size_rows(
    v2_path: Path | str = "output/csns_v2_summary.csv",
    b_gs: int = 1000,
) -> list[dict]:
    """Aligned I1/I2 extraction sizes (ion born with the bunch), not v1 as-run."""
    picked: dict[tuple, dict] = {}
    for r in load_summary(v2_path):
        if r.get("block") not in ("I1", "I2"):
            continue
        if r.get("beam") != "extraction":
            continue
        if "aligned" not in str(r.get("train", "")).lower():
            continue
        if int(r.get("voltage_kv") or 0) != 25:
            continue
        if int(r.get("dx_mm") or 0) != 0 or int(r.get("dy_mm") or 0) != 0:
            continue
        if int(r.get("b_gs") or -1) != b_gs:
            continue
        species = r.get("species")
        if species not in SPECIES_LABELS:
            continue
        sigma_mm = int(float(r.get("sigma_mm") or r.get("sigma_x_mm") or 0))
        power_kw = int(r["power_kw"])
        key = (species, power_kw, sigma_mm)
        if key in picked and picked[key].get("block") == "I1" and r.get("block") != "I1":
            continue
        picked[key] = {
            "species": species,
            "species_label": SPECIES_LABELS[species],
            "beam": "extraction",
            "b_gs": b_gs,
            "power_kw": power_kw,
            "sigma_x_mm": sigma_mm,
            "sigma_sc_on_mm": r["sigma_sc_on_mm"],
            "expansion_vs_no_sc_pct": r["expansion_vs_no_sc_pct"],
            "block": r.get("block"),
        }
    return list(picked.values())


def _size_series(
    rows: list[dict], species: str, beam: str, power_kw: int, b_gs: int = 1000
) -> list[dict]:
    return sorted(
        (
            r
            for r in rows
            if r["species"] == species
            and r["beam"] == beam
            and int(r["b_gs"]) == b_gs
            and int(r["power_kw"]) == power_kw
        ),
        key=lambda r: r["sigma_x_mm"],
    )


def plot_size_expansion(rows: list[dict], plot_dir: Path) -> None:
    """One figure per ring: rows are the three species, left column the
    expansion Δ(σ₀), right column the observed width σ_m(σ₀), at 0.1 T.
    Extraction ions are generated in time with the bunch."""
    aligned = aligned_extraction_size_rows()
    lims = np.array([0.0, 22.0])
    for beam, suffix in (("injection", ""), ("extraction", "_ext")):
        src = aligned if beam == "extraction" and aligned else rows
        fig, axes = plt.subplots(3, 2, figsize=(9.0, 10.5), sharex=True)
        for ax in axes[1:, 0]:
            ax.sharey(axes[0, 0])
        for ax in axes[1:, 1]:
            ax.sharey(axes[0, 1])
        for row_i, species in enumerate(SPECIES_SLUGS):
            ax_exp, ax_obs = axes[row_i]
            for power_kw in POWERS_KW:
                series = _size_series(src, species, beam, power_kw)
                if not series:
                    continue
                xs = [r["sigma_x_mm"] for r in series]
                ax_exp.plot(xs, [r["expansion_vs_no_sc_pct"] for r in series],
                            "o-", ms=3, lw=1.1, label=f"{power_kw} kW")
                ax_obs.plot(xs, [r["sigma_sc_on_mm"] for r in series],
                            "o-", ms=3, lw=1.1, label=f"{power_kw} kW")
            ax_exp.axhline(0.0, color="0.5", lw=0.8)
            ax_obs.plot(lims, lims, "k--", lw=0.9, label="obtained = true")
            title = f"{SPECIES_LABELS[species]}, {BEAM_TITLES[beam]}"
            ax_exp.set_title(title, fontsize=10)
            ax_obs.set_title(title, fontsize=10)
            ax_exp.grid(True, alpha=0.3)
            ax_obs.grid(True, alpha=0.3)
            ax_exp.set_ylabel(r"$\Delta$ [\%]")
            ax_obs.set_ylabel("Observed beam size [mm]")
            ax_exp.text(0.97, 0.95, f"({'ace'[row_i]})", transform=ax_exp.transAxes, ha="right", va="top")
            ax_obs.text(0.03, 0.95, f"({'bdf'[row_i]})", transform=ax_obs.transAxes, va="top")
            if row_i == 0:
                ax_exp.legend(fontsize=7, loc="upper right", bbox_to_anchor=(0.86, 1.0))
        for ax in axes[2]:
            ax.set_xlabel("True beam size [mm]")
        fig.tight_layout()
        path = plot_dir / f"csns_imode_size_expansion{suffix}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"Wrote {path}")


def plot_voltage(rows: list[dict], plot_dir: Path) -> None:
    """Expansion versus cage voltage at B = 0 (ion mode does not use B)."""
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), sharex=True)
    for ax, power_kw in zip(axes, IMODE_CHECK_POWERS_KW):
        for species in SPECIES_SLUGS:
            series = sorted(
                (
                    r
                    for r in rows
                    if r["species"] == species
                    and r["power_kw"] == power_kw
                    and r["b_gs"] == 0
                ),
                key=lambda r: r["voltage_kv"],
            )
            if not series:
                continue
            ax.plot(
                [r["voltage_kv"] for r in series],
                [r["expansion_vs_no_sc_pct"] for r in series],
                "o-",
                ms=5,
                lw=1.3,
                label=SPECIES_LABELS[species],
            )
        ax.axhline(0.0, color="0.5", lw=0.8)
        ax.set_title(f"{power_kw} kW", fontsize=11)
        ax.set_xlabel("cage voltage [kV]")
        ax.set_xticks(IMODE_VOLTAGES_KV)
        ax.grid(True, alpha=0.3)
        if power_kw == IMODE_CHECK_POWERS_KW[0]:
            ax.set_ylabel(r"$\Delta$ [\%]")
            ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_imode_voltage.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_imode_voltage.png'}")


def plot_offset(rows: list[dict], plot_dir: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(11.0, 10.0), sharex=True)
    for row_i, species in enumerate(SPECIES_SLUGS):
        for col_i, (beam, _sigma) in enumerate(IMODE_OFFSET_BEAMS):
            ax = axes[row_i, col_i]
            for dx, dy in ((0, 0), *IMODE_OFFSETS_MM):
                series = sorted(
                    (
                        r
                        for r in rows
                        if r["species"] == species
                        and r["beam"] == beam
                        and r["dx_mm"] == dx
                        and r["dy_mm"] == dy
                        and r["power_kw"] == 100
                    ),
                    key=lambda r: r["b_gs"],
                )
                if not series:
                    continue
                ax.plot(
                    [r["b_gs"] for r in series],
                    [r["expansion_vs_no_sc_pct"] for r in series],
                    "o-",
                    ms=4,
                    lw=1.1,
                    label=f"({dx:+d},{dy:+d}) mm",
                )
            ax.axhline(0.0, color="0.5", lw=0.8)
            ax.set_title(f"{SPECIES_LABELS[species]}, {BEAM_TITLES[beam]}", fontsize=9)
            ax.set_xticks(IMODE_B_GS)
            ax.set_xticklabels([str(b) for b in IMODE_B_GS])
            ax.grid(True, alpha=0.3)
            if row_i == 0 and col_i == 1:
                ax.legend(fontsize=7)
            if row_i == 2:
                ax.set_xlabel("B [G]")
            if col_i == 0:
                ax.set_ylabel("Expansion vs no SC [%]")
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_imode_offset.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_imode_offset.png'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imode-dir", default="output/imode", type=Path)
    parser.add_argument("--plot-dir", default="plots", type=Path)
    parser.add_argument("--summary-b", default="output/csns_imode_bscan_summary.csv")
    parser.add_argument("--summary-size", default="output/csns_imode_size_summary.csv")
    parser.add_argument("--summary-voltage", default="output/csns_imode_voltage_summary.csv")
    parser.add_argument("--summary-offset", default="output/csns_imode_offset_summary.csv")
    parser.add_argument(
        "--from-summary",
        action="store_true",
        help="Replot from existing summary CSVs; do not read particle CSVs.",
    )
    args = parser.parse_args()
    plot_conf()
    args.plot_dir.mkdir(parents=True, exist_ok=True)

    if args.from_summary:
        ref_rows = load_summary(args.summary_b)
        size_rows = load_summary(args.summary_size)
        v_rows = load_summary(args.summary_voltage)
        o_rows = load_summary(args.summary_offset)
    else:
        ref_rows = []
        size_rows = []
        for species in SPECIES_SLUGS:
            for beam, sigma_mm in IMODE_REF_BEAMS:
                for power_kw in POWERS_KW:
                    for b_gs in IMODE_B_GS:
                        row = collect_ref(args.imode_dir, species, beam, sigma_mm, power_kw, b_gs)
                        if row is not None:
                            ref_rows.append(row)
            for beam in ("injection", "extraction"):
                for power_kw in POWERS_KW:
                    for b_gs in IMODE_B_GS:
                        for sigma_mm in SIZE_MM:
                            row = collect_ref(
                                args.imode_dir, species, beam, sigma_mm, power_kw, b_gs
                            )
                            if row is not None:
                                size_rows.append(row)

        v_rows = collect_voltage_rows(args.imode_dir)
        o_rows = collect_offset_rows(args.imode_dir)
        # Particle CSVs of the closed A–D campaign were removed after
        # summarising. Merge so a partial re-collect cannot drop those rows.
        if Path(args.summary_voltage).is_file():
            have = {
                (r["species"], int(r["voltage_kv"]), int(r["power_kw"]), int(r["b_gs"])): r
                for r in load_summary(args.summary_voltage)
            }
            have.update(
                {
                    (r["species"], int(r["voltage_kv"]), int(r["power_kw"]), int(r["b_gs"])): r
                    for r in v_rows
                }
            )
            v_rows = list(have.values())
        if Path(args.summary_offset).is_file():
            have = {
                (
                    r["species"],
                    r["beam"],
                    int(r["dx_mm"]),
                    int(r["dy_mm"]),
                    int(r["power_kw"]),
                    int(r["b_gs"]),
                ): r
                for r in load_summary(args.summary_offset)
            }
            have.update(
                {
                    (
                        r["species"],
                        r["beam"],
                        int(r["dx_mm"]),
                        int(r["dy_mm"]),
                        int(r["power_kw"]),
                        int(r["b_gs"]),
                    ): r
                    for r in o_rows
                }
            )
            o_rows = list(have.values())

        if ref_rows:
            write_csv(Path(args.summary_b), ref_rows)
        if size_rows:
            write_csv(Path(args.summary_size), size_rows)
        write_csv(Path(args.summary_voltage), v_rows)
        write_csv(Path(args.summary_offset), o_rows)

    if ref_rows:
        plot_ref_b(ref_rows, args.plot_dir)
    if size_rows:
        plot_size_obtained(size_rows, args.plot_dir)
        plot_size_expansion(size_rows, args.plot_dir)
    if v_rows:
        plot_voltage(v_rows, args.plot_dir)
    if o_rows:
        plot_offset(o_rows, args.plot_dir)

    print(f"Reference B points: {len(ref_rows)} rows")
    print(f"Size scan: {len(size_rows)} rows")
    print(f"Voltage: {len(v_rows)} rows")
    print(f"Offset: {len(o_rows)} rows")


if __name__ == "__main__":
    main()
