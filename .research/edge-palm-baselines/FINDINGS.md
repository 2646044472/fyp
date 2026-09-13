---
topic: edge-palm-baselines
created: 2026-08-31
last_verified: 2026-08-31
status: active
depth: deep
related:
  - palm-template-transfer-boundary
sources:
  - url: https://github.com/Li-ChengYan/palmprint-recognition-python
    fetched: 2026-08-31
  - url: https://github.com/xuliangcs/ppnet
    fetched: 2026-08-31
  - url: https://github.com/X-Palm/X-Palm-2026
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2401.08111
    fetched: 2026-08-31
  - url: https://www.raspberrypi.com/documentation/computers/camera_software.html
    fetched: 2026-08-31
---

# Edge Palm Baselines

## Summary

Use the MIT-licensed Fast-CC reimplementation as the initial Pi 5 baseline: it has no model-weight or GPU dependency, and its capture integration can be tested independently of a neural runtime. PPNet is a relevant later comparison, but its public project uses an older Python/PyTorch environment and needs a Pi 5 compatibility gate. X-Palm is the strongest later protocol/data route for cross-domain research, subject to its academic EULA; its supplied training experiments use an RTX A6000. Palm-ID is useful for pipeline decomposition, but its reported server timing is not Pi evidence.

## Findings

Li-ChengYan's `palmprint-recognition-python` repository is an MIT-licensed personal reimplementation for study/comparison. It provides classic coding matchers, pairwise genuine/impostor score generation and a PolyU `P_F` benchmark. Fast-CC uses two Gabor directions and shifted Hamming distance. It is suitable for a reproducible, fixed-stand capture-to-template smoke test, provided the input crop and threshold are recorded.

| Candidate | Artefact state | Pi 5 role | Main blocker |
| --- | --- | --- | --- |
| Fast-CC | Source and MIT licence available; no pretrained model needed | First local 1:1 demo matcher | It requires a stable, manually controlled ROI and a separately frozen camera threshold. |
| PPNet | Source, CC-BY-NC 4.0 licence, pretrained-model links and Pi 4B instructions available | Offline comparison after Fast-CC | The repository's documented environment is Python 3.7-3.8 and PyTorch 1.2-1.7, so current Pi OS compatibility and model integrity are unverified. |
| X-Palm scripts | Benchmark code and EULA-mediated data access available | Later P2 device/domain protocol baseline | Training documentation specifies PyTorch 2.1.1 and an RTX A6000; it is not an edge inference package. |
| Palm-ID | Paper and mobile-system description available | Design/reference upper bound | It has a 76.04M-parameter model, while the paper's 18 ms extraction and 0.33 ms 1:10,000 search metrics are reported on an AMD EPYC 7543 server configuration. |

Raspberry Pi's current camera documentation supports `rpicam-*` applications and Picamera2 on Raspberry Pi OS. That settles the camera integration path, not a palm matcher, ROI detector, threshold or security result.

## Insights

- A descriptor-first baseline separates camera/ROI problems from model/runtime problems, which is the fastest way to make a new Pi setup measurable rather than merely impressive in a demo.
- The best research baseline is not necessarily the first edge runtime: X-Palm should evaluate later device/sensor/model transfer questions, while Fast-CC makes today's capture chain testable.
- Adding a neural network before an ARM-compatible model hash and a fixed input protocol would make a failed demo ambiguous: capture, ROI, runtime and matcher could all be the cause.

## Strongest objection

Fast-CC's strong controlled-dataset results can fail badly on a contactless RGB camera because it is not an online palm detector or pose-normalising ROI extractor. Therefore the first result is only a fixed-stand engineering check, and public-image calibration must not be reported as Pi-camera accuracy.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| Treat PPNet as the default Pi 5 runtime | Its documented stack is old and the current ARM64/model-hash gate is unverified | 2026-08-31 |
| Treat Palm-ID timing as Pi capacity evidence | The cited timing includes an AMD EPYC server configuration | 2026-08-31 |

## Open questions

- Does the exact Pi camera module and fixed physical guide produce a sufficiently repeatable crop for Fast-CC?
- Do source terms authorise processing the supplied archives, and does the institution authorise any persistent local palm template?
- Can a PPNet or X-Palm model be frozen, hashed and run in current Pi OS ARM64 without changing the protocol?

## Timeline

- 2026-08-31 - Initial baseline comparison stored; Fast-CC selected for the first Pi demo and PPNet/X-Palm retained as later controls.
