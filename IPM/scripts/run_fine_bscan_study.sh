#!/usr/bin/env bash
# E-mode B scan 0–200 G step 5 G, plus injection-σ=10 mm repeats.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py --fine-bscan

mapfile -t CASES < <(
  {
    find configs/csns_rcs_ipm/bscan5 -name '*.xml'
    find configs/csns_rcs_ipm/sig10 -name '*.xml'
    find configs/csns_rcs_ipm/bscan -name '*sig10*.xml'
  } | sort -u
)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No fine-scan / sig10 configs found" >&2
  exit 1
fi

mkdir -p output output/bscan output/bscan5 plots

echo "Running ${#CASES[@]} configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" ]] && { [[ -s "${csv}" ]] || [[ -s "${csv}.zip" ]] || [[ -s "${csv}.gz" ]]; }; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

python scripts/evaluate_bscan5.py
python scripts/evaluate_space_charge.py --set sig10
