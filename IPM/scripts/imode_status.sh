#!/usr/bin/env bash
# Report ion-mode replan progress (CSV count vs planned matrix).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET=2070
CSV_DIR="output/imode"
mkdir -p "$CSV_DIR"

count_csvs() {
  find "$CSV_DIR" -maxdepth 1 -name 'csns_*.csv' -size +0 2>/dev/null | wc -l | tr -d ' '
}

DONE="$(count_csvs)"
PCT=$(( DONE * 100 / TARGET ))
REMAIN=$(( TARGET - DONE ))

echo "=== Ion-mode replan status $(date -u +'%Y-%m-%d %H:%M:%S UTC') ==="
echo "CSV files: ${DONE} / ${TARGET} (${PCT}%; ${REMAIN} remaining)"

if tmux -f /exec-daemon/tmux.portal.conf has-session -t imode-replan 2>/dev/null; then
  echo "Runner: tmux session 'imode-replan' ACTIVE"
  tmux -f /exec-daemon/tmux.portal.conf capture-pane -t imode-replan -p | tail -8
else
  echo "Runner: tmux session 'imode-replan' not running"
fi

if [[ -f output/imode/run.log ]]; then
  echo "--- tail run.log ---"
  tail -5 output/imode/run.log
fi

python3 scripts/generate_csns_configs.py --imode-matrix 2>/dev/null | tail -12

if [[ "$DONE" -ge "$TARGET" ]]; then
  echo "STATUS: COMPLETE"
  exit 0
fi
echo "STATUS: RUNNING"
