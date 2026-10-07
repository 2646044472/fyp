# Validation Audit: 2026-09-23 newest directions and Palm post-MVP

## Decision investigated

Audit the newest divergence packets visible on 2026-09-23:

- `2026-09-23-cross-mechanism-edge-decisions.md`: `TRIG-LEAK`, `STALE-ACT`, `SLO-REFUSE`, and `PROOF-BOUND`.
- `2026-09-23-palm-direction-next-gate-divergence.md`: `A-ROI`, `G-ADMIT`, `S-SELECT`, and `P-DELETE`.
- `2026-09-23-staged-palm-transaction-questions.md`: the post-MVP `T-RETRY`, `E-BOUND`, and `PA-CHARGE` questions.

Read `AGENTS.md`, `research/ops/agent-validation.md`, active `README.md`, `00-project-charter.md`, and `01-candidate-register.md` first. This packet does not edit `research/active/`, `research/archive/`, or `.research/`.

## Claim under test

The newest packets claim that a one-year edge FYP may still obtain a thesis from either (a) a causal decision over traffic protection and deadlines, (b) action freshness, or (c) a Palm Payment post-MVP policy/evaluation. The validation question is stricter: does any candidate have a task, observation model, action, constraint, and evaluation endpoint that is both identifiable with the available apparatus and not removed by a direct neighbor or a simple baseline?

The current Palm route remains a staged engineering commitment: visible-light physical capture, live ROI, identifier-free open-set 1:N, frozen unknown handling, and an idempotent logged mock debit. That route is not itself a research contribution.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| `TRIG-LEAK` component | [KILL] Causal traffic camouflage already selects among padding, splitting, timing, cover traffic, compositions, and no transformation under bandwidth/latency limits. Event-level traffic shaping already trades privacy against dummy traffic and delay. | A hard application deadline and event-time AUC could define a narrower endpoint than device fingerprinting. | High collision; narrow endpoint distinction remains conditional. |
| `TRIG-LEAK` exact claim | [KILL] Timeliness/privacy joint optimization already includes update policies and leakage-sensitive timing. The proposed `send/defer/cover-send` controller is still a policy over an established privacy-cost surface. | [GAP] The exact combination of a declared event, hard deadline, byte budget, and defense-aware event-time attacker was not fully traced through the blocked DPShaping paper. This is an audit gap, not novelty evidence. | Medium-high collision. |
| `TRIG-LEAK` boundary | [KILL] A fixed schedule independent of the event can hide occurrence only by spending enough cover traffic and waiting no longer than the deadline. If the byte budget forbids that, the privacy target is infeasible rather than algorithmically improved. | [C] A finite empirical frontier can still be measured with an explicit threat surface, prior, deadline, budget, and retrained attacker. | High boundary confidence. |
| `STALE-ACT` component | [KILL] Task-age routing, delayed control prediction, and Age of Actuation/Age of Actuated Information already cover freshness-aware edge action decisions. | A local post-capture state-transition proxy and a tabletop endpoint are a narrower apparatus. | High collision. |
| `STALE-ACT` exact/boundary | [KILL] The direct execution-time state read is an observable witness of the target. If it is available at comparable cost, it dominates age and proxy policies. If it is forbidden without a real operational constraint, the restriction is artificial. Identical capture/age/proxy observations can correspond to opposite current states. | Only a constrained negative study survives: quantify how a proxy fails when the direct witness is unavailable. | High. |
| Palm `A-ROI`/`VIS-GUIDE` | [KILL] Mobile palm ROI, quality rejection, recapture, and open-set identification are already direct components; guided acquisition and ordinary retry are established controls. | A prospective, counterbalanced physical prompt versus a fixed retake can measure local all-start completion and p95 action time after the executable is frozen. | Medium-low thesis novelty; high evaluation feasibility conditional on MVP. |
| Palm `G-ADMIT` | [KILL] Gallery-relative calibration, gallery-size controls, quality/margin thresholds, and mate-present/absent evaluation are occupied by the inspected palm/biometric neighbors. | A finite, lawful, device-specific transport audit could be useful if a real gallery/unknown roster exists. It cannot establish a production FAR or transport guarantee. | High kill risk. |
| Palm `S-SELECT`/`P-DELETE` | [KILL] Runtime path selection among fixed VIS/NIR stages and ordinary transaction deletion/idempotency are engineering controls unless a new decision guarantee or resource frontier is demonstrated. | A measured deployment report or negative control remains useful for the project. | High. |
| Palm `T-RETRY`/`E-BOUND`/`PA-CHARGE` | [KILL] Sequential accept/reject/continue and dependent biometric attempts are established; enrollment quality controls are standard; generic physical RGB/NIR PAD and fusion are occupied. | `E-BOUND` could test longitudinal change, and `PA-CHARGE` could test a device-specific physical attack endpoint, but both require data, authorization, and a stable service path not currently evidenced. | Medium-high kill risk. |

