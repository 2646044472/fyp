#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="$APP_DIR/vendor/palmprint-recognition-python"
BASELINE_REPO="https://github.com/Li-ChengYan/palmprint-recognition-python.git"
BASELINE_COMMIT="d556f455a6cbdcb4264ec1cd75de2e451cf241b3"

sudo apt update
sudo apt install -y python3-picamera2 python3-numpy python3-scipy python3-pil git

if [[ ! -d "$VENDOR_DIR/.git" ]]; then
  mkdir -p "$(dirname "$VENDOR_DIR")"
  git clone "$BASELINE_REPO" "$VENDOR_DIR"
fi
if ! git -C "$VENDOR_DIR" cat-file -e "$BASELINE_COMMIT^{commit}" 2>/dev/null; then
  git -C "$VENDOR_DIR" fetch --tags origin
fi
git -C "$VENDOR_DIR" checkout --detach "$BASELINE_COMMIT"

chmod +x "$APP_DIR/run_palm_demo.sh"

printf 'Installed Fast-CC baseline at commit %s\n' "$BASELINE_COMMIT"
printf 'Test camera framing first with: rpicam-hello -t 0\n'
printf 'Run the local demo with: ./run_palm_demo.sh --help\n'
