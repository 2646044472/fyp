# Validation Audit: 2026-09-23 T-RETRY no-count feasibility

## Decision investigated

Can the staged Pi 5 Palm Payment FYP defend history-dependent `commit / guided retry / unknown` improving unknown-person wrong-debit, enrolled completion and p95 full-transaction time without a participant count? The December VIS live-ROI, identifier-free 1:N mock-debit MVP remains mandatory engineering, not novelty. This audit incorporates `minutes_note.md/9-22.md` as an uncalibrated observation.

## Claim under test

[C] With frozen gallery, matcher, threshold, at most three physical captures, prompt and deadline, history of ROI, score, top-two margin, elapsed time and prior outcome improves a held-out wrong-debit/completion/p95 frontier beyond best fixed 1/2/3-shot, quality-retake, margin and conservative one-shot controls. An episode starts at physical presentation and includes acquisition/ROI failure; it ends in at most one idempotent mock debit. Unknown means a bona-fide person absent from gallery, not an attack.

## Three-round novelty audit

| Round | Evidence for collision | Remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component | Palm-ID has mobile open-set 1:N and quality recapture; NIST IR 7544 covers quality reacquisition; Czajka/Bowyer studies dependent selected retries. | Pi full-path mock debit and prompt response are different measurements. | High/medium |
| Exact claim | Murakami/Takahashi WIFS 2009, Secs. 2-4, models `H0=non-enrollee`, enrolled hypotheses, score histories, accept/reject/continue, maximum inputs, enrollee/non-enrollee false accept and mean inputs. | Precollected multimodal scores, not prospective guided palm captures, p95 wall time or debit. Residual is causal acquisition/evaluation, not generic sequential-decision novelty. | High collision; newer citations incomplete |
| Boundary | Rare debit differences need independent unknown people; offline replay cannot reveal a capture under an untried prompt; always-unknown makes safety trivial but service unusable. | Randomized live prompt may identify a local completion/time effect, not rare-debit superiority without separate power. | High mathematical, conditional empirical |

## Assumption and identification audit

[K] Every eligible first physical presentation belongs in the episode denominator, including nonacquisition, ROI failure, refusal, timeout and retries. Person, hand, session, episode, frame and impostor pair are distinct units. Repeated frames/sessions of one person cannot be counted as independent new unknown people. Declare a fixed gallery and roster independent unknown truth; matcher scores do not label it. Report person-clustered intervals and enrolled wrong-identity debit separately.

[C] With zero wrong debits in `n` iid unknown-person episodes, the one-sided 95% binomial upper bound is `1-0.05^(1/n)`, approximately `2.996/n`. Bounds below 1%, 0.1% and 0.01% need about 299, 2,995 and 29,956 independent unknowns. Zero in 100 bounds near 3%; zero in 20 near 14%. These are upper bounds, **not efficacy, superiority or production safety**. Clustering or selection can make them optimistic.

[C] For paired A/B decisions on the same independent unknown episodes, define `d=P(A wrong,B safe)-P(A safe,B wrong)` and `q=P(discordant outcome)`. Approximate two-sided 5%, 80%-power screening: `n=(1.96+0.84)^2 q/d^2=7.84q/d^2`. Illustrative 1% versus 0.5% with disjoint errors gives `q=.015,d=.005,n~4,704`; 0.1% versus 0.05% gives ~47,040; 0.01% versus 0.005% gives ~470,400. Favorably nested errors in the first pair (`q=.005`) still need ~1,568. Pairing acts through discordance, not an automatic multiplier; near-identical policies reveal no useful difference. At 10,000 unknowns, expected baseline wrong debits are 100, 10 or 1 at those rates. These normal approximations are not rare-event/clustered power guarantees; simulate exact paired, person-cluster designs from development discordance.

[KILL] Retry selection conditional on first failure makes second-attempt scores nonrepresentative. Analyze assigned policy from all starts, not successful retries. Shared scripted traces allow replay only when proposed actions expose the same capture; a different prompt changes future data and needs randomized/counterbalanced prospective assignment. Freeze gallery, threshold, costs, prompt, stop rule and development/test identities. Predeclare threshold/gallery-size stress tests; post-hoc permissive threshold producing errors cannot establish benefit at the target operating point. Do not select only hard/high-score unknown transactions.

[GAP] `minutes_note.md/9-22.md` states assembled IR/camera, deep-learning ROI, `same hand FR 66 FA low`, and suggests background paper/box and camera swap. It supplies no denominator, units for 66, identities, sessions, threshold, modality, capture conditions or wrong-debit definition. It is **not** measured FRR/FAR or validated NIR vascular signal. Same-hand failures may make enrolled completion frequent enough to study while saying nothing about rare unknown debits. Changing camera/background mid-comparison changes the observation model.

