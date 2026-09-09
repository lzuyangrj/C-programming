#!/usr/bin/env python3
"""Compare IPM profiles with beam space charge on vs off."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CASES = [
    ("injection_electrons", "Injection 80 MeV, electrons"),
    ("extraction_electrons", "Extraction 1.6 GeV, electrons"),
    ("injection_ions", "Injection 80 MeV, H2+ ions"),
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output", type=Path)
    parser.add_argument("--plot", default="plots/csns_space_charge_impact.png")
    parser.add_argument("--summary", default="output/csns_space_charge_summary.csv")
    args = parser.parse_args()

    rows = []
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=False)
    drawn = 0

    for ax, (key, title) in zip(axes, CASES):
        on_path = args.output_dir / f"csns_{key}_sc_on.csv"
        off_path = args.output_dir / f"csns_{key}_sc_off.csv"
        if not on_path.is_file() or not off_path.is_file():
            ax.set_title(f"{title}\n(missing output)")
            ax.set_xlabel("x [mm]")
            continue

        xi_on, xf_on, n_on, nd_on = load_xy(on_path)
        xi_off, xf_off, n_off, nd_off = load_xy(off_path)
        if nd_on == 0 or nd_off == 0:
            ax.set_title(f"{title}\n(no DETECTED particles)")
            ax.set_xlabel("x [mm]")
            continue
        s_i = stats(xi_on)
        s_on = stats(xf_on)
        s_off = stats(xf_off)
        expansion = 100.0 * (s_on["rms"] / s_off["rms"] - 1.0) if s_off["rms"] else float("nan")
        vs_true = 100.0 * (s_on["rms"] / s_i["rms"] - 1.0) if s_i["rms"] else float("nan")
        n_common = min(len(xf_on), len(xf_off))
        dx = xf_on[:n_common] - xf_off[:n_common]
        rows.append(
            {
                "case": key,
                "n_sc_on": nd_on,
                "n_sc_off": nd_off,
                "sigma_initial_mm": s_i["rms"],
                "sigma_sc_off_mm": s_off["rms"],
                "sigma_sc_on_mm": s_on["rms"],
                "expansion_vs_no_sc_pct": expansion,
                "expansion_vs_initial_pct": vs_true,
                "rms_particle_dx_mm": float(np.sqrt(np.mean(dx**2))),
                "max_abs_particle_dx_mm": float(np.max(np.abs(dx))),
            }
        )

        stacked = np.concatenate([xf_on, xf_off, xi_on])
        lim = float(np.nanmax(np.abs(stacked))) if stacked.size else 1.0
        edges = np.linspace(-lim * 1.05, lim * 1.05, 45)
        ax.hist(xi_on, bins=edges, histtype="step", linewidth=1.4, label="initial", color="0.45")
        ax.hist(xf_off, bins=edges, histtype="step", linewidth=1.8, label="no space charge")
        ax.hist(xf_on, bins=edges, histtype="step", linewidth=1.8, label="with space charge")
        ax.set_title(
            f"{title}\n"
            f"σ_off={s_off['rms']:.2f} mm, σ_on={s_on['rms']:.2f} mm "
            f"({expansion:+.1f}%)"
        )
        ax.set_xlabel("x [mm]")
        ax.grid(True, alpha=0.3)
        if drawn == 0:
            ax.set_ylabel("counts")
            ax.legend(fontsize=8)
        drawn += 1

    fig.tight_layout()
    plot_path = Path(args.plot)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path, dpi=150)
    print(f"Wrote {plot_path}")

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with summary_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {summary_path}")
        print()
        print(
            f"{'case':<24} {'σ_init':>8} {'σ_off':>8} {'σ_on':>8} "
            f"{'Δ vs off':>10} {'Δ vs init':>10} {'rms Δx':>8}"
        )
        for row in rows:
            print(
                f"{row['case']:<24} "
                f"{row['sigma_initial_mm']:8.3f} "
                f"{row['sigma_sc_off_mm']:8.3f} "
                f"{row['sigma_sc_on_mm']:8.3f} "
                f"{row['expansion_vs_no_sc_pct']:9.2f}% "
                f"{row['expansion_vs_initial_pct']:9.2f}% "
                f"{row['rms_particle_dx_mm']:8.3f}"
            )
    else:
        raise SystemExit("No completed case pairs found in output/")


if __name__ == "__main__":
    main()
