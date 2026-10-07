Decision investigated

Can the current palmprint plus palm-vein extraction pipeline be considered runnable with existing assets?

## Claim under test

[E] The Pi at `10.12.194.1` serves changing camera frames, `/roi.jpg`, and `/api/users` on port 8080. [E] Host tests pass: 32 pytest tests plus six synthetic ROI geometry tests. [KILL] This does not establish one end-to-end pipeline: dynamic ROI is isolated in a 1:1 debug UI, the payment UI uses another ROI implementation, and no palm-vein feature or fusion code exists.

## Prioritized failure matrix

| Priority | Blocker | Evidence | Required falsification |
| --- | --- | --- | --- |
| P0 | `no_hand` conflates failures | `palm_roi.py:344-349,450-458,500-503` hides low score, invalid geometry, and absent candidates behind the same status. | Log raw logit, sigmoid score, decoded keypoints, geometry result, and one terminal reason per inference. |
| P0 | 80-pixel span gate | Geometry defaults to `min_span_px=80` on the 320x240 detector input. A visually obvious but moderately sized palm can be rejected. | Record MCP span before rejection. Score above 0.42 plus span below 80 identifies this blocker. |
| P0 | NoIR domain mismatch | The visible-image detector receives NoIR imagery without exposure, gain, AWB, channel statistics, or physical IR state logs. | Compare matched visible, NoIR IR-off, and NoIR IR-on frames with frozen geometry and detector logits. |
| P0 | Model/decode mismatch is untested | Code assumes ONNX output ordering and generated anchors. Tests do not run the detector ONNX; the local palm-detector model is absent. | Record deployed model SHA-256, OpenCV version, output names/shapes, and a known-positive decode. |
| P0 | Dynamic ROI is disconnected | `debug_ui.py` uses `HandLandmarkTracker` for 1:1; `palm_payment_ui.py` uses background-difference `AutomaticPalmROI`. | Use the same fresh dynamic ROI for enrolment, 1:N search, and payment. |
| P0 | No palm-vein implementation | No vessel enhancement, vein descriptor, NIR matcher, or fusion module was found. `noir-ir` is metadata only. | Specify and evaluate a separate NIR feature path after the optical gate. |
| P0 | Deployment archive is incomplete | The current zip omits required runtime modules and detector assets; clean import failed with `ModuleNotFoundError: biometric`. | Extract a fresh bundle into an empty directory and pass clean imports and service startup. |
| P1 | Frame/ROI staleness | Detection is asynchronous; the latest frame can be paired with a quad retained for up to 1500 ms without matching frame IDs. | Log capture, detector, ROI, and transaction frame IDs; reject stale or mismatched pairs. |
| P1 | Scheduling instability | Processing and detector submission are throttled around 800 ms with 1500 ms stale expiry. | Collect a 60-second capture/inference/status/ROI-age trace. |
| P1 | Pose refinement is disabled | The service supplies a pose-model path but omits `--refine-pose`. | Record detector-only versus refined mode in the runtime manifest. |
| P1 | Optical profile is not observed | The browser selects `rgb` or `noir-ir`; metadata hard-codes camera 0; illuminator state is not measured. | Bind profile to camera identity and logged physical IR state. |
| P1 | Pi runtime is unaudited | HTTP works, but SSH inspection failed and no status endpoint exposes board, commit, versions, camera, or hashes. | Record board, OS/kernel, Python/OpenCV/Picamera2/libcamera, service command, commit, and hashes. |
| P2 | Tests miss the load-bearing path | Tests cover synthetic geometry and service logic, not real ONNX inference, Pi capture, dynamic 1:N payment, NIR, or fusion. | Add those integration tests after repair. |

## Live-demo evidence

For every detector attempt collect:

1. Frame ID, `SensorTimestamp`, capture time, inference start/end, and ROI age.
2. Camera identity, tuning file, exposure, gain, frame duration, AWB gains, and physical IR state.
3. Detector input hash and per-channel mean, standard deviation, and clipping.
4. Model SHA-256, OpenCV version, output names, and tensor shapes.
5. Top raw logit, sigmoid score, decoded box, and seven keypoints.
6. MCP span and reason: `no_candidate`, `below_threshold`, `decode_invalid`, `span_too_small`, `bad_geometry`, `jump_rejected`, `accepted`, or `stale`.
7. Frame ID used for enrolment or verification.

