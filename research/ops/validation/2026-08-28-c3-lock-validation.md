# Validation Audit: 2026-08-28 C3 lock gate

## Decision investigated

Whether **C3** can be locked as a one-year undergraduate FYP after the user confirmed (i) purchasable low-cost hardware, (ii) a runnable demo by the end of 2026, and (iii) experiment expansion/optimization in the first half of 2027.

This is a falsification audit.  It treats C3 as a conditional empirical-boundary study only, never as a new failure detector, stress harness, or global novelty claim.  Labels: `[K]` source-verified; `[C]` candidate inference; `[GAP]` not verified; `[KILL]` defeats the stated form.

## Claim under test

The supplied claim is:

> On a preregistered held-out device/workload/fault cell, determine whether local resource telemetry (heartbeat inter-arrival, CPU, memory pressure, I/O, temperature) transfers beyond phi-accrual, Lifeguard where topology permits, percentile timeout, and one-signal rules at matched false-failover, detection-delay, and monitor-overhead budgets.

The operational decision is `continue / observe / fail over` for a local sensing or inference service.  A false failover creates a recorded-service interruption; a late failover extends a real service outage.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | `[KILL]` Pourreza and Narasimhan's UCC 2025 paper already combines heterogeneous Pi 4B/Jetson Nano edge hardware, heartbeat timeouts, CPU/memory/disk/cache/page-fault stress, resource/thermal signals, and the false-positive/detection-delay/overhead trade-off.  Its Sec. 3 explicitly places phi-accrual, Lifeguard, SafeTimer, and percentile/adaptive approaches in the comparison neighborhood.  Lifeguard itself is a resource/processing-health-aware SWIM extension. | Only a *fixed, cross-cell empirical protocol* remains.  Changing the rule or adding a resource feature is not a remaining distinction. | High collision. |
| 2. Exact-claim collision | `[K]` UCC 2025's Secs. 1-2 ask whether timeout configurations transfer across heterogeneous devices, workloads and stressors, then measure the same outcome family.  It does not, in the accessible author-supplied full text, report a preregistered source-versus-held-out device/workload/fault split or a common comparison of a frozen multi-signal policy against all of phi-accrual, Lifeguard, percentile timeout, and one-signal rules. `[GAP]` Absence from the accessible text is not evidence of absence.  EdgeStressBench's official bibliographic record confirms a 2026 paper, pages 300-306, but says access closed; this audit could not verify its protocol, artifact, or evaluation split. | A restricted answer about one *named, frozen policy family* on one held-out cell may still be different in task/evaluation design.  The supplied wording says whether telemetry helps in general, but does not name that family, so it is not yet a falsifiable exact claim. | Medium for the residual; low for any absence claim. |
| 3. Boundary / impossibility | `[KILL]` Under local observations only, a healthy process delayed by contention and a fail-slow/crashed process can emit the same finite prefix of heartbeat and resource observations.  Any deterministic policy restricted to that prefix takes the same action in both worlds; it cannot promise both no false failover and bounded detection of all real faults.  Chandra and Toueg formalize the setting with unreliable failure detectors in asynchronous crash-prone systems; Fetzer gives the direct perfect-detector impossibility statement and identifies extra timing/watchdog assumptions needed to evade it. | A finite, injected fault process and declared cost function make a *conditional* comparison identifiable.  The conclusion must be a transfer map or a no-gain result, not a universal detector guarantee or a causal diagnosis of the resource signal. | High for the no-universal-guarantee boundary. |

## Assumption and identification audit

1. **The target policy family is missing.** `[KILL]` “Whether local telemetry transfers” is existential unless the project freezes the permitted multi-signal rule family, training/tuning information, threshold-selection rule, and feature window before observing target-cell outcomes.  A post-hoc best-of-many rule would make even a negative result uninterpretable and a positive result a multiple-comparison artifact.  Required pivot: call the claim “the best policy in preregistered family `F`,” not “local telemetry” in general.

2. **Latent cause is not a label.** `[KILL]` CPU, memory, I/O, temperature and a late heartbeat cannot identify whether the service is harmlessly delayed, unavailable to clients, or permanently failed.  The experimental ground truth must be an injected, timestamped service contract: e.g., the next sensing/inference result did or did not reach the local failover controller before a frozen deadline.  Do not score “resource-stressed” as a class label.

