# ROI architecture and backend experiments, 2026-10-29

All work is isolated. Production v6, its Python packages, service configuration,
templates and networking remain unchanged. No reserved identities are evaluated.
The updated acceptance target is the entire pipeline within 2.5 seconds on Pi,
including slow queries (the original target was two seconds). None of the results below establishes that target or independent
recognition accuracy. Every original image stays in the screening denominator.

## Fixed smaller localization network: reject

The predeclared 200x150 backbone/segmentation input retains pretrained weights,
upsamples segmentation back to 400x300 and preserves the original keypoint head.
Export checks against PyTorch on two synthetic inputs show maximum coordinate
errors of 0.00631 and 0.00108 pixels. That checks export fidelity, not quality.

Actual development-image geometry passes only 34/40 new and 28/40 old. Overlays
show large shifts into background; median overlap with the existing ROI is
about 0.081. The crop change is not acceptable. Failed enrollment makes the
screen's pose gallery incomplete; zero scored successes in that condition
must not be presented as a standalone classifier accuracy measurement.

No full recognition or Pi latency claim is made for this rejected architecture.

## Fixed lightweight landmark ensemble: reject

The existing palm detector is evaluated at four right-angle rotations, original
and existing gamma-0.6 illumination, and scales 1/0.65 (existing recovery scale).
Select by detector confidence only; keep detector and pose thresholds unchanged.
All biometric texture comes from the original image. No per-image adjustment.

The complete detector-plus-pose-confirmation pipeline succeeds on 7/40 new and
39/40 old. Of the new failures, 32 fail hand-pose confirmation and one fails
palm detection. This is not a claim that palm detection alone succeeds on only
seven images. The previous detector-only fallback control had 22/40 new crops.
The stricter verified pipeline cannot replace the current localizer.

## Precision conversion: separate implementation failures from quality

