# Existing half-turn ROI candidate: device preservation guard

2026-11-01. Windows, previously seen development/device data. No independent
generalization, stranger FAR, Pi latency or deployment claim. No image, subject
identifier, original path, coordinates, feature data or per-image result is
published here.

## Candidate and frozen boundary

The existing half-turn candidate is unchanged. It retries only an invalid primary
ROI with reason `roi_out_of_bounds`, once at 180 degrees. The original span,
bounds and IoU >=0.5 checks remain. A valid primary is returned verbatim; span
failure is not bypassed. It does not solve all ranking errors or span failures.

The public SMPD run remains `paused_STOP` at 1239/3217, with STOP retained.
Its 676 wrong accepts include 118 missing-gallery and 558 enrolled-identity
ranking errors; its 209 processing failures include 183 span and 26 OOB failures.
These are subclasses, not extra outcomes. Public sample images were not rerun.
Saved public pilot evidence supplies OOB-success, OOB-failure, span-negative and
valid-primary controls; it remains archived evidence rather than new observations.

The historical 169-device-image ROI audit found all 169 primaries valid and no
recovery attempts. This guard therefore tests preservation on device data, not a
new device accuracy gain. The executed matcher is explicitly v27 lossless plus
the frozen terminal-RF policy, rather than inheriting the old split's v24 label.
Models, thresholds (.32/.08 early, 1.0/0 final), labels, original bytes and
rejection-off policy are fixed. All galleries retain their complete identity
sets and each identity's five original enrollment frames.

The old standard-source helper initially rejected three already committed v27
container adapters. Manual review against its standard Git blobs found only the
v27 registry entry, store factory/batching/codec metadata and cache namespace.
Their exact current hashes match the immutable v27 source lock; all other core
sources match the standard lock. This compatibility difference is recorded in
the private frozen plan. No core source was changed in this work.

## Harness failure retained

The first panel attempt stopped in its first baseline enrollment because the
observer did not forward `extractor.root`. The primary ROI was valid and the
candidate returned the same tuple; no enrollment completed and no identify
request was sent. This was an invalid harness observation, not a candidate
accuracy result. The original driver, plan, response and failure are preserved.
The repaired observer forwards extractor attributes; a synthetic regression test
covers that interface. A new plan binds the same panel/thresholds and the failed
run's receipts. No outcome-based sample replacement or parameter change occurred.

## Bounded panel

Selection used stored reference roles: the lexicographically first retained RF
correction's case, the first correct non-exhaustive query in that case, that RF
correction, and the first remaining error. Selection does not enter recognition.
One complete 11-identity case gallery was freshly enrolled (55 frames). Each
enrollment primary was valid, and the recovery wrapper returned the identical
tuple. Only after establishing this equivalence were those new v27 templates
byte-copied to the candidate's independent runtime. Candidate load/index ready
cost is recorded separately; it is not claimed to be fresh enrollment timing.

| Panel, three queries each | Baseline | Candidate |
|---|---:|---:|
| Correct | 2 | 2 |
| Wrong accepted | 1 | 1 |
| Rejected / processing failure | 0 / 0 | 0 / 0 |
| Correct within 2.5 seconds | 1 | 1 |
| HTTP P50 seconds | 4.049 | 4.068 |
| HTTP P95 seconds | 5.183 | 5.167 |
| HTTP maximum seconds | 5.309 | 5.290 |

All paired ROI pixels/geometry/details, final gallery scores/decisions/routes and
the stored terminal-RF reference scores matched exactly. The full 11 five-frame
template arrays matched exactly. No old correct was lost. No speed improvement
is established. Baseline enrollment requests totaled 100.613 seconds; candidate
load/index ready was 13.863 seconds. The different enrollment paths prevent a
comparative enrollment-speed claim. Peak sampled RSS was 1.295 GiB; minimum
available host memory 15.171 GiB. All public file bytes and original device input
bytes remained unchanged.

Both variants carry the same observation hooks. The baseline observer also checks
the candidate's pass-through on its primary result, to establish template-reuse
provenance. On these valid primaries this performs no additional model inference.
Timers include observation overhead; this setup does not isolate the tiny cost
of adding the policy to an otherwise uninstrumented service.

## Complete device regression protocol

The panel passed, so a separate explicit full-device command was authorized and
announced before launch. It includes all four original cases, 168 queries and
34 fresh five-frame enrollments **per variant**: 336 identification requests and
68 enrollments in total. The private plan freezes original case lists and query
shuffle seeds. Unlike the panel, neither variant reuses enrollment templates.
Outputs and payment databases are isolated by case/variant, with a single
inference worker and sequential variants. Startup/ready, enrollment and HTTP
query times are recorded separately. The announced rough budget was 15–25
minutes; it is not an ETA confidence interval or speed guarantee.