3. **Detector and service need separable failure semantics.** `[KILL]` If heartbeat, monitoring, and the service run in the same process/cgroup, a stressor can simultaneously suppress the witness and the thing being witnessed.  The study then cannot tell a monitor failure from a service failure.  The demo must place the sensing service, monitor, and failover controller in separate processes with logged monotonic timestamps; the full study should additionally log process scheduling/resource stats from an observer process.

4. **Lifeguard changes the observation topology.** `[KILL]` Lifeguard is not merely a phi threshold: it is a SWIM membership protocol using direct and indirect probes, suspicion dissemination, and local detector health.  Its published design uses group members and independent suspicions.  A two-node heartbeat setup cannot truthfully describe an apples-to-apples Lifeguard comparison; a minimum three-peer topology is required if it remains a mandatory baseline.  Otherwise it must be reported as topology-inapplicable, not silently omitted.

5. **Matched budgets need an action-level definition.** `[KILL]` Equal F1, equal timeouts, or equal sample counts do not equalize the user story.  Freeze: (a) what creates a false failover, (b) restart/failover interruption duration, (c) detection deadline measured from the injected service-contract breach, (d) CPU, memory, network-message, and optional power measurements of the monitor, and (e) a common warm-up/tuning budget.  A remote probe/redundant task may be an oracle upper bound but cannot be a fair local-observation baseline.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Pourreza & Narasimhan, *When Timeouts Fail: Revisiting Fault Detection under Resource Stress in Edge Computing*, UCC 2025, version of record published 2025-12-31, https://doi.org/10.1145/3773274.3774280 | Pi 4B/Jetson Nano, six workloads, heartbeat timeouts, CPU/memory/disk/cache/page-fault stress; static timeout calibration. | False positives, detection sensitivity/latency, and overhead across device/workload/stressor combinations.  Secs. 1-2, pp. 1-3; related-work baseline family Sec. 3, pp. 3-4; setup/results Secs. 4-6, pp. 4-9; conclusion p. 10. | Scenario, observations, hardware class, stressors, and endpoint family. | `[KILL]` a new timeout-brittleness, resource-aware-detector, hardware, or stress-harness contribution.  Leaves only a precisely preregistered held-out comparison, if its exact split is verified distinct. |
| Dadgar, Phillips & Currey, *Lifeguard: Local Health Awareness for More Accurate Failure Detection*, arXiv:1707.00788v2, 2018-04-03, https://arxiv.org/pdf/1707.00788 | SWIM member probes, acknowledgements, suspicion messages, local-health counter; action is group-member suspect/fail. | False positives and true-failure detection time in controlled and deployed settings.  Abstract and Secs. I-III, pp. 1-4; local-health mechanisms Sec. IV, pp. 4-7; evaluation Sec. V, pp. 7-10. | Local processing-health adaptation to reduce spurious failure decisions under CPU/network stress. | `[KILL]` novelty of local-health awareness.  Requires C3 to compare a genuine SWIM/Lifeguard topology or declare it inapplicable. |
| Pourreza & Narasimhan, *EdgeStressBench: A Framework for Reproducible Evaluation of Edge Systems Under Resource Stress*, MobiSys Workshops 2026, pp. 300-306, https://doi.org/10.1145/3812836.3814778; official DBLP record dated 2026-07-04, https://dblp.org/rec/conf/mobisys/PourrezaN26 | `[GAP]` Full text/artifact was unavailable in this audit. | `[K]` Bibliographic fact only: workshop paper, authors, title, and pages. | Potential direct overlap with any stress-framework claim. | `[KILL]` Do not claim a new harness even if it cannot be retrieved; `[GAP]` do not state its exact protocol, repository, hardware coverage, or split without source access. |
| Theodoropoulos et al., *Intelligent Proactive Fault Tolerance at the Edge through Resource Usage Prediction*, arXiv:2302.05336, 2023-02-09, https://arxiv.org/abs/2302.05336 | CPU/RAM/bandwidth/disk telemetry; RNN prediction; replication/migration action. | Resource-model accuracy plus CloudSim Plus reliability/maintainability; Secs. 1 and 3, HTML pp. 1-5; limitations Sec. 6, p. 13. | Resource telemetry linked to proactive edge fault-tolerance action. | `[KILL]` any broad claim that observing edge resource signals before migration/failover is new.  Leaves a low-cost physical timeout-boundary protocol rather than a predictive method. |
| Tuli et al., *DeepFT: Fault-Tolerant Edge Computing using a Self-Supervised Deep Surrogate Model*, arXiv:2212.01302, 2022-12-02, https://arxiv.org/abs/2212.01302 | Resource/load data, fault prediction, task scheduling/migration. | Pi-based edge cluster; fault-detection and QoS metrics.  Sec. I, pp. 1-2; evaluation Sec. V, esp. results near pp. 9-10. | Edge overload, resource contention, migration/fault tolerance. | `[KILL]` a broad telemetry-to-migration model claim.  Its learned surrogate is not a like-for-like C3 baseline; it is a scope warning, not a required demo dependency. |

