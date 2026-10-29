# Pi 5 quality-evidence development experiment, 2026-10-29

Candidate: `FastCCQualityEvidence-v24-experimental` (magic 2801064).
This is an isolated experiment. Production v6 is unchanged. Local device data
is the priority; public datasets are reserved for evaluation after freezing.

## Method

Two independent legacy SIFT views now run on the existing worker pool. Pooled
correspondence medians are batched by observation count. These optimizations
preserve the mathematics: scalar reference tests pass, and all 80 original /
reverse development queries retain exactly the v20 scores and routes.

After unchanged early pose, legacy, enrollment-link, affine and pooled checks
remain uncertain, v24 tries response-weighted FastCC evidence. The original
17-by-17 filter produces signs and sqrt(abs(response)) weights, sampled every
four pixels. The outer two feature rows/columns are masked because they depend
on convolution padding. Query/enrollment pair weights are multiplied; the
weighted mismatch fraction is minimized over the existing shifts and nine
fixed poses. Crops must remain within the original image. Best-two enrollment
aggregation is retained.

This is a **new distance**, not an exact Hamming acceleration. When the entire
gallery passes the existing .32 / .08 routing gate, all pair scores are replaced
together. Otherwise ordinary scores and complete fallback remain. Scores from
the two metrics are never combined by taking their minimum. No identity/image
special cases or cached query answers are used. The numerical gates are not
relaxed, but their unknown-person rejection calibration does not automatically
transfer to the new metric.

## Protocol and evidence

Original development data: 80 images, separate new/old device runs, four palm
identities per device. The 224 fixed cached-feature splits all scored 20/20.
This is a repeatedly used development cohort, not independent validation.
The already exposed reserved cohort and public datasets did not guide this
candidate. The historical reserved maximum of 10.681 seconds has not been
remeasured with v24.

Pi 5 8 GB, affinity 0/1/2, ORT 3, OpenCV/native 1, OMP_WAIT_POLICY=PASSIVE.
HTTP timings include original-image read, preprocessing, ROI, features,
search/registration, scoring and loopback response. Camera capture and external
upload are excluded. Power is sampled outside timed requests; any nonzero or
unreadable throttle flags abort the run and preserve partial evidence.

The shuffled protocol uses seed 20261029. Model startup is primed on zeros,
counted separately; each real query is recomputed. Fresh-enrollment checks
create empty isolated databases, register five images per identity, query the
other five, and exercise simulated confirmation, duplicate confirmation,
cancellation and cancelled-token rejection. Reverse swaps indices 1-5 with
6-10 for every identity, without selecting images from observed results.

Evidence resides in ignored `runtime/pi5-under2-20261028/`: `quality-v24-all/`,
`ready-quality-v24-*.json`, and `quality-v24-fresh-*/`. Generate the full HTML
table with `tools/report_quality_evidence.py EVIDENCE OUTPUT.html`.

## Pi HTTP results

| Protocol | Correct | Correct <=2.5 s | Median s | Maximum s |
| --- | ---: | ---: | ---: | ---: |
| New, reused templates, warm | 20/20 | 20/20 | 1.825 | 2.451 |
| Old, reused templates, warm | 20/20 | 20/20 | 1.457 | 1.920 |
| New, model primed, shuffled first pass | 20/20 | 20/20 | 1.826 | 2.453 |
| New, model primed, shuffled warm pass | 20/20 | 19/20 | 1.839 | 2.532 |
| Old, model primed, shuffled first pass | 20/20 | 20/20 | 1.478 | 1.973 |
| Old, model primed, shuffled warm pass | 20/20 | 20/20 | 1.469 | 1.943 |
| New, fresh original enrollment | 20/20 | 20/20 | 1.825 | 2.423 |
| New, fresh reversed enrollment | 20/20 | 17/20 | 1.808 | 13.886 |
| Old, fresh original enrollment | 20/20 | 20/20 | 1.460 | 1.944 |
| Old, fresh reversed enrollment | 20/20 | 20/20 | 1.483 | 1.662 |

Fresh runs exercise 80 queries in total, all correct; 77 meet 2.5 seconds.
Each of the four runs creates four isolated simulated transactions and passes
duplicate-confirmation/cancellation checks. All original hashes remain unchanged.
The reversed new run exposes a genuine full-search tail, not a stable <=2.5 s
result. Its slowest image is `20261020T165604274940Z-f7ec5fe1`; all failures
remain in the report. Two other reversed new requests took 2.791 s (legacy) and
3.047 s (pooled). Timing jitter also crosses the budget in the shuffled run.
All 268 fresh-workflow power samples reported `throttled=0x0`. Five-image
registration median was 46.4-47.9 s new and 20.8-22.0 s old; it is not included
in query latency and still needs improvement for a convenient enrollment UX.

Profiling all three over-budget reversed queries twice preserved exact identity,
scores and routing relative to their original HTTP results. The slowest repeat
was 13.889 s: initial gating at 1.187 s, unsuccessful early searches through
2.589 s, followed by approximately 11.300 s in full fallback. Full alternate
ROI generation took 3.068 s, complete feature extraction 3.413 s, and summed
complete per-identity matching 4.790 s. Instrumentation overlaps (and some jobs
run in parallel), so these stage times must not be summed as disjoint latency.

The weighted rescue also correctly refused an unsafe shortcut in this case:
its best distance was .351 for the wrong identity, while the true identity
scored .375. Both the absolute and margin gates failed. Lowering the gate or
blindly accepting top-1 would therefore sacrifice correctness. The other two
over-budget queries each spent about 2.035 s in localization before matching.
Next optimization should address alternate ROI coverage/early alignment and
localization retries as separate causes, preserving rejection safeguards.

## Remaining limitations

Neither four palm identities nor repeated development splits establish
40-person readiness. The current 256 MiB prepared-cache/index limits and
gallery-wide registration must be addressed before claiming that capacity.
Two hands per person are two palm identities. Live capture, new collection
sessions and unknown-person rejection remain unvalidated. Concurrent requests
are serialized and include queue delay; startup and registration are not
two-second operations.

## Verification

198 tests passed, four optional tests skipped, excluding the obsolete
`tests/test_existing_pipeline.py`. New tests check weighted scoring against
the direct scalar definition, missing support, image bounds, padding masks,
preservation of ordinary scores on uncertainty, whole-gallery replacement and
skipping rescue after an already confident result.
