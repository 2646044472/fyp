# Divergence Packet: 2026-09-23 directions beyond the Palm residual gate

## Decision investigated

Can the FYP retain the user-confirmed Raspberry Pi 5 Palm Payment route while identifying 3-7 technically different, undergraduate-feasible research candidates that could become a defensible thesis after the Phase 1 executable is stable?

Decision at this round: **no candidate is promoted**. `VIS-GUIDE` remains the only candidate directly compatible with the current Palm Payment commitment, and only as a prospective physical evaluation. `AUDIT-GAP` is the strongest non-palm research lead, but it is an evaluation/boundary question until an exact-neighbor audit and a physical pilot succeed. `SPLIT-LEAK`, `PROBE-BOUND`, and `ENERGY-CONFIG` are useful collision or negative-result candidates, not presently thesis-ready mechanisms.

The Palm Payment route is preserved as the execution commitment: visible-light physical capture -> live ROI -> identifier-free open-set 1:N -> frozen simulated debit and log. The route itself is engineering; none of the candidates below treats the MVP or Raspberry Pi deployment as novelty.

## Search boundary

Local evidence and role instructions read on 2026-09-23:

- `AGENTS.md`, `research/ops/agent-divergence.md`;
- `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`;
- newest relevant packets: `research/ops/divergence/2026-09-23-palm-direction-next-gate-divergence.md`, `2026-09-23-cross-mechanism-edge-decisions.md`, `2026-09-23-palm-dataset-feasibility-boundaries.md`, `2026-09-23-staged-palm-transaction-questions.md`;
- newest validations: `research/ops/validation/2026-09-23-palm-residual-direction-audit.md`, `2026-09-23-trig-leak-stale-act-validation.md`, `2026-09-23-post-demo-palm-security-validation.md`, and `2026-09-23-prf-tr-audit.md`.

External primary-paper searches on 2026-09-23 used arXiv API/HTML and official publisher or author pages. Queries included:

- `active verifier audit adaptive sensing missed event independent reference trace edge sensor 2024 2025 2026`;
- `dynamic sampling uncertainty edge sensor independent reference event coverage 2025`;
- `split inference feature inversion token shuffling reduction privacy 2025 2026`;
- `online conformal state probing edge action probe missed query error 2026`;
- `energy-aware inference resource-constrained device latency power Raspberry Pi 2025`;
- `palmprint live guided acquisition recapture mobile payment completion time`.

The search boundary is sampled, not exhaustive. Search absence is not evidence of novelty. Claims below are limited to inspected sources and the stated observation/action/endpoints.

## Recent-paper limitation map

