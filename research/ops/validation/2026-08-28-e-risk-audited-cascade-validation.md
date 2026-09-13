# Decision investigated: should candidate E lock as a risk-audited low-power sentinel cascade?

## Decision investigated

Should the FYP lock candidate E: a low-power sentinel controls a costly local verifier; a pre-frozen, known-probability random `audit-wake` among `no-wake` episodes estimates or bounds full-population no-wake safety risk and can trigger a conservative local action under fixed energy, latency, and coverage budgets? The task is a simulated local safety-assist zone only, with complete episode ground truth from an external reference used only for evaluation. It is not a certified interlock.

## Claim under test

The defensible version is not "a ToF/PIR wakes a camera" and not a new inverse-propensity, doubly robust, Bayesian, or partial-identification estimator. The narrow claim is:

> Given a frozen episode definition, a frozen full-support audit design, recorded realized inclusion probabilities, and a verifier whose audit-time observation has a separately measured relation to the target event, does a telemetry-stratified audit policy improve a pre-registered complete-episode risk--energy--latency frontier over fixed triggering and uniform audit?

[KILL] Without the last verifier/target relation, the audit estimates the rate of an `audit-time verifier-positive` proxy, not the rate of an intrusion at the sentinel decision time. It therefore cannot support a physical-safety guarantee or an online risk bound merely by inverse-probability weighting.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | Ballet et al. implement an ultra-low-power always-on probabilistic front end that wakes a stronger CPU on abnormal, ambiguous, or invalid output, and optimize mean energy as a function of wake frequency. Cui et al. use adaptive edge trigger sensing and optimize triggering/energy in wireless SHM. Moosmann et al. use an asynchronous event imager to wake an RGB vision node. | None of the inspected component papers makes randomized full-support audit sampling of `no-wake` episodes the primary endpoint. That is an absence within the recorded search, not evidence of novelty. | High that generic cascade/wake/energy claims collide; medium that the proposed combination has not yet collided. |
| 2. Exact-claim collision | Chen, Li, and Mao formalize selectively observed labels, exact identification conditions, and tight partial bounds for classification risk. Sadhuka et al. formalize costly multi-stage funnels where late ground truth is censored, and jointly model label and censoring decisions. These papers kill any claim that trigger-induced censoring, full-population risk identification, or risk bounding is a new statistical contribution. | The inspected works do not use an actual low-power sentinel and audit-wake on a local physical sensing device, nor do they report a complete-episode edge risk--energy--latency frontier. A system/protocol comparison remains only Amber. | High for estimator/bound collision; medium for the physical-system boundary. |
| 3. Boundary / impossibility | Chen et al. show that, under selectively observed labels, overlap and additional assumptions are required; without stronger assumptions exact risk identification is generally impossible and only a partial range remains. A no-wake policy creates precisely this failure when any episode/stratum has zero audit chance. | Deliberately randomized audit with known nonzero realized inclusion probability avoids the historical-policy identification problem for a *finite, predeclared population* if the audit observation is a valid label for the stated estimand. It does not identify an earlier transient intrusion from a later verifier frame. | High. |

### Component-collision detail

[K] Ballet et al., arXiv:2605.29533v1 (2026-05-28), Secs. Introduction and Wake-up policy, pp. 2-3 and 9-10, implement an always-on front end plus a stronger CPU back end. Their wake rule explicitly escalates abnormal, ambiguous, or invalid front-end outputs; Sec. `Wake-up probability and monitoring cadence determine the energy optimum`, pp. 12-14, defines energy as front-end plus monitoring plus wake-service energy. This makes a two-stage uncertainty/quality wake policy, energy profiling, and "turn silent errors into wake-ups" non-contributions for E.

[K] Cui et al., *Mechanical Systems and Signal Processing* 241 (2025) 113537, DOI version 2025, title/abstract and conclusion accessible through the publisher record, optimize adaptive trigger sensing with feedback, a digital twin, and Bayesian optimization for energy-efficient wireless SHM. It is a component neighbor, not an exact neighbor: its published setting is structural monitoring and its reported trigger endpoint is not the proposed full-population no-wake safety-risk audit. Full PDF section/page verification was unavailable in this round, so it is not used for an identification claim.

[K] Moosmann et al., arXiv:2608.23192v1 (2026-08-24), abstract, use an always-on event imager to trigger RGB acquisition and processing in a low-power vision node, reporting per-cycle energy and an activity-ratio lifetime projection. It kills a novelty claim for event/image-triggered RGB duty cycling. [GAP] Full-text section/page inspection was not available at audit time; do not use its reported figures as a baseline without retrieving the versioned PDF.

