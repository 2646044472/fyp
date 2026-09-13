---
topic: round12-sensing-divergence-boundary
created: 2026-08-31
last_verified: 2026-08-31
status: active
depth: deep
related: [pi5-rgb-noir-adaptive-sensing-boundaries, cross-device-illumination-transfer-boundary]
sources:
  - url: https://arxiv.org/abs/2606.17376
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2509.18460
    fetched: 2026-08-31
  - url: https://doi.org/10.1109/OJCOMS.2024.3363731
    fetched: 2026-08-31
  - url: https://openaccess.thecvf.com/content/ICCV2025/html/Chen_Image_as_an_IMU_Estimating_Camera_Motion_from_a_Single_ICCV_2025_paper.html
    fetched: 2026-08-31
  - url: https://doi.org/10.1177/16878132261449101
    fetched: 2026-08-31
---

# Round-12 sensing divergence boundary

## Scope and date

Physical-frequency and negative-observation sensing candidates for the Pi 5 RGB/NoIR setup, researched and independently validated on 2026-08-31.

## Synthesis

The divergence packet proposed five candidates. `IR-MOD-ID` (two-frequency PWM IR response) is the strongest fresh residual, but remains HOLD/Amber: it may only test finite incremental value beyond fixed two-shot and scalar IR-ratio controls. `LUX-AMBIG` is a matched-photopic-lux spectral identifiability negative benchmark, not a sensor-routing method. `ABSENCE-PULSE` collides with semantic active probing and visual camera challenges; `IMU-BLUR-ATTR` collides with IMU-assisted blur/velocity estimation; `EVENT-DROP` is both benchmarked and infeasible on the present low-cost platform.

The round-12 validation audit independently reaches the same decisions. `XFER-ACT` remains a finite action-rank audit, `POL-GLARE-VOI` remains Amber only if it beats fixed-filter and fixed-two-shot controls, and `IR-CAUSE` remains the sole live pilot gate. No candidate passes all three novelty audits and no global novelty claim is permitted.

Ke, Chu and Lin (published online 2026-05-12) further occupy transparent-material defect inspection with controlled wavelength illumination, full-factorial image variables and local edge deployment. This kills a tempting transparent-defect detector or multi-light comparison as a separate Pi thesis; it does not test the finite action-risk endpoint.

## Boundary and next gate

Passive RGB/lux/quality observations can be shared by low-light and transparent-cover worlds requiring different actions. Independent fixture labels, an exact payload oracle, frozen exposure/white-balance, timing and joule logs, and held-out cells make only a finite risk table identifiable. A repeatable held-out rank inversion or incremental IR information effect is required for promotion; otherwise the correct result is a bounded null or non-identifiability report.

## Insights

- The physical intervention is the only part that changes the observation model; changing the decoder, model size, or deployment board does not.
- A fixed two-shot action directly observes the proposed missing information, so any adaptive policy must demonstrate an action-cost advantage rather than only higher image quality.
- Equal-lux spectral cells are useful as a falsification fixture, but they do not by themselves establish that a lux sensor is valuable.

## Strongest objection

The PWM frequency response may simply be a noisier and more expensive version of the second NoIR+IR capture. If fixed two-shot dominates, the correct outcome is a null and the direction should not be promoted.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| Generic RGB/NoIR adaptive routing | Directly occupied by Lens, AdaptiveAE, Rampure and related sensor-selection work | 2026-08-31 |
| Transparent-material edge defect detector | Ke et al. 2026 already combines multi-light imaging, full-factorial design and edge deployment | 2026-08-31 |

## Open questions

- Whether a Pi-compatible PWM IR driver produces a repeatable frequency response under fixed exposure and white balance.
- Whether transparent-cover and clean-low-light worlds can be independently matched on the passive observable prefix.
- Whether the action-rank inversion survives held-out material and lamp cells.

## Timeline

- 2026-08-31 - round-12 divergence and independent validation stored; no candidate promoted.

## Sources

- Divergence packet: `research/ops/divergence/2026-08-31-round12-sensing-divergence.md`.
- Validation audit: `research/ops/validation/2026-08-31-round12-cross-device-voi-validation.md`.
- Primary sources and exact section/page mappings are recorded in those packets, including Rampure (arXiv:2606.17376), Han (arXiv:2509.18460), Stamatakis et al. (IEEE OJ-COMS 2024), Chen & Clark (ICCV 2025), Agnihotri et al. (CVPRW 2025), and Cazzato (Electronics 2025).
