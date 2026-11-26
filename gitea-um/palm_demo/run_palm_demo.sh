#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -x "$APP_DIR/.venv/bin/python" ]]; then
  exec "$APP_DIR/.venv/bin/python" "$APP_DIR/palm_demo.py" "$@"
fi

exec python3 "$APP_DIR/palm_demo.py" "$@"
