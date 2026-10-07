# Round-25 Targeted Reconciliation (2026-09-24)

## Decision

The targeted divergence and validation packets agree: no new method thesis is promoted. The strongest residual is `E-BOUND`, but only as a three-stage longitudinal enrollment-to-transaction evaluation. `PA-CHARGE` remains a bounded physical-to-action risk audit, not a new PAD method. `NOIR-SIDEINFO` and `PROG-RET` are finite communication/control benchmarks and should not displace the Palm MVP.

## Candidate disposition

| Candidate | Status | Exact surviving question | Kill condition |
| --- | --- | --- | --- |
| `E-BOUND` | HOLD/PIVOT | At equal enrollment minutes, revisit burden, template/search cost and original eligible-person coverage, does charged confirmation or cross-visit selection change later untouched full-transaction outcomes? | Best-quality, fixed multi-template or conservative refusal matches/dominates; selection bias; no third untouched visit; insufficient repeat participants. |
| `PA-CHARGE` | HOLD/PIVOT | Do physical print/display presentations that reach live ROI, open-set 1:N and mock action change an attack/bona-fide/time/resource frontier beyond no-PAD, quality rejection and fixed recapture/two-shot controls? | PAI fails before the claimed endpoint; fixed VIS controls match; no lawful attack/participant/lineage protocol; no independent stage denominators. |
| `NOIR-SIDEINFO` | PIVOT | Does a physically paired NoIR observation reduce total end-to-end communication cost beyond RGB ROI JPEG and code-only controls at fixed exact-code false-retain? | NoIR capture/registration/transfer overhead dominates, or the second VIS capture is equally informative. |
| `PROG-RET` | PIVOT | Can a calibration-frozen stopping rule lower expected bytes/latency at a fixed false-retain ceiling without using payload truth or test-set confidence? | Standard progressive JPEG, fixed high-quality JPEG, code-only or two-quality controls dominate; oracle leakage. |
| `OFFSYNC-RET` | NEGATIVE CONTROL | Can two hidden suffix/action worlds produce identical received prefixes but require opposite actions? | A witness makes the worlds distinguishable; retain as a bounded identifiability result. |

## Required design for the leading gate

`E-BOUND` must use one frozen matcher, gallery and threshold across six arms: best-quality single frame, random frame, same-session consistency, fixed diverse templates, fixed two-session enrollment, and conservative refusal. The outcome must include every originally eligible person at a third untouched visit, including failure-to-enroll, later correct completion, unknown, wrong identity, mock debit and time. An improvement among successfully enrolled users is insufficient.

This is an evaluation protocol, not an enrollment algorithm. It cannot be promoted before consent, repeat-visit access, storage/deletion rules, and a minimum person/session plan are confirmed. The Pi Phase 1 transaction trace remains the prerequisite.

### 2026-09-24 enrollment-path readiness correction

[E] `PalmPaymentApp.enroll()` currently calls `CameraFeed.frame()` repeatedly in a tight list comprehension (five times by default). `CameraFeed.frame()` copies the latest frame without waiting for a new frame ID, and `PalmPaymentWorkflow.enroll_user()` stores the resulting features with only a sample count. Consequently, five stored templates are **not evidence of five distinct presentations**; the same frame may be copied repeatedly, and sample/frame/session lineage is unavailable. This does not prove that any particular enrollment already contains duplicates. Before an `E-BOUND` pilot, demonstrate distinct source-frame IDs and independently prompted physical presentations, record their timestamps/session IDs and failures, and keep the third visit untouched. This is an engineering/measurement gate, not an enrollment research contribution.

## Project decision

Continue the Palm Payment MVP first: frozen VIS configuration, live ROI, identifier-free open-set 1:N, unknown handling, idempotent simulated debit, and all-start stage logging. Do not purchase NoIR/IR, a link apparatus, or attack materials for a thesis claim before the MVP trace and ethics/feasibility gates pass.

## Evidence boundary

The complete source chains, exact URLs, versions, sections/pages, queries and uncertainties are recorded in:

- `research/ops/divergence/2026-09-24-targeted-enrollment-action-progressive.md`
- `research/ops/validation/2026-09-24-targeted-e-bound-pa-charge-noir-prog-ret-audit.md`

Their absence of an exact paper is a bounded retrieval gap, not a novelty claim.

## Decision

PIVOT