Every issued token is canceled, pending tokens must clear and transactions stay
zero. No confirm/payment request is made; this does not rerun the positive
confirmation/deduction portion of the earlier payment regression suite.
All 166 stored correct identities, exact scores/routes and paired ROI/template
arrays are guarded. A result can be called complete only with all 168 fixed
query keys and all 34 enrollment groups present per variant.

Start requires >=12 GiB free RAM; frame/query boundaries require >=2 GiB free and
<=14 GiB process RSS. A local STOP ends work at a completed-request boundary,
preserving results without automatic continuation. Public STOP is never removed.
Telemetry samples CPU per logical core, process CPU/RSS, host available memory
and cumulative disk I/O once per second. System disk/CPU counters include other
host activity and do not alone prove a causal bottleneck.

## GPU scope and remaining work

RTX 4070 SUPER hardware is present. The frozen environment uses CPU-only PyTorch
and CPUExecutionProvider in ONNX Runtime. No driver/library installation, GPU
inference, new data download, system/security or network change occurred.

If a later GPU pilot is approved, the package candidate is
[`onnxruntime-gpu`](https://pypi.org/project/onnxruntime-gpu/) using the official
[CUDA provider requirements](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)
in a separate environment such as `runtime/gpu-pilot-env`,
with a version compatible with the ONNX models, driver, CUDA and cuDNN libraries.
The exact compatible versions must be verified before installation; a driver's
CUDA capability is not an inference runtime. Optional CUDA-enabled PyTorch
would come from the official PyTorch wheel index only if a measured Torch stage
requires it. The existing CPU environment should remain the reference.

Expected benefit is limited to measured ONNX/Torch model inference, potentially
batched extraction. It does not automatically accelerate OpenCV registration,
descriptor matching, Python scheduling or the whole exhaustive stage. The public
timer's 97.31% original-scoring share includes several such operations and is
not a neural-network percentage. Risks include CPU/GPU transfer and setup cost,
different floating-point scores/routes, memory duplication and limited VRAM.
Only a bounded paired test with full-output equivalence and net wall-clock gain
could justify expansion. Multiple workers require separate logs/runtimes and a
single result coordinator; no such parallel inference is implemented or run here.

The current session's supplied system model identifier is `gpt-6.1-sol`; no
separate tool-returned model-execution receipt is available. The prior Astra
task's creation receipt did not independently identify its actual runtime model.

## Preserved resource stop in the first execution epoch

The baseline finished all 168 queries and 34 five-frame enrollments. At the next
variant-start boundary, before the last candidate case began, the frozen memory
gate stopped the process. The last pre-stop sample had 10.692 GiB host available
and 1.112 GiB process RSS. This is consistent with insufficient headroom for the
next variant's 12 GiB startup requirement, rather than the 2 GiB in-run floor or
14 GiB RSS ceiling. The exact gate-instant numbers were not separately saved.
The responsible background allocation was not established and no other app was
closed or changed. The worker exited; no identify request was left in flight.

| Coverage at that stop | Baseline | Candidate |
|---|---:|---:|
| Queries completed / fixed target | 168 / 168 | 113 / 168 |
| Correct | 166 | 111 |
| Wrong accepted | 2 | 2 |
| Rejected / processing failure | 0 / 0 | 0 / 0 |
| Correct within 2.5 seconds | 153 | 106 |
| HTTP P50 seconds | 0.711 | 0.582 |
| HTTP P95 seconds | 4.403 | 4.168 |
| HTTP maximum seconds | 7.718 | 7.444 |
| Fresh five-frame enrollments, all ready | 34 | 23 |
| Enrollment requests total seconds | 379.326 | 280.024 |
| Gallery-ready time inside enrollment, seconds | 57.567 | 38.738 |
| Startup/initial ready total seconds | 2.944 | 2.285 |

These aggregate timing columns have different query/case denominators and must
not be used to claim improvement. Ready-within-enrollment is a nested component
of enrollment HTTP time, not an extra duration to add.

For the **same completed 113 queries** on both sides:

| Paired subset only | Baseline | Candidate |
|---|---:|---:|
| Correct / wrong / rejected / failure | 111 / 2 / 0 / 0 | 111 / 2 / 0 / 0 |
| Correct within 2.5 seconds | 106 | 106 |
| P50 / P95 / max seconds | 0.658 / 4.700 / 6.672 | 0.582 / 4.168 / 7.444 |

All 113 paired decisions, complete score vectors, routes and ROI outputs match
exactly. Read-only post-run array auditing also confirms all five arrays for each
of the 23 completed paired enrollment groups are identical. All 111 previously
correct queried controls remain correct; none crosses the 2.5-second boundary in
either direction. The remaining 55 previously correct queries are **untested on
the candidate**, not observed losses. The two existing wrong accepts remain
wrong. Sequential epoch/background effects and the larger candidate maximum do
not establish a speed benefit.

Across 979 one-second telemetry samples, process RSS peaked at 1.735 GiB and
available host memory reached a 10.105 GiB minimum. A separate live Windows peak
working-set counter observation was 1.785 GiB; that observation preceded final
baseline completion and is not a final post-exit peak counter. The sampled
interval was 986.873 seconds with 2097.594 process CPU seconds. Host-wide disk
counters increased by approximately 4.09 GB read / 3.01 GB written; these include
other host activity, exclude the outer integrity-hash phases and do not identify
which stage caused I/O pressure. Per-core and nested-stage aggregates are in the
published `summary.json`.

The complete baseline's HTTP total was 188.647 seconds: capture/extract 102.702,
gallery 83.820, original scoring 82.431 and appended RF 0.828 seconds. The primary
ROI timer was 76.867 seconds and lazy complete-features timer 12.864 seconds.
These timers overlap/nest. They support separate localization and gallery
investigation, not a claim that the exhaustive stage is entirely GPU-eligible.

All original device input bytes and all public parent/continuation bytes were
unchanged at that stop. The public chain stayed paused at 1239/3217, STOP present.
The invalid first harness attempt and every completed result remain local and
unmodified. No full-regression pass was claimed at that point. Coverage-related
false checks in the preserved partial export indicated missing observations,
not fabricated recognition errors.

At that boundary the remaining work was exactly one candidate case: 11 fresh
five-frame enrollments and 55 original queries. It was not automatically retried.
The reviewed continuation below completes the already authorized 168-query scope
without repeating any complete query. The original stop remains unchanged.

## Reviewed operational continuation and final complete coverage

After resource review, a new isolated sibling plan was frozen and announced
before launch. Only startup free-memory headroom changed from 12 to 8 GiB, based
on the observed 1.785 GiB worker peak counter and approximately 10.6 GiB host
availability. The 2 GiB running floor and 14 GiB RSS ceiling stayed fixed. No
recognition parameter, model, input, label, score or ROI policy changed. This was
a manually reviewed operational continuation, not an automatic program restart
or an accuracy-based trial. Its one-shot start marker prohibits another run.

The continuation binds the prior plan/result and every prior file hash, protects
the stopped directory with read-only handles/audit guards, and accepts only a
whole never-started candidate case. It freshly enrolled all 11 five-frame groups
and issued exactly the 55 missing queries in the original seeded order. All 55
were correct and exactly matched their saved baseline ROI/score/route. All 11
five-frame arrays matched the baseline. Prior records and public bytes remained
unchanged; all tokens were canceled, with zero payments.

The final aggregate is a new verified view of baseline168 and candidate113+55.
It does not overwrite or mark the original resource-stopped process complete.
Independent fixed-key auditing confirms exactly 168 unique case/query keys and
34 complete original five-frame groups per variant, no duplicate case or query,
all old166 correct retained and all stored terminal-reference decisions/scores
exact. All 168 paired ROI/score/route outputs and all 34 paired five-frame arrays
match. The final `summary.json` reports this complete logical evaluation and
separately records the preserved stop and reviewed continuation.

| Final, 168 queries each | Baseline | Candidate |
|---|---:|---:|
| Correct | 166 | 166 |
| Wrong accepted | 2 | 2 |
| Rejected / processing failure | 0 / 0 | 0 / 0 |
| Correct within 2.5 seconds | 153 | 159 |
| HTTP P50 seconds | 0.711 | 0.579 |
| HTTP P95 seconds | 4.403 | 2.949 |
| HTTP maximum seconds | 7.718 | 7.444 |
| Fresh five-frame enrollments, all ready | 34 | 34 |
| Enrollment requests total seconds | 379.326 | 397.686 |
| Gallery-ready time inside enrollment, seconds | 57.567 | 59.822 |
| Startup/initial ready total seconds | 2.944 | 3.421 |

No previously timely-correct sample crossed above 2.5 seconds; six crossed below
it in the later candidate observations. The candidate includes a separate process
and later host-load epoch for its last case, while every valid ROI/path/score was
unchanged. These numbers **do not establish causal speed improvement** from the
half-turn policy. They show preservation on this previously seen device set.
The two original errors remain errors. There is no new device accuracy gain.

The continuation's 171 telemetry samples covered 171.330 seconds, sampled peak
RSS 1.415 GiB and minimum host-available memory 9.201 GiB. Its saved actual
Windows process peak counter, including post-run verification, was 1.467 GiB.
The initial resource stop is not erased, and no other application was closed.
Neither the SMPD 3217 run nor a Pi evaluation was resumed. No GPU libraries,
drivers, system/network settings or production services were changed.

Publication validation: **13 synthetic tests passed** (observer forwarding,
selection/ROI/score guards and detection of missing/duplicate query/frame keys).
Continuation tests also reject partial-case retries, non-resource failures,
duplicate-case merges and mutation of the preserved parent result.
The checked scripts contain no fixed personal/sample identifiers; original
private plans, image paths, rows, ROI geometry and templates are excluded from
Git. The candidate algorithm itself was not modified.
