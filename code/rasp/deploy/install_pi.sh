#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$APP_DIR/vendor/palmprint-recognition-python"
BASELINE_REPO="https://github.com/Li-ChengYan/palmprint-recognition-python.git"
BASELINE_COMMIT="d556f455a6cbdcb4264ec1cd75de2e451cf241b3"

sudo apt update
sudo apt install -y python3-picamera2 python3-numpy python3-scipy python3-pil python3-opencv python3-venv git

if [[ ! -f "$VENDOR_DIR/palmprint/algorithms/registry.py" ]]; then
  mkdir -p "$(dirname "$VENDOR_DIR")"
  git clone "$BASELINE_REPO" "$VENDOR_DIR"
fi
if [[ -d "$VENDOR_DIR/.git" ]]; then
  if ! git -C "$VENDOR_DIR" cat-file -e "$BASELINE_COMMIT^{commit}" 2>/dev/null; then
    git -C "$VENDOR_DIR" fetch --tags origin
  fi
  git -C "$VENDOR_DIR" checkout --detach "$BASELINE_COMMIT"
fi

python3 -m venv --system-site-packages "$APP_DIR/.venv"
if [[ "${1:-}" == "--with-pklnet" ]]; then
  python3 -m venv --system-site-packages "$APP_DIR/.venv-pklnet"
  "$APP_DIR/.venv-pklnet/bin/python" -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r "$APP_DIR/requirements-pklnet.txt"
fi

printf 'Installed Fast-CC baseline at commit %s\n' "$BASELINE_COMMIT"
printf 'Test camera framing first with: rpicam-hello -t 0\n'
printf 'Run the collection UI from the app directory with: .venv/bin/python debug_ui.py --capture-only\n'
