# RobustPalmRoi × Tongji / Fast-CC offline findings

Date: 2026-09-18

## Scope and sources

The raw images and reference ROIs are the same 15 official Tongji pairs documented in [the Tongji pairing report](findings_report.md). No unpaired or substitute images were introduced. The RobustPalmRoi implementation was obtained from the public [leosocy/RobustPalmRoi repository](https://github.com/leosocy/RobustPalmRoi), using its upstream `samples/config.yaml` pipeline.

The work is isolated below `offline_tongji_roi_audit/`. Fast-CC was imported from the existing vendor source without edits; its SHA-256 is recorded in `robust_fastcc_results/summary.json`. No Fast-CC or production code was modified.

## Windows execution

The native DLL was built locally with MSVC, OpenCV and yaml-cpp in the audit directory. The upstream C API did not export its symbols on Windows, so the isolated clone received only a Windows export declaration plus OpenCV 4.x constant-name compatibility edits. These changes are not in production.

The OpenCV build available in the isolated environment decodes BMP but not TIFF/PNG through `imdecode`. Therefore Pillow decoded each original TIFF and encoded the identical RGB pixels losslessly as BMP bytes for the DLL boundary. Dimensions and pixels were preserved; this is recorded as `input_transport` in `robust_extraction.csv` and `summary.json`.

## RobustPalmRoi extraction

| result | count |
|---|---:|
| requested raw images | 15 |
| successful RobustPalmRoi ROIs | 0 |
| extraction failures | 15 |

Fourteen samples stopped at `PeakValleyDetector` with “Can't detect all peaks and valleys, please open your fingers”. Sample `00011` raised a native Windows exception (`0xe06d7363`) after the same pipeline stage. No RobustPalmRoi ROI was saved or used as a gallery image, so there is no valid Robust-vs-reference paired Fast-CC comparison for this 15-image set.

The comparison sheet intentionally marks the RobustPalmRoi column as failed rather than filling it with a reference or another algorithm's ROI.

## Fast-CC pairing

The deterministic pairing rule was applied identically wherever an ROI existed:

- gallery: `00001–00003` for palm 1 and `00011–00013` for palm 2;
- probes: the remaining samples;
- genuine pairs: probe against the three gallery samples of the same palm;
- impostor pairs: probe against the other palm's three gallery samples.

The reference-ROI control run completed with 9 genuine and 27 impostor pairs:

| reference ROI Fast-CC score | value |
|---|---:|
| genuine mean / median | 0.1632 / 0.1593 |
| impostor mean / median | 0.3907 / 0.3916 |
| selected equal-error threshold | 0.2349 |
| FMR / FNMR at that threshold | 0 / 0 |

These are reference-only control numbers. RobustPalmRoi has no score rows because its extraction success set is empty; there is no justified algorithm comparison or claimed Robust improvement.

## Requested diagnostics

| diagnostic | Tongji reference ROI | RobustPalmRoi ROI |
|---|---|---|
| palm coverage | not independently measurable from the released crop alone | N/A: 0/15 extracted |
| finger intrusion | not independently measurable without a hand/palm mask | N/A: 0/15 extracted |
| alignment consistency | no generated geometry to compare | N/A: 0/15 extracted |
| extraction failures | reference files available for 15/15 pairs | 15/15; see `robust_extraction.csv` |

The previously generated 7-point/21-point proxy metrics remain in `results/metrics.csv`; they are not mixed into the RobustPalmRoi result because the requested Robust ROI was never produced.

## Deliverables

- [comparison sheet](robust_fastcc_results/robust_vs_reference_sheet.png)
- [per-sample comparison images](robust_fastcc_results/robust_comparison_samples/)
- [extraction status and failure reasons](robust_fastcc_results/robust_extraction.csv)
- [reference Fast-CC genuine/impostor scores](robust_fastcc_results/genuine_impostor_scores.csv)
- [pair manifest](robust_fastcc_results/roi_pair_manifest.csv)
- [machine-readable summary](robust_fastcc_results/summary.json)