### Exact-claim collision detail

[K] Chen, Li, and Mao, ICML 2025, PMLR 267:8480-8519, official paper/PDF version 2025, Sec. 3.1 p. 3 defines labels observed only after a decision and requires overlap `P(D=1 | X,U)>0`; Sec. 5 pp. 5-6 states that exact risk identification is generally impossible without stringent assumptions and derives tight partial bounds. This directly subsumes E's generic words "probability correction", "full-population risk", and "risk bound".

[K] Sadhuka et al., *A Bayesian Model for Multi-stage Censoring*, ML4H 2026, PMLR 297:792-806, official PDF version 2026, Secs. 1-3 pp. 1-4 and Sec. 5 p. 8, treat a costly funnel in which later ground truth is observed only after earlier decisions; they jointly model outcome and censoring and emphasize the limits of causal interpretation. This is a direct conceptual neighbor for sentinel -> verifier funnels. It does not establish that their Bayesian model transfers to E's deliberately randomized audit design.

[KILL] If E presents the Horvitz--Thompson/IPW estimate, a confidence interval, a partial bound, an IV argument, or a learned censored-label model as its primary contribution, it is materially subsumed by the cited selective-label and multi-stage-censoring literature. The FYP may implement these as necessary baselines/analysis, but cannot market them as invented methods.

## Assumption and identification audit

Let episode `i` begin and end before the policy runs. Let `W_i=0` mean the sentinel did not ordinarily wake the verifier, `A_i` be the random audit inclusion, `pi_i=P(A_i=1 | frozen log state)` be recorded before the audit decision, `V_i` be the audit verifier's output after its actual readiness delay, and `Y_i` be the target event at the original decision time.

| Required condition | Why it is necessary | Candidate-E status / kill test |
| --- | --- | --- |
| Frozen target and time anchor | `V_i` after camera boot need not equal `Y_i` at the sentinel decision. A fast object can leave before the audit frame; then a verifier-negative sample does not mean no original intrusion. | [KILL] unless `Y_i` is explicitly redefined as an audit-time event, or external-reference data quantify and conservatively bound the time-anchor error by motion/readiness stratum. |
| Full support | For every intended no-wake episode or stratum, `0 < pi_i` must hold. A deterministic telemetry stratum never audited is unidentified. | [K] necessary by Chen et al., Sec. 3.1 p. 3. [KILL] if energy-throttling, cooldown, camera unavailability, or storage exhaustion creates zero realized inclusion for any claimed coverage cell. |
| Known *realized* inclusion, not merely planned inclusion | Failed wakes, dropped frames, thermal throttling, and skipped audits change the sampling design. Planned `pi_i` cannot weight missing or failed audits. | [GAP] No current hardware/log schema shows audit command, realized first-valid frame, failure flag, duty cycle, and `pi_i`. Audit must log all of them. |
| Valid audit label | A random sample fixes selection, not measurement error. `V_i` is a second model's prediction, not external truth; correlation with sentinel failure can remain. | [KILL] for a claim of "safety risk bound" unless validation measures `P(Y_i=1|V_i=0, W_i=0, stratum)` using the external reference and carries its uncertainty into the bound. |
| Population and dependence | Frame-level samples from one pass are serially dependent. Treating them as IID makes intervals too narrow; the policy can also change future contexts. | [GAP] Define independent episodes/trials or use cluster/block bootstrap and report effective sample size. Freeze policy epochs; do not recycle audit data from one policy to certify another. |
| Finite audit information | Rare event claims need enough independently audited no-wake episodes. With zero observed target events, an approximate one-sided 95% upper binomial rate is `3/n`: 300 independent audits only exclude rates above about 1%, 3,000 only rates above about 0.1%, before verifier error and dependence. | [C] This arithmetic is a planning lower bound, not a promised safety threshold. [KILL] if the project claims a smaller risk limit without an audit sample-size calculation, episode independence justification, and verified label fidelity. |
| Sequential action validity | Looking repeatedly and changing the sentinel/action after an adverse audit can invalidate a fixed-horizon confidence statement. | [GAP] The conservative-action controller must use predeclared epochs with holdout evaluation, or an appropriate sequential confidence method. Otherwise report retrospective diagnostics only. |

