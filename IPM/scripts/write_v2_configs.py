#!/usr/bin/env python3
"""Write Virtual-IPM XMLs for scan-matrix v2 (SCAN_MATRIX_V2.md).

Reads output/csns_scan_matrix_v2.csv (or regenerates it). Reuse=True rows are
skipped (v1 CSVs already exist). Extraction ions always get aligned timing:
generation-window centre = first tracking-bunch centre (80 ns at extraction).
Writes no particles; run with scripts/run_v2.sh.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_csns_configs import (  # noqa: E402
    BEAMS,
    E_Y,
    GAP_M,
    GS_TO_T,
    ION_SPECIES,
    N_PER_BUNCH_100KW,
    ROOT,
    _signed,
    b_tag,
    beam_xml,
    circular_train,
    device_and_fields,
    electron_case,
    electron_generation,
    ion_generation,
    n_bunch_at_power,
    round_sigma_xy_um,
    simulation,
    single_bunch_train,
    wrap,
    write,
)
from scan_matrix_v2 import existing_keys, imode_points, is_reuse, key_of  # noqa: E402
from scan_matrix_v2 import dedupe, emode_points, i2_dense_extraction_points  # noqa: E402

V2_CFG = ROOT / "configs" / "csns_rcs_ipm" / "v2"
V2_CSV = "output/v2"
OUT_CSV = ROOT / "output" / "csns_scan_matrix_v2.csv"
SPECIES_REST = {slug: rest for slug, rest, _ in ION_SPECIES}


def circular_first_arrival_ns(n: int, spacing_ns: float, offset_ns: float) -> float:
    """First t ≥ 0 at which a CircularBunchTrain bunch centre is at z = 0."""
    window = n * spacing_ns / 2.0
    max_off = window - spacing_ns / 2.0
    offsets = [max_off - k * spacing_ns for k in range(n)]
    if offset_ns != 0:
        sign = 1.0 if offset_ns > 0 else -1.0
        w = window
        rolled = []
        for o in offsets:
            x = (o + sign * w + offset_ns) % (sign * 2 * w) - sign * w
            if abs(x - w) < 1e-9:
                x = -w
            rolled.append(x)
        offsets = rolled
    arrivals = sorted(-o for o in offsets if o <= 1e-9)
    if not arrivals:
        raise RuntimeError(f"no approaching bunch: n={n} s={spacing_ns} L={offset_ns}")
    return float(arrivals[0])


def timing_ok(beam: str, sigma_t_ns: float, train: str) -> tuple[float, float]:
    """Return (gen_center_ns, first_bunch_ns). Abort if they differ by > 1 ns."""
    gen = 4.0 * sigma_t_ns
    spec = BEAMS[beam] if beam in BEAMS else None
    if train in ("single", "single aligned"):
        first = gen
    elif train == "3-bunch aligned":
        if spec is None:
            raise RuntimeError(f"aligned 3-bunch needs a named beam, got {beam}")
        first = circular_first_arrival_ns(3, spec["spacing_ns"], -4.0 * sigma_t_ns)
    elif train == "3-bunch":
        if spec is None:
            raise RuntimeError(f"3-bunch needs a named beam, got {beam}")
        first = circular_first_arrival_ns(3, spec["spacing_ns"], spec["offset_ns"])
    else:
        raise RuntimeError(f"unknown train {train!r}")
    if abs(first - gen) > 1.0:
        raise RuntimeError(
            f"timing abort: {beam} {train}: generation centre {gen:.2f} ns, "
            f"first bunch {first:.2f} ns"
        )
    return gen, first


def v2_slug(p: dict) -> str:
    beam = p["beam"]
    s = int(p["sigma_mm"])
    pw = int(p["power_kw"])
    v = int(p["voltage_kv"])
    dx, dy = int(p["dx_mm"]), int(p["dy_mm"])
    if p["mode"] == "e":
        if p["block"] == "E1":
            return f"ramp_e{int(p['energy_mev'])}mev_st{p['sigma_t_ns']:.0f}ns_s10x10mm_p{pw}kw"
        if v != 25:
            return f"{beam}_electrons_s{s}x{s}mm_v{v}kv_p{pw}kw"
        return f"{beam}_electrons_s{s}x{s}mm_p{pw}kw"
    sp = p["species"] or "ions"
    infix = {"3-bunch aligned": "aligned", "single aligned": "single_aligned", "single": "single",
             "3-bunch": ""}.get(p["train"], p["train"])
    mid = f"_{infix}" if infix else ""
    if dx or dy:
        return f"{beam}_{sp}{mid}_s{s}x{s}mm_dx{_signed(dx)}mm_dy{_signed(dy)}mm_p{pw}kw"
    if v != 25:
        return f"{beam}_{sp}{mid}_s{s}x{s}mm_v{v}kv_p{pw}kw"
    return f"{beam}_{sp}{mid}_s{s}mm_p{pw}kw"


def csv_rel(p: dict) -> str:
    return f"{V2_CSV}/csns_{v2_slug(p)}_{b_tag(int(p['b_gs']))}_{'sc_on' if p['sc_on'] else 'sc_off'}.csv"


def xml_path(p: dict) -> Path:
    return V2_CFG / f"{v2_slug(p)}_{b_tag(int(p['b_gs']))}_{'sc_on' if p['sc_on'] else 'sc_off'}.xml"


def write_electron(p: dict) -> Path:
    energy_mev = float(p["energy_mev"])
    if energy_mev >= 1000:
        energy, unit = f"{energy_mev / 1000:g}", "GeV"
    else:
        energy, unit = f"{energy_mev:g}", "MeV"
    st = float(p["sigma_t_ns"])
    if abs(st - 120) < 0.1:
        sim_time, sim_unit = "1100", "ns"
    elif abs(st - 20) < 0.1:
        sim_time, sim_unit = "220", "ns"
    else:
        sim_time, sim_unit = str(int(8 * st + 60)), "ns"
    return electron_case(
        v2_slug(p),
        energy=energy,
        energy_unit=unit,
        sigma_t_ns=st,
        sigma_xy_um=round_sigma_xy_um(p["sigma_mm"]),
        sim_time=sim_time,
        sim_unit=sim_unit,
        n_steps=8000,
        sc_on=bool(p["sc_on"]),
        b_y=int(p["b_gs"]) * GS_TO_T,
        b_tag=b_tag(int(p["b_gs"])),
        config_dir=V2_CFG,
        csv_dir=V2_CSV,
        n_bunch=n_bunch_at_power(p["power_kw"]),
        e_y=float(p["voltage_kv"]) * 1e3 / GAP_M,
    )


def write_ion(p: dict) -> Path:
    beam = p["beam"]
    spec = BEAMS[beam]
    st = float(p["sigma_t_ns"])
    train = p["train"]
    timing_ok(beam, st, train)
    if train == "3-bunch aligned":
        track = circular_train(3, spec["spacing_ns"], -4.0 * st)
    elif train == "3-bunch":
        track = circular_train(3, spec["spacing_ns"], spec["offset_ns"])
    elif train in ("single", "single aligned"):
        track = single_bunch_train()
    else:
        raise RuntimeError(train)
    pop = n_bunch_at_power(p["power_kw"])
    sigma = round_sigma_xy_um(p["sigma_mm"])
    offset = (p["dx_mm"], p["dy_mm"]) if (p["dx_mm"] or p["dy_mm"]) else None
    cage_e = -float(p["voltage_kv"]) * 1e3 / GAP_M
    rest = SPECIES_REST[p["species"] or "ions"]
    stem = f"{v2_slug(p)}_{b_tag(int(p['b_gs']))}_{'sc_on' if p['sc_on'] else 'sc_off'}"
    csv = f"{V2_CSV}/csns_{stem}.csv"
    gen = beam_xml(
        energy=spec["energy"], energy_unit=spec["energy_unit"], sigma_t_ns=st,
        sigma_xy_um=sigma, n_bunch=pop, e_off=True, b_off=True,
        train=single_bunch_train(), offset_mm=offset,
    )
    trk = beam_xml(
        energy=spec["energy"], energy_unit=spec["energy_unit"], sigma_t_ns=st,
        sigma_xy_um=sigma, n_bunch=pop, e_off=not p["sc_on"], b_off=not p["sc_on"],
        train=track, offset_mm=offset,
    )
    xml = wrap(
        "    <Beams>\n" + gen + "\n" + trk + "\n    </Beams>\n"
        + device_and_fields(e_y=cage_e, b_y=int(p["b_gs"]) * GS_TO_T) + "\n"
        + ion_generation() + "\n"
        + simulation(
            n_particles=100000, sim_time="12", sim_unit="us", n_steps=8000,
            charge=1, rest_energy=rest, filename=csv,
        )
    )
    path = V2_CFG / f"{stem}.xml"
    write(path, xml)
    return path


def load_points() -> list[dict]:
    if OUT_CSV.is_file():
        rows = []
        with OUT_CSV.open() as fh:
            for r in csv.DictReader(fh):
                r["energy_mev"] = float(r["energy_mev"])
                r["sigma_t_ns"] = float(r["sigma_t_ns"])
                r["sigma_mm"] = float(r["sigma_mm"])
                r["dx_mm"] = int(float(r["dx_mm"]))
                r["dy_mm"] = int(float(r["dy_mm"]))
                r["voltage_kv"] = int(float(r["voltage_kv"]))
                r["power_kw"] = int(float(r["power_kw"]))
                r["b_gs"] = int(float(r["b_gs"]))
                r["sc_on"] = str(r["sc_on"]).lower() in ("true", "1")
                r["reuse"] = str(r.get("reuse", "")).lower() in ("true", "1")
                rows.append(r)
        return rows
    have = existing_keys()
    rows = dedupe(emode_points() + imode_points())
    for r in rows:
        r["reuse"] = is_reuse(r, have)
    return rows


def new_points(rows: list[dict]) -> list[dict]:
    return [r for r in rows if not r.get("reuse")]


def write_all(rows: list[dict]) -> list[Path]:
    V2_CFG.mkdir(parents=True, exist_ok=True)
    (ROOT / "output" / "v2").mkdir(parents=True, exist_ok=True)
    paths = []
    for r in rows:
        paths.append(write_electron(r) if r["mode"] == "e" else write_ion(r))
    return paths


def order_rows(rows: list[dict]) -> list[dict]:
    rank = {"I1": 0, "I2": 1, "E1": 2, "E3": 3, "E4": 4, "I3": 5}
    return sorted(rows, key=lambda r: (rank.get(r["block"], 9), v2_slug(r), r["b_gs"], not r["sc_on"]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write XMLs for new (non-reuse) points")
    ap.add_argument("--list", action="store_true", help="print XML paths in run order")
    ap.add_argument("--matrix", action="store_true", help="print block counts")
    ap.add_argument(
        "--dense-ext",
        action="store_true",
        help="I2 1 mm aligned-extraction fill-in (H2O+/N2+ SC-on, H2+ SC-off)",
    )
    args = ap.parse_args()
    if args.dense_ext:
        rows = i2_dense_extraction_points()
        if args.matrix or not (args.write or args.list):
            ons = [r for r in rows if r["sc_on"]]
            offs = [r for r in rows if not r["sc_on"]]
            print(
                f"I2 dense extraction: {len(rows)} points "
                f"({len(ons)} SC-on, {len(offs)} H2+ SC-off); "
                f"sizes {[int(r['sigma_mm']) for r in offs]}"
            )
            for r in rows[:1]:
                g, f = timing_ok(r["beam"], r["sigma_t_ns"], r["train"])
                print(f"  timing sample {r['beam']} {r['train']}: gen {g:.1f} ns, first {f:.1f} ns")
            bad = 0
            for r in rows:
                try:
                    timing_ok(r["beam"], r["sigma_t_ns"], r["train"])
                except RuntimeError as exc:
                    print("FAIL", exc)
                    bad += 1
            if bad:
                raise SystemExit(f"{bad} timing failures")
            print("  timing contract: all dense extraction ion points pass (|Δ| ≤ 1 ns)")
        if args.write:
            paths = write_all(rows)
            print(f"wrote {len(paths)} XMLs under {V2_CFG}")
        if args.list:
            for r in rows:
                print(xml_path(r))
        return
    rows = load_points()
    new = order_rows(new_points(rows))
    if args.matrix or not (args.write or args.list):
        print("v2 new XMLs to write / run (reuse skipped):")
        for blk in ("I1", "I2", "E1", "E3", "E4", "I3"):
            sel = [r for r in new if r["block"] == blk]
            print(f"  {blk}: {len(sel)}")
        print(f"  Total new: {len(new)}   reused (not written): {len(rows) - len(new)}")
        ions = [r for r in new if r["mode"] == "i"]
        for r in ions[:1]:
            g, f = timing_ok(r["beam"], r["sigma_t_ns"], r["train"])
            print(f"  timing sample {r['beam']} {r['train']}: gen {g:.1f} ns, first {f:.1f} ns")
        bad = 0
        for r in ions:
            try:
                timing_ok(r["beam"], r["sigma_t_ns"], r["train"])
            except RuntimeError as exc:
                print("FAIL", exc)
                bad += 1
        if bad:
            raise SystemExit(f"{bad} timing failures")
        print("  timing contract: all extraction/injection ion points pass (|Δ| ≤ 1 ns)")
    if args.write:
        paths = write_all(new)
        print(f"wrote {len(paths)} XMLs under {V2_CFG}")
    if args.list:
        for r in new:
            print(xml_path(r))


if __name__ == "__main__":
    main()