Preflight before policy fitting: log versioned VIS camera, fixture/background, exposure/lighting, gallery/matcher, identity/session and consent; retain every physical capture/ROI failure with ROI/keypoints, blur/pose/brightness, embeddings, top-two scores/margin, threshold and stage times. Blindly inspect failed and successful ROI samples and separate localization, registration, illumination/domain and matcher-threshold failures. Vary one box/background/camera factor at a time on development captures, then freeze one VIS configuration. If a fixed ROI/quality correction removes the rejection, history policy loses its proposed mechanism. IR is only an assembled path until repeatable vessel evidence survives visible texture, crease and brightness controls across sessions.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Murakami and Takahashi, WIFS 2009, DOI https://doi.org/10.1109/WIFS.2009.5386482 ; author text https://www.researchgate.net/publication/224101509_Accuracy_improvement_with_high_convenience_in_biometric_identification_using_multihypothesis_sequential_probability_ratio_test | Multimodal score sequence; accept identity/unknown or continue up to T. | Secs. 2.2-2.3, 3.1-3.3, 4.1-4.2, pp. 66-70: EFRR, EFAR, NFAR, mean input count on BSSR1. | Direct sequential open-set collision; physical palm guidance and p95 debit path absent. | Kills generic adaptive 1:N stop/retry novelty; iid score assumptions need not hold for same-hand retries. |
| Grosz et al., Palm-ID arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Mobile ROI, quality reject/recapture, thresholded 1:N search. | Secs. II-A/F/G, III-A/C/D, IV-A/B: FPIR/FNIR, component latency. | Open-set quality/retry. | Search FPIR is not full debit risk; server search time is not Pi p95. |
| Czajka and Bowyer, BTAS 2015, DOI https://doi.org/10.1109/BTAS.2015.7358797 ; author text https://www.researchgate.net/publication/279911940_Statistical_evaluation_of_up-to-three-attempt_iris_recognition | Up to three selected iris presentations. | Secs. 1-5, pp. 1-6: attempt-conditioned score and quality; returning volunteers. | Retry dependence, 1:1 iris. | Kills iid frames and novel dependence observation. |
| NIST IR 7544, 2008, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Quality feedback and reacquisition. | Secs. 2.1.1-2.1.3, 4-6: quality and same-session optimism. | Guided quality control. | Requires a strong fixed reacquisition baseline. |
| X-Palm arXiv:2606.08437v1, 2026-06-07, https://arxiv.org/html/2606.08437 ; official https://github.com/X-Palm/X-Palm-2026 | Pi-controlled multispectral scanner and smartphone images, annotated ROI. | Secs. 2.1-2.4, 3.1-3.3, App. A: Rank-1/EER and domain protocols. | Palm/edge data, not transaction retry. | Training-disjoint open-set is not necessarily unknown-to-gallery debit rejection. |
| Ma et al., GBU-Palm arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389 | Physical print/replay RGB/NIR video and PAD ROI. | Secs. 2-4, Tables 1-3: bona-fide/attack discrimination. | Later attack stage, not bona-fide unknown retry. | Cannot proxy local full capture-to-1:N debit. |

## Strongest simple baseline

Select a **development-only frontier**, not a weak point: conservative one-shot `ROI valid AND top score >= tau AND margin >= m`, else unknown; the same rule after one fixed quality-triggered guided retake; and fixed 2/3-shot or best-quality capture with candidate consistency. Sweep score, quality and margin cutoffs on development people only, subject to predeclared completion and opportunity/time budgets. Freeze admissible points for held-out people/sessions. Charge all acquisition/ROI failures, guidance and time. Always-unknown is a safety floor but unusable at enrolled completion. The strongest specific comparator is fixed quality-triggered one-retake plus score/margin/candidate consistency. A learned history policy must beat its held-out frontier, not naive accept-any-shot. Keep VIS-only after preflight; IR requires separate validation.

## Contrarian result

[KILL] With no independent unknown-person count, measured transaction-level discordance or localized same-hand failure, positive wrong-debit policy superiority is not a feasible present thesis claim. The WIFS 2009 paper narrows sequential-decision novelty more than previous packets allowed. A small pilot can measure capture mechanics, completion and time, not production-like false-debit safety. [PIVOT] A lower-sample but still conditional question: *After a first physical ROI/quality failure on a frozen VIS Pi path, does a randomized predeclared positioning prompt improve held-out enrolled correct completion and p95 full-episode time over an equally budgeted fixed quality retake?* Unknown wrong debit is counted with person-level bounds, not claimed improved. This local causal acquisition question must survive Palm-ID/NIST-style guidance and fixed baselines; a null is useful bounded evidence, not automatic thesis promotion.

## Feasibility audit

