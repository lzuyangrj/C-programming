#!/usr/bin/env bash
# Replanned e-mode scans: 0–300 G / 5 G B-scans (3 reference beams × 100–500 kW)
# plus σ_x = 3–20 mm size scans at 0/100/200/300 G and 0.1 T.
# Existing CSVs with identical parameters are hard-linked and skipped.
#
#   ./scripts/run_emode_replan.sh --matrix   # show the matrix only, run nothing
#   JOBS=4 ./scripts/run_emode_replan.sh     # run all missing points
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--matrix" ]]; then
  python scripts/generate_csns_configs.py --emode-matrix
  exit 0
fi

JOBS="${JOBS:-4}"
python scripts/generate_csns_configs.py --emode-replan >/dev/null
PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" python -c \
  'from generate_csns_configs import link_existing_emode_outputs as L; print(f"reused {L(verbose=False)} existing e-mode CSVs")'
python scripts/generate_csns_configs.py --emode-matrix

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
