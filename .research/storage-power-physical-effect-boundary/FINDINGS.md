---
topic: storage-power-physical-effect-boundary
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - nonreference-systems-lifecycle
  - edge-provenance-outage
sources:
  - url: https://www.microsoft.com/en-us/research/wp-content/uploads/2021/10/tos-crashmonkey.pdf
    fetched: 2026-08-31
  - url: https://arxiv.org/pdf/2503.01390
    fetched: 2026-08-31
  - url: https://arxiv.org/pdf/1805.00140
    fetched: 2026-08-31
---

# Storage, power, and physical-effect boundary

## Summary

This round tested cheap physical edge-reliability ideas outside camera sensing, OTA and generic redundant computation. No thesis candidate survives. FSD-WIT is KILL: recovery-oracle crash testing, real power-fault validation and application crash-state selection already occupy the method family. For synthetic records, the standard valid-prefix scan defines and implements retention; for real sensor values it cannot establish acquisition truth. POF-ADM is only an optional instrumentation condition. LED-effect, UART-continuity and card-capability ideas are preflight controls, not research mechanisms.

## Findings

### FSD-WIT is KILL [KILL]

CrashMonkey/ACE provide bounded black-box recovery checking with persistence points and recovered-image oracles. Pathfinder (PACMPL/OOPSLA 2025) provides application-level representative crash-state testing. Ahmadian et al. combine physical supply cuts, known original data/checksums and post-reboot failure classification. Thus replacing a storage device with a cheap microSD card does not create a distinct task, action or evaluation endpoint.

The strongest simple baseline is a preallocated append-only layout with a two-phase validity marker, sequence/checksum scan after reboot, and `unknown` for every incomplete slot. It accepts the valid prefix by its declared predicate. Any remaining experiment characterizes a named configuration rather than establishing a new evidence mechanism.

### Boundary [KILL]

A synthetic external oracle cannot be silently generalized to a sensor-record truth claim: an on-card checksum establishes byte consistency, not that the sensor value was acquired or semantically correct. A confidence interval also needs a predeclared binary-trial population, confidence level, threshold, sample size and independence rationale. Repeated cuts on a changing consumer card do not identify another card, a different waveform or a stable retail-model population.

### POF-ADM is instrumentation only [PIVOT]

Power-fail comparator/reset state can stratify a power-cut experiment but cannot observe opaque FTL commit state or acquisition correctness. It warrants inclusion only if it reduces false retention against the valid-prefix baseline at a preregistered matched unknown rate.

## Insights

- A physical fault rig is evidence about its declared hardware and waveform, not a general certificate.
- An offline oracle can create a valid benchmark but must not be re-described as an on-device witness when it is unavailable to the deployed decision.
- A statistical reliability statement is meaningful only for its sampling population; a train/test split does not produce cross-device transportability.

## Strongest objection

The proposed value is a low-cost empirical discontinuity across opaque removable media. That is a useful lab observation but collapses into a benchmark/replication once B0 valid-prefix recovery is run, and it provides no new mechanism or general reliability claim.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| FSD-WIT microSD post-reboot evidence boundary | Existing crash and physical power-fault recovery methodology; B0 scan implements the full synthetic decision | 2026-08-31 |
| POF-ADM power-fail record admissibility | Comparator cannot witness card commit or sensor truth | 2026-08-31 |
| LED physical-effect loopback | Electrical/optical diagnostics are an established component family and cannot certify a human-facing effect | 2026-08-31 |
| UART continuity boundary | Sequence, length, CRC and overflow flags are the direct simple baseline | 2026-08-31 |

## Open questions

- Could a short power-cut dataset be useful as a reproducible lab appendix with a deliberately configuration-scoped result? This is not a thesis-direction question.

## Timeline

- 2026-08-31 - divergence generated storage/power/physical-effect candidates.
- 2026-08-31 - independent validation killed FSD-WIT as a thesis and restricted POF-ADM to instrumentation.
