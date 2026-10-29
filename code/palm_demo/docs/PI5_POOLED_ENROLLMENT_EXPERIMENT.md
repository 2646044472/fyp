# Sparse correspondence pooling on Pi 5, 2026-10-29

Experimental matcher: `FastCCPooledEnrollment-v20-experimental`, magic 2801060.
Production v6 remains unchanged. This experiment improves one development slow
case but does not establish a 2.5-second worst-case bound or 40-person readiness.
The earlier reserved-cohort maximum of 10.681 seconds has not been remeasured
with this candidate; do not substitute the development maximum for that result.

## Change and generality

When unchanged v13 pose, legacy, enrollment-link and affine checks remain
uncertain, pool their already available mutual RootSIFT correspondences through
the enrollment-to-enrollment transforms. For each target enrollment, transfer
observed points from the other enrollments into its coordinate system. Each
query point contributes once at the median transferred location. Fit the
existing bounded similarity and affine models, then score original query pixels
against the original target binary code.

No new descriptor searches, identity-specific branches, query answer cache,
confidence-threshold changes or removal of complete fallback. The candidate
uses the same processing for each supplied enrollment group. Point count is
deduplicated before geometric estimation. Original inlier, coverage, scale,
angle, anisotropy, source-bounds and anchor-overlap guards remain in force.

Pool-transfer allocation and validity checks are batched. The per-point
matrix/vector arithmetic is preserved; singleton medians avoid unnecessary
NumPy calls. Scalar-reference tests verify bit-exact transferred coordinates.

## Actual Pi HTTP results

Pi 5 8 GB; CPU affinity 0,1,2; ORT three threads; OpenCV/native one thread;
`OMP_WAIT_POLICY=PASSIVE`. Each request rereads its saved original and computes
ROI, features, search, alignment and scoring through the real HTTP handler.
Loopback response is timed. Live camera acquisition and external upload are
excluded. Templates are reused with verified payload-preserving v10-to-v20 tag
conversion, so these are not fresh-enrollment timings.

| Dataset/pass | Correct | Correct <=2.5 s | P50 s | P95 s | Maximum s |
| --- | ---: | ---: | ---: | ---: | ---: |
| New/first pass | 20/20 | 18/20 | 1.927 | 2.569 | 2.783 |
| New/warm pass | 20/20 | 19/20 | 1.892 | 2.496 | 2.565 |
| Old/first pass | 20/20 | 19/20 | 1.484 | 2.533 | 5.666 |
| Old/warm pass | 20/20 | 19/20 | 1.486 | 2.101 | 5.736 |

The old development query ending `283768e8` changes from approximately 5.18 s
in v13 to 1.909 s warm with pooled rescue. The query ending `575a2085` still
uses complete fallback: 5.736 s warm versus approximately 5.428 s previously.
The extra unsuccessful rescue increases this remaining tail. New warm maximum
is 2.565 s (query ending `b199fa06`), versus approximately 2.746 s in the earlier
v13 run. Historical baselines are separate runs, not interleaved measurements.

Startup was 13.600 s new / 5.005 s old. Two concurrent requests were both
correct, but serialized queue response times were 1.892/4.296 s new and
1.510/2.973 s old. Thus simultaneous arrivals do not meet a per-request 2.5 s
deadline. Peak RSS was 1.617 GB new / 1.406 GB old. All recorded power/throttle
flags were zero. Simulated transaction counts were unchanged; tokens cancelled.
These known-identity results do not calibrate unknown-person rejection or FMR.

## Development checks and rejected variants

Original 80-image development cohort only. All 224 fixed splits scored 20/20
(112 new and 112 old); repeated splits are not independent generalization.
Final transfer optimization and removal of unused experimental registrations
preserved every score and route in the 80-query original/reverse smoke audit.
The full split audit used the prior scalar transfer implementation; the final
implementation has bit-exact scalar parity tests plus that smoke comparison.
191 tests passed, four optional-dependency skips; obsolete
`test_existing_pipeline.py` was explicitly excluded as in prior experiments.

Rejected or retained only as private research evidence: four-way native distance
blocking (1.858 to 1.912 ms median), batched native ambiguity checks (1.970 to
2.018 ms), extra coarse/affine indexed stages, full indexed correspondences
(all 224 splits correct but actual old tails about 6.6 s), dense pose sweeps,
and deferring pooled rescue until after indexed search. Deferral protected the
original fast stages but put the rescued old query back above 2.5 s; its full
224-split audit was stopped after actual-Pi rejection. No complete audit claim
is made for that rejected candidate. Earlier unoptimized pooling was also
slower on several new queries; the final HTTP numbers above supersede it.

## Capacity issue for approximately 40 registrations

Existing prepared-template cache and descriptor-index limits are each 256 MiB.
Measured cached development features for four hand identities give:

| Source | Prepared bytes, 4 identities | Index descriptor bytes, 4 identities | Prepared/index estimate, 40 identities |
| --- | ---: | ---: | ---: |
| New camera | 199,970,896 | 159,953,408 | 2.00 GB / 1.60 GB |
| Old camera | 42,859,160 | 29,940,736 | 0.43 GB / 0.30 GB |

These are linear capacity estimates from the measured template distribution,
not a 40-person accuracy or latency experiment. Separate left/right hand
registrations double identity count. An oversized index currently raises an
error; exceeding the prepared cache can also cause repeated loading and index
rebuilds. Merely raising these limits does not bound query compute. A compact
retrieval index, bounded candidate verification and measured candidate recall
are still needed before claiming 40-person readiness.

Public datasets in `code/data` were not used for selecting this candidate.
The previously exposed reserved people remain evaluated data and were not used
for tuning. Local-device long-tail work takes priority. After freezing an
acceptable local candidate, public evaluation should record its split before
running, retain failures, and distinguish cropped-ROI supplements from complete
original-image Pi HTTP tests. No raw biometric data is committed.

## Private evidence and reproduction

Under `runtime/pi5-under2-20261028/`:

- `pooled-enrollment-v20-all/{protocol,results,summary}.json`
- `pooled-v20-final-smoke/{protocol,results,summary}.json`
- `ready-pooled-v20-final-{new,old}.json`
- `pooled-enrollment-report.html`
- `rejected-tail-candidates/` and intermediate candidate audit/HTTP records

Use `tools/prepare_linked_replay.py --matcher FastCCPooledEnrollment-v20-experimental`
on a guarded isolated v10 replay. Then use `tools/replay_ready_queries.py` with
fresh output, native library, three-core affinity and the thread settings above;
enable `--record-power --abort-on-power-fault`. Run the fixed-split audit with
`tools/audit_indexed_demo.py --matcher FastCCPooledEnrollment-v20-experimental`.
Offline registration/pair caches are audit accelerators, never latency results.
