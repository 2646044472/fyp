# 18 November 2026 | When does a second crop help?

**Keep the upright crop as the first choice; test the direct box as a fallback when no upright crop is available.** On MPD this recovered all 86 previously unscored attempts, but only 28 of those 86 identified the correct hand. On X-Palm it recovered eight of nine missing known queries, four correctly. These are offline results on previously inspected panels, not evidence that the fallback is safe to use for access or payment.

Two experiments answer different questions. The first changes training while keeping each evaluation crop fixed. The second freezes the recognizers and changes which crop is used. Their scores should not be pooled. “Correct” always means the correct person **and** hand; a missing crop stays in the planned denominator.

## 1. Does training augmentation help on a fixed crop?

On MPD/PalmSet, the 200 filename-prefix subjects were split by person into 158 training, 24 validation and 18 evaluation subjects. Left and right hands are separate recognition classes, but a person's two hands stay in the same split. Training used 12,587 of 12,640 planned images; validation used 1,916 of 1,920. Boxes derived from the supplied marks furnished training crops; evaluation used detector crops from the original RGB image, not the marks.

The recognizer used the first 11 layers of a pretrained YOLO11n detector as an image encoder, global average pooling and a normalized 256-dimensional feature vector. An angular-margin classification head was used during training, then discarded; evaluation ranked gallery images by cosine similarity. Matched runs used the same source images, subject split, initialization seed, optimizer (AdamW) and validation selection rule. **Standard augmentation** applied rotation up to 10° with reflected borders, brightness ×0.85–1.15 and contrast ×0.9–1.1, without flips. A third arm added up to 4% crop-scale jitter with bounded translation to standard augmentation; it did not simulate missing anatomy. All three ran 40 epochs. The selected validation epochs were 30 (960/1,872 probes correct) without augmentation, 35 (1,109/1,872) with standard augmentation and 37 (1,072/1,872) with added jitter. This comparison does not isolate the individual rotation and photometric transforms.

| Evaluation set / crop | Known probes planned | No aug: correct | Standard: correct | Standard + jitter: correct | Became correct / lost correct (none → standard) | No query in each arm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MPD / direct box | 1,404 | 647 | 702 | 775 | 198 / 143 | 13 |
| MPD / square, no rotation | 1,404 | 648 | 775 | 738 | 249 / 122 | 86 |
| MPD / square, upright | 1,404 | 692 | 792 | 831 | 239 / 139 | 86 |
| X-Palm development / direct box | 140 | 71 | 82 | 79 | 33 / 22 | 1 |
| X-Palm test / direct box | 136 | 76 | 74 | 82 | 24 / 26 | 2 |
| X-Palm test / square, upright | 136 | 77 | 77 | 75 | 19 / 19 | 9 |

The MPD gain depended on geometry: +55 on the direct box and +100 on the upright square. Resampling the 18 MPD subjects together with all of each subject's queries gave descriptive 95% intervals of −2.3 to +10.5 and +2.1 to +12.4 percentage points respectively for those changes. On X-Palm, the direct-box development gain did **not** carry over to the test panel. Even the unchanged 77/136 hides 38 queries that switched between correct and incorrect. Adding jitter improved MPD direct-box accuracy from 702 to 775, but reduced the no-rotation square from 775 to 738. A single seed and reused panels do not establish which transform will help on a new device. The split describes the recognizer training, not a claim that upstream pretraining or detector development had no exposure.

## 2. When the upright crop is missing, should we use the direct box?

The **direct box** route takes the predicted axis-aligned palm box on the original image. The **upright** route takes a square from an existing box and uses visible finger-gap landmarks to orient it. The square controls require both geometry and in-frame sampling; the no-rotation and upright versions in the first table share the same eligibility rule. The direct route uses a different detector/crop procedure, so its advantage in coverage cannot be attributed to rotation alone.

For this second experiment, each route used its own enrollment images cropped the same way as its queries. On X-Palm test, these galleries had 152 direct-box and 132 upright images; MPD had 36 in each. The match score was a fixed 50:50 mean of the cosine scores from the augmented YOLO encoder and a frozen DINOv2 encoder with a projection learned on MPD. There was **no** choice based on score, identity or the correct label: use upright when available, otherwise direct; if neither is available, return no result. A low upright score does not trigger another attempt.

| Panel | Crop policy | Correct | Other person | Right person, wrong hand | No query | Planned |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| MPD | Direct only | 785 | 548 | 58 | 13 | 1,404 |
| MPD | Upright only | 876 | 421 | 21 | 86 | 1,404 |
| MPD | Upright, then direct if missing | 904 | 479 | 21 | 0 | 1,404 |
| X-Palm test | Direct only | 91 | 38 | 5 | 2 | 136 |
| X-Palm test | Upright only | 93 | 26 | 8 | 9 | 136 |
| X-Palm test | Upright, then direct if missing | 97 | 30 | 8 | 1 | 136 |

On MPD, the fallback added 28 correct and **58 wrong-person rankings** relative to upright alone; it did not change any previously scored upright answer. On X-Palm test the added rankings split 4 correct / 4 wrong person. No stranger queries were planned on this MPD panel; it cannot measure stranger rejection.

## 3. Would a top-ranked hand actually be accepted?

For each policy separately, the cutoff was fitted on the maximum gallery score of each distinct, scorable X-Palm development stranger image, targeting at most 5% accepted there. The cutoff was then frozen and applied to the test split. Development and test had no shared people or source-image hashes in this audit. **The 5% target is not a measured security guarantee.**

| X-Palm test policy | Known: correct accept | Wrong accept | Rejected | No query | Strangers: false accepts / scored / planned |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct only | 39 | 5 | 90 | 2 | 1 / 112 / 115 |
| Upright only | 43 | 0 | 84 | 9 | 1 / 96 / 115 |
| Upright, then direct if missing | 45 | 0 | 90 | 1 | 1 / 115 / 115 |

The fallback had **97** correct top rankings but only **45** correct accepts out of 136 known attempts. At the stricter development target of 1%, it correctly accepted 35/136, still accepting one stranger attempt. The 115 planned stranger attempts came from only four people and included repeated images (113 distinct scorable images under the fallback). Treating them as 115 independent people would give misleading confidence. A missing query is neither a successful rejection nor a wrong acceptance.

**Next test.** Freeze the crop order, enrollment recipe, score mixture and threshold before collecting an independent session. Compare the fallback with requesting a retake on the same first-frame failures. Count wrong accepts, correct accepts, missing queries and time per decision, not just how many crops came back. Validate latency separately on the Pi; these runs did not measure it.

**Evidence and replay.** The tables use the 18 November matched YOLO-158 training and augmentation receipts, paired correctness summaries, and the coverage-policy audit. The [synthetic policy example](../../research_code/README.md#replay-the-crop-fallback-without-biometric-data) demonstrates the counting rule, not the measured accuracy. No participant data, crops, templates, per-image scores or weights accompany this report.
