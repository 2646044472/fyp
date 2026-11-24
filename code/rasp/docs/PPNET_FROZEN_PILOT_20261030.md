# Frozen PPNet pilot and prior-route inventory (2026-10-30)

## Inventory before executing a new model

| Route already examined | Evidence/decision |
|---|---|
| Thread budget / matching parallelism | No reliable end-to-end tail solution; `PI5_COMPUTE_EXPERIMENTS.md` and parallel profile tools. Do not rerun as a new idea. |
| Original/partial-distance/block4 SIMD | Partial and block4 variants preserve outputs but are slower; block4 23.314→24.190 ms per pair. |
| Fixed ROI neighborhood / pose expansion | Context pyramid adds three wrong confident decisions; nine poses do not rescue the hardest query. |
| Exact reuse / lazy or staged fallback | Prior cache only saves ~12–16.5% on its historical protocol; 11/13 current complete fallbacks cannot pass the unchanged .32 distance gate using a subset of the same scores. |
| Existing alternate original/gamma ROI | v26 tested on Pi:164/168 correct,146/168 timely; three reproducible path gains, four errors and15.225s max remain. |
| Early geometry, contrast/SIFT/XFeat, weaker descriptors | Existing fixed pilots do not rescue current hardest/error cohort reliably; see alignment and backend experiment docs. |
| Reduced localizer / landmark replacement | Low-res ROI shifts; verified MediaPipe control only7/40 new-device successes. |
| FP16 / INT8 / OpenCV Winograd | FP16/Winograd slower or numerically changed ROIs; actual Pi INT8 introduced a wrong identity. CPU-FP16 advertised target unavailable; no false FP16 claim. |

Full stage evidence: hard query enters fallback around2.65s, adds3.08–3.97s
localization,3.42–3.47s features and~5.11s matching. Simply changing scheduling
cannot supply stronger identity evidence. Raw/ROI comparisons show inconsistent
palm coverage and weak texture. Better representation may help texture, but
cannot be assumed to recover noncorresponding wrist/background crops.

## New hypothesis, frozen before inference

The author-released **PPNet Tongji600** representation has not been evaluated
in this project. Unlike CompNet's learned competitive Gabor coding, it uses a
convolution/normalization/nonlinearity stack and two512-unit feature layers.
One query embedding can be shared across the gallery, potentially avoiding
the repeated localization, SIFT and pairwise registration path. It retains
the existing primary ROI; no new ROI-window/pose search is added. This is a
new frozen representation experiment, not a claim that swapping a network
already solves the task.

Use exactly one author checkpoint, selected by the same Tongji600 pretraining
source as the prior CompNet control, not by device-query performance:

