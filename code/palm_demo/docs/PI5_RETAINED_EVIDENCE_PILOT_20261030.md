# Retain previously computed FastCC evidence — accuracy pilot, 2026-10-30

Source audit found that the terminal exhaustive branch recomputes frame scores and returns them independently of the preceding ordinary FastCC `pairs` accumulator. Existing gate traces show one wrong-query example with true identity mean .3084353298611111 before exhaustive fallback and .3876953125 afterward; the wrong identity then wins at .3836000504032258. This is a mechanism lead, not proof that merging fixes the full cohort.

Minimal hypothesis: when all early confidence checks fail, preserve the per-frame minimum of **ordinary FastCC shifted-overlap distances** already obtained from existing pose/accepted-registration/link/affine/pool/proposal paths and from exhaustive search, then keep the existing mean of the lowest two of five. Accepted registration means passing the existing geometric guards, not proven anatomical correspondence. Apply to all identities/frames uniformly. Numerical gates and final threshold=1.0/min_margin=0 are unchanged. CompNet angular distances are never merged. Quality-weighted scores only replace the ordinary accumulator when confident and return before fallback; an explicit guard rejects that separate metric if it were to reach the new terminal branch.

The isolated module pins the original staged source hash, patches only the terminal fallback inside its process, records before/after/merged frame arrays as scalar distances, and never changes production/core source files or enrollment data. Baseline paths remain available via an off-by-default flag. No query/image/person IDs enter the mechanism.

First run all 13 exhaustive queries plus four fixed fast correct controls, compare actual candidate HTTP decisions with frozen v26 and the retained shadow baseline. Pass requires at least one wrong identity to become the correct identity, no previously correct query to become wrong or RETRY, and unchanged fast-control responses. Any new wrong identity or metric mixing kills the pilot; do not fix it with per-sample exceptions or threshold scans. RETRY never counts as correct. Only a passing mechanism pilot justifies full168 regression. All remaining errors, timings and unknown-person limitations stay visible; no production deployment.

## Completed 17-query mechanism pilot

Actual Pi HTTP decisions: **14 correct, three wrong MATCH, zero RETRY**. Frozen selection was 13 correct and four wrong. The candidate corrected suffix `a4677ec5` from the other hand to its true identity, preserving **all 13 previously correct selected queries**, including all nine correct exhaustive cases. The four fast controls had exactly unchanged status, identity, best/second score and route. The other three wrong identities remain wrong; no threshold or sample exception was added after seeing these results.

The corrected query's true identity is .3084353298611111 before fallback, .3876953125 in the standalone exhaustive fallback, and .3084353298611111 after the per-frame merge. Its competing wrong identity stays .3836000504032258. The unchanged .08 early-margin gate still fails, so this correction is not an early-return or speed win. Its measured HTTP time was 4385ms; the slowest selected correct case remained 15082.91ms.

For every exhaustive query, aggregating the candidate's captured `after` frame scores exactly reconstructed every frozen identity score, not just the returned top two. Aggregating `merged` exactly reproduced the candidate whole-gallery scores. No different distance definitions entered the minima, no source template changed, no transaction was charged, and all power samples were `throttled=0x0`.

The mechanism pilot passes its fixed accuracy gate and proceeds to full168 replay. This is a development-cohort regression, not independent generalization evidence. Taking per-frame minima cannot increase an individual distance, but a competing identity can improve more than the true identity; preserved ranking is empirical, not guaranteed. Unknown-person rejection remains uncalibrated. No production deployment was made; this pilot alone is insufficient evidence for replacing the default matcher.

## Completed full168 Pi HTTP regression

The same source-checked candidate ran all four frozen cases in their saved query order, rereading every original and recomputing its ROI/features. Camera acquisition and external upload are excluded. Frozen prepared enrollment is reused; this is not a new enrollment-latency or payment-confirmation test. Pending recognition tokens were canceled and transaction counts did not change.

| Metric | Frozen v26 | Retained FastCC candidate |
|---|---:|---:|
| Correct identity | 164/168 (97.62%) | **165/168 (98.21%)** |
| Wrong MATCH | 4 | **3** |
| RETRY/reject | 0 | **0** |
| Previously correct decisions lost | — | **0/164** |
| Correct within 2500ms | 146/168 | 145/168 |
| P50 HTTP ms | 1540.17 | 1517.425 |
| P95 HTTP ms | 6019.3185 | 5906.6755 |
| Maximum HTTP ms | 15225.00 | 15234.24 |

| Frozen case | Correct before → after | Correct within 2500ms before → after |
|---|---:|---:|
| New camera original enrollment/query split | 28/29 → **29/29** | 27 → 26 |
| New camera reversed split | 29/29 → 29/29 | 25 → 25 |
| Old camera original split | 52/55 → 52/55 | 46 → 46 |
| Old camera reversed split | 55/55 → 55/55 | 48 → 48 |

All **155 earlier-route queries** retained exactly equal identity, status, scores and route. All **13 exhaustive queries** had exact full-gallery reconstruction of the frozen fallback scores from their captured `after` frames; merged frame aggregation exactly matched the actual candidate decision. All 164 originally correct cases stayed correct. All source templates stayed unchanged. Full regression had 338 power checkpoints, all `throttled=0x0`.

The net loss of one timely correct query is suffix `23aa84c8`, 2422.06→2512.22ms. It is an unchanged `affine_confident` route with exactly equal decision/scores, outside the patched fallback. This single historical-baseline-versus-current comparison does not establish a causal latency regression or improvement. No repeat-until-pass timing selection was performed. The newly corrected query took **4305.49ms** in full replay and therefore does not improve the timely-correct count. The worst query is still correct suffix `f7ec5fe1` at **15234.24ms**. This is an accuracy repair, not a long-tail speed solution.

Remaining errors are preserved:

| Suffix | True palm | Returned palm | Wrong distance | True distance | HTTP ms |
|---|---|---|---:|---:|---:|
| 61f30739 | old xyt right | old stephen left | .3740234375 | .3899589573732719 | 10213.17 |
| 8d6441d2 | old xyt right | old kss right | .37472098214285715 | .4058743759600615 | 9293.32 |
| 37d0c433 | old cyw left | old kss left | .345703125 | .37532433144725136 | 7954.62 |

The next accuracy investigation must address those fixed-pose collisions and localization/representation evidence. The five-frame manual ROI counterfactual did not consistently resolve them. The failed geometric-support RETRY rule blocks all four original errors but also eight correct exhaustive queries; it remains rejected. No image, person or hand-specific exception, threshold scan, extra template or public-dataset tuning is introduced here.

Reproducible scalar results, source hashes, per-stage true/competing five-frame distances and full case summaries: [RETAINED_EVIDENCE_PILOT_20261030.json](protocols/RETAINED_EVIDENCE_PILOT_20261030.json), generated by `tools/report_retained_evidence.py`. Execution: `tools/evaluate_retained_evidence.py` with the frozen baseline/manifest, native library and CompNet model arguments; run without `--full` for the fixed 17-query pilot, and only after its fixed pass criterion use `--full`. Both runs use the same candidate helper hash and patch hash. The source helper remains opt-in and only patches the isolated process. Production and the frozen v26 rollback remain unchanged.
