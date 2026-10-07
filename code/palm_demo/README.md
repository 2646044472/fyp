# Palm camera demo

Local Raspberry Pi palmprint enrollment and 1:1 verification. For connection,
installation and hardware precautions, see [SETUP](docs/SETUP.md).
Commands below run from `code/palm_demo` on Windows or `~/palm_demo` on the Pi.

## Architecture

Camera → palm ROI → quality gate → 128×128 normalized grayscale → features →
enrolled templates → distance and threshold decision.

| Entry | ROI | Matcher |
| --- | --- | --- |
| `debug_ui.py` / Pi service | OpenCV DNN hand detection and landmarks | DoN |
| Offline PKLNet runners | Learned keypoints and geometric crop | Fast-CC |

PKLNet lives in `../pklnet` and is not integrated into the service. This records
repository configuration, not the verified deployed Pi version. The same-stand
demo does not establish liveness, anti-spoofing or cross-device accuracy.

## Use

Open `http://<Pi-IP>:8080` when the debug service is running. Enter a user ID,
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
