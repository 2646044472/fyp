# RAW-JPEG-GATE capability and kill preflight

## Purpose

This is a feasibility and falsification gate, not a thesis lock. It tests whether the purchased Raspberry Pi 5B and Camera Module 3 can produce a reproducible RAW/JPEG pair and whether a RAW scalar is worth its extra cost for one non-personal printed-marker task.

The first capability probe is available at `code/palm_demo/tools/camera_capability_preflight.sh`. Run it on the Pi after camera bring-up; it records versions, camera enumeration, command help, sample RAW/JPEG outputs, elapsed capture time and file sizes. It does not prove same-exposure pairing or scene truth; those remain manual checks in this protocol.

## Story and bounded claim

A lab curator decides whether to retain or reacquire a printed maintenance indicator after one exposure. The bounded claim is:

> On a declared marker size and light/material cell, a scalar computed from the same-exposure RAW10 frame lowers exact-code false-retain at a fixed retry/storage/latency budget relative to JPEG luma/blur/saturation and decoder confidence.

No claim is made about general RAW quality, camera health, object detection, cross-device transfer, or security/authentication.

## Gate 0: capability

Record software image, kernel, libcamera/rpicam and Picamera2 versions, exact camera revision, lens mode, resolution, frame duration, analogue gain, exposure and white balance controls.

1. Confirm `rpicam-raw` produces documented RAW10 output and record the exact file size for one frame.
2. Confirm `rpicam-still --raw` or the Picamera2 raw stream produces a documented Bayer/DNG representation; record Bayer order, packing, bit depth and black/white levels.
3. Capture a RAW and JPEG from one request or one exposure sequence. Measure inter-frame time; if the two are not same-exposure, the candidate is downgraded to an appendix.
4. Measure unpacking time, JPEG time, bytes written, idle/capture/process power and dropped-frame count over 30 static captures.
5. Verify that fixed exposure/gain/WB can be held across the pair. If 3A changes, log it and do not pool conditions.

**Capability kill:** no stable RAW10/Bayer path, no reproducible pairing, or raw overhead cannot be measured. Stop the thesis candidate and retain only an engineering note.

## Gate 1: minimal paired cells

Use a generated QR/AprilTag payload registry as the independent payload oracle. Use a rigid mount and static target. Collect at least three sessions, 20 captures per cell/session, for:

- clean/high visible light;
- clean/low visible light;
- transparent cover at the same target distance;
- one held-out lamp or cover lot not used for thresholds.

Do not use decoder output as ground truth. Freeze thresholds on the source cells before reading payload equality on held-out cells.

## Policies and controls

- RAW scalar: saturation fraction, linear channel occupancy, and robust SNR proxy computed without a learned model;
- JPEG-only: luma, blur, saturation and decoder confidence;
- combined JPEG quality score;
- fixed single-capture retain;
- fixed two-shot or always-reacquire;
- offline oracle only for reporting the action frontier.

All policies choose `retain`, `unknown` or `reacquire`. Report false-retain, unknown, reacquisition count, bytes, wall time and joules. Use the predeclared loss `10*FR + 1*U + 0.1*J` with latency reported separately; do not tune the loss after seeing results.

## Promotion and kill criteria

Keep the candidate Amber only if all conditions hold:

- RAW is reproducible across sessions;
- the RAW scalar has a held-out confidence interval showing incremental information beyond the best JPEG-only control at the same false-retain target;
- the action frontier improves after RAW bytes, unpacking time and energy are charged;
- the effect repeats in at least two independent sessions and one held-out light/material cell.

Kill or pivot to a negative result if JPEG/decoder confidence, fixed two-shot or always-reacquire ties; if RAW changes exposure/timing; if the effect is unstable; or if the independent payload/condition labels cannot be maintained.

## Expected negative value

A null establishes a finite sufficiency boundary: for this marker family and hardware path, JPEG/decoder evidence is enough and RAW is not worth its cost. This is not evidence that RAW is useless in other tasks.

## Open gaps

- [GAP] Purchased camera revision and actual RAW10 mode.
- [GAP] Whether a same-request RAW/JPEG pair is exposed by the selected software API.
- [GAP] Exact capture energy and storage rate on the 64-GB card.
- [GAP] Whether transparent-cover and low-light cells remain distinguishable after all controls are fixed.
