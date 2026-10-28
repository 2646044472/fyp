# Palm camera demo

Local Raspberry Pi palmprint enrollment and 1:1 verification. For connection,
installation and hardware precautions, see [SETUP](docs/SETUP.md).
Commands below run from `code/palm_demo` on Windows or `~/palm_demo` on the Pi.

Pi 5 deployment verified with historical replay (2026-10-28): new/old cameras
both 20/20, including enrollment and isolated simulated payment/cancel checks.
Identification median is 14.46 s / 5.59 s; this is a supervised snapshot demo.
The installed Pi service uses the optional `deploy/demo-v6.conf` override and
waits for a camera. Live camera/preview latency remains untested. See
[Pi validation and rollback](docs/PI5_DEMO_VALIDATION.md).

Opt-in recognition command:

```sh
python debug_ui.py --enable-recognition --roi-mode pklnet --demo-matcher FastCCDemo-v6 --opencv-threads 4 --pklnet-threads 2
```

V6 retains the guarded v5 scores while separating enrollment-only work, caching
compact gallery data (64 MiB limit), and using two bounded workers. Existing
templates from other algorithm versions require reenrollment; balances remain.
All 80 query templates match serial extraction byte-for-byte apart from the
version marker, and all 3,120 within-device pair distances remain exactly equal.
The original/reverse/ten random/100 extra splits remain 20/20 on each device.
144 regression tests pass, 2 skip; the existing obsolete-module import test is
excluded. These are repeated development images, not independent validation.

Earlier Windows new-camera HTTP replay: 20/20 correct, four enrollments and four
simulated payments; five-frame enrollment median 4.59 s, identification median
4.80 s and p95 6.03 s. Old-camera replay also passes 20/20 with four enrollments
and payments; identification median 2.48 s, p95 2.69 s. Hardware capture and Pi timings are not included. This is
a supervised snapshot demo, not real-time identification. The repository base service remains capture-only/DoN; the installed Pi uses
the v6 drop-in described above.
See [ROI pipeline](docs/ROI_PIPELINE.md),
`runtime/roi-palmir-20261028/single-device/report-v6.html` for final timing/evidence,
and `report-v5.html` in the same directory for actual per-template scoring quads.

The new overlap guard removes spatially detached candidates, including the two
wall candidates in the inspected photo. It does not replace the localizer or
prove every retained crop contains a palm; the small anchor can still be wrong.

Current deployment (2026-10-28): `pklnet-illumination-consistent-v5`, with
original/brightened localization consistency and original-pixel ROI crops.
Pi new-camera DoN is **14/20**, FastCC **15/20**, geometry 40/40 and enrollment
4/4; local DoN is 15/20, so do not substitute it for the Pi result. Old-camera
local replay remains 20/20. PalmIR-style restoration adds no correct queries.
See `runtime/roi-palmir-20261028/report.html` for failed trials, synthetic stress,
backend pixel sensitivity and verified deployment/backup evidence.

