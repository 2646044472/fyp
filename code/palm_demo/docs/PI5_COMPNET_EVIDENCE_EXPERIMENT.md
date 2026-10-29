# Pi 5 frozen CompNet early evidence (2026-10-29)

The opt-in v25 candidate preserves all 164 correct decisions out of 168 device
queries while increasing correct decisions within 2.5 s from 139 to 145 against
a matched v24 control. The new-device medians fall from 1.85–1.87 s to 1.31–1.32 s.
Four existing mistakes and the longest queries remain unresolved. Production
has not been switched to this candidate.

## Mechanism and scope

`FastCCCompNetEvidence-v25-experimental` first runs the existing pose comparison.
Only when that is uncertain does it compute one frozen CompNet embedding of
the current native grayscale ROI. It compares that 512-dimensional vector
against original five-frame enrollment vectors, aggregates the best two
distances per palm, and requires distance <=0.32 and runner-up margin >=0.08.
Uncertainty continues the complete v24 pipeline. Scores from different metrics
are never mixed by taking their minima. Already confident pose queries skip
the model entirely. No file/person-specific rules, query cache or training on
device/public evaluation images were introduced.

These numerical gates are not an established equivalent false-accept rate
across the two metrics. Unknown-person rejection remains uncalibrated, and
the demo's final fallback is a closed-set ranking. This is experimental code,
not an accuracy or payment-security validation for unknown hands.

## Full Pi replay

Active data: 169 original images, seven physical people, 17 device-specific
palm identities. Each case enrolls its first or last five images and queries
the remaining originals, giving 168 main queries across four cases. The
user-directed deletion was applied before both runs and is not an algorithm
improvement. No cross-device enrollment/query pairs were evaluated.

| Case | v24 correct | v25 correct | v24 correct <=2.5 s | v25 correct <=2.5 s | v24 P50 s | v25 P50 s | v24 max s | v25 max s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| New original | 28/29 | 28/29 | 27/29 | 28/29 | 1.853 | 1.321 | 4.296 | 4.355 |
| New reverse | 29/29 | 29/29 | 22/29 | 24/29 | 1.869 | 1.315 | 14.879 | 15.210 |
| Old original | 52/55 | 52/55 | 45/55 | 45/55 | 1.517 | 1.541 | 10.259 | 10.363 |
| Old reverse | 55/55 | 55/55 | 45/55 | 48/55 | 1.539 | 1.520 | 9.527 | 9.478 |
| All | 164/168 | 164/168 | 139/168 | 145/168 | 1.559 | 1.535 | 14.879 | 15.210 |

Overall P95: 7.462 s control, 5.926 s candidate. This is not an all-queries
2.5-second result. The earlier continuous fresh-registration v24 run gave
137/168 timely-correct; use the matched 139/168 control when attributing gains.

Both matched runs copy the same completed v24 enrollment, initialize the HTTP
application, and recompute every original/ROI/query feature in the same order.
Only the candidate template envelope magic and algorithm metadata change;
remaining biometric payload bytes are verified unchanged. Candidate enrollment
embeddings are rebuilt during gallery preparation. Fresh v25 on-site enrollment
latency was not measured. Startup is separate from query latency. Query timing
includes file read, ROI, extraction, retrieval/alignment, scoring and local HTTP;
camera capture, hand positioning and external network upload are excluded.

All 33 auxiliary early returns were correct. All 168 ROI PNGs match the fresh
v24 baseline byte-for-byte. Every non-auxiliary decision has the same identity,
score, second score, status and recognition route as both v24 runs. Simulated
confirm, duplicate-confirm, cancel and cancelled-confirm checks pass. Original
images and source templates remain unchanged. All power flags were 0x0.

The four mistakes are retained:

- New original, billy:right, `20261029T120016111983Z-a4677ec5`.
- Old original, xyt:right, `20261013T111553178583Z-61f30739`.
- Old original, xyt:right, `20261013T111555214120Z-8d6441d2`.
- Old original, cyw:left, `20261013T111358589224Z-37d0c433`.

The slowest candidate is new reverse stephen:left,
`20261020T165604274940Z-f7ec5fe1`, 15.210 s. It still needs exhaustive search.
Seven people and at most 11 device-specific gallery palms cannot establish
40-person capacity, unseen-session accuracy or unknown-person rejection.
All current device queries have been exposed; there is no new held-out claim.

