# Fresh v27 lossless SMPD evaluation — 2026-10-31

This run executes the capacity-qualified v27 variable Union codec and five-frame
store with the unchanged terminal-RF scoring policy. The standard branch/tag stay
at `9d9bb43e909e992765bf586da13a3b881e3dc481`; no production/Pi deployment.

## Inputs, reuse decision and frozen accounting

Use the existing released3677 original JPEGs /92 right-palm identities, original
fixed F0–F4 selections (460 attempts), all remaining3217 queries, and the same
stable `(subject,index)` order with inventory ordinal resolving ties. No download,
replacement, deletion, new rotation search, label changes or threshold selection.
One complete eligible gallery includes protected identities; failed-enrollment
queries remain in the primary denominator. Rejection/retry never counts correct.
Early gates `.32/.08`, final `1.0/0`, rejection off; exact original model binaries.

The metadata audit examines **all460 previous records**, including417 successes
and43 failures, without loading their feature arrays. All417 successes lack a
stored decoded-RGB byte hash. Raw JPEG hashes and compatible pilot tensors do not
provide the requested whole-batch comparison to old decoder output bytes. No
batch conversion/reuse is certified: regenerate every fixed original, including
the43 previously failed images. This is an explicit conservative evidence limit,
not a claim that every previous tensor was numerically different.

Old241 ordinary-score queries and old70 terminal-RF queries remain immutable.
The former has a different score definition; the latter used a76-person gallery
which may expand after capacity repair. Neither is imported or appended. The old
71st inflight is not counted as completed. All new registration/query prefixes
start at zero, in `runtime/smpd-lossless-v27-20261031/` with a new fingerprint.

## Execution adapters and isolation

`tools/run_lossless_smpd.py` imports the unchanged old durable operational HTTP
loop but supplies explicit v27 prepare/feature/gallery/lock hooks through a new
function namespace. The request, whole-gallery score trace, cancellation,
failure accounting, fixed query order and atomic hash-chain journal code body
remain the same. Frozen preparer adaptation changes the runtime magic assertion
and observes decoded RGB SHA256; it does not change EXIF/RGB/ROI arithmetic.
Rendered preparer and original HTTP-loop digests are sealed in protocol metadata.

The new preparer explicitly selects the v27 matcher, verifies codec/store metadata
and actual runtime magic, records source/decoded-RGB hashes, actual payload bytes
and view counts. Capacity/allocation/memory exceptions stop the epoch with prefix
and inflight intact. Ordinary per-image localization failures remain recorded
outcomes. All original input bytes are checked within timed capture. Query RGB
hashing is included in the new timing scope; historical timings are not a paired
acceleration reference. Fast query objects are transient; only actually invoked
exhaustive payload sizes are observed. No query-feature/answer cache is imported.

Registration artifacts are fresh one-frame numeric arrays belonging only to the
new root. Loading checks source identity, RGB digest presence, file SHA, bounded
NPY member/header/length, exact variable codec and safe path. Five-frame gallery
archives use `LosslessTemplateStore` without stacking. Per-identity and complete
gallery seals bind the run fingerprint and frame-record hashes. Isolated account
balances remain10000; identification tokens are canceled; no query charges occur.

Source/model/metadata bytes are hashed at epoch start/end and every60 seconds;
file device/inode/size/mtime/ctime are checked at every frame/query boundary.
Any change stops, rather than refreshing the cached version. Environment package
versions are rechecked every60 seconds, relevant process environment at each
boundary; installed inference package content hashes are checked each epoch.
This avoids hashing unchanged large models twice per image while preserving an
explicit frozen execution boundary. The dependency/model/source set and all
operational adapters are part of the new protocol, never inferred from HEAD alone.

## Preflight, supervisor and failure policy

Execution/schema, mixed-frame, corrupt/oversized/member tests, ordered-prefix,
inflight recovery, process-lock and real HTTP handler tests run before launch.
The earlier capacity diagnostic supplies fresh30-frame/eight-query same-gallery
byte/vector/route parity; it does not establish a full public outcome.

Initial background work regenerates all460 registrations, builds/loads the one
complete gallery and executes **two actual formal queries**. It then pauses at
the record boundary. The sealed one-shot v27 supervisor validates the exact two
records, complete registration/gallery, input and candidate provenance, unchanged
versions and available memory. Correctness is not a continuation criterion. If
these checks pass and no STOP is present, the same candidate resumes at query3,
keeping the first two records unchanged. The supervisor never changes algorithms
or retries a failed epoch. It preserves a failure receipt and terminates.

Manual STOP is honored at complete-record boundaries. Infrastructure interruption
keeps its uncommitted attempt; later explicit same-version resume first validates
every record and can retry only that uncommitted sample. Completed failures are
never overwritten/repeated. A format, source, gallery rule or scoring change
requires another version. No partial fixed prefix becomes a full evaluation.

Windows resource allowances remain2GiB descriptor-index guard /6GiB prepared
cache,10GiB available before an epoch and1GiB before each frame/query. These are
resource-only allowances, not Pi settings or evidence that a larger gallery fits.
If the full gallery cannot remain resident or a guard fails, stop rather than
partitioning identities, dropping views or removing difficult images. Observe
process RSS/peak/available memory and gallery-build progress separately.

## Live reporting

`tools/report_lossless_smpd.py` extends the scalar journal report with codec,
reuse evidence, maximum observed payload and actual wall query throughput after
each complete-gallery-ready event. This wall rate includes lock checks, token
cancellation and checkpoint I/O, excludes gallery startup and paused gaps. HTTP
P50/P95/max remain separate. Query completion estimates stay unknown until20 new
records exist; thereafter report observed-mean and P95-cost extrapolations with
an explicit warning that later poses/routes can exceed both. No old-run ETA is
presented as new measurement. Registration ETA uses its own new prefix only.

Report all3217, development2588 and protected629, capture view, actual registered/
unregistered truth, correct/wrong/true-ID-tied/rejected/processing failure, ROI and
registration failures, correctly<=2.5s, startup/epoch/interruption costs and byte
duplicate diagnostics. Keep all files primary. The complete public dataset has
already participated in development; prospective protection is not blind
independent generalization, and closed-set identification is not stranger FAR.
Windows results do not establish real Pi timing/capacity.

The user requested a20-minute status report for this current experiment. A local
thread heartbeat is used only for reading this run and reporting real progress,
resources/throughput and uncertain ETA; it must not launch/retry/tune inference.
On completion/failure/STOP it reports and pauses itself. This is not an hourly
optimization schedule or a recurring evaluation. If the scheduler rejects the
request, disclose the rejection and do not switch scheduling mechanisms.
