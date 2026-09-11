#!/usr/bin/env bash
# Run a Virtual-IPM configuration from the repository root.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CONFIG="${1:-configs/lhc_6p5tev_electrons/smoke.xml}"
shift || true

if [[ ! -f "$CONFIG" ]]; then
  echo "Config not found: $CONFIG" >&2
  exit 1
fi

if [[ -x "$ROOT/.venv/bin/virtual-ipm" ]]; then
  VIPM="$ROOT/.venv/bin/virtual-ipm"
elif [[ -x "$ROOT/../.venv/bin/virtual-ipm" ]]; then
  VIPM="$ROOT/../.venv/bin/virtual-ipm"
elif command -v virtual-ipm >/dev/null 2>&1; then
  VIPM="$(command -v virtual-ipm)"
else
  echo "virtual-ipm not found. Create a venv and install requirements first:" >&2
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

mkdir -p output output/bscan output/bscan5 output/bscan5_power output/ionsize output/emode output/imode plots
echo "Running: $VIPM $CONFIG $*"
exec "$VIPM" "$CONFIG" "$@"
