# Pi compute experiments, 2026-10-29

Production remains v6. These are isolated experiments, not deployment approval.
The target is correct end-to-end recognition within two seconds, including slow
cases; median latency alone is insufficient. Reserved people remain untouched.

## Thread budget: rejected as a speed solution

Mechanism: two application workers each requesting four native threads may
oversubscribe four Pi cores. ONNX Runtime documents that spinning improves
wakeup latency but consumes CPU, and separate session pools can contend:
[official threading guide](https://onnxruntime.ai/docs/performance/tune-performance/threading.html).
The expectation was a modest scheduling gain, not elimination of model work.

All five previously recorded exhaustive queries were selected automatically.
Each configuration ran in a separate process, twice, sequentially on the Pi.
OpenMP used PASSIVE waiting; ONNX used four threads throughout. Every query
retained exactly the reference identity, scores, status and route (40/40 total).

| Native / OpenCV threads / ORT spin | New warm median | Old warm median |
| --- | ---: | ---: |
| 4 / 4 / enabled (baseline) | 10.932 s | 4.581 s |
| 2 / 2 / disabled | 11.209 s | 4.615 s |
| 1 / 2 / disabled | 12.953 s | 4.900 s |
| 2 / 4 / disabled | 11.005 s | 4.518 s |

The small old-camera change does not establish a repeatable gain. No alternative
was selected or integrated. This is a tail-only diagnostic, not a full accuracy
or latency audit. No transaction count changed. Thermal throttling was zero.

## Exact partial distance: rejected as slower

[Lakemond et al. (2013)](https://doi.org/10.1155/2013/405680) describe partial
distance termination for exact high-dimensional nearest-neighbour matching.
The pilot preserves descriptor order and floating-point accumulation order,
checks partial sums at 32/64/96 dimensions, and terminates only when the positive
partial sum strictly exceeds both forward and thread-local reverse second-best
distances. Ties are retained. This is a simple partial-distance pilot, not an
implementation of the paper's dimension sorting or d-D sort data structure.

Sixteen synthetic cases (including exact and near ties) and 80 real descriptor
pairs per thread count produced identical neighbour indices, distances and
transforms. Four alternating-order timing repetitions gave these medians:

| Native threads | Original | Partial distance |
| --- | ---: | ---: |
| 1 | 23.321 ms | 24.889 ms |
| 2 | 12.830 ms | 13.887 ms |
| 4 | 7.149 ms | 7.845 ms |

Branch/reduction overhead outweighs skipped arithmetic on these descriptors.
The build flag `PALM_PARTIAL_DISTANCE` is off by default; no experimental binary
replaces the existing one. No HTTP replay is claimed for the rejected kernel.

## Next architecture experiment: lower-resolution localization

Operator profiling on synthetic inputs shows convolution dominates PKLNet:
at four threads, Conv plus FusedConv account for about 331 ms per instrumented
run. Two 3x3 segmentation convolutions alone average about 155 ms together.
Profiling overhead and synthetic data mean these are diagnostic costs, not
end-to-end demo latency. Reducing the spatial resolution of the backbone and
segmentation head can reduce this work, unlike thread or cache tuning.

Predeclared pilot: resize the existing 400x300 prepared tensor to 200x150 for
the pretrained backbone/segmentation head, resize its segmentation output back
to 400x300, and retain the original keypoint head, output coordinates, weights,
recognition thresholds and test denominator. No retraining or identity-specific
rules. This changes predictions and is not an equivalent optimization; it must
pass a fresh geometry/recognition audit before consideration. Test the complete
80-image development set; stop or report regressions rather than fitting
exceptions. The existing 224 splits are correlated regression evidence only.

The already-tested MediaPipe control detected 22/40 new images (19/40 with
grayscale), so merely replacing PKLNet with that detector is not acceptable.
The low-resolution pilot is pending; no speed or accuracy result is claimed yet.

## Reproduction and private evidence

Tools: `benchmark_thread_budget.py`, `benchmark_native_variants.py`,
`profile_localizer_ops.py`. Run `--help` from the app's tools directory. The
native pilot is built with the existing ARM command plus
`-DPALM_PARTIAL_DISTANCE`, to a separate shared-library filename.
Evidence is under `runtime/pi5-under2-20261028/`: `thread-budget-*.json`,
`partial-native-*.json`, `localizer-ops-*.json`. Reports contain biometric sample
identifiers and are not committed. These experiments neither use reserved
archives nor modify production networking, service files or templates.
