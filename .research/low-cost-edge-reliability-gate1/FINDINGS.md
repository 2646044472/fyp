---
topic: low-cost-edge-reliability-gate1
created: 2026-08-28
last_verified: 2026-08-28
status: active
depth: deep
related:
  - edge-selective-observation-audit
sources:
  - url: https://doi.org/10.5194/amt-18-4871-2025
    fetched: 2026-08-28
  - url: https://doi.org/10.6084/m9.figshare.29310890.v3
    fetched: 2026-08-28
  - url: https://doi.org/10.1145/3773274.3774280
    fetched: 2026-08-28
  - url: https://doi.org/10.1145/3812836.3814778
    fetched: 2026-08-28
  - url: https://arxiv.org/pdf/1707.00788
    fetched: 2026-08-28
  - url: https://doi.org/10.1109/TNSE.2023.3306202
    fetched: 2026-08-28
---

# Low-Cost Edge Reliability Gate 1

## Summary

C1, calibration-age-aware CO2 alert/no-alert/inspect, is killed in its stated form. Its confirmed public data are outdoor K30/Picarro co-location records, not a classroom action workflow; the inspected tables also lack the claimed raw environmental inputs and do not support a high-CO2 ventilation threshold experiment.

C3, resource-informed edge-service failure suspicion, has a direct Pi/Jetson neighbor that already studies the resource-stress timeout trade-off, and a 2026 downstream stress-harness artifact. A narrow, pre-registered boundary result remains possible: establish whether any local telemetry improves on phi-accrual, Lifeguard, percentile timeout, and one-signal thresholds for stated device/workload/fault cells.

C2 and C4 remain unready because their data/hardware/task assumptions and exact-neighbor gates have not been met. No direction is locked.

## Findings

Cai et al.'s 30-month CO2 study provides a useful low-cost sensor drift artifact, but its public records are outdoor reference co-location with three K30 sensors. The candidate audit inspected the supplied tables and found no raw temperature, relative-humidity, or pressure columns, while the Picarro reference column's largest non-missing value was 739.61 ppm. This defeats the proposed classroom false-safe and inspection evaluation rather than merely weakening it.

Pourreza and Narasimhan's UCC 2025 work already centers resource stress, timeout false positives, detection delay, and Pi 4B/Jetson Nano. EdgeStressBench subsequently provides a resource-stress orchestration and measurement artifact. Consequently, replacing static timeouts with an untested resource-aware state machine is not a defensible central claim.

The remaining C3 question is conditional: within a declared observation model and fault process, can local resource telemetry improve a strong adaptive detector? Identical local traces from healthy contention and fail-slow behavior create an identification boundary, so any result must be limited to the evaluated devices, workloads, horizons, and injected faults.

## Insights

- Public data availability is not enough: the support of the reference labels must cover the claimed action threshold and operational story.
- A negative transfer or one-signal-suffices result for C3 would be useful because it removes unjustified multi-signal detector complexity under fixed baselines.
- The existing risk-audited cascade sensing candidate remains a separate Amber question; this round does not promote it.

## Strongest objection

The remaining C3 boundary study could still collapse if phi-accrual, Lifeguard, or one resource threshold matches its false-failover/detection-delay frontier. Its value depends on a frozen cross-device, workload, and fault protocol, not a new classifier.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| C1 public-data classroom CO2 inspection policy | Dataset setting, fields, and reference range cannot support the asserted action task. | 2026-08-28 |
| C3 new resource-aware detector or stress-harness claim | UCC 2025 and EdgeStressBench cover the core scenario, signals, endpoint, and experimental machinery. | 2026-08-28 |

## Open questions

- Is EdgeStressBench's exact repository revision compatible with the UCC timeout protocol on available hardware?
- Are a Pi/Jetson, isolated stress-injection environment, and project duration available for C3's required cross-device protocol?
- Can the archived risk-audited cascade candidate pass a fresh exact-claim citation-chain audit with a complete full-population ground-truth protocol?

## Timeline

- 2026-08-28 - Gate-1 divergence plus candidate-specific falsification completed; C1 killed and C3 pivoted to an Amber boundary study.
