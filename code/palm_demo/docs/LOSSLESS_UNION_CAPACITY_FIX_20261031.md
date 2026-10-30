# Lossless variable Union capacity repair — 2026-10-31

This is an opt-in v27 container experiment on `experiment/smpd-roi-20261030`.
No production service was started/reconfigured, no Pi deployment occurred, and
the frozen standard branch/tag remain at `9d9bb43e909e992765bf586da13a3b881e3dc481`.
No complete SMPD evaluation was launched or resumed by this repair.

## Failure and implementation

The stopped v26 terminal-RF run committed70/3217 query records, then failed while
packing `smpd-003-F-05`. Its 16MiB envelope cannot hold the maximum admissible
Union representation: legacy1639136 bytes +44 views×(88+1000×520) +20-byte header
already total24523028 bytes (~23.39MiB), before the lossless native PNG. Increasing
the fixed padding alone would also leave five-frame stacking and strict shape
readers incompatible.

`union_lossless_codec.py` adds explicit `UNIONV2`/version2 framing with64-bit
total/PNG lengths and actual-length contiguous uint8 payloads. It preserves the
legacy block, original PNG bytes, view order, float widths/endianness, points,
descriptors and all generated admissible views. No new filtering, quantization,
lossy compression, score mixing, acceptance adjustment or identity/file rule is
introduced. Existing hypothesis/anchor rules and1000-point extractor remain the
unchanged algorithm. The codec decoder returns the existing matcher tuple API.

`LosslessUnionMatcher`, explicitly selected as
`FastCCCompNetAlternateROI-v27-lossless-experimental`, inherits the real v26
extractor, stages and scoring functions. Only the Union pack/unpack boundary is
replaced. Its runtime magic is2801166; framing separately records the v26
semantic payload ID2801066. Old fixed v26 readers reject the new arrays. The new
reader can validate canonical old v26 payloads without changing them; it rejects
other semantic versions/nonzero hidden padding. This is not an in-place migration
or certification of every historical matcher format.

## Five-frame persistence, cache and API

`LosslessTemplateStore` writes one `USER.union2.npz` containing exactly
`manifest.json` and five ordered numeric `frame_000.npy`..`frame_004.npy` members.
Each frame has its own length/SHA256 and can have a different length. No object
array, pickle, external path reference or sidecar generation is used. The manifest
holds storage/codec versions, identity and normal enrollment metadata.

The archive is completely written to a same-directory temporary file, flushed and
fsynced, then replaced once. Data and metadata commit together. A failed write,
replacement or fifth-frame validation leaves the prior committed generation and
account usable. Temporary files do not appear as enrolled users. Windows
power-loss durability beyond the platform's fsync/replace guarantees is not
certified by the exception-injection tests. Template/account SQLite state are
still separate transactions; existing incomplete-account checks and rollback
continue to apply.

`DemoFlow` selects the new store/batch adapter only when the experimental matcher
requests it. Existing matchers retain `TemplateStore` and `np.stack`. The v27
batch is a reusable tuple of five arrays: inherited enrollment preparation
traverses the input repeatedly. Required metadata includes algorithm, ROI,
storage schema and codec. Gallery cache signatures include the store's version
namespace and the committed archive stat identity. New archive data is immutable
after loading. A new store reads canonical legacy templates for explicit
diagnostics but refuses an in-place overwrite or ambiguous old/new identity.

The actual HTTP enrollment/identify/confirm/cancel handlers are exercised in an
isolated test server. They continue to accept small JSON commands; feature bytes
are generated server-side, so their4096-byte request limits do not change. The
unrelated debug DoN enrollment format is not migrated.

## Bounded decoding

The archive footer's count, central-directory byte bound and file size are
checked before `ZipFile` allocates directory objects. Preflight and member reads
pin the same open file generation. Readers reject duplicate/missing/unexpected
members, encrypted/unsupported methods, oversized manifests and total expansion.
NPY versions, header byte count, numeric dtype/order/shape and exact member length
are checked before allocation. Per-frame SHA and ZIP CRC are checked on reading.

