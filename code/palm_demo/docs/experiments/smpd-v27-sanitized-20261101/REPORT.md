# SMPD v27: paused-prefix diagnosis and bounded ROI pilot

2026-11-01. Aggregate-only publication; local images, subject/sample identifiers,
paths, coordinates, feature containers, per-image hashes/scores, protocols and
runtime records are intentionally absent. This is previously seen public
development data on Windows, not Pi timing, independent generalization or FAR.

## Frozen baseline and diagnosis

The long evaluation remains `paused_STOP` at 1239/3217 (parent 216 + continuation
1023). Neither the old 70/241 runs nor the separate pilots enter this denominator.
Registration: 460 attempts, 447 feature successes, 13 failures, 86/92 complete
five-frame identities. Queries: 354 correct, 676 wrong accepts, 209 processing
failures; 194 correct within 2.5 seconds; no rejection or tied-true outcome.

The 209 failures are ROI-stage HTTP 400 responses with empty score vectors:
183 keypoint-span failures and 26 out-of-bounds results. Of the 676 wrong accepts,
118 have no true identity in the gallery and 558 rank an enrolled true identity
incorrectly. Geometry acceptance does not prove anatomical correctness. The
remaining upstream causes of those 558 errors are not established.

Original scoring accounts for 97.31% of cumulative HTTP time; the appended RF
calculation accounts for 0.699%. These nested timers cannot be added. Original
scoring includes lazy extraction, registration and matching; it is not a neural
network-only timer. RF corrects 19 ordinary-score errors but loses 13 ordinary
correct results, so reverting RF would sacrifice existing correct identities.

## Completed local pilots

The existing `tools/halfturn_roi_recovery.py` is reused **without modification**.
It accepts no identity, label or score. A valid primary result returns the same
objects. Only an invalid out-of-bounds result permits one 180-degree retry.
Coordinates are mapped back to the original image; existing span, bounds and
IoU >= 0.5 guards remain. Sampling uses original pixels. No threshold scan,
frame replacement, partial registration or sample-conditioned recognition rule.

Eight fixed geometry observations produced five retries and three recoveries.
Two valid controls and the span-failure negative control were unchanged. This
alone is geometric evidence, not correct recognition. One previously absent
development identity then had all five original enrollment frames successfully
extracted; its four originally valid frame arrays/codecs were exactly unchanged.

The independent identification pilot retained byte-identical copies of all 86
original five-frame templates, added that one complete identity, and prepared
the full 87-identity gallery once. Exactly eight queries ran:

| Outcome | Historical baseline | Candidate |
|---|---:|---:|
| Correct | 2 | 7 |
| Wrong identity accepted | 5 | 0 |
| Processing failure | 1 | 1 |
| Rejection | 0 | 0 |

All five target errors genuinely became correct. Both correct controls preserved
their effective ROI, route and every original-gallery score exactly. The
negative control retained the same failure without retry. All eight query ROIs
were unchanged: the demonstrated benefit is **recovered enrollment and gallery
coverage**, not general query-ROI repair. All tokens were canceled; zero payments.

Target HTTP times were 0.693–0.832 seconds, but the difficult correct control
still took **94.299 seconds**. Full-gallery preparation took 155.593 seconds.
The baseline was historical, not a contemporaneous timing repeat; no speed
improvement is claimed. All 2457 parent/continuation files were byte/stat-identical
after the identification pilot, with the original chain and STOP preserved.

Local execution asserted the actual `LosslessUnionMatcher`, magic 2801166,
lossless codec/storage, retained evidence, terminal-RF policy, threshold 1.0,
margin 0, rejection off and CPU provider. It did not run a mislabeled older
matcher. The eight-query result does not establish whole-dataset improvement.

## Published code versus executed local artifacts

The general recovery implementation and its existing geometry tests were already
tracked before this work. This commit adds publication exports of the two local
pilot drivers, their synthetic control tests and private-manifest binding guards.
No production algorithm or default service is replaced.

The exports move private input identifiers and run-directory bindings into an
external JSON selection. They add binding/path/role checks; inference and scoring
remain calls to the existing implementations. **They are not byte-identical to
the executed local drivers and were not rerun on biometric data.** The completed
local pilots had 8 geometry and 5 driver fixture passes. Publication validation
runs those 13 synthetic cases plus 8 new binding/isolation cases: **21 passed in
0.42 seconds** in the existing CPU environment. No image inference is part of
publication validation.

For future explicitly authorized use, the geometry driver's private selection
has `samples` (8 ordered identifiers) and `negative` (last identifier). The
identification selection has `enrollment` (5 original ordered frames), `queries`
(5 targets, 2 correct controls, 1 negative), `controls` (positions 6–7),
`recovered_enrollment` and `candidate_user`. The checked baseline must match these
roles; all selected subjects must be in the fixed development split. No actual
selection file is distributed. The original fixed 1239 boundary, 86→87 gallery
size and eight-query limits remain intentionally narrow.

Both CLIs require `prepare` or `run`, `--output`, `--parent`, `--continuation`,
`--selection`; identification also requires `--geometry`. Run directories must
be separate and cannot contain protected inputs. Prepare seals selection,
source/model/dependency and input locks; run refuses changed bindings and uses an
exclusive start marker. They do not restart or resume automatically. A geometry
run needs an 8-case fixture XML from the two original geometry test modules; an
identification run needs a 5-case fixture XML from its driver test module. Future
execution requires its own authorization and new frozen protocol, not this save.

## Next regression: memory and time plan only

No full 168 original-device regression has been run for this candidate. Before
adoption it must protect all 166 current correct cases (including the original
165), original fast paths, all 168 queries, fixed five-frame enrollments and
payment guards. Keep the completed standard reference and compare exact scores
and transitions; if a fresh paired timing reference is authorized, run variants
in separate sequential epochs with matching CPU settings, not concurrently.

Use one worker and one coordinator/writer. Start only with >=12 GiB free RAM;
check >=2 GiB free and <=14 GiB worker RSS at frame/query boundaries. Preserve
completed records and pause on a boundary if the resource gate fails; do not
discard difficult cases. Keep startup, five-frame enrollment, complete-gallery
ready and HTTP query timing separate. Estimate a run budget from the actual
original-device case counts and measured costs after reviewing the frozen
manifest. No estimate based solely on the five easy recovered queries is valid.
The 94.299-second control and 155.593-second gallery-ready observation warn
against promising a fast full run. No full run is scheduled by this report.

Hardware was read-only verified: RTX 4070 SUPER, 12282 MiB VRAM, driver 610.88;
Core Ultra 5 338H, 12 cores/logical processors, about 31.55 GiB RAM. The active
environment is PyTorch 2.15.0+cpu and ONNX Runtime 1.31.1 with no CUDA provider.
Driver CUDA capability is not an installed CUDA inference runtime. No libraries
or drivers were installed. A future CPU/GPU design must first isolate the costly
stages and prove score/output equivalence and net benefit on a bounded pilot.
Do not assume CPU/GPU parallelism, duplicate full galleries, or allow competing
workers to write a shared status file. Pi validation remains separate.

Model provenance: the analysis/pilot task was requested with `gpt-6-astra` and
the tool accepted task creation, but returned no independently verifiable actual
runtime-model field. Publication packaging does not provide new model evidence.
No full evaluation, deployment or mainline promotion is authorized by this save.
