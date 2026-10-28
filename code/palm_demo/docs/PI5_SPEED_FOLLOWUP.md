# Pi speed follow-up, 2026-10-28 to 2026-10-29

The production Pi still runs v6. The opt-in v10 experiment makes typical queries
substantially faster while retaining exhaustive search for uncertain results.
It does **not** satisfy a universal two-second identification limit. Do not
deploy it based on a median or interpret development splits as new people.

## Actual Pi HTTP replay

These are fresh isolated enrollment/query runs, using OpenCV 4, ONNX 4 and native
registration 4 threads. All queries, errors and times remain in the denominator.
Acquisition is file replay; no live camera or preview-contention claim is made.

| Cohort | Correct | Correct within 2 s | Median | P95 | Maximum |
| --- | --- | --- | --- | --- | --- |
| New camera | 20/20 | 15/20 | 1.554 s | 11.023 s | 11.185 s |
| Old camera | 20/20 | 18/20 | 1.419 s | 4.638 s | 4.658 s |

New-camera routes: 3 pose, 9 legacy registration, 5 normal-context index, and
3 exhaustive fallbacks. The three full searches take about 10–11 seconds.
Two other queries take 2.483 and 2.011 seconds. Old-camera routes: 16 pose,
2 legacy registration, and 2 full searches taking 4.637 and 4.658 seconds.
These slow results are not removed, relabeled as retries, or counted as fast.
All 40 new-camera originals are 1920x1080 (16:9); all 40 old-camera originals
are 3280x2464 (approximately 4:3). `window_candidates` adds three 4:3 windows,
each at original/gamma exposure, for the wide new images. On the measured Pi,
those six additional forwards alone cost roughly 2.7 s before descriptor work.
This explains a concrete obstacle to a two-second exhaustive fallback without
changing that search architecture; it is not a proof that every alternative
algorithm is incapable of meeting the target.

Five-image enrollment median is 41.838 s (new) and 19.094 s (old); indexed
enrollment is substantially more expensive than v6. Peak RSS is 2,268,053,504
and 1,274,478,592 bytes respectively. All eight simulated payments and their
cancel/replay checks pass. All original input hashes remain unchanged.

## What changed

The final v10 cached audit completes all 224 unchanged development splits:
112 new-camera and 112 old-camera splits, each 20/20. This recovers the recorded
v7/v8 regressions but is not independent validation. The final Python suite is
151 passed, two skipped, explicitly excluding the pre-existing obsolete import
in `tests/test_existing_pipeline.py`. Node demo interaction checks pass.
That excluded file contains five legacy tests against the removed `palm_demo`
API (including `parse_crop`); it is not claimed to pass. The two actual skips
are the exported PalmIR model/matcher tests in `test_palmir_restore.py:43,59`,
because Windows Anaconda lacks `onnxruntime`, confirmed with `pytest -rs`.

Fresh-process query-only repeats (without model priming) preserve 20/20 in each
pass. New-camera first/warm medians are 1.758/1.547 s, each 14/20 within 2 s;
the first query is 2.422 s and index startup is separately 6.778 s. Old-camera
medians are 1.424/1.426 s, 17/20 then 18/20 within 2 s; first query is 2.310 s,
startup 3.946 s. Two simultaneous new-camera requests finish at 1.546/12.540 s;
old-camera requests at 1.414/2.819 s. Both queues return the expected users,
all tokens are cancelled, and transaction counts remain unchanged. Queueing and
cold-start costs therefore do not support a blanket two-second promise either.

`StagedIndexMatcher` uses the existing 0.32 distance / 0.08 margin routing rule
at successive stages: pose bank, legacy registration, normal context, wider
context, then the original full v6 search. It never uses a subject or sample ID.
Each later stage preserves earlier pair distances. The original image and
localization candidates are retained for lazy full extraction. If that fallback
is unavailable, an uncertain query fails rather than silently accepting a guess.
This confidence rule is still a development heuristic, not unknown-person
calibration or an equivalence proof on unseen people.

