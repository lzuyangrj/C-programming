#!/usr/bin/env bash
# 1 kV / 1 mm figure-dense VIPM add-on. Existing 100 k CSVs and summary
# rows are skipped. Groups: ion-voltage, ion-offset, ion-ext, emode-dx, emode-c3.
#
#   JOBS=4 ./scripts/run_figure_dense.sh ion-voltage
#   JOBS=4 ./scripts/run_figure_dense.sh all
#   JOBS=4 C3_BATCH=80 ./scripts/run_figure_dense.sh emode-c3
# C3 evaluate --delete-c3-csv after every C3_BATCH (default 80) jobs.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GROUP="${1:-all}"
JOBS="${JOBS:-4}"

python3 scripts/figure_dense_scans.py --write >/dev/null

run_group() {
  local g="$1"
  mkdir -p output output/emode output/imode output/v2 plots
  # C3 writes ~27 MB/CSV; evaluate+delete in batches so 960 jobs cannot fill the disk.
  if [[ "$g" == "emode-c3" ]]; then
    local BATCH="${C3_BATCH:-80}"
    while true; do
      mapfile -t CASES < <(python3 scripts/figure_dense_scans.py --list-pending --group "$g")
      echo "=== $g: ${#CASES[@]} pending, JOBS=${JOBS} batch=${BATCH} $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="
      if [[ ${#CASES[@]} -eq 0 ]]; then
        python3 scripts/figure_dense_scans.py --evaluate --group "$g" --delete-c3-csv || true
        echo "=== $g finished $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="
        return 0
      fi
      printf '%s\n' "${CASES[@]:0:${BATCH}}" | xargs -P "${JOBS}" -I{} bash -c '
        cfg="$1"
        csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
        if [[ -n "${csv}" && -s "${csv}" ]]; then
          echo "SKIP (exists) $cfg"
          exit 0
        fi
        ./scripts/run_sim.sh "$cfg" --console-log-level=warning
      ' _ {}
      python3 scripts/figure_dense_scans.py --evaluate --group "$g" --delete-c3-csv
    done
  fi
  mapfile -t CASES < <(python3 scripts/figure_dense_scans.py --list-pending --group "$g")
  echo "=== $g: ${#CASES[@]} pending, JOBS=${JOBS} $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="
  if [[ ${#CASES[@]} -eq 0 ]]; then
    echo "nothing to run for $g"
    python3 scripts/figure_dense_scans.py --evaluate --group "$g" || true
    return 0
  fi
  printf '%s\n' "${CASES[@]}" | xargs -P "${JOBS}" -I{} bash -c '
    cfg="$1"
    csv="$(grep -oE "output/[^<]+" "$cfg" | head -1 || true)"
    if [[ -n "${csv}" && -s "${csv}" ]]; then
      echo "SKIP (exists) $cfg"
      exit 0
    fi
    ./scripts/run_sim.sh "$cfg" --console-log-level=warning
  ' _ {}
  python3 scripts/figure_dense_scans.py --evaluate --group "$g"
  echo "=== $g finished $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="
}

if [[ "$GROUP" == "all" ]]; then
  for g in ion-voltage ion-offset ion-ext emode-dx emode-c3; do
    run_group "$g"
  done
else
  run_group "$GROUP"
fi
