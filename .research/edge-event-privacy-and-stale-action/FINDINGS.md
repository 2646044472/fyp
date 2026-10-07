---
topic: edge-event-privacy-and-stale-action
created: 2026-09-23
last_verified: 2026-09-23
status: active
depth: deep
related: [physical-failure-synthetic-transfer-boundary]
sources:
  - url: https://arxiv.org/html/2111.14992
    fetched: 2026-09-23
  - url: https://arxiv.org/html/2609.25787
    fetched: 2026-09-23
  - url: https://arxiv.org/html/2512.13439
    fetched: 2026-09-23
  - url: https://arxiv.org/html/2504.07428
    fetched: 2026-09-23
  - url: https://arxiv.org/html/2601.15496
    fetched: 2026-09-23
---

# Event Privacy and Stale Edge Actions

## Summary

No new FYP direction was promoted on 2026-09-23. TRIG-LEAK is HOLD only for a cheap finite event-time privacy/deadline test against fixed-clock, constant-rate and event-DP baselines, after a real confidentiality owner and threat model are specified. STALE-ACT is KILL in its proposed tabletop setting because direct execution-time state read dominates its transition proxy. SLO-REFUSE is PIVOT/KILL-leaning and PROOF-BOUND is KILL as a positive thesis. The primary records are `research/ops/divergence/2026-09-23-cross-mechanism-edge-decisions.md` and `research/ops/validation/2026-09-23-trig-leak-stale-act-validation.md`.

## Findings

| Hypothesis | Direct work and collision | Residual and kill gate |
| --- | --- | --- |
| TRIG-LEAK | Xiong 2021 covers event timing/size DP shaping with dummy and queue costs; Worae 2026 covers causal budgeted camouflage with defense-aware attackers; Sathyavageeswaran 2025 jointly optimizes information leakage and update age. | Only a declared event-time attacker advantage at a hard notice deadline and byte budget is unmeasured here. Fixed clock may dominate; tail deadline misses, ACK/uplink leakage and changed event priors must be reported. Actual confidentiality owner is unknown. |
| STALE-ACT | Gan 2025 routes by task age; Nikkhah 2024/2026 formalize Age of Actuated Information. | Direct current-state MCU read is available in the proposed fixture and defeats proxy necessity. Without an independent witness, identical observations can hide opposite execution-time truth. |
| SLO-REFUSE / PROOF-BOUND | SneakPeek/EdgeServing and local CONTACT-EVIDENCE, respectively, occupy the broad scheduling and assurance families. | No positive thesis claim survives the present story; retain only controls or a negative boundary. |

## Insights

A cheap simulation is useful only as a kill test, not proof of operational privacy: event distribution, attacker vantage, byte-rate units, hard deadline and cover-packet cost determine the frontier. For a fixed packet size s and period T, event-independent fixed-clock masking with worst wait no more than D requires T no greater than D and long-run rate at least s/D, absent multiplexing.

## Strongest objection

TRIG-LEAK may merely instantiate established privacy/timeliness scheduling, and a fixed-clock policy may occupy its entire useful frontier. The ACM DPShaping full text was blocked during this round; exact overlap remains unresolved. No real owner has said the threshold event is confidential.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| STALE-ACT proxy in directly readable MCU fixture | Direct execution-time truth read is the honest baseline. | 2026-09-23 |
| Generic traffic camouflage, deadline scheduler or computation-proof guarantee | Direct mechanism neighbors and local prior boundary audits. | 2026-09-23 |

## Open questions

- Who owns a genuinely confidential event, what does the observer see, and what are D, B and the loss of a late notice?
- Does any causal policy improve a defense-aware event-time frontier over fixed clock at matched hard deadline and bytes?
- Can a real workflow justify unavailable direct state observation before reconsidering stale-action research?

## Timeline

- 2026-09-23 - divergence and independent contrarian validation; two cheap hypotheses reduced to one conditional kill test and one killed claim.
