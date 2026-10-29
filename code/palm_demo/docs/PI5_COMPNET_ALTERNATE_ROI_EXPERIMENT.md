# Pi 5 existing-base-ROI evidence (2026-10-30)

The opt-in v26 candidate preserves the v25 result of 164/168 correct and gives
146/168 correct within 2.5 seconds, versus 145/168 for v25. Three queries return
earlier through the new branch, all correct; two move inside 2.5 seconds while
one previously timely query moves outside. Overall P50/P95 and max do not
improve. This is a small path-specific gain, not a solution to the hardest tail
or an unconditional recommendation to replace v25. Production is unchanged.

## Mechanism

Initial PKLNet localization already evaluates original and gamma-adjusted views.
When their geometry disagrees, the original primary ROI may be retained while
the other valid candidate remains available. v25 only encodes the primary ROI.

`FastCCCompNetAlternateROI-v26-experimental` preserves existing pose and primary
CompNet confidence first. Only if both are uncertain, it encodes the other
existing base candidate from the native grayscale original. It retains the
existing overlap guard and image bounds, skips identical source transforms,
scores the whole original enrollment gallery with the same frozen model, and
requires the same numerical <=0.32 distance and >=0.08 margin. Conflicting
confident candidates continue the unchanged v24 fallback. Distances from
different ROIs/metrics are not mixed by minima. No additional localizer call,
fixed spatial pyramid, new pose bank, target-data training or person/file rule.

Enrollment still uses each frame's original primary embedding only. The app
attaches existing localization diagnostics only for the explicitly selected
v26 matcher. Default service selection is unchanged. The response's displayed
ROI remains the original primary ROI; actual auxiliary matching geometry is
recorded separately as `auxiliary_roi_quad`, with report comparison images.

## Full Pi HTTP replay

Same 169 immutable active originals, seven physical people, 17 device-specific
palms, four earliest/latest-five enrollment cases and 168 query trials. All
failures remain. The user-directed historical deletion predates these runs;
the old 170-query baseline is separate, not an algorithm-gain denominator.

| Run | Correct | Correct <=2.5 s | P50 s | P95 s | Max s |
|---|---:|---:|---:|---:|---:|
| v24 matched enrollment-copy control | 164/168 | 139/168 | 1.559 | 7.462 | 14.879 |
| v25 frozen primary evidence | 164/168 | 145/168 | 1.535 | 5.926 | 15.210 |
| v26 existing alternate base ROI | 164/168 | 146/168 | 1.540 | 6.019 | 15.225 |

| Case | Correct v25/v26 | Timely v25 | Timely v26 | v26 P50 s | v26 P95 s | v26 max s |
|---|---:|---:|---:|---:|---:|---:|
| New original | 28/29 | 28/29 | 27/29 | 1.316 | 2.506 | 4.344 |
| New reverse | 29/29 | 24/29 | 25/29 | 1.316 | 3.991 | 15.225 |
| Old original | 52/55 | 45/55 | 46/55 | 1.539 | 9.128 | 10.257 |
| Old reverse | 55/55 | 48/55 | 48/55 | 1.542 | 4.317 | 9.638 |

The three new route returns:

| Case / sample | v25 seconds | v26 seconds |
|---|---:|---:|
| New reverse / `20261020T165710063889Z-9dea7e47` | 3.716 | 2.284 |
| Old original / `20261013T111806724809Z-7baf26f9` | 2.503 | 1.631 |
| Old reverse / `20261013T111339367360Z-dfb1a66b` | 2.495 | 1.555 |

New original `20261020T165646467846Z-2239e833` moves from 2.469 to 2.558 s,
despite retaining the same decision/route. Report net +1 timely query rather
than attributing all three path gains to total timely-rate improvement. One
full run does not establish that this net count is repeatable.

### Paired mechanism check

Select all three actual new-route returns mechanically. In the same initialized
v26 app/gallery, disable only the alternate stage (v25 raw evidence remains),
then run disabled/enabled/enabled/disabled. All 12 requests are correct;
disabled decisions match the completed v25 scores/routes exactly, and each
mode's two repeats have identical decision fields. Simulated tokens are
cancelled without transactions. All power flags remain 0x0.

| Case | v25 disabled, two seconds | v26 enabled, two seconds |
|---|---|---|
| New reverse | 3.720,3.702 | 2.215,2.293 |
| Old original | 2.581,2.520 | 1.580,1.541 |
| Old reverse | 2.566,2.501 | 1.542,1.535 |