Union parsing retains the original structural, finite-number, geometry, bounds,
point-count and view-order checks. PNG IHDR grayscale format/dimensions and a
native pixel budget are checked before `imdecode`. Limits are fixed resource
guards:16384 per side,64Mi pixels,66MiB encoded PNG,42 query/two gallery views,
1000 points/view, and the resulting explicit maximum payload. They do not resize
or truncate data. Existing SMPD metadata reports a maximum decoded15872256
pixels and5312 pixels on either axis; the metadata check is not a new image scan.

This local template format is **not encrypted/authenticated**. CRC/SHA detect
corruption, not adversarial rewriting by a party able to replace the manifest.
Native pixels/descriptors remain biometric data and stay outside Git.

## Verification and evidence boundaries

Final scalar evidence and owned report are in
`docs/experiments/union-lossless-fix-20261031/`. The test matrix covers all decoded
tensor bytes/PNG/view order, full42-query/two-gallery payload beyond16MiB, mixed
five-frame storage, legacy compatibility/new-reader refusal by the old format,
bad versions/lengths/counts, path/duplicate members, corruption, object headers,
oversized directory/NPY allocations, atomic failure, metadata/cache invalidation,
fifth-frame/account preservation and real HTTP payment guards. Existing default
store, gallery, ROI, demo/index and terminal-RF tests are included.

The bounded real-model diagnostic uses fresh original-device extraction in one
fixed six-identity/five-frame gallery. It selects the first previously recorded
query per original route in fixed protocol order, independent of correctness;
all prepared tensors, whole-gallery scores, original stage vectors, final routes
and RF provenance are compared exactly. No historical feature arrays are loaded
as new candidate references. This is a finite regression/equivalence diagnostic,
not a universal proof of recognition accuracy or a speed improvement.

Only the stopped public sample is re-extracted, once per diagnostic version,
to observe its original pre-pack blocks and prove that the new container keeps
every block. It is not ranked against SMPD and creates no public query outcome.
The initial diagnostic initialization omitted its opt-in retained flag and
stopped before processing any frames. A second diagnostic passed; after the
same-file-handle hardening a separately locked third diagnostic revalidates the
same fixed inputs. No samples or parameters are changed between them.

## Preserved evidence and next full-run boundary

Before editing sources,539 scalar files from the stopped run were copied to
private `runtime/union-lossless-fix-20261031/preserved-r2/`, with an immutable
per-file hash manifest. Original460 enrollment records,70 query records,
`smpd-003-F-05` inflight marker, protocols/gallery/epochs are preserved and checked
again after diagnostics. The old241 ordinary-score results and JSONL are also
verified against their original stop receipt. No old record is appended,
overwritten, reclassified or promoted to a new version.

The old70 final scores belong completely to the previous code/gallery version.
The71st request has no completed outcome. Changing format requires a new run
fingerprint and zero query prefix. Recovering former capacity-failed registrations
may change the gallery and confidence routes even if all common per-pair scores
stay equal. No registration reuse is certified: all460 fixed F0–F4 attempts must
be regenerated for the next evaluation, all92 identities accounted, and all3217
queries retained. Failed registrations and ROI failures remain in its primary
denominator. Source JPEG paths/hashes, original inventory, exact models and the
fixed74-development/18-protected split can identify the same raw data.

The next-run contract is a **candidate/version boundary**, not a certified full
execution launcher. A new evaluator/resume lock must explicitly support the
variable store; existing `run_terminal_smpd.py` remains a frozen old-format runner
and intentionally cannot resume after these source changes. No full run has been
authorized to launch in this turn. Thresholds remain`.32/.08/1.0/0`, rejection off.

The prior76-person Windows gallery peaked at8.05GiB with~159–163s model/gallery
startup. New bounded diagnostic memory is reported separately. Variable
persistence does not eliminate descriptor/index memory or exhaustive search.
92-person capacity and actual Pi latency remain unmeasured; no Pi deployment or
capacity claim follows. SMPD remains seen public development data, not independent
generalization or stranger-FAR evidence.