[K] Chen et al., Sec. 3.1 p. 3 and Sec. 5 pp. 5-6 establish the central boundary: selection alone leaves risk unidentified absent overlap and additional assumptions. Their specific IV assumptions are not required if E actually randomizes audit inclusion with full support, but the paper prevents treating a nonrandom telemetry-selected audit as automatically corrected.

[K] Sadhuka et al., Secs. 1 and 3 pp. 1-4 show why a funnel's observation rule must be modeled with the outcome; Sec. 5 p. 8 explicitly limits causal reading of its learned threshold differences. This supports a conservative interpretation of E's controller: a lab audit can estimate a stated experimental quantity, not certify an intervention against real-world harm.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Ballet et al., arXiv:2605.29533v1, 2026 | Always-on memristor probabilistic front end; wake CPU on abnormal/ambiguous/invalid output. | Heartbeat classification; final macro-F1, wake fraction, energy model. | Low-power screener -> high-power verifier; reliability through escalation; energy/wake tradeoff. | [KILL] Architecture, uncertainty wake-up, and wake-energy novelty. Leaves no-wake random audit and full-population audit-risk endpoint untested. |
| Cui et al., MSSP 241 (2025) 113537 | Wireless SHM event trigger; edge feedback/digital twin/Bayesian optimization. | Trigger quality and energy-efficient sensing in SHM. | Adaptive edge triggering under acquisition cost. | [KILL] Generic adaptive trigger/energy story. [GAP] Publisher full text could not be inspected here for exact observation-bias treatment. |
| Moosmann et al., arXiv:2608.23192v1, 2026 | Event imager in always-on wake-on-motion mode triggers RGB/edge processing. | Sense-to-report energy, object recognition, activity-ratio lifetime. | Low-power visual trigger -> RGB verifier at edge. | [KILL] Device/system demo novelty. [GAP] Need full PDF audit before final packet claims a detailed exclusion. |
| Chen, Li, Mao, ICML 2025 | Decision-created selectively observed labels; IV / point and partial identification; cost-sensitive learning. | Full-population classification risk and tight partial bounds. | Censoring caused by a prior decision; risk estimation/bounding. | [KILL] New selective-label estimator, generic IPW/bounds, and vague full-population claim. Leaves a physically measured audit protocol only. |
| Sadhuka et al., ML4H 2026 | Multi-stage costly funnel with late labels; joint outcome/censoring model. | Censored-population outcome prediction and decision threshold analysis. | Sentinel -> costly verifier funnel and labels missing downstream. | [KILL] Treating multi-stage censoring as unexplored or claiming a generic joint model. Leaves actual edge power/readiness and random audit design. |
| Ma et al., arXiv:2608.14991v1, 2026 | Onboard VLM/detector decides selective cloud VLM request; local validation/AEB remains local. | CARLA task success, cloud requests, AEB use, timing, network profiles. | Risk-triggered costly escalation and authority separation. | [KILL] Generic risk-adaptive expensive inference / local conservative action. Leaves no-wake audit identification and Pi-scale physical sensing. |

## Strongest simple baseline

[KILL] `B3: fixed trigger + uniform periodic/random audit + design-based estimate` is the most dangerous baseline. It has full support, known inclusion probabilities, no learned telemetry model, and directly answers the candidate's identification story. If it matches any telemetry-stratified policy on complete-episode estimate error/interval coverage and the energy/latency frontier, E has no remaining mechanism contribution.

Required comparison, all under the same pre-frozen episode definition and resource budget:

| Baseline | Required outcome | What a non-inferior or superior result means |
| --- | --- | --- |
| `B0` verifier always on | Complete-population risk proxy / external-reference evaluation; energy and latency upper cost. | The cascade is unnecessary at the claimed resource level. |
| `B1` fixed sentinel threshold, no audit | System missed-event and cost. | Establishes how much audit actually changes complete-population assessment. |
| `B2` adaptive/uncertainty trigger | Same endpoints. | Separates audit value from ordinary threshold tuning, already crowded by Ballet/Cui. |
| `B3` uniform full-support audit | Estimate bias/error, interval coverage/width, energy, readiness delay. | If comparable to telemetry stratification, the learned/stratified policy fails. |
| `B4` telemetry-stratified audit with IPW/HT analysis | Same endpoints plus realized inclusion/failure logging. | The only candidate mechanism; it must win without eroding support. |

## Contrarian result

