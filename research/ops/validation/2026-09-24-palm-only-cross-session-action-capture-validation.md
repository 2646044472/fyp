# Validation Audit: 2026-09-24 Palm-only Cross-session, Action, Capture, Missing-modality, and Full-path PAD Claims

## Decision investigated

Adversarial audit of E-BOUND-X, OPEN-ACTION-EP, VIS-GUIDE, NIR-MISS-X, and PA-FULLPATH from research/ops/divergence/2026-09-24-palm-only-cross-session-action-capture.md. The scope is Palm-only recognition. Pi, latency, energy, and simulated debit are evaluation conditions, not contributions. Only this file is written; research/active/, research/archive/, and .research/ are untouched.

## Claim under test

- E-BOUND-X: equal-cost charged second pose/visit changes a third untouched transaction outcome beyond best-quality, same-session, diverse-template, and refusal controls, counting every originally eligible person.
- OPEN-ACTION-EP: participant-linked episodes expose terminal wrong/correct action, unknown, and time beyond marginal matcher rates.
- VIS-GUIDE: one prospective physical prompt changes all-start completion or capture-to-action time beyond fixed prompt, recapture, and unknown controls.
- NIR-MISS-X: a VIS fallback when NIR is unavailable beats VIS-only and fixed second-VIS capture across sessions at equal cost.
- PA-FULLPATH: a physical presentation can be evaluated through capture, ROI, PAD, 1:N, and mock action.

These are not claims for a new CNN, cropper, threshold, gallery calibration rule, or generic modality selector. A local apparatus endpoint supports only a bounded evaluation or negative identifiability study.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component: E-BOUND-X | [KILL] NIST IR 7544 covers quality, failure-to-enroll, recapture and optimistic same-session evaluation. Chen et al. cover long-term representative palmprint/palm-vein template selection/update. Palm-ID combines mobile capture, ROI, quality rejection/recapture, enrollment and open-set 1:N. | Charged confirmation, refusal accounting, a later untouched visit and original-eligibility accounting are protocol choices, not a new enrollment mechanism. | High method; medium exact protocol. |
| Exact/boundary: E-BOUND-X | [KILL-leaning] Best-frame selection, multi-template enrollment, quality rejection and longitudinal representation are the functional core. A Pi account simulator adds no mechanism. A confirmation visit used as the test visit contaminates selection; successful-enrollee-only analysis rewards refusal; marginal rates do not identify joint action risk. | [GAP] A finite audit may remain if visits are disjoint, account binding is external, original denominators are retained, and template/search cost is matched. | High kill; medium-low residual. |
| Component: OPEN-ACTION-EP | [KILL] Sequential accept/reject/continue decisions, transaction metrics, quality/recapture and stage reporting are established. | Participant-linked episodes may support a negative result about marginal stage rates versus terminal action. | High method; medium negative boundary. |
| Exact/boundary: OPEN-ACTION-EP | [KILL-leaning] Replacing offline false accept with mock debit is an endpoint relabel unless action policy and sampling frame change. FAR/FRR/FNIR/FPIR/FTE/FTX from different denominators cannot be multiplied into wrong-action risk. | [GAP] A direct episode count is identifiable with independent authorization labels, all-start logging and a frozen policy. | High. |
| Component: VIS-GUIDE | [KILL-leaning] Guided mobile palm acquisition, hand localization, ROI, quality rejection and recapture already occupy the mechanism. | The actual payment executable and completion/time endpoint are local apparatus conditions. | High method; medium evaluation. |
| Exact/boundary: VIS-GUIDE | [KILL-leaning] A prompt improving placement or recapture is the same guidance mechanism; mock debit does not make it novel. Unfrozen exposure, ROI, fixture or matcher confounds the effect, and small bona-fide samples cannot establish rare wrong-debit superiority. | A single frozen prompt factor and all-start trace permit a bounded null/effect estimate. | High. |
| Component: NIR-MISS-X | [KILL-leaning] Missing-modality recognition, RGB/NIR fusion, modality dropout, quality fallback and fixed modality selection are established families. | A paired cross-session observation on the exact Pi optical path with terminal action labels is narrower. | High method; medium benchmark. |
| Exact/boundary: NIR-MISS-X | [KILL-leaning] “NIR missing, use VIS” is a fixed fallback; learned completion is ordinary missing-modality fusion. NoIR brightness/crease contrast is not vein evidence, and a second VIS capture may be cheaper/equally informative. | [GAP] A finite test remains only if paired hardware, independent missingness, person-blocked sessions and charged capture/registration/inference/energy exist. | High. |
| Component: PA-FULLPATH | [KILL] ISO/IEC 30107-3 and GBU-Palm-style work occupy PAI instruments, print/display/replay, RGB/NIR PAD, lineage, holdouts and PAD metrics. | A local physical path through the exact Pi ROI/1:N/mock action is a narrower audit opportunity. | High. |
| Exact/boundary: PA-FULLPATH | [KILL-leaning] Adding open-set identity and mock debit changes reporting, not detector mechanism. If a PAI never reaches valid ROI or 1:N, there is no attack-to-action endpoint; cropped ROI injection and digital replay bypass physical capture. | [GAP] A bounded audit needs authorized materials, person/material/device/session holdouts, frozen no-PAD controls and stage denominators. | High. |

