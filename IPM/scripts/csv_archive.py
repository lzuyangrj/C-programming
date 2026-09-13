#!/usr/bin/env python3
"""Particle-CSV archive helpers: skip-if-zipped and one-file zip+delete.

Never zip allowlisted summary / invert tables. A path is 'done' if the
uncompressed CSV or a sibling .csv.zip / .csv.gz exists and is non-empty.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

PARTICLE_DIRS = (
    OUT / "emode",
    OUT / "v2",
    OUT / "ionsize",
    OUT / "bscan5",
    OUT / "bscan5_power",
    OUT / "imode",
    OUT / "bscan",
)

KEEP_NAMES = frozenset(
    {
        "csns_space_charge_summary.csv",
        "csns_space_charge_summary_sig10.csv",
        "csns_bscan_summary.csv",
        "csns_bscan5_summary.csv",
        "csns_bscan_power_summary.csv",
        "csns_ionsize_summary.csv",
        "csns_emode_bscan300_summary.csv",
        "csns_emode_size_summary.csv",
        "csns_emode_voltage_summary.csv",
        "csns_emode_offset_summary.csv",
        "csns_emode_voltage_fine_summary.csv",
        "csns_emode_offset_fine_summary.csv",
        "csns_imode_bscan_summary.csv",
        "csns_imode_size_summary.csv",
        "csns_imode_voltage_summary.csv",
        "csns_imode_offset_summary.csv",
        "csns_imode_kick_model.csv",
        "csns_imode_inversion.csv",
        "csns_imode_voltage_1kv.csv",
        "csns_review_scaling_checks.csv",
        "csns_scan_matrix_v2.csv",
        "csns_v2_summary.csv",
        "lhc_6p5tev_electrons_smoke.csv",
    }
)


def particle_csv_done(path: Path | str) -> bool:
    """True if the 100 k archive is on disk as CSV, .csv.zip, or .csv.gz."""
    p = Path(path)
    for cand in (p, Path(str(p) + ".zip"), Path(str(p) + ".gz")):
        if cand.is_file() and cand.stat().st_size > 0:
            return True
    return False


def zip_path_for(csv_path: Path) -> Path:
    return Path(str(csv_path) + ".zip")


def zip_one(csv_path: Path) -> Path | None:
    """Zip one particle CSV and delete the original. Returns the zip path."""
    csv_path = Path(csv_path)
    if csv_path.name in KEEP_NAMES:
        return None
    if not csv_path.is_file() or csv_path.stat().st_size == 0:
        return zip_path_for(csv_path) if particle_csv_done(csv_path) else None
    dest = zip_path_for(csv_path)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    if tmp.exists():
        tmp.unlink()
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        zf.write(csv_path, arcname=csv_path.name)
    tmp.replace(dest)
    if dest.is_file() and dest.stat().st_size > 0:
        csv_path.unlink()
        return dest
    raise RuntimeError(f"zip failed: {csv_path}")


def iter_particle_csvs() -> list[Path]:
    found: list[Path] = []
    for folder in PARTICLE_DIRS:
        if not folder.is_dir():
            continue
        found.extend(sorted(p for p in folder.glob("*.csv") if p.name not in KEEP_NAMES))
    if OUT.is_dir():
        for p in sorted(OUT.glob("csns_*_sc_on.csv")) + sorted(OUT.glob("csns_*_sc_off.csv")):
            if p.name not in KEEP_NAMES:
                found.append(p)
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    paths = iter_particle_csvs()
    print(f"particle CSVs to zip: {len(paths)}")
    n = 0
    for i, p in enumerate(paths, 1):
        if args.dry_run:
            print(f"  would zip {p}")
            continue
        zip_one(p)
        n += 1
        if i == 1 or i % 100 == 0 or i == len(paths):
            print(f"  zipped {i}/{len(paths)}  last={p.name}", flush=True)
    print(f"zipped {n} files")


if __name__ == "__main__":
    main()