[KILL] The strongest objection is not that E lacks an attractive application. It is that its claimed intellectual core splits into two already mature pieces: low-power escalation systems already optimize wake frequency and energy, while selective-label/multi-stage-censoring work already studies risk identification and bounds under action-dependent missingness. The remaining crossover can be an honest undergraduate systems measurement study only if it is framed as a pre-registered empirical boundary: whether physical audit wake-ups buy more trustworthy full-episode evaluation/control than uniform audit at the same budget.

## Feasibility audit

### Hardware and measurement

[K] ST's VL53L1X datasheet, DS12385 Rev. 8, Secs. 3.4-3.6 pp. 8-10, documents user-programmable ranging thresholds and range status, calibration needs, timing/power tradeoffs, and XSHUT-controlled standby. These make a low-cost sentinel prototype technically plausible, but do not make it safety-rated.

[K] The same datasheet's published ranges depend on target reflectance, ambient light, timing budget, cover glass, field of view, and calibration; it says unmeasurable/weak signals return a range status (Sec. 3.4 p. 8). This supports putting signal rate, ambient rate, range status, boot/readiness and calibration state in the audit log instead of treating distance alone as an adequate `X`.

[KILL] IEC 62061:2021+AMD1:2024 is the applicable machinery functional-safety systems standard and requires design/integration/validation of safety-related control systems. A Pi/consumer ToF/camera prototype cannot be described as a certified interlock from its experiment. The project must remain a simulated assist zone with lights/logged mock stop, as stated in the decision.

[GAP] The canonical charter confirms only that affordable items may be self-purchased. It does not confirm a BOM, a board capable of physically gating the verifier, a power instrument, delivery timing, project duration, or a thermal/continuous-run protocol. Before promotion, demonstrate an actual `off -> first valid audit frame` trace and measured incremental joules; software FPS while camera hardware is still powered is not sufficient.

### Data, labels, and ethics

[GAP] There is no confirmed public dataset for E's joint quantities: sentinel raw/status, actual wake/readiness/failure, randomized `pi_i`, verifier output, external-reference episode truth, power, and latency. A controlled collection is required.

[KILL] If the external reference is only video reviewed after the fact, it may validate the research evaluation but cannot become the online source that makes deployment risk known. The final paper must keep those roles separate: external reference labels held-out evaluation; the running node only sees its sentinel, audit outcome, and log state.

[GAP] A dummy/rail-controlled object task can avoid collecting bystander data, but human hand-intrusion collection, storage, consent, institutional permission, and retention have not been authorized. The lowest-risk minimal experiment uses non-personal standardized objects first; any human footage needs the institution's applicable approval before collection.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Always-on low-power screen can wake a stronger local CPU on abnormal/ambiguous/invalid output; wake frequency governs energy. | [K] | Ballet et al., arXiv:2605.29533v1, 2026-05-28, https://arxiv.org/pdf/2605.29533 | Abstract p. 1; Introduction pp. 2-3; Wake-up policy pp. 9-10; energy analysis pp. 12-14. | Heartbeat/memristor-FPGA/ASIC setting; direct component collision only. |
| Selective labels need overlap; without stronger assumptions exact risk identification is generally impossible, while partial bounds are possible. | [K] | Chen, Li, Mao, ICML 2025, PMLR 267:8480-8519, official PDF 2025, https://proceedings.mlr.press/v267/chen25al.html and https://raw.githubusercontent.com/mlresearch/v267/main/assets/chen25al/chen25al.pdf | Sec. 3.1 p. 3; Sec. 4 pp. 4-5; Sec. 5 pp. 5-6; conclusion p. 9. | Their multiple-decision-maker/IV setting differs from a deliberately randomized audit; it kills estimator novelty, not necessarily protocol utility. |
| Costly multi-stage funnels censor downstream truth; joint label/censoring modeling changes censored-population prediction and has causal-interpretation limits. | [K] | Sadhuka et al., ML4H 2026, PMLR 297:792-806, official PDF 2026, https://proceedings.mlr.press/v297/sadhuka26a.html and https://raw.githubusercontent.com/mlresearch/v297/main/assets/sadhuka26a/sadhuka26a.pdf | Sec. 1 pp. 1-2; Sec. 2 pp. 2-3; Sec. 3 pp. 3-4; Sec. 5 p. 8. | Healthcare rather than edge sensing; direct conceptual/methodological neighbor. |
| Risk-triggered edge-cloud escalation with local safety authority and task/communication/timing endpoint is already demonstrated in simulation. | [K] | Ma et al., arXiv:2608.14991v1, 2026-08-15, https://arxiv.org/abs/2608.14991 and https://arxiv.org/html/2608.14991 | Abstract and Sec. I, pp. 1-2; Secs. III-IV as listed in versioned HTML. | CARLA, cloud VLM, not audit sampling; kills generic risk-triggered costly-inference/authority claim. |
| A consumer ToF can expose threshold/status/telemetry and needs calibration; range/power depend on scene and configuration. | [K] | STMicroelectronics, VL53L1X DS12385 Rev. 8, official datasheet, https://www.st.com/resource/en/datasheet/vl53l1x.pdf | Secs. 3.3-3.6 pp. 8-10; Sec. 7 pp. 25-31. | Hardware capability, not a safety certification or proof for black/reflective/moving targets. |
| Safety-related machine control requires design/integration/validation beyond a consumer prototype. | [K] | IEC 62061:2021+AMD1:2024 CSV, official IEC listing, https://webstore.iec.ch/en/publication/93654 | Scope and clauses list on official product page, accessed 2026-08-28. | Standard is a scope boundary; full standard text was not purchased/read. |
| ToF geometry and reflectivity can distort measurement in robotic-safety experiments. | [K] | Tufekcioglu et al., *Sensors* 25(14):4385, 2025, https://doi.org/10.3390/s25144385 | Abstract; Secs. 2-4 and Figs. 8-11 inspected from publisher page/search extract. | Different direct-ToF setups; supports stress-strata planning rather than a quantitative prediction for VL53L1X. |
| A full-support audit gives a valid original-time safety-risk bound. | [KILL] | No source supports this proposition as stated. | N/A. | It fails unless audit observation is shown to label the original time-anchored event or the target is explicitly narrowed. |

