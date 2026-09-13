---
topic: transfer-release-evidence-boundary
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - c3-transfer-boundary
  - outside-family-edge-decision-boundaries
sources:
  - url: https://onlinelibrary.wiley.com/doi/epdf/10.1002/asmb.2912
    fetched: 2026-08-31
  - url: https://doi.org/10.1002/asmb.2863
    fetched: 2026-08-31
---

# Transfer release evidence boundary

## Summary

This round formalized the user's question: whether a method tuned on one device/load/fault setting retains its decision value on a new one. The only initially plausible answer, TRC-X, is superseded as a thesis. Reliability demonstration and acceptance sampling already provide release/reject/no-decision plans, consumer risk and unit heterogeneity. Cheap finite bench hardware cannot identify a broad future-device guarantee; finite-matrix enumeration is still useful characterization but not a new edge mechanism.

## Findings

### TRC-X is KILL [KILL]

For a future sampled device population, device units rather than repeated load/fault trials are the independent sampling unit. Under the optimistic i.i.d. device model and zero failures, the 95% one-sided upper failure limit is `1 - 0.05^(1/m)`: 0.527 for four and 0.393 for six devices. A target limit of 0.20/0.10 needs at least 14/29 independent zero-failure devices. Repeated cells cannot replace them without an unvalidated model of unit/cell dependence.

For a finite purchased-board matrix, pre-registered full-factorial testing directly reports observed cells. It cannot make a claim about an unobserved replacement device. The `release / do-not-release / trial-only` action is existing accept/reject/no-decision terminology, and seeded fault tests establish only their seeded distribution.

### Other transfer candidates [KILL]

Cross-machine fault diagnosis and low-cost sensor calibration/recalibration are direct literature families. A trace-only transfer guarantee is the known unlabeled target-risk identification boundary; fault-injection transfer remains an honest negative control, not a guarantee.

## Insights

- “Tested many conditions” is not equivalent to “tested many device units.”
- A published model assumption can make an acceptance calculation valid conditionally; it cannot be inferred from a convenience purchase of a few boards.
- The right negative result for a small bench is evidence sufficiency: state what the matrix establishes and what it cannot support.

## Strongest objection

The specific policy/record story does not change the statistical release decision. Existing acceptance sampling gives the same actions and cost/risk vocabulary, while the proposed hardware scale cannot validate the population assumptions needed for a transfer claim.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| TRC-X crossed-cell release certificate | Standard reliability demonstration; inadequate independent device count | 2026-08-31 |
| MFD-Release cross-machine fault gate | Direct diagnosis literature | 2026-08-31 |
| MQ-Guard sensor-transfer guard band | Calibration/recalibration family | 2026-08-31 |
| UOD/FIP transfer boundaries | Useful screens/appendices but known or non-generalizable | 2026-08-31 |

## Open questions

- Future projects may use a real manufacturer sampling frame and a specified parametric population model. That is outside the present low-cost FYP scope and still needs an exact-neighbor audit.

## Timeline

- 2026-08-31 - divergence generated transfer-decision candidates.
- 2026-08-31 - validation killed TRC-X after acceptance-sampling and device-level identifiability audits.
