# Divergence Packet: 2026-09-23 cross-mechanism edge decisions

## Decision investigated

Can a one-year, low-cost, non-production edge FYP identify a falsifiable claim outside the killed palm, maintenance, calibration, storage, generic TTA and camera-decoder mechanisms? This divergence packet does not replace the conditional PRF-TR physical feasibility gate. Decision: two narrow hypotheses merit adversarial validation, but none is thesis-ready.

## Search boundary

Searched 2026-09-23 using arXiv API, OpenAlex, direct arXiv PDFs, local active files and earlier divergence packets. Families: privacy of traffic timing, task-age inference, deadline-constrained multi-model serving and verifiable execution. Read primary tasks, inputs, actions, methods, baselines, evaluation and limitations/future work. The ACM DPShaping PDF returned a challenge and is only a collision lead, never full-text evidence. No global novelty claim. Archive edge-sensing README was read for overlap, not promoted. All proposed scenes are synthetic/non-personal and non-safety. Distinctions must be observation/action/endpoint differences, not new boards or models.

## Recent-paper limitation map

| Family | Direct work inspected | Limitation and consequence |
| --- | --- | --- |
| Traffic privacy | Worae et al. 2026, arXiv:2609.25787v1, pp. 1-3, 5-10: previous-window causal padding/splitting/timing/no-change choice, budget-matched and defense-aware controls. Xiong et al. 2021, arXiv:2111.14992v1, pp. 4-7, 12-15: event-level DP traffic shaping with dummy bytes, queue delay and event-time/size privacy. | Worae principally tests closed-set device identity with a passive observer; defense-aware training recovers protection on two datasets (pp. 3, 10). Xiong discusses burst-event limits (p. 14). Generic adaptive camouflage or DP shaping is occupied. A specific trigger/deadline frontier may still be measured, but fixed-clock controls may dominate. |
| Semantic timeliness | Gan et al. 2025, arXiv:2504.07428v1, pp. 1-2, 4-5: resolution and SLM/LLM routing, SMDP threshold, simulation. Diao et al. 2025, arXiv:2503.08661v1, pp. 1-2, 4-6, 10-13: task JSCC and delay-aware control prediction in CARLA. | Routing by task-age and predicting delayed control are occupied. Neither proves a physical benign operator action, but putting a scheduler on Pi is not a difference. A narrower post-capture state-change endpoint needs direct-state and age-threshold baselines. |
| Serving/runtime | Wolfrath et al. 2025, arXiv:2505.06641v1, pp. 1-3, 7-12: SneakPeek chooses models/batches for accuracy-deadline utility. Cao et al. 2026, arXiv:2605.05527v1, pp. 1-2, 4-9: EdgeServing chooses models, exits, batches for SLOs on edge GPUs. | Device-side execution is mentioned as SneakPeek future work (p. 11), not proof of a gap. A generic scheduler or refusal wrapper likely reduces to reweighted utility and EDF. |
| Execution proof | Kiri et al. 2026, arXiv:2606.07470v1, pp. 1, 3-4, 9-10, 12, 14: VECODI verifies execution/model parameters on TrustZone-M against secure-world baseline. Maheri et al. 2025, arXiv:2506.20037v1, pp. 1-3: edge unlearning zk proof. | Correct computation on a declared input does not certify the truth of a physical source. This is an assurance boundary, but local CONTACT-EVIDENCE already reached a similar kill. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| TRIG-LEAK (traffic privacy; HOLD) | Lab operator sends a non-personal threshold notice. Passive LAN observer infers event occurrence/time from encrypted packet timing; deferral can miss the notice deadline. Actor chooses `send now / scheduled defer / cover-send`. | [C] With declared event process, deadline D and byte budget B, characterize minimum defense-aware attacker event-time advantage at bounded late-notice rate. A causal schedule might improve the privacy-deadline frontier over fixed clock and event-DP shaping. Inputs: event flag, queue age, deadline, budget. Action: packet schedule. Metric: attacker AUC/advantage at fixed P95 delivery and bytes. | Xiong 2021 event-DP; Worae 2026 causal camouflage; DPShaping 2025 full text [GAP]. Distinction is event-time and hard application deadline, not device identity or generic privacy. | Synthetic event trace plus local gateway; compare fixed periodic, constant-rate cover, Xiong-style shaping, Worae-style previous-window choice, all same budget; retrain attacker on defended traces. [KILL] Fixed clock dominates or deadline/bytes make privacy impossible. Pivot: bounded frontier and defense-aware benchmark. | Two commodity machines or replay, packet capture, no personal traffic. Need genuine confidentiality owner/threat model [GAP], networking/privacy advisor. |
| STALE-ACT (task freshness; HOLD) | Technician reviews a non-safety tabletop indicator. Capture-time inference was correct, but state changed before `execute`; wrong action repeats a benign test, while `reacquire/unknown` delays work. Disconnection makes remote correction late. | [C] Timestamp plus pre-action transition proxy yields lower wrong-action risk at equal capture/latency cost than age-only and confidence-only actions on a declared finite transition family. Inputs: capture/completion timestamps, proxy, inference and costs. Actions: `execute / reacquire / unknown`. Metric: wrong action and unknown at fixed joules/latency, independently logged state truth. | Gan 2025 task-age threshold; Diao 2025 delayed control; local WATERMARK-CLOSE is killed. Different endpoint only if current-state decision is independently witnessed. | MCU LED/state machine, randomized transitions, wired truth logger and delayed inference replay; compare direct latest-state read, fixed age, cost-aware age threshold, confidence, always reacquire. [KILL] Direct sample or fixed age dominates, or proxy does not identify change. Pivot: paired-world impossibility. | Cheap Pi/MCU/LED; no real actuation or people. Workflow harm/advisor interest [GAP]. |
| SLO-REFUSE (runtime; PIVOT/KILL-leaning) | Shared edge queue processes benign lab jobs. Overdue confident output can be worse than explicit refusal; too much refusal repeats work. Actor is local scheduler. | [C] Frozen asymmetric-loss `shallow / full / refuse` scheduler lowers wrong-on-time-action plus refusal cost over equally informed EDF/early-exit on held-out bursts. Inputs: queue, deadlines, calibrated profiles. Metric: weighted harm, deadline misses, refusals, energy. | SneakPeek 2025, EdgeServing 2026, local SLOW-CAP. | Trace replay against EDF+refuse, fixed shallow/full and their utility/exit/batch controls. [KILL] Utility reweighting or fixed cutoff matches complete frontier. Pivot: negative control for STALE-ACT. | Software cheap; comparable GPU and calibrated profiles [GAP]. Pi-only demo is not mechanism evidence. |
| PROOF-BOUND (security; KILL positive thesis) | Reviewer accepts a verifiably computed non-personal inspection output; invented physical input still causes false acceptance. Actions `accept / recheck`. | [C] Paired-world demonstration: same signed input and execution proof, different physical source state, opposite correct review action. Proof of computation cannot certify physical semantic truth. Metric: false accept versus recheck. | VECODI 2026, Maheri 2025, local CONTACT-EVIDENCE and CHAIN-REPLAY. | Signed/replayed-input pair, compared with hash, secure timestamp, challenge and independent second observation. [KILL] Standard threat-model distinction already gives result; no separate FYP. Pivot: assurance taxonomy/control. | Simulation sufficient, no TEE purchase. Source trust/adversary [GAP]. |

