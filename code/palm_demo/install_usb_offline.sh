#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEEL_DIR="$APP_DIR/offline_wheels"
VENV_DIR="$APP_DIR/.venv"

if [[ "$(uname -m)" != "aarch64" ]]; then
  echo "错误：这个 USB 包的二进制依赖是 Raspberry Pi OS 64 位（aarch64）。当前架构：$(uname -m)" >&2
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
  echo "错误：USB 包支持 Python 3.11 或 3.13；当前版本：3.$PY_MINOR" >&2
  exit 1
fi

python3 -m venv --system-site-packages "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --no-index --find-links "$WHEEL_DIR" \
  "numpy==$NUMPY_VERSION" "scipy==$SCIPY_VERSION" Pillow==12.2.0

if ! python3 -c 'import picamera2' >/dev/null 2>&1; then
  echo "警告：系统还没有 Picamera2/libcamera。" >&2
  echo "联网一次后执行：sudo apt update && sudo apt install -y python3-picamera2" >&2
  echo "底层相机组件不能可靠地只靠 pip wheel 替代。" >&2
else
  echo "已检测到系统 Picamera2/libcamera。"
fi

chmod +x "$APP_DIR/run_palm_demo.sh"

echo "离线 Python 依赖安装完成。运行：./run_palm_demo.sh --help"
