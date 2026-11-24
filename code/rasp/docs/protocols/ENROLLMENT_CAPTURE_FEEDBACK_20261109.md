# Enrollment capture failure feedback — 2026-11-09

## Change

The eight-candidate enrollment step now preserves a small stable failure code and shows a matching user-actionable prompt for `NO_HAND`, `ROI_UNSTABLE`, `CAMERA_BUSY`, and `CAMERA_UNAVAILABLE`. Low-level detector and camera exception strings are not shown. Unknown capture failures keep a generic recovery prompt. The same typed error carries the user-facing detail through the single-frame identify response. Only `ROI_UNSTABLE` consumes the 15-event quality-failure budget; no-hand, camera busy, and camera unavailable are retryable wait states and remain bounded by the existing 120-second session timeout.

## Verification

- `tests/test_demo_enrollment_burst.py`: 11 passed on X, including mock cases for no hand, unstable palm geometry, and unavailable camera; each produces a distinct prompt and adds no candidate. Twenty consecutive simulated no-hand attempts remain in `WAIT`, do not consume the quality-failure budget, and schedule a 500 ms retry.
- `node --test tests/test_demo_page.cjs`: passed on X; a new DOM flow check confirms the no-hand prompt is displayed, quality failures stay at `0/15`, the client waits 499 ms without another step request, then resumes automatic capture at 500 ms.
- The project interpreter under `DevWork/environments/projects/fyp-palm-demo` has ONNX Runtime 1.31.0, OpenCV 4.10.0, NumPy 2.5.4, PyTorch 2.15.0+cpu, Pillow 13.0.0, and pytest 9.2.0 installed. The `activate.sh` entrypoint adds DevWork tools to PATH; it does not activate this project interpreter.
- `python -m py_compile demo_flow.py palm_app/debug_ui.py tests/test_demo_enrollment_burst.py`: passed.
- `git diff --check` for the touched flow, tests, and protocol note: passed.

## Limits

These are simulated capture-failure cases. The detector/camera error modes were not physically induced, and this does not validate a real person's capture experience or Raspberry Pi behavior. Existing no-hand readiness gating remains covered by prior X UVC/DOM results; this change adds no new live-camera measurement.
