# Generic alignment proposal pilots, 2026-10-29

No application matcher, routing threshold, model default or production service
was changed. These are rejected offline proposal screens, not latency gains.
The full Pi baseline remains 165/170 correct and 139/170 correct within 2.5s,
P50 1.564s, max 14.342s. The five errors remain unresolved.

## Scope and fixed controls

Use all 30 v24 exhaustive-fallback trials from the original 224 development
splits / 4,480 queries. These 30 trials repeat only three distinct images from
the 80-image development cohort. Previously confident routes are unchanged;
the candidate is hypothetically inserted immediately before exhaustive search.

Then check all 16 exhaustive-fallback queries of the expanded 170-query,
seven-person device baseline using the fixed method. These people/images are
already exposed and must not be described as independent unseen validation.
Labels are only used to report correctness and define supplied enrollment
groups; transform estimation has no query identity or filename conditions.

All candidates use original-pixel FastCC scoring, best-two enrollment-frame
aggregation, the existing similarity/affine, sampling and anchor-overlap guards,
and the .32 best-score / .08 runner-up margin gate. Failure to meet the gate
retains the v24 fallback result. A correct top rank with weak evidence is not
counted as successful recognition. No thresholds are relaxed.

## Results and decision

| Proposal | Correct confident / dev fallback | Wrong confident / dev | Correct confident / expanded fallback | Wrong confident / expanded |
|---|---:|---:|---:|---:|
| Fixed CLAHE + RootSIFT | 10/30 | 0 | 0/16 | 0 |
| XFeat + original SIFT ratio test | 0/30 | 0 | Not run | Not run |
| XFeat + upstream default MNN | 1/30 | 0 | 0/16 | 0 |
| XFeat + default MNN + enrollment links | 1/30 | 0 | 0/16 | 0 |

All three expanded screens retain 165/170 correct because none trigger an
early return. Zero new wrong confident answers is not a calibrated false-accept
rate. The screens provide no target-device latency result, and the original
14.342-second difficult query is not rescued. No candidate is integrated.

CLAHE uses clipLimit=2 and tileGridSize=(8,8), followed by raw/sigma2 RootSIFT.
It increases local contrast without choosing parameters per image. The query
view is a 768-square context centered on the original 384-square palm frame;
enrollment uses the 384-square frame. Original grayscale is always used for
the final warped 128-square score.

XFeat uses public pretrained weights from
[verlab/accelerated_features](https://github.com/verlab/accelerated_features)
(Apache-2.0), without fine-tuning. Detection threshold .05, top1000 and 5x5 NMS
are fixed. The initial ratio-test control retained too few useful matches.
The separate MNN control uses the upstream match method's default cosine>.82,
rather than selecting a palm-specific descriptor threshold. Similarity and
bounded affine geometry remain unchanged. This is sparse XFeat, not the full
XFeat-star / fine-matcher / LightGlue pipeline.

Enrollment-link transfer composes a valid query-to-enrollment transform with
the existing within-identity SIFT similarity links, checks composed geometry
and sampling bounds, and re-scores original query pixels against each target
frame. It adds 27 valid scoring calls on the development trials and 60 on the
expanded trials, without additional confident returns. More proposals alone
are insufficient. A few erroneous queries rank correctly only because one
frame aligns; best-two evidence still fails. Do not count these as fixes.

## Conversion and data integrity

Reviewed upstream sources and weights are held in the ignored runtime folder,
with per-file hashes and upstream license. Only our exporter, adapter and
screen/report tools are committed. Neither third-party weights nor public
datasets are uploaded.

The exporter loads weights with weights_only=True and creates fixed 384/768
ONNX feature/logit/reliability maps. Random-input PyTorch/ORT map outputs agree
within atol/rtol 1e-4 (max absolute error about 5e-5). Sparse decoded keypoint
coordinates match upstream exactly on those inputs; normalized descriptors
pass 1e-4 parity. The NumPy decoder uses exact bilinear/bicubic formulas rather
than OpenCV's quantized remap table. These checks establish conversion/decoder
parity on the tested inputs, not palm accuracy or Pi speed.

Torch export ran in an isolated Python startup with a pip NumPy wheel to avoid
the host Anaconda/torch duplicate OpenMP runtime conflict; no unsafe duplicate
OpenMP override was enabled. Recognition screens use ONNX Runtime and contain
no PyTorch inference dependency. Host timing is explicitly offline only.

Expanded screens SHA-check original JPEG bytes from the tracked device ZIPs,
use actual Pi query transforms from baseline diagnostics and actual Pi stored
enrollment transforms/reference codes. Pi exports all 170 enrollment records
and within-enrollment links using the pinned native library. Original template
hashes remain unchanged. Power flags are checked before/after each identity
and are all 0x0. No production templates or payments are changed.

## Tools and private evidence

- `tools/screen_local_contrast_alignment.py`: optional --xfeat-root and
  --enrollment-links; all development fallback trials retained.
- `tools/screen_device_contrast_alignment.py`: same fixed proposal on expanded
  baseline, optional --enrollment-links points to the actual Pi link export.
- `tools/export_evaluation_template_geometry.py`: --all-enrolled and optional
  --native-registration export stored codes/matrices and within-identity links.
- `tools/export_xfeat_pilot.py`: reviewed upstream tree to fixed ONNX artifacts
  and conversion/decoder parity evidence; no model download implicit in import.
- `xfeat_alignment_pilot.py`: isolated ORT sparse proposal adapter, absent from
  the biometric registry and application flow.
- `tools/report_alignment_pilots.py`: combined report without latency claims.

Under ignored `runtime/pi5-under2-20261028/`:
`local-contrast-screen-20261029/`, `device-contrast-screen-20261029/`,
`xfeat-pilot-20261029/{development-screen,development-mnn-screen,development-linked-screen,device-mnn-screen,device-linked-screen}/`,
and `alignment-pilot-report-20261029.html`. Each screen retains protocol,
source/model hashes, complete per-query scores and rejection/scoring counts.
Feature/pair reuse is strictly offline; it must not be reported as live query
latency or turned into a saved-image answer cache.

This rejects these fixed combinations. It does not establish that all learned
local features, all contrast methods or all possible ROI strategies fail.

## Fixed 180-degree localizer control

As a separate generic ROI check, rotate every localizer input by 180 degrees,
retain the frozen illumination PKLNet policy and map its quadrilateral back
into the original image. Construct FastCC pose banks from original pixels.
No per-image/identity orientation choice or landmark retraining. Both a rotated
query against original enrollment and uniformly rotated-query/enrollment
control are declared before running all 80 development images / 224 splits.

Geometry is valid for 79/80 images. The query-only control yields 2,172/4,480
correct confident decisions and zero wrong confident decisions; rotating both
sides yields 2,247/4,480 and zero wrong confident decisions. Neither rescues any
of the 30 v24 exhaustive fallbacks. Original pose-confident decisions are
2,554/4,480. These counts describe proposal gates, not total identification
accuracy after fallback. The controls add 74/142 confident decisions beyond
the original pose route, but lose more of the previously confident decisions.
Their additional localization cost has not been established on Pi.

Reject as an unconditional ROI replacement. No expanded-data or Pi replay is
performed for this failed screen. `tools/screen_rotated_localizer.py` retains
every failed localization and all trial scores in the private
`rotation-localizer-screen-20261029/` evidence folder. No rotation policy is
registered in the application.