## Strongest simple baseline

The strongest practical kill baseline is **a tuned one-signal policy plus phi-accrual**, tuned only on source cells and evaluated once on the same held-out target cell.  Run the four single signals separately (CPU, memory pressure, I/O, temperature), not only the most convenient one.  If any one-signal policy or phi-accrual reaches the same held-out false-failover/detection-delay frontier with lower monitor resource cost, C3's multi-signal family has no contribution.

The required baseline set is therefore:

1. fixed timeout;
2. rolling-percentile timeout;
3. phi-accrual;
4. one signal at a time, using a frozen threshold family;
5. Lifeguard/memberlist only on the same three-peer topology; and
6. `always observe for one extra interval` as an action-policy lower-complexity baseline.

`Always fail over`, `never fail over`, and a remote/redundant-probe oracle should be reported as bounds.  They are not substitutes for the local detector comparison.

## Contrarian result

**C3 is not ready to lock in its present wording.**  UCC 2025 is the strongest direct neighbor: it already poses the edge resource-stress timeout trade-off on matching hardware and stresses, and explicitly names the adaptive detector family.  The only defensible residual is a small, predeclared transfer protocol, but the current claim lacks the policy family and common Lifeguard-compatible topology that make its answer falsifiable.  It would be misleading to turn that gap into “no one has tested this.”

The positive hypothesis can fail cleanly: one-signal or phi-accrual may match the held-out frontier, or every multi-signal policy may fail to transfer.  That is useful only if all thresholds and source/target roles were frozen beforehand.  If the study instead selects a detector after examining the target cell, it becomes an unrepeatable configuration search rather than a boundary result.

## Feasibility audit

