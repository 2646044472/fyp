# Validation Audit: 2026-09-23 AUDIT-GAP

## Decision investigated

Audit `AUDIT-GAP` from `research/ops/divergence/2026-09-23-beyond-palm-residual-divergence.md` as a possible non-palm edge FYP direction:

> A low-cost edge node chooses `cheap sentinel`, `full verifier`, or `unknown` under a bounded verifier budget. An independently recorded full-support reference trace supplies episode truth. Compare adaptive, periodic, random, and always-verify policies on missed-event/false-no-event episodes, decision latency, energy, and unknown burden.

The project charter and candidate register were read before this audit. The current user-confirmed Palm Payment route remains the execution commitment; `AUDIT-GAP` is only a conditional alternative and must not displace it without passing this gate.

## Claim under test

The strongest defensible version is not “adaptive sensing is novel” and not “adaptive sensing always beats periodic sampling.” It is:

**[C]** On a preregistered, finite physical event family, an edge policy using a cheap sentinel to allocate a fixed amount of expensive verification can produce a better held-out frontier of episode-level missed-event duration, false `no-event` decisions, detection latency, energy, and `unknown` rate than budget-matched periodic, uniform-random, and always-verify controls.

The proposed distinction is the evaluation contract: an independently clocked original-time reference, an episode-level endpoint, matched verifier cost, and an explicit `unknown` outcome. The distinction is not a new sampler unless the experiment proves a mechanism-level effect beyond these controls.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | Adaptive/event-sensitive sampling, sentinel-triggered wake-up, uncertainty-triggered expensive acquisition, randomized schedules, and sampling-control change detection are established. Lu et al. combine sparse sampling, continuously sampled sentinels, event detection, latency, coverage and energy. iAirGuard uses low-cost dynamic sampling and secondary sensing. Han et al. choose costly physical metrology from uncertainty and compare fixed/random schedules. | A separately powered reference used for evaluation, rather than as an online policy input, is a useful provenance requirement. It is not a new adaptive-sensing component. | **High collision** for a method claim. |
| 2. Exact claim collision | The endpoint family is already occupied in pieces: event detection rate, onset delay, anomaly-window coverage, sampling rate and energy in Lu et al.; temporal coverage and detection delay in Chatterjea and Havinga; detection delay, false alarms and observation cost in sampling-control change detection. Risk-aware online probing now directly formulates action/probe tradeoffs, missed-query error and probing rate. | No inspected source was verified to combine all four narrow conditions: independent original-time full-support reference, matched verifier-on budget, episode-level false-no-event/unknown semantics, and a held-out physical testbed. This remains `[GAP]`, not evidence of novelty. | **Medium for exact overlap; weak residual distinction.** |
| 3. Boundary / impossibility | If events can begin and end between verifier observations while the cheap sentinel trace is unchanged, `no event` and `short event` worlds are observationally identical to the policy. If event timing is independent of the schedule and verifier count is fixed, the periodic maximum-gap schedule can dominate variable/adaptive timing for event detection. An independently recorded reference fixes evaluation bias only; it does not make skipped intervals observable online. | A real predictive relation between sentinel history and future event occurrence could make adaptation useful. That relation must be measured on source cells and frozen before held-out evaluation. A bounded `unknown` contract or physical maximum-gap guarantee could also yield a valid reliability-boundary result. | **High** for the conditional kill; **low** for positive separation. |

## Assumption and identification audit

Let `S_t` be the cheap sentinel, `V_t` the expensive verifier, `A_t` the policy action, and `R_t` the independent reference trace. The online policy may observe `S` and its history, but not `R` or `V` during skipped periods.

