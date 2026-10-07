# Raspberry Pi Palm Matcher Diagnostic (2026-10-05)

## Decision investigated

Does the poor recognition seen with our own Pi captures come from a broken Fast-CC implementation, or from the current capture, ROI and matcher combination?

## Evidence

- [E] The Pi and PC use Fast-CC commit `d556f455a6cbdcb4264ec1cd75de2e451cf241b3`. For the Pi's `20260916T201834Z/sample_001` ROI, both machines produced the same packed-feature SHA-256 (`42716e9bf4e5c000d94433fa19d0f2054dca30017f60fec49f1c72341e3b28fc`) and the same distance to `sample_008` (`0.3958333333333333`). Self-distance was zero. This checks one exact pair, not every device/runtime path.
- [E] The 33 saved Pi debug samples have 33 distinct frame IDs. Recomputing each 128x128 ROI from its saved raw frame and recorded quadrilateral matched the saved ROI exactly (33/33). The raw frames are 480x360; the debug UI uses `palm-detector-mcp-v2` dynamic ROI. The local copies are in `code/palm_demo/data/processed/pi-own-captures/debug_capture/` and remain outside Git.
- [E] In the three complete 10-image Pi batches, using samples 1-5 as enrollment and 6-10 as queries, Fast-CC median-of-five probe scores were:

  | Pi batch (UTC) | Query scores | Scores at or below 0.28 | Scores at or below 0.15 |
  | --- | --- | ---: | ---: |
  | `20260916T152121Z` | 0.322, 0.410, 0.377, 0.400, 0.376 | 0/5 | 0/5 |
  | `20260916T201834Z` | 0.323, 0.254, 0.321, 0.243, 0.244 | 3/5 | 0/5 |
  | `20260916T202013Z` | 0.358, 0.389, 0.328, 0.352, 0.411 | 0/5 | 0/5 |

  [E] The user clarified on 2026-10-05 that the three batches were not all the same hand. [GAP] The debug metadata lacks a person/hand label for each sample, including within-batch labels. These are *within-batch scores*, not genuine-match trials or measured false-reject rates; cross-batch scores must not be treated as genuine either. The September 16-17 live logs contain low-score accepts at threshold 0.15, but those transactions are not linked to these debug sample IDs and do not establish cross-presentation reliability.
- [E] The existing PalmBigDataBase development subset has 20 identities x 10 pre-cropped 128x128 palm images. With five enrollment and five query images per identity and threshold 0.28, the current Fast-CC script reproduced 3 rejects among 100 genuine queries and 0 accepts among 1,900 pairwise impostor comparisons. This is a local development subset and same-source result, not Pi-camera performance.
- [E] CASIA WHT full-hand images are 768x576. On a fixed first-20-subject/both-hand subset (240 images), a single-frame replay of the Pi-style dynamic detector returned an ROI for all 240. With three enrollment and three query images per hand, the correct hand ranked first in only 23/120 queries. At threshold 0.28, 7 were correct and 113 unknown. This offline replay does not exercise the Pi's five-frame quality gate or independent visits.
- [E] The separate payment UI defaults to `AutomaticPalmROI`, rather than the Pi debug UI's dynamic detector. On the same 240 CASIA WHT full-hand frames, its original edge rule returned `HAND_CLIPPED` for 237 and accepted 3. Many frames show the wrist reaching the image edge. This demonstrates a payment-path ROI incompatibility with these full-hand images; it does not explain the Pi debug captures, which used the dynamic detector.
- [E] The normalized central 64x64 ROI's median gradient magnitude was 25.3 for the PalmBigDataBase subset, 6.4 for CASIA ROIs from the payment UI's automatic ROI mode, and 2.1 for the 33 Pi ROIs. The Pi ROIs had a median 17.4% pixels above intensity 235, versus 2.0% in PalmBigDataBase. These descriptive metrics use different sensors and ROI procedures; they support a visual observation of faint/washed-out palm lines but do not identify exposure, focus or illumination as the sole cause.
- [E] All 33 Pi debug captures were labelled `READY` by the current quality gate (median whole-ROI contrast 36.12, sharpness 20.04). The gate checks whole-ROI contrast/sharpness and geometric stability; its acceptance does not establish that the palm interior contains stable line detail. The large skin/background boundary and finger gaps can contribute to the whole-ROI measures while the central texture remains weak.
- [E] Fixed centre crops (96x96 or 80x80, resized) and CLAHE on the Pi ROIs did not improve the 15 within-batch query results at threshold 0.28: all retained only 2-3 scores at or below 0.28. This is a diagnostic replay, not a safe policy comparison; impostor outcomes are absent.

## Interpretation and next gate

### ROI output-size comparison (existing dataset only)

- [E] All 200 images in the PalmBigDataBase development manifest are natively 128x128. The evaluation script crops the full image, normalizes to 128x128 and passes that array to FastCC. Its 97/100 genuine accepts at threshold 0.28 therefore did not depend on higher-resolution algorithm input.
- [E] Replayed the same 240 CASIA WHT original frames and independently located each palm once. The exact same quadrilateral was then sampled at 128x128, 256x256 and 512x512, with the same 1st/99th-percentile intensity normalization, FastCC kernels, 4-pixel subsampling and 4-feature-pixel matching shift. With the fixed 3-enroll/3-query split over 40 hands, correct-hand rank 1 was 23/120, 23/120 and 19/120 respectively. Mean extraction times on this PC were 8.9 ms, 34.2 ms and 142.0 ms; these are not Pi timings. Results: `code/palm_demo/data/processed/casia-wht-dev/eval-roi-sizes-2026-10-05.json`.
- [E] The median native quadrilateral side was 377.8 source pixels, so the 512 output often interpolates beyond native palm sampling. [GAP] This experiment changes output sampling and the effective physical scale of fixed filters/shift tolerance together. It does not test a higher-resolution camera capture, nor establish that retuned larger-size models cannot improve. No larger-size threshold was calibrated.
- [E] No new Pi palm image was captured during this comparison; the user paused physical collection while clarifying image sizes. A local collection-page draft exists but has not been deployed to the Pi.

- [E] No Fast-CC arithmetic, version, or saved-ROI mismatch was found in the checks above.
- [C] The current Fast-CC plus free-hand ROI pipeline is poorly matched to these full-hand images. The Pi ROIs visibly include changing finger gaps/palm placement and weak line detail. A clean background alone is unlikely to recover missing palm texture, and raising the threshold without independent non-mate probes could increase wrong matches.
- [GAP] Record person/hand identity for every Pi image and capture-session lineage, collect independent same-hand and non-mate probes, and record per-frame exposure/gain/focus/illumination before assigning a cause or estimating FRR/FAR. A controlled capture comparison should hold one hand, distance, light, focus and ROI method fixed while changing only one presentation or background condition at a time.

The original payment UI edge rule was restored after an exploratory local check; no algorithm change was deployed to the Pi.
