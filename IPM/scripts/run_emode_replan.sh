#!/usr/bin/env bash
# Replanned e-mode scans, all with ROUND beams (σ_y = σ_x):
#   A  0–300 G / 5 G B-scans (25×25 inj., 10×10 ext., 10×10 inj. × 100–500 kW)
#   B  σ = 3–20 mm size scans at 0/100/200/300 G and 0.1 T
#   C  cage voltage 5–30 kV on the 10×10 mm injection beam
#   D  beam-offset check on the 10×10 mm beams
# Points whose CSV already exists are skipped.
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
python scripts/generate_csns_configs.py --emode-matrix

# Order: Block C (voltage), Block D (offset), Block A reference beams, then Block B sizes.
mapfile -t CASES < <(
  {
    find configs/csns_rcs_ipm/emode -name '*_v*kv_*.xml' | sort
    find configs/csns_rcs_ipm/emode -name '*_dx*mm_dy*mm_*.xml' | sort
    find configs/csns_rcs_ipm/emode \( -name 'injection_electrons_s25x25mm_*.xml' \
      -o -name 'extraction_electrons_s10x10mm_p*.xml' -o -name 'injection_electrons_s10x10mm_p*.xml' \) | sort
    find configs/csns_rcs_ipm/emode -name '*.xml' | sort
  } | awk '!seen[$0]++'
)

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