1. **Independent reference is an evaluation oracle, not online evidence.** It must have an independent sensing chain, clock, power path, calibration record, and sampling resolution finer than the shortest event claimed detectable. If it shares the same sensor, driver, clock, power rail, or physical blind spot, “independent” is only asserted. If the event generator is software-triggered from the same clock used by the monitor, timing labels can be circular.
2. **False `no-event` is not identifiable in a blind interval.** Consider `W0`, where the target stays below threshold, and `W1`, where a short excursion crosses threshold and returns entirely between verifier observations. If `S_t` is identical in both worlds, every permitted online policy receives the same history and cannot certify which world occurred. It must emit `unknown`, impose a maximum blind gap, or retain an independent continuous witness; emitting `no-event` is an unsupported claim.
3. **The reference must support episode matching, not merely pointwise labels.** The protocol must predeclare threshold, hysteresis, minimum duration, merge gap, onset/offset tolerance, and whether overlapping excursions form one episode. Otherwise missed duration and detection latency can be changed by post hoc segmentation.
4. **Adaptive advantage requires predictive information.** If the sentinel is only a noisy contemporaneous copy of the target and event timing is independent of its history, adaptation changes observation timing but does not create information. A positive result on pulses deliberately preceded by a sentinel trigger demonstrates a designed correlation, not general superiority. Source-cell sentinel/event mutual information or a comparable preregistered predictive test is required.
5. **Cost matching is multi-dimensional.** Equal verifier-on fraction alone is insufficient if policies differ in wake-up energy, sentinel duty cycle, storage, radio traffic, CPU time, calibration overhead, or reference hardware. The reference may be used only for labels and excluded from deployment cost; this must be stated explicitly.
6. **The action endpoint must be real.** “Bad maintenance decision” is only a story unless a benign, authorized downstream action or record state is defined. A safe FYP endpoint can be `event / no-event / unknown` record correctness and review workload; it cannot claim safety or industrial maintenance impact without a real stakeholder and consequence model.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Lu, Sun, Jiang & Butler, *Adaptive Sampling for Spatiotemporal Anomaly Monitoring in Wireless Sensor Networks*, arXiv:2607.15235v1, 2026-07-16 | Uncertainty-driven sparse sampling; continuously sampled sentinel nodes; sentinel GLR wakes neighbors and triggers recovery. | Injected temperature anomalies in Intel Berkeley data; event detection, onset delay, anomaly-window coverage, sampling ratio, global rate and energy. | **High** component/endpoint overlap with sentinel-triggered adaptive verification under resource cost. | Kills a thesis framed as sentinel-assisted adaptive event coverage. Its injected-anomaly/public-trace limitation leaves only a physical independent-label audit open. URL: https://arxiv.org/html/2607.15235v1 |
| Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, DOI 10.1109/COMSNETS67989.2026.11418151, 2026-03-23 | ESP32-S3 environmental sensing; mean/variance-driven dynamic interval; secondary prediction/fault score. | Continuous versus adaptive deployment comparison; storage/transmission and environmental sensing behavior. | **High** for low-cost edge adaptive monitoring plus secondary sensing. | Kills a Pi/ESP32 adaptive-environment-monitor thesis. It does not establish the exact independent-reference protocol. URL: https://cse.iitm.ac.in/~cs25d002/assets/iairguard_paper.pdf |
| Han et al., *A Comparative Study of Semiconductor Virtual Metrology Methods and Novel Algorithmic Framework for Dynamic Sampling*, IEEE TSM 38(2), 2025, DOI 10.1109/TSM.2025.3531920 | Predictive uncertainty selects expensive physical metrology; fixed/random sampling controls. | Metrology load and model performance under drift/shift; sparse-sampling degeneration is discussed. | **High** for uncertainty-driven costly verification and budget comparison. | Kills generic “uncertainty decides when to verify.” Leaves physical episode truth and `unknown` semantics as a scope difference only. URL: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958452 |
| Bhuiyan et al., *e-Sampling*, ACM TAAS 12(1), Article 1, 2017, DOI 10.1145/2994150 | Local event-sensitive adaptive rate and decentralized event indication. | Structural-health/fire-event settings; rate, event indication, data and energy reduction. | **High** for local event-sensitive sampling under resource limits. | Kills a new-rate-control claim; does not settle the independent-reference evaluation contract. URL: https://cis.temple.edu/~wu/research/publications/Publication_files/Bhuiyan_ACM_2017.pdf |
| Chatterjea & Havinga, *Improving Temporal Coverage of an Energy-Efficient Data Extraction Algorithm for Environmental Monitoring Using WSNs*, Sensors 9(6):4941-4954, 2009, DOI 10.3390/s9064941 | Adaptive and randomized staggered sampling across correlated nodes. | Temporal coverage, event-to-detection delay and energy on environmental monitoring traces. | **Medium/high** endpoint overlap: coverage and delay under energy constraints. | Weakens any claim that episode coverage, delay, or random schedules are new. URL: https://doi.org/10.3390/s9064941 |
| Loreti, Bracciale & Bianchi, *StableSENS*, IEEE IoT Journal 6(6):9908-9918, 2019, DOI 10.1109/JIOT.2019.2933335 | Sampling-period control for energy-harvesting IoT sensing. | Analysis of event misses under equal sample count and sampling stability. | **High** for the strongest periodic-baseline argument. | Conditionally kills adaptive timing when event timing is schedule-independent; it does not rule out an informative sentinel. URL: https://doi.org/10.1109/JIOT.2019.2933335 |
| Zhang & Mei, *Bandit Change-Point Detection for Real-Time Monitoring High-Dimensional Data Under Sampling Control*, Technometrics 65(1):33-43, 2023, DOI 10.1080/00401706.2022.2054861 | Sampling-controlled sequential change detection with observation decisions. | Detection delay, false alarms and observation cost. | **Medium** decision/constraint overlap for budgeted observation and event detection. | Kills a claim that budgeted detection-delay/false-alarm tradeoffs are unstudied. Different statistical setting leaves only the physical-label protocol open. URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC10027391/ |
| Talli, Popovski & Simeone, *Risk-Aware Online Conformal State Probing*, arXiv:2609.25889v1, 2026-09-22 | Predict a state, choose action or spend a probe; controls probing rate and risk. | Missed-query error, probing rate and risk-aware action/probe tradeoff. | **High** generic action-versus-probe overlap with `verify / skip / unknown`. | Kills a generic risk-aware probing mechanism. A physical sensor-specific negative audit would need a genuinely different action restriction and independently labelled endpoint. URL: https://arxiv.org/html/2609.25889v1 |

