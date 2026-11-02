# Registration diagnostic attribution — 2026-11-02

Added opt-in scalar diagnostics to similarity registration and a shared resource
boundary for the two bounded CPU drivers. Synthetic tests verify unchanged
registration outputs, enrolled scores and Gallery decisions. No real-image
experiment, model inference, recognition improvement or speedup is claimed.

## Preserved work and execution scope

Before edits, the original task and old bridge were idle; no competing project
Python/PowerShell worker or supervisor was found. Available RAM was 12.2679 GiB
at 07:25:49 UTC. This task performed only source work and lightweight synthetic
tests, not a resource-gated image experiment.

The previously untracked morning drivers and [morning report](../cpu-bounded-followup-20261102/REPORT.md)
were reviewed. That report is retained verbatim. Before editing, both drivers
matched their archived `executed-driver.py` exactly:

| Driver | SHA-256 of the actually executed morning source |
| --- | --- |
| `pilot_gallery_lifecycle.py` | `26306871328515d857ae6b3afdfb07f2a19f1808ae1395f4dfd3e9ac2b16e8d7` |
| `audit_global_sift_geometry.py` | `1bfc7bd279caccfdca01918bcc6f3ca0fe61177b12c6cb19803713461ca22006` |

The archived drivers, their private protocols/results and original data were not
changed. The edited working-tree drivers are newer, unexecuted versions. Their
new helper and registration-source hashes require a new prospective protocol
before any future authorized experiment; no historical protocol is rewritten.
The failed global-query/existing-ROI SIFT combination remains retired.

## New attribution

`registration(left, right, diagnostics=trace)` returns the same matrix or `None`
as the ordinary two-argument call. The mapping is caller-owned, reset per call,
and records schema, last reached stage, outcome, reason, counts and scalar
geometry measurements. It contains no images, descriptors or identity labels.
Nothing logs or selects an ROI automatically.

| Stage | Recorded rejection information |
| --- | --- |
| Descriptor count | Insufficient query/enrollment descriptors; both counts |
| Correspondence | Insufficient mutual ratio matches; matched-pair count |
| Similarity fit | Missing transform or nonfinite transform |
| Inlier count | Insufficient inliers; inlier count |
| Geometry | Coverage, scale and angle; every failing geometry gate |

Unreached measurements remain null. An exception retains the last stage,
records its exception type, keeps the rejection reason null and is re-raised
unchanged. The observational driver preserves that incomplete diagnostic in
its private failure report with `accepted=null`; it does not turn it into a
measured rejection. A successful registration remains distinct from subsequent
sampling bounds and from recognition acceptance.

The morning 220 failed registrations contain only the old combined
`existing_correspondence_or_geometry_gate` reason. Their true substages remain
unknown. No retrospective inference, relabeling or rerun was performed.

## Resource boundary

Both bounded CPU drivers now call `experiment_resource_limits.resource_fault`,
including the lifecycle sampler. The authorized byte boundaries are:

- Startup available RAM >=12 GiB.
- Running available RAM >=2 GiB.
- Worker RSS <=14 GiB; exactly 14 GiB is allowed, one byte more fails.

The former two driver implementations already used `rss > 14 GiB`. Sharing
their implementation removes ambiguity without loosening their behavior or
changing RAM, wall-clock, STOP or recognition thresholds. This is not a change
to archived protocols or a recovery of the blocked GPU environment.

## Verification

24 targeted synthetic tests passed. Coverage includes each rejection stage,
multiple simultaneous geometry failures, unchanged exception propagation,
unmeasured/null fields, and a real OpenCV fit on hand-authored point/descriptor
arrays. Existing matcher score aggregation and production Gallery MATCH,
UNKNOWN and RETRY decisions are identical with diagnostics enabled or disabled.
No image feature extraction, neural model or real enrollment gallery is needed.

An AST audit compared the numerical registration core with commit
`2d49e2e389a094a720e711daeef7d6ee4a8ef36b`. After removing only explicit diagnostic
blocks and normalizing the internal function name/optional argument, the trees
match exactly. Canonical AST SHA-256:
`8e8b6798f1f93365420b34bb1f3c4534821630a742d01238ed40dfd9e83441b1`.
All original ratio, RANSAC seed/settings, inlier and geometry limits remain.

Private JUnit output is `runtime/registration-diagnostics-20261102-r1/tests.xml`.
The sanitized `verification.json` records test and unchanged historical-result
hashes. No synthetic test establishes real-device score parity, full168
preservation, repeated gallery lifecycle stability or Pi latency.

GPU installation remains blocked by the previously observed sandbox temporary
wheel write/cleanup access denial. It was not retried, rerouted or repaired in
this task. SMPD remains paused at 1239 queries. The next useful evidence must
come from a separately justified mechanism and prospective protocol; additional
logging is not an accuracy result.
