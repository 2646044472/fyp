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

## Real Pi non-overlapping request timing

Completed all 26 preregistered requests: four wrong queries, 18 correct queries over 2.5 seconds in the frozen baseline, and one lexicographically fixed fast correct control per case. All 26 preserve final status, identity, full-precision best/second scores and recognition route exactly. This is instrumented selected-query analysis, not a new full168 latency/accuracy evaluation. A baseline-over-budget request measured 2.496 seconds this time; that run variation is not an algorithm improvement.

Each wrapper tracks its calling thread, parent, inclusive interval and **exclusive time after subtracting same-thread children**. The sum of request-thread exclusive nodes reconciles to the request root for every request; the difference to HTTP wall clock is recorded separately. Worker roots have separate thread IDs, can overlap the request thread, and are never added to its wall-time partition. Call counts, candidate identities and template-frame counts are saved per request. This avoids the old error of adding inclusive localization, feature and gallery times together.

For the slowest request `20261020T165604274940Z-f7ec5fe1`:

- HTTP 15,201.89 ms = request root about 15,200.81 ms plus about 1.08 ms outside it.
- Top-level capture/extract 1,113.574 ms and gallery 14,086.775 ms are siblings. They are inclusive categories; do not add them again to the leaf partition below.
- Non-overlapping request-thread attribution: all localizer calls 4,922.39 ms (32.38% of HTTP), fallback feature extraction exclusive 3,454.22 ms (22.72%), full identity matching exclusive 5,107.53 ms (33.60%). Remaining time is in early scoring, context features, I/O and other recorded nodes.
- Actual calls: 8 localizer evaluations, 7 retained hypothesis-feature jobs, 6 complete identity scores and 30 pair comparisons (six identities times five enrollment frames). Other candidates can be rejected by the existing anchor guard; counts are actual, not invented from maximum configured views.

Full-gallery initialization/ready costs, excluded from timed queries and explicitly retained: new original 17.987 s, new reverse 16.687 s, old original 30.447 s, old reverse 31.711 s. No fresh on-site enrollment timing claim is made. All power statuses stayed 0x0. Model SHA readbacks match frozen PKLNet `bf477f1778f03ccc203b64dd0c84d418c9bb22839a23ba923f479ab991aa067f` and CompNet `b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea`.

Evidence: `protocols/PI5_EXCLUSIVE_TIMING_TREE_20261030.json`, evaluator source SHA `f9a46890deedc3d574118407f6b1a9b8261561d73de250a91e2a6c3cd99f88d0`, source commit `4745dc1499c8ccce3164c4184ce280d31847c599`.

## Known-true-candidate optimistic cost diagnostic

Mechanically selected all four wrong queries plus the global slowest query. Supply the known true identity only to the scoring step, skip retrieval/early-gallery search and other identity scores, but preserve original capture/localization, exhaustive feature generation, existing geometric guards and all five true enrollment-frame comparisons. Each request makes exactly five pair calls, and the resulting true-identity aggregate matches the original full-gallery true score **exactly in all five cases**. Final threshold/margin are unchanged. The changed route and supplied truth make normal response parity intentionally inapplicable; a forced true MATCH is not recognition success.

| Query suffix | Frozen normal-gallery HTTP | Known-true-candidate HTTP | True score parity | Main remaining cost |
|---|---:|---:|---|---|
| a4677ec5 | 4.344 s | 3.035 s | exact | localizer 1.078 s + fallback features 1.671 s |
| f7ec5fe1 | 15.225 s | 9.794 s | exact | localizer 4.938 s + fallback features 3.453 s + five-frame match 1.224 s |
| 37d0c433 | 8.081 s | 3.938 s | exact | localizer 1.138 s + fallback features 1.981 s |
| 61f30739 | 10.257 s | 4.173 s | exact | localizer 1.133 s + fallback features 1.994 s |
| 8d6441d2 | 9.397 s | 3.919 s | exact | localizer 1.134 s + fallback features 1.900 s |

All five remain over 2.5 seconds even after removing the retrieval problem. Therefore candidate pruning alone cannot meet the target for this frozen exhaustive path. This is an optimistic cost diagnostic for the existing path, not a lower bound on every redesigned algorithm. It points to lowering query localization/feature cost and true-candidate verification cost before attempting a broader 40-person gallery optimization.

To stay within available Pi storage, the oracle runtime copies only the preselected true-identity template files and separately copies writable databases. In the old-original case the prepared store contains the two preselected true identities for its three requests, but each request evaluates just its supplied true identity. Initialization/ready is recorded separately: 2.407 s, 4.536 s and 7.800 s for the three cases. It is not credited as a normal-gallery speedup. No source templates, production service or original images are changed, and no simulated charge is confirmed.

Evidence: `protocols/PI5_ORACLE_CANDIDATE_COST_20261030.json`, including evaluator SHA, actual five-pair counts, exact expected/observed true score and the full request timing tree.

## Outcome and stopping criteria

No new production algorithm or thresholds are adopted. The anatomical oracle has mixed outcomes and one retained unavailable image; the known-true cost diagnostic fails the 2.5-second budget in all five hard cases. A full168 candidate replay would not validate a new successful mechanism here, so it is not repeated. Frozen normal-gallery figures remain **164 correct accepts, 4 wrong accepts, 0 rejects; 146 correct within 2.5 seconds; P50 1.540 s, P95 6.019 s, maximum 15.225 s**. Historical 170-query reports retain their old denominator and are not pooled with this cohort.

No exact score lower-bound search is introduced. Knowing that an identity score is the mean of its lowest two frame distances does not give a useful positive lower bound while two unexamined frames may both have distance zero. FastCC masks, denominators, spatial shifts and multiple-transform minima must be accounted for before any exact pruning proof. No heuristic or per-ID pruning is hidden in these diagnostics.

Verification: real Pi original-pair parity 8/8; full-gallery instrumented output parity 26/26; optimistic true-score parity 5/5; source-template hash invariance in all runs; three focused timing-tree tests pass (nested exclusive accounting, separate parallel worker roots, exception cleanup). Raw images, feature codes and templates are not pushed. The 2.5-second accuracy/speed target and independent unknown-person rejection remain unresolved.