## Queries and failed searches

Date pinned: 2026-08-28. Primary/official sources were preferred; snippets generated leads only.

| Query / retrieval | Outcome |
| --- | --- |
| `"selective labels" "active sensing" edge safety 2024 OR 2025 OR 2026` | No direct physical edge audit-wake collision found; led to Chen 2025 and unrelated results. |
| `"inverse propensity" "wake-up" camera edge sensing 2024 OR 2025 OR 2026` | No direct collision found; results were predominantly unrelated causal/medical uses. |
| `"audit" "no wake" sensor safety risk edge 2024 OR 2025 OR 2026` | No direct collision found; strong vocabulary ambiguity with marine no-wake/audit material. |
| `"event-triggered sensing" "selective labels" 2024 OR 2025 OR 2026` | No exact paper located; supports only a bounded search observation. |
| `"random audit" "selective labels" safety "sensor"` | No physical-sensor direct neighbor located; retrieved general selective-label/audit literature. |
| `"risk auditing" "selective observation" machine learning` | No exact collision located; results were primarily governance/audit, not sensing. |
| `"known inclusion probability" "sensor" "audit"` | No direct edge-safety paper located; do not treat this absence as novelty evidence. |
| `"Uncertainty-triggered wake-up" "edge AI" 2026` | Located Ballet et al., a strong component collision. |
| `"energy proportional" vision IoT node 2026 event imager RGB` | Located Moosmann et al., a strong component collision; full paper needs final inspection. |
| `"Smart Adaptive Trigger Sensing"` and DOI retrieval | Located publisher/author metadata for Cui et al.; publisher full text returned 403, and the linked repository returned 404. Marked full-text details [GAP]. |
| Forward citation chain from Ballet (2026-05-28), Chen (ICML 2025), and Sadhuka (2026) | arXiv/PMLR pages expose citation links but no auditable, complete forward-citation list in the accessible interface. Citation-chain closure remains [GAP]; repeat via institutional Scholar/Scopus access before locking. |

## Unresolved uncertainties

- [GAP] A direct 2024-2026 paper combining all of: physical low-power sentinel, known-probability audit wakes of no-wake cases, correction/bounds, and an edge safety endpoint may exist outside the recorded databases/terms. Its absence from this audit is not a novelty result.
- [GAP] The exact available hardware, incremental power instrumentation, FYP duration, and ethics authorization remain unknown.
- [GAP] The candidate has not demonstrated a target event whose truth can be recovered after verifier wake delay; this is the largest identification risk.
- [GAP] No sample-size/risk tolerance has been chosen. Until it is, "conservative action" is a policy slogan, not a calibrated decision rule.

## Decision

PIVOT
