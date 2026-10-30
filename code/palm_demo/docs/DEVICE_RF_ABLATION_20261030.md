# Uniform receptive-field support ablation — prospective protocol

This experiment follows the verified v26 + retained FastCC Windows reference (165/168 correct, three wrong, zero rejection). The previous contour candidate remains rejected and is not changed or rerun. Standard, production, original images/labels, enrollment frames and thresholds stay frozen.

The corrected observational replay selected seven queries mechanically before new scoring: all three errors, slowest correct, the query previously corrected by evidence retention, first correct exhaustive query and first timely correct in the errors' case. It reproduced every full-gallery score/HTTP decision exactly. All **8,081 ordinary FastCC calls** have known query and target provenance; all traced source support equals the same fully supported 17x17 filter footprint (784 of 1,024 sampled positions). Zero unknown query/target calls, zero extra unsupported interiors and zero missing-warp records. Initial instrumentation omitted calls compiled under the retained-evidence helper's synthetic filename; its result and exact source are preserved, then tracing coverage alone was repaired. Neither recognition nor geometry changed.

Original/normalized query and all five true/wrong enrollment frames were also rendered and reviewed. A first gray-before-warp reconstruction did not reproduce stored codes and was excluded as pixel evidence. The corrected atlas uses the unchanged PKLNet RGB/BGR sampling path; all 30 displayed enrollment instances reproduce their stored base binary codes exactly. Those private images are exposed development diagnostics, not anatomical ground truth.

Mechanism: artificial filter padding can contribute unusually favorable agreements for a wrong identity. The geometric audit establishes sufficient support in actual crop interiors. Test **one uniform distance change**: compare only code locations whose complete 17x17 receptive field lies inside each 128px crop, with the actual valid-overlap denominator for each of the existing 81 shifts. Do not drop black source pixels, choose a mask/shift using identity labels, change feature extraction, poses, five-frame best-two aggregation, gallery identities, registration guards, CompNet or quality metrics. The ordinary FastCC replacement applies to the shared base matcher in every stage, including both sides of retained evidence; no old/new ordinary distances are mixed. This is a new metric, not an exact acceleration.

Preconditions: completed seven-query observational audit with exact reference parity and complete geometric support provenance; fixed source/model/template hashes. The isolated kernel must equal the exhaustive valid-bit shift oracle, already tested on random binary arrays and padding cases. The normal .32 distance / .08 margin early gate and final 1.0 / 0 gates remain unchanged; rejection stays off.

Pilot: same seven original-image HTTP queries, all identities and five frames in their original galleries. Fresh isolated writable databases, immutable enrollment links, explicit actual v26 class and shared-base checks. Compare identities to the unmodified reference. Do not count the instrumented observational durations as baseline timing. The pilot is not a fresh-enrollment test or proof of acceleration.

Pass requires at least one genuine wrong-to-correct transition, zero previously-correct losses (wrong/rejected/processing failure), intact originals/templates and unchanged isolated transaction counts. Otherwise reject without parameter or threshold scanning. Only a passing pilot permits full168 paired reference/candidate regression, with fresh enrollment, all payment guards and separate startup/ready/query cost accounting. A Pi performance/adoption claim additionally requires Pi regression; no deployment is authorized by this experiment.

The fixed seven-query pilot completed: five correct, two wrong, zero rejection/processing failure, one genuine correction (`37d0c433`) and zero loss of the four previously correct controls. Both xyt queries remain wrong and return different wrong identities; this is explicitly not a solution for them. No parameter changed after the pilot. Full168 verification proceeds by running the candidate with fresh enrollment against the existing immutable full168 reference first. Any previously-correct loss disqualifies it, without running a redundant fresh timing control. Only a surviving candidate proceeds to a new fresh standard arm for the paired timing/pipeline qualification. This execution order is fixed before full168 candidate outcomes; no speed claim is made from the instrumented audit or pilot.

## Completed full168 paired Windows result

The fixed candidate completes all four cases with **166 correct, two wrong accepted, zero rejection and zero processing failure /168**. All 165 reference-correct queries remain correct. `37d0c433` genuinely changes from kss-left to cyw-left; both xyt errors remain wrong and are preserved, including changed wrong competitors. No tuning or sample removal follows these results.

The new fresh standard arm completes all168 with **165 correct, three wrong, zero rejection/failure**, and exactly reproduces the prior standard's full-gallery scores, status, identity and route on **168/168**. Each arm independently executes 34 five-frame enrollments, all ready, and passes confirmation/balance, duplicate-confirmation block, cancellation and canceled-confirmation block in every case. The candidate's 34 stored feature arrays exactly equal the original standard arrays; only distance interpretation changes.

| Windows metric | Fresh standard | RF candidate |
|---|---:|---:|
| Correct / wrong / rejected | 165 / 3 / 0 | **166 / 2 / 0** |
| Correct within 2.5 seconds | **158/168** | 156/168 |
| P50 seconds | .719 | .741 |
| P95 seconds | **3.246** | 4.616 |
| Maximum seconds | **7.290** | 7.580 |
| Five-frame enrollment HTTP P50 seconds | 11.249 | 11.583 |
| Last-frame-read end to ready response P50 seconds | 4.345 | 4.471 |

Case-correct counts, standard → candidate: new original 29→29/29; new reverse 29→29/29; old original 52→53/55; old reverse 55→55/55. Candidate timely counts are 27,28,49,52; fresh-standard counts are 29,28,49,52. Startup, immediate-after-enrollment and complete-gallery first queries are separate in the summary.

This passes the predeclared **accuracy** criterion, not a demo replacement/speed criterion. The latency regression has a concrete routing mechanism: two previously correct new-original queries (`13cf34d4`, `2239e833`) move from enrollment-link/pooled confidence to exhaustive search. Against the original reference they take .839→7.104 s and 1.227→7.508 s; exact fresh-standard decisions/routes reproduce that reference. The metric changes the confidence distribution even though gates stay fixed. Do not relax thresholds on these cases to hide the cost. The next distinct hypothesis is preserving old confident early paths and computing the new independent distance only for genuinely uncertain terminal evidence; it has not been implemented or validated, and old/new distances must never be minimized together.

All three complete runs are sequential Windows epochs, with candidate then fresh-standard order fixed before full candidate outcomes. They are not randomized interleaved trials or Pi timing. Live acquisition, new-session generalization, stranger rejection and 40-person scaling remain unmeasured. Pi was verified read-only over Wi-Fi with zero throttle flags; the candidate was not deployed or run on Pi. The original Pi reference remains 165/168, not 166/168.

The candidate stays experimental; frozen standard and official service remain unchanged. All raw photo/ROI atlases and templates remain private. [Full scalar report](experiments/device-rf-full168-20261030/report.html), [summary](experiments/device-rf-full168-20261030/summary.json), [504-row ledger of original standard, candidate and fresh standard](experiments/device-rf-full168-20261030/decisions.csv).
