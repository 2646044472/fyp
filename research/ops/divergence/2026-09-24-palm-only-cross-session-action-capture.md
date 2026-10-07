# Divergence Packet: 2026-09-24 Palm-Only Cross-Session, Action, Capture, and Missing-Modality Questions

## Decision investigated

The user has locked the FYP scope to palm recognition. This packet therefore searches only inside the palm-recognition pipeline and deliberately excludes generic edge mechanisms.

Result: no new palm method is promoted. Four bounded questions remain worth validation, all as evaluation or negative-result candidates:

- `E-BOUND-X`: cross-session enrollment selection measured at a later untouched transaction visit;
- `OPEN-ACTION-EP`: open-set unknown decisions evaluated through the actual downstream action, not as an offline threshold/calibration method;
- `VIS-GUIDE`: physical presentation and live ROI reachability, evaluated as completion/time beyond fixed recapture controls;
- `NIR-MISS-X`: whether a paired VIS/NIR observation remains useful when one modality is missing or unavailable across sessions, with the terminal identity/action endpoint.

`PA-FULLPATH` is included only as a conditional PAD gate. It is not a promoted candidate and must be killed if the full physical path, lawful attack protocol, and denominators cannot be obtained.

## Search boundary

Excluded as already covered or killed in the active register: generic ROI/recognition/retry/gallery/calibration, generic open-set threshold transport, model transfer, generic adaptive sensing or modality selection, stage-risk/calibration/selective prediction, generic compression/side information, and any PAD claim that bypasses physical capture or lacks a full path.

Read before proposing: `research/active/README.md`, `00-project-charter.md`, `01-candidate-register.md`, `40-round-25-targeted-reconciliation.md`, `41-round-26-stage-risk-reconciliation.md`, and `research/archive/2026-08-edge-sensing/README.md`. The current Palm route is a VIS live-capture, identifier-free open-set 1:N, simulated-account transaction. This is an engineering commitment, not itself a novelty claim.

The distinction sought in every candidate is the endpoint and observation protocol: cross-session person-blocked outcome, all-start physical transaction, or full physical presentation path. A new CNN, threshold, cropper, or NIR fusion block is explicitly out of scope.

## Recent-paper limitation map

### Enrollment and longitudinal representation

NIST IR 7544, *Biometric Quality: A Survey of Methods and Best Practices* (2008), discusses acquisition quality, failure-to-enroll, recapture and the danger of optimistic same-session evaluation. Chen et al., *Long-Term Representative Palmprint/Palm Vein Template Selection* (2019), directly studies selecting representative templates from longer-term samples. Palm-ID (2024) combines mobile palm acquisition, ROI, quality rejection/recapture, enrollment and open-set 1:N. These sources occupy quality-driven enrollment, template selection and ordinary recapture.

The remaining question is not a new enrollment algorithm. It is whether a charged enrollment choice, including refusal or a second visit, changes the later untouched full-transaction outcome when the denominator includes every originally eligible person. This is a protocol/evaluation distinction and is vulnerable to selection bias.

### Open-set identity to action

Murakami and Takahashi, WIFS 2009, formulate sequential open-set biometric accept/reject/continue decisions. NIST transaction metrics and Palm-ID occupy open-set recognition and recapture reporting. The active `STAGE-RISK` audit also killed a generic stage-conditioned risk estimator.

The only residual is an episode-level audit: a participant who reaches the live path is labelled as bona fide enrolled, authorized-but-unknown, or unauthorized/mate-absent, and the actual action outcome is recorded. No new threshold or calibration claim is made. The contribution, if any, is a finite identifiability result about which open-set/action outcomes cannot be inferred from matcher-only summaries.

### Physical capture and ROI reachability

The 2015 mobile palm record and Palm-ID occupy guided acquisition, ROI localization, quality rejection and recapture as general mechanisms. Therefore `VIS-GUIDE` can survive only as an apparatus-specific prospective comparison on the actual payment executable: one prompt versus fixed prompt, fixed quality/margin retake, and conservative unknown. The endpoint is all-start completion and capture-to-action time, not ROI accuracy or a generic guidance method.

### VIS/NIR missing modality

