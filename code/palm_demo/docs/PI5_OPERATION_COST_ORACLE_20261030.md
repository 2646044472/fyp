# Pi operation-cost and full-SIFT oracle diagnosis — 2026-10-30

## Scope and actual call graph

Frozen v26/active169, five predefined difficult queries (all four wrong plus global slowest) and the lexicographically first fast correct control in each of their three cases. No labels, thresholds, inputs, gallery frames or public evaluation data change. Production is not deployed. Cost rows are anonymized separately from the private sample-to-case selection.

The actual recognition call graph is:

```
POST /api/demo/identify
  DemoFlow.identify
    capture_feature -> App.capture_demo_feature
      read original -> PKLNet original/gamma (aspect retry when required)
      extract_probe_with_context -> nine fixed query poses
    Gallery.identify
      load already-prepared per-identity five-frame groups
      StagedIndexMatcher.score_gallery
        all identities x five frames x valid poses -> best-two mean -> confidence
        primary CompNet then existing alternate base ROI -> separate score/gate
        cached enrollment index + query primary/secondary RootSIFT
        all five-frame legacy scores -> confidence
        enrollment-link / affine / pooled / quality stages -> confidence
        normal and wide contexts: each two blur views -> index proposals
          identity x frame x proposed target views -> validate warp -> score
        if still uncertain: probe.exhaustive()
          complete_hypotheses: base views + six window localizations if needed
          extract_with_hypotheses: context/blur SIFT, native PNG, packed envelope
        for each identity, sequentially:
          FastCCDemoMatcher.score_prepared
            worker map over all five frames:
              _match_unpacked(shared prepared query, prepared frame)
                legacy: min over query poses and accepted primary/blur alignment
                loop all compatible sigma/hypothesis views:
                  native descriptor pairs -> seeded RANSAC -> geometric guards
                  original-image warp -> bounds/anchor overlap
                  FastCC binary feature -> shifted-overlap distance
                minimum of all accepted per-frame branch distances
            identity distance = mean(sorted(five frame distances)[:2])
      rank all identities -> final threshold=1.0 / min_margin=0
    simulated pending token (only canceled in this diagnostic)
```

The five-frame map is inside an outer sequential identity loop. Prepared enrollment data and a single unpacked exhaustive query are already shared across those five comparisons. Existing stages have several confidence checks; they are not the final unknown-person policy. FastCC compares 32x32 binary codes over 81 shifts, with each shift's overlap-area denominator. A large number of keypoints/low pose distance is not proof of valid anatomical correspondence.

## Previously tested nodes versus this diagnosis

| Node | Existing route and evidence | This round |
|---|---|---|
| Identical local-feature/registration inputs | Within-query exact memoization preserved old outputs, saved about 12–16.5%, still slow; retained as isolated tool | Not rerun as a new optimization |
| Shared exhaustive query across frames | Already one unpacked query fed to per-frame scoring | No new reuse claimed |
| Enrollment links/index/template preparation | Already cached and separately timed at ready/rebuild | Remains unchanged |
| Lazy subset of identical hypotheses | 11/13 current fallbacks cannot meet the unchanged .32 distance gate even with full evidence | No early-return relaxation |
| Extra window ONNX session | Shared-session ABBA pilot saved first-use setup but only 56ms warm; rejected sustained gate | Baseline separate-session behavior retained |
| All SIFT operations, including unique inputs | No real implementation can assume answers are available before extraction | Recorded outputs replayed only as an oracle cost bound |

No new deployable exact reuse node is established by this source audit. The oracle is deliberately more generous than the old duplicate-only memoization and does not rename it as a new performance candidate.

## Measurement and replay protocol

Eight unique selected queries, five phases each: (1) real execution with operation recording and private-memory SIFT snapshots, (2) ordinary real execution before, (3) replay with full byte-hash/array-equality input validation, (4) timed replay with structural call position, shape/type and complete call-set checks but no hash/profiler, (5) ordinary real execution after. Final identity, status, full-precision best/second scores, route and displayed ROI bytes must match frozen v26 in every phase. A mismatch stops the experiment; failures are preserved. Only after the two-query pilot passed did the remaining six run.

Feature replay is keyed by generic executor task paths and per-call position; task paths follow submission order and remain valid across scheduling changes. It is not an image/person rule. Stored SIFT input/output arrays exist only in private RAM, are capped at 256MiB accounted array bytes, copied defensively, and discarded after each query. They are never serialized or uploaded. Replay checks that every recorded call is consumed. No recognition result/token is replayed; downstream matching and HTTP handlers execute normally.

