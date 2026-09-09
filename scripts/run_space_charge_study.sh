#!/usr/bin/env bash
# Run CSNS RCS IPM space-charge on/off pairs.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python scripts/generate_csns_configs.py

CASES=(
  configs/csns_rcs_ipm/injection_electrons_sc_off.xml
  configs/csns_rcs_ipm/injection_electrons_sc_on.xml
  configs/csns_rcs_ipm/extraction_electrons_sc_off.xml
  configs/csns_rcs_ipm/extraction_electrons_sc_on.xml
  configs/csns_rcs_ipm/injection_ions_sc_off.xml
  configs/csns_rcs_ipm/injection_ions_sc_on.xml
)

mkdir -p output plots
for cfg in "${CASES[@]}"; do
  echo "=== $(basename "$cfg") ==="
  ./scripts/run_sim.sh "$cfg" --console-log-level=warning
done

python scripts/evaluate_space_charge.py
