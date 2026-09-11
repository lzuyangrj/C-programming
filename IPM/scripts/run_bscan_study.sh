#!/usr/bin/env bash
# Guiding-B scan: 0, 50, 100, 200 G; injection/extraction; e-mode and H2+ ion-mode.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py

mapfile -t CASES < <(find configs/csns_rcs_ipm/bscan -name '*.xml' | sort)
if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No B-scan configs in configs/csns_rcs_ipm/bscan" >&2
  exit 1
fi

mkdir -p output/bscan plots
echo "Running ${#CASES[@]} Virtual-IPM configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} ./scripts/run_sim.sh {} --console-log-level=warning

python scripts/evaluate_bscan.py
