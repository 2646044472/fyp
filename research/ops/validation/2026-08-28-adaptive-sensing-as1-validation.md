# Validation Audit: 2026-08-28 AS1 audited adaptive sensing

## Decision investigated

Whether AS1 can replace the locked C3 direction as a one-year FYP: a low-cost edge monitor observes a cheap sentinel and decides `verify / skip`; under a fixed verifier-on budget, a frozen adaptive policy is evaluated against equal-cost periodic, uniform-random, and change/uncertainty-only policies using a separately recorded original-time reference trace.  The intended operational endpoint is `event / no-event / unknown` for threshold excursions, not a new sensing algorithm.

The confirmed schedule is a runnable benign benchtop demonstration by 2026-12 and full experiment/optimization in 2027-H1.  Affordable hardware may be self-purchased; no human subjects, production monitoring, or safety actuation are allowed.  These are scope constraints, not evidence of research distinction.

## Claim under test

**Only permitted AS1 claim.**  For a preregistered finite family of pulse, placement, and drift conditions, does a frozen adaptive verifier-audit policy produce a better held-out frontier of missed-excursion duration, decision latency, verifier energy/storage, and false `no-event`/`unknown` burden than budget-matched periodic, uniform-random, and sentinel-change/uncertainty-only policies?

AS1 may not claim a new adaptive sampler, a general event-detection guarantee, that adaptive sensing is generally better than periodic sensing, or that a reference trace removes all measurement error.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | `e-Sampling` already adjusts sensing rate from locally acquired signal content for event-aware, resource-constrained monitoring. AAS already switches between sparse and higher-rate acquisition to sense critical events under an energy objective. iAirGuard already combines low-cost ESP32 environmental sensing, mean/variance-controlled dynamic sampling, secondary sensing, and an energy/storage comparison. Lu et al. 2026 combine sparse uncertainty-driven sampling, continuously sampled sentinels, event-triggered wake-up, event metrics, and cost. | AS1 does not introduce their mechanisms. It proposes an independent physical reference plus a tri-state reporting/equal-verifier-budget protocol. | **Red** for any mechanism claim; **Amber** only for the narrow protocol distinction. |
| 2. Exact-claim collision | Lu et al. evaluate event-level detection, onset delay, anomaly-window coverage, sampling rate, and energy under sentinel-assisted adaptive sampling. Chatterjea and Havinga explicitly study temporal coverage, event-detection delay, and randomized schedules for energy-efficient environmental WSN sampling. AAS explicitly frames critical-event timeliness versus energy. | In the inspected works, I did not find all of: a separately powered original-time reference logger, a predeclared held-out physical condition, matched verifier-on rather than generic sample-cost accounting, and an explicit `no-event / unknown` operational endpoint. Absence from these papers is not evidence of a globally open gap. | **Amber/weak**: the remaining difference is evaluation hygiene plus a narrow endpoint, not a new system task. |
| 3. Boundary / impossibility | StableSENS states that, if event timing is independent of the sampling process and sample count is fixed, increasing inter-sample-interval variance raises miss probability; constant periodic sampling maximizes event-detection probability in that model. With no verifier observation in an interval, a no-excursion world and a short excursion that begins and ends in the interval can produce identical sentinel-visible traces. Selective-label work independently establishes the general evaluation problem when outcomes are observed only following decisions. | Adaptation can only improve on periodic sampling if a prevalidated sentinel carries predictive information about future verifier events, or a declared physical event model invalidates the independence condition. That relation must be tested before the held-out comparison and cannot be inferred from the result. | **High** for the conditional counterexample; it rules out any universal or unqualified AS1 claim. |

## Assumption and identification audit

### Observation model

Let `S_t` be the cheap sentinel, `V_t` the expensive verifier, and `A_t in {verify, skip}` the policy action.  `V_t` is unavailable whenever `A_t = skip`.  If the policy emits `no-event` over an interval with no `V_t`, then the following two physical trajectories are observationally equivalent to it:

- `W0`: the target never crosses the threshold;
- `W1`: the target crosses and returns between two verifier observations while `S_t` follows the same trace in both worlds.