| Requirement | Status under the corrected schedule | Gate / consequence |
| --- | --- | --- |
| End-of-2026 runnable demo | `[K]` Plausible in the remaining four months if limited to one sensing/inference service, timestamped fault injector, a failover action, fixed/percentile/phi baselines, and one safe stressor. | The demo is **not** evidence of cross-device transfer.  It must already emit raw action/resource logs needed for the later study. |
| First-half-2027 experiment expansion | `[C]` Plausible for two workloads, several declared fault processes, and repeated target-cell trials if the logging/data schema is fixed during the demo. | Treat these as a phased plan, not evidence that enough trials will be obtained. |
| Devices/topology | `[K]` The user permits self-purchase of inexpensive devices. `[GAP]` Exact board model, delivery date, router/network isolation, power instrument, and budget are not selected. | If Lifeguard stays mandatory, select at least three independent peer devices before the demo; two peers do not exercise its indirect-probe/suspicion design. |
| Labels | `[K]` Controlled fault injection can create timestamped service-contract labels without personal data. | Log injector intent and externally observed service output separately; never infer fault type from telemetry alone. |
| Ethics/safety | `[K]` A non-production benchtop sensing workload, synthetic requests, and isolated stress/failover events require no personal data. | Do not connect to production sensing, safety interlocks, or real maintenance action. |
| Compute | `[K]` Fixed thresholds, phi-accrual, and a small frozen rule family are laptop/board feasible. | `[KILL]` A learned predictor, hyperparameter sweep over target data, or an unbounded detector search breaks the claimed low-cost/one-year scope. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Static timeouts on Pi 4B/Jetson Nano under five resource stressors have the same false-positive/detection-delay/overhead problem family as C3. | `[KILL]` | Pourreza & Narasimhan, UCC 2025 version of record, published 2025-12-31, https://doi.org/10.1145/3773274.3774280 | Secs. 1-2, pp. 1-3; Sec. 3, pp. 3-4; Secs. 4-6, pp. 4-9; conclusion p. 10. | Kills detector/harness/broad problem framing, not automatically a predeclared transfer-study endpoint. |
| Lifeguard uses SWIM direct/indirect probing, gossip suspicion and local detector health; it is not a scalar timeout variant. | `[K]` | Dadgar et al., arXiv:1707.00788v2, 2018-04-03, https://arxiv.org/pdf/1707.00788 | Sec. I p. 1; Sec. III pp. 2-4; Sec. IV pp. 4-7. | The baseline applies only when C3 implements comparable group-membership topology. |
| A perfect failure detector cannot be implemented in the purely asynchronous crash model without extra assumptions. | `[K]` | Chandra & Toueg, *JACM* 43(2), 225-267, 1996, https://doi.org/10.1145/226643.226647; Fetzer, *IEEE Transactions on Computers* 52(2), 99-112, 2003, https://doi.org/10.1109/TC.2003.1176979 | Chandra & Toueg abstract and Sec. 2, pp. 225-231; Fetzer abstract and Sec. I, pp. 99-101. | Supports only the no-universal-guarantee boundary; C3's finite injected empirical comparison remains possible. |
| Resource-usage prediction with proactive replication/migration is an established edge-fault-tolerance component. | `[K]` | Theodoropoulos et al., arXiv:2302.05336, 2023-02-09, https://arxiv.org/abs/2302.05336 | Sec. 1 and Sec. 3; Sec. 6 limitations. | Simulation/method scope differs; it is a component-collision warning. |
| EdgeStressBench exact methods/artifact/evaluation split. | `[GAP]` | Pourreza & Narasimhan, MobiSys Workshops 2026, DOI https://doi.org/10.1145/3812836.3814778; DBLP metadata version 2026-07-04, https://dblp.org/rec/conf/mobisys/PourrezaN26 | DBLP record lines 98-104 and 149-150 read; publisher text unavailable. | Do not use an unverified artifact claim to assert distinction or feasibility. |

## Queries and failed searches

Queries run on 2026-08-28:

- `"When Timeouts Fail: Revisiting Fault Detection under Resource Stress in Edge Computing" PDF`
- `"EdgeStressBench: A Framework for Reproducible Evaluation of Edge Systems Under Resource Stress" PDF`
- `2025 2026 edge fault detection resource stress phi accrual timeout telemetry transfer study`
- `2024 2025 2026 edge systems failure detector resource telemetry heartbeat CPU memory false positives paper`
- `"resource-aware" "phi-accrual" failure detector`
- `"resource telemetry" "failure detector" heartbeat edge`
- `"local health awareness" "edge" failure detector CPU memory telemetry`
- `"adaptive failure detector" edge resource contention heartbeat telemetry`
- `Chandra Toueg unreliable failure detectors asynchronous system indistinguishable executions pdf`
- `site:github.com lifeguard SWIM failure detector implementation`

Failed/limited retrievals:

- The UCC official text was readable through discovery results but direct PDF retrieval did not yield a stable local page render in this round.  Section/page claims above are from the version-of-record structure and accessible text; re-render the paper before any thesis quote or exact numerical replication claim.
- EdgeStressBench full text and any repository/revision were not retrievable from its DOI/DBLP record.  The record explicitly marked access closed.  No result here establishes that an artifact is publicly available or that it lacks the proposed split.
- No inspected 2024-2026 primary source established the exact C3 pre-registered source-to-held-out comparison.  This is a retrieval limitation, **not** novelty evidence.

## Decision

**HOLD.**  Do not lock C3 until the coordinator freezes (1) the finite multi-signal policy family and tuning procedure, (2) a three-peer topology or an explicit Lifeguard-inapplicability boundary, (3) timestamped service-contract labels and common action-cost accounting, and (4) the exact UCC/EdgeStressBench split/artifact facts.  If those are written before the demo, C3 can be reconsidered as an Amber empirical boundary study; it cannot be locked as a new detector or stress framework.

HOLD