- [Author code](https://github.com/xuliangcs/ppnet/blob/main/PPNet/models/ppnet.py).
- [Author preprocessing](https://github.com/xuliangcs/ppnet/blob/main/PPNet/models/dataset.py).
- [Released models](https://drive.google.com/drive/folders/1xcBzSxIDDWeIKK4mb6XHIdgwGsvQURHc).
- `ppnet_params_tongji_600.pth`, public file ID
  `1cjG7ZshKBbkzWzoCLyliqbjQZsIWNt97`.

No classifier fitting, enrollment/query training, public evaluation training,
parameter search, per-person/file rule or label change. Author code/weights
remain ignored local dependencies (CC-BY-NC4.0), not Git redistributions.

## Minimum isolated experiment and kill criteria

Declared before loading device images through PPNet:

1. Review source and safely load only the state dict with `weights_only=True`;
   require exact architecture/state compatibility. No randomly initialized
   feature layers or unsafe unpickling fallback.
2. Preserve author inference preprocessing: grayscale128, /255, positive-pixel
   zero mean/sample std+1e-6, zeros retained. Author feature output is unnormalized
   and its example uses Euclidean distance. Record that raw Euclidean ranking.
   A separately declared L2-normalized angular representation is an experimental
   control, not a reproduction of the author's distance or calibrated FAR.
3. Export full FP32 embedding only, no classifier. On three fixed synthetic
   tensors, require raw PyTorch/ORT allclose(atol=1e-4,rtol=1e-4) and normalized
   embedding max absolute error<=1e-5. Stop on incompatibility or bad numerics.
4. Screen all169 active originals using stored Pi primary ROI geometry, all168
   current query cases plus4480 historical split queries. No new localization,
   data filtering or camera acquisition. Existing .32/.08 numerical confidence
   gates stay fixed for the declared angular control. They do not establish the
   same error-acceptance rate as prior metrics.
5. Stop before full Pi replay if any wrong confident control result appears,
   or if it adds no correct confident evidence on a current exhaustive-fallback
   query. Improvement only on already-fast images is insufficient. Record all
   errors/ranks; do not tune another checkpoint or preprocessing to rescue them.
6. Only after this screen passes, benchmark isolated actual Pi encoder first/
   warm states. Kill if warm encoder P95>250ms or added prepared/model RSS>512MiB.
   Synthetic encoder timing is not full HTTP latency.
7. Only a surviving candidate may be added as an explicit opt-in branch after
   existing reliable v26 branches, with original fallback preserved. It must run
   full real-Pi168-query accuracy, correct<=2.5s, P95/max and all four errors,
   first/warm states and simulated payment/cancel regression. No production
   switch. Initialization/ready wait, query time and fresh registration latency
   remain separate.

No unknown-person data exists in the current protocol, so FAR/verification FRR
remain unmeasured even if a screen has zero wrong confident decisions. The
current 164/168,146/168,6.019s P95,15.225s max reference and historical deleted
image cohorts remain unchanged. Offline feature reuse is not runtime caching.

## Status

**Rejected at the predeclared offline screen.** The author checkpoint loaded
safely and strictly; ONNX export parity passed all three synthetic inputs.
The normalized-vector maximum absolute error was2.81e-7; raw-feature maximum
absolute error was8.35e-7. No feature layer was left randomly initialized.

| Cohort | Query trials | Raw Euclidean ranking correct | Angular ranking correct | Confident | Wrong confident | Current exhaustive rescues |
|---|---:|---:|---:|---:|---:|---:|
| Active169, four cases | 168 | 147 | 147 | 67 | 0 | 0/13 |
| Historical224 splits | 4480 | 4141 | 4209 | 2264 | 0 | Not applicable |

These are standalone feature ranking/confidence results, not the complete v26
pipeline. Do not compare147/168 to164/168 as though a candidate had been
integrated and lost17 decisions; no integration occurred. Nor is zero wrong
confident on registered inputs a measurement of unknown-person FAR.

The hardest query and billy:right error both rank the true palm first with
PPNet, but their angular gaps are only0.007426 and0.031171, below the unchanged
0.08 requirement. The hard query's best/runner-up are0.285967/0.293393.
Ranking first is not reliable early acceptance. No current exhaustive query
passes the fixed gate, so the declared kill criterion triggers. Do not change
the gate or select another checkpoint/preprocessor after inspecting this result.

Accordingly, **no PPNet Pi encoder/full-HTTP/first-warm benchmark, registration
measurement or production switch was performed**. The existing v26 complete
result remains164/168 correct,146/168 timely, P95 6.019s,max15.225s. No new Pi
performance claim, training or background experiment is implied. This tests
one frozen PPNet encoder, not the author's complete dual-camera alignment system.

### Remaining capability/data gap

This released representation still does not separate the current difficult
ROIs strongly enough under the fixed confidence test. Author raw Euclidean
distance has no supplied transferable device/open-set calibration in the
reviewed inference example. Choosing new thresholds on these exposed queries
would violate this protocol and would not establish false-accept control.
Independently captured sessions and unregistered hands would be needed to
calibrate/validate a genuinely different decision rule; merely reranking the
present frames is not sufficient. Better localization/representation still
needs to be demonstrated, rather than assumed from a paper or correct top1.

### Provenance and reproduction

| File | SHA256 |
|---|---|
| Reviewed author ppnet.py | `f7fe9a894cf845350718d44dd63b90181942f498fbc8431ec2fbe7f32b0f9a30` |
| Author Tongji600 checkpoint (91,736,778 bytes) | `c542c9daf893ac7cacee01402b39a12367bb137313f9d7c8825287263f0d21bb` |
| Exported FP32 ONNX | `e3405d03412af5e9689cd8e7e5f0ddd6d46e9bed786e171984a38d0f85a18af7` |

Tools: `tools/export_ppnet_pilot.py`, `ppnet_pilot.py` (not registered),
`tools/screen_ppnet_frozen.py`. Protocol, the verified original-manifest hash, both complete
distance matrices, all4480/168 query records, model/export hashes and HTML
report remain under ignored `runtime/pi5-under2-20261028/ppnet-pilot-20261030/`.
Model source/weights and biometric images are not uploaded or redistributed
by this commit. Export parity, complete offline screen and tool compilation
were checked; no application behavior was changed.
