#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEEL_DIR="$APP_DIR/offline_wheels"
VENV_DIR="$APP_DIR/.venv"

if [[ "$(uname -m)" != "aarch64" ]]; then
  echo "Error: this USB package requires 64-bit Raspberry Pi OS (aarch64). Current architecture: $(uname -m)" >&2
  exit 1
fi

PY_MINOR="$(python3 -c 'import sys; print(sys.version_info.minor)')"
if [[ "$PY_MINOR" == "11" ]]; then
  WHEEL_DIR="$APP_DIR/offline_wheels"
  NUMPY_VERSION="2.2.6"
  SCIPY_VERSION="1.16.3"
elif [[ "$PY_MINOR" == "13" && -d "$APP_DIR/offline_wheels/cp313" ]]; then
  WHEEL_DIR="$APP_DIR/offline_wheels/cp313"
  NUMPY_VERSION="2.3.5"
  SCIPY_VERSION="1.17.1"
else
  echo "Error: this USB package supports Python 3.11 or 3.13; current version: 3.$PY_MINOR" >&2
  exit 1
fi

python3 -m venv --system-site-packages "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --no-index --find-links "$WHEEL_DIR" \
  "numpy==$NUMPY_VERSION" "scipy==$SCIPY_VERSION" Pillow==12.2.0

if ! python3 -c 'import picamera2' >/dev/null 2>&1; then
  echo "Warning: Picamera2/libcamera is not installed on the system." >&2
  echo "Connect to the internet once, then run: sudo apt update && sudo apt install -y python3-picamera2" >&2
  echo "The low-level camera components cannot be reliably replaced by pip wheels alone." >&2
else
  echo "System Picamera2/libcamera installation detected."
fi

chmod +x "$APP_DIR/run_palm_demo.sh"

echo "Offline Python dependencies installed. Run: ./run_palm_demo.sh --help"
