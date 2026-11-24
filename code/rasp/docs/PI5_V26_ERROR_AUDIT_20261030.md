# Frozen v26 error audit and conservative speed hypothesis — 2026-10-30

This is development analysis, not a production deployment or independent validation. Preserve v26 rollback, all four errors, original identity labels, scores and existing numerical gates.

## Preregistered speed hypothesis

For any RANSAC inlier subset, its convex-hull area cannot exceed the bounding-box area of all supplied correspondences. If the minimum of the two all-point box areas is strictly below the existing coverage gate (0.02 of 384 squared, with a conservative 1e-6 margin), that estimate cannot pass the current gate. A necessary-condition precheck may avoid an estimator call without changing accepted scores.

The first experiment only observes actual estimator calls, their wall times and these bounds; no calls are skipped. The diagnostic selection is mechanically all four incorrect frozen v26 queries, with no sample-specific algorithm rules. This deliberately selected subset does not estimate population performance.

Kill criteria: reject implementation if eligible estimator time is negligible relative to the multi-second tail; do not run a full replay merely to confirm a negligible upper bound. Any later skipping prototype must preserve scores, identities, route, transforms and ROI parity before considering a full replay. Do not change thresholds, train on these samples or remove failures.

## Diagnostic isolation

Copy each case runtime before initialization/cancel requests. Validate frozen result/code/native hashes and original image hashes. Read existing Pi images only; retrieve scalar diagnostics, not raw biometrics. Record actual RANSAC return values without rerunning the estimator. Instrumented HTTP latency is not a replacement for the frozen uninstrumented baseline. Abort on a nonzero or unreadable power status.

## Actual Pi results

Two complete four-error replays preserved all four statuses, returned identities, scores, second scores and routes exactly. Displayed ROI bytes also matched. Power samples stayed 0x0. No confirm/payment requests were made. Both runs used copied runtimes; production was not selected.

The coverage precheck was rejected before implementing skipping: 4,098 estimator calls per replay, only eight eligible. Eligible estimator wall time by query was 0.033/0.436/0/0.025 ms in the first replay and 0.068/0.316/0/0.025 ms in the second. These are observational upper bounds on savings before precheck overhead, not measured speedups. No full168 candidate replay is justified.

## Winning branch audit

All eight winning wrong-identity enrollment comparisons (two per identity) came from `legacy_v2`, specifically its fixed pose-bank comparison. The actual pose instrumentation shows no legacy aligned-score call for these eight winners. Thus an accepted RANSAC warp did not cause these winning scores. A geometrically accepted transform elsewhere in the search must not be mistaken for the decision's winning transform.

Indices below are zero based; angle/scale refer to the fixed query pose around its existing ROI. Lower distance is better. See the scalar JSON for every pose score and the CSV for the frozen response ledger.

*The participant-linked evidence for this section is retained locally.*

The next substantive accuracy experiment must improve anatomical correspondence before expensive gallery search and preserve existing successes. This audit does not claim that change has been implemented. Current frozen performance remains 164/168 correct, 146/168 correct within 2.5 seconds, with a 15.225-second maximum. No unknown-person probes were tested, so these figures do not establish false-accept performance.

Artifacts: `protocols/v26-four-error-ledger-20261030.csv`, `protocols/V26_FOUR_ERROR_AUDIT_20261030.json`. Private images, raw templates and full private traces remain outside Git.

## Full-precision reconciliation follow-up

Executed `tools/audit_frozen_error_scores.py` against the frozen v26 results, complete pose diagnostics, active169 manifest/protocol and all-candidate geometry. All 195 frame distances (30 new-device, 55 for each of three old-device queries) reproduce every recorded identity score exactly using `float(np.mean(sorted(five_distances)[:2]))`. Every selected enrollment frame ID resolves through the original case protocol and geometry. All returned winner and second scores match the frozen response exactly; baseline v26 code hashes match current scoring sources. No distances were recomputed or rounded before comparison.

Pi readback independently confirms native SHA `272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600`, frozen result SHA `f9e9b39a8d37085318dd089309d975acec19ef1b5a826d813ae1f54af8828a09`, and manifest SHA `08a4fa9574f94023057efcf7aa7bee3b1d07625be91c2835ed9dab464a0472c4`; power remains 0x0. The active protocol contains 169 images and exactly 168 query occurrences over four cases. Historical 170-query results are not merged.

`second_score` means the second-ranked gallery identity, not the true identity's score. This explains apparently inconsistent true/second comparisons in abbreviated tables. Full precision:

*The participant-linked evidence for this section is retained locally.*

Sorted position uses stable source gallery order for ties; it is not a claim that a tied score is strictly worse. The JSON retains all ties, all five distances per identity, actual best-two frame IDs, winning branch, pose scores, primary ROI geometry and accepted geometric estimates/coverage summaries. It excludes raw feature codes and image pixels. This is an audit of the existing behavior; no ROI oracle, pseudo-unregistered experiment or new speed improvement is claimed by this follow-up.
