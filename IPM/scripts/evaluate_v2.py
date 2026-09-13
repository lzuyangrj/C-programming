#!/usr/bin/env python3
"""Summarise completed v2 CSVs (output/v2) against their SC-off partners."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import summarize_pair  # noqa: E402
from write_v2_configs import csv_rel, load_points, new_points  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "csns_v2_summary.csv"


def _match_off(on: dict, r: dict) -> bool:
    want_sp = "ions" if on["mode"] == "i" else on["species"]
    return (
        r["mode"] == on["mode"]
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
        and (r["species"] == want_sp or on["mode"] == "e")
    )


def off_path(on: dict, all_rows: list[dict]) -> Path | None:
    """SC-off partner: v2 file if written, otherwise the matching v1 CSV."""
    for r in all_rows:
        if not _match_off(on, r):
            continue
        if not r.get("reuse"):
            return ROOT / csv_rel(r)
        return v1_off_path(on)
    return v1_off_path(on)


def v1_off_path(on: dict) -> Path | None:
    s = int(on["sigma_mm"])
    b = int(on["b_gs"])
    if on["mode"] == "e":
        beam = on["beam"]
        if beam == "ramp":
            beam = {(80.0, 120.0): "injection", (1600.0, 20.0): "extraction"}.get(
                (on["energy_mev"], on["sigma_t_ns"]), ""
            )
        if not beam:
            return None
        return ROOT / f"output/emode/csns_{beam}_electrons_s{s}x{s}mm_p100kw_b{b}G_sc_off.csv"
    if on["beam"] == "injection" and on["train"] == "3-bunch":
        return ROOT / f"output/imode/csns_injection_ions_s{s}mm_p100kw_b{b}G_sc_off.csv"
    return None


def _v2_key(r: dict) -> tuple:
    return (
        r.get("block"),
        r.get("beam"),
        r.get("species"),
        int(float(r.get("sigma_mm") or 0)),
        int(float(r.get("voltage_kv") or 0)),
        int(float(r.get("power_kw") or 0)),
        int(float(r.get("b_gs") or 0)),
        int(float(r.get("dx_mm") or 0)),
        int(float(r.get("dy_mm") or 0)),
        r.get("train"),
    )


def merge_dense_extraction() -> int:
    """Append completed I2 1 mm aligned-extraction rows; do not rewrite v1/v2."""
    from scan_matrix_v2 import i2_dense_extraction_points  # noqa: PLC0415

    existing: list[dict] = []
    if OUT.is_file():
        with OUT.open() as fh:
            existing = list(csv.DictReader(fh))
    idx = {_v2_key(r): i for i, r in enumerate(existing)}
    added = 0
    for r in i2_dense_extraction_points():
        if not r["sc_on"]:
            continue
        on_p = ROOT / csv_rel(r)
        # H₂⁺ SC-off is shared across power (no bunch field).
        off_p = ROOT / csv_rel(dict(r, species="ions", sc_on=False, power_kw=100))
        if not on_p.is_file() or not off_p.is_file():
            continue
        row = summarize_pair(on_p, off_p, f"{r['block']}_{v_family(r)}", r["b_gs"])
        if row is None:
            continue
        row.update(
            block=r["block"],
            beam=r["beam"],
            species=r["species"],
            train=r["train"],
            energy_mev=r["energy_mev"],
            sigma_t_ns=r["sigma_t_ns"],
            sigma_mm=r["sigma_mm"],
            voltage_kv=r["voltage_kv"],
            power_kw=r["power_kw"],
            dx_mm=r["dx_mm"],
            dy_mm=r["dy_mm"],
        )
        k = _v2_key(row)
        if k in idx:
            existing[idx[k]] = row
        else:
            idx[k] = len(existing)
            existing.append(row)
            added += 1
    if existing:
        keys = list(existing[0].keys())
        with OUT.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(existing)
    print(f"I2 dense extraction: merged {added} new rows → {len(existing)} in {OUT}")
    return added


def main() -> None:
    if "--dense-ext" in sys.argv:
        merge_dense_extraction()
        return
    all_rows = load_points()
    new = new_points(all_rows)
    done = miss = 0
    out_rows: list[dict] = []
    for r in new:
        if not r["sc_on"]:
            continue
        on_p = ROOT / csv_rel(r)
        off_p = off_path(r, all_rows)
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
    plot_i1_aligned(out_rows)


def plot_i1_aligned(rows: list[dict]) -> None:
    from plot_conf import plot_conf
    import matplotlib.pyplot as plt

    plot_conf()
    model = {"ions": 102.0, "h2o_ions": 40.0, "n2_ions": 39.0}
    asrun = {"ions": 33.5, "h2o_ions": 55.6, "n2_ions": 49.9}
    labels = [("ions", r"H$_2^+$"), ("h2o_ions", r"H$_2$O$^+$"), ("n2_ions", r"N$_2^+$")]
    aligned = {}
    for r in rows:
        if (
            r.get("block") == "I1"
            and float(r["sigma_mm"]) == 10
            and int(r["power_kw"]) == 100
            and int(r["b_gs"]) == 0
            and int(r["voltage_kv"]) == 25
            and int(r["dx_mm"]) == 0
            and int(r["dy_mm"]) == 0
        ):
            aligned[r["species"]] = float(r["expansion_vs_no_sc_pct"])
    if len(aligned) < 3:
        return
    fig, ax = plt.subplots()
    x = range(3)
    w = 0.25
    ax.bar([i - w for i in x], [asrun[s] for s, _ in labels], w, label="ion born 125 ns early", color="C0")
    ax.bar(list(x), [aligned[s] for s, _ in labels], w, label="ion born with the bunch", color="C3")
    ax.bar([i + w for i in x], [model[s] for s, _ in labels], w, label="kick model (born with bunch)", color="0.45")
    ax.set_xticks(list(x))
    ax.set_xticklabels([lab for _, lab in labels])
    ax.set_ylabel(r"expansion vs no-SC [\%]")
    ax.set_title(r"Extraction 10 mm, 0 G, 100 kW, 25 kV")
    ax.legend(fontsize=9)
    path = ROOT / "plots" / "csns_v2_aligned_extraction.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("wrote", path)


def v_family(r: dict) -> str:
    return f"{r['beam']}_{r.get('species') or 'e'}_{int(r['sigma_mm'])}mm"


if __name__ == "__main__":
    main()
