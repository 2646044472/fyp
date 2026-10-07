# Round-30 PALM-UPDATE Reconciliation (2026-09-24)

## Decision

`PALM-UPDATE` is **KILL as a positive online template-update or secure adaptive-enrollment method**. Palm-specific template selection/update and generic unsupervised-update poisoning already occupy the mechanism family. Retain only `PALM-UPDATE-NULL` as a lower-priority extension of `E-BOUND-X` and `GALLERY-CHURN-NULL`.

## Exact surviving question

On a frozen VIS Palm transaction path, can current score, margin and quality evidence distinguish a beneficial cross-session template update from a false-accept or abnormal-capture update that will cause later identity drift? Compare:

- never-update;
- fixed multi-template;
- quality-gated update;
- human-confirmed update; and
- periodic re-enrollment.

The endpoint must include template lineage/version, future-session recognition, unknown/wrong identity, mock action and time. No automatic update is presumed safe.

## Hard gates

Require the frozen all-start trace, three disjoint visits, independent owner/unknown labels, explicit template versioning and consent/retention approval. Without these, close the candidate. A large number of frames or repeated same-session captures cannot replace independent visits and identities.

## Project ordering

`PALM-UPDATE-NULL` is lower priority than the Phase 1 VIS trace, `PALM-STOP-NULL` and `E-BOUND-X`. It must not trigger new hardware, a new matcher or a new dataset purchase. If performed, report it as a bounded poisoning/identifiability audit, not as a new update algorithm.

## Evidence boundary

The direct validation audit is `research/ops/validation/2026-09-24-palm-update-validation.md`. It records Palm template-update neighbors, unsupervised-update error propagation, poisoning, controls, feasibility and unresolved source gaps.

## Decision

PIVOT