The auxiliary stage rises from 8.55–8.89 to 17.31–17.92 ms, about 9 ms extra,
while these queries avoid their later registration stages. This reproduces
the three mechanism-specific gains; it does not repeat the full 168-query
timely rate, P95 or max. Retain all full-run numbers above.

All 165 queries outside the new route retain exactly the v25 identity, score,
runner-up score, status and recognition route. All 168 displayed primary ROIs
remain byte-identical to the v24 baseline. All simulated confirmation,
duplicate blocking, cancellation and cancelled-confirmation checks pass.
Original source images/templates are unchanged; every power sample is 0x0.
Native library and model hashes are retained in runtime evidence.

Like the matched v24/v25 runs, this copies a completed v24 enrollment and
changes only template envelope magic/algorithm metadata; feature payload bytes
are verified unchanged. Prepared embeddings are rebuilt during initialization.
Every query re-reads the original and recomputes its ROI/features. Timings cover
file read through local HTTP identification, exclude camera capture/positioning
and external upload. Startup and fresh on-site v26 registration latency are
not part of these query numbers or claimed under 2.5 seconds.

## Prior screens and hardest-query diagnosis

The actual v25 slowest query remains new reverse stephen:left
`20261020T165604274940Z-f7ec5fe1`. A Pi diagnostic records every raw 128px crop
already emitted by accepted alignment stages while preserving all original
decision fields exactly. Four crops are emitted: two around 2.00/2.66 s in the
fast stages, two around 13.33 s during full fallback. The early two provide no
confident whole-gallery CompNet evidence. The latter two prefer the true palm
with angular distance ~0.363 and runner-up ~0.445, but still fail the unchanged
0.32 gate. Do not relax the gate for this file. This diagnostic does not change
decisions; its instrumented timestamps are not acceptance latency.

Further frozen offline controls, no Pi timing claims:

| Control | Current 168: extra confident / wrong | Historical 4480: extra confident / wrong |
|---|---:|---:|
| Original ROI, percentile normalization + existing CLAHE(2,8x8), both sides | 1 / 0 | 46 / 0 |
| All stored base/window ROI hypotheses | 6 / 0 | 244 / 0 |
| Only already-computed original/gamma base hypotheses | 3 / 0 | 92 / 0 |

CLAHE only adds an already timely 1.80-second query, so it is not integrated.
All-window hypotheses require more localization, offer no rescue for the
hardest query or the four errors, and are not integrated. The base-only
mechanism is the one subjected to the complete Pi v26 replay above. These
controls do not rehabilitate the rejected fixed spatial pyramid, which adds
three wrong confident decisions on this cohort.

## Verification and limitations

224 local tests passed, four optional dependency skips, excluding obsolete
`test_existing_pipeline.py`. New tests cover primary precedence, alternate
whole-gallery evidence, identical/disjoint candidate skips, conflicting
candidates, required diagnostics and single-identity uncertainty. Tool smoke
checks and actual Pi template-read/hash checks also completed.

The four v25 mistakes remain unchanged: billy:right
`20261029T120016111983Z-a4677ec5`, xyt:right
`20261013T111553178583Z-61f30739` and `20261013T111555214120Z-8d6441d2`,
cyw-real:left `20261013T111358589224Z-37d0c433`.
Unknown-person rejection remains uncalibrated; nominal equal gates do not
establish equal false-accept rates for different metrics/searches. All device
queries have been exposed. Forty-person capacity, unseen sessions and live
capture are not validated. Model weights and author source are not redistributed.

Tools: `inspect_aligned_compnet.py`, `screen_compnet_contrast.py`,
`screen_compnet_context.py --stored-candidates [--base-only]`,
`export_evaluation_template_geometry.py --all-enrolled --candidates`,
`replay_compnet_candidate.py --matcher FastCCCompNetAlternateROI-v26-experimental`,
`benchmark_compnet_paired.py --disable-alternate-only`,
`report_compnet_alternate.py`. Runtime evidence lives under
`runtime/pi5-under2-20261028/`, in `aligned-compnet-slowest-20261030`,
`compnet-contrast-screen-20261030`, `compnet-stored-window-screen-20261030`,
`compnet-base-candidate-screen-20261030`, `compnet-v26-pi-20261030` and
`compnet-v26-paired-20261030`. The v26 run retains its source archive.

The subsequent unchanged-result stage diagnosis and explicit remaining blockers
are in [PI5_V26_STAGE_BLOCKERS_20261030.md](PI5_V26_STAGE_BLOCKERS_20261030.md).