## Strongest simple baseline

The strongest baseline is a **budget-matched periodic maximum-gap verifier**:

- choose verifier duty budget `b` and verifier-on duration;
- verify every `Delta(b)` seconds with randomized initial phase across runs;
- use the same sentinel, wake-up, storage, CPU and logging accounting as the adaptive policy;
- emit `event` only when a verifier-supported episode is observed;
- emit `unknown`, rather than `no-event`, whenever the coverage contract cannot certify absence.

This baseline has a transparent worst blind interval and needs no training data, uncertainty calibration, or trigger tuning. Add two required controls: uniform-random verification at equal expected verifier cost and always-verify as the lower-miss upper-cost reference. An abstain-only policy that emits `unknown` for every uncertified interval is also required; otherwise a method can appear accurate by making unsupported `no-event` claims.

The candidate is killed as a positive method if periodic is non-inferior on the preregistered held-out cells, or if its apparent gain comes from unequal sentinel/wake-up cost, event timing designed around its trigger, or a relaxed definition of `no-event`.

## Contrarian result

The strongest case for `AUDIT-GAP` is not a better adaptive policy. It is a reproducible result that exposes a reliability boundary:

- an independent reference can show how many short episodes are missed by each policy;
- no policy can certify absence inside an unobserved interval when the permitted observations are identical in two worlds;
- a maximum-gap periodic audit may dominate adaptive timing when event timing is not predictable from the sentinel;
- adaptation is justified only when a frozen, independently measured sentinel-to-future-event relation survives held-out physical conditions.

That is scientifically useful, but it is a protocol/negative-result contribution, not yet a defensible undergraduate thesis claim. A negative result can be publishable-quality only if the event generator, timing, reference failure analysis, policy family, cost accounting, and analysis plan are preregistered and the data/code are reusable. A one-board demo with hand-made pulses and a graph of energy is not enough.

## Feasibility audit

