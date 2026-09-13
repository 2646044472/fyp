---
topic: adaptive-sensing-audit
created: 2026-08-28
last_verified: 2026-08-28
status: concluded
depth: medium
related:
  - c3-transfer-boundary
sources:
  - url: https://arxiv.org/abs/2607.15235
    fetched: 2026-08-28
  - url: https://doi.org/10.1109/COMSNETS67989.2026.11418151
    fetched: 2026-08-28
  - url: https://doi.org/10.1109/JIOT.2019.2933335
    fetched: 2026-08-28
---

# Adaptive Sensing Direction Audit

## Result

AS1, an independently audited cheap-sentinel / costly-verifier sensing policy, is **PIVOT**, not a replacement FYP direction. Ordinary adaptive sampling, uncertainty-triggered verification, local event wake-up, and energy/event-coverage trade-offs are already direct literature families. The remaining independent-reference and `event / no-event / unknown` machinery is required evaluation discipline for any selective sensing study, but is too narrow to carry a standalone contribution.

## Load-bearing evidence

- [KILL] Lu et al., *Adaptive Sampling for Spatiotemporal Anomaly Monitoring in WSNs*, arXiv:2607.15235v1, submitted 2026-07-16, https://arxiv.org/abs/2607.15235, Sec. I pp. 1-2 and Sec. IV-B/C pp. 6-8: continuous sentinels, uncertainty-driven sparse sampling, event-triggered wake-up, detection/coverage/delay, and cost coexist in one recent system.
- [KILL] Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, DOI https://doi.org/10.1109/COMSNETS67989.2026.11418151, Sec. II-A/B pp. 3-4 and Sec. III pp. 4-6: low-cost ESP32 environmental dynamic sampling and secondary prediction-based fault sensing are also occupied.
- [K] Loreti, Bracciale, and Bianchi, *StableSENS*, IEEE IoT J. 6(6), 2019, https://doi.org/10.1109/JIOT.2019.2933335, Sec. I p. 2/Fig. 1: for schedule-independent events and fixed sample count, equal periodic intervals minimize residual blind time. This is AS1's decisive simple baseline condition.
- [K] Han et al., *A Comparative Study of Semiconductor Virtual Metrology Methods and Novel Algorithmic Framework for Dynamic Sampling*, IEEE TSM 38(2), 2025, https://doi.org/10.1109/TSM.2025.3531920, Secs. I, III-C, IV-C pp. 232-239: uncertainty-selected costly measurements versus fixed/random sampling under drift/shift are directly studied.

## Boundary

With only a cheap sentinel observation during a skipped verifier interval, a no-event physical trajectory and a short excursion can yield the same observed trace. The online policy cannot truthfully turn every skipped interval into `no-event`; it must report `unknown`, observe under a declared maximum gap, or rely on a separately validated physical predictive relation. A continuous reference logger prevents selective evaluation only if its timing, threshold, response/inclusion time, calibration, and independence are established.

## Conditional reopening gate

Reopen only if a benign physical task proves all three before target evaluation: (1) a source-only, independently measured predictive relation from sentinel history to future verifier event; (2) auditable reference/injection/timestamp labels; and (3) a held-out advantage over a budget-matched, phase-randomized periodic maximum-gap verifier baseline. Otherwise use the reference and tri-state accounting as experimental hygiene, not thesis novelty.