The ARM64 kernel computes every descriptor distance once and retains nearest
neighbors in both directions. It preserves the ratio, mutual-match and geometric
guards. Near numerical ties are checked with the original OpenCV BF matcher.
Its 80-pair real-descriptor benchmark has identical transforms and a median
7.128 ms versus 11.855 ms for the reference. A separate, deliberately untimed
20-query audit compares all 4,760 registrations against the reference and finds
no changed transform. Synthetic duplicated and nearly tied descriptors also pass.
That finite evidence does not constitute a universal floating-point proof.

Native loading is explicit and scoped to one matcher instance. No source is
compiled automatically, no library is loaded by default, and other instances
retain the reference implementation. The kernel requires ARM64 NEON/OpenMP.

## Failed alternatives are retained

- Dense shared matrices through OpenCV GEMM and NumPy preserve the tested
  transforms but take about 70 ms versus 12 ms on this Pi; they are not enabled.
- Heatmap-only ONNX graph pruning reduces the file from 67.7 to 21.9 MB and keeps
  all 160 tested original/gamma outputs bit-identical. Median inference changes
  only from 460.15 to 450.31 ms, with worse measured P95. The full diagnostic
  model remains in use; there is no model retraining or quantization.
- Proposal-only v8 reaches 2.452 s new-camera median but has five 19/20 splits
  among the 112 new-camera development splits. All old-camera splits are 20/20.
  It is not accepted as an accuracy-preserving replacement.
- Unstaged guarded v9 gives 2.474 s new-camera median and 12.156 s P95. Its
  superseded cached audit was stopped after 89/224 completed cases, all 20/20;
  those results remain preserved and are not presented as a complete audit.
- A fixed centered-letterbox preprocessing experiment passes geometric checks
  for all 40 new images, but its legacy-stage recognition over all 112 unchanged
  new-camera splits averages 18.143/20 versus 18.625/20 for the original padding;
  both have a minimum of 16/20. Confident queries rise only from 1,723 to 1,763
  out of 2,240 correlated development queries, with no confident errors in
  either tested set. This does not justify replacing preprocessing. All 40
  old-camera inputs are unchanged by centered padding (their offset is zero).
  This is a legacy-stage comparison, not an evaluation of a complete centered
  v10 pipeline. The experiment is not integrated; no weights were retrained.

The four reserved people / 80 old-camera images remain unevaluated. The existing
80 development images and their repeated splits do not establish independent
new-camera or cross-session accuracy. The two-second tail-latency gate remains
unmet, so the reserved cohort is not being consumed for tuning.

## Reproduce in an isolated Pi checkout

```sh
mkdir -p runtime/native-build
c++ -O3 -mcpu=cortex-a76 -fopenmp -shared -fPIC -ffp-contract=off \
  native/descriptor_match.cpp -o runtime/native-build/descriptor_match.so
OMP_WAIT_POLICY=PASSIVE python tools/replay_demo_manifest.py inputs/new.json fresh-output \
  --opencv-threads 4 --onnx-threads 4 --demo-matcher FastCCStagedIndex-v10-experimental \
  --native-registration runtime/native-build/descriptor_match.so
OMP_WAIT_POLICY=PASSIVE python tools/replay_ready_queries.py fresh-output fresh-ready.json \
  --native-registration runtime/native-build/descriptor_match.so
python tools/audit_indexed_demo.py runtime/roi-palmir-20261028 fresh-split-audit \
  --matcher FastCCStagedIndex-v10-experimental
```

`fresh-output` and `fresh-ready.json` must not already exist. The ready-query tool
recomputes every query twice, reports startup separately, tests two queued HTTP
requests, cancels their tokens, and checks that simulated transaction counts do
not change. It does not precompute query identities. Its optional model priming
uses zeros and is charged to startup time, never hidden inside a latency claim.
The cached split-audit command runs on the original-data host (currently Windows),
where paths in `stability/records.json` exist; it is not a Pi latency benchmark.

Local private evidence is under `runtime/pi5-under2-20261028/`, including
`pi-staged-{new,old}-summary.json`, `ready-staged-{new,old}.json`,
`staged-final-all-splits/`, `query-native-verify.json`, and `heatmap-parity.json`.
These biometric artifacts and compiled binaries are not committed.