| Requirement | Current status | Validation judgment |
| --- | --- | --- |
| Independent reference sensor and clock | `[GAP]` | Mandatory. A second cheap sensor is insufficient unless its error modes, clock, power and physical placement are independent. |
| Controlled physical event generator | `[GAP]` | Use benign temperature/light/occupancy-like pulses only. Software-injected events or a source controlled by the monitor clock do not establish physical validity. |
| Energy measurement | `[GAP]` | Need a current/voltage instrument or calibrated inline monitor for sentinel, verifier, wake-up and storage/radio costs. CPU time alone is not energy. |
| Event labels and episode rules | `[GAP]` | Predeclare threshold, duration, hysteresis, merge gap, timestamp tolerance and minimum detectable event. |
| Hardware/compute | `[C]` | A Pi/MCU plus a wired reference logger is likely affordable, but the exact sensor, resolution, sampling rate and power instrument are not confirmed in the packet. Do not purchase hardware before the reference contract is written. |
| Data volume and repetitions | `[GAP]` | Need enough repeated source and held-out cells across pulse duration, placement, amplitude, drift and phase. A few manually selected demonstrations cannot support a frontier. |
| Ethics and permissions | `[K]` | A non-personal, non-hazardous benchtop test can avoid human-subject and safety claims. Any occupancy, biometric, medical, or production-maintenance data would reopen approval and access gates. |
| FYP schedule | `[C]` | Feasible only as a bounded pilot/negative audit after the protocol and hardware are fixed. It is not feasible to discover the task, build a new sampler, collect a robust physical dataset, and establish novelty late in the Palm MVP schedule. |
| User/workflow owner | `[GAP]` | No current stakeholder, maintenance decision, or quantified cost of false `no-event` is confirmed. Without one, the story remains an instrumentation benchmark. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Sentinel-assisted adaptive sampling already combines event detection, coverage, delay and energy under sparse acquisition. | [KILL] | Lu et al., arXiv:2607.15235v1, 2026-07-16, https://arxiv.org/html/2607.15235v1 | Secs. I-II; Sec. IV-B-C; Sec. V, pp. 1-2, 6-8 | Public Intel Berkeley trace with injected anomalies; physical independent-reference protocol is not established. |
| Low-cost edge dynamic sampling plus secondary sensing is already published. | [KILL] | Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, 2026-03-23, https://cse.iitm.ac.in/~cs25d002/assets/iairguard_paper.pdf | Abstract p. 1; Sec. II-A-B, pp. 3-4; Sec. III, pp. 4-6 | Its endpoint is mainly data/storage/transmission reduction and local prediction comparison. |
| Uncertainty-driven costly measurement with fixed/random controls is established. | [KILL] | Han et al., IEEE TSM 38(2), 2025, https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958452 | Sec. I, pp. 232-233; Sec. III-C, pp. 236-237; Sec. IV-C, pp. 238-239 | Semiconductor metrology domain; mechanism collision, not exact physical event endpoint. |
| Event-sensitive adaptive sampling and decentralized event indication are established. | [K] | Bhuiyan et al., ACM TAAS 12(1), Article 1, 2017, https://cis.temple.edu/~wu/research/publications/Publication_files/Bhuiyan_ACM_2017.pdf | Secs. 2.1-2.2, pp. 1:4-1:6; Secs. 4-6, pp. 1:11-1:17; results pp. 1:23-1:27 | Older source; establishes component collision. |
| Temporal coverage/detection delay and randomized schedules under energy constraints are established. | [K] | Chatterjea & Havinga, Sensors 9(6):4941-4954, 2009, https://doi.org/10.3390/s9064941 | Abstract; Sec. 5, pp. 4949-4952 | Environmental WSN deployment trace; not the two-fidelity reference protocol. |
| Under schedule-independent events and equal sample count, constant periodic timing is a strong event-detection baseline. | [K] | Loreti et al., IEEE IoT Journal 6(6):9908-9918, 2019, https://doi.org/10.1109/JIOT.2019.2933335 | Sec. I, p. 2, including Fig. 1 and residual-lifetime argument | Conditional result; does not rule out predictive sentinels. |
| Sampling-controlled change detection already trades delay, false alarms and observation cost. | [K] | Zhang & Mei, Technometrics 65(1):33-43, 2023, https://pmc.ncbi.nlm.nih.gov/articles/PMC10027391/ | Abstract; Sec. 1, p. 34; Sec. 3.1, pp. 36-37; Sec. 4, p. 39 | Different high-dimensional statistical model. |
| Action-versus-probe risk and missed-query error are directly formulated. | [KILL] | Talli, Popovski & Simeone, arXiv:2609.25889v1, 2026-09-22, https://arxiv.org/html/2609.25889v1 | Abstract; Secs. 1-4 | Generic policy mechanism; a physical testbed would not by itself distinguish the method. |
| A reference trace removes selective evaluation bias only if it is valid and recorded independently; it does not make skipped intervals observable. | [K] / [C] | Lakkaraju et al., KDD 2017, 2017, https://www.cs.cornell.edu/home/kleinber/kdd17-selective.pdf | Abstract and Sec. 1, p. 275; Sec. 4, pp. 278-280; observation-model construction in this audit | Selective-label paper is conceptual support; the blind-interval argument is conditional on the stated model. |
| No inspected source was verified to contain the exact combination of independent full-support reference, matched verifier budget, episode false-no-event/unknown endpoint, and held-out physical conditions. | [GAP] | Search chain and sources above, searched 2026-09-23 | N/A | Search absence is not novelty evidence; this residual may be only evaluation hygiene. |