Bob Zhang adjacency for all four is only broad imperfect-observation and conservative-decision context. No claim extends a particular PAMI method; exact advisor-paper neighbor audit remains [GAP] before any promotion.

## Top two formalizations

### TRIG-LEAK

- **[D]** Episodic event E_t, hard deadline D, byte budget B. Passive attacker sees outbound times/sizes but not encrypted payload and trains on defended traces. Notice useful only by t+D.
- **[A]** Causal randomized `send / defer / cover` from local event and queue, with dummy, delay and drop cost charged. No future-event oracle.
- **[T]** Held-out event-time attacker advantage at matched late-notice rate and B against fixed periodic, constant-rate, event-DP and causal previous-window baselines. Outcome: non-dominated privacy-deadline point or none.
- **Counterexample / negative value:** One event window, D shorter than next cover slot, B too small for cover in every slot: a timely packet reveals the event. Derive only a bounded lower frontier under these assumptions; test whether traces approach it. Not a universal lower bound.

### STALE-ACT

- **[D]** Finite-state benign process may change after capture and before action. Wired reference timestamps transitions; wrong execute costs L_w, reacquisition costs time/energy, unknown costs a repeat. No safety claim.
- **[A]** Use timestamps and pre-action proxy for `execute / reacquire / unknown`; freeze policy on training cells.
- **[T]** Block transition/load patterns; measure wrong-action at matched capture/unknown budget versus direct latest-state read, fixed age, age-plus-confidence and always reacquire. Outcome: held-out gain surviving direct observation, or null.
- **Counterexample / negative value:** Identical capture, timestamps, proxy and output in two worlds, one changing state after observation. Opposite execute decisions cannot both be correct. Without witness or restricted transition law, current truth is unidentifiable. Cheap direct read likely kills proxy method.