The 2026-10-27 Pi 5 replay verified the four locally available October 12–13
capture archives (40 images): four five-image enrollments, all 20 held-out
identifications, and four explicitly confirmed simulated payments. The deployed
October 27 `pklnet-heatmap-aspect-v4` repaired four geometric failures in the new-camera
development batch: 40/40 geometry passes, 4/4 enrollments and 13/20 DoN queries
(previous guarded v3: 36/40, 2/4 and 10/20). Seven queries remain incorrect.
`tools/replay_pi_pipeline.py`
reproduces the real HTTP workflow with file input at the camera boundary and
isolated stores. Connection repairs, power observations and reproduction steps
are in [SETUP](docs/SETUP.md#pi-5-connection-repair-and-replay-verification-2026-10-27).

## Architecture

Camera → palm ROI → quality gate → 128×128 normalized grayscale → features →
enrolled templates → distance and threshold decision.

| Entry | ROI | Matcher |
| --- | --- | --- |
| `debug_ui.py` / Pi service (default) | None: original full-resolution collection | None |
| Optional recognition debug mode | PKLNet keypoints and native crop | DoN verification / DoN demo |
| Offline capture benchmark | Same PKLNet extractor and normalization | All 14 registered matchers |

The service defaults to `--capture-only`: no detector, ROI worker or matcher is
loaded. The root page and `/collect` show the full-resolution collection UI.
PKLNet remains available for deferred extraction. Use `make_deploy_bundle.ps1
-IncludePKLNet` to include its weights, and explicitly pass `--enable-recognition`
with `--roi-mode pklnet` to enter the optional recognition debug mode.
The engineering guard rejects keypoint gaps below 10% of the shorter source-image
side and out-of-bounds crops. It detects collapsed predictions, not all misplaced
keypoints. On the connected Pi 4, CPU extraction took about 4.2 seconds per preview
and 4.5 seconds per full still. Preview display continues independently; the five
stable inference frames require about 20–25 seconds. PKLNet results have an 8-second
age budget and capture waits up to 12 seconds for the next processed frame.
The same-stand
demo does not establish liveness, anti-spoofing or cross-device accuracy.

## Use

### Local PalmIR-style restoration on Pi 5

Open `/palmir` (linked from the collection page). Capture a full-resolution
still, click the palm center on the frozen image and adjust the square, then
restore the selected ROI. The page compares the exact 128x128 RGB input and
restored output, and offers downloads of both and the full original. This is
manual ROI selection, not automatic palm detection or identity verification.
Images are held in memory; capture data is not overwritten. The server retains
only the latest restoration snapshot; another tab's capture expires the old one.

The Pi 5 UVC camera exposes continuous autofocus through V4L2; `/palmir` shows
its state and offers an enable button. A motor control being enabled does not
prove convergence or a sharp photograph. The service requests supported
640x480 preview (configurable through `PALM_PREVIEW_WIDTH`/`PALM_PREVIEW_HEIGHT`),
and full-still capture waits 15 frames after switching resolution.

Set a selected ROI as the in-memory reference, take another image of the same
palm and restore it to see raw/restored distances from the original DoN matcher
(lower is better). The API also retains diagnostic cosine similarities from the
clean CNN used in RIA training, explicitly separate from DoN. A checksum/provenance
check binds that CNN to the restorer. No live-camera acceptance threshold is deployed; these scores
are not acceptance rates. References disappear on service restart and are shared
between tabs. Comparing the reference snapshot against itself is labelled.

The deployed model is the completed local `polyu_palm/ria/best.pt` checkpoint
(seed 2026, selected epoch 48 of a completed 50-epoch run), exported from the
provenance-matched CompactRestorer implementation. It is a controlled local
PalmIR-style baseline, not the official PalmIR architecture. PolyU ROI training
does not validate improvement or recognition accuracy on this live USB camera.
The paused decision-alignment training queue is unrelated and remains paused.

Install `requirements-palmir.txt` into `.venv` for CPU ONNX inference. The
`models/local-palmir-ria.json` manifest records checkpoint/source/model hashes
and preprocessing. Runtime verifies the ONNX checksum before loading it.
Re-export with `tools/export_local_palmir.py <experiment-root> <checkpoint>
models/local-palmir-ria.onnx` using a host with PyTorch, ONNX and ONNX Runtime.
The export check covers random, black and white inputs, requiring less than
one quarter of an 8-bit level before rounding and at most one level after.
Measured max float difference was 0.0001191; two Pi 5 CPU inference calls took
90.5 and 77.3 ms, excluding still capture and HTTP/image encoding.
These initial export checks do not cover all real inputs: the later low-contrast
blur audit exceeded that bound (about one 8-bit level on a checked example),
and changed one near-threshold impostor decision. The challenged results were
rechecked with the original PyTorch checkpoint; do not transfer thresholds
between runtimes without on-device calibration. An attempted explicit centered
GroupNorm export did not solve all discrepancies and was not deployed.

`tools/compare_local_palmir_captures.py <archives> <fresh-output>` performs a
small historical-camera assay using PKLNet ROIs and this trained matcher. Per
labelled palm, sample 1 supplies the same raw gallery in both branches, 2–5 set
one raw-branch impostor threshold, and 6–10 measure raw/restored true and false
accepts at that fixed threshold. It reports failures and saves paired examples,
scores and hashes. These are correlated captures from one burst per palm;
neither a population accuracy claim nor calibration for a new USB camera.

The corrected `/palmir-report` adds full-image ROI overlays, original DoN with
five raw gallery images, and three predetermined synthetic blur diagnostics.
Originals: true accepts 20/20 and false accepts 1/60 both before/after restoration.
Original PyTorch checkpoint under synthetic Gaussian sigma 1.5: true accepts
20/20 -> 7/20; sigma 2.5: true accepts unchanged 20/20, false accepts 8/60 -> 2/60;
motion length 9 at 45 degrees: unchanged. These small correlated examples do
not support enabling automatic restoration by default. All 40 samples remain;
22 have contrast below the engineering warning value 12, which is not a
validated eligibility cutoff. The earlier 55% figure belongs to the local CNN
assay, not DoN, and remains in the original summary/CSV for audit.

Open `http://<Pi-IP>:8080` when the service is running. Enter a participant code,
select left or right hand, and press the capture button or Space. The first shot
starts a labelled ten-image group. Check originals and click an image to inspect
native pixels. Switch hands or finish a partial group without deleting photos;
download any nonempty group as a ZIP. Each new sample saves only `full.jpg` and
`metadata.json`, with `roi_processing=deferred`; the group also has a manifest.
The live preview and browser magnifier do not create saved ROI artifacts.

Select a thumbnail and use **Delete selected photo** to remove a bad shot and
continue capturing up to ten retained images. Remaining metadata indices are
renumbered; their original indices and the previous manifest are preserved.
Saved groups also offer **Delete entire group**. Both actions require a UI
confirmation and move originals into `runtime/collection_trash/` rather than
erasing them. Recovery is currently manual using the saved recovery record,
manifest and metadata backups; the UI does not have a restore button.

In optional recognition debug mode, enter a user ID,
enroll five samples, remove and replace the hand, then verify. The quality gate
requires five fresh, in-bounds frames with sufficient contrast and sharpness.
Capture states are NO_HAND, TRACKING, LOW_QUALITY and READY; lost/stale tracking
clears the accepted ROI. Gate thresholds are engineering settings.

Use camera enrollment with institutional approval and participant consent.
ACCEPT/REJECT includes distance, threshold and pipeline time. Thresholds are
provisional. RGB and NoIR+IR use separate profiles/templates; check the camera
index. Changing matcher/ROI mode needs re-enrollment. NoIR+IR is not automatically
palm-vein recognition. The retired CLI is under `../../archive/palm_demo_legacy/`.

## Capture and analyze

The default `/collect` page saves full-resolution originals and capture metadata.
ROI extraction happens later on saved images. In optional recognition mode, `/demo`
uses the full-still PKLNet extractor with DoN and the verification page processes
preview frames with PKLNet and DoN. Existing templates from another
ROI version require re-enrollment; demo ranking excludes incompatible templates.
The demo defaults to DoN; use `--demo-matcher OC`, `--demo-matcher PC` or
`--demo-matcher FastCC` when explicitly comparing alternatives. Templates also
need re-enrollment when changing matcher, since feature formats differ.

To regenerate ROIs and run the 14-matcher benchmark on a saved Pi snapshot:

```powershell
python tools/benchmark_pklnet_captures.py C:/path/to/pi_snapshot C:/path/to/results
```

The runner preserves originals, saves raw/normalized ROIs, keypoints and overlays,
and writes extraction manifests, pair scores, gallery/probe scores and a comparison
sheet. Only explicit participant/hand labels enter identity comparisons. The first
five images per hand form the gallery; indices 6–10 are probes. Unlabelled older
images get new ROIs but are excluded from identity metrics. Short continuous hand
bursts provide exploratory scores, not an estimate of population accuracy.
Nonmate scores include both another hand of the same participant and hands of
other participants; `pair_relation` distinguishes these groups. Identical branch
image sets reuse the measured scores and timings while preserving both branches.

The default camera-only service uses `.venv` and does not need PyTorch. For offline
PKLNet, install `requirements-pklnet.txt` in `.venv-pklnet` alongside the runtime
dependencies, or run the extraction benchmark on the development PC.

PKLNet extraction defaults to FP32 ONNX Runtime, using the same PKLNet weights
and ROI geometry as the PyTorch path. Install `requirements-pklnet.txt` and place
`pklnet-keypoints.onnx` and its generated JSON manifest beside the weights. The
export script is `tools/export_pklnet_onnx.py` (requires the `onnx` Python package
on the export host). Use `--roi-backend torch` with the offline benchmark to select
the original PyTorch path. On the Pi 4, 20 saved full-resolution captures took a median
4.57 seconds with PyTorch and 1.92 seconds with ONNX. All 20 ONNX crops passed the
geometry guard and keypoints differed by at most 0.0019 source-image pixels.
In this small same-person, left/right-hand dataset, FastCC pair EER changed from
0% to 1.06% with the ONNX crops after one opposite-hand score crossed a near-tie.
This EER sweep is exploratory; its approximately 0.392 decision point differs
from the benchmark's fixed FastCC reference threshold of 0.28. Keep one backend for enrollment and matching,
and recalibrate thresholds before switching an existing deployment.

Replaying all 14 matchers on the same 20 ONNX crops gave OC 0% exploratory pair
EER and 10/10 gallery/probe rankings, with a positive boundary gap of 0.00833
(minimum opposite-hand distance minus maximum same-hand distance). The same gap
was 0.00833 on the PyTorch crops; FastCC's gap changed from 0.00090 to -0.00111.
OC took about 57 ms per feature extraction and 4 ms per pair comparison on the
Pi 4, excluding ROI extraction. EDM had a wider 0.02890 gap but took about
218 ms per extraction and 25 ms per comparison. OC was selected for the original
snapshot for its lower CPU cost; this single-person snapshot does not establish general
recognition accuracy. The demo continues to rank compatible enrolled templates
without a calibrated open-set acceptance threshold.

The expanded 2026-10-13 snapshot contains two participants, four labelled palms
and 40 full-resolution originals. All 40 ONNX crops passed the geometry guard;
visual inspection found no obvious collapsed or out-of-palm crops, with some
low-contrast samples retained. Median ROI extraction was 2.06 seconds on the Pi,
including JPEG decoding. Across 180 same-hand and 600 nonmate pairs, exploratory
EER was 0.97% for DoN, 1.42% for DRCC, 1.67% for EDM, 2.19% for OC and 2.36% for
FastCC. All 14 matchers ranked all 20 gallery/probe trials correctly. The prior
20 normalized ROIs and their pair scores were identical on replay; the changed
metrics came from the expanded sample set. Cross-person pairs and same-person
opposite-hand pairs are reported separately; no acceptance threshold is deployed
from these results. The expanded comparison selected DoN as the default demo
matcher. Existing OC or FastCC templates are excluded by their algorithm metadata
and need re-enrollment before use with DoN.

Profiling the actual DoN Gallery path on the Pi with four palms and five stored
features per palm gave a warm median of 2.96 seconds from a saved full-resolution
JPEG to identification (20 probes, 20/20 correct; p95 3.06 seconds). The cold
first call took 6.09 seconds, including 3.04 seconds to load ONNX. Warm stage
medians were 219 ms JPEG decoding, 1,988 ms ROI extraction, 3 ms normalization,
15 ms DoN extraction and 728 ms template-file loading plus 20 comparisons.
These measurements exclude camera capture and HTTP transport. Reproduce on the
Pi with `python tools/profile_pklnet_identification.py <extraction_manifest.json> <fresh-output-directory>`;
profiling templates stay in that output directory.

The remaining capture and verification controls below belong to optional
recognition debug mode, enabled with `--enable-recognition`.

In the web **Quick 10-image repeatability test**, start a new session, remove
the hand, confirm removal, replace it, wait for READY and save one image per
placement. Download the ZIP after ten placements. Each sample contains raw.png,
the exact matcher-path roi_128.png and metadata.json (times, geometry, quality,
camera settings and hashes). From Windows:

```powershell
python .\tools\analyze_repeatability.py C:\path\to\test01 --expected 10
```

For a 30-placement pilot on the Pi:

```bash
python3 tools/collect_roi_diagnostics.py --output runtime/repeatability/person01_hand01_repeat30 --placements 30 --frames-per-placement 1
python3 tools/analyze_repeatability.py runtime/repeatability/person01_hand01_repeat30
```

Keep hand, camera, light and distance consistent; remove/replace for each
placement. Preserve partial sessions. Analysis uses image 1 as reference and
writes scores, summary and comparison sheets under repeatability_report.
Lower Fast-CC distance means greater similarity. Decisions remain UNASSESSED
without a previously selected `--threshold`; do not fit it to the same samples.
A single hand cannot measure false accepts. Inspect difficult crops for palm
coverage, rotation, scale, blur and lighting.

## Files and provenance

- Entry point: debug_ui.py (web).
- palm_app/: camera UI, shared normalization/storage, ROI, quality and matching.
- models/ and vendor/: runtime dependencies, not disposable caches.
- deploy/: installation, packaging, connection and service tools.
- tools/ and tests/: collection, analysis and development checks.
- runtime/: local templates, logs and captures, excluded from deployment bundles.

Remove both user .npz and .json files under runtime/templates to delete a
template. Original camera frames are saved by explicit debug collection.
Keep originals and manifests when cleaning derived results.

The old dataset tools are archived under `../../archive/palm_demo_legacy/tools/`.
Install requirements-dev.txt and the pinned matcher before reproducing them.
Labels use P_F_<identity>_<sample>.bmp;
this does not establish Pi-camera accuracy. See [source manifest](data/SOURCE_MANIFEST.md)
and preserve source restrictions on redistribution.

OC/Fast-CC/DoN use [palmprint-recognition-python](https://github.com/Li-ChengYan/palmprint-recognition-python),
pinned to d556f455a6cbdcb4264ec1cd75de2e451cf241b3. Fast-CC uses two Gabor
directions and shifted Hamming distance. The MIT implementation is independent,
not an official reproduction; upstream benchmark numbers are not ours.
[PPNet](https://github.com/xuliangcs/ppnet) (old runtime stack),
[X-Palm](https://github.com/X-Palm/X-Palm-2026) (academic data EULA) and
[Palm-ID](https://arxiv.org/abs/2401.08111) are research references, not deployment
dependencies. Their training/search timings are not Pi timings. Before adopting
another model, record source/license, commit, weight hash, ARM64 installation,
deterministic image checks and Pi latency, memory and temperature.
# ROI localization repair (2026-10-25)

The October 25 default was `pklnet-heatmap-v3`: use the heatmap branch for every image,
instead of averaging it with the FC branch. Opposite endpoint ordering made
the old average collapse several palm crops. Fixed branch selection avoids
that fusion defect; it cannot repair every incorrect landmark prediction.
No identity scores enter localization. Branch disagreement remains diagnostic
and no longer vetoes the selected crop. Finite coordinates, bounds and minimum
span still protect against invalid geometry.

The ONNX runtime needs the additional diagnostics artifact. Generate it from
the existing checksum-verified export on a computer with `onnx` installed:

```powershell
python tools/expose_pklnet_branches.py ../pklnet/pklnet-keypoints.onnx ../pklnet/pklnet-keypoints-diagnostics.onnx
```

Deploy both the new `.onnx` and `.json` alongside the existing weights and
`roiExtractor.py`. The extension exposes existing branch tensors without
retraining or changing weights. Unknown fusion graphs and missing branch
outputs are rejected. `policy="legacy"` and `policy="consensus"` retain the old
policies for explicit historical replay; v4 startup uses the aspect policy described below.

Contrast and sharpness are diagnostic only, as requested; they do not reject
live or high-resolution samples. Completely constant crops remain unusable
for percentile normalization. There is no new temporal wait on the capture
button. An unsuccessful batch writes no new template. Old geometry
templates are excluded; entering the original ID again replaces an incompatible
template only after five valid captures, preserving its existing account name,
balance and transactions. The demo page identifies accounts needing re-enrollment.

Replay: `tools/evaluate_heatmap_policy.py <benchmark> <new-output-directory>`.
Actual ONNX replay on all 40 originals, fixed first-five/last-five split, no
quality filtering: DoN 3→11/20, FastCC 9→11/20, local neural matcher 12→14/20.
These all-sample diagnostics include invalid crops and isolate localization;
the separate `runtime-guard.json` reports deployment geometry rejections against
all 20 probes. Geometry acceptance is 36/40, compared with 31/40 originally.
Four localization failures remain. This repeatedly inspected two-person batch
is a development set, not independent validation or a calibrated acceptance test.

Endpoint permutation fusion was also tested: DoN 5/20, FastCC 7/20, neural
13/20. It is not enabled. The independent OpenCV hand detector control returned
crops on only 22/40 images (including visible background false detections);
it is not an automatic fallback. The local PalmIR-style RIA gives no additional
neural rank-one improvement (14/20); it is not official PalmIR and remains optional.
No matcher or acceptance threshold was changed. The current report and patch are
under `runtime/pi5-new-camera-20261021/heatmap-v3-20261025/`; the earlier
consensus-v2 report/archive are historical and superseded. V3 was deployed on October 27,
then superseded by v4 below.

The follow-up `restoration-adaptation-20261025/report.html` evaluates input
normalization, half-strength restoration, probe-only restoration and the existing
pixel-only checkpoint. Normalization alone changes the neural development result
from 14 to 15/20; RIA adds no correct queries. Its mean change is only 0.086/255
on raw camera inputs. CPU PyTorch matches ONNX on this batch (max 2.8e-5 in [0,1]).
Existing pixel-only restoration scores 13/20 raw and 15/20 normalized. Training
domain synthetic response checks show the model can restore its trained blur;
they do not establish camera-domain benefit. No training was started.

## Reference ROI control (2026-10-26)

All 40 images now have assistant visually estimated finger-web reference points,
reviewed and hashed before scoring. These are development annotations, not
independently adjudicated human ground truth. Keeping the same complete split
and matchers, reference crops score DoN 17/20, FastCC 19/20 and neural 17/20,
versus automatic heatmap 11/20, 11/20 and 14/20. Nine automatic crops have IoU
below 0.5 against the references, despite only four failing the old geometric
guard. This supports localization as a major bottleneck; it does not establish
an automatic 19/20 pipeline. RIA still adds no correct queries.

Report: `runtime/pi5-new-camera-20261021/reference-roi-20261026/report.html`.
Run `tools/audit_reference_roi.py prepare|render|score <benchmark> <output>`;
`render` consumes explicitly supplied `annotations.json` and refuses revisions
after scoring. Label-independent segmentation zoom and contour prototypes were
also evaluated and regressed, so that investigation retained heatmap-v3. No new training
or Pi deployment occurred on October 26. Use new sessions for any future localization training
validation; this repeatedly inspected batch is only a development set.

## Conditional aspect repair (2026-10-27, deployed)

The October 27 default used `pklnet-heatmap-aspect-v4`. It retains valid
full-frame heatmap crops exactly. Only a geometric failure triggers a centered
4:3 inference crop, preserving orientation. Coordinates are mapped back and
checked against the original image and unchanged minimum span; final ROI pixels
come from the original. This reduces sensitivity to the wide image's padding
and field of view. It does not establish a camera hardware defect.

Pi replay of all 40 new-camera originals yielded 40 valid geometries, four
five-image enrollments, 13/20 actual HTTP DoN identifications and four held-out
simulated payments. FastCC scored 12/20. Single-core ROI latency was median
1.52 s, p95 3.06 s; failed first passes require two inferences. The Pi reported
`throttled=0x0` before and after this run. The 40-image old-camera local replay
remains 20/20 DoN and FastCC with all four enrollments/payments passing.
All 36 previously valid new-camera ROIs and all 40 old-camera ROIs were unchanged
in the local pixel comparison. Originals were preserved; stores were isolated.

Seven new-camera queries are still wrong. Geometry validity is not anatomical
accuracy, and this repeatedly inspected development batch is not independent
validation. Manual reference results (17/20 DoN, 19/20 FastCC) are not automatic
pipeline results. No thresholds, matcher, training weights or identity-based
selection were changed. Use `policy="heatmap"` for explicit v3 reproduction.
Old templates need re-enrollment under v4; existing accounts and balances remain.
The Pi service stays capture-only and currently waits for the unplugged camera.

Evidence and comparison: `runtime/pi5-roi-v4-20261027/report.html`; Pi results:
`pi/summary.json`; verified deployed hashes and backup: `deployment.json` in the
same evidence directory. Relevant unit tests: 38 passed.

## Illumination consistency (2026-10-28, deployed)

`PKLNetROI()` now defaults to `pklnet-illumination-consistent-v5`. Run the v4
localizer on original RGB and on fixed gamma 0.6 RGB. If both are valid, use
the adjusted prediction only when the quadrilateral IoU is at least 0.5;
otherwise retain the original prediction. If only the adjusted result is valid,
use it. Final ROI pixels always come from the original image. No identity scores
or reference labels enter this choice. `policy="aspect"` reproduces v4.

All 40 new images remain geometrically valid. Full-denominator local DoN/FastCC
is 15/20; real Pi HTTP DoN is 14/20 and offline FastCC is 15/20. Four enrollments
and four isolated held-out simulated payments pass on Pi. Original files are
unchanged. Old local real-HTTP replay remains 20/20 with four enrollments/payments.
Pi single-core ROI median is 3.16 s, p95 6.22 s; this adds latency versus v4.
The service remains capture-only, waiting for a camera, with `throttled=0x0`.

The local DoN improvement corrects three probes but regresses one; Pi additionally
flips a near-tied probe. Pi/local quad differences are below 0.002 original-image
pixels, but normalized ROI pixels differ slightly. Local matching of Pi's exact
saved pixels reproduces 14/20. This isolates the discrepancy upstream of matching,
with the later frozen-quad audit locating the principal difference in OpenCV
uint8 perspective interpolation/quantization: JPEG RGB hashes match for all 40
images, while 9,390 warped gray pixel values differ by one before normalization.

Probe-only synthetic stress (clean five-image enrollment held fixed) compares
v4/v5: DoN darkening 13/16, blur 14/15, translation 7/16 correct out of 20;
FastCC 9/16, 17/16, 13/16. Every failed probe stays in the denominator. These are
development perturbations, not independent validation, and include a regression.

The existing local PalmIR-style RIA was evaluated on all 40 final v5 ROIs with
raw/normalized inputs, both-side/probe-only restoration and half residual blending.
No setting adds correct queries: DoN/FastCC stay 15/20 locally; paired neural
matcher stays 14/20 raw and 13/20 normalized. Mean raw change is 0.0214/255.
It is not official PalmIR and is not enabled in default recognition.

Tests: 43 passed. Tools: `audit_roi_robustness.py`, `audit_roi_consistency.py`,
`stress_roi_pipeline.py`, `write_roi_v5_report.py`; final Pi replay:
`/home/fyp5/pipeline-roi-v5-consistent-20261028/`. Use
`tools/replay_pi_pipeline.py <source> <new-output> --policies illumination`
for current-only real HTTP replay. Earlier policy audits remain explicit controls.

## Pose matcher and stability audit (2026-10-28, optional / not deployed)

`--demo-matcher FastCCPoseNearest-v1` enables a fixed nine-pose query bank
(angles 0/±12 degrees and scales 0.85/1/1.15), cropped from the original full
image around the v5 quadrilateral. It requires PKLNet ROI mode. Matching uses
the nearest of five original enrollment templates. Its versioned feature format
cannot share old templates; reenroll into an isolated store. The default remains
DoN. This provides ranking only, with no validated unknown-person threshold.

Actual local HTTP replay: new images 18/20, old images 20/20, each with four
enrollments and four isolated simulated payments. This candidate has not been
validated on Pi. Wider pose search, crop-only augmentation, floating-point
sampling and the existing PalmIR restoration did not produce stable gains.

Stability is insufficient for a reliability claim. Ten fixed random 5-of-10
enrollment splits give new-image candidate 15–18/20 (mean 16.7), versus DoN
13–17/20 (mean 15.1). Reversing the original split gives candidate 16/20 versus
DoN 18/20. All old-image splits score 20/20 for both algorithms. These reuse the
same 80 development photos from two people / four palms, not independent trials.

Cross-camera candidate results are 6/20 for old enrollment → new queries and
10/20 in reverse. Global rotation/reflection/polarity controls do not resolve
this. Mixed enrollment is also not a fix: old/new 3+2 or 2+3 templates yield
new-query random ranges 8–17/20 or 9–18/20; even 5+5 templates give 15/20.
Query indices 6–10 never enter those enrollment pools. Do not infer hardware
failure, relabel identities, or choose the highest development score as an
independent validation result.

Evidence: `runtime/roi-palmir-20261028/stability/report.html`, with source JSON,
full HTTP traces, and input hashes linked there. Tools:
`audit_matcher_stability.py`, `audit_cross_camera_orientation.py`,
`audit_mixed_camera_enrollment.py`, `write_stability_report.py`.
The hourly automation was removed; no scheduled iteration is active.

## Single-device registered matching (2026-10-28, optional / not deployed)

The user explicitly scoped subsequent work to enrollment and queries on the same
device. Cross-device recognition is not an acceptance criterion for this work.

`--demo-matcher FastCCRegisteredBest2-v2 --roi-mode pklnet` adds automatic local
alignment before FastCC matching. It uses the frozen automatic v5 palm quad,
384px RootSIFT correspondences from original and Gaussian-sigma-2 descriptor
views, and constrained partial-affine RANSAC. Appearance is sampled from the
original grayscale context; descriptor smoothing does not alter matching pixels.
Invalid alignment or sampling outside the original image/context falls back to
the existing nine-pose comparison. Each identity uses the mean of its best two
templates, retaining all five enrolled samples. No identity labels or reference
points enter extraction or matching. Version v1 retains the single-view control.

Packed numeric templates are versioned, saved with the existing compressed NPZ
store, and cannot share DoN/pose/v1 templates. Reenrollment is required. V2 stores
approximately 1.64 MB per capture before compression, including grayscale palm
context and descriptors; protect them as biometric templates. Default DoN is
unchanged. Pi deployment and timing have not been verified.

Same-device results with the actual v2 matcher and reloaded templates:

| New-camera split | Pose nearest | Registered v2 |
| --- | --- | --- |
| First five enroll, last five query | 18/20 | 20/20 |
| Reversed | 16/20 | 18/20 |
| Original ten random splits | 15–18/20, mean 16.7 | 17–20/20, mean 18.3 |
| Additional 100 fixed seeded splits | 15–20/20, mean 17.28 | 16–20/20, mean 18.65 |

Old-camera results remain 20/20 for all 112 splits. Actual local HTTP replay for
each camera gives 20/20, four enrollments, and four isolated simulated payments.
The 80 original image hashes remain unchanged. This is still repeatedly inspected
development data from two people/four palms, not 2,000 independent test samples,
an unknown-person rejection test, or live-camera validation. Some splits regress;
the improvement does not solve every severely mislocalized palm crop.

Error diagnosis found four photos failing almost whenever queried; the same
photos have inconsistent palm scale/position. Replacing only the ROI with frozen
assistant visual reference crops gives FastCC-median 18–20/20 across the original
ten splits. These are development annotations, not automatic results or an
independent ground truth. Pure local-feature counts and aggregation-only changes
did not solve the problem.

Report: `runtime/roi-palmir-20261028/single-device/report.html`. Evidence and tools:
`audit_local_alignment.py`, `audit_registered_matching.py`,
`audit_registered_runtime.py`, `audit_alignment_smoothing.py`,
`write_single_device_report.py`. Relevant regression tests: 27 passed.

### Multi-ROI development candidate (2026-10-28)

Optional `--demo-matcher FastCCMultiROI-v3` preserves both valid original/gamma
localizations and samples aligned appearance once from native grayscale pixels.
It requires PKLNet ROI mode and newly enrolled version-specific templates
(8.16 MB per capture uncompressed). Default DoN remains unchanged.
Actual stored/reloaded runtime results: new original 20/20, reverse 19/20,
ten random 19–20 (mean 19.8), extra 100 18–20 (mean 19.92); old all 20/20.
Local HTTP historical replay: each device 20/20, four enrollments and four
isolated simulated payments. 44 related tests passed. No Pi deployment.

Further **offline-only** fixed-window plus coarse-descriptor candidate union
reaches 20/20 in all existing 112 splits per device. This is repeated development
data, not independent validation, and that union is not integrated into v3.
Visual diagnosis and all controls: `runtime/roi-palmir-20261028/single-device/report-v3.html`.

### Window/coarse union runtime v4 (2026-10-28)

Optional `--demo-matcher FastCCWindowUnion-v4` now implements the uniform offline
union in the actual PKLNet capture pipeline. See [ROI pipeline](docs/ROI_PIPELINE.md).
Default DoN remains unchanged; no Pi deployment or network change was made.

- All 3,120 non-self within-device pair distances from saved/reloaded templates
  exactly match the offline union. `base_full` remains a separate control.
- Fresh ONNX inference reproduces 76/80 templates byte-for-byte. All 300 directed
  pairs touching the four changed templates were recomputed. The unchanged
  original/reverse/ten random/100 extra splits remain 20/20 for both devices.
- Actual local HTTP historical-image replay: each device 20/20, four successful
  enrollments and four isolated simulated payments. 48 regression tests pass.
- Each numeric template reserves 16 MiB, compressed NPZ median 5.44 MB/capture.
  During concurrent local audits, fresh localization plus extraction median was
  3.71 s; HTTP identify median new 10.00 s, old 4.75 s. These are not isolated
  benchmarks or Pi timings. Current runtime is expensive for an interactive demo.

Results remain repeatedly inspected development data from two people. There is
no independent-session generalization, unknown-person rejection or live-camera
validation. New version-specific enrollment is required; preserve old accounts
and templates. Report: `runtime/roi-palmir-20261028/single-device/report-v4.html`.
Source patch: `single-device-v4-patch.zip` with `patch-v4-manifest.json` in that
directory; historical patches and failed controls remain intact.
