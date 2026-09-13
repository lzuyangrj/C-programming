#!/usr/bin/env bash
# Aligned-extraction I2 1 mm fill-in. SKIP if the CSV or .csv.zip exists.
# Does not relaunch existing 100 k v1/v2 CSVs. Default JOBS=1 so this
# does not collide with a 4-core figure-dense VIPM campaign.
#
#   ./scripts/run_i2_dense.sh --write
#   JOBS=1 ./scripts/run_i2_dense.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--write" ]]; then
  python3 scripts/write_v2_configs.py --dense-ext --write --matrix
  exit 0
fi

JOBS="${JOBS:-1}"
python3 scripts/write_v2_configs.py --dense-ext --write --matrix

mapfile -t CASES < <(python3 scripts/write_v2_configs.py --dense-ext --list)
if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No I2 dense extraction configs" >&2
  exit 1
fi

mkdir -p output output/v2 plots
LOG="output/v2/run_i2_dense.log"
echo "=== I2 dense ext start $(date -u +'%Y-%m-%dT%H:%M:%SZ') jobs=${JOBS} n=${#CASES[@]} ===" | tee -a "$LOG"

printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" ]] && { [[ -s "${csv}" ]] || [[ -s "${csv}.zip" ]] || [[ -s "${csv}.gz" ]]; }; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  echo "RUN $cfg"
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

echo "=== I2 dense ext finished $(date -u +'%Y-%m-%dT%H:%M:%SZ') ===" | tee -a "$LOG"
python3 scripts/evaluate_v2.py --dense-ext | tee -a "$LOG"
python3 scripts/csv_archive.py | tee -a "$LOG"
python3 scripts/invert_imode.py | tee -a "$LOG"
