# Tongji Contactless Palmprint ROI audit

Date: 2026-09-18

## Dataset and access verification

The official Tongji project page is [Towards Contactless Palmprint Recognition](https://cslinzhang.github.io/ContactlessPalm/). It identifies the dataset authors/project, states that there are 12,000 images from 600 palms in two sessions, and links both the [Original Images archive](https://drive.google.com/file/d/15hEsOm0fZKUHpFNChPSjwiRfMczxcnVQ/view?usp=sharing) and the [ROI Images archive](https://drive.google.com/file/d/1KZCXi6zAk5mZ1nQHFdeYHboAII3DOjls/view?usp=sharing). The same page explicitly says that an ROI image exists for each original image and that matching names identify the same palm sample.

Both Google Drive links were accessible without an account in this run:

- Original Images: HTTP 200, advertised size 4,949,788,107 bytes.
- ROI.rar: HTTP 200, advertised size 98,291,177 bytes.

The 15 raw members were obtained from the official original archive by byte-range retrieval; the full 4.95 GB raw archive was not copied. The ROI archive was downloaded and the selected members were extracted locally.

Selected pairs are `session1/00001` through `session1/00015`:

- raw: `.tiff`, 800×600, original hand image;
- reference: `.bmp`, 128×128, official ROI;
- pairing check: exact filename stem match for all 15;
- hashes and byte sizes: `results/pairing_manifest.csv`.

No unpaired or substitute images were used.

## Offline processing

The audit imports the existing geometry in [`code/palm_demo/palm_roi.py`](../code/palm_demo/palm_roi.py): the 7-point detector route uses `palm_detection_to_palm_quad`, and the 21-point route uses `landmarks_to_palm_quad`. The existing detector and hand-pose ONNX models were run at the runtime input size of 320×240, then warped to the existing 128×128 ROI size.

The missing OpenCV Zoo `MPHandPose` Python wrapper was placed only in this audit directory. It was not added to production code. Fast-CC was not invoked.

## Findings

| Measure | 7-point | 21-point |
|---|---:|---:|
| Successful ROI extractions | 13/15 (86.7%) | 12/15 (80.0%) |
| Extraction failures | 00013, 00014: detector below threshold/invalid | 00012: hand-pose below threshold; 00013–00014: no 7-point seed |
| Foreground coverage proxy, mean | 87.3% | 88.4% |
| Foreground coverage proxy, range | 0.0–100.0% | 71.8–97.5% |
| Finger-intrusion proxy, mean | 18.2% | 14.0% |

Alignment was directly comparable on the 12 samples where both routes succeeded. The 21-point quad differed from the 7-point quad by a mean center displacement of 0.222× the 7-point quad width, a mean absolute angle difference of 31.6° (maximum 77.4°), and a mean width difference of +27.7%.

These results indicate that the current 7-point and 21-point routes are not geometrically consistent on this small paired sample. The 21-point route generally produces lower finger-side occupancy, but it is not more reliable in this run because it inherits the 7-point detector seed and has one additional hand-pose failure.

“Palm coverage” and “finger intrusion” above are explicitly diagnostic proxies: the released Tongji pair contains the original image and cropped ROI, not a pixel-level hand/palm segmentation mask or landmark ground truth. The proxies use the dark-background foreground mask and the normalized ROI’s top band; they should not be presented as ground-truth anatomical coverage.

## Deliverables

- [15-sample comparison sheet](results/tongji_15_sample_comparison_sheet.png)
- Per-sample comparison images: `results/sample_001_comparison.png` … `results/sample_015_comparison.png`
- [Per-sample metrics](results/metrics.csv)
- [Pairing manifest with hashes](results/pairing_manifest.csv)
- [Machine-readable summary](results/summary.json)

All downloaded data, the offline runner, temporary archive helpers, and generated outputs are under `offline_tongji_roi_audit/`. No production code was changed by this audit, and nothing was deployed.
