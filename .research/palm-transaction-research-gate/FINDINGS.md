---
topic: palm-transaction-research-gate
created: 2026-09-23
last_verified: 2026-09-23
status: active
depth: deep
related: [edge-palm-baselines, palm-roi-following-pipeline, physical-failure-synthetic-transfer-boundary]
sources:
  - url: https://arxiv.org/html/2401.08111
    fetched: 2026-09-23
  - url: https://arxiv.org/html/2608.14389
    fetched: 2026-09-23
  - url: https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf
    fetched: 2026-09-23
  - url: https://doi.org/10.1109/BTAS.2015.7358797
    fetched: 2026-09-23
  - url: https://doi.org/10.1109/WIFS.2009.5386482
    fetched: 2026-09-23
---

# Palm Transaction Research Gate

## Summary

The 2026-09-13 user-confirmed meeting note establishes one staged Pi 5 Palm Payment FYP: VIS live capture-to-simulated debit first, then gated NIR and physical attack/PAD research. This overrides the older PRF-TR default route. No paper claim is locked. The cheapest post-demo question is T-RETRY: can an attempt-history decision improve open-set wrong-debit/completion/p95-time at matched cost beyond fixed retry, quality/margin and conservative refusal? It is HOLD pending consented full-path Pi evidence, independent participants and a feasible error count.

**2026-09-23 correction:** The `minutes_note.md/9-22.md` apparent same-hand rejection (`FR 66`) has no numerator/denominator or frozen condition and cannot be cited as measured FRR. Murakami/Takahashi WIFS 2009 already covers sequential open-set accept/reject/continue, and rare wrong-debit differences require an unknown-person count not established locally. KILL T-RETRY's positive rare wrong-debit policy claim as specified; PIVOT only to stagewise VIS failure localization and, conditionally, a randomized guidance-versus-fixed-retake completion/time question. See `research/active/36-palm-failure-localization-gate.md` and the 2026-09-23 no-count audit.

**Residual-direction correction:** G-ADMIT is now KILL as an offline novel calibration method after direct gallery-relative scoring, per-gallery threshold and open-set audits. VIS-GUIDE is the only remaining Palm-side research lead, and only as a local prospective completion/time evaluation after the payment/debug ROI-path split is resolved. Current gate: `research/active/37-palm-residual-direction-gate.md`.

The residual is weaker than previously stated: an official 2015 mobile palmprint record describes a guided capture window/hand localization workflow (https://yonsei.elsevierpure.com/en/publications/an-empirical-study-of-palmprint-recognition-for-mobile-phones/). Full text/pages were not obtained, so this is a collision lead rather than complete exact-claim clearance. Treat VIS-GUIDE as evaluation-only pending the actual payment trace.

## Findings

| Candidate | Direct collision | Residual and gate |
| --- | --- | --- |
| T-RETRY | Palm-ID has mobile open-set 1:N and quality rejection; Czajka/Bowyer 2015 studies dependent three-attempt biometric transactions; NIST covers guided recapture. | Only prospective, frozen, held-out action-and-cost frontier on full physical Pi transactions could differ. Fixed controls or too few independent wrong debits kill the positive claim. |
| E-BOUND | NIST quality enrollment and long-term palm template selection occupy components. | A charged confirmation/refusal decision needs three separate visit stages and unknown-person transactions. Not currently feasible by assumption. |
| PA-CHARGE | GBU-Palm physically captures print/replay RGB/NIR palm PAD with lineage/environment splits. | Only a bounded full presentation-to-mock-debit risk/cost endpoint remains, after MVP, physical authorization and held-out lineages. |

Local `python -m pytest -p no:cacheprovider -q` on 2026-09-23 returned 46 passed, but did not exercise a live Pi full 1:N transaction, physical attack, NIR vessel observation or consent. Dataset manifest explicitly leaves archive use rights unresolved. Older research/active PRF-TR pages remain historical alternatives, not user-selected Palm Payment thesis.

The instrumentation gate advanced on 2026-09-23: `CameraFeed` now emits a monotonic frame ID/context and checkout events include capture context, ROI status/reason/quality, identification status/second score and stage timings. The same test command now returns 47 passed from `code/palm_demo`. This proves only software trace behavior; it does not prove the Pi path or resolve `FR 66`.

## Insights

The action endpoint matters only if it changes a decision relative to existing biometric acquisition and PAD controls; reporting additional metrics is not itself a CS mechanism. Unknown bona-fide people and physical PAIs are different populations. A small pilot can measure acquisition and latency but cannot support rare-event security claims; zero errors over n independent trials only gives a rough 95% upper bound near 3/n.

## Strongest objection

The strongest fixed guided retry or quality/margin rejection can match the entire useful transaction frontier. Even if it does not, a small number of independent people/unknowns may leave uncertainty too wide to distinguish policies. The closest palm/face sequential-decision and advisor-paper full-text chain remains incomplete.

The sequential decision formulation itself is also an exact-claim collision with Murakami/Takahashi WIFS 2009 (Secs. 2-4, DOI https://doi.org/10.1109/WIFS.2009.5386482). A novel policy cannot be inferred from reusing it on a Pi. Public ROI-only images lack local physical prompt counterfactuals.

## Discarded approaches

| Approach | Why dropped | Date |
| --- | --- | --- |
| Pi deployment, simple quality retry, generic RGB/NIR PAD/fusion | Direct component neighbors already cover these; different hardware is not an exact CS contribution. | 2026-09-23 |
| PRF-TR as default user route | Superseded by the 2026-09-13 confirmed Palm Payment roadmap; retain only as an alternative. | 2026-09-23 |
| T-RETRY rare wrong-debit superiority as the first thesis claim | No independent unknown-person count, direct sequential-biometrics collision and unverified failure stages. | 2026-09-23 |

## Open questions

- Can the user obtain ethics/consent approval and enough independent enrolled/unknown participants and sessions for a meaningful frontier comparison?
- Will a live Pi Phase 1 transaction produce measurable retry and unknown-match outcomes with a frozen threshold?
- Does a direct palm/face sequential-decision or advisor paper already occupy the proposed exact action-cost endpoint?

## Timeline

- 2026-09-23 - divergence and two validation packets reconciled; Palm Payment restored as current route and T-RETRY identified only as first cheap kill gate. Protocol is `research/active/35-palm-transaction-research-gate.md`.
- 2026-09-23 - corrected after 9-22 note and independent no-count validation; positive rare-debit policy KILL, failure-localization/guidance PIVOT. `research/active/36-palm-failure-localization-gate.md` is current.
- 2026-09-23 - residual audit killed G-ADMIT and reduced VIS-GUIDE to a conditional payment-path evaluation; current gate is `research/active/37-palm-residual-direction-gate.md`.
