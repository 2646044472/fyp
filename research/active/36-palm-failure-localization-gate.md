# Palm VIS Failure Localization Gate (2026-09-23)

## Decision investigated

The user-confirmed Pi 5 Palm Payment route remains in force. The five-line `minutes_note.md/9-22.md` says IR/camera assembled, deep-learning ROI, `same hand FR 66 FA low`, and proposes background/box and camera changes. [GAP] No raw count, denominator, threshold, identity/session roster, modality, optical settings or transaction outcomes accompany it. Do not report a 66% FRR, low FAR, NIR vessel observation, or an experimentally established cause.

Independent divergence (`research/ops/divergence/2026-09-23-palm-dataset-feasibility-boundaries.md`) and validation (`research/ops/validation/2026-09-23-t-retry-no-count-feasibility-audit.md`) agree that the immediate action is a small authorized stagewise VIS preflight, not policy fitting. The former treats this as engineering diagnosis; the latter kills T-RETRY's rare wrong-debit superiority as presently specified.

## Stagewise estimands and record

One eligible, consented physical presentation starts one episode, even if no frame or ROI is produced. Let C be a captured frame, R a valid ROI tied to that frame, M the correct roster identity within a *frozen* thresholded 1:N gallery, and A the correct terminal mock transaction action. Report counts and person/session-clustered uncertainty for `P(C)`, `P(R|C)`, `P(M|C,R)`, `P(A|C,R,M)` and end-to-end `P(C,R,M,A)` over **all eligible starts**. Record capture failure, ROI no-hand/quality/stale-frame reason, top/second scores and margin, threshold, unknown/retry, wrong-identity/correct mock debit, enrollment provenance, camera/profile/IR state, exposure/gain/AWB, background/box, session and stage times. No actual payment or unapproved biometric collection.

For each incident, distinguish `failure to capture`, `failure to acquire ROI`, `same-hand score/threshold rejection`, `wrong gallery match` and `UI/payment action failure`. `FR 66` cannot be mapped to one of these without the original count. Preserve consent and data-minimization/deletion policy; a note or existing local sample is not ethics approval.

## Minimum intervention and kill sequence

1. Reproduce the note on a frozen VIS camera/ROI/matcher/gallery/threshold with a consented, independently rostered small pilot. Retain every start, not only accepted crops. Check the same-source frame/ROI transaction invariant. Report numerator and denominator by person/session, not a pooled video-frame rate.
2. On development presentations, vary **one factor at a time**: declared background/box while camera and exposure are logged; then camera only after a new baseline and separate enrollment. Counterbalance order. Do not call a camera swap a sensor effect while ROI, pose, illumination and gallery also change. Never use held-out people to tune threshold or pick a preferred condition.
3. Compare frozen fixed-guide/fixed exposure, existing dynamic ROI, fixed quality-and-margin rejection, and one guided VIS retake. If a simple acquisition/ROI correction removes most failure, it kills a history-dependent policy story. If there is no repeatable stage-specific effect beyond controls, record a bounded null.
4. Only after an authorized full VIS live capture-to-identifier-free 1:N-to-idempotent mock-debit MVP is stable, estimate whether a prospective, counterbalanced guidance intervention changes enrolled completion and p95 transaction time against the strongest fixed quality/margin retake at matched captures. Unknown-person wrong debits are separately counted with person-level intervals, **not** claimed reduced without adequate informative paired errors.

## Feasibility and thesis status

[K] Murakami and Takahashi, WIFS 2009, DOI https://doi.org/10.1109/WIFS.2009.5386482 (author text Secs. 2-4), already models sequential open-set biometric accept/reject/continue. Palm-ID, arXiv:2401.08111v1 (Secs. II-F/G, III-C/D, IV-A/B), already studies mobile palm quality recapture and open-set 1:N. The residual guidance comparison is an apparatus-specific causal acquisition question, not a generic sequential decision method. Its exact palm/face neighbor and advisor-paper chains remain [GAP].

[C] Zero wrong debits in n independent unknown-person episodes has one-sided 95% binomial upper bound `1 - 0.05^(1/n)` (about `3/n`), under independent Bernoulli assumptions. Repeated frames from the same person are not new unknown people. The validation audit derives illustrative paired differences needing thousands of independent episodes at rare target rates; this is a feasibility screen, not a claim about the local true rate.

`F-ATTR`: HOLD as MVP diagnosis, not a thesis. `T-RETRY` positive rare wrong-debit policy: KILL as presently specified; PIVOT to the narrow prospective guidance completion/time study only if failure localization and permissions make it testable. `G-MATE`: HOLD separately for a lawful person-disjoint dataset calibration audit; IITD, X-Palm and local archives have unresolved use terms and small/compound identity splits, and cropped data never prove live retry or mock-debit safety. `E-BOUND` requires three distinct visits; `PA-CHARGE` requires later physical-attack and ethics gates. No thesis locked.

## Sources and search boundary

The new packets record queries, exact paper sections and official dataset access terms: `research/ops/divergence/2026-09-23-palm-dataset-feasibility-boundaries.md` and `research/ops/validation/2026-09-23-t-retry-no-count-feasibility-audit.md`. Local implementation has 46 passing software tests (2026-09-23), but no documented 9-22 raw experiment log or authorized live Pi open-set transaction score; do not promote this gate on unit-test evidence. The first decision-changing artifact is a consented stage-count table with frozen settings and independent identity/session labels.

PIVOT