[K] Therefore AS1 cannot truthfully turn every skipped interval into `no-event` from the stated observations alone.  It needs one of: (a) `unknown`, (b) a fixed maximum verifier gap that is explicitly weaker than a no-event assertion, or (c) a separately justified physical relation from the sentinel to the verifier event.  This is a direct finite counterexample, not a claimed new impossibility theorem.

### Independent reference does not automatically create labels

[KILL] A second logger is not an original-time truth instrument merely because it samples continuously.  To label a pulse it must have a clock relation to the policy log, known response/inclusion time, a calibration/uncertainty envelope around the threshold, and independence from the failure injected into the verifier.  A thermal or gas reference with different lag can disagree on event onset even when neither device is faulty.  The present AS1 packet specifies none of these.  The continuous reference can evaluate the policy offline; it does not grant the online policy information it did not observe.

[K] Lakkaraju et al. show the core selective-label issue: outcome observations created by a prior decision are not representative of all cases.  Its KDD 2017 setting is not an AS1 sensor-system neighbor, but it supports the diagnosis that evaluating only `verify` intervals is biased.  Logging a full-rate reference removes that *evaluation* selection problem only if the reference is valid; it does not itself make AS1 a new algorithmic contribution.

### Simple-baseline boundary

[K] Loreti, Bracciale, and Bianchi derive the relevant counterexample for sporadic events independent of the schedule: at the same number of samples, zero-variance periodic intervals maximize detection probability, because variable intervals increase the residual unobserved time.  AS1 must include a deterministic maximum-gap periodic schedule at each verifier budget and randomize its initial phase across repetitions.  Reporting only average period or a hand-picked periodic phase would be inadequate.

[KILL] If AS1 deliberately constructs pulses preceded by an informative sentinel change, its positive result establishes only that designed relationship.  If it uses uncorrelated or abrupt pulses, periodic may dominate by the StableSENS condition.  Either choice leaves no broad adaptive-sensing claim.  The discriminating prerequisite is an independently measured, source-only association between pre-event sentinel history and future verifier event on source conditions, frozen before target evaluation.  This prerequisite is currently [GAP].

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Lu et al., *Adaptive Sampling for Spatiotemporal Anomaly Monitoring in WSNs*, arXiv:2607.15235v1, submitted 2026-07-16; marked accepted IEEE ISSC 2026 | Uncertainty-driven sparse sampling; continuously sampled sentinel nodes; sentinel GLR triggers neighbor wake-up and recovery control. | Injected temperature anomalies in the Intel Berkeley trace; event-detection rate, onset delay, coverage, anomaly-window sampling ratio, global sampling rate, energy. | Very high component and endpoint overlap: sentinel-assisted adaptive allocation under cost with event visibility and latency. | [KILL] It eliminates a thesis framed as sentinel-triggered adaptive sampling for better event coverage/cost. Its Sec. IV limitation is injected data anomalies rather than physical drift/faults; it does **not** establish an exact collision with AS1's independent-reference tri-state protocol. |
| Rao et al., *Adaptive Data Acquisition with Energy Efficiency and Critical-Sensing Guarantee for WSNs*, Sensors 19(12):2654, 2019 | Adaptive switching between compressed/sparse and prediction-based data gathering; adaptive tolerance. | Timely critical-event acquisition and energy/data reduction on a realistic trace. | The energy-versus-critical-event-timeliness task is occupied. | [KILL] It eliminates generic “adaptive rate detects critical events while saving energy.” It leaves only AS1's auditing/label endpoint uninspected. |
| Bhuiyan et al., *e-Sampling*, ACM TAAS 12(1), Art. 1, March 2017 | Nodes adapt rate and intervals from signal frequency, then make decentralized event indications. | High-rate structural-health/fire-event settings; rate, indication, data/energy reduction. | Local event-sensitive adaptive rate control with a low-cost/resource story. | [KILL] It eliminates the claim that local event-sensitive adaptation itself is a new edge mechanism. Sec. 2.2 also records the known difficulty: short physical events may occur before rate adaptation. |
| Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, DOI 10.1109/COMSNETS67989.2026.11418151 | ESP32-S3 environmental sensor node; mean/variance dynamic interval; TinyML secondary sensing/fault score. | Kitchen/office/outdoor comparison of continuous versus adaptive sensing; storage/transmission and reliability claims. | Same low-cost environmental-monitoring story plus dynamic sampling and secondary sensing. | [KILL] It eliminates an AS1 story built around a cheap adaptive air/environment monitor, uncertainty/variation trigger, and drift/fault addition. Its Sec. III comparison is not an independent-reference, budget-matched event-coverage study. |
| Chatterjea and Havinga, *Improving Temporal Coverage of an Energy-Efficient Data Extraction Algorithm for Environmental Monitoring Using WSNs*, Sensors 9(6):4941-4954, 2009 | Adaptive sampling plus randomized staggered sampling across correlated nodes. | Temporal coverage, delay from event to detection, and energy using a Great Barrier Reef deployment trace. | Event delay/coverage and randomized schedules under energy constraints. | It weakens the claim that temporal coverage or periodic/random comparison is a newly discovered endpoint. It does not contain AS1's verifier/reference split. |
| Loreti et al., *StableSENS*, IEEE Internet of Things Journal 6(6):9908-9918, 2019 | Sampling-period controller for energy-harvesting IoT sensing. | Sampling-rate stability/continuity; explicit analysis of event miss under equal sample count. | The equal-budget event-observability baseline is directly relevant. | [KILL] Under its stated independence condition, a fixed periodic schedule is the strongest simple baseline and variable/adaptive timing is disadvantaged. |
| Han et al., *A Comparative Study of Semiconductor Virtual Metrology Methods and Novel Algorithmic Framework for Dynamic Sampling*, IEEE TSM 38(2), May 2025 | Uncertainty-triggered expensive physical metrology versus fixed/random sampling. | Metrology load and model performance under drift/shift on a public CMP dataset. | Direct collision for “sample costly verifier only when uncertainty is high.” | [KILL] It eliminates uncertainty-triggered verifier acquisition as a contribution. Different domain and endpoint leave physical event coverage, but not the sampling mechanism. |