## Assumption and identification audit

1. [KILL] `STALE-ACT` cannot claim improved action correctness from a proxy while denying the direct current-state measurement that defines correctness. The paired-world counterexample is decisive: two worlds may have the same capture, timestamp, age, and proxy trace but opposite execution-time state, forcing the same policy action.

2. [KILL] `TRIG-LEAK` does not identify a privacy improvement unless the observation surface is fixed. Packet sizes, timing, direction, retransmission, ACKs, endpoints, and metadata can leak outside the proposed feature surface. A classifier AUC on a synthetic trace is not a guarantee against a changed event prior or richer observer.

3. [GAP] `TRIG-LEAK` has no confirmed confidentiality owner, loss function for a missed deadline, byte budget, network vantage, or permission to capture traffic. Without these, its story is hypothetical and the chosen endpoint is arbitrary.

4. [KILL] The Palm note `same hand FR 66 FA low` has no count, denominator, threshold, modality, session, identity roster, or raw trace. It cannot identify a matcher, ROI, camera, or vein failure. The payment UI's default automatic ROI and the debug UI's deep-learning landmark ROI are separate paths; debug observations cannot be assigned to the payment chain.

5. [KILL] `G-ADMIT` requires person-disjoint development and final identities, known and absent users, gallery provenance, and held-out sessions. A cropped public dataset or gallery rotation does not identify live physical capture-to-debit behavior.

6. [GAP] `VIS-GUIDE` can identify only a local completion/time effect if prompt assignment is prospective, the all-start denominator is retained, the matcher/ROI/configuration is frozen, and unknown-person wrong commits are counted. Replay of successful captures cannot estimate the counterfactual hand trajectory created by a prompt.

7. [GAP] `E-BOUND` requires repeated visits with stable enrollment and an authorized longitudinal roster. `PA-CHARGE` requires authorized physical attack sources, optical/electrical safety review, source-lineage splits, and a real local endpoint. None is currently evidenced.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Worae et al., *Adaptive Traffic Camouflage*, arXiv:2609.25787v1, 2026-09-22 | Previous-window traffic shape; selects padding, splitting, timing, cover, compositions, or no action under resource profiles. | Device fingerprinting Macro-F1, bandwidth, latency, clean/defense-aware/incremental attackers. | [K] Same causal resource-aware mechanism and heterogeneous action selection as `TRIG-LEAK`. | Kills generic adaptive traffic camouflage. Leaves only a narrower event/deadline measurement, not a new mechanism. |
| Xiong et al., *Network Traffic Shaping for Enhancing Privacy in IoT Systems*, arXiv:2111.14992v1, 2021-11-29 | Event/packet timing and size shaping, dummy traffic, delay and privacy controls. | Traffic privacy versus overhead and delay. | [K] Same privacy-cost control family. | Kills generic event shaping; leaves a bounded apparatus-specific frontier if the threat model is real. |
| Sathyavageeswaran et al., *Balancing Timeliness and Privacy in Discrete-Time Updating Systems*, arXiv:2512.13439v1, 2025-12-15 | Update timing/accumulation policy. | Joint leakage and timeliness/AoI objectives. | [K] Same privacy-versus-timeliness objective family. | Kills a claim that deadline-aware privacy is a new objective; exact event endpoint remains [GAP]. |
| Nikkhah et al., *Semantics in Actuation Systems*, arXiv:2601.15496v1, 2026-01-21 | Age/semantic information at actuation. | Age of actuated information and action timeliness. | [K] Direct freshness/action neighbor for `STALE-ACT`. | Kills generic freshness-aware action claim; local proxy can survive only as a negative constrained test. |
| Grosz et al., *Palm-ID*, arXiv:2401.08111v1, 2024-01-16 | Mobile palm images, ROI, quality rejection/recapture, enrollment and open-set 1:N. | FNIR/FPIR, rank/quality, search and component timing. | [K] Direct overlap with Palm ROI, quality, retry, and open-set admission components. | Kills a new mobile palm pipeline or quality-retry thesis; does not measure this Pi's full physical transaction endpoint. |
| Seyedmohammadi et al., *X-Palm*, arXiv:2606.08437v2, 2026-06-22 | Pi-controlled multispectral scanner and paired mobile/scanner palm data. | Identity-disjoint benchmark, Rank-1/EER and cross-domain performance. | [K] Kills Pi/multispectral hardware novelty. | Leaves local physical transaction measurement only; its benchmark open-set split is not unknown-to-gallery debit rejection. |
| Ma et al., *GBU-Palm*, arXiv:2608.14389v1, 2026-08-14 | RGB/NIR physical print/replay videos with lineage/environment splits. | PAD classification and RGB/NIR fusion. | [K] Kills generic physical PAD, NIR-is-secure, and fusion claims. | Leaves a device-specific transaction endpoint only after authorized attacks and a stable MVP. |
| Murakami and Takahashi, WIFS 2009 sequential open-set biometric decision | Score history and repeated accept/reject/continue decisions with non-enrollees. | Sequential open-set acceptance/rejection trade-offs. | [K] Direct collision with positive `T-RETRY` sequential policy claim. | Kills generic retry/continue novelty; a local cost measurement may remain. |
| NIST IR 7544, 2008 | Quality acquisition, enrollment, failure-to-enroll and recapture controls. | Biometric acquisition and enrollment guidance. | [K] Direct control collision with `E-BOUND` enrollment/quality framing. | Kills “select a sharper enrollment sample” as thesis; leaves longitudinal risk only. |

