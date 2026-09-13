---
topic: polarization-material-glare-boundary
status: active/amber
searched_at: 2026-08-31
sources: [CVF, arXiv, IEEE, Springer, PLOS ONE]
---

# Polarization, Glare and Material State

## Summary

An external linear polarizer could be added cheaply to the Pi RGB/NoIR setup, but the optical mechanisms are already occupied. Only a finite exact-marker value-of-information test remains Amber.

## Findings

- Tang (CVPR 2024) already uses four polarization angles, transparent film and QR/OCR downstream evaluation: https://arxiv.org/html/2403.04368v1.
- PolarFree (CVPR 2025) occupies reflection/transmission reconstruction with RGB plus four polarization angles: https://arxiv.org/html/2503.18055.
- Khandaker (2024) evaluates glare mitigation across recognition, tracking, depth and lane endpoints: https://arxiv.org/html/2404.10992.
- Laser Shield (DAC 2024) occupies polarizer rotation for attack defense: https://doi.org/10.1145/3649329.3657358.
- Water/glare angle dependence and photoelastic stress benchmarks further kill universal wetness or stress claims: Venkatesulu 2025 https://doi.org/10.1364/AO.544390; Efferz 2024 https://doi.org/10.1007/s40940-024-00270-3; MultiPolar 2026 https://doi.org/10.3390/data11030055.

## Surviving gate

`POL-GLARE-VOI`: one controlled filter intervention for a printed marker behind a transparent cover, compared at matched cost against no-filter, fixed-filter, fixed-two-shot, scalar quality and digital deglare. Require independent cover/glare labels, manual or logged exposure, angle/lux/energy logs and held-out illumination. A single external sheet is not a full-Stokes camera.

## Strongest objection

Polarizer attenuation plus auto-exposure, scene angle and material variation can explain any apparent gain. If fixed controls or RGB quality features are Pareto-optimal, report a null and kill the thesis claim.

## Decision

**HOLD (Amber) for POL-GLARE-VOI; PIVOT for POL-WET-STATE/POL-STRESS-TRUST; KILL POL-SEC-ANGLE.** No thesis is locked.
