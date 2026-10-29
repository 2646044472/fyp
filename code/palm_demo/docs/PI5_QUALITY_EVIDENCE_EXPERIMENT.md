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

### Immediate query after each new enrollment

Additional empty-gallery experiment on the new-device original split registers
one identity, immediately queries its sixth image, then registers the next.
No query input primes the model; generic zero-input startup took 1.379 s.
Actual capture/hand-placement time remains unmeasured: frame reads are JPEG
decode at the camera boundary. The current production flow processes each
frame fully before taking the next frame, so the user must not assume a rapid
five-frame burst followed by all processing in the background.

| Gallery identities after registration | Five-frame enrollment HTTP s | Last frame read to ready s | Immediate first query s | Correct |
| --- | ---: | ---: | ---: | --- |
| 1 | 47.206 | 14.742 | 11.446 | Yes |
| 2 | 45.849 | 15.382 | 1.133 | Yes |
| 3 | 47.392 | 16.787 | 1.615 | Yes |
| 4 | 51.338 | 20.193 | 2.320 | Yes |

The one-identity case cannot pass the existing two-candidate margin gate and
therefore uses complete fallback. This is a general gallery-size boundary,
not an image-specific failure. It needs a separately justified verification
policy or faster fallback, not removal of the confidence guard. Five-image
registration itself is currently too slow to describe as a convenient instant
on-site experience. Precomputation moves work into registration; it does not
make that work disappear.

Per-frame primary ROI, alternate ROI, complete feature, gallery preparation,
descriptor-index and enrollment-link timers are saved in
`quality-v24-on-site-new/result.json`. They overlap and should not be summed.
Each frame took 7.108-8.684 s including primary ROI (usually about 1.04 s,
occasionally 2.08 s), alternate ROI (about 3.07 s) and complete features
(2.868-3.928 s). Gallery preparation after identities 1/2/3/4 took
2.918/4.655/6.457/8.502 s respectively. Descriptor-index construction alone
took 1.155/2.026/2.952/4.007 s; the enclosing index-plus-enrollment-link stage
took 2.157/3.935/5.740/7.765 s. This confirms expanding-gallery rebuild costs,
not merely a fixed per-person registration cost. Template persistence and
remaining HTTP work are included in enrollment totals but not separately timed.

A separate fresh Python process then loaded the four saved identities:
generic model startup 1.385 s, app/gallery cache rebuild 13.780 s, followed by
a correct first query in 1.848 s. This is process restart, not a Pi reboot.
No query sample was used for warmup; simulated transactions were unchanged.
The model and cache preparation time is paid before the first query and must
be displayed as startup preparation, not hidden in a claim of instant readiness.

### Lossless enrollment-cost improvements

Unchanged prepared identity snapshots now retain their within-identity links
when another identity is registered. Snapshot order/replacement invalidates
that identity only; removal evicts links and strong references. No query result
or feature is cached. This does not yet make the global FLANN index incremental.
Tests exercise addition, replacement, reordering, deletion and re-addition.
The complete 224-split development audit remains 20/20 throughout, with exact
per-identity score and route equality on all 4,480 queries against prior v24.
Evidence: `quality-v24-link-cache-all/`.

With link reuse alone, sequential new-device enrollment took
47.264 / 44.764 / 45.416 / 48.561 s (identities 1 through 4), compared with
47.206 / 45.849 / 47.392 / 51.338 s before. At identity four, last-frame-read
to ready decreased from 20.193 to 17.446 s. All immediate queries were correct;
the single-identity fallback still took 11.377 s. These are sequential runs,
not an interleaved statistical latency study.

An isolated Pi benchmark also compared standard lossless NPZ compression:
eight writes/reads at each level across all four new-device templates, with
forward/reverse level order and exact dtype/array equality on every read.
Mean level-6 save/read: 3.398/0.357 s, 28.042 MB. Level 1: 2.210/0.317 s,
29.372 MB (+4.7%). No compression: 1.924/0.080 s, 83.886 MB. The experimental
v24 factory now opts into level 1; ordinary TemplateStore clients and production
v6 keep the original default. Existing NPZ readers and template payloads are
unchanged. The source templates were untouched. Evidence:
`template-io-quality-v24.json`.

Combined link reuse + level-1 compression, fresh Pi enrollment and immediate
query (same fixed new-device images):

| Gallery identities | Enrollment s | Last frame read to ready s | First query s |
| --- | ---: | ---: | ---: |
| 1 | 45.968 | 13.488 | 11.422 |
| 2 | 43.099 | 12.573 | 1.134 |
| 3 | 45.114 | 14.499 | 1.618 |
| 4 | 47.434 | 16.235 | 2.382 |

All four first queries were correct. Newly instrumented template save times
were 2.536/1.385/2.271/2.414 s; prepare_enrollment was
0.402/0.360/0.362/0.373 s. Total gallery preparation was
2.880/3.582/4.508/5.675 s. At four identities the unchanged full index took
4.011 s, and index plus the new identity's links took 4.984 s. Thus the former
identity-dependent link rebuild growth is removed, but the full index still
grows. Source hashes and overlapping stage events are retained in
`quality-v24-on-site-link-cache-fastzip-new/result.json`.

A fresh process still needed 1.375 s generic model startup and 13.588 s gallery
rebuild, followed by a correct 1.833 s query. In-memory link reuse does not
survive process restart. Reprofiling all three previously over-budget reversed
queries twice retained exact reference scores/routes; the hard fallback still
took 13.911 s on the second repetition. This optimization reduces registration
cost, not the remaining hard-query tail. Power flags remained zero.

205 tests passed, four optional skips (same obsolete-test exclusion).

Two further **unadopted offline screens** reused the existing auxiliary ROI
codes without changing thresholds. Across 1,926 non-confident primary-pose
queries from the same 224 splits, comparing query poses against auxiliary
gallery codes gave 407 confident results; comparing auxiliary query codes
against primary gallery codes gave 433. Neither screen had a wrong confident
result on this development cohort, but **neither rescued any v24 complete
fallback**. They therefore do not solve the current tail and are not integrated.
These screens have no Pi timing or independent validation. Evidence:
`gallery-pose-screen.json`, `query-pose-screen.json`. The next relevant
experiment is staged auxiliary-ROI geometric registration, with full fallback
and fixed guards retained; direct code comparison alone was insufficient.

### Capacity and independent validation (still pending)

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
