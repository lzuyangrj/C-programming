#!/usr/bin/env python3
"""Write, list, and evaluate the 1 kV / 1 mm figure-dense VIPM add-on.

Does not relaunch points already in a summary CSV or whose particle CSV
already exists. Extraction ion offsets use aligned v2 timing.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_bscan import load_xy, stats, summarize_pair  # noqa: E402
from evaluate_emode import add_centroids, voltage_pair  # noqa: E402
from generate_csns_configs import (  # noqa: E402
    ION_SPECIES,
    ROOT,
    emode_fine_c3_voltage_points,
    emode_fine_d3_offset_points,
    imode_fine_offset_points,
    imode_fine_voltage_points,
    imode_offset_csv_name,
    imode_offset_xml_path,
    imode_volt_csv_name,
    imode_volt_xml_path,
    offset_csv_name,
    offset_xml_path,
    volt_csv_name,
    volt_xml_path,
    write_figure_dense_emode,
    write_figure_dense_imode,
)
from csv_archive import particle_csv_done  # noqa: E402
from plot_conf import load_summary  # noqa: E402
from write_v2_configs import csv_rel, write_ion, xml_path  # noqa: E402

SPECIES_LABELS = {slug: label for slug, _rest, label in ION_SPECIES}
EMODE_DIR = ROOT / "output" / "emode"
IMODE_DIR = ROOT / "output" / "imode"
V2_DIR = ROOT / "output" / "v2"

VOLT_SUM = ROOT / "output" / "csns_imode_voltage_summary.csv"
OFF_SUM = ROOT / "output" / "csns_imode_offset_summary.csv"
V2_SUM = ROOT / "output" / "csns_v2_summary.csv"
EFINE_SUM = ROOT / "output" / "csns_emode_voltage_fine_summary.csv"
EOFF_SUM = ROOT / "output" / "csns_emode_offset_summary.csv"


def _done_csv(path: Path) -> bool:
    return particle_csv_done(path)


def _load(path: Path) -> list[dict]:
    return load_summary(path) if path.is_file() else []


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys: list[str] = []
    seen: set[str] = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _merge(old: list[dict], new: list[dict], key_fn) -> list[dict]:
    idx = {key_fn(r): i for i, r in enumerate(old)}
    out = list(old)
    for r in new:
        k = key_fn(r)
        if k in idx:
            out[idx[k]] = r
        else:
            idx[k] = len(out)
            out.append(r)
    return out


def volt_key(r: dict) -> tuple:
    return (r["species"], int(r["voltage_kv"]), int(r["power_kw"]), int(r["b_gs"]))


def off_key(r: dict) -> tuple:
    return (
        r["species"],
        r["beam"],
        int(r["dx_mm"]),
        int(r["dy_mm"]),
        int(r["power_kw"]),
        int(r["b_gs"]),
    )


def v2_key(r: dict) -> tuple:
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


def efine_key(r: dict) -> tuple:
    return (int(r["voltage_kv"]), int(r["power_kw"]), int(r["b_gs"]))


def eoff_key(r: dict) -> tuple:
    return (
        r["beam"],
        int(r["dx_mm"]),
        int(r["dy_mm"]),
        int(r["power_kw"]),
        int(r["b_gs"]),
    )


def extraction_offset_points() -> list[dict]:
    """Aligned extraction Δy = −5…+5 mm and Δx = 0…10 mm at 0 G, 100 kW."""
    pts: list[dict] = []
    offsets = {(0, dy) for dy in range(-5, 6)} | {(dx, 0) for dx in range(0, 11)}
    for species, _rest, _label in ION_SPECIES:
        for dx, dy in sorted(offsets):
            if (dx, dy) == (0, 0):
                continue
            for sc_on in (True,) + ((False,) if species == "ions" else ()):
                pts.append(
                    dict(
                        mode="i",
                        block="I1",
                        beam="extraction",
                        energy_mev=1600.0,
                        sigma_t_ns=20.0,
                        sigma_mm=10,
                        dx_mm=dx,
                        dy_mm=dy,
                        voltage_kv=25,
                        power_kw=100,
                        b_gs=0,
                        species=species,
                        train="3-bunch aligned",
                        sc_on=sc_on,
                    )
                )
    return pts


def ion_voltage_in_summary(species: str, v_kv: int) -> bool:
    for r in _load(VOLT_SUM):
        if volt_key(r) == (species, v_kv, 100, 0):
            return True
    return False


def ion_offset_in_summary(species: str, beam: str, dx: int, dy: int) -> bool:
    for r in _load(OFF_SUM):
        if off_key(r) == (species, beam, dx, dy, 100, 0):
            return True
    return False


def v2_offset_in_summary(species: str, dx: int, dy: int) -> bool:
    for r in _load(V2_SUM):
        if (
            r.get("block") == "I1"
            and r.get("beam") == "extraction"
            and r.get("species") == species
            and int(float(r.get("sigma_mm") or 0)) == 10
            and int(float(r.get("voltage_kv") or 0)) == 25
            and int(float(r.get("power_kw") or 0)) == 100
            and int(float(r.get("b_gs") or 0)) == 0
            and int(float(r.get("dx_mm") or 0)) == dx
            and int(float(r.get("dy_mm") or 0)) == dy
        ):
            return True
    return False


def pending_xmls(group: str | None = None) -> list[str]:
    rels: list[str] = []

    def add(xml: Path, csv_path: Path, skip: bool) -> None:
        if skip or _done_csv(csv_path):
            return
        rels.append(str(xml.relative_to(ROOT)))

    if group in (None, "ion-voltage"):
        for species, v_kv, power_kw, b_gs, sc_on in imode_fine_voltage_points():
            add(
                imode_volt_xml_path(species, v_kv, power_kw, b_gs, sc_on),
                IMODE_DIR / imode_volt_csv_name(species, v_kv, power_kw, b_gs, sc_on),
                skip=ion_voltage_in_summary(species, v_kv) if sc_on else ion_voltage_in_summary("ions", v_kv),
            )
    if group in (None, "ion-offset"):
        for species, beam, dx, dy, power_kw, b_gs, sc_on in imode_fine_offset_points():
            if beam != "injection":
                continue
            add(
                imode_offset_xml_path(species, beam, dx, dy, power_kw, b_gs, sc_on),
                IMODE_DIR / imode_offset_csv_name(species, beam, dx, dy, power_kw, b_gs, sc_on),
                skip=ion_offset_in_summary(species if sc_on else "ions", beam, dx, dy),
            )
    if group in (None, "ion-ext"):
        for p in extraction_offset_points():
            add(
                xml_path(p),
                ROOT / csv_rel(p),
                skip=v2_offset_in_summary(p["species"] if p["sc_on"] else "ions", p["dx_mm"], p["dy_mm"]),
            )
    if group in (None, "emode-dx"):
        for beam, dx, dy, power_kw, b_gs, sc_on in emode_fine_d3_offset_points():
            add(
                offset_xml_path(beam, dx, dy, power_kw, b_gs, sc_on),
                EMODE_DIR / offset_csv_name(beam, dx, dy, power_kw, b_gs, sc_on),
                skip=False,
            )
    if group in (None, "emode-c3"):
        have = {(int(r["voltage_kv"]), int(r["power_kw"]), int(r["b_gs"])) for r in _load(EFINE_SUM)}
        for v_kv, power_kw, b_gs, sc_on in emode_fine_c3_voltage_points():
            add(
                volt_xml_path(v_kv, power_kw, b_gs, sc_on),
                EMODE_DIR / volt_csv_name(v_kv, power_kw, b_gs, sc_on),
                skip=(v_kv, power_kw, b_gs) in have,
            )
    return rels


def write_all() -> None:
    n_e = len(write_figure_dense_emode())
    n_i = len(write_figure_dense_imode())
    V2_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "configs" / "csns_rcs_ipm" / "v2").mkdir(parents=True, exist_ok=True)
    n_x = 0
    for p in extraction_offset_points():
        write_ion(p)
        n_x += 1
    print(f"wrote {n_e} e-mode, {n_i} injection-ion, {n_x} aligned-extraction XMLs")


def evaluate_ion_voltage() -> int:
    new: list[dict] = []
    for species, _rest, label in ION_SPECIES:
        for v_kv in range(5, 31):
            on = IMODE_DIR / imode_volt_csv_name(species, v_kv, 100, 0, True)
            off = IMODE_DIR / imode_volt_csv_name("ions", v_kv, 100, 0, False)
            row = summarize_pair(on, off, f"injection_{species}_s10x10", 0)
            if row is None:
                continue
            row["species"] = species
            row["species_label"] = label
            row["voltage_kv"] = v_kv
            row["power_kw"] = 100
            new.append(row)
    if not new:
        return 0
    merged = _merge(_load(VOLT_SUM), new, volt_key)
    _write(VOLT_SUM, merged)
    print(f"ion voltage: merged {len(new)} new/updated rows → {len(merged)} in {VOLT_SUM}")
    return len(new)


def evaluate_ion_offset() -> int:
    new: list[dict] = []
    for species, beam, dx, dy, power_kw, b_gs, sc_on in imode_fine_offset_points():
        if beam != "injection" or not sc_on:
            continue
        on = IMODE_DIR / imode_offset_csv_name(species, beam, dx, dy, power_kw, b_gs, True)
        off = IMODE_DIR / imode_offset_csv_name("ions", beam, dx, dy, 100, b_gs, False)
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
        new.append(row)
    if not new:
        return 0
    merged = _merge(_load(OFF_SUM), new, off_key)
    _write(OFF_SUM, merged)
    print(f"ion offset: merged {len(new)} new/updated rows → {len(merged)} in {OFF_SUM}")
    return len(new)


def evaluate_ext_offset() -> int:
    new: list[dict] = []
    for p in extraction_offset_points():
        if not p["sc_on"]:
            continue
        on = ROOT / csv_rel(p)
        off_p = dict(p, species="ions", sc_on=False)
        off = ROOT / csv_rel(off_p)
        row = summarize_pair(on, off, f"I1_extraction_{p['species']}_10mm", 0)
        if row is None:
            continue
        row.update(
            block="I1",
            beam="extraction",
            species=p["species"],
            train="3-bunch aligned",
            energy_mev=1600.0,
            sigma_t_ns=20.0,
            sigma_mm=10,
            voltage_kv=25,
            power_kw=100,
            dx_mm=p["dx_mm"],
            dy_mm=p["dy_mm"],
        )
        new.append(row)
    if not new:
        return 0
    merged = _merge(_load(V2_SUM), new, v2_key)
    _write(V2_SUM, merged)
    print(f"aligned ext. offset: merged {len(new)} new/updated rows → {len(merged)} in {V2_SUM}")
    return len(new)


def evaluate_emode_dx() -> int:
    new: list[dict] = []
    for beam, dx, dy, power_kw, b_gs, sc_on in emode_fine_d3_offset_points():
        if not sc_on:
            continue
        on = EMODE_DIR / offset_csv_name(beam, dx, dy, power_kw, b_gs, True)
        off = EMODE_DIR / offset_csv_name(beam, dx, dy, 100, b_gs, False)
        row = summarize_pair(on, off, f"{beam}_electrons", b_gs)
        if row is None:
            continue
        add_centroids(row, on, off)
        row["beam"] = beam
        row["dx_mm"] = dx
        row["dy_mm"] = dy
        row["power_kw"] = power_kw
        new.append(row)
    if not new:
        return 0
    merged = _merge(_load(EOFF_SUM), new, eoff_key)
    _write(EOFF_SUM, merged)
    print(f"e-mode Δx: merged {len(new)} new/updated rows → {len(merged)} in {EOFF_SUM}")
    return len(new)


def evaluate_emode_c3(delete_csv: bool = False) -> int:
    new: list[dict] = []
    csvs: list[Path] = []
    for v_kv, power_kw, b_gs, sc_on in emode_fine_c3_voltage_points():
        if not sc_on:
            continue
        on, off = voltage_pair(EMODE_DIR, v_kv, power_kw, b_gs)
        row = summarize_pair(on, off, "injection_electrons_s10x10", b_gs)
        if row is None:
            continue
        row["voltage_kv"] = v_kv
        row["power_kw"] = power_kw
        new.append(row)
        csvs.extend([on, off])
    if not new:
        return 0
    merged = _merge(_load(EFINE_SUM), new, efine_key)
    _write(EFINE_SUM, merged)
    print(f"e-mode C3: merged {len(new)} new/updated rows → {len(merged)} in {EFINE_SUM}")
    if delete_csv:
        n = 0
        for v_kv, power_kw, b_gs, sc_on in emode_fine_c3_voltage_points():
            path = EMODE_DIR / volt_csv_name(v_kv, power_kw, b_gs, sc_on)
            if _done_csv(path):
                path.unlink()
                n += 1
        print(f"  deleted {n} C3 particle CSVs after merge")
    return len(new)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write figure-dense XMLs")
    ap.add_argument(
        "--list-pending",
        action="store_true",
        help="print XML paths that still need a Virtual-IPM run",
    )
    ap.add_argument(
        "--group",
        choices=("ion-voltage", "ion-offset", "ion-ext", "emode-dx", "emode-c3"),
        help="restrict --list-pending / --evaluate to one group",
    )
    ap.add_argument("--evaluate", action="store_true", help="merge completed CSVs into summaries")
    ap.add_argument(
        "--delete-c3-csv",
        action="store_true",
        help="after C3 evaluate, delete those particle CSVs to free disk",
    )
    args = ap.parse_args()
    if args.write:
        write_all()
    if args.list_pending:
        for rel in pending_xmls(args.group):
            print(rel)
    if args.evaluate:
        if args.group in (None, "ion-voltage"):
            evaluate_ion_voltage()
        if args.group in (None, "ion-offset"):
            evaluate_ion_offset()
        if args.group in (None, "ion-ext"):
            evaluate_ext_offset()
        if args.group in (None, "emode-dx"):
            evaluate_emode_dx()
        if args.group in (None, "emode-c3"):
            evaluate_emode_c3(delete_csv=args.delete_c3_csv)


if __name__ == "__main__":
    main()
