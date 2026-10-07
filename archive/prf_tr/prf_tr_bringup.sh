#!/usr/bin/env bash
set -euo pipefail

# Capture one logged PRF-TR bring-up episode. This script records evidence for
# the experiment; it does not choose retain/reacquire/review actions.

usage() {
  cat <<'EOF'
Usage:
  prf_tr_bringup.sh \
    --out DIR --session ID --attempt ID --cell CELL \
    --camera ID --camera-label LABEL --illumination STATE \
    [--expected-payload FILE] [--width PX] [--height PX] [--timeout-ms MS]

Required fields:
  --out DIR                 Output directory for one or more episodes.
  --session ID              Physical session/remount identifier.
  --attempt ID              Unique attempt identifier within the session.
  --cell CELL               Preassigned physical fixture condition.
  --camera ID               rpicam camera index, for example 0.
  --camera-label LABEL      Manually verified path label, for example noir_visible.
  --illumination STATE      Logged external illumination state, for example visible_on or ir_on.

Optional fields:
  --expected-payload FILE   One-line expected QR payload. Used only after capture for evaluation.
  --width PX                Requested capture width (default: 1920).
  --height PX               Requested capture height (default: 1080).
  --timeout-ms MS           rpicam-still timeout in milliseconds (default: 1000).

Before use, manually verify the current Camera NoIR v2 mapping with rpicam-hello.
The script never infers the physical cell or camera modality from an image.
EOF
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

OUT_DIR=''
SESSION=''
ATTEMPT=''
CELL=''
CAMERA_ID=''
CAMERA_LABEL=''
ILLUMINATION=''
EXPECTED_FILE=''
WIDTH='1920'
HEIGHT='1080'
TIMEOUT_MS='1000'

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) [[ $# -ge 2 ]] || fail 'missing value for --out'; OUT_DIR="$2"; shift 2 ;;
    --session) [[ $# -ge 2 ]] || fail 'missing value for --session'; SESSION="$2"; shift 2 ;;
    --attempt) [[ $# -ge 2 ]] || fail 'missing value for --attempt'; ATTEMPT="$2"; shift 2 ;;
    --cell) [[ $# -ge 2 ]] || fail 'missing value for --cell'; CELL="$2"; shift 2 ;;
    --camera) [[ $# -ge 2 ]] || fail 'missing value for --camera'; CAMERA_ID="$2"; shift 2 ;;
    --camera-label) [[ $# -ge 2 ]] || fail 'missing value for --camera-label'; CAMERA_LABEL="$2"; shift 2 ;;
    --illumination) [[ $# -ge 2 ]] || fail 'missing value for --illumination'; ILLUMINATION="$2"; shift 2 ;;
    --expected-payload) [[ $# -ge 2 ]] || fail 'missing value for --expected-payload'; EXPECTED_FILE="$2"; shift 2 ;;
    --width) [[ $# -ge 2 ]] || fail 'missing value for --width'; WIDTH="$2"; shift 2 ;;
    --height) [[ $# -ge 2 ]] || fail 'missing value for --height'; HEIGHT="$2"; shift 2 ;;
    --timeout-ms) [[ $# -ge 2 ]] || fail 'missing value for --timeout-ms'; TIMEOUT_MS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "unknown argument: $1" ;;
  esac
done

[[ -n "$OUT_DIR" ]] || fail 'missing required --out value'
[[ -n "$SESSION" ]] || fail 'missing required --session value'
[[ -n "$ATTEMPT" ]] || fail 'missing required --attempt value'
[[ -n "$CELL" ]] || fail 'missing required --cell value'
[[ -n "$CAMERA_ID" ]] || fail 'missing required --camera value'
[[ -n "$CAMERA_LABEL" ]] || fail 'missing required --camera-label value'
[[ -n "$ILLUMINATION" ]] || fail 'missing required --illumination value'

command -v rpicam-still >/dev/null 2>&1 || fail 'rpicam-still is not installed or not on PATH'

if [[ -n "$EXPECTED_FILE" ]]; then
  [[ -r "$EXPECTED_FILE" ]] || fail "expected payload file is not readable: $EXPECTED_FILE"
  EXPECTED_PAYLOAD="$(head -n 1 "$EXPECTED_FILE" | tr -d '\r\n')"
  [[ -n "$EXPECTED_PAYLOAD" ]] || fail "expected payload file is empty: $EXPECTED_FILE"
else
  EXPECTED_PAYLOAD=''
fi

mkdir -p "$OUT_DIR"
MANIFEST="$OUT_DIR/episodes.tsv"

if [[ ! -f "$MANIFEST" ]]; then
  printf '%s\n' 'session_id	attempt_id	physical_cell	camera_id	camera_label	illumination_state	capture_started_utc	capture_command	frame_path	frame_sha256	frame_bytes	capture_elapsed_ms	decoded_payload	decoded_exact	decoder_status' >"$MANIFEST"
fi

CAPTURED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SAFE_ATTEMPT="$(printf '%s' "$ATTEMPT" | tr -cs 'A-Za-z0-9._-' '_')"
FRAME="$OUT_DIR/${SESSION}_${SAFE_ATTEMPT}_${CAMERA_LABEL}.jpg"
STDOUT="$OUT_DIR/${SESSION}_${SAFE_ATTEMPT}_${CAMERA_LABEL}.stdout.txt"
STDERR="$OUT_DIR/${SESSION}_${SAFE_ATTEMPT}_${CAMERA_LABEL}.stderr.txt"
COMMAND=(rpicam-still --camera "$CAMERA_ID" -n -t "$TIMEOUT_MS" --width "$WIDTH" --height "$HEIGHT" -o "$FRAME")

start_ns="$(date +%s%N)"
if ! "${COMMAND[@]}" >"$STDOUT" 2>"$STDERR"; then
  fail "capture failed; inspect $STDERR"
fi
end_ns="$(date +%s%N)"

[[ -s "$FRAME" ]] || fail "capture returned success but no frame was written: $FRAME"
FRAME_SHA256="$(sha256sum "$FRAME" | awk '{print $1}')"
FRAME_BYTES="$(stat -c '%s' "$FRAME")"
ELAPSED_MS="$(( (end_ns - start_ns) / 1000000 ))"
DECODED_PAYLOAD=''
DECODED_EXACT=''
DECODER_STATUS='not_run'

if command -v zbarimg >/dev/null 2>&1; then
  if DECODED_PAYLOAD="$(zbarimg --quiet --raw "$FRAME" 2>/dev/null | head -n 1 | tr -d '\r\n')"; then
    DECODER_STATUS='decoded'
  else
    DECODER_STATUS='no_symbol'
  fi
  if [[ -n "$EXPECTED_PAYLOAD" ]]; then
    if [[ "$DECODED_PAYLOAD" == "$EXPECTED_PAYLOAD" ]]; then
      DECODED_EXACT='true'
    else
      DECODED_EXACT='false'
    fi
  fi
else
  DECODER_STATUS='zbarimg_unavailable'
fi

command_text="$(printf '%q ' "${COMMAND[@]}")"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$SESSION" "$ATTEMPT" "$CELL" "$CAMERA_ID" "$CAMERA_LABEL" "$ILLUMINATION" \
  "$CAPTURED_AT" "$command_text" "$FRAME" "$FRAME_SHA256" "$FRAME_BYTES" "$ELAPSED_MS" \
  "$DECODED_PAYLOAD" "$DECODED_EXACT" "$DECODER_STATUS" >>"$MANIFEST"

printf 'Captured %s\nManifest: %s\n' "$FRAME" "$MANIFEST"
