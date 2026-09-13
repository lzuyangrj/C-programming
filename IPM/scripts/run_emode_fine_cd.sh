#!/usr/bin/env bash
# Fine C/D e-mode scans (round 10×10 mm). Not part of run_emode_replan.sh.
#   C1  5–30 kV / 1 kV at diagnostic B
#   C2  5 G B-scan at 10/12/15/18/20 kV (25 kV / 5 G is Block A)
#   D1  Δy = −10…+10 mm / 1 mm at diagnostic B (Δy=0 is Block A)
#   D2  5 G B-scan at Δy = ±5 mm
# Points whose CSV already exists are skipped.
#
#   ./scripts/run_emode_fine_cd.sh --matrix   # show the matrix only
#   JOBS=4 ./scripts/run_emode_fine_cd.sh     # run the missing points
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--matrix" ]]; then
  python scripts/generate_csns_configs.py --emode-fine-cd-matrix
  exit 0
fi

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py --emode-fine-cd >/dev/null
python scripts/generate_csns_configs.py --emode-fine-cd-matrix

mapfile -t CASES < <(python scripts/generate_csns_configs.py --emode-fine-cd-list)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No fine C/D configs found" >&2
  exit 1
fi

mkdir -p output output/emode plots

echo "Running ${#CASES[@]} fine C/D configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" ]] && { [[ -s "${csv}" ]] || [[ -s "${csv}.zip" ]] || [[ -s "${csv}.gz" ]]; }; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

python scripts/evaluate_emode.py --fine-cd
