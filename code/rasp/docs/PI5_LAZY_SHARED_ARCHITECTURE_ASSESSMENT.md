# Exact shared/lazy fallback assessment (2026-10-30)

Assessed architecture: compute each broad-query feature once, reuse it across
templates, and defer further ROI hypotheses until needed. No candidate was
integrated or deployed. This round reads saved evidence and source code only;
it is not a new recognition run or Pi benchmark.

The latest complete Pi reference stays 164/168 correct, 146/168 correct within
2.5 s, P95 6.019 s, max 15.225 s. Four wrong-identity MATCH responses and zero
explicit rejections remain. Unknown-person FAR and verification FRR are not
measured. Historical 170-query/deleted-image cohorts remain separate.

## Why this was considered

The current full fallback constructs legacy features, two expanded-context
views and the complete base/window hypothesis set before gallery matching.
The measured hard query spends 3.08–3.97 s on additional localization,
3.42–3.47 s constructing fallback features, then about 5.11 s matching. A
shared, demand-driven feature graph would avoid eagerly repeating operations
and could move useful evidence earlier.

However, this proposal has two distinct parts that need separate claims:

1. Reuse exactly identical computations while still completing the full score.
2. Stop after a subset of the existing hypotheses passes the existing gate.

## Exact reuse is already a tested route

[PI5_SPEED_FOLLOWUP.md](PI5_SPEED_FOLLOWUP.md), "Bounded fallback reuse audit",
records the previous exact-input per-query SIFT/registration memoization pilot.
It preserved outputs and reduced warm historical slow-query times by about
12–16.5%, but new-device queries still took 9.06–9.51 s. Extra localizer inputs
were not duplicates. These are that older development protocol's timings,
not a prediction or fresh benchmark of v26. The defensive-copy version of the
tool is also not the version benchmarked in that historical table.

Therefore another hash/memoization wrapper is not a materially new architecture
experiment. It was not rerun. Enrollment-link reuse, the v26 alternate base ROI
and existing template/index preparation are already separately implemented and
reported; they must not be counted again as new gains.

## An unchanged-score early-stop obstruction

For one template, the exhaustive score takes the minimum of its legacy/pose
distance and accepted registration/hypothesis distances (`union_matcher.py`,
`_match_unpacked`). A subset of the same hypotheses cannot have a smaller
minimum than the full set. The identity score is the average of its best two
enrollment-template distances (`demo_matcher.py`, `score_prepared`); this
aggregation is monotone when individual distances increase.

Thus, for the **identical exhaustive FastCC hypotheses and distances**:

```
every identity's subset score >= that identity's full score
minimum identity subset score >= minimum identity full score
```

If the full best score is above 0.32, no reordering/subset of those same
computations can satisfy the unchanged <=0.32 distance part of the early gate.
This conclusion does not require reasoning about its margin.

The saved complete v26 result has 13 exhaustive queries. The audit checks that
each diagnostic gallery minimum/runner-up equals the actual returned score and
runner-up before deriving the following counts:

| Exhaustive-query category | Count |
|---|---:|
| Full best score >0.32: unchanged-hypothesis subset cannot pass distance gate | 11 |
| Full best <=0.32: this distance-only certificate does not apply | 2 |
| Current wrong identities included in the 11 | 4/4 |

The worst query's complete best score is 0.3583984375. All four wrong-identity
queries also have complete best scores above 0.32. Merely moving their
unchanged partial scoring earlier cannot make it confident under this gate.

The remaining two exhaustive queries have best/second scores
0.315524/0.386278 and 0.314453/0.380859. Their complete margins fail 0.08, but
that alone does **not** certify that every partial margin fails: incomplete
runner-up scores could be larger. They are explicitly not covered by the
distance-only certificate. No unsupported all-query impossibility claim.

## Limits of the conclusion

The certificate is not a lower bound on runtime. It does not prove that a
different exact implementation cannot finish **all** work faster. It also does
not cover new descriptor representations, newly generated geometry, the
separate quality-weighted distance or CompNet embedding metric. A single-pass
global-image SIFT or learned feature representation would change descriptors
relative to ROI-specific warping, normalization and blur; it is not exact reuse
and would require new accuracy/unknown-rejection validation, rather than
inheriting this reference's correctness claim.

Nor is this an assessment of every slow query. There are 18 correctly
identified queries over 2.5 s: nine exhaustive and nine in other confident
routes. Those other routes remain possible optimization targets, but improving
them cannot be represented as solving the hardest query or four mistakes.

## Concrete blocker and stopping condition for this proposal

No new source of reliable evidence is supplied by this exact shared/lazy
architecture as assessed. Exact reuse was already tested; unchanged-hypothesis
early gating cannot handle 11 of the 13 current fallbacks. There is therefore
no evidence-supported reason to implement another version of this route or
repeat a full Pi benchmark claiming it solves the present hard cases.

A next candidate must introduce a genuinely different, reproducible ROI or
representation mechanism, keep the current regression cohort and failures, and
be validated on real Pi first/warm requests, full accuracy/timely/P95/max and
wrong identities/rejections. It must not loosen gates, relabel images, use
person/file exceptions, cache query answers or exclude hard samples. New
sessions and unregistered hands are still needed for independent robustness
and rejection claims. No architecture is declared universally impossible.

## Reproduction

```
python tools/assess_lazy_shared_architecture.py \
  runtime/pi5-under2-20261028/compnet-v26-pi-20261030/results.json \
  runtime/pi5-under2-20261028/lazy-shared-architecture-assessment-20261030
```

Use a fresh output directory. `assessment.json` retains all 13 cases, the exact
reference-results SHA256 and hashes of the audited scoring/gating source files.
No model inference, new image processing, new Pi latency result or raw biometric
upload occurs. Existing startup/ready timings and fresh enrollment latency must
remain distinct as documented in
[PI5_V26_STAGE_BLOCKERS_20261030.md](PI5_V26_STAGE_BLOCKERS_20261030.md).
