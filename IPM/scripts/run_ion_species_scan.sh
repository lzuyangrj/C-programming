#!/usr/bin/env bash
# Continue ion-mode size/power scan for H2O+ and N2+ (H2+ CSVs already exist).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py --extended

mapfile -t CASES < <(
  find configs/csns_rcs_ipm/ionsize \( -name '*h2o_ions*.xml' -o -name '*n2_ions*.xml' \) \
    | sort -u
)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No H2O+/N2+ ion-size configs found" >&2
  exit 1
fi

mkdir -p output/ionsize plots
echo "Running ${#CASES[@]} H2O+/N2+ ion-size configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" ]] && { [[ -s "${csv}" ]] || [[ -s "${csv}.zip" ]] || [[ -s "${csv}.gz" ]]; }; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

python scripts/evaluate_extended.py
