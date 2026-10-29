# Follow-up context and exact-compute pilots

Both follow-up proposals are rejected. The completed v25 Pi result remains
164/168 correct, 145/168 correct within 2.5 seconds, P95 5.926 s, max 15.210 s.
Production, thresholds, labels, accounts, templates and active images are unchanged.
The user-directed deletion and historical 170-query baseline remain separate.

## Visual diagnosis

Reviewed the actual Pi ROI and original-image/enrollment comparison sheets,
including the slowest new reverse stephen:left query
`20261020T165604274940Z-f7ec5fe1`. Its primary crop is visibly smaller than the
enrollment crops and lies nearer the finger bases. The two failed xyt:right
queries have wrist/heel/background coverage unlike the enrolled central palm.
The billy:right failure has much weaker visible fine detail and a changed
viewpoint. These observations motivate hypotheses, not proof of recoverability
or of a particular camera defect. Do not delete additional failures.

## Frozen CompNet spatial pyramid: reject on accuracy

Hypothesis: a bounded set of native-image context crops could correct ROI scale
and translation without six more expensive localizer calls. Use the original
ROI plus scales 0.5,1,2, each at center and four half-width/height translations:
15 fixed views total. Out-of-frame optional views are invalid, never clamped.
All enrolled templates remain original primary ROI embeddings.

Each query view independently scores the five enrollment frames using best-two
angular distance aggregation. The original confident decision keeps precedence.
Otherwise all confident views must agree on identity; scores are not minimized
across views. Nominal <=0.32 and >=0.08 margin are unchanged, but this changed
search still lacks unknown-person calibration.

No device/public evaluation training, filename/person branches, threshold search
or query dropping. This is an offline screen using immutable archived originals,
frozen author weights and saved Pi primary geometry, not a complete Pi replay.
Offline reuse of embeddings across splits is explicitly not runtime caching.

| Cases | Query trials | Extra confident | Extra wrong |
|---|---:|---:|---:|
| Four current device cases | 168 | 3 | 3 |
| 224 historical development splits | 4480 | 0 | 0 |

The three new wrong decisions would override correct v25 results:

| Case | Sample | True palm | Proposed wrong palm |
|---|---|---|---|
| New original | `20261020T165625070833Z-13cf34d4` | stephen:left | billy:right |
| New original | `20261020T165636416608Z-526288bd` | stephen:left | billy:right |
| Old reverse | `20261013T111339367360Z-dfb1a66b` | cyw-real:left | xyt:right |

The slowest query and four original mistakes receive no confident rescue.
No context path is registered, integrated or deployed. Do not restrict the
method to favorable identities/cases or relax gates to rescue a selected image.
The 224 correlated historical splits alone fail to reveal these regressions.

### Numerical control

The earlier offline nine-pose tool rebuilds even its zero-angle original quad
through center subtraction and addition. Four images differ from their stored
quad by 0.00000763–0.00003052 pixels. Such changes can cross interpolation
rounding boundaries; float32 GEMM also slightly changes near-1 self products,
amplified by arccos. Self-comparison never occurs in these disjoint protocols.

This screen preserves the exact stored original quad. Reconstructing the older
zero-angle arithmetic recovers its cosine-distance matrix within 3.58e-7. All
168 original-ROI confidence decisions agree with that earlier offline screen.
No historical Pi result is changed, and no numerical-control difference is
reported as an accuracy or speed gain. Five new tests cover exact original
geometry, image bounds, original precedence, conflicting candidate identities,
margin preservation and single-identity uncertainty.

Tool: `tools/screen_compnet_context.py`; proposal: `compnet_context_pilot.py`.
Evidence: `runtime/pi5-under2-20261028/compnet-context-screen-20261029-final/`.
Earlier failed parity checks are retained in the neighboring run2/run3/run4
folders; the final diagnostic explains them rather than suppressing them.

## Four-candidate ARM SIMD: reject on speed

Hypothesis: pack four gallery descriptors and reuse query loads across them,
keeping each squared-distance accumulation and final reduction tree identical.
`native/descriptor_match_block4.cpp` exposes a separate shared library and
includes the original scalar code for tail lanes. It does not replace the
original binary. Bidirectional nearest-two results, tie ordering, ratio checks,
mutual checks, ambiguity rechecks and geometric estimator are unchanged.

Actual Pi 5, one native thread (current HTTP protocol), three-core affinity,
OpenMP passive waiting, no concurrent experiment. Twenty synthetic cases
include exact/near ties, unequal sizes and incomplete SIMD blocks. Eighty real
descriptor-pair cases use four alternating-order timing repetitions each.
Indices, distances and resulting transforms are identical in every case.

| Median per real pair | Milliseconds |
|---|---:|
| Original | 23.314 |
| Four-candidate | 24.190 |

The candidate is about 3.8% slower; no HTTP improvement is claimed or further
full replay performed. All 102 recorded power flags are 0x0. The benchmark now
has explicit power-abort and odd-size audit options; defaults remain unchanged.

Build in an isolated directory on Pi:

```sh
g++ -shared -fPIC -O3 -march=armv8-a+simd -fopenmp \
  descriptor_match_block4.cpp -o descriptor_match_block4.so
```

Tool: `tools/benchmark_native_variants.py` with `--threads 1 --odd-sizes
--abort-on-power-fault`. Evidence: `block4-native-pilot-20261029/threads1.json`.
Candidate binary SHA256:
`495e30ea051def4594f343123855f3472046635f6ef90a23295c70f5cadec46b`.
Original library SHA256:
`272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600`.

The hardest tail still needs reliable corresponding-palm evidence. Neither
broader candidate search nor this lower-level optimization solves it.