No participant count, ethics route, independent unknown roster, consent/retention rules or returning visits is established. One enrolled and one unknown live MVP proves plumbing, not a rate. Resolve preflight localization before training policy. Then preregister minimum meaningful completion/time difference and interval width, people/session split, gallery, threshold, prompt, costs, deadline and test stop rule. Estimate development discordance and recalculate person-clustered feasibility. If randomized prompting is impermissible, the causal pivot also fails. The p95 needs sufficient independent episodes and person-level uncertainty. E-BOUND needs genuinely distinct visits; PA-CHARGE needs authorized physical lineages; neither bypasses unknown-person needs.

Palm-ID's MSU PalmDB official agreement https://biometrics.cse.msu.edu/Publications/Databases/MSU_PalmDB/MSU_PalmDB_Database_Agreement.pdf and access page https://biometrics.cse.msu.edu/Publications/Databases/MSU_PalmDB/ require a research agreement/PI approval, not unrestricted reuse. X-Palm's official GitHub README above requires a signed noncommercial academic EULA and restricts redistribution; its annotated ROIs and different Pi scanner/smartphone route cannot estimate this fixture's acquisition failures or prompt response. GBU-Palm v1 says its physical video PAD dataset is public, but dataset-specific distribution terms were not established here; a paper's CC license is not image consent. Even lawfully accessed images/videos cannot establish local capture-to-mock-debit latency or independent unknown-person risk. Check institutional human-subject and biometric-data permission separately. Do not treat frames, pair scores or attack videos as new people.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Sequential non-enrollee decision exists | [K] | Murakami/Takahashi WIFS 2009 accepted author text, DOI and URL above | pp. 66-70, Secs. 2-4, Figs. 1/4 | Precollected multimodal scores; citing descendants not exhaustively traced. |
| Selected biometric attempts differ | [K] | Czajka/Bowyer BTAS 2015 full author text and DOI above | pp. 1-6, Secs. 1-5 | Iris 1:1, not local palm 1:N. |
| Palm quality and open-set search | [K] | Palm-ID arXiv:2401.08111v1, 2024-01-16 | II-A/F/G, III-C/D, IV-A/B | Search FPIR not episode wrong debit. |
| Guided quality control precedes proposal | [K] | NIST IR 7544 (2008), URL above | 2.1.1-2.1.3, 4-6 | Not proof a particular prompt works. |
| Dataset scope/terms | [K/GAP] | X-Palm arXiv:2606.08437v1, 2026-06-07, Secs. 2-4/App. A and official GitHub README; GBU-Palm arXiv:2608.14389v1, 2026-08-14, Secs. 2-4; MSU PalmDB agreement | Sections as stated; GitHub Dataset Access; MSU agreement | Confirm institution-specific permission; GBU distribution terms unresolved. |
| Same-hand rejection observation | [GAP] | `minutes_note.md/9-22.md`, date inferred from filename; entire five-line note | Entire note | `66`, `FA low`, protocol, denominator and modality unverified. |
| Rare-event requirements | [C] | Binomial zero-event formula and paired-discordance approximation derived above | This audit | Illustrative iid person equivalents, not clustered power. |

## Queries and failed searches

Searched 2026-09-23: `sequential biometric identification quality guided retry face recognition open set transaction sequential probability ratio test full paper`; `site:arxiv.org sequential face recognition adaptive frame selection verification video open set quality reject retry`; `site:openaccess.thecvf.com sequential face recognition active acquisition uncertainty stop recognition video`; `Czajka Bowyer statistical evaluation up to three attempt iris recognition pdf`; `palm-ID MSU palmprint database release data license request github`; `site:arxiv.org X-Palm dataset license 2026 palmprint multispectral`; `site:arxiv.org/html/2608.14389 GBU-Palm dataset access license`; `site:nd.edu Statistical evaluation of up-to-three-attempt iris recognition pdf`; `Murakami Takahashi multihypothesis sequential biometric identification WIFS 2009`. A face open-set primary PDF was located, https://openaccess.thecvf.com/content_cvpr_2017_workshops/w6/papers/Gunther_Toward_Open-Set_Face_CVPR_2017_paper.pdf , but its full protocol was not verified in this pass and it supports no central conclusion here. Newer WIFS citation descendants and Bob Zhang's closest full open-set paper remain unresolved. No exact Pi transaction study found by these bounded queries is **not** global novelty evidence. GBU release terms, local ethics, cohort, operating threshold, policy discordance, camera/IR settings and cause of `FR 66` remain [GAP].

## Decision

**KILL** the positive rare wrong-debit/sequential-policy thesis as presently specified. **PIVOT** conditionally to a preflight-localized, randomized VIS quality-guidance completion/time comparison against the fixed quality/margin retake, with unknown-debit counts and honest person-level upper bounds only. Do not pool camera/background changes or claim NIR vein validation. Continue the authorized MVP unchanged.

PIVOT
