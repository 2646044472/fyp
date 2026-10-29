# Seven-person device evaluation, 2026-10-29

Frozen matcher: `FastCCQualityEvidence-v24-experimental`, source snapshot
`0eb9679af7332820bd050c8ddd35e6df80468e9d` plus SHA-pinned evaluation tools.
No recognition code, weights, thresholds, candidate rules or labels changed.
Pi 5 connected through Wi-Fi at 192.168.31.55. Production and real accounts
were not modified. Only isolated simulated payments were exercised.

## Data and protocol

Active original captures: 170 unique images, seven physical people. The old
camera group contains 110 images / eleven palm identities; the new-camera
group contains 60 images / six palm identities, including billy's new left
and right sessions. Bankey and stephen occur in both device groups. The removed
syr session `20261013T111838871161Z-df3d072b` remains excluded. Public datasets
are neither included nor used for tuning.

Each identity has ten images. Original split enrolls the earliest five and
queries the latest five; reverse does the opposite. Each case starts empty.
No cross-device matching. New-camera is a project grouping: sensor serials
were not saved, and billy's 2592x1944 frames differ from the previous
1920x1080 new-camera frames. Do not interpret it as verified identical hardware.

Saved originals go through the actual HTTP registration, recognition and
simulated confirmation/cancellation handlers. Recognition includes original
reading, preprocessing, ROI, features, registration/search, scoring and local
HTTP response; excludes camera acquisition, positioning and external upload.
Immediate post-enrollment queries and fresh-process startup are separate.
ORT uses three threads; OpenCV/native one, CPU affinity 0/1/2. Power faults
abort the experiment. All 864 baseline power samples were 0x0; all original
image hashes were unchanged. This is a process restart test, not a Pi reboot.

## Frozen results

| Case | Correct | Correct <=2.5s | P50 s | P95 s | Maximum s |
|---|---:|---:|---:|---:|---:|
| New original | 28/30 | 28/30 | 1.861 | 3.460 | 4.833 |
| New reverse | 30/30 | 22/30 | 1.871 | 5.371 | 14.342 |
| Old original | 52/55 | 44/55 | 1.541 | 9.137 | 10.212 |
| Old reverse | 55/55 | 45/55 | 1.536 | 4.267 | 9.486 |
| Combined | 165/170 | 139/170 | 1.564 | 6.012 | 14.342 |

All 170 main requests returned MATCH: five were misidentifications. No UNKNOWN
or RETRY occurred. This is closed-set accuracy, not stranger rejection evidence.
The two splits use different query images; differences cannot be attributed
solely to enrollment choice. Reusing these viewed images is no longer unseen
validation. Eleven or six enrolled palms do not establish forty-person capacity.

All 34 enrollments reached ready; all immediate queries identified correctly.
Simulated confirmation, duplicate confirmation rejection, cancellation and
confirmation-after-cancellation checks passed for all cases.

| Case | Enrollment P50/max s | Immediate query max s | Rebuild after process restart s |
|---|---:|---:|---:|
| New original | 43.814 / 47.188 | 11.333 | 15.081 |
| New reverse | 43.390 / 45.279 | 12.931 | 14.036 |
| Old original | 22.121 / 24.148 | 4.525 | 23.907 |
| Old reverse | 22.591 / 25.095 | 9.489 | 24.967 |

Generic model startup was 1.37-1.40 seconds; first queries after rebuilding
took 1.169/1.849/1.545/1.548 seconds respectively. Enrollment and startup
costs are not hidden inside the main-query median.

## Error evidence

All five errors used exhaustive fallback, not confident early return.

| Query | True palm | Returned palm | True rank | Best/true scores |
|---|---|---|---:|---:|
| 20261029T085720586167Z-7619919c | billy:left | bankey:left | 2 | .379980 / .384766 |
| 20261029T120016111983Z-a4677ec5 | billy:right | billy:left | 2 | .383600 / .387695 |
| 20261013T111553178583Z-61f30739 | xyt:right | stephen-10-13:left | 3 | .374023 / .389959 |
| 20261013T111555214120Z-8d6441d2 | xyt:right | kss:right | 10 | .374721 / .405874 |
| 20261013T111358589224Z-37d0c433 | cyw-real:left | kss:left | 3 | .345703 / .375324 |

The actual Pi query ROI and stored Pi enrollment transforms were inspected.
Enrollment grayscale panels are reconstructed locally using those transforms;
query PNGs are actual Pi output. The two xyt ROIs slide onto palm heel/wrist,
while enrolled ROIs are centered in the palm. Cyw remains within the palm but
has weak/blurred texture. Billy remains within the palm, with weak fine lines,
broad smooth shading and viewpoint changes. Clipping has not been established
as billy's cause. All generated base ROI candidates were retained: there is no
evidence that an overlap guard removed the correct candidate.

Diagnostic replay of five errors and four controls exactly reproduced identity,
scores, route and ROI bytes. A second feature-tracing run reproduced all five
errors again. Its per-registration-call counts below are overlapping attempts
across regions, scales and enrollment frames, not independent image counts.