Operation recording captures actual call count, input/output shape, dtype, byte count and contiguity. It wraps ONNX inference, SIFT/RootSIFT, native descriptor matching, FastCC feature/distance calls, warps/RANSAC, packing/PNG codecs and explicit NumPy allocation/conversion calls. Implicit ndarray `.astype`/slice assignments remain inside their parent operation; conversion-call bytes do not imply an actual physical copy occurred.

Same-thread nested intervals subtract direct children for exclusive wall and issuing-thread CPU time. Across threads, interval union yields a non-overlapping wall partition; simultaneous different categories are explicitly mixed bins rather than added twice. Worker native threads inside ORT are not issuing-thread CPU: whole-process CPU is measured once per HTTP, and the remaining native/background CPU is left unattributed. These CPU scopes must not be equated. Metadata/hash/copy validation overhead is recorded separately from real operator spans; profiling HTTP itself is not a production latency result.

The timed replay omits content-hash validation after the separately successful validated replay; defensive output copies and structural checks remain timed. All ordinary-before/after and downstream response checks are retained. Even a near-free SIFT oracle is not a deployable algorithm, and the remaining HTTP cost is not a mathematical lower bound on every redesigned system.

## Completed results

All 40 responses (eight queries, five phases) preserved frozen identity, status, full-precision best/second scores, route and actual displayed ROI bytes. No template mutation or power fault occurred. The separate numerical audit then ran two phases on all five hard queries: **all ten whole-gallery score dictionaries** matched frozen v26 exactly, and all **225 per-frame scores** matched between record and validated replay. Their best-two aggregation also exactly reconstructed each identity score. These are parity checks, not additional speed trials. The evaluator was extended to collect these numeric fields after the original timing jobs; its source hashes are preserved separately in each input file.

| Anonymous query | Role | Ordinary bracketing median ms | Timed SIFT-output oracle ms | Actual SIFT calls |
|---|---|---:|---:|---:|
| C01 | Fast correct control | 1204.395 | 1163.65 | 0 |
| C02 | Wrong MATCH | 4351.920 | 2524.58 | 28 |
| C03 | Fast correct control | 1848.010 | 1748.01 | 2 |
| C04 | Slowest correct | 14333.460 | 10714.01 | 48 |
| C05 | Fast correct control | 1540.465 | 1533.78 | 0 |
| C06 | Wrong MATCH | 8068.740 | 6209.31 | 28 |
| C07 | Wrong MATCH | 10228.035 | 8260.92 | 28 |
| C08 | Wrong MATCH | 9361.865 | 7419.51 | 20 |

Even removing real SIFT extraction through an oracle leaves all five hard queries above 2.5 seconds. C02 is only 24.58ms over and should not be interpreted as a robust lower-bound violation. The other four remain far over budget; SIFT optimization alone cannot explain a solution. No identity is corrected by this cost oracle.

C04's instrumented request took 15,463ms with whole-process CPU 30,922ms and summed issuing-thread exclusive CPU 22,172ms. Its additive global wall partition includes inference 3,928ms, distance matching 5,501ms, SIFT 3,588ms, framework 1,380ms, transforms 224ms and geometry 206ms (rounded, smaller categories omitted here). Native descriptor pairing ran **1,248 times**, operation wall union 5,702.62ms, issuing CPU 9,619.3ms, with inputs up to 1000x128 float32. The ONNX calls were eight PKLNet inputs `[1,3,400,300]` float32 and two CompNet inputs `[1,1,128,128]`. FastCC matching itself was 814 calls, wall union 132.91ms. These per-operation unions overlap other operations and must not be added to the global partition.

C07 had 1,155 native descriptor-pair calls, wall union 5,128.71ms and issuing CPU 8,368.53ms; four ONNX calls consumed 1,003.98ms. Its 1,487 FastCC matches consumed 248.05ms union wall. Explicit `ascontiguousarray` call unions were only 8.72ms (C04, 2,820 calls) and 8.73ms (C07, 2,634 calls); counting their bytes as actual copy cost would misdiagnose the bottleneck. Native matching, model inference and feature extraction remain substantive; there is no evidence for a large generic packing/copy win.

Scalar per-call input/output specifications, operation counts, CPU scopes, interval partitions and provenance are in [OPERATION_COST_ORACLE_20261030.json](protocols/OPERATION_COST_ORACLE_20261030.json). Numerical parity counts are in [ACCURACY_DIAGNOSTICS_20261030.json](protocols/ACCURACY_DIAGNOSTICS_20261030.json). Frozen formal recognition remains **164/168 correct, 146/168 correct within 2.5s**, P50 1540.17ms, P95 6019.3185ms, maximum 15225ms. Do not replace those formal figures with oracle timings.
