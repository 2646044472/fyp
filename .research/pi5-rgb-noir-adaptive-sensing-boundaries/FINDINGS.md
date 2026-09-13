---
topic: pi5-rgb-noir-adaptive-sensing-boundaries
created: 2026-08-31
last_verified: 2026-08-31
status: active
depth: deep
related: [edge-palm-baselines, physical-observation-rf-boundaries]
sources:
  - url: https://www.raspberrypi.com/documentation/computers/camera_software.html
    fetched: 2026-08-31
  - url: https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2503.02170
    fetched: 2026-08-31
  - url: https://papers.neurips.cc/paper_files/paper/2024/file/cc596a803bedc7a03a87e98c77a22efe-Paper-Conference.pdf
    fetched: 2026-08-31
  - url: https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf
    fetched: 2026-08-31
  - url: https://openaccess.thecvf.com/content/CVPR2025W/TMM-OpenWorld/papers/Liao_Benchmarking_Multi-Modal_Semantic_Segmentation_under_Sensor_Failures_Missing_and_Noisy_CVPRW_2025_paper.pdf
    fetched: 2026-08-31
  - url: https://doi.org/10.1109/MIPR62202.2024.00039
    fetched: 2026-08-31
  - url: https://doi.org/10.1139/tcsme-2023-0156
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2607.14760
    fetched: 2026-08-31
---

# Pi 5 RGB/NoIR Adaptive Sensing Boundaries

## Summary

The purchased Pi 5B, RGB camera, NoIR camera and IR illuminator make a static non-personal optical bench feasible. They do not make generic adaptive sensing novel: Lens (ICLR 2025), AdaptiveISP (NeurIPS 2024), AdaptiveAE (ICCV 2025) and CM-ASAP (MIPR 2024) already cover adaptive camera, ISP, exposure and modality actions under resource budgets. A physical-failure transfer benchmark and an IR on/off condition-diagnosis experiment remain Amber/Pivot hypotheses, not a locked thesis. The next purchase should add independent measurement or controlled intervention, not another model or camera.

## Findings

The standard Camera Module 3 has an IR-cut filter while the NoIR variant omits it, so the two devices are distinct optical paths. Raspberry Pi documentation also does not guarantee synchronized 3A behavior for two cameras. Sequential captures of static printed markers are therefore feasible; moving-scene paired comparisons need an independent timing reference.

Generic preview-based mode selection, exposure scheduling, burst timing and modality activation are direct neighboring problem structures. Lens selects sensor parameter options from an image and compares fixed, random and oracle baselines (Secs. 3.1-3.2, 4-5, pp. 4-8). AdaptiveISP selects ISP sequences with a compute-time penalty (Secs. 3-5, pp. 4-10). AdaptiveAE selects ISO/shutter sequences under an exposure-time budget (ICCV 2025, pp. 25176-25185). CM-ASAP activates modalities and frame rate under an edge power budget (MIPR 2024, pp. 207-213). These collisions kill ACR-MODE, BURST-COMP, EV-EXPO and MOD-MISSING as generic thesis mechanisms.

Two narrower candidates remain. PHY-MASK compares synthetic missing/noisy masks with physically unplugged, blocked, saturated or covered camera paths on a printed-marker task. Its useful result is a finite physical-versus-digital ranking test, not a general failure guarantee. FULL-CAP similarly tests whether digital corruption severity predicts the ranking of real capture failures; it is a negative benchmark.

ILLUM-CAUSE/OPT-WIT and ASI-IR use a real IR on/off action. The intended outcome is a bounded record state for a named clean/cover/contamination condition, with an independently printed marker as the task oracle. The claim is only that the physical intervention adds value beyond a passive quality router or fixed two-shot ratio rule at matched time and energy. Transparent contamination can be IR-transparent, and auto-exposure can confound the intervention, so the result may be non-identifiable.

| Candidate | Current status | Honest endpoint |
|---|---|---|
| ACR-MODE | KILL | Fixed RGB/NoIR engineering control |
| BURST-COMP / EV-EXPO | KILL | Exposure/timing control only |
| MOD-MISSING | KILL | Physical cells for PHY-MASK |
| CAL-TRANSPORT | PIVOT | RGB-to-NoIR threshold-shift table |
| PHY-MASK / FULL-CAP | PIVOT | Negative physical-vs-digital benchmark |
| ASI-IR / OPT-WIT / ILLUM-CAUSE | HOLD (Amber) | Named physical value-of-information test |

## Insights

- The hardware changes feasibility, not novelty. The distinction must come from a physical intervention or independent oracle.
- A printed code/marker is preferable to a human or biometric label because exact correctness is externally known and the bench remains non-personal.
- The highest-risk baseline is simple: fixed two-shot IR off/on plus a brightness/blur or IR-ratio threshold. If it matches the learned policy, the mechanism is gone.
- The most honest negative result is that synthetic masks or digital corruptions do not preserve the action ranking observed under physical camera failures, or that IR has no marginal value. Both results delimit when edge sensing simulations mislead.

## Strongest objection

The IR intervention may only change the camera's auto-exposure/white-balance response, while low light and transparent contamination remain observationally equivalent. In that case no policy can identify the proposed cause from the available observations; the correct output is `unknown` or a scoped condition map.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| Generic RGB/NoIR adaptive selector | Directly occupied by Lens, AdaptiveISP, AdaptiveAE and CM-ASAP | 2026-08-31 |
| New tiny fusion or exposure model | Model/board substitution does not change the task or endpoint | 2026-08-31 |

## Open questions

- Exact camera module revision, illuminator wavelength/power/diffuser and eye-safety specification.
- Whether AE, gain and white balance can be frozen or fully logged in the installed camera stack.
- Independent illuminance and capture-energy measurement.
- Whether clean/contaminated cover states can be assigned before capture and held out by material/geometry.
- Whether the fixed two-shot ratio baseline already dominates the proposed IR policy.

## Timeline

- 2026-08-31 - merged independent Pi 5 RGB/NoIR divergence and validation; generic adaptive sensing killed, physical-intervention and physical-failure boundary candidates retained as Amber/Pivot.