Run at least 30 attempts per frozen cell across visible, NoIR IR-off, and NoIR IR-on; palm spans `<60`, `60-79`, `80-119`, and `>=120` pixels; upright, +/-45, and +/-90 degrees; left/right palm; centered/edge/clipped; current/plain background.

- Score above 0.42 followed by span below 80 kills the claim that the detector did not see the palm.
- Visible success with matched NoIR failure supports sensor/domain shift.
- Failure on a known-positive image supports model/decode/runtime mismatch.
- Accepted detection followed by UI `no_hand` or another transaction frame supports async/staleness failure.

## Strongest simple baseline

Use one fresh still capture, fixed guide/crop, Fast-CC, a frozen profile-specific threshold, and `MATCH / UNKNOWN / one guided recapture`. Run VIS and NoIR+IR separately. Dynamic ROI must beat this baseline without stale-frame errors. Do not start fusion before both unimodal paths work.

## Acceptance gates

1. **Deployment:** clean bundle imports every module, records model hashes, and starts after reboot without undeclared files.
2. **Detector:** every inference has one reason code; known-positive images decode; no transaction accepts ROI age above 250 ms.
3. **ROI:** detector, ROI, and transaction frame IDs match; zero accepted ROIs on 100 empty frames; at least 95 valid ROIs from 100 in-guide attempts; all failures return `RETRY`.
4. **Palmprint 1:N:** payment uses dynamic ROI; enrolled, unknown, retry, insufficient-balance, and idempotent paths pass; no payment occurs on `UNKNOWN` or `RETRY`; stage p95 times are logged.
5. **NIR apparatus:** camera, wavelength/current/geometry, IR state, exposure/gain/AWB, and timestamps are logged; repeated sessions show stable structure not explained by brightness, blur, exposure, or visible palm texture.
6. **Palm-vein/fusion:** a declared vessel feature separates held-out within-hand from between-hand comparisons and beats intensity/texture controls; fusion beats VIS-only, NIR-only, VIS recapture, fixed two-shot, and simple score sum after latency and energy are charged. Otherwise use `NIR-assisted palmprint`, not `palm-vein`.

## Direct neighbors

- Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111, occupies mobile capture/ROI/quality/template processing.
- Kumar et al., 2017, https://ijaas.iaescore.com/index.php/IJAAS/article/download/9470/7878, occupies a Pi, NIR illumination, ROI, and palm-vein prototype.
- Dhabarde and Kashyap, 2019, https://ijsrd.com/articles/IJSRDV7I40667.pdf, occupies a NoIR/IR/Pi palm-vein apparatus.
- Fan et al., IEEE TSMC 2024, https://doi.org/10.1109/TSMC.2023.3346961, occupies generic palmprint/palm-vein fusion.
- Raspberry Pi camera documentation, https://www.raspberrypi.com/documentation/computers/camera_software.html, and Picamera2 manual revised 2026-06-30, pp. 78-80, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf, define missing capture controls and metadata.

## Evidence and commands inspected

Read `AGENTS.md`, `research/ops/agent-validation.md`, required active files, newest 2026-09-15/13 divergence and validation packets, `minutes/09-13-palm-payment-roadmap-update.md`, `Biometrics/README.md`, relevant `code/palm_demo` files, and archive logs 15, 21, 22, 25, 28, and 29.

Diagnostics included `git status --short`, `rg --files`, `python -m pytest -q`, `python -m unittest -v test_palm_roi.py`, `python -m compileall -q .`, `Test-Connection`, `Test-NetConnection`, HTTP GETs to `/api/users`, `/frame.jpg`, and `/roi.jpg`, clean zip extraction/import, and archive hashing. SSH read-only inspection failed authentication. No code, active state, archive, dataset, model, or runtime template was modified.

The camera/debug subchain is alive, but the unified extraction pipeline is not run through. Diagnose `no_hand`, enforce frame/ROI identity, connect dynamic ROI to 1:N payment, and pass an optical evidence gate before using palm-vein or fusion wording.

## Decision

The current assets do not justify saying the palmprint plus palm-vein extraction pipeline is run through. First make `no_hand` falsifiable, starting with the 80-pixel span gate versus raw detector score; then repair frame/ROI identity and connect dynamic ROI to 1:N payment. Keep fixed-guide Fast-CC as the recovery baseline and keep palm-vein/fusion behind the optical gate.

HOLD
