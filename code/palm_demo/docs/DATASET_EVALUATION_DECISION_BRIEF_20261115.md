# Palmprint evaluation decision brief — 2026-11-15

## Decision

There is no demonstrated cross-dataset winner and no candidate is ready to be described as a reliable live or Raspberry Pi system. Keep the current deployed baseline unchanged while treating **PKLNet-v5 ROI + PalmBridge/SF2Net** and **D127 21-point ROI + PalmBridge/SF2Net** as comparison candidates. D127 has broader matched-dataset evidence; it is not a general winner. The recognizer choice is dataset-dependent, and thresholds are not transferable without independent, person-separated calibration.

All results below are offline development evidence from previously exposed cohorts. They must not be described as independent validation, fresh-person accuracy, physical-device transfer, or Pi performance. Left and right hands are separate identities. Rank-1 and EER use each experiment's stated support; values across different supports or datasets must not be ranked directly.

## Results that change the decision

| Dataset and condition | ROI / recognizer | Result | Interpretation |
|---|---|---|---|
| 11KHands development20, 590 planned rows | D127 21-point / SF2e20 | ROI 590/590; Rank-1 185/185; EER .04324 (185 genuine, 9,615 impostor) | Strongest current development slice for this combination; no frozen 11K open-set threshold, and the cohort is exposed. |
| 11KHands development20, same images and PKLNet keypoints | PKLNet alpha .15 vs alpha 0 / PB170 | ROI 527/590 vs 537/590; strict paired Rank-1 transitions included 6 wrong-to-correct and no correct-to-wrong; paired EER unchanged at .03731 | Alpha 0 improved coverage and some ranks on this support, but does not establish a broad or independent gain. |
| 11KHands development20, same images and keypoints | PKLNet alpha .15 vs alpha 0 / SF2e20 | ROI 527/590 vs 537/590; strict paired EER .04197 vs .07463 | The geometry change helped coverage but materially worsened SF2 ranking on the paired cohort. Do not adopt alpha 0 globally. |
| TCD, 12,000 planned ROI rows; no stranger cohort | RTM ROI / PB170 | ROI 11,993/12,000; Rank-1 5,281/6,000 planned (5,877 rankable); EER .02978 (28,914 genuine, 17,261,220 impostor) | Useful closed-set component comparison only. There are no stranger results, verified person/hand-side labels, or reference ROI comparison. |
| TCD, same cohort | RTM ROI / SF2e20 | Same ROI support; Rank-1 5,800/6,000 planned (5,877 rankable); EER .01631 on the same comparison counts | Better rank and EER than PB on this TCD support; this does not establish open-set performance or cross-dataset superiority. |
| PalmSet b16d, 1,600 planned rows | PKLNet-v5 / PB170 | ROI 1,514/1,600; 12/20 gallery hands complete; Rank-1 353/700 planned (405 rankable); EER .06914 (405 genuine, 4,455 impostor) | Many queries are unrankable because of ROI failures or incomplete true galleries. |
| PalmSet b16d, same cohort | PKLNet-v5 / SF2e20 | Same ROI support; Rank-1 338/700 planned (405 rankable); EER .09877 on the same comparisons | The author-formula reference ROI arm is not manual ground truth and has severe direct overlap with recognizer training images. Its high scores are pipeline diagnostics, not a valid generalization target. |
| PalmSet b16d, controlled reconstructed geometry diagnostic | PKLNet keypoints, alpha .15 vs 0 / fixed PB170 and SF2e20 | Both geometries: 1,514/1,600 ROI; same 12/20 complete galleries and 405 rankable known queries. PB Rank-1 355→349, EER .07901→.09383; SF2 Rank-1 348→338, EER .10123→.12593 (405 genuine, 13,551 impostor per arm). | Alpha 0 reduced rank for both recognizers with no coverage gain. The alpha .15 arm was regenerated with shared normalization and is not pixel-identical to production D167 PKLNet-v5 ROI (121/1,514 exact); use only as a controlled geometry diagnostic, not a production comparison. Cohort has direct training-image overlap. |
| X-Palm historical test split, 406 planned rows | D127 21-point / PB170 or SF2e20 | ROI 388/406; 8/20 complete gallery hands; PB Rank-1 39/55 rankable, EER .14545 (55 genuine, 385 impostor); SF2 Rank-1 33/55, EER .25455 | The open-set stranger cohort is not scoreable against a complete gallery. X-Palm was previously exposed, so this is not blind testing. |
| Axon paired cohort, 120 source images | D127 vs PKLNet-v5 / PB170 and SF2e20 | No reference-ROI arm exists. On the 48 common known queries, PB Rank-1 39→39 and EER .1667→.1482; SF2 Rank-1 36→45 and EER .1875→.1042. | A paired ROI comparison on the same images; identity and device limitations remain. Only 10 unknown queries per arm had complete galleries; do not generalize their outcome to the remaining queries or to a FAR guarantee. |

## Coverage, rejection, and leakage

- ROI or feature failure and incomplete gallery are not recognition rejection. Always retain the planned denominator alongside rankable counts.
- EER is computed only from the available genuine/impostor comparisons and is not an operational acceptance threshold. Small or correlated query sets do not support low-FAR claims.
- On PalmSet, the evaluated b16d/cbe42 prefixes substantially overlap the recognizer's training images. Those scores are excluded from generalization claims. Participant, hand-side, and device tokens in PalmSet/TCD are not verified human/device labels.
- X-Palm has person/hand splits, but the project history records prior exposure. Its incomplete galleries also prevent a native full-gallery stranger-rejection result.
- Self-capture and Axon have useful component and paired diagnostics, but no result in this brief establishes fresh-person performance or a Pi/live-camera experience.

## Demonstration status and next work

Do not switch the Pi demo based on these offline results. Keep the current device configuration as the operational fallback. The next meaningful selection step is a frozen, person-separated calibration and evaluation cohort with complete enrollment galleries, followed by a fresh Pi 5 deployment check covering ROI failure, stranger rejection, latency, and the full enrollment-to-identification interaction. No Pi result is inferred from X timings.

This brief contains aggregate metrics only; it intentionally excludes source paths, sample identifiers, images, ROIs, embeddings, and per-sample score records. Detailed local run artifacts remain in the ignored `runtime/` tree and are not required to read this summary.
