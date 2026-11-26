# 18 November 2026 | Follow-up experiments: what actually changed?

Five controlled comparisons revisit earlier findings without pooling unlike populations. A correct result means the right person **and** hand. Failure to produce a query and failure to enroll its true hand are kept separate where the protocol distinguishes them. The [main results ledger](2026-11-18-experimental-results.md) covers the broader 17-table benchmark.

## 1. Does correcting crop winding fix the MPD gap?

These are the **same 252 planned probes** and the same 35 usable enrollment images out of 36 planned. Both localizers use original RGB sampled at 224 pixels. A probe unavailable in either paired arm stays unavailable in all rows. The winding diagnostic changes orientation handling in the PKL crop; it is not an independent third detector.

| Recognizer | Crop | Correct | Wrong person | Same person, wrong hand | Unavailable in pair | True hand absent |
| --- | --- | --- | --- | --- | --- | --- |
| Flow filter | RTM | 224 | 6 | 0 | 17 | 5 |
| Flow filter | PKL | 184 | 44 | 2 | 17 | 5 |
| Flow filter | PKL winding control | 184 | 44 | 2 | 17 | 5 |
| PalmBridge | RTM | 207 | 15 | 8 | 17 | 5 |
| PalmBridge | PKL | 186 | 43 | 1 | 17 | 5 |
| PalmBridge | PKL winding control | 158 | 54 | 18 | 17 | 5 |
| SF2Net | RTM | 209 | 16 | 5 | 17 | 5 |
| SF2Net | PKL | 176 | 54 | 0 | 17 | 5 |
| SF2Net | PKL winding control | 162 | 52 | 16 | 17 | 5 |

Winding correction alone did not explain the gap. It changed no Flow outcomes in aggregate; PB and SF2 lost correct matches and produced more wrong-hand matches. Retain the original geometry baseline and inspect orientation together with position and scale.

## 2. Is the X-Palm frame calibration helpful when enrollment stays unchanged?

The subject-balanced calibration used **1,289 training rows from 66 people**. At development evaluation, the gallery membership was held to the same 117 usable images. The gallery pixels could remain from the previous crop or be rebuilt using the calibrated crop. Known probes: 140 planned; unknown probes: 109 planned. “Unknown scored” is coverage, **not** the number correctly rejected.

| Recognizer | Query and gallery | Correct | Wrong person | Wrong hand | No query | Unknown scored |
| --- | --- | --- | --- | --- | --- | --- |
| PalmBridge | Previous crop, previous gallery | 90 | 25 | 2 | 23 | 83/109 |
| PalmBridge | Calibrated crop, previous gallery | 63 | 48 | 2 | 27 | 82/109 |
| PalmBridge | Calibrated crop, rebuilt gallery | 88 | 25 | 0 | 27 | 82/109 |
| SF2Net | Previous crop, previous gallery | 81 | 36 | 0 | 23 | 83/109 |
| SF2Net | Calibrated crop, previous gallery | 35 | 77 | 1 | 27 | 82/109 |
| SF2Net | Calibrated crop, rebuilt gallery | 83 | 30 | 0 | 27 | 82/109 |

PB fell from 90 to 63 correct when calibrated probes met the old gallery, then recovered to 88 when both sides used the new crop. SF2 moved from 81 to 35 to 83. The experiment demonstrates a gallery/query compatibility effect, not a consistent localization gain: both calibrated arms also lost four more known probes.

## 3. Does moving the crop inward avoid false accepts?

MPD development pilot: 12 people, 48 enrollments, 912 planned known queries. The unknown-hand counts come from a separate four-fold run of 912 attempts; they are not additional known-query decisions. Five recovered source images belonged to one hand, device and session. Counts below compare a strict baseline, a corner-adjusted crop, and a rigid shift into the image.

| Recognizer | Boundary rule | Known correct | Known wrong | Known missing | Unknown accepted | Unknown rejected | Unknown missing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Flow filter | Strict | 902 | 5 | 5 | 72 | 835 | 5 |
| Flow filter | Corner-adjusted | 907 | 5 | 0 | 72 | 840 | 0 |
| Flow filter | Rigid shift | 907 | 5 | 0 | 72 | 840 | 0 |
| PalmBridge | Strict | 903 | 4 | 5 | 77 | 830 | 5 |
| PalmBridge | Corner-adjusted | 908 | 4 | 0 | 77 | 835 | 0 |
| PalmBridge | Rigid shift | 908 | 4 | 0 | 77 | 835 | 0 |
| SF2Net | Strict | 898 | 9 | 5 | 159 | 748 | 5 |
| SF2Net | Corner-adjusted | 903 | 9 | 0 | 164 | 748 | 0 |
| SF2Net | Rigid shift | 903 | 9 | 0 | 159 | 753 | 0 |

Both repairs recovered all five known attempts. Only SF2 distinguished the two on unknowns: corner adjustment increased false accepts from 159 to 164; the rigid shift retained 159. This merits evaluation on new hands and sessions, not deployment on the strength of five related examples.

## 4. Did the actual PKLNet locator benefit from white backgrounds in the reviewed examples?

This is a **selected diagnostic**, not a population estimate. Four examples per dataset were chosen to illustrate outcomes in an earlier comparison and rerun using the actual PKLNet path. Only the localization image changed in the white-background arm; recognition always used original texture. The same four probes are reused in every row for their dataset. Cells show **correct / wrong / failed**.

| Selected examples | Recognizer | Reference query crop | PKL on original | PKL on white |
| --- | --- | --- | --- | --- |
| MPD | PalmBridge | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| MPD | SF2Net | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| X-Palm | PalmBridge | 2 / 2 / 0 | 1 / 3 / 0 | 1 / 3 / 0 |
| X-Palm | SF2Net | 0 / 4 / 0 | 2 / 2 / 0 | 2 / 2 / 0 |

For these selected probes, the original and white PKL inputs produced the same correct/wrong counts. The reference crop and PKL crop could still disagree. These eight examples do not overturn the 94-query comparison in tables 9–10 of the main ledger.

## 5. Did the three author-code runs really use the same split?

No. The author-code SF/roll split is randomized by hand. Each run had 38 probes, 38 genuine and 1,406 impostor comparisons. Changing the seed also changed training size, which people overlapped with evaluation, and the checkpoint selected under the test-EER rule.

| Seed | Training images | People in both partitions | Selected epoch | Correct / planned | EER |
| --- | --- | --- | --- | --- | --- |
| 42 | 3768 | 22 | 199 | 3/38 | 34.71% |
| 43 | 3695 | 30 | 100 | 6/38 | 34.28% |
| 44 | 3691 | 28 | 50 | 5/38 | 40.68% |

The three-seed mean remains 12.28% rank-1 and 36.56% EER, versus the paper’s 24.56% and 23.77%. The earlier figure of 22 overlapping people describes seed 42 only. This protocol cannot establish person-disjoint generalization or identify why local results differ from the paper.

### Evidence and next checks

The tables were transcribed from the 18 November paired-orientation MPD summary, X-Palm supervised-frame summary, MPD rigid-recentering summary, actual-PKLNet eight-example replay and three-seed author-score audit. Known- and unknown-role totals were checked separately against their planned denominators. The two small development pilots are not independent test sets. No individual scores or images are published.

Next, freeze the gallery/query crop contract before comparing encoders; retest boundary repair on independent captures; and use a fixed, person-disjoint evaluation before describing a training change as a general improvement.
