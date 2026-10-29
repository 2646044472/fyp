# Bounded affine rescue on Raspberry Pi 5 (2026-10-29)

The two remaining new-camera v12 tail queries needed 15.234 and 15.790 seconds
under two-core USB-powered replay. Uniform-scale/rotation registration did not
produce a sufficiently separated ranking, triggering exhaustive localization
and search. `FastCCAffineEnrollment-v13-experimental` adds bounded affine
alignment for tilted palms after the unchanged v12 early stages.

## Implementation and safeguards

Retain the existing mutual RootSIFT correspondences when computing legacy
similarity registration. Reuse those correspondences for a query-to-template
affine fit only if v12 remains uncertain; do not run another descriptor search.
Correspondences belong to the current query and are cleared even on failure.
No query result or identity is reused across requests.

The additional affine model permits unequal axis scaling and shear, unlike the
older similarity model. It requires six inliers (rather than the similarity
model's four), at least 2% spatial coverage, positive determinant, singular
values in [0.5, 2], anisotropy at most 1.5, and rotation within 40 degrees, in
both directions. It preserves original-image bounds and anchor overlap checks.
FastCC scores are recomputed from the original query pixels. The distance <=
0.32 and margin >= 0.08 routing rule and full fallback remain unchanged.

This is a new geometric hypothesis, not a claim of identical scores to v12 on
rescued images. The routing rules remain uncalibrated for open-set rejection.
Production v6 remains unchanged; v13 is an explicit experimental matcher.

## Same-resource Pi HTTP comparison

CPU affinity 0,1; OpenCV one thread, ORT two threads, native matcher one thread.
Each run includes first and warm passes of 20 images, queue handling and token
cancellation. Stored original images are reloaded and ROI/features recomputed;
camera acquisition and external upload are excluded. Compatible isolated v10
enrollment was copied and payload-verified; fresh enrollment is not measured.

For the two previously difficult queries, warm HTTP latency changed from
15.234 to 2.970 seconds and 15.790 to 2.917 seconds, with correct identities.
Both now use `affine_confident`. A further query changed from indexed search to
affine alignment, reducing 2.539 to 2.261 seconds. All unchanged routes retained
exactly the same user ID, best score and second score as v12.

| New-camera warm queries | v12 | v13 |
| --- | ---: | ---: |
| Correct | 20/20 | 20/20 |
| Correct within 2.5 s | 15/20 | 16/20 |
| Median seconds | 2.160 | 2.180 |
| P95 seconds | 15.262 | 2.977 |
| Maximum seconds | 15.790 | 3.115 |

This is a tail-latency improvement, not a meaningful median improvement. Under
the two-core constraint, localization still dominates some queries. The first
target's initial run spent 2.711 s in capture/extraction and 0.254 s in matching;
the second spent 2.087 s and 0.865 s respectively.

Old-camera warm two-core results remained 20/20 correct, 18/20 correct within
2.5 seconds, median 1.770 seconds and maximum 5.688 seconds. This change does
not solve those old-camera tails.

## Three-core validation and reordered repeat

After clean two-core power monitoring, CPU affinity 0,1,2 and ORT three threads
were tested, retaining OpenCV/native one thread. Both new- and old-camera first
and warm passes scored 20/20. Warm new-camera results: median 1.896 s, P95 2.505 s,
maximum 2.746 s, 19/20 correct within 2.5 seconds. Old-camera results: median
1.484 s, P95 5.195 s, maximum 5.428 s, 18/20 correct within 2.5 seconds.

A second complete new-camera replay shuffled all 20 queries with seed 20261029.
Both passes remained 20/20; warm median 1.902 s, P95 2.495 s, maximum 2.663 s,
19/20 correct within 2.5 seconds. Across the four three-core passes, the first
target ranged 2.394–2.406 s and the second 2.486–2.493 s. This is a narrow margin,
not a worst-case guarantee or attainment of the original two-second goal.
Three-core results include a resource-budget change and must not be presented
as an algorithm-only improvement over the two-core baseline.

All completed runs passed the queued-query and cancellation checks, left
simulated transactions unchanged, and reported zero preflight, per-request and
post-queue power flags. These samples cannot rule out all transients.

## Validation and evidence

187 local tests passed; four optional-dependency skips. The five previously
obsolete tests in `test_existing_pipeline.py` remain excluded. Tests cover
bounded tilt recovery, reflection/scale/shear rejection, clustered matches,
minimum inliers, unchanged confidence gates, correspondence reuse without
descriptor search, and query-local cleanup on failure.

The uncached original/reverse split audit (80 queries) exactly matches the
cached audit's scores and routes. Offline registration caching keys frozen,
SHA-checked descriptors and explicit correspondences; it is confined to the
audit tool and is never a runtime latency optimization. Audit timings are not
HTTP benchmark timings. Repeated development splits are correlated; the
reserved four people were not used for tuning or this audit.

The final forward matcher completed all 224 development splits at 20/20 (112
per camera). Relative to v12, affine rescue avoided 74 exhaustive fallbacks in
2,240 correlated new-camera queries and six in 2,240 old-camera queries, without
introducing additional fallback routes. Those counts support the intended
mechanism on development data, not generalization to unseen sessions. The
reserved cohort remains untouched.

Private evidence is under `runtime/pi5-under2-20261028/`:
`affine-v13-forward/`, `affine-v13-forward-smoke/`, and
`ready-affine-forward-{new,old}-{2core,3core}.json`.
The replay records CPU affinity, thread budgets, OpenCV version, code hashes,
native-library hash and power flags. Every query starts from the original image.

An earlier reverse-affine pilot improved only the first target on Pi; cached
Windows geometry overstated its benefit on the second. The final forward
direction was selected on development data, then frozen for validation. Its
reuse of existing forward correspondences also removes the pilot's extra
descriptor search. Interrupted reverse-pilot split results are not a completed
224-split validation and are separate from final forward evidence.
That reverse-pilot audit was interrupted after 105 cases. Its code snapshot is
preserved in the private tar archive; it is not the final matcher.

The HTML supplement is `runtime/pi5-under2-20261028/affine-rescue-report.html`,
with source evidence hashes in `affine-rescue-evidence.json`.
