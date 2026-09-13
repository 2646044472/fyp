---
topic: wet-view-drainage-boundary
created: 2026-09-04
last_verified: 2026-09-04
status: superseded
depth: deep
related:
  - pi5-rgb-noir-adaptive-sensing-boundaries
  - physical-failure-synthetic-transfer-boundary
sources:
  - url: https://doi.org/10.1017/wat.2026.10018.pr5
    fetched: 2026-09-04
  - url: https://doi.org/10.1111/jfr3.13038
    fetched: 2026-09-04
  - url: https://doi.org/10.1080/13241583.2023.2292608
    fetched: 2026-09-04
  - url: https://doi.org/10.3390/app15052690
    fetched: 2026-09-04
  - url: https://openaccess.thecvf.com/content_cvpr_2013/html/You_Adherent_Raindrop_Detection_2013_CVPR_paper.html
    fetched: 2026-09-04
  - url: https://openaccess.thecvf.com/content/ICCV2021/html/Li_Lets_See_Clearly_Contaminant_Artifact_Removal_for_Moving_Cameras_ICCV_2021_paper.html
    fetched: 2026-09-04
---

# Wet-view drainage decision boundary

## Summary

`WET-VIEW-IDENT` is not a viable positive FYP direction. Urban drainage work already covers camera-based debris/culvert blockage classification, action-relevant uncertainty, and camera plus water-level/flow hybrid hydraulic-blockage assessment. Lens water/dirt is separately an established contamination-detection, cleaning-trigger, and restoration family.

The proposed scene-blockage versus optical-path-contamination distinction is physically real, but it does not create a defensible new mechanism when the proposed repair is a hydraulic sensor, fusion, conservative review, a camera-health score, or an optical cleaning/deraindrop intervention. It may remain as a nuisance/control cell in a finite visual-evidence experiment, not as the FYP's claimed contribution.

## Findings

Drainage-camera blockage classification is directly occupied. Smith et al. use 577 labelled CCTV images from a culvert to classify blocked versus unblocked trash-screen states, including imbalance handling and augmentation. Rowlatt et al. analyse 1,089 images from a Cardiff trash screen, use `low risk / high risk / unknown risk` labels, and study operational uncertainty under fixed-time, water-level-triggered and manual captures. Their setting explicitly varies daylight and seasonal conditions.

The proposed independent hydraulic witness is also not a new observation model. The AIoT framework of Iqbal et al. combines camera-based visual blockage status with upstream water level, inlet discharge and surface velocity, and describes visual-only, hydraulic-only and hybrid predictors of hydraulic blockage. Recent field work likewise combines edge vision with radar water level, flow velocity, rainfall and environmental context. Therefore a camera plus flow/water-level system that reports drainage blockage, dispatch priority, or a confidence state is a direct continuation.

Lens contamination is a real and measurable failure source, but its positive method space is occupied. Kim et al. directly measure water-droplet effects on cover-glass MTF and object detection, reporting substantial degradation under controlled contamination. You et al. provide adherent-raindrop detection and removal in video, while Li et al. address dust, dirt and moisture contaminant removal for moving cameras. So a new water-droplet detector, de-raindrop model, focus/multi-view discriminator, cleaning trigger, or generic image-health score does not distinguish this candidate from direct literature.

The only narrow observation remaining would be a physical paired-world control: real screen obstruction versus water/dirt on a camera protection window, with preassigned physical states and no sensor leakage to the image-only policy. That control is useful for testing a different visual-evidence study, but it does not support a standalone drainage, sensor-fusion, or camera-diagnosis paper.

## Insights

- The camera and hydraulic channels solve the same operational problem from complementary measurements; making the hydraulic channel the proposed “minimal witness” is standard hybrid blockage assessment, not a new causal result.
- Calling an action `manual review` or an image class `unknown` does not create a new endpoint because operational uncertainty has already been evaluated in field CCTV blockage work.
- The useful transferable lesson is experimental: a physical scene state and an optical-path state must be labelled independently whenever camera evidence is used to justify a record or action.

## Strongest objection

No located source was found with the exact wording “scene blockage versus protection-window contamination action ambiguity.” That absence is insufficient: the candidate's mechanism decomposes into already covered drainage hybrid sensing and established lens-contamination handling, so the residual is too small and too easily absorbed by direct baselines.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| WET-VIEW-IDENT as a primary drainage FYP | Camera/hydraulic hybrid blockage assessment and lens-contamination methods directly absorb its observation, action and repair mechanisms. | 2026-09-04 |

## Open questions

- Can a non-drain, non-safety field-maintenance record offer a materially different physical truth and decision endpoint from the established hybrid blockage family?
- If a paired scene-versus-optical-path cell is retained, which already-live finite evidence audit can use it as a nuisance control without changing its claim?

## Timeline

- 2026-09-04 - New direct-neighbour and contrarian audit; candidate marked superseded as a primary direction.
