# Shared localizer session pilot — preregistered 2026-10-30

Isolated resource-lifetime experiment; no production modification. Frozen v26 scores/thresholds, original active169 manifest and 168-query protocol remain unchanged. Historical 170-query data and frozen public evaluation data are not used.

## Difference from rejected routes

Read `PI5_LAZY_SHARED_ARCHITECTURE_ASSESSMENT.md`, `PI5_SPEED_FOLLOWUP.md` bounded fallback reuse audit, `PI5_COMPUTE_EXPERIMENTS.md`, `PI5_QUALITY_EVIDENCE_EXPERIMENT.md` parallel-window rejection and enrollment-link sections, and `PI5_V26_STAGE_BLOCKERS_20261030.md`.

The old exact-input memoization stores SIFT/registration results; it preserved outputs but remained slow and is not rerun. Lazy subset early return cannot meet the existing distance gate for 11/13 fallbacks. Enrollment/index/link caching already exists and is not counted as a new gain. The independent one-thread parallel-window sessions changed coordinates and were slower; this experiment does not parallelize, change threads, prune the ONNX graph or alter the inference input/order.

New mechanism: main illumination localizer and window heatmap localizer use the same diagnostic ONNX graph, three-thread configuration and geometry code. The baseline lazily loads a second graph/session for its first window inference. The experimental heatmap policy borrows the main localizer's already validated session, geometry module and inference lock, keeping a separate policy object. Each original image/window still executes the same inference and all postprocessing. No prediction, tensor, ROI, descriptor or answer cache is introduced. Unsupported/legacy/Torch parents abort rather than silently choosing a different graph.

## Locked minimal design and stop rules

Select the maximum-latency frozen query, the lexicographically first other exhaustive query in that same case, and the lexicographically first correct <=2500ms control in that case. Use the unchanged full gallery for that case. Sample IDs only select diagnostics; they never enter the sharing mechanism.

Four fresh processes in baseline/shared/shared/baseline order, same CPU affinity and original thread settings. Each process initializes and primes the usual main model/gallery, recording initialization/ready separately. It runs the three fixed queries twice in the same order, so the first hard query contains baseline lazy-window startup and the second is warm. One isolated copied runtime is reused across these sequential processes; payments are canceled, not confirmed. No mutable DB is hardlinked to the source.

Require exact returned status/identity/best/second/route against frozen v26; exact displayed ROI bytes; exact per-call localizer ROI/quad/diagnostic signatures and call counts against baseline. Any mismatch or unreadable/nonzero power flag stops the suite. Source model/template hashes must stay unchanged.

For a sustained-performance candidate, hard-query warm medians must improve by at least max(100ms, 5% of baseline), and the smallest baseline warm time must exceed the largest candidate warm time by at least 100ms. Cold hard times must not regress. Overlapping noisy warm results, changed outputs or any new error reject adoption and stop before ablation/full168. Cold-only initialization savings are reported as such, never as meeting 2.5 seconds or as a steady-state solution. Only a passing pilot justifies another ablation and full168 replay.

Full168 reference remains 164 correct accepts, four wrong accepts, zero rejects, 146 correct <=2.5s, P50 1540.17ms, P95 6019.3185ms, max 15225ms. The selected repeated-query suite reports its own denominator and first/warm timings; it cannot replace the full reference or establish unknown-person rejection.

## Completed actual Pi result: rejected for sustained speed

Four fresh processes completed in the preregistered ABBA order, using the full six-identity/30-frame new-reverse gallery and one isolated runtime. The fixed samples were `f7ec5fe1` (global slowest), `89bd294d` (first other exhaustive query) and `e022bbe6` (first fast correct control), with full IDs in the scalar artifact. Each process ran all three queries twice.

All 24 HTTP responses exactly preserve frozen v26 status, identity, best/second distances and route. All displayed ROI PNG bytes match the frozen reference. Across 96 actual localizer calls, corresponding per-call ROI, quad and diagnostic signatures are identical across processes; no inference was skipped. The baseline actually holds two distinct loaded sessions after the hard query, whereas the candidate's window policy actually references the parent session. Three focused unit tests passed for separate policy state/shared resources and rejection of legacy, unloaded and Torch backends.

Hard-query HTTP times in milliseconds:

| Process order | Mode | First hard request | Repeated hard request |
|---|---|---:|---:|
| A1 | baseline | 15252.86 | 14344.65 |
| B1 | shared | 14207.29 | 14253.56 |
| B2 | shared | 14249.58 | 14272.68 |
| A2 | baseline | 15225.18 | 14294.43 |

First-request median improves 15239.02 -> 14228.435 ms (1010.585 ms), consistent with eliminating the second session's lazy loading/first-run overhead. Main initialization/ready remains separate: baseline 16738.864 and 16723.305 ms; shared 16769.864 and 16766.160 ms. No startup work was moved into enrollment or hidden outside these records.

Repeated-request median improves only 14319.54 -> 14263.12 ms: **56.42 ms (0.394%)**, below the required 715.977 ms. The gap between the fastest baseline warm request and slowest shared warm request is only 21.75 ms, also below the 100 ms separation guard. Two measurements per mode do not establish a population significance claim. The preregistered sustained-performance gate is false; no ablation, full168 replay, default change or production deployment follows.

Selected-suite metrics (12 requests per mode, three unique already-exposed images; never substitute this denominator for full168):

| Mode | Correct accepts | Wrong accepts / rejected | Correct <=2.5s | P50 | P95 | Max |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 12/12 | 0 / 0 | 4/12 | 3.929960 s | 15.237636 s | 15.252860 s |
| Shared | 12/12 | 0 / 0 | 4/12 | 3.927185 s | 14.262164 s | 14.272680 s |

The selected-suite P95/max reduction is driven by removing first-window setup; it is not proof of a sustained speedup or a new full168 P95. Hard warm queries still take about 14.3 seconds. The four known full-cohort mistakes remain in the unchanged reference; none is deleted or claimed fixed by this selected pilot. No unknown-person/FAR inference is made.

All Pi power samples stayed 0x0, transaction counts and source template hashes are unchanged. Readback confirms frozen PKLNet SHA `bf477f1778f03ccc203b64dd0c84d418c9bb22839a23ba923f479ab991aa067f` and CompNet SHA `b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea`. Raw images, tensor/descriptor values, templates and models were not uploaded. The JSON contains scalar outcomes and geometry signatures only, with evaluator/mechanism source hashes.

Evidence: `protocols/SHARED_LOCALIZER_SESSION_PILOT_20261030.json`; private run logs and complete summary stay under `runtime/pi5-under2-20261028/` and on the isolated Pi experiment root. The full168 reference remains 164 correct accepts, 4 wrong accepts, 0 rejects, 146 correct <=2.5s, P50 1.54017 s, P95 6.0193185 s and maximum 15.225 s. Historical 170-query data remains separate. This experiment rules out this resource-sharing change as a sufficient steady-state solution; it does not rule out every exact implementation optimization.
