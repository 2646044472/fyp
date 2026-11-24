# Server-side enrollment capture readiness gate

Date: 2026-11-09 (X).

## Change

The browser already disables enrollment until the preview reports a fresh ROI state and sufficient consecutive READY frames. The enrollment API now enforces the same condition before requesting a high-resolution frame:

- camera down/status error → retryable `WAIT/CAMERA_UNAVAILABLE`;
- fresh, explicit `NO_HAND` → pause as `NO_HAND`, preserve the candidate pool, and let the browser resume or cancel;
- stale ROI state → retryable `WAIT/CAPTURE_TIMEOUT`;
- fresh but non-READY or below the required READY-frame count → retryable `WAIT/ROI_NOT_READY`;
- only fresh READY with the frame count at or above the required count can proceed to capture.

Pre-capture waits do not add quality failures or candidates. Existing per-candidate sharpness, contrast, duplicate suppression, and eight-candidate selection remain unchanged. Identification does not use this enrollment gate.

## Verification

- `tests/test_pklnet_no_hand_normalization.py` plus `tests/test_demo_enrollment_burst.py`: **34 passed**.
- `py_compile` for `demo_flow.py`, `palm_app/debug_ui.py`, and `tests/test_pklnet_no_hand_normalization.py`: passed.
- Targeted `git diff --check`: passed.
- Actual X UVC API smoke at 640×360, with no hand present: `/` returned HTTP 200; fresh status was `camera_ready=true`, `roi_status_fresh=true`, `NO_HAND`, `0/5`; `/frame.jpg` returned JPEG in memory; enrollment start → step returned `NO_HAND`, `quality_failures=0`, `candidate_pool_count=0`; cancel returned `CANCELLED`. The temporary runtime contained only its empty payment database; no template directory was created. The project runtime and image files were not written.

The mock state matrix also confirms camera-down, stale, tracking, and insufficient-frame states skip high-resolution capture and do not consume the failure budget; fresh READY at threshold passes the gate.

## Limitations

Camera status and the subsequent high-resolution capture are not atomic. If the hand leaves between those operations, the captured still can differ from the preview state; per-frame ID revalidation is a separate follow-up. The camera was empty, so this does not validate real-hand READY capture, photo selection, recognition, or browser resume after a hand is shown. It is not a Pi test.

## Browser verification addendum

After the server-gate API smoke, the same temporary-runtime X UVC app was opened in Chrome at `http://127.0.0.1:8765/demo`. The page showed `NO_HAND (0/5)` and the enrollment action was disabled. After filling the user/name fields and selecting a hand, the action remained disabled. No enrollment request was sent from the browser; the temporary app was closed afterward. This verifies the no-hand browser gate, not real-hand READY/resume behavior.

## Identification no-hand finding and fix

A follow-up single-frame check found that direct `capture_demo_feature(enrollment=False)` on a real fresh NO_HAND scene could still return a feature candidate from a low-quality background crop (contrast 0.453, sharpness 0.049). This was a feature extraction observation, not a demonstrated gallery match or false accept. The demo's `identify` callback now requires the same fresh READY frame gate as enrollment. Direct calls used by offline evaluation scripts keep their prior behavior by default.

A real X UVC `POST /api/demo/identify` smoke with an empty scene returned HTTP 200 with `status=RETRY`, `reason=NO_HAND`, and zero high-resolution capture calls. No pending identity token or template directory was created; only the temporary payment database existed. The targeted Python suite then reported **38 passed**. This verifies the no-hand API boundary, not recognition accuracy with an enrolled gallery or behavior with live participants or on the Pi.

## READY auto-resume and production callback regression check

To reduce handling during continuous enrollment, the browser resumes the same buffered enrollment session automatically after a fresh poll observes a non-READY state followed by camera-ready, fresh ROI, and the required consecutive READY frames. Requiring that state transition prevents a preview/high-resolution capture mismatch from looping repeated NO_HAND attempts while preview remains READY. Cancel and manual resume remain available. The resume action uses the same busy guard, so repeated polls cannot launch parallel step loops.

Regression tests now instantiate the real `App` with an isolated temporary runtime, force the live camera status to `NO_HAND`, and make `Gallery.identify` raise if scoring is entered. `/api` flow returns `RETRY/NO_HAND` with exactly one status read and zero high-resolution captures, while gallery scoring is never called. Page tests cover auto-resume after a non-READY→READY transition, suppress auto-loop when the high-resolution capture reports NO_HAND while preview remains READY, and retain manual resume. Validation: **39 Python tests passed** across `test_pklnet_no_hand_normalization.py` and `test_demo_enrollment_burst.py`; `tests/test_demo_page.cjs` interaction checks passed; Python compilation and `git diff --check` passed. These UI transitions are tested in the page harness only; live hardware still has no hand in view, so READY resume, real hand capture, and Pi behavior remain unverified.