## Strongest simple baseline

**Budget-matched periodic maximum-gap verifier schedule.**  At verifier duty budget `b`, sample every `Delta(b)` time units with the same powered-on duration and storage accounting as AS1; rotate the initial phase across replicate runs; emit `event` only from a verifier-supported threshold crossing and emit `unknown` whenever the declared coverage contract is not met.  It has no model-training data, no uncertainty calibration, no selective-label mechanism, and a transparent worst blind gap.

The AS1 adaptive policy is killed if this schedule matches its held-out frontier.  If an adaptive policy exceeds it only for hand-designed, sentinel-predictable pulses, the conclusion must be limited to that finite pulse/sentinel relationship.  `Uniform random`, `sentinel-only`, and `always-on` remain necessary additional controls, but periodic maximum-gap is the primary adversarial baseline.

## Contrarian result

AS1's advertised positive effect has two incompatible regimes.  With pulse timing independent of the cheap sentinel, the periodic schedule's equal spacing is favored by the known inspection-paradox argument.  With pulse timing predictable from the sentinel, the policy can win, but the experiment may merely re-demonstrate a designed trigger correlation already assumed by the testbed.  The independent reference corrects selective evaluation but does not resolve this causal problem.

The newer Lu et al. 2026 work additionally occupies the more compelling systems story: continuous sentinels trigger denser sampling to improve event-window visibility at lower cost.  AS1's residual tri-state/reference protocol is valuable experimental hygiene, but currently too narrow to carry an FYP research contribution by itself.

## Feasibility audit