The [ORT 1.29 release notes](https://github.com/microsoft/onnxruntime/releases/tag/v1.29.0)
describe Arm64 FP16 convolution/GEMM support. ORT 1.31.1 was installed only in
an experiment-specific import directory on Pi, leaving production's 1.28 intact.
No calibration images or retraining were used.

Converting only Conv to FP16 works on all 80 images. Broad mixed conversion
initially fails at runtime in an If/Split function: these are execution failures,
not a measured loss of localization accuracy, and their short elapsed times
are not performance improvements. A minimal standalone AffineGrid model with
an identity transform reproduces the FP16 failure while FP32 succeeds on the
same runtime and input shape. The corrective mixed model retains AffineGrid,
GridSample, normalization, softmax and pooling in FP32. Pooling is retained
because the Pi build lacks the required internal NHWC FP16 AveragePool kernel.

Static-shape folding before conversion removes unnecessary graph control flow.
The converter can duplicate a shared cast output; the exporter removes only
identical casts and rejects conflicting definitions. All exported candidates
must pass a synthetic forward smoke check. These are implementation repairs,
not identity-dependent parameter tuning.

## Pi paired localization measurements

All 80 originals are evaluated by both models in alternating execution order,
four CPU threads, spinning disabled, no concurrent benchmark. Times include
the original-plus-gamma localization procedure, exclude JPEG decoding and model
loading, and include successful first calls. They are **not full HTTP identify
times**. No recognition/rejection performance is claimed from valid geometry.

| Candidate | Geometry baseline/candidate | Baseline median | Candidate median | Candidate P95 | Candidate max |
| --- | --- | ---: | ---: | ---: | ---: |
| Conv-only FP16 | 80/80; 80/80 | 1.160 s | 1.117 s | 1.430 s | 1.916 s |
| Corrected mixed FP16 | 80/80; 80/80 | 1.158 s | 1.284 s | 1.806 s | 2.334 s |
| FP32 OpenCV 5 DNN/Winograd | 80/80; 80/80 | 1.150 s | 1.216 s | 1.588 s | 2.120 s |

Mixed FP16 is slower and changes some ROIs appreciably despite valid geometry.
Conv-only conversion saves about 3.7%, insufficient to justify replacing the
localizer without a complete recognition audit. Neither is integrated.

OpenCV's [Net documentation](https://docs.opencv.org/4.10.0/db/d30/classcv_1_1dnn_1_1Net.html)
describes faster 3x3 convolution with Winograd and small numerical differences.
The existing FP32 model, with only static graph optimization, runs through
OpenCV 5.0.0.93 in another isolated package directory. Outputs are close, but
the measured full localization pipeline is slower, so this backend is rejected.
Its paired baseline also uses OpenCV 5 preprocessing to avoid confounding that
library update with the inference backend comparison.

## Binary feature experiment: ORB rejected as a direct replacement

Default ORB (same 1000-point cap) plus Hamming matching replaces RootSIFT/L2 in
an offline pilot. All saved v5 ROI/view candidates, original image pixels,
ratio/mutual tests, RANSAC checks, overlap checks, FastCC final pixel scores and
best-two enrollment aggregation are retained. No threshold is relaxed.
All 224 unchanged development splits were evaluated. Old images retain 20/20
in every split. New images have nine splits at 19/20; the other 103 are 20/20.
No wrong ranking passed the existing distance <=0.32 and margin >=0.08 gate.
An offline cascade screen (ORB only when confident, otherwise v10) preserves
all development rankings. However, it resolves only 75 of 247 correlated new
image fallback trials and none of 37 old image fallback trials. This is not
independent validation, a false-accept study, or a deployed cascade.

Pi compute-only measurements on the original split, 20 queries per cohort:

| Cohort/pass | Correct ranking | P50 | P95 | Maximum | >2.5 s |
|---|---:|---:|---:|---:|---:|
| New/first |20/20|2.665 s|3.361 s|3.497 s|11/20|
| New/repeat |20/20|2.657 s|3.342 s|3.501 s|11/20|
| Old/first |20/20|0.519 s|0.588 s|0.610 s|0/20|
| Old/repeat |20/20|0.517 s|0.593 s|0.621 s|0/20|

These times include fresh binary descriptor extraction and all gallery scoring.
They EXCLUDE camera capture, upload, queuing, image decode, ROI/candidate inference,
pose-bank extraction and HTTP return. Geometry is cached, never query descriptors
or identities. First pass is not a cold-start end-to-end measurement. New-image
compute alone already exceeds the budget. No complete HTTP trial is claimed.
The extraction refactor reproduces all 3,120 directed distances exactly,
including missing cross-device entries, and the same full split results.

## Paused at user request, 2026-10-29

No candidate is deployed. Production v6 remains active; the last Pi check showed
`throttled=0x0` and no running binary/localizer benchmark process. The local AKAZE
experiment was stopped at feature extraction 78/80, before pair scoring. Its
partial output is not an accuracy result. Reserved holdout remains unevaluated.

Resume evidence (ignored/private):

- ORB full audit: `orb-default-audit/`; exact refactor replay: `orb-refactored-audit/`.
- ORB cascade screen: `orb-default-audit/cascade-screen.json`.
- Pi ORB per-query evidence: `orb-pi-compute.json`; Pi directory
  `/home/fyp5/demo-indexed-v7-20261028/orb-pi-compute/`.
- Portable cached-geometry input: `orb-geometry-bundle/` on both hosts.
- AKAZE: `akaze-cv410-audit.log` and `akaze-cv410-audit/protocol.json`.
  No extracted-feature checkpoint was written, so resume requires a fresh output
  directory and rerunning extraction. Use the isolated Windows `cv410` package
  via PYTHONPATH; base OpenCV 5 lacks AKAZE. Do not reuse the incomplete directory.

No further experiments or tests were started after the pause request. Previously
completed checks: four landmark-coordinate tests and two converter tests passed;
full ORB refactor distance parity passed. Earlier broader suite had 156 passes
and two skips with five obsolete API tests explicitly excluded. AKAZE remains
unverified. Raw biometrics, runtime packages/models and unrelated user changes
are intentionally outside the commit.

## Resumed over USB, 2026-10-29

User resumed work and explicitly excluded live camera acquisition. USB SSH works
at 10.55.0.1 with the pinned host key; Windows DHCP is 10.55.0.27, UDC configured,
usb-gadget activated. Wi-Fi is down. Initial throttled flags are 0x0, temperature
31.8 C. The service is active but waiting for a camera, with no HTTP listener;
this is not a USB failure. No network or production service changes were needed.

The resumed AKAZE audit (`akaze-cv410-resumed-audit/`) completed: every one of
224 fixed splits ranks 20/20 correctly, with no confident wrong rankings.
Default AKAZE uses at most the existing 1000-point cap by response. This is
development regression only, not independent accuracy or application acceptance.
The interrupted first extraction is retained as incomplete evidence. Pi AKAZE
compute timings and USB-powered v10 HTTP replays are separate follow-ups.

The HTTP replay now reports <=2.5-second correct counts and timeout counts, with
optional per-request Pi throttle/temperature sampling outside timed requests.
It explicitly records included/excluded timing stages and separate queue tests.

### Completed USB power and AKAZE results

v10 USB-powered warm replay: new 20/20 correct, 17/20 within 2.5 seconds,
P50 1.618 s, P95 11.174 s, maximum 11.233 s; old 20/20 correct, 18/20 within
2.5 seconds, P50 1.419 s, P95 4.576 s, maximum 4.657 s. First-pass new maximum
11.934 s includes a 4.115 s first request. All request-adjacent throttle samples
are 0x0. Both queue tests pass and simulated transaction counts are unchanged.
These are saved-image HTTP replays, excluding physical capture/external upload.

Full AKAZE compute-only warm P50 is 3.747 s new and 1.477 s old; extraction
alone is 2.687 s and 1.416 s. Complete fresh-enrollment HTTP flows also ran:
new 20/20, P50 7.678 s, P95 8.540 s, maximum 9.842 s; old 20/20, P50 3.066 s,
P95 3.299 s, maximum 4.028 s. Each cohort passed four simulated payments,
duplicate/cancel guards and PalmIR restore API checks. PalmIR used a fixed
manual square: this verifies execution, not anatomical accuracy or enhancement
benefit. Full AKAZE is not a speed replacement for v10.

The candidate has an explicit opt-in name, `FastCCAKAZE-v11-experimental`, with
a distinct numeric template magic. Byte descriptors are losslessly padded in
the existing float32 envelope; SIFT templates cannot be loaded as AKAZE.
The default extractor remains SIFT. An instance-level extractor hook prevents
cross-instance/global changes. Validation with OpenCV 4.10: 163 tests pass,
three dependency skips, excluding five obsolete API tests as before.

Further fixed development controls, all with unchanged scoring and gates:

- Only primary/secondary plus two context views: new minimum 17/20, reject.
- Half-size AKAZE on both query and gallery: six new splits at 19/20, reject.
- Half-size query with full-resolution enrollment: four new splits at 19/20,
  reject. Old splits remain 20/20 for each control. No confident wrong rankings
  were observed, but that is not an independent false-accept estimate.

Private evidence: `usb-power-ready-{new,old}.json`,
`http-akaze-{new,old}-summary.json`, `akaze-pi-compute.json`,
`akaze-context-audit/`, `akaze-half-audit/`, `akaze-asymmetric-audit/`.

Whole-frame AKAZE (context plus two full-frame views, long side capped at 1536)
also has new minimum 17/20 and old 20/20; it does not replace window localization.
The window scheduling control on all 40 new images gives sequential median
2.945 s versus two-worker median 2.993 s. All validity decisions agree, maximum
quad difference 0.004883 pixels. It is not integrated into recognition.

Conv-only static QDQ INT8 is the next isolated localizer pilot. Fixed MinMax
calibration uses the 40 original-split enrollment images, each original and
existing gamma transform; no original-split query or reserved holdout input.
It is not training, but calibration means the repeated development splits
cannot be called independent validation. Initial export with ORT's intermediate
output cap failed because that version clears samples without merging ranges;
the corrected exporter retains all reduced calibration statistics.
The corrected model passes geometry on 80/80 images, with zero extraction
errors. Pose-only screen: new 34/40 ranking correct, old 40/40. These are not
full recognition results. Pi paired latency and full-template split regression
must finish before any adoption decision. Evidence: `int8-conv-fixed/`,
`int8-screen/`, `int8-templates/`, `int8-full-splits/`.

The completed paired Pi INT8 localization benchmark has baseline/candidate
P50 1.157/0.822 s, P95 1.486/0.987 s, maximum 2.087/1.331 s, both 80/80 valid.
This is about 29% lower localization median, not full recognition latency.
All 80 complete templates were rebuilt successfully. The uncached split audit
was deliberately stopped with its partial results retained, then restarted
as `int8-cached-splits/`. Its optional cache reuses only deterministic exhaustive
query/gallery scores across offline splits; runtime queries never use it.
The first 140 overlapping query results agree exactly in scores, decisions and
routes with the uncached audit. More complete comparison remains possible from
the saved partial results. Audit timings with this option are not latency claims.

Latest regression suite with OpenCV 4.10: 164 passed, three dependency skips;
five obsolete API tests explicitly excluded. Parallel-window tests also verify
order preservation and propagation of model failures. Application replay tools
can now select an explicit isolated localizer; ready-query replays verify and
reuse that exact model hash instead of silently falling back to the default.

### INT8 rejected by actual Pi recognition

New-image actual Pi HTTP replay identifies 19/20 correctly: one query is
misidentified as a different enrolled user at the exhaustive fallback stage.
P50 is 1.332 s, P95 10.234 s, maximum 10.685 s; only 14/20 are correct within
2.5 seconds. This is a wrong accept, not a timeout or a mere ranking ambiguity.
The script's final correctness assertion fails, so the chained old-image HTTP
replay does not run. The standalone paired localization test still covered all
80 images; it must not be mistaken for 80 successful identifications.

The full development audit was stopped after 45 of 224 cases because this
candidate had already failed acceptance. Two completed new-camera splits
(`new_random_2026102807` and `new_random_2026102808`) are 19/20, independently
confirming a regression. No complete 224-split success is claimed. Preserve
`int8-rejection.json`, `int8-cached-splits/results.json`, and
`http-int8-new-summary.json`. No thresholds were loosened and no candidate was
deployed to production.

### Dominant convolution microbenchmark: no hybrid backend integration

Both large segmentation Conv+ReLU pairs have input shape 1x224x100x75 and
224x224x3x3 weights. With unchanged FP32 weights on Pi, ONNX Runtime is about
68 ms per pair versus OpenCV Winograd about 103 ms, including input binding.
These are synthetic operator timings, not ROI or end-to-end timings. The
partial backend replacement is rejected before splitting the full graph.

An additional requested CPU-FP16 target was ignored by OpenCV 5's graph engine;
the resulting numbers are FP32 fallback, not FP16 performance evidence.
Production OpenCV 4.10 advertises CPU only as well. The tool now rejects an
unadvertised FP16 target before collecting timings. No supported FP16 speed
claim or deployment results from this check. Logs and raw JSON remain private
under `large-convs*` for traceability.

## Evidence and tooling

Private evidence stays under `runtime/pi5-under2-20261028/`: `lowres-screen/`,
`landmark-ensemble-screen/`, `conv16-screen/`, `conv16-pi-localizer.json`,
`mixed16-pool32-fixed-screen/`, `mixed16-pool32-pi-localizer.json`,
`dnn-pi-localizer.json`, and conversion logs. Model files, overlays and biometric
data are not committed. Exporters, the all-image screen, the paired localization
benchmark, and the binary-feature audit are reproducible tools under `tools/`.

The current 224 splits reuse 80 development images. Even passing all of them
does not establish accuracy for new people, new camera sessions, or unknown
users. Freeze an acceptable candidate before using independent validation.
