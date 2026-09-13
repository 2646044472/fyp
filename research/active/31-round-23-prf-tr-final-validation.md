# Round 23 Reconciliation: PRF-TR Final Validation Gate

## Decision investigated

Whether `PRF-TR` can be retained as the project's one-year undergraduate FYP
direction after the independent divergence and validation audits.

## Evidence checked

- [PRF-TR three-story divergence](../ops/divergence/2026-09-03-prf-tr-three-stories-divergence.md)
- [Finite action-rank validation](../ops/validation/2026-09-03-finite-action-rank-study-validation.md)
- [Round-22 reconciliation](30-round-22-prf-tr-reconciliation.md)
- [Cross-device action-rank pilot](11-cross-device-action-rank-pilot.md)
- [Pilot execution gates](12-pilot-execution-gates.md)

## Final research identity

`PRF-TR` is retained as **PIVOT (Amber)** with the following paper identity:

> **A finite physical-versus-digital action-rank audit for edge visual
> inspection:** do brightness, blur, masking, noise, and frame-loss tests
> preserve the ordering of `retain`, `reacquire`, and `unknown` actions when
> the same printed marker is exposed to real low-light, glare, cover, and
> optical-path conditions on a Raspberry Pi Camera NoIR v2 setup?

The story is a release engineer preparing a field-maintenance camera pipeline.
Digital corruption tests are cheap, while physical fault testing is costly.
If the tests rank capture policies incorrectly, the deployed edge device may
retain a bad inspection record or waste time on unnecessary reacquisition.
This story is a motivating decision, not evidence of a currently authorised
field deployment. Until such access exists, describe the study as a finite
bench evaluation.

## What survives the audit

- The target is an action-risk ranking, not decoder accuracy alone.
- The physical labels are assigned by the fixture before policy evaluation.
- The exact printed payload is generated and stored before capture; the policy
  cannot use the independent oracle result.
- Digital and physical conditions are compared at the same declared action
  semantics, with real capture, decode, latency, storage and energy costs
  charged where applicable.
- Source-cell thresholds are frozen before blocked physical sessions, material
  lots, lamp conditions, remounts, or camera paths are scored.
- Rank preservation, rank inversion, and non-identifiability are all valid
  outcomes.

## What is killed

Do not claim a new decoder, adaptive camera controller, conformal abstention
wrapper, camera-health certificate, network protocol, synthetic-to-real
theorem, camera-family guarantee, maintenance-completion proof, or security
property. `DEPLOY-GATE` is an engineering acceptance artifact unless its
physical evidence changes a separately defined scientific endpoint.

## Minimum experiment

Use one static printed marker family and at least four preassigned cells:
clean/high-light, clean/low-light, transparent-cover/glare, and one held-out
lamp, cover lot, remount, or optical path. Run fixed NoIR-visible,
fixed NoIR+IR and fixed visible-then-IR only if a fixed IR illuminator is
actually included, plus scalar brightness/blur/decoder-confidence, random
action, and always-review controls. Repeat by session, not by treating frames
from one fixture as independent devices.

Primary output is the source-to-held-out action-rank relation under a frozen
loss. Secondary outputs are false retain, exact-code success, unknown rate,
reacquisition count, wall time, bytes, and joules. The strongest kill test is
that fixed two-shot, scalar quality, or always-review is Pareto-optimal.

## Gate decision

The direction may be promoted from Amber only if a repeatable held-out rank
inversion survives the fixed controls and independent-label checks, or if the
advisor explicitly approves a sufficiently rich negative-result thesis. If
neither occurs, retain the dataset/protocol as a bounded null and do not spend
time on model search.

## Feasibility and next action

The confirmed Pi and Camera NoIR v2 are sufficient for the first static pilot.
An IR illuminator is optional; a second camera is not required. The workspace
currently contains no physical capture data, acquisition log, or power log.
The next action is hardware bring-up and the fixed baseline matrix. No
additional camera, larger model, or biometric data is justified before that
gate.

## Status

**PIVOT (Amber).** This is the only current candidate, but it is not yet a
locked thesis. Its contribution is an auditable finite evaluation or negative
result, not a new algorithm.