Pareto: TRIG-LEAK has clearest privacy harm and inexpensive replay, but strong shaping neighbors and no confirmed owner. STALE-ACT has independent truth and cheap physical test, but weak workflow and likely fixed-age/direct-read dominance. SLO-REFUSE has operational relevance but minimal exact novelty and hardware-profile gaps. PROOF-BOUND has high negative clarity but duplicates a local killed boundary. No aggregate score hides these trade-offs.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Causal, budgeted camouflage selects heterogeneous transforms; defense-aware recovery varies by dataset. | [K] | Worae et al., *Adaptive Traffic Camouflage*, arXiv:2609.25787v1, 2026-09-22, https://arxiv.org/pdf/2609.25787v1 | Abstract/Intro pp. 1-2; threat p. 3; controller pp. 5-6; evaluation pp. 7-9; Sec. VII p. 10. | One-day-old preprint; device identity/passive observer, not event-deadline theorem. |
| Event-level timing/size DP, queue/dummy costs and burst limitation exist. | [K] | Xiong et al., *Network Traffic Shaping for Enhancing Privacy in IoT Systems*, arXiv:2111.14992v1, 2021-11-29, https://arxiv.org/pdf/2111.14992v1 | Model pp. 4-7; evaluation pp. 12-13; Sec. IX p. 14; conclusion p. 15. | Primary preprint says journal under review; foundational baseline only. |
| DPShaping is a likely direct neighbor. | [GAP] | Zhang et al., *DPShaping: Balancing Privacy Guarantee and Communication Cost in IoT Traffic Shaping*, ACM DOI 10.1145/3745783, 2025-06-25 metadata, https://doi.org/10.1145/3745783 | Title/metadata only; full PDF blocked, no sections read. | Cannot support central claim until audited. |
| Task-age resolution/SLM-LLM threshold routing exists in simulation. | [K] | Gan et al., arXiv:2504.07428v1, 2025-04-10, https://arxiv.org/pdf/2504.07428v1 | Abstract/Intro pp. 1-2; policy/evaluation pp. 4-5. | Not current physical state truth. |
| Task-specific communication plus delay-aware control is adjacent. | [K] | Diao et al., arXiv:2503.08661v1, 2025-03-11, https://arxiv.org/pdf/2503.08661v1 | Intro pp. 1-2; method pp. 4-6; CARLA evaluation pp. 10-12; conclusion p. 13. | Simulation, no bench action evidence. |
| Data-aware model/batch scheduling already optimizes deadline utility. | [K] | Wolfrath et al., *SneakPeek*, arXiv:2505.06641v1, 2025-05-10, https://arxiv.org/pdf/2505.06641v1 | Task pp. 1-3; evaluation pp. 7-10; future work p. 11; conclusion p. 12. | Future-work sentence does not prove gap. |
| Edge multi-DNN model/exit/batch choice already targets SLO. | [K] | Cao et al., *EdgeServing*, arXiv:2605.05527v1, 2026-05-07, https://arxiv.org/pdf/2605.05527v1 | Intro pp. 1-2; method pp. 4-5; evaluation pp. 6-8; conclusion p. 9. | GPU/Jetson setting, Pi comparison [GAP]. |
| Low-end TEE protects declared inference execution/model. | [K] | Kiri et al., *VECODI*, arXiv:2606.07470v1, 2026-06-05, https://arxiv.org/pdf/2606.07470v1 | Threat pp. 3-4; evaluation pp. 9-10; conclusion p. 12; appendix p. 14. | Does not independently certify scene truth. |
| An edge model operation has a zk verification neighbor. | [K] | Maheri et al., *Poster: Verifiable Unlearning on Edge*, arXiv:2506.20037v1, 2025-06-24, https://arxiv.org/pdf/2506.20037v1 | Intro p. 1; method/evaluation pp. 2-3; future work p. 3. | Poster and different operation; component collision only. |
| Identical observations can have opposite post-capture state. | [C] | Paired-world construction above; compare Gan/Diao and locally killed WATERMARK-CLOSE. | Formalization here, not sourced empirical result. | Requires explicit transition family and clock-error assumptions. |

## Queries and failed searches

- arXiv API: `all:traffic AND all:shaping AND all:privacy`, `all:smart AND all:home AND all:traffic AND all:analysis`, `all:edge AND all:inference AND all:sidechannel`, `all:BCEdge`, `all:deadline AND all:edge AND all:batch AND all:inference`, `all:task-oriented AND all:age AND all:inference`; exact-ID metadata query.
- OpenAlex: `traffic shaping IoT privacy`, `IoT traffic shaping privacy`, `edge inference interference`, `energy harvesting edge inference`, title searches with 2024-01-01 to 2026-09-23 filter. Survey hits excluded from evidence.
- Local register/charter/README and prior packet scan for already killed mechanisms. No new Bob Zhang paper chain was inspected [GAP].
- [GAP] ACM DPShaping PDF challenged, so exact sections/baselines unresolved. [GAP] Event confidentiality owner and operator loss unconfirmed. [GAP] Event-time deadline citation chain/later work not exhaustive. [GAP] Pi/GPU inventory and clock/power measurement unconfirmed. Search absence is not novelty.

## Decision

HOLD TRIG-LEAK and STALE-ACT only for the stated cheap falsification gates. SLO-REFUSE is PIVOT/KILL-leaning; PROOF-BOUND is KILL as positive thesis. Compare both HOLDs against the pending PRF-TR physical feasibility/baseline gate, not its story alone. Fixed-clock or direct-state baseline victory closes the respective claim without further model search.

HOLD
