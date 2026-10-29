# Pi ROI oracle and rejection/cost diagnostics — 2026-10-30

## Scope and frozen controls

Experimental analysis only; production service and frozen v26 templates remain unchanged. Preserve threshold 1.0 and min_margin 0. No public CASIA/PalmBig evaluation images are used. This is exposed development data, not independent validation.

The six fixed queries are all four wrong v26 queries plus the lexicographically first correct query in each original-device case. True and competing identities each use the **first protocol enrollment frame**, never a frame chosen by its matching score. Correct controls use the lexicographically first other identity as competitor. These two-candidate, single-frame distances cannot be reported as whole-gallery recognition accuracy, best-two enrollment accuracy or normal HTTP latency.

## Locked position/scale oracle

Randomized anonymous thumbnail IDs were annotated without matching scores shown. Earlier analysis had exposed these samples, so this is score-independent annotation, not a claim of independent double blinding. Before running the matcher, lock SHA was `6b3e53f2edf72711539503bc465d2ae71916da49069a0470811fc005a9f0f889`.

The same rule applies to every image: mark index/middle and ring/little interdigital valleys A/B and wrist direction W; square side 1.05 times distance(A,B); center at their midpoint plus 0.65 times that distance toward the wrist, perpendicular to AB. Preserve the original corner orientation/chirality by nearest centered normalized corner ordering. This investigates location/scale; it cannot correct an original 90/180 degree orientation error. No retry, alternative rule or score-guided landmark adjustment is allowed. One of 17 images lacked reliably visible required anatomy and remains unavailable; 46 of 48 planned pair cells ran. This missing cell pair belongs to a correct-control competitor, not a removed error.

Other original query hypotheses remain frozen. Changing the primary anchor can change their anchor-overlap eligibility, as required by the unchanged matcher. Geometric visibility, original/oracle overlap, areas, actual returned matrices, RANSAC inlier coverage and winning branches are saved in the scalar artifact. A finite transform alone is not counted as a successful winning registration; inspect the accepted scoring branch and aligned region.

## Actual Pi oracle results

All eight original-query/original-enrollment error-pair distances exactly reproduce the frozen diagnostic source. Source template hashes remained unchanged; all recorded power samples are 0x0. The oracle is never written into the stored gallery.

Each cell below is **wrong first-frame distance minus true first-frame distance**; positive favors true. OO = original query/original enrollment, AO = anatomical query/original enrollment, OA = original query/anatomical enrollment, AA = anatomical on both sides.

| Query suffix | OO | AO | OA | AA | Interpretation |
|---|---:|---:|---:|---:|---|
| a4677ec5 | +.024036 | +.035296 | -.006696 | +.026686 | The first true frame already wins OO; the real gallery error depends on the five-frame/best-two aggregation. Enrollment-only oracle makes this diagnostic worse. |
| 61f30739 | -.002993 | +.045119 | -.017578 | +.001953 | Query position/scale is a useful mechanism lead; changing enrollment alone hurts. |
| 8d6441d2 | -.010372 | -.026210 | -.003528 | -.034073 | None of the four locked cells favors true; this rule does not solve this failure. |
| 37d0c433 | -.013398 | +.008064 | +.007183 | +.009482 | Both sides influence the score; query-only changes the ordering in this limited comparison. |

All error-cell winners are fixed pose comparisons inside `legacy_v2`, with no improving legacy alignment call. Thus the observed flips are not successful registration rescue. The old correct control stays ahead in all four cells; its true distance changes .247984 -> .232863 on AA. The new correct control's true comparison remains strong, but its competing anatomical enrollment is unavailable and is not counted as a pass. No full-gallery correction or performance gain is established. The mixed results reject a blanket replacement of every ROI by this square.

Machine-readable scalar evidence: `protocols/ANATOMICAL_ORACLE_20261030.json`. Private original images and thumbnail sheets remain ignored and are not uploaded.

## Fixed-gate pseudo-unregistered results

Actual Pi HTTP, six fixed queries in each removal mode; threshold remains 1.0 and min_margin remains 0. Entire physical person removal includes both hands through the frozen alias map. Same-hand-only removal retains the other hand and is a separate group, not a stranger test. Each of ten removal groups initializes a fresh matcher and a copied/pruned runtime; no full-gallery index survives from another group. The scorer asserts that actual candidate IDs exactly equal the retained store. Original templates remain hash-identical. Tokens were canceled; no confirmations or charges were made.

| Gallery condition | Queries | Correct hand accepted | Wrong identity accepted | Rejected | HTTP P50 / P95 / max |
|---|---:|---:|---:|---:|---|
| Frozen normal gallery, full168 | 168 | 164 | 4 | 0 | 1.540 / 6.019 / 15.225 s |
| Whole physical person removed, selected development queries | 6 | 0 | 6 | 0 | 8.312 / 16.144 / 16.361 s |
| Same hand removed, other hand retained | 6 | 0 | 6 | 0 | 8.240 / 15.952 / 18.086 s |

For example, whole-person-removed billy:right returns bankey:left with best .3876953125, second .3878370715725806, gap .00014175907258062725, status MATCH. Same-hand-only billy:right returns billy:left. Both outcomes are retained as failures for the hand identity task; the latter is explicitly not an unseen-person observation.

This agrees with the source policy: final acceptance checks score against 1.0; the margin check is inactive at 0. Internal .32/.08 early-return gates control search, not the final unknown-person decision. Searching longer can therefore still end in a weak MATCH. This experiment diagnoses the frozen behavior and does not calibrate or modify rejection. Six exposed queries cannot establish population FAR, confidence intervals for deployment, or independent generalization.

Ten fresh initialization/ready operations total 229.781 s and are reported separately from HTTP query times. First versus subsequent requests within each group are identified in the JSON. Removed galleries alter retrieval, index preparation and early-return opportunities, so their latency is not an estimate of a speed optimization. Every power sample remained 0x0.

Scalar evidence, including all final best/second/gap/status and the retained/removed identity lists: `protocols/PSEUDO_UNREGISTERED_20261030.json`.