| Family | Primary work inspected | Limitation or collision relevant to this round |
| --- | --- | --- |
| Palm acquisition and sequential decisions | Palm-ID, arXiv:2401.08111v1, Secs. II-F/G, III-B-D, IV-A/B, V; NIST IR 7544, Secs. 2.1.1-2.1.3 and 4-6; Murakami/Takahashi WIFS 2009, Secs. 2-4; local residual audit | Generic ROI, quality rejection/recapture, open-set search and score-history accept/reject/continue are occupied. A one-prompt/one-retake effect on all-start physical completion and time is still a finite causal evaluation, not a new sequential policy. |
| Adaptive sensing | Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, Secs. II-A/B and III, pp. 3-6; Han et al., IEEE TSM 2025, Sec. IV-C, pp. 6-7 | Dynamic sampling and uncertainty-driven expensive measurement are occupied. The residual candidate must require an independently recorded original-time reference, episode-level missed-event endpoint, matched verifier cost and held-out physical conditions. |
| Split-inference privacy | Leggio et al., *Position Matters*, arXiv:2609.01232v3 (2026-09-17), Secs. 2-5 and 7; Li et al., arXiv:2608.01148v1 (2026-08-02), Secs. 3-6 | Token shuffling/reduction, feature inversion and adaptive privacy-preserving split placement are direct neighbors. A Pi demo that transmits activations or masks tokens is not a contribution; only a bounded, application-specific leakage audit could survive. |
| Risk-aware probing | Talli, Popovski & Simeone, *Risk-Aware Online Conformal State Probing*, arXiv:2609.25889v1 (2026-09-22), Secs. 1-4 | The exact generic action-versus-probe problem, missed-query error (MQE), probing-rate tradeoff and online conformal policy are now directly occupied. A tabletop state-probe implementation would reproduce the mechanism. Its simulations do, however, provide a sharp negative/identification comparator. |
| Edge energy/latency tuning | Xu et al., *Camel*, arXiv:2508.09173v1 (2025-08-07), Abstract, Introduction and Sections `Camel Design`/`Implementation and Evaluation`; local EdgeServing/SneakPeek audits | MAB selection of frequency/batch configurations for energy-delay tradeoff is occupied. Replacing Jetson/LLM with Pi/palm or a different model is not an exact CS distinction. Only an application-level action endpoint with fixed quality and energy accounting could remain, and that is currently unverified. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| **VIS-GUIDE** (Palm, conditional) | An enrolled user presents a palm to a local mock-payment terminal. A capture/ROI failure causes delay or abandonment; an over-permissive retry could produce a wrong mock action. | On the frozen physical payment executable, prospectively assigned one prompt plus at most one retake changes all-start enrolled correct completion and capture-to-terminal p95 beyond fixed guide, fixed quality/margin retake and conservative unknown controls at matched capture cost. Report unknown-person wrong commits with exact counts/bounds, not superiority claims. | Palm-ID quality recapture; NIST IR 7544 acquisition controls; Murakami/Takahashi sequential open-set decisions; Bob Zhang CROI abstract is a direct ROI lead but full method remains [GAP]. | Kill if ROI/fixture/exposure repair dominates, fixed retake matches, prompt assignment is not feasible, or all-start person/session counts are insufficient. Replay-only data cannot estimate the prompt counterfactual. | Uses the committed MVP hardware and can be small after consent/ethics. It is likely a local evaluation paper, not a new policy. |
| **AUDIT-GAP** (outside palm; conditional negative/boundary result) | A low-cost edge monitor may skip expensive verification to save energy, yet a short threshold excursion during a blind interval can create a false `no event` record and trigger a bad maintenance decision. | Given an independently recorded full-support reference trace, compare adaptive sentinel/uncertainty-triggered verifier audits against periodic, uniform-random and always-on controls at matched verifier-on cost. Claim only a held-out frontier of missed excursion duration, decision latency and energy; include `unknown` when the trace cannot certify absence. | iAirGuard dynamic sampling; Han et al. uncertainty-driven virtual-metrology sampling. Distinction is independent original-time reference, episode coverage and action endpoint, not “adaptive sampling.” | Kill if periodic sampling matches at equal cost, the reference trace is not independent, or an adversarial short excursion is unobservable under all permitted policies. A useful result may be a blind-interval impossibility/bound rather than a better sampler. | Cheap Pi/MCU plus temperature/light/gas-like benign signal and wired reference logger. Requires a clean event-duration label and no safety/medical claim. Strongest non-palm lead, but exact-neighbor audit is still [GAP]. |
| **SPLIT-LEAK** (outside palm or later Palm privacy appendix; collision-heavy) | A camera or biometric edge device may offload intermediate features to a curious server. A visually private input could be reconstructed even when accuracy and bandwidth look acceptable. | For one frozen split model and a declared attacker, measure reconstruction leakage versus task utility, bytes and edge energy under position-aware inversion, token reduction, shuffling and a matched no-offload control. The contribution would be a finite application-specific audit protocol or null, not a new defense. | Leggio et al. SARA directly reconstructs position and missing tokens after token shuffling/reduction (Secs. 2-5); Li et al. adapt split points under encrypted collaboration (Secs. 3-6). | Kill as a method if SARA or a simpler inversion reproduces the result, if no genuine split deployment exists, or if the endpoint is only image similarity without a concrete confidentiality owner. | Requires a split model, remote endpoint, attack implementation and privacy/biometric governance. Current Palm executable is local and does not establish a split-inference need. |
| **PROBE-BOUND** (outside palm; negative-result candidate) | A disconnected edge node must decide whether to act on a predicted state or spend energy to probe; a wrong action is costlier than a delayed one. | Test whether a claimed local proxy (age, confidence or cheap sentinel) can distinguish two physical worlds that have identical proxy histories but opposite action-optimal states. If not, document the indistinguishability region and compare against direct probe, age threshold and always-probe controls. | Talli et al. OCSP directly defines action/probe policies, MQE and probing rate (Secs. 1-4). Earlier local STALE-ACT audit shows direct execution-time read is the honest baseline. | Kill any positive proxy claim if direct probe is available at comparable cost, if the proxy adds no conditional information beyond age, or if paired worlds cannot be independently generated. Promote only the negative boundary if it is repeatable and the restriction is real. | Very feasible with an MCU/LED or benign tabletop state machine, but its positive mechanism is already occupied and its story needs a real user/constraint. |
| **ENERGY-CONFIG** (outside palm; engineering/negative control) | A local terminal must meet a response deadline without wasting energy on every capture or inference. A poor operating point causes slow checkout or battery/thermal budget failure. | Under a frozen application-quality constraint, measure the Pareto frontier of CPU frequency, batch/queue policy and model path for end-to-end action latency, joules and completion. Only a result showing application-level action differences beyond component profiling could support a thesis. | Camel MAB frequency/batch tuning; SneakPeek and EdgeServing model/batch/exit scheduling; local S-SELECT validation. | Kill if fixed best configuration or standard DVFS/queue controls match; kill if energy is not measured at the application boundary; kill if “Pi implementation” is the only distinction. | Easy to measure only with a power instrument and stable workload. The current Palm route has no verified instrument or need, so retain as a deployment report. |

