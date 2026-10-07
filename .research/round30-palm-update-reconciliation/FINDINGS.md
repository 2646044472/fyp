---
topic: round30-palm-update-reconciliation
created: 2026-09-24
last_verified: 2026-09-24
status: active
depth: deep
related: [round27-palm-only-reconciliation, round29-gallery-churn-reconciliation, palm-transaction-research-gate]
sources:
  - url: https://doi.org/10.1007/978-3-319-69923-3_27
    fetched: 2026-09-24
  - url: https://doi.org/10.1109/ACCESS.2019.2945064
    fetched: 2026-09-24
  - url: https://doi.org/10.1109/EuroSP48549.2020.00020
    fetched: 2026-09-24
  - url: https://doi.org/10.1016/j.patrec.2013.05.021
    fetched: 2026-09-24
---

# Round 30 PALM-UPDATE Reconciliation

## Summary

Positive online Palm template update is killed as a thesis mechanism. Palm-specific template selection/update and generic unsupervised-update poisoning occupy the family. The only remaining value is `PALM-UPDATE-NULL`: a bounded audit of whether local score/quality evidence can distinguish beneficial cross-session updates from false-accept-driven identity drift.

## Findings

Compare never-update, fixed multi-template, quality-gated, human-confirmed and periodic re-enrollment under a frozen matcher and explicit template lineage. The outcome must include later sessions, unknown/wrong identity, mock action and version history. Without independent visits and labels, update safety is not identifiable from the local match alone.

## Insights

- Template update is not a new Palm direction merely because it runs on a Pi or uses a Palm matcher.
- The useful Palm-specific boundary is whether a live open-set transaction exposes an update-versus-poisoning tradeoff that offline recognition metrics hide.
- This is an extension of longitudinal enrollment and gallery churn, not a separate method candidate.

## Strongest objection

The proposed audit may simply reproduce standard template aging/update evaluation and poisoning demonstrations. If no independent future-session labels exist, it should be closed rather than expanded.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| New online Palm update algorithm | Palm-specific update and generic adaptive-template methods already exist. | 2026-09-24 |
| Unsupervised update as safe by default | False-accept feedback can poison later templates; no local score-only certificate establishes safety. | 2026-09-24 |

## Open questions

- Can the system retain immutable template versions and link updates to later sessions?
- Are independent owner/unknown labels and three visits available?
- Does quality-gated or human-confirmed update add anything beyond fixed multi-template enrollment?

## Timeline

- 2026-09-24 - Palm online-update audit completed; positive method killed; null audit retained as a lower-priority extension.
