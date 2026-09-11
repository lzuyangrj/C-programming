#!/usr/bin/env bash
# Ion-mode parameter-scan matrix, parallel to the e-mode replan:
#   B fields are only 0, 200, and 1000 G (no B-scan grid).
#   A  three ref. beams (25×25 inj., 10×10 ext., 10×10 inj.) × 100–500 kW × 3 spp
#   B  σ = 3–20 mm size scans × 3 species
#   C  cage voltage 5–30 kV on the 10×10 mm injection beam × 3 species
#   D  beam-offset check on the 10×10 mm beams × 3 species
# All beams are ROUND (σ_y = σ_x). Points whose CSV already exists are skipped.
#
#   ./scripts/run_imode_replan.sh --matrix   # show the matrix only, run nothing
#   JOBS=4 ./scripts/run_imode_replan.sh     # run all missing points
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--matrix" ]]; then
  python3 scripts/generate_csns_configs.py --imode-matrix
  exit 0
fi

JOBS="${JOBS:-4}"
python3 scripts/generate_csns_configs.py --imode-replan >/dev/null
python3 scripts/generate_csns_configs.py --imode-matrix

mapfile -t CASES < <(python3 scripts/generate_csns_configs.py --imode-list)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "No ion-mode replan configs found" >&2
  exit 1
fi

mkdir -p output output/imode plots

echo "Running ${#CASES[@]} ion-mode replan configs with ${JOBS} parallel jobs"
printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
  cfg="$1"
  csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
  if [[ -n "${csv}" && -s "${csv}" ]]; then
    echo "SKIP (exists) $cfg"
    exit 0
  fi
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
' _ {}

echo "Ion-mode replan runs finished. Evaluate when an evaluate_imode.py is added."
