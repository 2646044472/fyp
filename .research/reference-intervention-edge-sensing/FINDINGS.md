---
topic: reference-intervention-edge-sensing
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - adaptive-sensing-audit
  - ebr-i2c-action-boundary
sources:
  - url: https://doi.org/10.13031/ja.15603
    fetched: 2026-08-31
  - url: https://arxiv.org/html/2506.09186v1
    fetched: 2026-08-31
  - url: https://arxiv.org/html/2607.14760v1
    fetched: 2026-08-31
  - url: https://pmc.ncbi.nlm.nih.gov/articles/PMC4080814/
    fetched: 2026-08-31
  - url: https://ojs.aaai.org/index.php/AAAI/article/view/32257/34412
    fetched: 2026-08-31
---

# Reference intervention edge sensing

## Summary

This round sought a low-cost edge direction in which a physical reference action provides information unavailable from passive sensing. It is now superseded: PHT-2R is occupied by automated pH/EC compensation and calibration scheduling, while the candidate's own affine equal-noise model makes the widest two-buffer pair fixed D-optimal. LENS-RC is also killed as a thesis: controlled chart metrology/self-test, passive camera-health monitoring and costly-observation routing already occupy its components. A chart can test one named image-path condition under frozen capture settings, but cannot validate a scene-derived record.

## Findings

### PHT-2R is superseded [KILL]

Cho et al. describe automated one- and two-point normalization for pH/EC probes, with the first handling offset and the second sensitivity variation, and compare the system with laboratory analysis. Hurst et al. model affine chemical-sensor response coefficients and allocate a finite calibration budget through uncertainty-based interval scheduling. Under PHT-2R's stated model, a one-point design has rank one and two equal-noise points have information determinant proportional to the squared buffer separation. The largest permissible separation is therefore a fixed design choice. An `accept / unknown` report after that calibration is interval reporting rather than a distinct mechanism.

### LENS-RC is killed as a thesis [KILL]

Ma et al. provide the required low-cost passive clean-reference baseline for camera-path monitoring. Camera charts and active calibration targets are established metrology, and the SIDL work occupies a new dirty-lens dataset/restoration claim. A fixed chart observes camera/lens/illumination behavior, not a hidden tabletop scene state. Thus a chart pass cannot certify a count or condition record when distinct scene truths can share the same task image and chart result.

ISO 12233:2024 and IEEE 1858-2023 establish the chart/SFR image-quality component. Heuillet, Ahmad and Durand (UAI 2024) establish costly information acquisition as partial monitoring. The remaining external-chart action therefore does not supply a distinct mechanism merely by being local or low-cost. The only defensible activity is a short apparatus preflight: with frozen pose, exposure, illumination and chart geometry, test a named camera-path degradation against a Ma-style passive monitor, fixed-period chart capture and always-chart capture at equal cost. A positive or negative result is configuration evidence, not a reason to reserve the FYP slot.

## Insights

- A reference action is not automatically a new observation model. Its value must remain after an equally informed policy receives the same action result and cost.
- A witness for one causal path cannot certify an endpoint controlled by another latent path. A camera chart can assess image-path health but not independently label scene truth.
- Algebraic identifiability can kill an adaptive-sensing claim early: once two reference points already determine the candidate's two free coefficients, relabeling their use as a policy does not create a new information result.

## Strongest objection

LENS-RC's preflight may simply reproduce a fixed chart schedule or Ma-style passive monitor once settings are controlled. A positive result on a single camera or synthetic contamination condition would not establish a reusable mechanism; the component, policy and broad-record boundaries are already failed.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| PHT-2R selected two-buffer pH policy | Standard one/two-point drift handling plus calibration scheduling occupy the mechanism; fixed maximum separation is optimal under its stated model | 2026-08-31 |
| Generic LENS-RC record-validity router | Chart outcome does not identify scene truth, and camera-health/chart components are established | 2026-08-31 |
| Thermal uncertainty action | 2026 on-device thermal uncertainty work is a direct component/endpoint neighbor | 2026-08-31 |
| Load-cell reference-mass scheduler | Compensation and reference allocation reduce this to an implementation/metrology demonstration | 2026-08-31 |
| Battery diagnostic pulse | Active pulse observability is an established BMS family and creates an unnecessary safety scope | 2026-08-31 |

## Open questions

- If the apparatus is otherwise useful, can a fixed-chart intervention improve a named camera-path health alarm on camera- and scene-held-out physical blocks after controlling exposure, illumination and geometry? This is an instrumentation question only.

## Timeline

- 2026-08-31 - divergence generated pH, camera, thermal, load-cell and battery-reference candidates.
- 2026-08-31 - independent validation killed PHT-2R and restricted LENS-RC to a controlled camera-path witness preflight.
- 2026-08-31 - a further active-chart audit killed LENS-RC as a thesis after component, policy and boundary collisions; the preflight remains optional apparatus work.
