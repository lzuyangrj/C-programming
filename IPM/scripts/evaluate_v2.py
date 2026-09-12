#!/usr/bin/env python3
"""Summarise completed v2 CSVs (output/v2) against their SC-off partners."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import summarize_pair  # noqa: E402
from write_v2_configs import csv_rel, load_points, new_points, xml_path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "csns_v2_summary.csv"


def off_row(on: dict, rows: list[dict]) -> dict | None:
    """Matching SC-off: same geometry, 100 kW, H₂⁺ for ions."""
    want_sp = "ions" if on["mode"] == "i" else on["species"]
    for r in rows:
        if (
            r["mode"] == on["mode"]
            and r["block"] == on["block"]
            and r["beam"] == on["beam"]
            and r["energy_mev"] == on["energy_mev"]
            and r["sigma_t_ns"] == on["sigma_t_ns"]
            and r["sigma_mm"] == on["sigma_mm"]
            and r["dx_mm"] == on["dx_mm"]
            and r["dy_mm"] == on["dy_mm"]
            and r["voltage_kv"] == on["voltage_kv"]
            and r["b_gs"] == on["b_gs"]
            and r["train"] == on["train"]
            and not r["sc_on"]
            and (r["species"] == want_sp or (on["mode"] == "e" and r["species"] == on["species"]))
        ):
            return r
    return None


def main() -> None:
    all_rows = load_points()
    new = new_points(all_rows)
    done = miss = 0
    out_rows: list[dict] = []
    for r in new:
        if not r["sc_on"]:
            continue
        on_p = ROOT / csv_rel(r)
        off = off_row(r, new)
        off_p = ROOT / csv_rel(off) if off else None
        if off_p is None or not on_p.is_file() or not off_p.is_file():
            miss += 1
            continue
        row = summarize_pair(on_p, off_p, f"{r['block']}_{v_family(r)}", r["b_gs"])
        if row is None:
            miss += 1
            continue
        row.update(
            block=r["block"], beam=r["beam"], species=r["species"], train=r["train"],
            energy_mev=r["energy_mev"], sigma_t_ns=r["sigma_t_ns"], sigma_mm=r["sigma_mm"],
            voltage_kv=r["voltage_kv"], power_kw=r["power_kw"], dx_mm=r["dx_mm"], dy_mm=r["dy_mm"],
        )
        out_rows.append(row)
        done += 1
    if out_rows:
        keys = list(out_rows[0].keys())
        with OUT.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(out_rows)
    print(f"v2 evaluate: {done} SC-on pairs summarised, {miss} incomplete, wrote {OUT if out_rows else '(nothing)'}")
    by = {}
    for r in out_rows:
        by.setdefault(r["block"], []).append(r.get("expansion_vs_no_sc_pct"))
    for blk, vals in by.items():
        nums = [v for v in vals if v == v]
        if nums:
            print(f"  {blk}: {len(nums)} expansions, median {sorted(nums)[len(nums)//2]:.1f} %")


def v_family(r: dict) -> str:
    return f"{r['beam']}_{r.get('species') or 'e'}_{int(r['sigma_mm'])}mm"


if __name__ == "__main__":
    main()
