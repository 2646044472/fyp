#!/usr/bin/env bash
set -u

# Collect the minimum evidence needed before evaluating RAW-JPEG-GATE.
# This script does not infer scene truth and does not tune a research policy.

OUT_DIR="${1:-camera-preflight-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT_DIR"

log() {
  printf '%s\n' "$*" | tee -a "$OUT_DIR/manifest.txt"
}

run_capture() {
  local label="$1"
  shift
  local start end rc
  start="$(date +%s%N 2>/dev/null || date +%s000000000)"
  "$@" >"$OUT_DIR/${label}.stdout.txt" 2>"$OUT_DIR/${label}.stderr.txt"
  rc=$?
  end="$(date +%s%N 2>/dev/null || date +%s000000000)"
  log "capture=$label rc=$rc elapsed_ns=$((end - start)) command=$*"
  return 0
}

log "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "host=$(hostname 2>/dev/null || true)"
log "arch=$(uname -m 2>/dev/null || true)"
log "kernel=$(uname -a 2>/dev/null || true)"
log "python=$(python3 --version 2>&1 || true)"
log "picamera2=$(python3 -c 'import picamera2; print(getattr(picamera2, "__version__", "import-ok"))' 2>&1 || true)"
log "rpicam_hello=$(rpicam-hello --version 2>&1 || true)"
log "rpicam_raw=$(rpicam-raw --version 2>&1 || true)"

if command -v rpicam-hello >/dev/null 2>&1; then
  rpicam-hello --list >"$OUT_DIR/cameras.txt" 2>&1 || true
  log "camera_list=$OUT_DIR/cameras.txt"
else
  log "ERROR missing rpicam-hello"
fi

if command -v rpicam-raw >/dev/null 2>&1; then
  rpicam-raw --help >"$OUT_DIR/rpicam-raw-help.txt" 2>&1 || true
  run_capture raw-1 rpicam-raw -t 1000 --frames 1 -o "$OUT_DIR/frame.raw"
else
  log "ERROR missing rpicam-raw"
fi

if command -v rpicam-still >/dev/null 2>&1; then
  rpicam-still --help >"$OUT_DIR/rpicam-still-help.txt" 2>&1 || true
  run_capture jpeg-1 rpicam-still -n -t 1000 --frames 1 -o "$OUT_DIR/frame.jpg"
  if rpicam-still --help 2>&1 | grep -q -- '--raw'; then
    run_capture raw-jpeg-1 rpicam-still -n -t 1000 --frames 1 --raw -o "$OUT_DIR/pair.jpg"
    log "expected_raw_pair=$OUT_DIR/pair.dng"
  else
    log "WARNING rpicam-still does not advertise --raw"
  fi
else
  log "ERROR missing rpicam-still"
fi

find "$OUT_DIR" -maxdepth 1 -type f -printf '%f %s bytes\n' 2>/dev/null \
  | sort >"$OUT_DIR/file-sizes.txt" || true
log "file_sizes=$OUT_DIR/file-sizes.txt"
log "NEXT: inspect stderr/help and verify whether RAW/JPEG files came from one request and one exposure."
log "NEXT: record exposure, analogue gain, frame duration, white balance, Bayer order, packing, black/white levels and dropped frames."
log "NEXT: if pairing or cost cannot be verified, downgrade RAW-JPEG-GATE to an engineering/null appendix."

printf 'Preflight output: %s\n' "$OUT_DIR"