Palm-ID and GBU-Palm-style protocols occupy mobile capture, RGB/NIR variation, attack/environment splits and recognition/PAD evaluation. The active register also kills generic adaptive modality selection and treats `NOIR-SIDEINFO` as a communication/control benchmark. A narrow recognition question remains only if the modality is collected as a physically paired observation and the experiment fixes capture opportunities: does VIS-only recognition/action remain safe when NIR is unavailable, and does a predeclared missing-modality fallback beat VIS-only and fixed two-shot controls across held-out sessions? It must not be called palm-vein sensing from NoIR brightness or crease cues.

### PAD full path

GBU-Palm and ISO/IEC 30107-3 occupy physical presentation-attack terminology, attack instruments, lineage and PAD reporting. A local study could still be an apparatus-specific endpoint audit from physical print/display presentation through capture, ROI, PAD, open-set 1:N and simulated debit, but only with authorized attack materials, person/material/session holdouts, a frozen no-PAD control, and complete stage denominators. Cropped ROI injection or digital replay is not a physical PAD experiment.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| `E-BOUND-X` | A user is enrolled quickly with a poor or nonrepresentative palm sample. At a later visit the owner is rejected, or an unknown person is assigned a mock account; extra enrollment burden can exclude users. | At equal enrollment minutes and storage/search cost, compare best-quality single frame, same-session consistency, fixed diverse templates, charged second-visit confirmation, and refusal. Claim only an effect on the third untouched visit's full transaction outcome, including every originally eligible person. Inputs: enrollment captures, visit/session ID, consent, gallery state, fixed matcher/threshold. Actions: enroll, request revisit, refuse, later commit, unknown, or no action. | NIST IR 7544; Chen et al. 2019 longitudinal template selection; Palm-ID 2024. | Best-quality, fixed multi-template, same-session, or conservative refusal matches/dominates; no third untouched visit; or successful-enrollee-only analysis produces the effect. A second visit used as both enrollment and test kills the claim. | Strongest route-compatible question, but requires repeat visits, consent, person-blocked splits, deletion policy, and enough unknown/mate-absent episodes. `HOLD/PIVOT`. |
| `OPEN-ACTION-EP` | A matcher returns a plausible identity for an unauthorized or mate-absent palm. A downstream commit then creates a wrong mock debit; a conservative unknown delays an owner. | Without changing the matcher, quantify whether matcher-only summaries identify the terminal action outcome under participant-level open-set episodes. Compare direct episode frequency with fixed unknown/retake/refusal controls. Inputs: all eligible starts, true authorization class, gallery membership, match/top score/margin, action policy and result. Endpoint: correct action, wrong identity action, unknown, owner completion, and time. | Murakami/Takahashi WIFS 2009 sequential open-set decisions; NIST transaction metrics; Palm-ID 2024; active `STAGE-NULL`. | If a fixed score/margin/quality rule predicts and controls the action endpoint, or if mate-absent and owner episodes cannot be lawfully sampled, kill. If only marginal FAR/FRR/FTE are available, retain only the non-identifiability counterexample. | Feasible only after the Palm MVP has full all-start traces and an authorized independent unknown-person protocol. No offline gallery-calibration thesis. `PIVOT`. |
| `VIS-GUIDE` | A legitimate user cannot present the palm in the physical capture window, causing delay; an over-permissive continuation can trigger a wrong mock action. | On the frozen payment executable, a prospectively assigned physical prompt changes all-start completion or p95 capture-to-action time beyond fixed prompt, fixed quality/margin retake, and conservative unknown at matched capture opportunities. Inputs: physical start, prompt assignment, raw frame, ROI reachability, matcher/open-set output, action and timing. | 2015 mobile palm guidance; Palm-ID 2024 quality rejection/recapture; sequential open-set work. | Fixed retake or a repaired fixture/ROI dominates; payment path is unstable; prompt assignment is not counterbalanced; or the result is only ROI-stage accuracy. No rare wrong-debit superiority claim. | Requires no new modality, but needs frozen hardware/software, all-start logging, participant consent and prospective counterbalancing. `HOLD/PIVOT`, evaluation-only. |
| `NIR-MISS-X` | A palm transaction is enrolled or tested with VIS, but NIR is unavailable due to power, glare, hardware or capture failure. Falling back incorrectly rejects an owner or accepts an unknown. | In paired cross-session VIS/NIR captures, evaluate a predeclared VIS-only fallback when NIR is missing against VIS-only-from-start, fixed VIS+NIR, and fixed second-VIS capture at equal capture opportunities. Endpoint is held-out open-set identity/action, not generic modality accuracy. | Palm-ID 2024; GBU-Palm RGB/NIR and PAD protocols; active `IR-CAUSE`, `NOIR-SIDEINFO`, and generic modality-selection audits. | NIR is not independently useful beyond a second VIS capture; registration/energy/capture overhead dominates; a fixed fallback is Pareto-optimal; or NoIR evidence is incorrectly interpreted as vein truth. | Requires paired camera operation, exact synchronization and a lawful person/session set. No purchase or thesis claim before a capability and cross-session feasibility preflight. `HOLD/KILL-leaning`. |
| `PA-FULLPATH` | A physical print/display presentation reaches the payment path and may cause a false account action; a strict PAD rule may reject legitimate users. | Only if feasible: compare no-PAD, fixed quality/score rejection, fixed recapture, and a frozen PAD control from physical presentation through ROI, PAD, open-set 1:N and mock action at matched bona-fide completion/time/resource cost. | GBU-Palm; ISO/IEC 30107-3; Palm-ID 2024; prior palm spoofing literature. | PAI fails before ROI/matcher; no independent attack lineage/holdout; fixed controls match; or the experiment uses cropped/digital injection. Zero attacks in a small pilot is not an assurance bound. | High ethics, material, participant and apparatus burden. Keep only as a gated audit, not a method. `KILL/PIVOT`. |

