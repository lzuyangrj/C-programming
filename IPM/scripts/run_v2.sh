#!/usr/bin/env bash
# Execute scan-matrix v2. SKIP if the CSV or .csv.zip already exists. Writes no v1 files.
#   ./scripts/run_v2.sh --matrix     # counts only
#   ./scripts/run_v2.sh --write      # write XMLs, run nothing
#   JOBS=4 ./scripts/run_v2.sh       # write + run missing points (I1→I2→E1→E3→E4→I3)
#   ./scripts/run_v2.sh I1           # one block
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--matrix" ]]; then
  python3 scripts/write_v2_configs.py --matrix
  exit 0
fi
if [[ "${1:-}" == "--write" ]]; then
  python3 scripts/write_v2_configs.py --write --matrix
  exit 0
fi

BLOCK="${1:-}"
JOBS="${JOBS:-4}"
python3 scripts/write_v2_configs.py --write --matrix >/dev/null
python3 scripts/write_v2_configs.py --matrix

mapfile -t CASES < <(python3 scripts/write_v2_configs.py --list)
if [[ -n "${BLOCK}" ]]; then
  mapfile -t CASES < <(printf '%s\n' "${CASES[@]}" | grep -E "/${BLOCK}_|_${BLOCK}_|${BLOCK,}" || true)
  # Filter by block via the matrix CSV slug mapping: keep XMLs whose stem appears in that block.
  mapfile -t CASES < <(python3 - "${BLOCK}" <<'PY'
import csv, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from write_v2_configs import load_points, new_points, order_rows, xml_path
blk = sys.argv[1]
for r in order_rows(new_points(load_points())):
    if r["block"] == blk:
        print(xml_path(r))
PY
)
fi

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No v2 configs to run" >&2
  exit 1
fi

mkdir -p output output/v2 plots
LOG="output/v2/run.log"
echo "=== v2 start $(date -u +'%Y-%m-%dT%H:%M:%SZ') block=${BLOCK:-all} jobs=${JOBS} n=${#CASES[@]} ===" | tee -a "$LOG"

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

echo "=== v2 finished $(date -u +'%Y-%m-%dT%H:%M:%SZ') ===" | tee -a "$LOG"
python3 scripts/evaluate_v2.py | tee -a "$LOG"
