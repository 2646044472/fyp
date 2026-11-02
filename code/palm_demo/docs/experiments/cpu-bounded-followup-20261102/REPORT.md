# CPU bounded follow-up — 2026-11-02

Two isolated experiments completed. The real 86-identity gallery lifecycle
released the observed owners and approximately 2.69 GiB of residual RSS after
the epoch returned. A four-image global-SIFT geometry audit produced no valid
registration and was rejected before identity scoring. No recognition accuracy
gain or GPU/Pi speedup is established.

The standard recognizer, recognition thresholds, original enrollment frames,
labels and original query images were not changed. The existing SMPD full run
remains at its paused STOP boundary; neither old experiment was resumed. These
are Windows, previously exposed development data, not independent evaluation
or unknown-person FAR evidence. Current developer model identifier is
`gpt-6.1-sol`; there is no independent runtime-model receipt.

## Real-gallery lifecycle

Private artifacts: `runtime/gallery-lifecycle-20261102-r1/{protocol,results}.json`,
the archived executed driver, and one-second `telemetry.jsonl`. The protocol
locks the original 86 template-container hashes and model hashes. It copies
the existing containers into a new runtime and uses the normal v27 App,
gallery preparation and search index. All 86 identities and 430 original
enrollment frames were present. There were 430 normal gallery-embedding
inferences, zero localizer inferences, zero fresh enrollment attempts, zero
identity scores and zero HTTP requests. No HTTP socket/server was created.

The same previously documented Windows-only 2 GiB index / 6 GiB prepared-cache
capacity allowance was used; the Pi configuration and original files were not
edited. Recognition logic and feature selection were unchanged. Original
template hashes and the public STOP/status hashes matched after the run.

| Boundary | Worker RSS, GiB | Host available, GiB |
| --- | ---: | ---: |
| Initial startup gate | 0.0216 | 13.3926 |
| Epoch startup, after copies/imports | 0.1005 | 12.4954 |
| Complete gallery/index ready | 9.4532 | 4.9561 |
| Closed and GC inside still-live epoch | 2.8428 | 11.5711 |
| Epoch returned, explicit GC completed | 0.1538 | 14.3028 |

The original limits remained startup available RAM >=12 GiB, running available
RAM >=2 GiB, worker RSS <=14 GiB. Peak process working set was 9.4532 GiB;
one-second sampled minimum host available RAM was 4.3005 GiB. No sampled or
boundary limit violation occurred. The minimum available sample is a different
instant from the gallery-ready boundary; it is not interchangeable with that
boundary reading.

The inside-epoch collection collected zero objects, while App, matcher,
localizer, both ONNX sessions and the final prepared-frame array remained
reachable. After returning, `collect_finished_epoch()` collected 3,321 objects;
all six observed weakrefs were dead. RSS fell by 2.6889 GiB. At that instant,
the unchanged 12 GiB next-start gate would pass. This is a real-gallery
ownership and working-set result, beyond the earlier synthetic App test.

Lifecycle wall time, including session/gallery construction and cleanup, was
168.494 s with 165.188 CPU-seconds, approximately 0.980 average CPU cores.
Whole worker wall time, including copying, verification and imports, was
179.215 s. The CPU number is low-load process-time sampling, not a per-function
profiler or query latency. The one-second sampler is included in worker CPU.
The six weakrefs do not enumerate every native allocation. One lifecycle does
not establish repeated-load stability, second-epoch initialization latency,
query correctness or exact causality for the earlier failed startup gate.

## Global-query SIFT geometry prerequisite

Private artifacts: `runtime/global-sift-geometry-20261102-r1/{protocol,results}.json`
and the archived executed driver. The protocol was written before matching.
The previously fixed D1-D4 panel was reused: two remaining device errors, one
correct terminal control and one correct fast control. Every image was
compared against all 11 identities and all five original enrollment frames.

The query descriptor was deliberately new: one native grayscale full-image
view, uniformly resized to long side <=1536, normalized with the existing
1st/99th percentile routine, and the existing 1000-point RootSIFT extractor.
Enrollment descriptors were the unchanged stored primary 384px ROI SIFT.
No model was loaded or inferred. Native query points were mapped through the
frozen primary matrix solely to express the existing similarity-fit scale,
angle and coverage limits in their original coordinate convention. Before the
run, all four coordinate roundtrips were exact in float32; D1/D2 primary
matrices also matched their earlier saved diagnostic matrices exactly.

The existing mutual .85-ratio matching and seeded similarity registration
were used. Anchor overlap was measured, not used to discard global fits in
this observational diagnostic. A prospective prerequisite required at least
two distinct enrollment frames with pairwise ROI IoU >=.5 for the true identity,
and no wrong identity with equally supported geometry, for both error cases.
Truth labels were consulted only after every gallery registration. No identity
or distance was used to choose a query crop.

| Panel role | Query SIFT points | Attempts | Accepted fits | Geometry wall, s |
| --- | ---: | ---: | ---: | ---: |
| D1 error | 1000 | 55 | 0 | 1.304 |
| D2 error | 1000 | 55 | 0 | 1.269 |
| D3 correct terminal | 740 | 55 | 0 | 1.077 |
| D4 correct fast | 1000 | 55 | 0 | 1.602 |

All 220 attempts returned no transform from the existing combined
correspondence/geometry gate. That gate did not log the separate rejection
substage, so this does not identify ratio failure versus fit/coverage/angle
failure. Both originally correct controls also failed this new descriptor
combination. It is consequently unjustified to infer absent palm texture or
irrecoverable capture quality from these observations.

The gate failed, so there was no recognition integration, FastCC scoring,
threshold adjustment, additional image view, retry or full168 replay. There
are no new correct/wrong/rejected recognition counts: zero identity-scoring
requests were made. The listed durations are geometry-diagnostic wall times,
not HTTP query latency or a speedup claim. Process peak working set was
0.5203 GiB; total worker wall time was 7.294 s. Original image/template hashes
and the public STOP/status hashes remained unchanged.

## Decision

The post-return collection now has one real-gallery resource validation. Keep
it as an experiment-lifecycle measure without changing recognition policy.
Retire this global-query/existing-ROI descriptor combination. The earlier
rotation-quorum and common-pose rules also remain rejected. None of these
results qualifies a recognition change for full168 evaluation or deployment.