## Top two formalizations

### 1. `E-BOUND-X`

- **[D] Decision-maker:** enrollment operator/policy deciding accept, request a charged revisit, or refuse; later transaction policy decides commit, unknown, or no action.
- **[A] Actions:** one of six predeclared enrollment arms; at the third untouched visit, commit, unknown, guided retake, or no action.
- **[T] Constraints:** equal enrollment minutes, frozen matcher/gallery/threshold, person-blocked sessions, original-eligibility denominator, no use of the third-visit outcome during enrollment, and an explicit storage/deletion policy.
- **Observable outcome:** failure-to-enroll, later correct completion, unknown, wrong identity, mock debit, and capture-to-action time.
- **Counterexample:** the apparent benefit disappears when all initially eligible people and refusals are included, or the “test” visit is also the charged enrollment visit.
- **Minimum falsification experiment:** at least two enrollment visits plus one untouched transaction visit, with six arms and a person-level analysis; a matched-control result that is no worse than the charged arm kills the positive claim.
- **Negative-result value:** establishes whether a longitudinal enrollment decision is identifiable separately from template selection and selection bias.

### 2. `OPEN-ACTION-EP`

- **[D] Decision-maker:** the frozen open-set transaction policy after a live physical capture.
- **[A] Actions:** commit to the selected account, return unknown/retake, or refuse action.
- **[T] Constraints:** every eligible physical start is logged; gallery membership and authorization class are independent labels; matcher and threshold are frozen; no test-set score tuning; terminal action is the primary endpoint.
- **Observable outcome:** correct owner action, wrong identity action, unknown, no completion, and time.
- **Counterexample:** construct two episode populations with identical marginal FAR/FRR/FTE/FTX and score distributions but different dependence between stage reachability and terminal action. If action risk differs, marginal summaries are insufficient; if a fixed matcher/quality/margin control resolves it, no positive method remains.
- **Minimum falsification experiment:** a small authorized person-blocked open-set pilot with all-start denominators and an exact action trace; no new calibration algorithm.
- **Negative-result value:** cleanly separates biometric performance reporting from the downstream action endpoint and gives a defensible stop condition if the required unknown-person labels are unavailable.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Quality, failure-to-enroll and recapture must be separated from later transaction performance. | [K] | NIST IR 7544, *Biometric Quality*, 2008, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Quality/acquisition and evaluation sections; pp. 1-3, 22-30 | General biometric guidance, not a palm-specific open-set method. |
| Long-term palm template selection is already studied. | [K] | Chen et al., *Long-Term Representative Palmprint/Palm Vein Template Selection*, 2019, source chain recorded in `research/ops/validation/2026-09-24-targeted-e-bound-pa-charge-noir-prog-ret-audit.md` | Task, multi-session protocol, template-selection evaluation and limitations as recorded in that packet | Therefore `E-BOUND-X` is an endpoint protocol, not a new template selector. |
| Mobile palm acquisition, ROI, quality rejection/recapture and open-set 1:N are direct neighbors. | [K] | Palm-ID (2024), official paper/code URL and exact reading notes in the targeted validation packet | Introduction, acquisition/ROI, quality/recapture and recognition evaluation | Exact local payment executable remains apparatus-specific; no global novelty claim. |
| Sequential open-set accept/reject/continue is established. | [K] | Murakami & Takahashi, WIFS 2009, URL and pages recorded in `research/active/01-candidate-register.md` and validation packet | Sequential open-set decision formulation and experiments | Kills a generic retry/continue policy claim. |
| Physical palm presentation attacks and PAD reporting have established protocols. | [K] | ISO/IEC 30107-3; GBU-Palm source chain and exact sections in targeted validation packet | Attack instruments, protocols, splits and PAD metrics | A full local physical-to-action audit may still be finite; it is not a new PAD method. |
| `E-BOUND-X` can be distinct only through a later untouched full transaction and original-eligibility accounting. | [C] | Inference from direct neighbors and active round-25 reconciliation | `research/active/40-round-25-targeted-reconciliation.md`, candidate design above | Must be checked by validation; no novelty claim. |
| `OPEN-ACTION-EP` cannot be inferred from marginal stage rates without dependence/linkage assumptions. | [C]/[GAP] | Counterexample retained in `research/active/41-round-26-stage-risk-reconciliation.md` | Surviving `STAGE-NULL` formalization | This is a negative-result hypothesis, not a new estimator. |
| VIS/NIR missing-modality fallback is not yet a promoted direction. | [GAP] | Active register entries `NOIR-SIDEINFO`, `IR-CAUSE`, `XFER-ACT` and round-25 packet | Candidate collision and feasibility sections | The exact recognition/action endpoint still needs a targeted direct-neighbor audit. |

