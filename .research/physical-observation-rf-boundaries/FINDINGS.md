---
topic: physical-observation-rf-boundaries
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - adaptive-sensing-audit
  - outside-family-edge-decision-boundaries
sources:
  - url: https://doi.org/10.3390/s24165268
    fetched: 2026-08-31
  - url: https://doi.org/10.1016/j.measurement.2025.117721
    fetched: 2026-08-31
---

# Physical observation and RF boundaries

## Summary

A physical-observation/RF search generated CSI, UWB, magnetic, mmWave and gas-sensor candidates. All are superseded as thesis directions. UWB was the sole temporary Amber lead, but independent validation found direct multi-link online trustworthiness and fine-grained CIR/range credibility systems. Its residual physical-cause claim is not identified by passive link diagnostics.

## Findings

### UWB reference-link cause triage [KILL]

Peterseil et al. (2024) already assess UWB link, node and system indicators online, including per-link RSSI/CIR anomaly signals and sequential filtering of untrusted anchors. Yang et al. (2025) already classify ranging-error sources from CIR/range evidence and choose retain/delete/mitigate. Renaming one link as a target and others as fixed references does not change this information/action structure.

The remaining cause statement is weaker, not new: a finite vector of CIR/FQA/RSSI/range diagnostics lacks an independent propagation-path or radio-state witness. Different target-path, shared interference and multipath conditions can overlap in these summaries. A finite labelled fixture set may support a configuration classifier, but cannot establish general causal attribution or unseen-fixture transfer.

### Other sensor families [KILL]

OpenCSI occupies CSI baseline-maturity/reliability/abstention. Magnetic residuals are calibration/localization and have field non-uniqueness. mmWave fixed reflectors are calibration, not scene truth. Reference-free low-cost gas-sensor quality assurance has a direct Pi-class on-device neighbor.

## Insights

- A second RF link can provide incremental data without creating a new causal inference mechanism.
- A source of extra measurements must be evaluated against an equally informed baseline, not merely against a lower-information single-link rule.
- Diagnostic register availability is a feasibility fact, not a novelty result.

## Strongest objection

The candidate's physical labels describe fixtures selected by the experimenter rather than radio-observable root causes. Existing systems already act on the same multi-link evidence, and the unobserved-cause problem remains when the vocabulary is made more specific.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| UWB-RL-CAUSE | Existing multi-link trustworthiness/error-source systems; passive cause ambiguity | 2026-08-31 |
| CSI-BaselineGate | Existing CSI reliability/maturity/stale-baseline abstention | 2026-08-31 |
| MAG-GeometryWitness | Calibration/localization and field ambiguity | 2026-08-31 |
| MMW-ClutterWitness | mmWave self-calibration/state-detection collision | 2026-08-31 |
| AQ-ReferenceFreeAudit | Pi-class reference-free sensor diagnosis collision | 2026-08-31 |

## Open questions

- A narrow raw-CIR replication can measure a named board/fixture performance boundary. It is not a thesis direction without a new observation or endpoint.

## Timeline

- 2026-08-31 - divergence generated physical/RF candidates.
- 2026-08-31 - independent UWB audit killed the temporary Amber lead.
