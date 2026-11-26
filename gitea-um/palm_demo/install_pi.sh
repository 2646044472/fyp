#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="$APP_DIR/vendor/palmprint-recognition-python"
BASELINE_REPO="https://github.com/Li-ChengYan/palmprint-recognition-python.git"
BASELINE_COMMIT="d556f455a6cbdcb4264ec1cd75de2e451cf241b3"

sudo apt update
sudo apt install -y python3-picamera2 python3-numpy python3-scipy python3-pil python3-venv git wget

VENV_DIR="$APP_DIR/.venv"
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv --system-site-packages "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$APP_DIR/requirements-pi.txt"

MODEL_DIR="$APP_DIR/models"
MODEL_PATH="$MODEL_DIR/palm_detection_mediapipe_2023feb.onnx"
HAND_POSE_MODEL_PATH="$MODEL_DIR/handpose_estimation_mediapipe_2023feb.onnx"
mkdir -p "$MODEL_DIR"
if [[ ! -s "$MODEL_PATH" ]]; then
  wget -q --show-progress \
    'https://huggingface.co/opencv/palm_detection_mediapipe/resolve/main/palm_detection_mediapipe_2023feb.onnx?download=true' \
    -O "$MODEL_PATH"
fi
if [[ ! -s "$HAND_POSE_MODEL_PATH" ]]; then
  wget -q --show-progress \
    'https://github.com/opencv/opencv_zoo/raw/main/models/handpose_estimation_mediapipe/handpose_estimation_mediapipe_2023feb.onnx' \
    -O "$HAND_POSE_MODEL_PATH"
fi

if [[ ! -d "$VENDOR_DIR/.git" ]]; then
  mkdir -p "$(dirname "$VENDOR_DIR")"
  git clone "$BASELINE_REPO" "$VENDOR_DIR"
fi
if ! git -C "$VENDOR_DIR" cat-file -e "$BASELINE_COMMIT^{commit}" 2>/dev/null; then
  git -C "$VENDOR_DIR" fetch --tags origin
fi
git -C "$VENDOR_DIR" checkout --detach "$BASELINE_COMMIT"

chmod +x "$APP_DIR/run_palm_demo.sh"

"$VENV_DIR/bin/python" - <<'PY'
import cv2
print(f"OpenCV DNN available: {cv2.__version__}")
PY

printf 'Installed Fast-CC baseline at commit %s\n' "$BASELINE_COMMIT"
printf 'Installed palm detector at %s\n' "$MODEL_PATH"
printf 'Installed 21-point hand pose model at %s\n' "$HAND_POSE_MODEL_PATH"
printf 'Test camera framing first with: rpicam-hello -t 0\n'
printf 'Run the local demo with: %s --roi-mode dynamic --help\n' "$VENV_DIR/bin/python"