## Queries and failed searches

Queries used or inherited for this Palm-only round:

- `cross-session palmprint enrollment template selection later transaction open set`
- `mobile palmprint ROI quality recapture open set 1:N`
- `palmprint sequential open set accept reject continue transaction`
- `palmprint RGB NIR missing modality recognition cross session`
- `palm presentation attack physical print replay RGB NIR full path`

The searches returned direct work for quality/recapture, longitudinal templates, sequential open-set decisions, RGB/NIR/PAD evaluation, and physical presentation protocols. No exact source was verified for the combination “charged cross-session enrollment decision + untouched later palm transaction + original-eligibility denominator”; that is a bounded retrieval gap, not a novelty claim. Likewise, no exact source was verified for the local Pi executable's physical prompt endpoint or VIS/NIR missing-modality action endpoint.

Rejected framings:

- new ROI or cropper: already generic ROI/quality and current MVP engineering;
- new retry/threshold/calibration policy: killed by sequential open-set and calibration neighbors;
- offline gallery calibration: killed by `G-ADMIT` audit;
- generic stage-conditioned transaction risk: killed by `STAGE-RISK` audit;
- generic NIR/NoIR fusion or modality selection: already audited and likely dominated by fixed controls;
- PAD from cropped ROIs or digital injection: not a physical full-path claim.

## Decision

**PIVOT.** There is no promoted palm method in this round.

Priority for validation is:

1. `E-BOUND-X`, strongest and most route-compatible, but evaluation-only and gated on repeat visits;
2. `OPEN-ACTION-EP`, only as a bounded action-linkage/identifiability audit after all-start traces;
3. `VIS-GUIDE`, only as a prospective physical completion/time comparison;
4. `NIR-MISS-X`, only after paired hardware and cross-session feasibility;
5. `PA-FULLPATH`, conditional audit and otherwise KILL.

The minimum next research experiment is not a new model: freeze the VIS payment pipeline, log every physical start through ROI, open-set identity, unknown/correct/wrong identity, mock action and timing, then test whether a third untouched session and independent open-set labels can be obtained. If that gate fails, retain the negative identifiability result and do not expand the palm mechanism.
