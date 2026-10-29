# Six-person local capture evaluation, 2026-10-29

The user paused algorithm optimization and requested experiments on all six
people shown in the local collection. Recognition code is frozen at the state
of `4b0ee17517354647a77d09b1bd771f4cf52e7604`, with file hashes saved before
the first result. Matcher: `FastCCQualityEvidence-v24-experimental`. No model,
threshold, candidate coverage, ranking rule or geometric constraint is tuned
using this evaluation. Production v6 and real accounts remain separate.

## Data and labels

Use all twelve original ZIPs in `code/data/pi-captures-2026-10-15`, totaling
120 distinct original JPEGs and six subject labels: bankey-10-12, stephen-10-13,
cyw-real, kss, xyt and syr. Each has 20 images. The confirmed correction changes
the ten images from session `20261013T111838871161Z-df3d072b` from syr:left to
syr:right. Both syr sessions therefore form one right-hand identity. Original
ZIP metadata and historical original-label scores remain untouched.

This gives eleven subject/hand identities: ten with ten images each and one
(syr:right) with twenty images. All original image hashes are matched against
the already present Pi copies. The archive, session-index and correction hashes,
original/corrected identities and sample/session indices are preserved in the
private manifest/protocol. There are no duplicate JPEG hashes.

## Fixed protocol

For every identity, order all images by their immutable capture sample IDs.
The original case enrolls the earliest five, and the reverse case enrolls the
latest five. All remaining images query: 55 enrollments and 65 queries per case.
This retains all 120 images in each case; syr contributes fifteen query images,
while each other person contributes ten across their two hands. Query order is
shuffled with seed 20261029. No quality- or outcome-based sample selection.

Each case starts with an empty isolated database and freshly computes five-frame
enrollment, template persistence, prepared templates, index and geometry links.
After each identity enrolls, immediately query its chronologically first
non-enrollment image. These eleven additional immediate queries are reported
separately from the main 65-query denominator; all are recomputed again if they
also appear in the main query pass. They never prime enrollment with query data.

Main queries exercise simulated confirmation, duplicate confirmation rejection,
cancellation and cancelled-token rejection using their actual returned tokens.
A separate fresh Python process then measures model startup, full gallery
rebuild and a first query on the saved experimental enrollment. Generic model
priming uses only zeros, and its time is reported separately.

## Timing and integrity

Pure Pi 5, CPU affinity 0/1/2, ONNX Runtime three threads, OpenCV/native one
thread, OMP_WAIT_POLICY=PASSIVE. Native-library and source hashes are checked.
HTTP recognition includes reading the saved original, preprocessing, ROI,
features, retrieval/registration, scoring and response. Live camera acquisition,
hand positioning and external upload are excluded. Registration, last frame
read to response, immediate queries and process restart are separately timed.
Nested/parallel stage timers overlap and must not be summed.

Every failed enrollment, failed localization, wrong identity and over-budget
query remains visible. A nonzero/unreadable Pi throttle flag aborts the run,
saves partial evidence and does not produce a complete-run claim.

## Interpretation

The earlier 80/80 development result concerned bankey and stephen, not all six
people. All six labels are now previously exposed data; this is an expanded
frozen evaluation, not an unseen-person validation. Comparisons with the old
four-person original-label evaluation also differ in gallery, roles, label
correction and matcher, so counts cannot isolate an algorithmic improvement.
The simulated demo uses closed-set ranking; unknown-person rejection is not
calibrated. Eleven palm identities do not demonstrate 40-person capacity.

## Evidence and reproduction

Private outputs: `runtime/pi5-under2-20261028/six-person-v24-frozen-20261029/`.
Preparation: `tools/prepare_six_person_evaluation.py` creates a protocol and
manifest by checking the archives and matching existing Pi image paths by SHA.
`tools/evaluate_six_person_frozen.py` runs fresh original/reverse HTTP evaluation
and fresh-process startup checks. `tools/report_six_person_evaluation.py` renders
all main query results, including failures, as a standalone HTML report.

## User-requested pause

The user paused all experiments to shut down on 2026-10-29. Experiment processes
were stopped, Pi filesystem buffers synced, and the latest checkpoint copied
to the computer as `results-paused.json`. `PAUSED.json` records the pause.
Do not resume without an explicit user instruction.

Original case completed all eleven enrollments, eleven immediate queries,
65 main queries, simulated payment checks and a fresh-process restart check.
Main results: 62/65 correct, 52/65 correct within 2.5 s, median 1.604 s,
P95 8.836 s, maximum 10.235 s. All eleven simulated payment checks passed.

Reverse case checkpoint contains five completed enrollments, with no main query
results yet. An in-flight enrollment may have left extra partial runtime files;
preserve this partial directory and use a fresh isolated runtime when resuming
the remaining reverse evaluation. Do not silently rerun the completed original
case or describe the reverse case as complete.
