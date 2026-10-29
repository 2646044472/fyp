# v26 hardest-query and error blockers (2026-10-30)

No algorithm, metric, threshold, label, active image, template or production
configuration changed in this round. The latest full Pi result remains
164/168 correct, 146/168 correct within 2.5 seconds, P95 6.019 s, max 15.225 s.
The pre-deletion 170-query cohort remains a separate historical result.

## What was measured

Select the union of the global max-latency v26 query and every incorrect
identity mechanically: five distinct case/query pairs. Replay each twice on
isolated copies of the completed v26 enrollment, with the same native library,
three-core affinity, one native thread and main-localizer startup priming.
No camera capture. All ten requests retain exactly the reference identity,
score, second score, status and recognition route. This includes all four
incorrect identities (eight instrumented requests), not just successful cases.
Simulated tokens are cancelled; transaction counts and source files remain
unchanged. All power flags are 0x0.

These are instrumented diagnostics, not a new full 168-query accuracy/latency
run. Overlapping/nested timers are not summed. The reporting tool takes the
union of intervals when computing stage or native-matching active durations.

## The 15-second tail is multiple expensive phases

Actual hard query: new reverse stephen:left,
`20261020T165604274940Z-f7ec5fe1`.

| Phase | First instrumented query, seconds | Second, seconds |
|---|---:|---:|
| Elapsed before entering full fallback (includes initial capture/ROI/features) | 2.648 | 2.667 |
| Additional window localization | 3.966 | 3.076 |
| Complete fallback feature construction | 3.468 | 3.422 |
| Complete identity matching | 5.106 | 5.116 |
| HTTP total | 15.216 | 14.309 |

Native correspondence/registration-active interval union is 5.575/5.609 s
across the whole request, already overlapping other rows; do not add it again.
Even removing only its work would leave several seconds of other phases in
this measured execution. This is not a theoretical lower bound on future
algorithms, but rules out claiming that a small distance-kernel change alone
solves the present 2.5-second gap.

The first additional localizer invocation is 1.364 s versus 0.506 s on the
second repetition. The ~0.86 s first-call difference suggests that prewarming
the lazy fallback model might help cold behavior, but no isolated causal
prewarm comparison was run. The warm second request is still 14.309 s. Moving
this small cost into ready wait would not solve the multi-second remaining
localization, SIFT/features and matching phases.

Prior accepted-crop evidence remains relevant: only two weak alignment crops
appear around 2.00/2.66 s; better aligned crops appear around 13.33 s, but their
frozen CompNet distance ~0.363 still fails the fixed 0.32 gate. Existing
original/gamma candidate reuse helps three other frames, not this frame.

## Initialization/ready wait is separate

| Existing-gallery case | Model/index initialization until ready, seconds |
|---|---:|
| New original | 17.834 |
| New reverse | 16.713 |
| Old original | 30.554 |

This loads the existing enrolled gallery, builds indexes and primes the main
localizer. The fallback-window model retains its normal lazy loading. These
are not fresh on-site enrollment measurements, do not include recapturing any
enrollment frame, and are not included in the query table above. They must not
be advertised as under-2.5-second readiness or registration.

## The four wrong identities are weak closed-set matches

The complete v26 run has 168 MATCH responses, four of them the wrong identity,
and zero explicit REJECT responses. Every query belongs to an enrolled person.
Thus the observed wrong-identity rate is 4/168; unknown-person FAR and
verification FRR are not measured. Do not call zero explicit rejection 0% FRR
or label the four closed-set mistakes an unknown-person FAR estimate.

| Sample | Winning score | Runner-up | Gap |
|---|---:|---:|---:|
| billy:right `20261029T120016111983Z-a4677ec5` | .383600 | .387695 | .004095 |
| xyt:right `20261013T111553178583Z-61f30739` | .374023 | .389347 | .015323 |
| xyt:right `20261013T111555214120Z-8d6441d2` | .374721 | .375000 | .000279 |
| cyw-real:left `20261013T111358589224Z-37d0c433` | .345703 | .360871 | .015168 |

All fail the earlier <=.32 / >=.08 confidence gate. `demo_flow.py` constructs
the final Gallery with threshold 1.0; the Gallery's default min_margin is 0.0.
This final policy ranks an enrolled identity even when the earlier evidence is
insufficient. It is unchanged. At the last recorded gate before 2.5 seconds,
the billy query happens to lead with the true identity; the hard stephen query
and three old-camera errors lead with a wrong identity. None has a confident
gate before the deadline. Simply returning the current leader is therefore
not an established accuracy-preserving deadline strategy.

Earlier source/ROI sheets show the two xyt crops include wrist/heel/background
rather than the enrolled central palm; billy has weaker fine detail and a
viewpoint change; cyw's fine texture is weak. These are observations, not proof
that all such captures are irrecoverable. No additional samples were deleted.

## Concrete blocker and a defensible next step

The current tested ROI/representation stages do not produce reliable evidence
soon enough for the hardest query and do not resolve the four mistakes. The
complete fallback is inherently multi-stage and measured in many seconds on
this Pi. Failed fixed-neighborhood, SIMD, contrast/alignment, pose and model
precision pilots do not justify more parameter search on these exposed frames.

A substantive next experiment needs a different, reproducible ROI or
representation mechanism with a credible way to avoid full fallback. It must
retain all current cases, avoid person/file rules, threshold relaxation and
query-answer caching, preserve or improve whole-cohort correctness, demonstrate
the hard query correctly within 2.5 s on Pi, and report full timely rate,
P95/max and all mistakes together. New sessions and unregistered hands are
needed for independent robustness/rejection claims; repeated splits of these
exposed images are insufficient. This is the remaining validation boundary,
not a claim that no future algorithm can work.

Tools: `profile_staged_queries.py --retain-reference-errors --warm-model` and
`report_v26_stage_blockers.py`. Private evidence under
`runtime/pi5-under2-20261028/v26-stage-diagnosis-20261030/` includes the exact
selection/source hash, all ten profiles, interval summaries and HTML report.
The ready-style JSON files are protocol adapters containing the original
selected v26 observations; they do not invent new baseline measurements.

The follow-up assessment of exact shared/lazy feature computation, including
its scoped early-gate obstruction, is in
[PI5_LAZY_SHARED_ARCHITECTURE_ASSESSMENT.md](PI5_LAZY_SHARED_ARCHITECTURE_ASSESSMENT.md).
