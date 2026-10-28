# Pi-only speed experiment and validation gates

For the subsequent staged/native experiments and current measured limits, see
[PI5_SPEED_FOLLOWUP.md](PI5_SPEED_FOLLOWUP.md). This document retains the v7 results.

The target is a correct identification within 2 seconds on the Raspberry Pi 5,
without reducing accuracy. `FastCCDemo-v6` remains the deployed default.
`FastCCIndexed-v7-experimental` is explicitly opt-in and is not approved for demo
deployment. It moves candidate extraction/index construction into enrollment and
uses a smaller query search. This changes recognition behavior, not just runtime.

## Preventing overfitting

- The existing 80 images (40 per camera, two people) are development data. All 224
  repeated train/query splits are regression checks, not 224 independent tests.
- Keep each device separate, every image in the denominator, and the original
  five enrollment/five query assignments. Never enroll a query image.
- No identity-specific thresholds, sample-ID branches, manual ROI patches for
  particular failures, or deletion of difficult images.
- Reserve the other four people (`syr`, `kss`, `xyt`, `cyw-real`), eight hands and
  80 old-camera images, until the candidate passes development accuracy and speed
  gates. Their archive hashes are recorded in the local reservation manifest.
- Freeze code and parameters before evaluating that cohort once. If its results
  inform a subsequent change, it becomes development data and a fresh holdout is
  required. Even a pass only establishes held-out identities from old-camera
  bursts; it does not establish cross-session or new-camera generalization.
- A fresh new-camera session is still needed before claiming live-demo accuracy.

## Measurement

Use `tools/replay_demo_manifest.py` with original images and an isolated runtime
on the Pi. This exercises the actual HTTP endpoints, localization, matching,
storage, and simulated payment/cancel/replay protections. Camera acquisition is
replayed; live capture and preview contention remain unmeasured.

Report every query, including errors, median/p95/maximum HTTP time, first-query
time, total correct, and correct-within-2-seconds. Fast failures are not successful
identifications. Enrollment/index build time and resident memory are separate
costs, not hidden as free preprocessing. Desktop/cached timings cannot establish
the Pi latency target. The supervised demo ranks enrolled identities; these tests
do not calibrate rejection of unknown people.

## Experiments retained

`fastcc_accelerated.py` replaces numerical kernels while retaining all original
shifts and overlap denominators. Random, uniform, ramp and shifted-code tests
compare the reference implementation. The existing 80-image preparation audit
and all 3,120 directed same-device non-self pair comparisons have no differences.
This is numerical regression evidence, not a universal floating-point proof.

The indexed matcher includes normal and wider query context plus the existing
registered fallback. Its reduced candidate search has already lost two matches
on development splits where v6's equivalent v5 reference scored 20/20. It has
therefore failed the accuracy gate, regardless of its eventual latency.

Completed fixed-split audit: new camera 110/112 splits at 20/20 and two at 19/20;
old camera all 112 splits at 20/20. Do not pool these correlated query repetitions
into a claim about independent recognition accuracy.

Actual Pi new-camera HTTP replay (OpenCV 4 / ONNX 4 threads): 20/20 correct on
the original split, median 2.879 s, p95 3.369 s, maximum 3.513 s, first query
3.147 s. Only 3/20 were both correct and within 2 seconds. Five-image enrollment
median is 41.541 s and process peak RSS is 2,196,094,976 bytes. Both the speed
and accuracy gates remain unmet. Four simulated payments and cancellation/replay
protections passed. Original images remain byte-identical.

The corresponding old-camera Pi HTTP replay was 20/20 correct: median 1.418 s,
p95 2.646 s, maximum 2.896 s, first query 1.441 s; 16/20 were both correct and
within 2 seconds. Five-image enrollment median was 19.043 s, peak RSS
1,266,434,048 bytes. All four simulated payments and replay/cancellation checks
passed. This also does not establish a 2-second upper bound.

A separate new-camera query-only replay reused the isolated enrollment database
with OpenCV 2 / ONNX 4 threads: 20/20 correct, median 3.259 s, p95 3.856 s,
maximum 4.407 s, and 3/20 correct within 2 seconds. Startup/index loading took
6.741 s separately. Reducing OpenCV threads did not improve this measurement;
it is not selected as a speed fix.

Regression suite: 147 passed, two skipped; the pre-existing obsolete
`tests/test_existing_pipeline.py` import is explicitly excluded. Node demo UI
interaction tests pass. Windows skips do not replace actual Pi ONNX execution.

An initial Pi HTTP attempt failed all queries due to invoking a pose extractor
through a subclass with a different feature format. This is retained as a failed
run; a dedicated pose extractor and regression test fix the integration error.
The replay reporter now saves failure counts instead of crashing on missing
timing fields. None of this alters the stable production service.

Local evidence is under `runtime/pi5-under2-20261028/`: `heldout-reservation.json`,
`kernel-parity/`, `frozen-v2-all-splits/`, and the Pi HTTP artifacts. These contain
private biometric development data and are deliberately not committed.