## Queries and failed searches

Searches run or rechecked on 2026-09-23:

- `active verifier audit adaptive sensing missed event independent reference trace edge sensor 2024 2025 2026`
- `dynamic sampling uncertainty edge sensor independent reference event coverage 2025`
- `independent reference adaptive sampling event detection sensor verification budget`
- `adaptive sampling missed event duration periodic baseline energy sensor monitoring paper`
- `false no-event sensor sampling event detection`
- `active sensing verifier audit independent ground truth edge sensor`
- `expensive sensor cheap sensor adaptive sampling event detection paper`
- `sentinel verifier adaptive sensing event detection sensor`
- `missed event periodic sampling energy sensor detection paper`
- `selective labels sensor monitoring adaptive sampling ground truth`
- `verification budget adaptive sensing event detection`
- `online conformal state probing edge action probe missed query error`
- `sampling-controlled change detection false alarm observation cost`

Citation-chain and local-file checks:

- Read `AGENTS.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, and the supplied divergence packet.
- Rechecked the prior AS1 audit and its source chain in `research/ops/validation/2026-08-28-adaptive-sensing-as1-validation.md`; it already records the periodic-baseline and blind-interval arguments.
- Retrieved official arXiv HTML for arXiv:2607.15235v1 and arXiv:2609.25889v1, and the PMC full text for Zhang & Mei. The NIST PDF endpoint for Han et al. returned HTTP 503 during this recheck; the local prior audit records the version, URL, sections and pages previously read. This retrieval failure is not treated as evidence for or against novelty.

Failed or unresolved searches:

- No authoritative primary paper was verified that exactly joins all four narrow conditions above.
- No forward-citation audit established that this exact evaluation contract is a recognized standalone contribution.
- No current physical apparatus, independent reference, power instrument, event generator, workflow owner, or authorized data plan is confirmed.

## Decision

**PIVOT**

Kill `AUDIT-GAP` as a positive thesis claim about adaptive sensing, uncertainty-triggered verification, or risk-aware probing. Those mechanisms and most of the endpoint family are directly occupied, and the periodic maximum-gap baseline can dominate under a valid schedule-independent event model.

Retain only a bounded, non-palm **independent-reference reliability audit** if all of the following are fixed before implementation: a benign physical event source; an independently powered and clocked reference with documented resolution; a preregistered episode/`unknown` contract; equal-cost periodic, random, always-verify and abstain controls; a held-out physical split; and a real downstream record/review endpoint. A null, periodic-dominance result, or measured blind interval is the preferred scientific outcome if it is reproducible and the data/protocol are reusable. Until that gate is passed, keep the candidate at `PIVOT`, not `HOLD` or `PROMOTE`.