## Assumption and identification audit

### E-BOUND-X

The unit is an eligible person, not a frame. Keep enrolled, refused, failed-to-enroll and lost-to-follow-up people in the denominator. Enrollment, optional confirmation and third transaction must be disjoint sessions; the third visit cannot choose the template. Match participant/operator minutes, template count, search work and storage. Externally bind enrollment, revisit, refusal, unknown, correct/wrong identity and mock debit to account truth. Kill if no third untouched visit/original denominator exists, or best-quality/diverse-template/refusal dominates; pivot only to longitudinal reproducibility.

### OPEN-ACTION-EP

Every physical start needs one episode ID linking capture, ROI, matcher/open-set output, policy transition, action and timing. Required classes are bona-fide owner, authorized-but-unknown/failed capture, and unauthorized or mate-absent presentation; scores cannot supply these labels. Test STAGE-NULL: equal marginal stage rates can have different dependence and terminal action risk. Kill if only successful captures/owners are available, or fixed score/margin/quality rules explain the endpoint; retain only a negative identifiability result.

### VIS-GUIDE

Freeze camera, illumination, mount, exposure/white balance, ROI, matcher, threshold, unknown rule, retry count and idempotent action. Counterbalance one prompt factor. Record every physical start, including no-ROI, invalid-ROI, matcher rejection, unknown, correct/wrong identity, action and stage times. Kill if fixed recapture or fixture repair matches, or if the endpoint is only ROI accuracy.

### NIR-MISS-X

First prove the exact camera/illuminator pair, timestamps, registration, illumination and energy behavior. Define missingness by unplugged/disabled/logged failure or predeclared dropout, not outcome quality. Compare VIS-only, fixed paired VIS+NIR, predeclared VIS fallback and fixed second-VIS capture. Kill if pairing fails, NIR adds no information beyond second VIS, or fixed fallback is Pareto-optimal.

### PA-FULLPATH

Authorize attack materials and participants; document storage/deletion. Hold out person, PAI lineage/material, presentation device, session and illumination. Freeze no-PAD, quality/score rejection and fixed recapture. Log presentation, capture, ROI, PAD, 1:N, unknown/correct/wrong identity, action, time and resources. Kill if attacks do not reach the claimed endpoint; do not infer assurance from zero accepts without independent-episode bounds.

## Direct-neighbor table

| Work | Inputs/actions | Target/evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Tabassi & Grother, NIST IR 7544 (2008) | Quality, enrollment, recapture, FTE | Biometric acquisition/evaluation | E-BOUND-X and VIS-GUIDE components | Kills mechanism; local later-transaction protocol remains open |
| Chen et al., IEEE Access 7 (2019), DOI 10.1109/ACCESS.2019.2945064 | Longer-term palmprint/palm-vein samples and representative templates | Long-term template representativeness | E-BOUND-X template/visit mechanism | Kills new template-selection claim; leaves charged refusal accounting |
| Palm-ID, arXiv:2401.08111v1 (2024-01-16) | Mobile capture, ROI, quality rejection/recapture, enrollment, open-set 1:N | Recognition and acquisition failures | VIS-GUIDE, NIR-MISS-X recognition, PA-FULLPATH components | Kills generic ROI/recapture/open-set claim; local endpoint remains open |
| Murakami & Takahashi, WIFS 2009 | Sequential accept/reject/continue | Sequential biometric decisions | OPEN-ACTION-EP retry/continue | Kills generic policy; leaves negative linkage audit |
| Czajka & Bowyer, BTAS 2015 | Repeated biometric attempts | Dependence and later-attempt behavior | E-BOUND-X/VIS-GUIDE independence assumptions | Kills iid assumption; not Palm open-set exact |
| Ma et al., GBU-Palm, arXiv:2608.14389v1 (2026-08-14) | Physical RGB/NIR presentations and lineage splits | Palm PAD robustness | PA-FULLPATH PAI/RGB-NIR/holdout components | Kills generic PAD claim; local action endpoint remains finite |
| ISO/IEC 30107-3:2023 ed. 2 | PAD terminology, attack instruments, reporting | Presentation-attack testing | PA-FULLPATH protocol layer | Kills standards-level novelty; full text not freely accessed |

