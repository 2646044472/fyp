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
