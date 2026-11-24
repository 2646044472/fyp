# Strict preview quality gate for the demo (2026-11-09)

## Problem

The automatic capture preflight on `/demo` previously used the diagnostic `quality_status`. Its lower bounds for contrast and sharpness were 0, so a poor preview could be marked READY and fail only during high-resolution capture processing.

## Changes

- Retain the diagnostic gate (minimum contrast and sharpness both 0) for status reporting on debug/diagnostic pages.
- Add a demo-specific gate: require 5 consecutive frames, contrast ≥ 12 and sharpness ≥ 2, retaining the existing ROI freshness and geometric stability checks.
- The `/demo` browser controls and server capture preflight prefer the `demo_quality_*` fields. Test doubles without these fields can still use the legacy fields.
- Show actionable prompts for low sharpness, low contrast and unstable palm regions. If the server is not ready, return WAIT/RETRY before high-resolution capture without counting it against the capture failure budget.
- Calculate quality on the same processed 128×128 grayscale ROI. The thresholds match the existing `pklnet_policy.require_matchable_quality` and `EnrollmentPhotoSelector`. Reusing the measurement domain and current thresholds does not establish usability with real participants.

## Verification

On host X, without a real palmprint input:

- `tests/test_roi_quality.py` and `tests/test_pklnet_no_hand_normalization.py`: 31 passed.
- `node tests/test_demo_page.cjs`: interaction checks passed. When diagnostics report READY but the demo quality gate fails, the control stays disabled, a blur prompt appears and the action never reaches the server.
- Python `py_compile`: passed.

## Limits

No hand was available in front of the camera for a live acceptance test. This round did not tune thresholds under live lighting or blur, test the Pi camera, or measure end-to-end recognition latency. This reversible usability guard is not evidence of improved recognition accuracy.

## Additional no-hand hardware check on X UVC (2026-11-09)

- On X, `/dev/v4l/by-path/pci-0000:00:14.0-usb-0:6:1.0-video-index0` mapped to Integrated Webcam HD. A read-only preview ran at 640×360 for approximately 4 seconds. All 10/10 status samples reported NO_HAND; capture ran at about 30.2–30.3 fps and detection took 24.9–29.5 ms. The script has no enrollment or recognition route and writes no frames.
- The main `/demo` app ran on X with `--camera-backend uvc --roi-mode pklnet --enable-recognition`, listening only on `127.0.0.1`. All ten `/api/status` checks reported a ready camera, a fresh ROI status, NO_HAND for both the diagnostic and strict gates, and 0/5 consecutive ready frames. `GET /demo` returned the new page.
- The isolated instance received 1 empty-scene request: `POST /api/demo/identify`. It returned `RETRY/NO_HAND` with no score or ROI image. The live gate runs before gallery matching; no gallery comparison or identity score was produced. The roughly 0.225ms `gallery` timing measured the gallery-integrity check, not matching. The isolated runtime contained 0 users, accounts and transactions.
- The app's first launch revealed that `.venv-pklnet` lacked `scipy>=1.14`, already declared in the repository's `requirements-dev.txt`. Only that virtual environment was updated, using `uv` to install scipy 1.18.1; the dependency manifest did not change. The isolated runtime at `/tmp/codex-palm-demo-nohand-uvc-v2-20261109` was retained. Both the app and preview service exited normally.
- This establishes only safe blocking for the observed empty scene and local API. It is not a READY enrollment or recognition test with a real participant, a Pi validation or an accuracy result.