## Strongest simple baseline

Use a frozen, fully logged VIS pipeline: one best-quality frame or fixed diverse templates, fixed ROI and matcher, fixed score/margin/quality unknown rule, one fixed recapture/two-shot policy, conservative refusal/unknown, idempotent mock debit, and person/session-blocked all-start logging. For E-BOUND-X add fixed best-quality, same-session, diverse-template, second-visit, and refusal arms at equal effort. For NIR-MISS-X the strongest comparator is fixed second VIS. For PA-FULLPATH use no-PAD plus fixed quality/score rejection and fixed recapture. For VIS-GUIDE compare one prompt against the existing fixed prompt and recapture.

If the proposed candidate cannot beat these controls at the same capture opportunities and cost, it is an engineering choice.

## Contrarian result

- E-BOUND-X: KILL as a positive enrollment mechanism; PIVOT to a pre-registered longitudinal evaluation only.
- OPEN-ACTION-EP: KILL as a positive action-risk estimator/policy; PIVOT to STAGE-NULL/action-linkage identifiability.
- VIS-GUIDE: KILL as a generic guidance method; HOLD/PIVOT as a prospective completion/time evaluation only.
- NIR-MISS-X: KILL as a new missing-modality/fusion/selector claim; HOLD/PIVOT only after a capability preflight, currently kill-leaning.
- PA-FULLPATH: KILL as a positive PAD/security claim unless the physical path is demonstrated; PIVOT to a bounded endpoint audit.

No candidate reaches PROMOTE.

## Feasibility audit

E-BOUND-X needs repeat consented visits and a third untouched session. A large frame count cannot replace independent people and sessions. OPEN-ACTION-EP and PA-FULLPATH need authorized mate-absent/unauthorized or PAI episodes; accidental strangers are not a label protocol. Zero wrong actions in a small cohort is a clustered upper bound, not payment security.

The MVP must freeze the exact VIS camera, mount, illumination, ROI path, matcher, threshold, unknown policy and idempotent mock debit. NIR-MISS-X additionally needs paired VIS/NIR timestamps, registration, illumination and energy evidence. PA-FULLPATH needs materials and a setup that demonstrably reaches the target capture path.

Palm images/templates, repeat visits, unauthorized presentations and physical PAI materials require consent, access control, retention/deletion rules and applicable approval. The charter confirms a consented local VIS MVP but does not prove repeat-visit recruitment, unknown-person sampling, attack authorization or NIR approval.

## Highest-information minimum Palm experiment

Before buying hardware or collecting attack data, freeze the current VIS pipeline and run one capability/trace gate:

1. Use one authorized participant set and frozen camera, mount, ROI, matcher, threshold and action configuration.
2. Record every eligible physical start with episode ID and session ID.
3. Log start, valid frame, ROI reachability, matcher identity/score/margin, open-set decision, owner/unknown/unauthorized class where authorized, policy transition, correct/wrong/no action, mock debit and each stage time.
4. Run two separate capture sessions for a subset and test whether a third untouched visit and original-eligible denominator are feasible. Do not use the third visit for enrollment selection.
5. Counterbalance one prompt factor only if the pipeline is stable.
6. Compare direct episode outcomes with product-of-marginals, matcher confidence, fixed quality/margin retake and refusal/unknown controls.
7. Record whether paired NIR and any authorized physical presentation reach valid ROI and 1:N. These are capability gates, not thesis results.