## Top two formalizations

### 1. VIS-GUIDE

- **[D] Decision:** Given an eligible physical presentation on the frozen payment executable, choose `accept`, `one prompted retake`, or `unknown`.
- **[A] Assumptions:** Person/session consent; camera, ROI, matcher, gallery, threshold and action semantics frozen; prompt assignment randomized or counterbalanced before observing outcome; all-start denominator retained; unknown-person probes are separately labelled; repeated frames are clustered by person/session.
- **[T] Target:** Estimate the difference in all-start correct enrolled completion and capture-to-terminal p95 at equal maximum attempts, with wrong mock commits reported as counts and uncertainty bounds. The prompt must be compared with fixed guide, quality/margin retake and conservative unknown.
- **Observable outcome:** Stage-linked capture/ROI/matcher/action trace, completion, p50/p95 elapsed time, and per-person/session failure counts.
- **Counterexample:** The prompt appears helpful only because it changes background, camera exposure or ROI; after freezing those, fixed retake matches it. Or all observed rejections are ROI failures, making prompt policy irrelevant.
- **Negative-result value:** A reproducible null localizes the remaining usability problem to fixture/ROI or shows that physical guidance adds no measurable value. It does not support a payment-security claim.

### 2. AUDIT-GAP

- **[D] Decision:** At each time step, choose `cheap sentinel only`, `full verifier`, or `unknown/retain audit` under a verifier-energy budget.
- **[A] Assumptions:** An independently clocked full-support reference trace records the target signal continuously or at a resolution finer than the shortest event of interest; policy sees only the permitted cheap observation until it elects verification; event windows and costs are preregistered.
- **[T] Target:** Compare missed excursion duration, false `no event`, detection latency, verifier energy and unknown rate at equal verifier-on fraction across adaptive, periodic, random and always-on controls, on held-out pulse duration/placement/drift cells.
- **Observable outcome:** Reference-labelled event intervals, policy-visible trace, action, verifier invocation, energy and latency.
- **Counterexample:** A short excursion and a stable trace produce the same sentinel history until the verifier is invoked. No policy using only that history can certify absence; the honest result is an unknown or a maximum blind-interval bound.
- **Negative-result value:** It can close a tempting adaptive-sampling story with a physical identifiability result and a simple periodic baseline, while still yielding a publishable-quality benchmark only if the exact protocol survives direct-neighbor validation.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| The committed Palm route is a VIS physical capture, live ROI, identifier-free open-set 1:N and logged simulated debit; later NIR/PAD are gated. | [K] | Local `minutes/09-13-palm-payment-roadmap-update.md`, 2026-09-13 | Decision and Phase 1-4 sections | User/project decision, not literature evidence. |
| Palm mobile ROI, quality recapture and open-set 1:N are established components. | [K] | Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Secs. II-F/G, III-B-D, IV-A/B, V | Does not establish the exact Pi physical prompt endpoint. |
| Acquisition controls and sequential biometric accept/reject/continue are established. | [K] | NIST IR 7544 (2008), https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf; Murakami & Takahashi, WIFS 2009, https://doi.org/10.1109/WIFS.2009.5386482 | NIST Secs. 2.1.1-2.1.3, 4-6; WIFS Secs. 2-4 | The WIFS full-paper read is recorded in the 2026-09-23 validation packet. |
| Dynamic sampling and local prediction/fault logic are already used in a low-cost edge sensing system. | [K] | Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, DOI 10.1109/COMSNETS67989.2026.11418151, 2026-03-23, https://cse.iitm.ac.in/~cs25d002/assets/iairguard_paper.pdf | Sec. II-A/B, pp. 3-4; Sec. III, pp. 4-6 | Its endpoint is mainly data/storage/transmission reduction; exact independent-reference protocol remains [GAP]. |
| Uncertainty-driven dynamic sampling can degenerate when too few samples remain. | [K] | Han et al., IEEE TSM 38(2), 2025, DOI 10.1109/TSM.2025.3531920, https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958452 | Sec. IV-C, pp. 6-7 | Semiconductor virtual metrology domain; mechanism collision, not exact event-coverage endpoint. |
| Position-aware inversion attacks can recover information after token shuffling/reduction in ViT split inference. | [K] | Leggio et al., *Position Matters*, arXiv:2609.01232v3, 2026-09-17, https://arxiv.org/html/2609.01232v3 | Secs. 2-5 and Sec. 7 | Directly lowers the novelty of a generic split-privacy method; current Palm system has no split deployment. |
| Adaptive encrypted split placement already jointly models end/edge/cloud latency and privacy. | [K] | Li et al., *Latency-Optimal Adaptive Split Inference*, arXiv:2608.01148v1, 2026-08-02, https://arxiv.org/html/2608.01148v1 | Secs. 3-6 | FHE/CNN setting; supports collision pressure, not an exact application claim. |
| Risk-aware online action/probe policy with MQE and probing-rate control is directly formulated. | [KILL] | Talli, Popovski & Simeone, *Risk-Aware Online Conformal State Probing*, arXiv:2609.25889v1, 2026-09-22, https://arxiv.org/html/2609.25889v1 | Abstract; Sec. 1; Sec. 2 system model; Sec. 3 OCSP; Sec. 4 experiments | Numerical simulations and arbitrary state predictors; a Pi tabletop implementation would reproduce the generic mechanism. |
| Energy-delay configuration search over frequency and batch size is already formulated as a bandit framework on an edge device. | [K] | Xu et al., *Camel*, arXiv:2508.09173v1, 2025-08-07, https://arxiv.org/html/2508.09173v1 | Abstract; Introduction; `Camel Design Problem Formulation`; `Implementation and Evaluation` | Jetson/LLM rather than Pi/palm; still kills a generic configuration-search claim. |
| A two-world identical-proxy construction defeats any claim that a proxy alone certifies current state. | [C] | Formal construction in this packet; related local validation `research/ops/validation/2026-09-23-trig-leak-stale-act-validation.md` | Candidate formalizations and paired-world audit | Applies only to the stated observation model and action restriction; not a universal impossibility theorem. |

