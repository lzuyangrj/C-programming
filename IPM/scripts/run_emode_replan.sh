#!/usr/bin/env bash
# Replanned e-mode scans: size × diagnostic B × power, plus 10 mm inj. B×P.
# Does not re-run the closed 0–250 G / 5 G painted/extraction grids.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py --emode-replan
PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" python -c \
  'from generate_csns_configs import link_existing_emode_outputs as L; print(f"reused {L()} existing e-mode CSVs")'

mapfile -t CASES < <(find configs/csns_rcs_ipm/emode -name '*.xml' | sort)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No e-mode replan configs found" >&2
  exit 1
fi

mkdir -p output output/emode plots

echo "Running ${#CASES[@]} e-mode replan configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" && -s "${csv}" ]]; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

python scripts/evaluate_emode.py