| Requirement | Status | Audit result |
| --- | --- | --- |
| 2026-12 runnable demo | [C] feasible | An SBC/ESP32 class controller, a cheap sentinel, a duty-cycled verifier, and a non-hazardous controlled light or thermal pulse source are technically modest. A demo can show logs, actions, and budget accounting. This does not demonstrate research novelty. |
| 2027-H1 experimental study | [GAP] | Feasible only after a calibration protocol, original-time event generator/log, reference-clock bound, independent reference failure analysis, and frozen physical source/target cells exist. Those tasks are substantial but fit six months if the hardware is decided immediately. |
| Labels | [KILL] currently unsupported | “Separately powered continuous logger” is insufficiently specified. Need source-controlled event timestamps or a validated continuous instrument, threshold hysteresis, response latency/inclusion-time characterization, and an audit trail proving reference data stayed available. |
| Hardware/energy | [GAP] | No exact verifier, sentinel, board, power instrument, power state, or measurement interval has been selected. Existing papers' data/storage proxies cannot substitute for this BOM. Compare measured verifier-on energy, not only CPU/packet counts. |
| Ethics/safety | [C] feasible if bounded | Use a closed benign light or thermal apparatus; prohibit people, personal data, exposure claims, and real safety/control decisions. An occupancy, health, air-quality, or fire narrative would introduce label, permission, and harm claims not supported by the minimum setup. |
| Compute/data | [C] feasible | A frozen finite rule family and CSV logs need no GPU or external data. Any learning/uncertainty model adds source-data and calibration burden and collides with Han et al. and Lu et al. |
| Story | [GAP] weak | “A facility monitor decides whether to take an expensive verification sample” is understandable, but ordinary periodic inspection is already defensible and may be preferred. No verified stakeholder or operational cost makes marginal adaptive improvement consequential. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| A 2026 paper combines continuously sampled sentinel nodes, uncertainty-driven sparse sampling, local wake-up, event detection/coverage/delay, and cost. | [K] | Lu, Sun, Jiang, Butler, arXiv:2607.15235v1, submitted 2026-07-16; https://arxiv.org/abs/2607.15235 | Sec. I, esp. pp. 1-2; Sec. IV-B/C, pp. 6-8; Sec. V, p. 8. | Accepted-paper status is stated by arXiv; experiments use injected anomalies in a public temperature trace, not a physical independent verifier. |
| Lu et al. report a limitation to injected anomalies and call for real labelled traces/deployment-like disturbances. | [K] | Same as above | Sec. IV-C/V, p. 8. | This limitation leaves a deployment validation gap, not a license to claim AS1 novel. |
| Dynamic low-cost environmental sampling with an ESP32-S3, secondary sensing, storage/transmission reduction, and a continuous-versus-adaptive deployment comparison is already published. | [K] | Mondal et al., COMSNETS SysAI 2026, DOI 10.1109/COMSNETS67989.2026.11418151, PDF timestamp 2026-03-23: https://cse.iitm.ac.in/~cs25d002/assets/iairguard_paper.pdf | Abstract p. 1397; Sec. I-A and II-A/B, pp. 1398-1400; Sec. III, pp. 1401-1402. | Its own text admits single-node/environmental-interference limitations; it does not validate AS1's exact endpoint. |
| Costly physical metrology selected by predictive uncertainty is compared with fixed/random sampling under drift/shift. | [K] | Han et al., IEEE TSM 38(2), May 2025, DOI 10.1109/TSM.2025.3531920; official NIST PDF: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958452 | Sec. I, pp. 232-233; Sec. III-C, pp. 236-237; Sec. IV-C, pp. 238-239. | Different semiconductor task. It is a mechanism collision, not an exact physical-event collision. |
| Adaptive switching is already proposed for energy efficiency and timely critical-event acquisition. | [K] | Rao et al., Sensors 19(12):2654, 2019, DOI 10.3390/s19122654: https://doi.org/10.3390/s19122654 | Abstract; Sec. 1; Sec. 4.3 (publisher HTML inspected 2026-08-28). | Public trace evaluation; no independent verifier/reference endpoint found in inspected text. |
| Event-sensitive local adaptive sampling and decentralized event indication are established. | [K] | Bhuiyan et al., ACM TAAS 12(1), Article 1, March 2017, DOI 10.1145/2994150; author PDF: https://cis.temple.edu/~wu/research/publications/Publication_files/Bhuiyan_ACM_2017.pdf | Sec. 2.1-2.2, pp. 1:4-1:6; Algorithms/Sections 4-6, pp. 1:11-1:17; results pp. 1:23-1:27. | Kills a mechanism claim, not AS1's reference protocol. |
| A randomized schedule was already proposed to reduce temporal coverage delay under adaptive sampling in environmental WSNs. | [K] | Chatterjea and Havinga, Sensors 9(6):4941-4954, 2009, DOI 10.3390/s90604941: https://doi.org/10.3390/s90604941 | Abstract; Sec. 5, pp. 4949-4952 (official index/PubMed record inspected). | Uses correlated nodes and deployment data; not AS1's two-fidelity verifier setup. |
| With schedule-independent events and equal sample count, constant intervals maximize event detection; variable intervals increase missed-event risk. | [K] | Loreti, Bracciale, Bianchi, *StableSENS*, IEEE IoT J. 6(6):9908-9918, 2019, DOI 10.1109/JIOT.2019.2933335: https://doi.org/10.1109/JIOT.2019.2933335 | Sec. I, p. 2, especially Fig. 1 and its stated residual-lifetime argument. | Conditional on event/schedule independence; not a universal dominance theorem for informative sentinels. |
| Sampling-controlled sequential change detection already formalizes detection delay, false alarms, and observation cost. | [K] | Zhang and Mei, *Bandit Change-Point Detection for Real-Time Monitoring High-Dimensional Data Under Sampling Control*, Technometrics 65(1):33-43, 2023, DOI 10.1080/00401706.2022.2054861: https://pmc.ncbi.nlm.nih.gov/articles/PMC10027391/ | Abstract and Sec. 1, p. 34; Sec. 3.1, pp. 36-37; Sec. 4, p. 39. | Different multi-stream statistical model; supports the claim that the AS1 trade-off family is established. |
| Outcome labels restricted by prior decisions are selectively labeled and nonrepresentative. | [K] | Lakkaraju et al., KDD 2017, pp. 275-284, DOI 10.1145/3097983.3098066; author PDF: https://www.cs.cornell.edu/home/kleinber/kdd17-selective.pdf | Abstract and Sec. 1, p. 275; Sec. 4, pp. 278-280. | Conceptual evaluation support only; not a sensing-system neighbor or an AS1 contribution. |
| No inspected primary work exactly matches AS1's independent physical reference + equal verifier-on budget + tri-state endpoint + held-out physical cell. | [GAP] | Queries and source chain below; direct works above. | N/A | Failed retrieval is not a novelty result. The remaining difference may be too small for a thesis even if it survives exact-collision search. |

