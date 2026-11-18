# Seven-person device evaluation, 2026-10-29

Frozen matcher: `FastCCQualityEvidence-v24-experimental`, source snapshot
`0eb9679af7332820bd050c8ddd35e6df80468e9d` plus SHA-pinned evaluation tools.
No recognition code, weights, thresholds, candidate rules or labels changed.
Pi 5 connected through Wi-Fi at 192.168.31.55. Production and real accounts
were not modified. Only isolated simulated payments were exercised.

## Data and protocol

*The participant-linked evidence for this section is retained locally.*

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

*The participant-linked evidence for this section is retained locally.*

Diagnostic replay of five errors and four controls exactly reproduced identity,
scores, route and ROI bytes. A second feature-tracing run reproduced all five
errors again. Its per-registration-call counts below are overlapping attempts
across regions, scales and enrollment frames, not independent image counts.

*The participant-linked evidence for this section is retained locally.*

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

*The participant-linked evidence for this section is retained locally.*

Private exact evidence: `geometry-diagnostics.json`; command option
`tools/diagnose_frozen_device_errors.py --wrong-only --geometry-details`.
`tools/build_device_failure_evidence.py --geometry <complete-export>
--include-slowest` also creates a sheet for the slowest query without rerunning
recognition. Historical metrics above are unchanged.

*The participant-linked evidence for this section is retained locally.*