Every outcome is useful: retain a longitudinal protocol if the third visit is feasible; retain STAGE-NULL if marginal summaries fail; reopen VIS-GUIDE only if a prompt can be counterbalanced; kill NIR-MISS-X or PA-FULLPATH when physical prerequisites fail.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Quality, FTE, recapture and same-session caveats are established. | [K] | NIST IR 7544 (2008-11), https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Secs. 2.1.1-2.1.3, PDF pp. 19-22; Sec. 5.1, pp. 37-40 | General guidance, not Palm transaction study. |
| Long-term representative palm templates are established. | [K] | Chen et al., IEEE Access 7 (2019), https://doi.org/10.1109/ACCESS.2019.2945064 | Secs. II-III and IV, pp. 145083-145094 | Not exact charged/refusal protocol. |
| Mobile Palm acquisition, ROI, quality recapture, enrollment and open-set 1:N are established. | [K] | Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111v1 | Secs. II-F/G, III-B/C/D, IV-A/B, V | Local Pi endpoint differs. |
| Sequential open-set accept/reject/continue is established. | [K] | Murakami & Takahashi, WIFS 2009, https://ieeexplore.ieee.org/document/5356597 | Formulation and experiment, pp. 1-4 | Exact page access should be rechecked before final thesis citation. |
| Repeated biometric attempts can be dependent. | [K] | Czajka & Bowyer, BTAS 2015, https://doi.org/10.1109/BTAS.2015.7358797 | Secs. 1-4.3 and 5, pp. 1-6 | Iris/1:1 caution, not exact Palm overlap. |
| Physical RGB/NIR Palm PAI and lineage splits are established. | [K] | Ma et al., GBU-Palm, arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389v1 | Secs. 2-4; Tables 2-6 | Local full-path transfer remains GAP. |
| PAD testing has defined instruments and reporting scope. | [K] | ISO/IEC 30107-3:2023 ed. 2, https://www.iso.org/standard/79520.html | Official scope/abstract | Normative full text not freely accessible. |
| Marginal stage rates need not identify joint terminal action risk. | [C]/[GAP] | STAGE-NULL counterexample, research/active/41-round-26-stage-risk-reconciliation.md | Counterexample and all-start linkage requirement | Proposed negative boundary, not an external theorem. |
| NoIR is not automatically vein sensing. | [K] | Raspberry Pi Camera Module 3 product brief, https://pip-assets.raspberrypi.com/categories/786/786-product-brief.pdf | Product brief p. 3 | Exact purchased revision remains unresolved. |

## Queries and failed searches

Queries run or rechecked on 2026-09-24:

- cross-session palmprint enrollment template selection later transaction open set
- palmprint palm vein long-term representative template selection 2019 paper
- mobile palmprint ROI quality recapture open set 1:N Palm-ID
- palmprint sequential open set accept reject continue transaction Murakami Takahashi WIFS 2009
- physical palmprint presentation attack print display replay RGB NIR full path
- GBU-Palm RGB NIR palm presentation attack detection arXiv 2026
- palmprint missing modality RGB NIR cross-session recognition fallback

No primary paper was verified that combines charged cross-session enrollment, a third untouched live Palm transaction, and an original-eligible denominator; this is a retrieval gap, not proof of novelty. No exact local Pi guidance/action, paired VIS/NIR action, or physical PAI-to-ROI/1:N/action paper was verified. The 2015 mobile-palm full bibliographic record and normative ISO clauses remain source gaps and are not upgraded beyond the labels above.

## Decision

| Candidate | Decision | Kill/pivot gate |
| --- | --- | --- |
| E-BOUND-X | **PIVOT** | Longitudinal evaluation only; kill without disjoint third visit/original denominator or if fixed controls dominate. |
| OPEN-ACTION-EP | **PIVOT** | STAGE-NULL/action-linkage only; kill positive policy if labels or all-start linkage are missing. |
| VIS-GUIDE | **HOLD/PIVOT** | Reopen only after frozen executable and counterbalanced prompt; kill if fixed recapture/fixture repair matches. |
| NIR-MISS-X | **HOLD/PIVOT, kill-leaning** | Prove paired hardware and independent missingness first; kill if second VIS or fixed fallback matches. |
| PA-FULLPATH | **PIVOT, otherwise KILL** | Keep only as physical endpoint audit; kill if PAI cannot reach ROI/1:N or authorization/holdouts fail. |

**Overall decision: PIVOT. No candidate is PROMOTED.**
