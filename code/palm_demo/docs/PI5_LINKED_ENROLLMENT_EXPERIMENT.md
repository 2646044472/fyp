# Enrollment geometry reuse experiment (2026-10-29)

Experimental matcher: `FastCCLinkedEnrollment-v12-experimental`. Production stays
on v6. This experiment does not replace existing templates or change defaults.

## Method

Build geometric links between the five enrollment images within each identity.
Compose a query's existing legacy registration with a single enrollment link to
propose another alignment. Validate the composed geometry, original-image bounds
and anchor overlap, then score original query pixels with FastCC. Retain the
existing distance/margin routing gates and complete v10 fallback. Links never
cross identities; no sample names or expected query identities control routing.

Gallery preparation is cached by the existing gallery key and rebuilt when the
gallery changes. Normal enrollment invokes gallery warm-up. A restarted replay
can pay lazy gallery preparation on its first query; this cost remains timed.
There is no query answer cache. The existing gates are routing heuristics, not
calibrated open-set acceptance thresholds.

## Development audit

All 224 fixed splits scored 20/20: 112 new-camera and 112 old-camera splits.
Across 2,240 correlated queries per cohort, new-camera queries used the linked
route 222 times and avoided 104 exhaustive fallbacks compared with v10. Old-camera
queries used the linked route seven times and avoided no exhaustive fallbacks.
Neither cohort introduced extra exhaustive fallbacks.

These are repeated splits of the same development images, not independent
generalization evidence. The reserved four people/eight hands remain unused.
The audit reuses frozen descriptors and deterministic exhaustive pair scores;
its times must not be reported as end-to-end Pi latency.

## USB power and measurement protocol

The Pi rebooted during the initial fresh-enrollment v12 run. Its cause is unknown.
The user reconnected USB and warned of possible undervoltage. A clean power flag
after reboot cannot rule out a fault before reboot. The interrupted fresh run has
no completed summary and is not counted as a successful enrollment test.

Subsequent query-only diagnostics use two-core CPU affinity (0,1), OpenCV one
thread, ONNX Runtime two threads, native registration one thread, and passive
OpenMP waiting. Only one Pi benchmark runs at a time. This is a controlled
comparison under reduced concurrency, not directly comparable with earlier
four-core results and not proof that USB power is adequate.

`prepare_linked_replay.py` copies an isolated v10 replay and changes only the
template outer version tag and algorithm metadata. It verifies payload hashes
after reloading the copies. This does not measure fresh enrollment and does not
modify the source or production. All query images are read and processed again.

`replay_ready_queries.py --record-power --abort-on-power-fault` samples Pi flags
before startup, after each request and after the queue test, saving partial
evidence as requests finish. Any nonzero current/historical flag or unreadable
flag stops the run. Sampling cannot prevent a sudden USB disconnect or detect
every transient fault. Temperature sampling is outside the timed HTTP request.

Private evidence: `runtime/pi5-under2-20261028/enrollment-links-v12/`,
`ready-{links,staged}-{new,old}-2core.json`. Biometric inputs and outputs are not
committed. The earlier complete experiment report remains a pre-v12 snapshot.

## Validation

Local suite: 176 passed, four optional-dependency skips; the five previously
obsolete `test_existing_pipeline.py` tests remain excluded. Focused tests cover
composition direction, geometry rejection, legacy score preservation, link
isolation/cache invalidation, and fail-closed power flag handling.
An additional copy-tool test passed, checking source-file preservation, unchanged
feature payloads, new outer tags, and exclusion of inherited benchmark results.

## Two-core new-camera HTTP comparison

Both versions returned 20/20 correct in both passes and passed queued recognition
and token cancellation, with no simulated transaction changes.

| Warm queries | v10 | v12 |
| --- | ---: | ---: |
| Correct within 2.5 seconds | 14/20 | 15/20 |
| Median seconds | 2.207 | 2.160 |
| P95 seconds | 15.188 | 15.262 |
| Maximum seconds | 15.763 | 15.790 |

One previously exhaustive query changed from 14.270 to 2.037 seconds, using the
linked route. Two other queries switched from indexed search to linked scoring,
from 2.424 to 2.215 seconds and from 2.488 to 2.123 seconds. Two difficult queries
still use full fallback, so tail latency remains unresolved. The small median
difference is not a reliable general speedup claim from a single ordered run.

Startup was 13.834 seconds for v12, with a 4.788-second first request (versus
3.100 seconds for v10's first request); preparation is not free. No power flags
were reported during completed requests. These are query-only replay results,
not a completed fresh-enrollment run or a four-core demo performance claim.

## Two-core old-camera HTTP comparison

Both versions were correct on all 20 queries in both passes, passed the queued
HTTP checks, and left simulated transaction counts unchanged. Warm v10/v12
medians were 1.767/1.771 seconds, P95 5.434/5.483 seconds, and maxima 5.736/5.681
seconds. Both achieved 18/20 correct within 2.5 seconds. No query changed routing
in this fixed replay. There is no demonstrated old-camera latency improvement.

All four completed benchmark files contain clean preflight, per-request and
post-queue power samples. The private HTML supplement is
`runtime/pi5-under2-20261028/linked-enrollment-report.html`, with per-file hashes
in `linked-enrollment-evidence.json`. Single-run ordering and CPU restriction
limit timing conclusions. Keep v12 experimental; do not claim the worst-case
latency requirement or generalization requirement is met.
