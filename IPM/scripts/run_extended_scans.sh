#!/usr/bin/env bash
# 250 G e-mode update, ion size scan 3–20 mm, e-mode/ion repeats at 200–500 kW.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py --fine-bscan --extended

mapfile -t CASES < <(
  {
    find configs/csns_rcs_ipm/bscan5 -name '*.xml'
    find configs/csns_rcs_ipm/bscan5_power -name '*.xml'
    find configs/csns_rcs_ipm/ionsize -name '*.xml'
    find configs/csns_rcs_ipm/bscan -name '*b250G*.xml'
    find configs/csns_rcs_ipm/bscan -name '*sig10*b250G*.xml'
  } | sort -u
)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No extended-scan configs found" >&2
  exit 1
fi

mkdir -p output output/bscan output/bscan5 output/bscan5_power output/ionsize plots

echo "Running ${#CASES[@]} configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" && -s "${csv}" ]]; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

python scripts/evaluate_bscan5.py
python scripts/evaluate_bscan.py || true
python scripts/evaluate_extended.py
