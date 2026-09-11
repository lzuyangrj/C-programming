#!/usr/bin/env python3
"""Evaluate CSNS IPM guiding-B scan: 0, 50, 100, 200 G; e-mode and ion-mode."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plot_conf import load_summary, plot_conf

B_SCAN_GS = (0, 50, 100, 200, 250)
FAMILIES = [
    ("injection_electrons", "Injection 80 MeV, e−"),
    ("extraction_electrons", "Extraction 1.6 GeV, e−"),
    ("injection_ions", "Injection 80 MeV, H₂⁺"),
    ("extraction_ions", "Extraction 1.6 GeV, H₂⁺"),
]


def _col(df: pd.DataFrame, names: list[str]) -> str:
    for name in names:
        if name in df.columns:
            return name
    lowered = {c.lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    raise KeyError(f"None of {names} in {list(df.columns)}")


def load_xy(path: Path) -> tuple[np.ndarray, np.ndarray, int, int]:
    df = pd.read_csv(path)
    n_all = len(df)
    if "status" in df.columns:
        detected = df["status"].astype(str).str.upper() == "DETECTED"
        df = df.loc[detected]
    x_i = df[_col(df, ["initial x"])].to_numpy(float) * 1e3
    x_f = df[_col(df, ["final x"])].to_numpy(float) * 1e3
    return x_i, x_f, n_all, len(df)


def stats(x: np.ndarray) -> dict[str, float]:
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {"rms": float("nan"), "mean": float("nan")}
    return {"rms": float(np.std(x, ddof=0)), "mean": float(np.mean(x))}


def summarize_pair(on_path: Path, off_path: Path, family: str, b_gs: int) -> dict | None:
    if not on_path.is_file() or not off_path.is_file():
        return None
    xi_on, xf_on, n_on, nd_on = load_xy(on_path)
    xi_off, xf_off, n_off, nd_off = load_xy(off_path)
    s_i = stats(xi_on)
    s_on = stats(xf_on)
    s_off = stats(xf_off)
    expansion = 100.0 * (s_on["rms"] / s_off["rms"] - 1.0) if s_off["rms"] else float("nan")
    vs_true = 100.0 * (s_on["rms"] / s_i["rms"] - 1.0) if s_i["rms"] else float("nan")
    n_common = min(len(xf_on), len(xf_off))
    dx_rms = float("nan")
    dx_max = float("nan")
    if n_common:
        dx = xf_on[:n_common] - xf_off[:n_common]
        dx_rms = float(np.sqrt(np.mean(dx**2)))
        dx_max = float(np.max(np.abs(dx)))
    return {
        "family": family,
        "b_gs": b_gs,
        "b_t": b_gs * 1e-4,
        "n_sc_on": nd_on,
        "n_sc_off": nd_off,
        "n_all_on": n_on,
        "n_all_off": n_off,
        "detected_frac_on": nd_on / n_on if n_on else float("nan"),
        "detected_frac_off": nd_off / n_off if n_off else float("nan"),
        "sigma_initial_mm": s_i["rms"],
        "sigma_sc_off_mm": s_off["rms"],
        "sigma_sc_on_mm": s_on["rms"],
        "expansion_vs_no_sc_pct": expansion,
        "expansion_vs_initial_pct": vs_true,
        "rms_particle_dx_mm": dx_rms,
        "max_abs_particle_dx_mm": dx_max,
    }


def plot_scan(rows: list[dict], plot_dir: Path) -> None:
    plot_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.5), sharex=True)
    by_family = {key: [] for key, _ in FAMILIES}
    for row in rows:
        by_family[row["family"]].append(row)

    for ax, (key, title) in zip(axes.ravel(), FAMILIES):
        series = sorted(by_family[key], key=lambda r: r["b_gs"])
        if not series:
            ax.set_title(f"{title}\n(missing)")
            continue
        b = [r["b_gs"] for r in series]
        ax.plot(b, [r["sigma_sc_off_mm"] for r in series], "o-", label="σ no SC")
        ax.plot(b, [r["sigma_sc_on_mm"] for r in series], "s-", label="σ with SC")
        ax.plot(b, [r["sigma_initial_mm"] for r in series], "x--", color="0.45", label="σ initial")
        ax.set_title(title)
        ax.set_ylabel("σ_x [mm]")
        ax.grid(True, alpha=0.3)
        ax2 = ax.twinx()
        ax2.plot(
            b,
            [r["expansion_vs_no_sc_pct"] for r in series],
            "^:",
            color="C3",
            label="expansion",
        )
        ax2.set_ylabel("expansion [%]", color="C3")
        ax2.tick_params(axis="y", labelcolor="C3")
        if key == FAMILIES[0][0]:
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="best")
    for ax in axes[1]:
        ax.set_xlabel("B [G]")
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_bscan_sigma.png", dpi=150)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharey=False)
    for ax, kind, ylabel in (
        (axes[0], "expansion_vs_no_sc_pct", "profile expansion vs no SC [%]"),
        (axes[1], "detected_frac_on", "detected fraction (SC on)"),
    ):
        for key, title in FAMILIES:
            series = sorted(by_family[key], key=lambda r: r["b_gs"])
            if not series:
                continue
            ax.plot(
                [r["b_gs"] for r in series],
                [r[kind] for r in series],
                "o-",
                label=title,
            )
        ax.set_xlabel("B [G]")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        if kind == "detected_frac_on":
            ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(plot_dir / "csns_bscan_expansion.png", dpi=150)
    print(f"Wrote {plot_dir / 'csns_bscan_sigma.png'}")
    print(f"Wrote {plot_dir / 'csns_bscan_expansion.png'}")


def plot_profiles(output_dir: Path, plot_dir: Path, mode: str) -> None:
    if mode == "electron":
        keys = ["injection_electrons", "extraction_electrons"]
        titles = ["Injection e−", "Extraction e−"]
        fname = "csns_bscan_electron_profiles.png"
    else:
        keys = ["injection_ions", "extraction_ions"]
        titles = ["Injection H₂⁺", "Extraction H₂⁺"]
        fname = "csns_bscan_ion_profiles.png"

    fig, axes = plt.subplots(2, len(B_SCAN_GS), figsize=(18.0, 7.6), sharey=False)
    drawn_legend = False
    for row, (key, title) in enumerate(zip(keys, titles)):
        for col, b_gs in enumerate(B_SCAN_GS):
            ax = axes[row, col]
            stem = f"csns_{key}_b{b_gs}G"
            on_path = output_dir / f"{stem}_sc_on.csv"
            off_path = output_dir / f"{stem}_sc_off.csv"
            if not on_path.is_file() or not off_path.is_file():
                ax.set_title(f"{title}, {b_gs} G\n(missing)")
                continue
            xi_on, xf_on, _, nd_on = load_xy(on_path)
            _, xf_off, _, nd_off = load_xy(off_path)
            if nd_on == 0 and nd_off == 0:
                ax.set_title(f"{title}, {b_gs} G\n(no DETECTED)")
                continue
            stacked = np.concatenate(
                [a for a in (xf_on, xf_off, xi_on) if a.size]
            )
            lim = float(np.nanmax(np.abs(stacked))) if stacked.size else 1.0
            edges = np.linspace(-lim * 1.05, lim * 1.05, 81)
            ax.hist(xi_on, bins=edges, histtype="step", linewidth=1.2, label="initial", color="0.45")
            ax.hist(xf_off, bins=edges, histtype="step", linewidth=1.6, label="no space charge")
            ax.hist(xf_on, bins=edges, histtype="step", linewidth=1.6, label="with space charge")
            s_off = stats(xf_off)["rms"]
            s_on = stats(xf_on)["rms"]
            expansion = 100.0 * (s_on / s_off - 1.0) if s_off else float("nan")
            ax.set_title(
                f"{title}, {b_gs} G\n"
                f"σ_off={s_off:.2f} mm, σ_on={s_on:.2f} mm ({expansion:+.1f}%)"
            )
            ax.set_xlabel("x [mm]")
            ax.grid(True, alpha=0.3)
            if not drawn_legend:
                ax.legend(fontsize=7)
                ax.set_ylabel("counts")
                drawn_legend = True
    fig.tight_layout()
    fig.savefig(plot_dir / fname, dpi=150)
    print(f"Wrote {plot_dir / fname}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output/bscan", type=Path)
    parser.add_argument("--plot-dir", default="plots", type=Path)
    parser.add_argument("--summary", default="output/csns_bscan_summary.csv")
    parser.add_argument(
        "--from-summary",
        action="store_true",
        help="Replot sigma/expansion from the summary CSV; still draw profiles if CSVs exist.",
    )
    args = parser.parse_args()
    plot_conf()

    if args.from_summary:
        rows = load_summary(args.summary)
        missing = 0
    else:
        rows = []
        missing = 0
        for key, _title in FAMILIES:
            for b_gs in B_SCAN_GS:
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
        raise SystemExit(f"No completed B-scan pairs in {args.output_dir}")

    plot_scan(rows, args.plot_dir)
    plot_profiles(args.output_dir, args.plot_dir, "electron")
    plot_profiles(args.output_dir, args.plot_dir, "ion")

    if not args.from_summary:
        summary_path = Path(args.summary)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with summary_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {summary_path}")
    print()
    print(
        f"{'family':<22} {'B[G]':>6} {'σ_off':>8} {'σ_on':>8} "
        f"{'Δ%':>8} {'det_on':>8} {'N_on':>8}"
    )
    for row in rows:
        print(
            f"{row['family']:<22} {row['b_gs']:6d} "
            f"{row['sigma_sc_off_mm']:8.3f} "
            f"{row['sigma_sc_on_mm']:8.3f} "
            f"{row['expansion_vs_no_sc_pct']:7.2f}% "
            f"{row['detected_frac_on']:8.3f} "
            f"{row['n_sc_on']:8d}"
        )
    if missing:
        print(f"\n({missing} pair(s) missing)")


if __name__ == "__main__":
    main()