| Error | Primary/secondary keypoints | Too few descriptors | Too few mutual pairs | RANSAC/geometric rejection | Accepted |
|---|---:|---:|---:|---:|---:|
| billy left | 373/60 | 16 | 171 | 173 | 0 |
| billy right | 39/12 | 82 | 396 | 122 | 0 |
| xyt first | 412/32 | 55 | 356 | 688 | 1 |
| xyt second | 1000/47 | 0 | 218 | 442 | 0 |
| cyw | 354/96 | 0 | 337 | 763 | 0 |

The one accepted xyt registration was to an incorrect identity. No true-target
registration passed. Many keypoints can represent noise or the wrong region.
RANSAC/geometric rejection is not yet separated into inlier count, coverage,
scale and angle; do not assert one specific guard is responsible.

The slowest sample is `20261020T165604274940Z-f7ec5fe1`, stephen:left,
new reverse: 14.342 seconds, including 1.112 seconds capture/extract and
13.229 seconds gallery work. Even full search scores (.358398 best,
.393649 second) fail the .32/.08 early gate. Faster early stopping alone
cannot solve this sample without changing evidence quality or acceptance risk.

The final demo Gallery uses threshold 1.0 / minimum margin 0 after fallback;
weak closed-set evidence therefore still assigns an identity. ROI reliability,
registration quality and unknown/retry policy need separate evaluation. Rejection
must not be counted as correct identification, and relaxing gates cannot be
claimed as an accuracy-preserving speed fix.

## Reproduction and next optimization boundary

Private evidence (ignored):
`runtime/pi5-under2-20261028/seven-person-device-frozen-20261029/` contains
`protocol.json`, `manifest.json`, `results.json`, `diagnostics.json`,
`feature-diagnostics.json`, stored transforms, actual ROIs and `report.html`.
`tools/prepare_device_cohort_evaluation.py` freezes inputs;
`tools/evaluate_six_person_frozen.py` runs the generic case protocol;
`tools/diagnose_frozen_device_errors.py` instruments failures;
`tools/export_evaluation_template_geometry.py` and
`tools/build_device_failure_evidence.py` create evidence panels;
`tools/report_device_cohort_evaluation.py` renders the report.

Preserve this baseline. Choose generic algorithm changes on the original
development protocol, freeze before expanded/public evaluation, and report
accuracy, rejection and latency together with all failures retained. Prefer
fixing observable ROI disagreement and failed alignment evidence over adding
identity-specific branches. These exposed error images can diagnose mechanisms
but cannot provide fresh validation of a subsequent fix.

Original device ZIP/image bytes remain unchanged. Capture-sidecar LF policy and
SHA256SUMS are normalized for reproducible Windows/Linux checkout verification;
checksums include .gitattributes and exclude SHA256SUMS itself.

## Subsequent exact geometry and visual inspection

An additional Pi replay observes the actual outputs of OpenCV's similarity
and affine RANSAC estimators without rerunning them, changing their inputs or
changing any guard. All five query identities, scores, routes and ROI PNG bytes
again match the frozen baseline exactly. This instrumented run is not latency
evidence. True-target calls below include only labeled fallback attempts that
actually reach an estimator; calls with fewer than four mutual pairs do not.

| Error sample suffix | True-target estimator calls | Too few inliers first rejection | Coverage first rejection | Maximum inliers |
|---|---:|---:|---:|---:|
| 7619919c | 31 | 31 | 0 | 3 |
| a4677ec5 | 14 | 14 | 0 | 2 |
| 61f30739 | 66 | 65 | 1 | 4 |
| 8d6441d2 | 43 | 43 | 0 | 3 |
| 37d0c433 | 73 | 73 | 0 | 3 |

Thus 226/227 traced true-target estimator calls first fail the existing inlier
minimum, not merely an angle/scale limit. Similarity needs four inliers; affine
needs six. The one four-inlier xyt attempt covers only 0.0024375 of the
384-square frame (required .02), with scale .4719 and angle -46.07 degrees.
Multiple guard violations can coexist; do not sum overlapping violation counts
as independent failures. This does not justify relaxing the guards.

All five sheets were actually opened and inspected alongside the true and
predicted enrollment ROIs. The xyt two crops visibly include the wrist/heel
and background unlike centered enrollment crops. Billy's images have marked
viewpoint changes and broad smooth shading; the left query samples nearer the
finger bases than some enrollment frames. Cyw stays on-palm with visible main
creases but weak fine detail. These observations are clues, not a proof of
motion blur, sensor failure, or one exclusive cause. Bright appearance alone
does not establish pixel saturation.

Private exact evidence: `geometry-diagnostics.json`; command option
`tools/diagnose_frozen_device_errors.py --wrong-only --geometry-details`.
`tools/build_device_failure_evidence.py --geometry <complete-export>
--include-slowest` also creates a sheet for the slowest query without rerunning
recognition. Historical metrics above are unchanged.

The user subsequently explicitly deleted `20261029T085720586167Z-7619919c`
after inspecting its strongly oblique original. It is removed from the Pi's
active collection and re-exported active left-session ZIP; remaining image
bytes are unchanged. Current active originals total 169. This post-result,
user-directed dataset change is not an algorithm improvement; the 170-query
baseline and its errors remain historical evidence. A new cohort protocol
has 29/29 new-camera and 55/55 old-camera queries (168 total); it has not been
rerun and has no new accuracy or latency result yet.