### Paired overhead diagnostic

Mechanically select the three slowest control queries plus the largest measured
auxiliary gain (already among those three). In the same initialized v25 app,
alternate disabled/enabled/enabled/disabled with the gallery and loaded model
held fixed; every request recomputes the original. All 12 requests completed,
power 0x0, simulated tokens cancelled without creating transactions.

| Sample | Disabled seconds | Enabled seconds | Auxiliary milliseconds |
|---|---|---|---|
| `20261020T165616782627Z-47472168` | 14.914,14.013 | 1.169,1.250 | 8.59,8.51 |
| `20261020T165604274940Z-f7ec5fe1` | 15.310,14.246 | 14.266,14.489 | 8.57,8.56 |
| `20261013T111553178583Z-61f30739` | 10.266,10.208 | 10.200,10.172 | 8.79,8.81 |

Identity/route/score decisions are unchanged between repeats for each mode.
The first two images remain correctly identified; the third remains incorrect.
The measured 8.5–8.8 ms auxiliary cost cannot explain the 14–15 s remaining
tail, but this three-query diagnostic does not establish no global overhead.
The full-run max regression is retained above.

The already computed nine-pose screen would add seven confident returns over
the v25 routes, six already within 2.5 seconds and only one outside. The
slowest image remains unconfident even with nine poses. This expansion was
not integrated: it adds inference to uncertain probes without solving the
main tail and requires its own Pi/unknown-rejection validation.

## Reproducibility and model provenance

Tools: `tools/export_compnet_pilot.py`, `tools/screen_compnet_pilot.py`,
`tools/screen_device_compnet_pilot.py`, `tools/replay_compnet_candidate.py`,
`tools/report_compnet_experiment.py`, `tools/benchmark_compnet_paired.py`.
Runtime evidence is retained locally under `runtime/pi5-under2-20261028/`:
`active169-baseline-20261029`, `compnet-v24-control-pi-20261029`,
`compnet-v25-pi-20261029`, and `compnet-paired-pi-20261029`.

The author Tongji600 checkpoint is frozen; its classifier is unused. Input is
128x128 grayscale /255, positive pixels standardized with sample std +1e-6,
zeros retained. Gabor kernel materialization preserves exact PyTorch output;
ONNX maximum absolute embedding error across three random inputs is about
1.1e-7. Author source/checkpoint/model are ignored local dependencies and are
not redistributed here (author repository license: CC-BY-NC-4.0).

| Artifact | SHA256 |
|---|---|
| Author compnet.py | `6db4d7859cbe1ffa2317b2ca036c125f0d7e2891df6dd52b212c4f0d6f1c2695` |
| Author checkpoint | `e27c86179dad2a69e9d9c7d4365eae5a31c3ccb4770a891a4ea3c1844d9f8a9a` |
| Exported ONNX | `b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea` |

The standalone encoder was less accurate than v24 and is deliberately not a
replacement matcher. Nine-pose inference was screened but not integrated.
An independent multiaxis quality pilot rescued only 1/30 development fallback
trials and was also not integrated. Existing suite: 213 passed, four optional
skips; obsolete `test_existing_pipeline.py` excluded. Integration tests cover
pose precedence, uncertainty fallback, query-local inference and preprocessing.

## Literature and limits

- [CompNet author implementation](https://github.com/xuliangcs/compnet): actual
  frozen checkpoint used in this experiment (LSP 2021, DOI
  `10.1109/LSP.2021.3103475`).
- [BEST, Pattern Recognition 2023](https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf):
  shared local feature computation motivates amortizing extraction across the
  gallery. Its official archive is encrypted; no reproduced BEST model claim.
- [Palm-ID, 2024](https://arxiv.org/abs/2401.08111): compact retrieval vectors;
  paper's server/mobile timings are not Pi timings.
- [ERAlign, 2025](https://www.nature.com/articles/s41467-025-58213-7): stable
  orientation/ROI and capture geometry, with infrared/ToF hardware assumptions.

The common design lesson is to extract useful evidence once per query and
reuse it across identities. All these methods retain ROI/quality failure modes;
the literature does not establish that our hardest captures are recoverable.
