#!/usr/bin/env python3
"""Revised CSNS IPM scan matrix (v2) derived from LITERATURE_REVIEW.md.

Enumerates the proposed points, tells which ones already exist as summary
rows, prints the block table and writes output/csns_scan_matrix_v2.csv.
It writes no Virtual-IPM XML and launches nothing; the generator hooks for
the new axes (beam energy, aligned extraction timing, single-bunch train)
are listed in SCAN_MATRIX_V2.md.

Each point is (mode, block, beam, energy_mev, sigma_t_ns, sigma_mm, dx_mm,
dy_mm, voltage_kv, power_kw, b_gs, species, train, sc_on).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.constants import e, m_e

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

GAP_M = 0.231
PROTON_MEV = 938.272
CIRCUMFERENCE_M = 227.92
SIGMA_T_NS = {"injection": 120.0, "extraction": 20.0}
ENERGY_MEV = {"injection": 80.0, "extraction": 1600.0}
SPECIES = ("ions", "h2o_ions", "n2_ions")

# ---- e-mode -----------------------------------------------------------------
# E1 ramp / β scan (review §2.1 "low-β benchmark: open"; PRAB N/β column).
E1_ENERGIES_MEV = (80, 200, 400, 800, 1200, 1600)
E1_SIGMA_T_NS = (120.0, 20.0)  # fixed bunch lengths isolate β; ramp table later
E1_B_GS = (0, 100, 200, 300, 500, 1000)
E1_POWERS_KW = (100, 500)
# E3 cyclotron-phase-aware voltage scan for the beams Block C never covered (review §2.3).
E3_BEAMS = (("extraction", 10), ("injection", 25))
E3_VOLTAGES_KV = (10, 15, 20, 30)  # 25 kV = Block A
E3_HALF_PERIODS = 6  # sample k·ΔB (zeros) and (k+½)·ΔB (extrema), k = 1..6
E3_POWERS_KW = (100, 500)
# E4 low-power commissioning points (review §2.6: CSNS commissioning at ≈ 80 kW).
E4_POWERS_KW = (20, 50, 80)
E4_B_GS = (0, 100, 200, 300, 1000)
REF_BEAMS = (("injection", 25), ("extraction", 10), ("injection", 10))

# ---- ion mode ---------------------------------------------------------------
I_B_GS = (0, 1000)  # 200 G dropped (review §3.4: < 0.5 % change)
# I1 aligned extraction re-run (review §3.5) — replaces the as-run extraction ion points.
I1_SIZES_MM = (3, 5, 7, 10, 15, 20)
I1_POWERS_KW = (100, 200, 300, 400, 500)
I1_OFFSETS_MM = ((10, 0), (0, 5), (0, -5))
I1_OFFSET_POWERS_KW = (100, 500)
I1_VOLTAGES_KV = (5, 10, 15, 20, 25, 30)
# I2 correction look-up table (review §3.7 recipe): h(σ₀, N, species) at 0 G, 25 kV.
I2_SIZES_MM = (5, 10, 15, 20, 25)
I2_POWERS_KW = (20, 50, 80, 100, 150, 200, 250, 300, 400, 500)
# 1 mm identified-species invert at aligned extraction (not in the coarse I1/I2 grids).
I2_DENSE_SIZES_MM = tuple(range(3, 21))
I2_DENSE_POWERS_KW = (100, 200, 300, 500)
# I3 single-bunch vs 3-bunch train (review §3.1 mixed regime, Shiltsev 1 + 0.8 t_b/τ₀).
I3_POWER_KW = 100


def beta(energy_mev: float) -> float:
    gamma = 1 + energy_mev / PROTON_MEV
    return float(np.sqrt(1 - 1 / gamma**2))


def electron_tof_s(voltage_kv: float) -> float:
    field = voltage_kv * 1e3 / GAP_M
    return float(np.sqrt(2 * (GAP_M / 2) * m_e / (e * field)))


def phase_grid_gs(voltage_kv: float, half_periods: int) -> tuple[int, ...]:
    """B values at the predicted zeros (k·ΔB) and extrema ((k+½)·ΔB) of Δ(B)."""
    d_b = np.pi * m_e / (e * electron_tof_s(voltage_kv)) * 1e4
    pts = [round(k * d_b / 2 / 5) * 5 for k in range(1, 2 * half_periods + 1)]
    return (0,) + tuple(int(p) for p in pts) + (1000,)


def point(**kw) -> dict:
    base = dict(
        mode="", block="", beam="", energy_mev=None, sigma_t_ns=None, sigma_mm=None,
        dx_mm=0, dy_mm=0, voltage_kv=25, power_kw=100, b_gs=0, species="", train="3-bunch",
        sc_on=True,
    )
    base.update(kw)
    if base["energy_mev"] is None:
        base["energy_mev"] = ENERGY_MEV[base["beam"]]
    if base["sigma_t_ns"] is None:
        base["sigma_t_ns"] = SIGMA_T_NS[base["beam"]]
    return base


def emode_points() -> list[dict]:
    pts: list[dict] = []
    # E1
    for en in E1_ENERGIES_MEV:
        for st in E1_SIGMA_T_NS:
            for b in E1_B_GS:
                for p in E1_POWERS_KW:
                    pts.append(point(mode="e", block="E1", beam="ramp", energy_mev=en, sigma_t_ns=st,
                                     sigma_mm=10, power_kw=p, b_gs=b))
                pts.append(point(mode="e", block="E1", beam="ramp", energy_mev=en, sigma_t_ns=st,
                                 sigma_mm=10, b_gs=b, sc_on=False))
    # E3
    for beam, s in E3_BEAMS:
        for v in E3_VOLTAGES_KV:
            for b in phase_grid_gs(v, E3_HALF_PERIODS):
                for p in E3_POWERS_KW:
                    pts.append(point(mode="e", block="E3", beam=beam, sigma_mm=s, voltage_kv=v, power_kw=p, b_gs=b))
                pts.append(point(mode="e", block="E3", beam=beam, sigma_mm=s, voltage_kv=v, b_gs=b, sc_on=False))
    # E4 (SC-off shared with Block A)
    for beam, s in REF_BEAMS:
        for p in E4_POWERS_KW:
            for b in E4_B_GS:
                pts.append(point(mode="e", block="E4", beam=beam, sigma_mm=s, power_kw=p, b_gs=b))
    return pts


def imode_points() -> list[dict]:
    pts: list[dict] = []
    # I1 aligned extraction: A' (10 mm ref), B' sizes, C' voltage, D' offsets
    for s in I1_SIZES_MM:
        for b in I_B_GS:
            for sp in SPECIES:
                for p in I1_POWERS_KW:
                    pts.append(point(mode="i", block="I1", beam="extraction", sigma_mm=s, power_kw=p, b_gs=b,
                                     species=sp, train="3-bunch aligned"))
            pts.append(point(mode="i", block="I1", beam="extraction", sigma_mm=s, b_gs=b, species="ions",
                             train="3-bunch aligned", sc_on=False))
    for v in I1_VOLTAGES_KV:
        if v == 25:
            continue
        for sp in SPECIES:
            for p in I1_OFFSET_POWERS_KW:
                pts.append(point(mode="i", block="I1", beam="extraction", sigma_mm=10, voltage_kv=v, power_kw=p,
                                 species=sp, train="3-bunch aligned"))
        pts.append(point(mode="i", block="I1", beam="extraction", sigma_mm=10, voltage_kv=v, species="ions",
                         train="3-bunch aligned", sc_on=False))
    for dx, dy in I1_OFFSETS_MM:
        for b in I_B_GS:
            for sp in SPECIES:
                for p in I1_OFFSET_POWERS_KW:
                    pts.append(point(mode="i", block="I1", beam="extraction", sigma_mm=10, dx_mm=dx, dy_mm=dy,
                                     power_kw=p, b_gs=b, species=sp, train="3-bunch aligned"))
            pts.append(point(mode="i", block="I1", beam="extraction", sigma_mm=10, dx_mm=dx, dy_mm=dy, b_gs=b,
                             species="ions", train="3-bunch aligned", sc_on=False))
    # I2 look-up table at 0 G, 25 kV
    for beam in ("injection", "extraction"):
        train = "3-bunch aligned" if beam == "extraction" else "3-bunch"
        for s in I2_SIZES_MM:
            for sp in SPECIES:
                for p in I2_POWERS_KW:
                    pts.append(point(mode="i", block="I2", beam=beam, sigma_mm=s, power_kw=p, species=sp, train=train))
            pts.append(point(mode="i", block="I2", beam=beam, sigma_mm=s, species="ions", train=train, sc_on=False))
    # I3 single bunch vs train. Extraction must use the same −4σ_t default as
    # the generation bunch (train="single aligned"); a SingleBunch that inherits
    # BEAMS["extraction"]["offset_ns"] = −204.6 ns would recreate the 125 ns lag.
    for beam, s in REF_BEAMS:
        train = "single aligned" if beam == "extraction" else "single"
        for sp in SPECIES:
            pts.append(point(mode="i", block="I3", beam=beam, sigma_mm=s, power_kw=I3_POWER_KW, species=sp,
                             train=train))
        pts.append(point(mode="i", block="I3", beam=beam, sigma_mm=s, species="ions", train=train, sc_on=False))
    return pts


def i2_dense_extraction_points() -> list[dict]:
    """Aligned extraction I2 fill-in: 1 mm in σ₀ at B = 0, 25 kV.

    H₂O⁺ / N₂⁺ SC-on; H₂⁺ SC-off is shared. Existing I1/I2 sizes are omitted
    so completed 100 k v2 CSVs are not rewritten.
    """
    have = set(I1_SIZES_MM) | set(I2_SIZES_MM)
    pts: list[dict] = []
    for s in I2_DENSE_SIZES_MM:
        if s in have:
            continue
        for sp in ("h2o_ions", "n2_ions"):
            for p in I2_DENSE_POWERS_KW:
                pts.append(
                    point(
                        mode="i",
                        block="I2",
                        beam="extraction",
                        sigma_mm=s,
                        power_kw=p,
                        species=sp,
                        train="3-bunch aligned",
                    )
                )
        pts.append(
            point(
                mode="i",
                block="I2",
                beam="extraction",
                sigma_mm=s,
                species="ions",
                train="3-bunch aligned",
                sc_on=False,
            )
        )
    return pts


def dedupe(pts: list[dict]) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for p in pts:
        key = tuple((k, p[k]) for k in sorted(p) if k != "block")
        seen.setdefault(key, p)
    return list(seen.values())


def existing_keys() -> set[tuple]:
    """Points already on disk as summary rows.

    Injection ion points of I2 overlap Blocks A/B (correctly timed); e-mode E1
    points at (80 MeV, 120 ns) and (1.6 GeV, 20 ns) are the Block A 10 mm beams.
    Extraction ion rows are never reused (timing artefact, review §3.5).
    """
    keys: set[tuple] = set()
    for name in ("csns_imode_size_summary.csv", "csns_imode_bscan_summary.csv"):
        path = OUT / name
        if not path.is_file():
            continue
        with path.open() as fh:
            for r in csv.DictReader(fh):
                if r["beam"] != "injection":
                    continue
                s, b = int(float(r["sigma_x_mm"])), int(float(r["b_gs"]))
                keys.add(("i", "injection", s, int(float(r["power_kw"])), b, r["species"], True))
                keys.add(("i", "injection", s, 100, b, "ions", False))
    for name in ("csns_emode_bscan300_summary.csv", "csns_emode_size_summary.csv"):
        path = OUT / name
        if not path.is_file():
            continue
        with path.open() as fh:
            for r in csv.DictReader(fh):
                s, b = int(float(r["sigma_x_mm"])), int(float(r["b_gs"]))
                keys.add(("e", r["beam"], s, int(float(r["power_kw"])), b, "", True))
                keys.add(("e", r["beam"], s, 100, b, "", False))
    return keys


def key_of(p: dict) -> tuple:
    beam = p["beam"]
    if beam == "ramp":
        beam = {(80, 120.0): "injection", (1600, 20.0): "extraction"}.get((p["energy_mev"], p["sigma_t_ns"]), "ramp")
    return (p["mode"], beam, p["sigma_mm"], p["power_kw"] if p["sc_on"] else 100, p["b_gs"],
            p["species"], p["sc_on"])


def is_reuse(p: dict, have: set[tuple]) -> bool:
    if p["voltage_kv"] != 25 or p["dx_mm"] or p["dy_mm"] or p["train"] not in ("3-bunch",):
        return False
    return key_of(p) in have


def report(pts: list[dict], have: set[tuple]) -> str:
    lines = ["Block  description                                              runs   reuse    new",
             "-" * 82]
    desc = {
        "E1": "ramp / β scan, 6 energies × 2 σ_t, 10 mm, 6 B, 100/500 kW",
        "E3": "phase-aware B grid × V (10–30 kV), ext. 10 mm + inj. 25 mm",
        "E4": "low power 20/50/80 kW, 3 ref. beams, 5 B",
        "I1": "aligned extraction: sizes × 5 P × 2 B, V scan, 3 offsets",
        "I2": "look-up h(σ₀, N, species): 5 σ × 10 P, inj. + aligned ext.",
        "I3": "single bunch vs 3-bunch; extraction is single aligned",
    }
    tot = [0, 0, 0]
    for blk in ("E1", "E3", "E4", "I1", "I2", "I3"):
        sel = [p for p in pts if p["block"] == blk]
        reuse = sum(1 for p in sel if is_reuse(p, have))
        lines.append(f"{blk:5s}  {desc[blk]:56s} {len(sel):5d} {reuse:7d} {len(sel) - reuse:6d}")
        tot[0] += len(sel)
        tot[1] += reuse
        tot[2] += len(sel) - reuse
    lines.append("-" * 82)
    lines.append(f"{'Total':5s}  {'':56s} {tot[0]:5d} {tot[1]:7d} {tot[2]:6d}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", type=Path, default=OUT / "csns_scan_matrix_v2.csv")
    args = ap.parse_args()
    pts = dedupe(emode_points() + imode_points())
    have = existing_keys()
    print("Phase-aware B grids [G] (zeros k·ΔB and extrema (k+½)·ΔB, ΔB = π m_e/(e·ToF)):")
    for v in E3_VOLTAGES_KV + (25,):
        print(f"  {v:2d} kV: {phase_grid_gs(v, E3_HALF_PERIODS)}")
    print("Ramp β:", ", ".join(f"{en} MeV → β = {beta(en):.3f}" for en in E1_ENERGIES_MEV))
    print()
    print(report(pts, have))
    keys = ["mode", "block", "beam", "energy_mev", "sigma_t_ns", "sigma_mm", "dx_mm", "dy_mm", "voltage_kv",
            "power_kw", "b_gs", "species", "train", "sc_on", "reuse"]
    with args.csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for p in pts:
            row = {k: p[k] for k in keys if k != "reuse"}
            row["reuse"] = is_reuse(p, have)
            w.writerow(row)
    print("wrote", args.csv)


if __name__ == "__main__":
    main()
