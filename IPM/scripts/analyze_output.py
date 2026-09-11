#!/usr/bin/env python3
"""Plot initial vs final transverse profiles from a BasicRecorder CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plot_conf import plot_conf


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str:
    for name in candidates:
        if name in df.columns:
            return name
    lowered = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lowered:
            return lowered[name.lower()]
    raise KeyError(f"None of {candidates} found in columns: {list(df.columns)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv",
        nargs="?",
        default="output/lhc_6p5tev_electrons_smoke.csv",
        help="BasicRecorder CSV path",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="plots/profile_comparison.png",
        help="Output plot path",
    )
    parser.add_argument("--bins", type=int, default=40, help="Histogram bins")
    args = parser.parse_args()
    plot_conf()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise SystemExit(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    # BasicRecorder columns vary slightly by version; tolerate common names.
    x_i = _pick_column(df, ["initial x", "initial_x", "x initial", "x_i"])
    x_f = _pick_column(df, ["final x", "final_x", "x final", "x_f"])

    x_initial = df[x_i].to_numpy(dtype=float) * 1e3  # m -> mm
    x_final = df[x_f].to_numpy(dtype=float) * 1e3

    lim = float(np.nanmax(np.abs(np.concatenate([x_initial, x_final]))))
    lim = max(lim * 1.05, 1.0)
    edges = np.linspace(-lim, lim, args.bins + 1)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(x_initial, bins=edges, histtype="step", linewidth=1.8, label="initial x")
    ax.hist(x_final, bins=edges, histtype="step", linewidth=1.8, label="final x")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("counts")
    ax.set_title(f"IPM profile comparison ({csv_path.name})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}")
    print(f"Particles: {len(df)}")
    print(f"initial x std: {np.nanstd(x_initial):.3f} mm")
    print(f"final   x std: {np.nanstd(x_final):.3f} mm")


if __name__ == "__main__":
    main()
