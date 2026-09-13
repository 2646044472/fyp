---
topic: outside-family-edge-decision-boundaries
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - tta-unlabeled-accept-rollback
  - adaptive-sensing-audit
sources:
  - url: https://arxiv.org/html/2505.01160v1
    fetched: 2026-08-31
  - url: https://openreview.net/pdf?id=wcrff7Gh0RR
    fetched: 2026-08-31
---

# Outside-family edge decision boundaries

## Summary

An outside-family scan generated four mechanisms. None is a thesis direction. Quantisation sign guards are covered by existing verification. Active acoustic path checks are established calibration/self-diagnosis and do not isolate the full measurement chain. Physical-factor label queues collapse to stratified sampling if metadata is known or become non-implementable if it is not. Trace-only deployment risk bounds restate known target-risk non-identifiability.

## Findings

### Factor-aware label queue [KILL]

TActiLE already makes online irreversible retain/discard decisions for a bounded label batch, retrains locally, and evaluates accuracy, time and memory against standard selection controls. A physical factor known before review supplies stratum metadata, for which fixed quota/stratified sampling is the decisive low-compute baseline. If the factor must be learned by the reviewer, it cannot drive the pre-review queue. Neither case identifies labels in a never-labelled factor cell without an independently stated structural model.

### Trace-only performance boundary [KILL]

Garg et al. already show that arbitrary conditional shift makes target accuracy unidentifiable from unlabeled data. Keeping ordinary resource telemetry constant extends the same two-world construction: identical input/prediction/telemetry traces can have opposite labels and risk. A restricted shift assumption, delayed labels or independent reference changes the task into a known family; no new sufficient/minimal physical witness is specified.

### Verification and acoustic self-test [KILL]

Quantisation robustness/verification directly cover reference-versus-integer semantic preservation. Active acoustic self-diagnosis and low-cost microphone calibration already use reference excitation and independent meters. The remaining low-cost apparatus differences are not new decision mechanisms.

## Insights

- Metadata does not become a novel active-learning observation merely because it names a controlled physical factor.
- Telemetry can be useful operationally, but it is not automatically a semantic label witness.
- A negative identification theorem is a candidate only when its observation restriction or its minimal restoring witness is materially new and formally specified.

## Strongest objection

All four ideas substitute a board, physical bench or controlled factor for an already-defined action/verification/inference family. None changes the direct task/action/evaluation endpoint, and the two remaining pivots fail before any hardware purchase.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| AL-FactorQueue | TActiLE collision; known factors reduce to stratification and unknown factors leak labels | 2026-08-31 |
| UPM-EdgeBound | Direct instance of known unlabeled target-risk impossibility | 2026-08-31 |
| QNN-DecisionGuard | Quantisation verification is established | 2026-08-31 |
| ASV-PathCheck | Active acoustic self-diagnosis/calibration is established and path-entangled | 2026-08-31 |

## Open questions

- A future direction must state one independently observable, pre-action variable that changes a named decision and has a nontrivial baseline beyond stratification, reference calibration or known verification.

## Timeline

- 2026-08-31 - divergence generated four outside-family mechanisms.
- 2026-08-31 - independent validation killed all four before implementation.
