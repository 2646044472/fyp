# Palm camera demo

Local Raspberry Pi palmprint enrollment and 1:1 verification. For connection,
installation and hardware precautions, see [SETUP](docs/SETUP.md).
Commands below run from `code/palm_demo` on Windows or `~/palm_demo` on the Pi.

## Architecture

Camera → palm ROI → quality gate → 128×128 normalized grayscale → features →
enrolled templates → distance and threshold decision.

| Entry | ROI | Matcher |
| --- | --- | --- |
| `debug_ui.py` / Pi service (default) | None: original full-resolution collection | None |
| Optional recognition debug mode | PKLNet keypoints and native crop | DoN / Fast-CC demo |
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
uses the full-still PKLNet extractor with Fast-CC and the verification page processes
preview frames with PKLNet and DoN. Existing templates from another
ROI version require re-enrollment; demo ranking excludes incompatible templates.

To regenerate ROIs and run the 14-matcher benchmark on a saved Pi snapshot:

```powershell
python tools/benchmark_pklnet_captures.py C:/path/to/pi_snapshot C:/path/to/results
```

The runner preserves originals, saves raw/normalized ROIs, keypoints and overlays,
and writes extraction manifests, pair scores, gallery/probe scores and a comparison
sheet. Only explicit participant/hand labels enter identity comparisons. The first
five images per hand form the gallery; indices 6–10 are probes. Unlabelled older
images get new ROIs but are excluded from identity metrics. A single person's two
continuous hand bursts provide exploratory scores, not biometric accuracy.

The default camera-only service uses `.venv` and does not need PyTorch. For offline
PKLNet, install `requirements-pklnet.txt` in `.venv-pklnet` alongside the runtime
dependencies, or run the extraction benchmark on the development PC.

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

Fast-CC/DoN use [palmprint-recognition-python](https://github.com/Li-ChengYan/palmprint-recognition-python),
pinned to d556f455a6cbdcb4264ec1cd75de2e451cf241b3. Fast-CC uses two Gabor
directions and shifted Hamming distance. The MIT implementation is independent,
not an official reproduction; upstream benchmark numbers are not ours.
[PPNet](https://github.com/xuliangcs/ppnet) (old runtime stack),
[X-Palm](https://github.com/X-Palm/X-Palm-2026) (academic data EULA) and
[Palm-ID](https://arxiv.org/abs/2401.08111) are research references, not deployment
dependencies. Their training/search timings are not Pi timings. Before adopting
another model, record source/license, commit, weight hash, ARM64 installation,
deterministic image checks and Pi latency, memory and temperature.
