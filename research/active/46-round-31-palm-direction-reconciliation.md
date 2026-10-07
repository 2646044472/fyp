# Round-31 Palm Direction Reconciliation (2026-09-27)

## Decision

The 2026-09-27 divergence and validation packets agree: **no new Palm direction is promoted**. Preserve the 2026-09-24 ordering, updated by the user's confirmation below. `E-BOUND-X` is now the next conditional evaluation to prepare; `OPEN-ACTION-EP` / `STAGE-NULL` remain the fallback if the longitudinal protocol cannot be executed or the full-path trace does not support its estimand. `VIS-GUIDE` remains a narrow physical comparison. `NIR-MISS-X` is kill-leaning and `PA-FULLPATH` remains behind the apparatus and ethics gate.

## User feasibility update (2026-09-27)

- [K] The user confirmed that three separate Palm visits can be arranged.
- [GAP] This confirms expected scheduling access only. It does not establish completed institutional approval, written consent, a return-participant count, independently presented/fresh frame provenance, or a frozen transaction path. Keep these as entry gates and do not describe the study as approved or already collected.
- Decision effect: retain `E-BOUND-X` as the primary conditional research gate rather than selecting `OPEN-ACTION-EP` solely because three visits might be unavailable. The next design work should define the third untouched visit, person-level denominator, template arms, and trace fields before any study data are used.

## What changed this round

- [K] Palm-ID already combines mobile capture, ROI, quality-based rejection/recapture, open-set identification, and time-separated evaluation. This makes capture guidance, generic quality retry, ROI, open-set, and generic mobile deployment weak or occupied contributions. It does not evaluate this project's mock action or its three-stage enrollment question.
- [K] X-Palm v2 (2026-06-22) provides paired multispectral-scanner and smartphone palm identities and cross-domain/open-set protocols. It strengthens the direct-neighbor case against a broad VIS/NIR-to-mobile claim. Its terms, temporal structure for a three-visit stability estimand, and payment-action relevance remain unresolved or distinct.
- [K] GBU-Palm v1 (2026-08-14) directly benchmarks physical print/replay PAD with RGB/NIR video, held-out identity/attack lineage, and environment conditions. It reports that RGB-NIR fusion does not consistently beat RGB-only. This further closes generic Palm RGB/NIR PAD or fusion claims; a local mock-action trace would remain an apparatus-specific audit only.
- [E] The current checkout has latest-frame IDs/timestamps, but the payment enrollment UI still calls `frame()` repeatedly without waiting for a new presentation and the stored template metadata records a sample count rather than per-template frame/visit lineage. Checkout gets the image and its shared capture context in separate calls, so the image-context binding is not atomic under concurrent requests. This is a measurement/readiness gap, not a thesis contribution.
- [E] The inspected local JSONL artifact contains five events and lacks frame ID, visit ID, ROI status, and terminal transaction result fields. It is not an all-start study. Local PalmBigDataBase and CASIA archives are present, but their reuse terms are unresolved and neither archive supplies the live app's terminal action endpoint.

## Candidate disposition

| Candidate | Current status | Decision-changing prerequisite |
| --- | --- | --- |
| `E-BOUND-X` | HOLD/PIVOT; longitudinal evaluation only | Approved consent and retention; three disjoint visits; distinct presented frames with atomic image/frame/time/session provenance; original eligible denominator; frozen matcher/gallery/threshold; untouched third-visit action outcome. |
| `OPEN-ACTION-EP` | PIVOT; linked episode audit | Frozen physical VIS path, all-start trace, independent owner/unknown authorization labels, and terminal mock action linked to the same episode. |
| `STAGE-NULL` | Negative control only | Use only to state the dependence/reachability boundary for marginal metrics; a stand-alone two-world example adds little without the actual episode trace. |
| `VIS-GUIDE` | HOLD/PIVOT; apparatus-specific comparison | Stable executable and baseline first; then prospective, counterbalanced prompt vs fixed retake/quality-marginal control. |
| `NIR-MISS-X` | HOLD, kill-leaning | Paired physical capture capability, missingness assignment, cross-session identity endpoint, VIS-only and fixed second-VIS controls at matched cost. |
| `PA-FULLPATH` | PIVOT behind ethics and apparatus gates | Authorized physical attacks that reach the live capture/ROI/matcher path, separate stage denominators, and no-PAD/quality-reject/fixed-recapture controls. |

## Coordinator assessment

There is no substantive conflict between the packets. Divergence keeps `E-BOUND-X` first only if the three-visit protocol is feasible; validation agrees on the ranking while emphasizing that its remaining distinction is a protocol/action endpoint, not a method novelty claim. Validation provides the strongest kill map for `VIS-GUIDE`, generic RGB/NIR fusion/PAD, and any attempt to infer rare wrong-action safety from a small cohort. Both packets treat the absence of an exact local mock-payment paper as a bounded search result, not novelty evidence.

The workspace already contains extensive user-owned edits; this coordinator reconciliation records the gate and does not rewrite those changes. The next useful research artifact is not another algorithm proposal. It is a frozen, authorized VIS all-start trace with atomic frame-to-episode linkage and independent identity/action labels, followed by a three-visit protocol whose visit 3 is untouched. The user confirmed visits can be arranged; if approval, consent, lineage, return-person count, or trace prerequisites fail, use the linked `OPEN-ACTION-EP` / `STAGE-NULL` audit and do not claim an enrollment contribution.

## Evidence boundary

- Divergence: `research/ops/divergence/2026-09-27-palm-only-direction-recheck.md`.
- Validation: `research/ops/validation/2026-09-27-palm-candidate-gates-validation.md`.
- Palm-ID: Grosz et al., arXiv:2401.08111v1, https://arxiv.org/abs/2401.08111; reviewed sections and tables are documented in both packets.
- X-Palm: Seyedmohammadi et al., arXiv:2606.08437v2, https://arxiv.org/abs/2606.08437; protocol and limitation sections are documented in the divergence packet.
- GBU-Palm: Ma et al., arXiv:2608.14389v1, https://arxiv.org/abs/2608.14389; dataset, held-out protocol, and spectral/temporal analyses are documented in both packets.
- Current implementation and log inspection: `code/palm_demo/camera.py`, `palm_payment_ui.py`, `workflow.py`, and the inspected 2026-08-31 JSONL summary. No runtime experiment or participant result is inferred.

## Decision

PIVOT