## Queries and failed searches

Searches run on 2026-08-28:

- `adaptive sampling event detection sensor network periodic random baseline missed events`
- `adaptive sensing periodic random sampling sensor events energy detection paper`
- `adaptive sensor scheduling independent reference trace selective labels evaluation paper`
- `adaptive sampling sensor drift uncertainty random sampling paper`
- `independent reference adaptive sampling sensor monitoring`
- `missed event duration adaptive sampling sensors`
- `maximum sampling interval adaptive sampling event detection energy sensor`
- `selective labels active sensing evaluation independent ground truth sensor`
- `adaptive sensor trigger expensive verifier periodic sampling event detection edge camera sentinel study 2024 2025`
- `two tier sensor adaptive sampling expensive sensor cheap sentinel event detection paper`
- `adaptive sensing cheap sensor expensive sensor event detection`
- `sensor scheduling event detection periodic maximum interval adaptive`
- `full-support audit adaptive sensing`
- `independent reference trace adaptive sampling`
- `unknown adaptive sampling event detection sensor`
- `false clear adaptive sensing sensor event`

Citation-chain pass: Lu et al. explicitly cite and compare against AAS and adapted e-Sampling (Sec. I/II/IV).  Its arXiv record is v1 submitted 2026-07-16 and says accepted IEEE ISSC 2026; a reliable later-citation count was not available from the inspected official record, so no absence-of-follow-up inference is made.  iAirGuard's direct system paper and Han et al.'s uncertainty/metrology paper were inspected independently rather than treated as search snippets.  No primary paper located by these queries established the exact AS1 protocol; this is recorded as [GAP], not a positive novelty finding.

## Decision

**PIVOT.**  Do not promote AS1 as an adaptive-sensing thesis or replace C3 with it.  Existing work already covers the central mechanism and event-cost story; the most recent direct neighbor, Lu et al. 2026, makes the collision especially strong.  The independent-reference, equal-budget, tri-state machinery should be retained only as a mandatory evaluation/provenance protocol for any future sensing candidate.

AS1 may return to HOLD only after a different gate is passed: identify a consequential benign physical task where (1) the cheap sentinel has a preregistered, independently measured predictive relation to future verifier events, (2) the reference/injection/timestamp contract makes false-clear labels auditable, and (3) the periodic maximum-gap baseline is not already adequate on held-out cells.  Without all three, the credible result is a small engineering demo rather than a defensible FYP claim.

PIVOT
