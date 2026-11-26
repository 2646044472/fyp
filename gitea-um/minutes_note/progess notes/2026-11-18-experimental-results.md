# 18 November 2026 | Palm recognition: results, comparison conditions and trade-offs

This report asks four questions: Can the localizer find a usable palm region? How often does the correct hand rank first against a fixed gallery? Are unknown hands falsely accepted? Do offline findings transfer to a different setting? A correct match requires the same person and hand. Each table states its own denominator and any relevant training exposure or comparison limits. Results from different cohorts are not pooled.

[Project narrative, methods and training diagnostics](2026-11-18.md) · [Report index](README.md)

| If you want to know… | Read |
| --- | --- |
| Which crop methods worked, and whether changing gallery coverage explains the difference | [Tables 1–4: cross-dataset and fixed-gallery comparisons](#1-cross-dataset-baselines-and-fixed-gallery-comparisons) |
| Whether the model saw these people during training and whether rejection thresholds transferred | [Tables 5–8: full-gallery evaluation and training exposure](#2-full-gallery-evaluation-training-exposure-and-rejection-thresholds) |
| Whether background masking, depth or a fallback fixed difficult captures | [Tables 9–12: localization and offline Pi replay](#3-localization-failures-fallback-routes-and-offline-pi-replay) |
| How the authors’ result compared with local runs, and whether augmentation helped | [Tables 13–17: reproduction and controlled training comparisons](#4-author-code-reproduction-pose-augmentation-and-crop-free-recognition) |

**Reading the counts:** *Rank-1* asks whether the correct hand ranked first. *EER* is the equal error rate from a threshold sweep; lower is better. *ROI* is the palm region cropped for recognition. A probe that could not be ranked disappears from a rankable-only denominator, but it still counts as a failed attempt in the full planned denominator.

[Follow-up comparisons: crop winding, gallery compatibility, boundary repair, selected white-background examples and the seed-by-seed audit](2026-11-18-follow-up-comparisons.md).

## 1. Cross-dataset baselines and fixed-gallery comparisons

### Table 1. Rank-1 across 10 datasets and 4 crop methods

Correct matches / rankable probes. A dash means no result is reported. Denominators vary with the crop, usable gallery or experimental cohort; do not average the columns.

| Dataset | Recognizer | Reference / existing ROI | PKLNet-v5 | 21-point letterbox | RTM |
| --- | --- | --- | --- | --- | --- |
| MPD / PalmSet | PB | 699/700 | 514/614 | 402/657 | 331/700 |
| MPD / PalmSet | SF2 | 700/700 | 529/614 | 312/657 | 249/700 |
| X-Palm | PB | 117/136 | 76/131 | 82/124 | 77/110 |
| X-Palm | SF2 | 99/136 | 58/131 | 67/124 | 56/110 |
| TCD / Tongji | PB | — | 5,281/5,877 | 4,425/5,993 | 4,465/5,998 |
| TCD / Tongji | SF2 | — | 5,800/5,877 | 4,410/5,993 | 3,685/5,998 |
| 11KHands | PB | 119/120 | 125/134 | 184/185 | — |
| 11KHands | SF2 | 120/120 | 128/134 | 185/185 | — |
| Axon | PB | — | 25/44 | 48/59 | 29/42 |
| Axon | SF2 | — | 29/44 | 53/59 | 24/42 |
| Project captures | PB | — | 59/94 | 50/60 | 61/87 |
| Project captures | SF2 | — | 63/94 | 51/60 | 52/87 |
| Public99 | PB | 486/518 | — | — | 719/814 |
| Public99 | SF2 | 496/518 | — | — | 624/814 |
| SMPD | PB | — | — | — | 248/2,568 |
| SMPD | SF2 | — | — | — | 124/2,568 |
| BMPD | PB | — | — | — | 646/798 |
| BMPD | SF2 | — | — | — | 621/798 |
| BJTU | PB | 366/400 | — | — | — |
| BJTU | SF2 | 380/400 | — | — | — |

**Interpretation:** Localizers can fail on different images from the same dataset. A higher conditional success rate may simply mean the easier queries remained. Table 2 reports verification scores; tables 3 and 4 hold more of the comparison fixed.

### Table 2. Cross-dataset EER, aligned cell by cell with table 1

Values are percentages. PalmSet overlaps with training images; the historical X-Palm test set was used during development; TCD may share a source with training data; Public99 derives from 11KHands.

| Dataset | Recognizer | Reference / existing ROI | PKLNet-v5 | 21-point letterbox | RTM |
| --- | --- | --- | --- | --- | --- |
| MPD / PalmSet | PB | 0.95% | 9.47% | 21.83% | 28.43% |
| MPD / PalmSet | SF2 | 0.16% | 10.59% | 30.52% | 35.14% |
| X-Palm | PB | 10.29% | 20.49% | 17.74% | 20.91% |
| X-Palm | SF2 | 14.11% | 27.32% | 25.00% | 27.27% |
| TCD / Tongji | PB | — | 2.98% | 17.81% | 11.49% |
| TCD / Tongji | SF2 | — | 1.63% | 25.37% | 23.25% |
| 11KHands | PB | 2.55% | 3.73% | 4.14% | — |
| 11KHands | SF2 | 0.83% | 4.20% | 4.32% | — |
| Axon | PB | — | 20.46% | 16.59% | 10.20% |
| Axon | SF2 | — | 22.73% | 11.86% | 19.05% |
| Project captures | PB | — | 27.45% | 13.33% | 24.14% |
| Project captures | SF2 | — | 20.21% | 13.33% | 32.18% |
| Public99 | PB | 5.99% | — | — | 7.62% |
| Public99 | SF2 | 4.99% | — | — | 15.90% |
| SMPD | PB | — | — | — | 42.63% |
| SMPD | SF2 | — | — | — | 45.29% |
| BMPD | PB | — | — | — | 11.15% |
| BMPD | SF2 | — | — | — | 15.44% |
| BJTU | PB | 7.40% | — | — | — |
| BJTU | SF2 | 8.00% | — | — | — |

### Table 3. Paired X-Palm comparison with a fixed gallery

Both methods use the same 131 probes and five gallery templates per hand. This is not the 136-probe reference group in table 1.

| Recognizer | Reference crop: correct | PKL correct | Net change in correct count |
| --- | --- | --- | --- |
| PB | 106/131 | 76/131 | −30 |
| SF2 | 95/131 | 58/131 | −37 |

### Table 4. Unknown-hand rejection on X-Palm at a fixed threshold

The PalmBridge threshold is unchanged. The gallery contains 19 hands × 5 templates; the test includes 124 known and 98 unknown probes.

| ROI | Correct accepts | Wrong accepts (known) | Known rejected | Unknown false accepts |
| --- | --- | --- | --- | --- |
| Reference | 61/124 | 0/124 | 63/124 | 0/98 |
| PKL | 28/124 | 1/124 | 95/124 | 3/98 |
| 21-point | 42/124 | 2/124 | 80/124 | 7/98 |

**Interpretation:** With the gallery held fixed, changing crops cost both PalmBridge and SF2 correct matches. With the rejection threshold held fixed, PKL and the 21-point approach also accepted some unknown hands. Closed-set rank is not an access-control acceptance test.

## 2. Full-gallery evaluation, training exposure and rejection thresholds

### Table 5. Full MPD gallery: include planned queries without usable crops

200 people and 800 planned enrollment images. All three recognizers share the same 771 usable gallery images. The second-session rows are subsets of the full cohort.

| Recognizer | Scope | Planned queries | Correct | Wrong person | Same person, wrong hand | Probe without ROI | Missing correct template |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FlowPalm | All | 15200 | 10321 | 4147 | 10 | 561 | 161 |
| FlowPalm | Second session | 8000 | 4753 | 2773 | 5 | 384 | 85 |
| PB | All | 15200 | 9675 | 4780 | 23 | 561 | 161 |
| PB | Second session | 8000 | 4509 | 3006 | 16 | 384 | 85 |
| SF2 | All | 15200 | 10396 | 4073 | 9 | 561 | 161 |
| SF2 | Second session | 8000 | 4877 | 2649 | 5 | 384 | 85 |

### Table 6. MPD results by prior training exposure, using the same gallery

Groups follow the historical PalmBridge/SF2 training and development lists. Absence from those lists does not establish that FlowPalm pretraining excluded these people.

| Group | People | FlowPalm correct | PalmBridge correct | SF2 correct |
| --- | --- | --- | --- | --- |
| Historical training | 160 | 8203/12160 | 8706/12160 | 8799/12160 |
| Historical development | 20 | 1099/1520 | 564/1520 | 850/1520 |
| Outside both lists | 20 | 1019/1520 | 405/1520 | 747/1520 |

**Interpretation:** Table 5 counts every planned query. Table 6 shows that PalmBridge and SF2 scores drop outside their training group. FlowPalm's pretraining identities are unknown, so the subset does not establish a blind-test winner.

### Table 7. MPD crop-boundary correction: known-hand identification and false accepts

12 people, 48 enrollments and 912 queries. All 5 recovered crops came from the same person, hand, device and session. Unknown-hand false accepts come from a separate four-fold evaluation.

| Recognizer | Strict localization: correct | Correct after correction | Strict: unknown false accepts | Unknown false accepts after correction |
| --- | --- | --- | --- | --- |
| PB | 903/912 | 908/912 | 77/912 | 77/912 |
| SF2 | 898/912 | 903/912 | 159/912 | 164/912 |
| Mobile | 902/912 | 907/912 | 72/912 | 72/912 |

### Table 8. Transferring the same locked rejection thresholds

Score correction has a cost. MPD calibration had only 94 valid scores; X-Palm included only 4 known and 3 unknown people.

| Data | Intervention | Known correct accepts | Unknown false accepts |
| --- | --- | --- | --- |
| MPD | Uncorrected | 1365/1440 | 2/480 |
| MPD | Corrected | 1398/1440 | 0/480 |
| X‑Palm | Uncorrected | 55/104 | 0/78 |
| X‑Palm | Corrected | 75/104 | 3/78 |

**Interpretation:** On MPD, correction admitted more known hands and fewer unknown hands. On X-Palm, it improved correct acceptance but introduced 3 unknown-hand false accepts. Do not carry a single development threshold to a new device without validation.

## 3. Localization failures, fallback routes and offline Pi replay

### Table 9. White-background localization on the same 94 project-capture queries

Only the localizer receives the white-background image. Texture is cropped from the original image. The 54 enrollment images are fixed.

| Recognizer | Localizer input | Correct | Wrong | No output |
| --- | --- | --- | --- | --- |
| SF2 | Original image | 62 | 17 | 15 |
| SF2 | White background | 66 | 20 | 8 |
| SF2 | Repaired white background | 66 | 25 | 3 |
| PB | Original image | 60 | 19 | 15 |
| PB | White background | 58 | 28 | 8 |
| PB | Repaired white background | 60 | 31 | 3 |

### Table 10. Independent white-background comparison: query only vs both sides

The processing pipeline differs from table 9; do not pool their results. The 40 difficult queries are a subset of the 94.

| Processing | All 94: correct / wrong / no output | Difficult 40: correct / wrong / no output |
| --- | --- | --- |
| Original image | 68 / 20 / 6 | 16 / 19 / 5 |
| White background on queries only | 67 / 21 / 6 | 16 / 19 / 5 |
| White background for enrollment and query | 69 / 19 / 6 | 16 / 19 / 5 |

**Interpretation:** With the repaired mask, SF2 failures fell from 15 to 3 but wrong matches rose from 17 to 25. The separate query-only comparison did not improve the difficult 40 cases either. Preserve original-image texture and failure counts: any output is not necessarily a correct match.

### Table 11. Authors' FETC localization: original RGB vs depth preprocessing

Both routes crop from the original. Each cell gives correct / wrong / no ROI; the three counts sum to the planned queries.

| Data | Recognizer | Queries | Original RGB | Depth |
| --- | --- | --- | --- | --- |
| Project captures | sf2net | 94 | 52 / 0 / 42 | 47 / 0 / 47 |
| X‑Palm | sf2net | 136 | 69 / 55 / 12 | 60 / 47 / 29 |
| MPD | sf2net | 252 | 51 / 34 / 167 | 24 / 14 / 214 |
| Project captures | palmbridge | 94 | 52 / 0 / 42 | 47 / 0 / 47 |
| X‑Palm | palmbridge | 136 | 73 / 51 / 12 | 65 / 42 / 29 |
| MPD | palmbridge | 252 | 47 / 38 / 167 | 22 / 16 / 214 |

### Table 12. Raspberry Pi 5: offline pipeline replay

Times exclude the camera, interface, network and startup. Access-control false accepts were not measured. Two duplicate source items were excluded from X-Palm.

| Data | Pipeline | Queries | Correct | Wrong | No output | Median (s) | P95 (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MPD | YOLO + PB | 300 | 298 | 2 | 0 | 1.834 | — |
| MPD | RTM + PB | 300 | 156 | 144 | 0 | 0.631 | — |
| X‑Palm | Primary route | 207 | 144 | 43 | 20 | — | — |
| X‑Palm | Primary plus fallback on failure | 207 | 157 | 48 | 2 | 1.636 | 1.886 |

**Interpretation:** Offline runtime is not camera-to-screen latency. The X-Palm fallback added 13 correct matches and 5 wrong ones. Test rejection on new users and actual hardware before enabling it by default.

## 4. Author-code reproduction, pose augmentation and crop-free recognition

### Table 13. Authors' CompNet: X-Palm spread-finger / roll conditions

Both headline figures average three runs. The paper did not publish the corresponding seeds. The local author-code protocol selected models by test EER; this is not an independent blind test. Each run used 38 queries, 38 genuine and 1,406 impostor pairs. Splitting by hand left 22, 30 and 28 people in both training and evaluation for seeds 42, 43 and 44 respectively.

| Source | EER ↓ | Rank‑1 ↑ |
| --- | --- | --- |
| Paper three-run mean | 23.77% | 24.56% |
| Local seed 42 | 34.71% | 3/38（7.89%） |
| Local seed 43 | 34.28% | 6/38（15.79%） |
| Local seed 44 | 40.68% | 5/38（13.16%） |
| Local three-run mean | 36.56% | 12.28% |

**Interpretation:** The mean across three local runs did not match the paper. Test-set model selection, the hand-level split and unspecified paper seeds limit interpretation; no single change explains the gap.

### Table 14. Pose examples and augmentation with fixed spread-finger enrollment

Historical test panel: 14 people, 28 enrolled hands, 27 roll probes and 28 pitch probes. Donor count is not test population size. Arm D also used 64 real recipient images.

| Training condition | Donors | Roll EER | Pitch EER |
| --- | --- | --- | --- |
| A: standard | 0 | 43.62% | 32.14% |
| A: with donors | 4 | 48.7% | 32.14% |
| A: with donors | 8 | 44.17% | 32.14% |
| A: with donors | 16 | 41.02% | 28.57% |
| A: with donors | 32 | 40.74% | 28.57% |
| B: ordinary smooth deformation | 8 | 42.11% | 32.14% |
| C: donor-paired optical flow | 8 | 49.38% | 32.14% |
| D: extra real recipient images | 8 | 44.44% | 34.26% |

### Table 15. Repeated donor selection: 8 people × 3 draws

The evaluation people remain the same; these are not independent test sets. C minus B is measured in percentage points; negative values favor paired deformation over ordinary augmentation.

| Pose | Donor draw | A EER | B EER | C EER | C−B |
| --- | --- | --- | --- | --- | --- |
| Roll | 1 | 44.17% | 42.11% | 49.38% | +7.27 |
| Roll | 2 | 44.44% | 43.48% | 41.84% | -1.65 |
| Roll | 3 | 46.36% | 40.74% | 44.58% | +3.84 |
| Pitch | 1 | 32.14% | 32.14% | 32.14% | +0.00 |
| Pitch | 2 | 28.57% | 28.57% | 32.14% | +3.57 |
| Pitch | 3 | 32.14% | 29.89% | 28.57% | -1.32 |

**Interpretation:** Changing the selected 8 donors reversed the sign of the difference between paired and ordinary deformation. The evidence did not justify scaling up generation on the assumption of a consistent benefit.

### Table 16. Frozen recognizers on the same 27 development probes

14 development participants, 28 enrolled hands. Architectures, training sources and input sizes differ.

| Weights | Roll correct | Roll EER | Pitch correct | Pitch EER |
| --- | --- | --- | --- | --- |
| Tongji ResNet18 | 8/27 | 25.93% | 13/27 | 22.36% |
| MPD IRes18 | 2/27 | 44.44% | 5/27 | 36.49% |

### Table 17. Crop-free whole-hand recognition: corners-only control

In the zero-shot control the corners occupy only 2.04% of the image. The trained model uses a different corner definition; corners may contain part of the hand. Counts are correct / all planned probes.

| Input | Project captures | X‑Palm | MPD |
| --- | --- | --- | --- |
| Zero-shot: full frame | 56/94 | 77/136 | 33/252 |
| Zero-shot: corners only | 33/94 | 34/136 | 5/252 |
| Trained: corners only | 40/94 | 42/136 | 14/252 |

**Interpretation:** Some queries still matched correctly with only the corners visible. These may retain hand pixels or reveal background cues. Correct whole-hand identification does not prove that the model relied on palmprint texture. Control the background and use new people and devices.

**Evidence:** Corrected 16 November cross-dataset summaries and fixed-gallery/threshold records; 17–18 November full MPD gallery and exposure groups, crop borders and rejection, paired white-background and FETC analyses, offline Pi runs, three CompNet seeds and pose experiments. Only aggregate results are included; no identities, individual scores, palm images or weights are provided.