## Strongest simple baseline

- For `STALE-ACT`: read the state at execution time. This is the target witness and dominates a timestamp/proxy policy whenever its cost and permissions are comparable.
- For `TRIG-LEAK`: fixed-period or constant-rate cover traffic, plus a no-defense control, matched to the same byte and deadline budget. If the fixed schedule is infeasible, the desired privacy guarantee is infeasible under that budget; if it wins, adaptive selection is unnecessary.
- For Palm `VIS-GUIDE`: frozen automatic ROI plus one fixed retake rule, compared with a fixed human guide, with all-start completion, terminal action time, unknown decisions, and wrong commits. A plain exposure/ROI repair or margin threshold must be included before any learned policy.
- For Palm `G-ADMIT`: global score threshold, gallery-size-specific threshold, quality gate, and top-two margin gate at equal matcher cost. If these match the proposed calibration, the thesis is removed.
- For Palm `T-RETRY`: fixed one-shot, fixed two-shot, fixed three-shot, and conservative abstain. Attempt history must beat all of them on a predeclared frontier, not only reduce retries.

## Contrarian result

[KILL] The strongest stories are not currently technical contributions. `STALE-ACT` is a direct-witness problem; `TRIG-LEAK` is an occupied traffic-shaping family with an unconfirmed owner; Palm ROI, quality, admission, retry, NIR, and PAD each collide with direct work or ordinary controls. A Raspberry Pi, a new camera, a new model, or a simulated debit does not change these collisions.

[HOLD] A narrow negative/evaluation study can still be valuable. The most defensible residual is a prospective, apparatus-specific VIS capture-to-terminal-action audit after the MVP: stagewise failure attribution first, then counterbalanced guide-versus-fixed-retake completion/time measurement. That is a local causal evaluation, not a promoted mechanism. `TRIG-LEAK` is a weaker alternative only if a real confidentiality owner and hard deadline are supplied before implementation.

## Feasibility audit

