#!/usr/bin/env bash
# Wait for a CSI/libcamera camera before starting the collection UI.
set -euo pipefail
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"
echo 'Waiting for a libcamera camera; power off before changing CSI cables.'
until "$APP_DIR/.venv/bin/python" -c 'from picamera2 import Picamera2; raise SystemExit(0 if Picamera2.global_camera_info() else 1)'; do
  sleep 10
done
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/debug_ui.py" --host 0.0.0.0 --port 8080 --capture-only --camera "${PALM_CAMERA_INDEX:-0}" --width "${PALM_PREVIEW_WIDTH:-640}" --height "${PALM_PREVIEW_HEIGHT:-480}" "$@"
