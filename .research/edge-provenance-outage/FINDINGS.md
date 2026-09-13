---
topic: edge-provenance-outage
created: 2026-08-28
last_verified: 2026-08-28
status: superseded
depth: medium
related:
  - low-cost-edge-reliability-gate1
sources:
  - url: https://doi.org/10.1109/JSEN.2024.3466966
    fetched: 2026-08-28
  - url: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
    fetched: 2026-08-28
  - url: https://doi.org/10.1007/s44187-025-00427-1
    fetched: 2026-08-28
  - url: https://media.path.org/documents/Cold_Chain_Temperature_Data_Job_Aid_FINAL_May_2025.pdf
    fetched: 2026-08-28
---

# Outage-Provenance Thermal Evidence

## Summary

Superseded on 2026-08-29. A local temperature node may honestly emit `known-safe`, `known-violation`, or `indeterminate` only from persisted evidence, but a crash-atomic durable journal plus the same verifier subsumes the proposed fields and incomplete-trace semantics are established. The remaining work is a bounded crash-window measurement, not a direction lock.

The narrow research question is whether this source-local provenance reduces reference-labelled benign intervals sent to `indeterminate` without increasing unsafe `known-safe` decisions, at the same sensing and radio budget as a retained latest-value stream, QoS plus a persisted sequence/epoch, online imputation, and `any gap => indeterminate`.

## Findings

Bagchi, Jenamani, and Routray's 2024 reefer paper directly covers online missing-value imputation under power, communication, and sensor disruptions, but its accessible official metadata/abstract reports RMSE, MAE, MAPE, bias, and retained-information endpoints rather than an evidence-state decision. The full primary PDF remains [GAP], so this is a direct-neighbor lead, not proof of distinction.

The OASIS MQTT 5.0 standard defines QoS 1 as at-least-once delivery for an application message (Sec. 4.3.2, p. 94) and retained messages as replacement of the prior application message for a topic (Sec. 3.3.1.3). It does not itself certify whether an unsent sample was never scheduled, could not be read, was locally persisted, or was later acknowledged by a gateway. This supports a scoped observation-model distinction, not a claim that a new protocol is required.

Firl et al. (2025) use independent reference loggers and separately measure packet loss and temperature deviation in practical supply-chain deployments. PATH's May 2025 job aid illustrates a physical evidence gap after power loss, thermal holdover, and logger battery exhaustion. Both support the bounded story, but neither supplies a research-method novelty claim.

## Strongest objection

A durable local journal that includes `epoch`, expected sample index, read status, and delivery acknowledgement may be functionally equivalent to R1. If `QoS 1 + persisted journal` achieves the same reference-labelled safety/availability frontier, R1 has no remaining systems mechanism. Its only residual value would be a pre-registered empirical boundary map of which outage/fault cells cannot support an honest release decision.

## Open questions

- Does Bagchi et al.'s full 2024 paper already use a decision/action endpoint beyond its accessible imputation summary?
- Can a plain persistent journal make every R1 provenance state receiver-identifiable under the finite non-adversarial fault model?
- Does a physical rate envelope provide any extra safe-release information after a blackout, beyond timestamps and the conservative `any gap => indeterminate` rule?
- Can a low-cost reference logger and power-interruption trace independently validate the claimed fault provenance?

## Timeline

- 2026-08-28 - divergence generated R1 and marked it PROMOTE only to exact-claim/feasibility audit. No global novelty claim is implied.
- 2026-08-29 - independent validation killed R1 as a standalone mechanism; retain only a device-specific durable-journal/crash-window control.