- Palm: [GAP] no authoritative September 22 checkout trace, participant/unknown roster, longitudinal access, ethics/consent record, or Pi login is evidenced. Public cropped images cannot substitute for physical all-start denominators. No real funds or production security claims are permitted.
- Palm PA/NIR: [GAP] source-lineage permissions, retention/deletion, optical wavelength/irradiance, eye/skin safety, camera response, and power measurement remain unresolved. Do not buy or benchmark attack/NIR hardware as a thesis direction before these gates.
- `TRIG-LEAK`: [GAP] network capture permission, observer vantage, event owner, deadline loss, byte budget, and richer side-channel surface are unresolved. A two-machine synthetic replay is feasible as a falsification test but not evidence of operational privacy benefit.
- `STALE-ACT`: [KILL] the required apparatus restriction against direct execution-time state is not a real constraint in the supplied tabletop story. Without that restriction there is no defensible experiment.
- All candidates: [GAP] one undergraduate year and the December 2026 MVP deadline leave no evidence that a new hardware, ethics, or cohort dependency can be completed and evaluated rigorously.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Causal traffic camouflage selects heterogeneous transformations under explicit resource limits and tests defense-aware attackers. | [K] | Worae et al., *Adaptive Traffic Camouflage*, arXiv:2609.25787v1, 2026-09-22, https://arxiv.org/html/2609.25787 | Abstract; Sec. III-A-C; Sec. IV-A-E; Sec. V-A-D; Sec. VI-A-F; Sec. VII | Closed-set device identification and traffic-shape surface; not event-deadline privacy. |
| Event traffic shaping already trades privacy against dummy traffic and delay. | [K] | Xiong et al., *Network Traffic Shaping for Enhancing Privacy in IoT Systems*, arXiv:2111.14992v1, 2021-11-29, https://arxiv.org/html/2111.14992 | Secs. II-VII, VIII limitations, IX conclusion; PDF pp. 4-7, 12-15 | Foundational neighboring control, not a proof of exact overlap. |
| Timeliness and privacy are jointly optimized in discrete-time updating systems. | [K] | Sathyavageeswaran et al., *Balancing Timeliness and Privacy in Discrete-Time Updating Systems*, arXiv:2512.13439v1, 2025-12-15, https://arxiv.org/html/2512.13439 | Secs. II-IV, especially IV-D; Secs. V-VII | Update/AoI setting, not a physical edge notice. |
| Age of actuated information is a direct action-freshness neighbor. | [K] | Nikkhah et al., *Semantics in Actuation Systems: From Age of Actuation to Age of Actuated Information*, arXiv:2601.15496v1, 2026-01-21, https://arxiv.org/html/2601.15496 | Secs. II-VI | Does not exactly implement the proposed tabletop proxy. |
| Mobile palm ROI, quality recapture, enrollment and open-set 1:N are occupied components. | [K] | Grosz et al., *Palm-ID*, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Secs. II-A-II-G; III-B-III-E; IV-A-IV-B; V | Not Pi full transaction timing. |
| Pi multispectral palm acquisition and cross-domain evaluation exist. | [K] | Seyedmohammadi et al., *X-Palm*, arXiv:2606.08437v2, 2026-06-22, https://arxiv.org/html/2606.08437 | Secs. 2.1-2.4; 3.1-3.3; 4; App. A.5 | Benchmark open-set means identity-disjoint evaluation, not unknown-gallery debit. |
| Physical RGB/NIR palm PAD and fusion are benchmarked. | [K] | Ma et al., *GBU-Palm*, arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389 | Secs. 1-4; Tables 1-6 | Canonical ROI/video PAD, not this local payment endpoint. |
| Quality acquisition and recapture controls are established. | [K] | Tabassi and Grother, NIST IR 7544, 2008-11, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Secs. 2.1.1-2.1.3 (PDF pp. 20-22); Secs. 4-6 | General biometric guidance, not palm-specific. |
| Sequential biometric accept/reject/continue and non-enrollee behavior are direct neighbors. | [K/GAP] | Murakami and Takahashi, WIFS 2009, exact author-text source recorded in prior validation packet; bibliographic URL not re-obtained this pass | Secs. 2-4 in prior packet | Full primary text should be reattached before a formal citation upgrade; collision lead is already sufficient to reject generic retry novelty. |
| Local payment default ROI and debug deep-learning ROI are separate. | [K] | Local `code/palm_demo/palm_payment_ui.py`, `roi.py`, `debug_ui.py`, inspected 2026-09-23 | Payment default `--roi-mode auto`; debug dynamic mode | Local code evidence; no September 22 transaction trace. |
| The September 22 FR/FA note lacks an estimand and denominator. | [K] | Local `minutes_note.md/9-22.md`, inspected 2026-09-23 | Entire five-line note | It cannot support FRR/FAR, modality, or novelty claims. |

## Queries and failed searches

Queries run or audited on 2026-09-23:

- `Adaptive Traffic Camouflage Worae 2026 event inference`
- `Network Traffic Shaping for Enhancing Privacy in IoT Systems event timing deadline`
- `Balancing Timeliness and Privacy in Discrete-Time Updating Systems arxiv`
- `Age of Actuated Information edge action freshness 2026`
- `palmprint contactless open set identification transaction quality retry failure to acquire paper 2024 2025 pdf`
- `palmprint mobile payment end-to-end 1:N identification presentation attack ROI evaluation`
- `palmprint identification gallery size open set threshold quality`
- `X-Palm cross domain palmprint 2026`
- `palmprint physical print replay RGB NIR PAD 2026`
- `biometric multiple attempts retry false match correlation identification transaction`
- `Bob Zhang palmprint ROI VIS NIR verification DOI`

Primary full-text access was obtained for the arXiv HTML sources listed above. The ACM `DPShaping` full text, the complete Bob Zhang direct-neighbor papers, and the full WIFS 2009 text were not all available in this pass. Those gaps prevent a global or exact-claim novelty statement; they do not rescue a candidate already defeated by its direct baseline. Search absence is not evidence of novelty.

## Decision

**PIVOT.** No newest direction is promoted. `STALE-ACT`, generic Palm admission/retry/ROI/PAD, and runtime/transaction hygiene are killed as positive thesis mechanisms. `TRIG-LEAK` is HOLD only as a cheap, owner-backed empirical privacy/deadline falsification gate. The Palm route should continue only through the required physical VIS MVP and stage-count trace; after that, the only defensible residual is a pre-registered apparatus-specific guide-versus-fixed-retake completion/time evaluation with honest uncertainty and a negative-result path. This is not yet a thesis claim and must be re-audited after actual transaction data and the missing direct papers are obtained.

PIVOT