## Queries and failed searches

The queries are listed in **Search boundary**. Additional exact-ID retrievals were performed for arXiv `2609.25889v1`, `2609.01232v3`, `2608.01148v1`, and `2508.09173v1`, using official arXiv HTML and PDF endpoints. The arXiv query for `edge computing` plus `abstention` returned no exact records, so broader terms (`probe`, `active data acquisition`, `risk-aware`, `split inference privacy`) were used.

Unresolved searches and uncertainties:

- [GAP] No exhaustive forward-citation audit was completed for `VIS-GUIDE`, especially the full Bob Zhang CROI paper and the 2015 mobile guided-capture record.
- [GAP] No exact primary paper was verified for the `AUDIT-GAP` combination of independent full-support reference, adaptive verifier audit, episode-level false-no-event endpoint and matched physical cost. This is not novelty evidence.
- [GAP] The actual Palm Payment executable still lacks the all-start stage-count trace, authorized person/session roster and confirmed deployment manifest.
- [GAP] `SPLIT-LEAK` lacks a real confidentiality owner and current system split point; no biometric template/privacy claim is permitted from the present local-only app.
- [GAP] `AUDIT-GAP` hardware, energy instrument, event generator and reference-clock resolution are not confirmed.
- [GAP] No new Bob Zhang paper chain was inspected beyond the local packets' abstract/list references; advisor adjacency must not be used as a novelty argument.

## Pareto comparison

- `VIS-GUIDE`: best fit to the committed route and lowest new hardware cost; weakest technical novelty and dependent on a stable live executable.
- `AUDIT-GAP`: strongest distinct observation/action endpoint and useful negative-result path; requires an independent reference and exact-neighbor validation, and has no current user workflow owner.
- `SPLIT-LEAK`: meaningful privacy story but direct SARA collision and absent current split architecture make it a poor primary FYP direction.
- `PROBE-BOUND`: excellent falsification clarity and low hardware cost, but the positive mechanism is occupied by OCSP and the negative result needs a real constrained workflow.
- `ENERGY-CONFIG`: easy deployment measurement but likely engineering/profiling; no thesis claim until a downstream action endpoint survives fixed controls.

## Decision

**HOLD.** Keep Palm Payment as the current execution commitment. After the Phase 1 trace exists, test `VIS-GUIDE` only as a prospective, counterbalanced physical completion/time evaluation. In parallel, the only non-palm candidate worth a validation packet is `AUDIT-GAP`, framed as an independently labelled reliability boundary experiment rather than a new adaptive sampler. Treat `SPLIT-LEAK` and `ENERGY-CONFIG` as collision/engineering controls, and `PROBE-BOUND` as a negative-result comparator unless a real action restriction is documented.

HOLD
