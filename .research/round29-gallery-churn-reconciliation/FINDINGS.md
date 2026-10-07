---
topic: round29-gallery-churn-reconciliation
created: 2026-09-24
last_verified: 2026-09-24
status: active
depth: deep
related: [round27-palm-only-reconciliation, palm-transaction-research-gate]
sources:
  - url: https://arxiv.org/html/2401.08111v1
    fetched: 2026-09-24
  - url: https://arxiv.org/html/2606.08437v2
    fetched: 2026-09-24
  - url: https://doi.org/10.1109/ACCESS.2019.2945064
    fetched: 2026-09-24
---

# Round 29 GALLERY-CHURN Reconciliation

## Summary

Dynamic Palm gallery composition is not a new method direction. Dynamic thresholds, gallery admission, recalibration and matcher changes reduce to prior `G-ADMIT` and known open-set/gallery-size/template-aging effects. The only remaining value is `GALLERY-CHURN-NULL`: a synthetic, person/time-blocked benchmark of whether fixed-gallery measurements transfer to add/remove/update gallery states.

## Findings

Use a frozen matcher and threshold. Replay predeclared gallery add/remove/update states and compare fixed threshold, gallery-size strata, max-score order-statistics, recalibration and refusal. Preserve identity/session blocks and distinguish synthetic replay from real account lifecycle. Without lawful lifecycle labels or terminal action outcomes, no live Palm Payment claim is supported.

## Insights

- Gallery growth can be a useful stress axis, but changing the gallery does not create a new recognition algorithm.
- The strongest result would be a bounded transfer failure or null, not a new dynamic threshold policy.
- This benchmark is lower priority than the physical all-start trace and continuous-stop audit.

## Strongest objection

The effect may be predicted entirely by gallery size and max-score order statistics; then the benchmark is a routine characterization and should be an appendix.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| Dynamic gallery admission/threshold policy | Repeats G-ADMIT and standard open-set calibration. | 2026-09-24 |
| New matcher for gallery churn | Matcher substitution is outside the established research boundary. | 2026-09-24 |

## Open questions

- Do the available Palm datasets support lawful person/time-blocked synthetic replay?
- Does gallery size alone explain rank/margin/unknown changes?
- Can any action endpoint be measured without inventing lifecycle labels?

## Timeline

- 2026-09-24 - GALLERY-CHURN audit completed; positive method killed; synthetic null benchmark retained at low priority.
