# Geometric valid-support mechanism audit — 2026-10-30

Primary goal is genuine correct identification, with threshold calibration only a secondary concern. Preserve the retained-evidence reference (165 correct, three wrong, zero rejection /168); frozen v26 is a separate 164-correct reference. No threshold sweep, pure speed trial, label change, sample deletion, identity exception or production deployment is part of this protocol.

Existing logs establish full-five-frame ordinary FastCC scores and the winning fixed poses for each of the three remaining mistakes. They do not record the winning dx/dy, receptive-field valid support or CompNet per-frame angular distances. Independent CompNet identity scores appear in old stage traces but lack explicit per-frame provenance. These gaps justify a bounded isolated **observational** replay, not another ROI/aggregation parameter scan.

## Fixed selection and isolation

Select all three retained-reference mistakes. Add the global slowest correct query, the previously wrong query corrected by evidence retention, and the lexicographic first correct exhaustive and first correct <=2500ms control in the mistakes' case. All seven samples are fixed mechanically from the saved results before new matching; every gallery identity and all five enrollment frames remain in each query's ranking. No true-label winner selection occurs in the matcher.

Run original-image HTTP requests with copied writable DBs and links to immutable frozen templates. The source-checked retained-evidence helper is enabled; rejection policy stays absent and final threshold=1.0/min_margin=0 remains unchanged. Require exact whole-gallery score/status/identity/route equality to the retained reference. Abort on nonzero/unreadable power flags. Trace creation is not latency acceptance evidence. Never export binary codes, masks, embedding vectors or image pixels.

## Geometric support, not gray-value masking

Propagate an all-one source plane through the actual perspective/rotation/scale chain using the same raster interpolation and zero border as the image sampler. For context-then-alignment, propagate through both warps rather than collapsing two interpolation stages. Use only a numerical float32 tolerance when identifying fully supported pixels. A real black pixel remains valid; grayscale zero is never a mask criterion.

Erode the final 128px crop support by the complete 17x17 FastCC filter footprint, with outside support zero, then sample every four pixels. Even a completely valid crop has only 28x28=784 fully supported code locations: the outer two code rows/columns depend on artificial filter padding. For all 81 dx/dy overlaps, report total bits, valid bits, invalid agreements/mismatches, ordinary mismatch fraction and valid-support-only mismatch fraction. Preserve all tied best shifts and every fixed pose. These scores are separate diagnostics, not mixed with CompNet or weighted-quality scores.

Observe actual scored geometric warps and source/caller provenance. Match/extraction wrappers retain the actual code/warp relationship in RAM, verify ordinary dx/dy minima exactly reproduce the real FastCC distance, and record valid support for both query and target. Missing or ambiguous provenance must stay visible rather than being replaced by an assumed mask.

CompNet diagnostics reuse the actual primary/alternate embedding vectors in memory during the unchanged scoring call. Record its full-gallery ranking, top1/top2, true-identity rank for analysis, all five frame distances, and separate distance/margin gate outcomes. Its float32 frame aggregation is preserved. No angular/FastCC distance minimum, voting by true labels or oracle branch substitution is allowed.

## One prospective general ablation

Only if the observational trace proves that the scoring paths' geometric masks have no unsupported interior beyond the known filter boundary, test one uniform modification: compute ordinary FastCC distance using only code responses with a fully supported 17x17 footprint. The new denominator is the actual valid overlap at each dx/dy. This changes the score definition; it is not an exact acceleration or a newly calibrated acceptance policy. Keep all poses, five-frame aggregation, candidates, confidence gates and labels fixed. Apply the same definition in every ordinary FastCC stage so the retained accumulator never mixes old and new distances. CompNet and weighted-quality metrics remain separate.

Test the same seven fixed queries first. Any newly wrong/rejected previously correct control kills the candidate; do not tailor it or change thresholds. If it does not genuinely correct at least one remaining wrong identity, stop it as ineffective. Only a passing accuracy ablation proceeds to full168 regression, with correct/wrong/rejected/time reported separately. A failed ablation is retained with the masks and evidence explaining why it failed. Manual anatomical ROI remains an oracle and is not counted as a deployed detector or formal recognition result.
