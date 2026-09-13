# Validation Audit: 2026-08-28 current C3 and surviving alternatives

## Decision investigated

Whether the currently locked **C3** direction should remain a one-year, low-cost edge FYP after a fresh adversarial check of its closest 2025--2026 literature and its own registered protocol.  The user constraints are: a runnable benign benchtop demo by 2026-12, experiment expansion in 2027-H1, self-purchased inexpensive equipment, and no personal data, production deployment, or safety actuation.

This is a validation packet, not evidence of novelty.  I also checked the two still-plausible alternatives, B1 BLE proximity and C2 irrigation, only to determine whether either is ready to replace C3.

## Claim under test

C3's admissible claim is only this: a finite, source-tuned policy family that observes heartbeat suspicion and local Linux pressure/temperature telemetry is frozen before one device/workload/fault cell; on that untouched cell, determine whether it improves the false-failover / service-contract-delay / monitor-overhead frontier over fixed and percentile timeouts, phi-accrual, each one-signal policy, observe-one-extra-interval, and three-peer Lifeguard.

It must not claim a new failure detector, a new stress framework, general resource-aware fault detection, or a universal detection guarantee.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | `[KILL]` UCC 2025 already joins edge hardware, heterogeneous workloads, controlled CPU/memory/disk/cache/page-fault stress, timeout-driven failure decisions, and CPU/memory/I/O/temperature observations.  Its related-work discussion places phi-accrual, Lifeguard, percentile/adaptive timeout, and resource-aware detectors in the same neighborhood.  EdgeStressBench 2026 adds parameterized stress injection, structured system/application measurement, heterogeneous Pi/Jetson execution, optional replication-aware modes, and an announced open artifact. | Only the deliberately frozen **source-to-one-held-out-cell comparison of a named finite policy family** is not established by the inspected descriptions.  This is an evaluation-protocol distinction, not a mechanism distinction. | High collision; low-to-medium confidence in the residual because the EdgeStressBench full text/artifact could not be inspected. |
| Exact-claim collision | `[K]` UCC 2025 explicitly asks whether timeout configurations transfer across device, workload, and stress scenarios, and measures false positives, detection sensitivity/delay, and overhead.  That is the same high-level question and endpoint family. | `[GAP]` The accessible UCC text describes static timeout configurations, not C3's source-only selection of a 1,344-member telemetry family followed by a frozen evaluation against phi, Lifeguard, one-signal, and observe baselines.  EdgeStressBench's accessible abstract describes a reusable evaluation framework, not the detector-policy comparison or data split.  Retrieval failure is not evidence that no exact collision exists. | High risk: a reviewer can reasonably view C3 as a stricter test split of UCC's question unless its protocol and result are unusually clean. |
| Boundary / impossibility | `[KILL]` A healthy-but-contented service and a fail-slow or failed service can share a finite prefix of heartbeat and resource observations.  A policy restricted to that prefix must take the same action in both executions; it cannot promise both zero false failovers and uniformly bounded detection for all faults. | A finite injected service-contract process with an externally recorded deadline makes a conditional empirical comparison possible.  The paper may report only the declared board, workload, fault process, horizon, and action costs. | High for the no-universal-guarantee boundary. |

## Assumption and identification audit

1. **The tested intervention is weaker than the story implies.** `[K]` In the locked protocol, every member of `F` first uses `phi`; resource telemetry does not identify a failure or trigger failover by itself.  It only changes a high-phi action from immediate failover to `observe` when pressure is high.  The actual claim is therefore *whether a pressure-conditioned wait is useful after phi*, not whether multi-signal telemetry detects failures.  The required `observe-one-extra-interval` baseline directly attacks this distinction.

2. **Source-only selection is still a substantial configuration search.** `[K]` The registered family has `4` phi quantiles, `4` single-signal choices with `4` thresholds, `6` two-signal choices with `4 x 4` thresholds, and `3` wait lengths: `4 x (4 x 4 + 6 x 4 x 4) x 3 = 1,344` candidate tuples.  `[GAP]` No source-episode count, independent tuning/selection split, multiplicity treatment, or confidence-interval rule is registered.  Selecting the source p95 winner from sparse episodes can select noise; a single target cell cannot repair that uncertainty.

3. **One target cell is a demonstration, not an estimate of transferability.** `[K]` The protocol deliberately leaves one compound cell untouched.  A result may truthfully say that this exact policy did or did not transfer to that one cell.  `[KILL]` It cannot establish that telemetry is transferable across devices, workloads, or faults generally.  At least two predeclared target cells or a carefully worded one-cell result is required; the latter remains weaker than the title-level story.

4. **The local-observation boundary must include monitor failure.** `[C]` CPU PSI, memory PSI, I/O PSI, and temperature must come from an agent on or near the node being judged.  Under node starvation/crash, a missing metric can be caused by monitor starvation, transport loss, or the service fault itself.  Separate service, monitor, controller, and injector processes plus an external result trace make the service-contract label usable, but they do not identify the causal meaning of each resource signal.  The paper must not claim resource-root-cause diagnosis.

5. **Topology and action cost are still critical-path procurement gates.** `[K]` Lifeguard is a SWIM protocol with direct/indirect probes, suspicion dissemination, and local-health mechanisms, not a scalar threshold.  A genuine comparison needs three independently running peers.  `[GAP]` The active protocol still has no chosen boards, local AP, power meter, action interruption measurement, or delivered bill of materials.  The year is adequate only if the December demo proves the trace and restart/routing semantics before buying into the full comparison.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Pourreza & Narasimhan, *When Timeouts Fail: Revisiting Fault Detection under Resource Stress in Edge Computing*, UCC 2025, version of record published 2025-12-31, https://doi.org/10.1145/3773274.3774280 | Pi 4B and Jetson Nano, six workloads, static heartbeat timeouts, five resource stressors, resource and thermal measurement. | Its Sec. 1 and Sec. 2, pp. 1--3, state false-positive/detection-delay/overhead trade-offs and ask whether timeout settings transfer across heterogeneous edge scenarios; Sec. 3, pp. 3--4, lists adaptive-neighbor families; setup/evaluation Secs. 4--6, pp. 4--9. | Same operational failure story, hardware class, stress family, metrics, and cross-condition concern. | `[KILL]` new detector, new stress harness, static-timeout-brittleness, or generic multi-metric contribution.  Leaves only a tightly registered detector-comparison split, subject to the high exact-claim risk. |
| Pourreza & Narasimhan, *EdgeStressBench: A Framework for Reproducible Evaluation of Edge Systems Under Resource Stress*, MobiSys Workshops 2026, pp. 300--306, https://doi.org/10.1145/3812836.3814778 | Official abstract: workload orchestration, parameterized stress injection, structured application/system measurements, heterogeneous devices, optional replication-aware execution. | Published 2026-06-02; the available official bibliographic metadata and abstract say it releases code, workloads, configurations, and scripts.  Exact paper sections, artifact repository, baseline detectors, and split are `[GAP]`: ACM PDF retrieval was blocked. | It overlaps C3's practical experimental apparatus and reproducibility framing. | `[KILL]` any claim to a new testbed, injection workflow, tracing format, or reproducibility artifact.  It may also prove exact-protocol collision once full text/artifact is read. |
| Dadgar, Phillips & Currey, *Lifeguard: Local Health Awareness for More Accurate Failure Detection*, arXiv:1707.00788v2, 2018-04-03, https://arxiv.org/pdf/1707.00788 | SWIM direct/indirect probes, gossip suspicion, local health score; action is member suspicion/failure declaration. | Secs. III--IV, pp. 2--7; evaluation Sec. V, pp. 7--10. | Local processing-health-aware response to spurious failure detection. | `[KILL]` local-health awareness as a new idea; requires genuine three-peer implementation or an explicit topology-inapplicable boundary. |
| Theodoropoulos et al., *Intelligent Proactive Fault Tolerance at the Edge through Resource Usage Prediction*, arXiv:2302.05336v1, 2023-02-09, https://arxiv.org/abs/2302.05336 | CPU/RAM/bandwidth/disk telemetry predicts resource behaviour before replication/migration. | Secs. 1 and 3, pp. 1--5; limitations Sec. 6, p. 13. | Resource telemetry drives edge fault-tolerance action. | `[KILL]` the broad premise that telemetry-guided failover is new; different learned/simulation scope does not remove C3's narrower possible evaluation distinction. |
| Filus et al., *Cost-effective filtering of unreliable proximity detection results based on BLE RSSI and IMU readings using smartphones*, *Scientific Reports* 12, Art. 2440, 2022-02-14, https://doi.org/10.1038/s41598-022-06201-y | RSSI plus local IMU determines prediction reliability and filters unreliable proximity results. | Abstract; “System overview” and “Results” sections (article-number pagination). | B1's proposed `record / abstain` reliability framing and cheap local sensing components. | `[KILL]` any B1 claim that adding local quality/reliability evidence to BLE proximity and filtering/abstaining is new.  RSS-only finite-panel wording is not thereby proven identical. |

## Strongest simple baseline

For C3, the decisive baseline is **source-tuned phi-accrual plus `observe one extra interval`**.  It has the same observation/action vocabulary but does not need PSI/temperature collection.  It must be tuned under the same source-only schedule and evaluated once on each untouched target episode.  Any multi-signal member of `F` that does not beat this policy, a one-signal rule, and Lifeguard at the same false-failover and monitor-cost budgets is not a contribution.

For B1, the strong baseline is an RSS rolling median with a fixed abstention band and no added reliability model.  For C2, it is a deterministic irrigation threshold plus `wait / inspect`; neither alternative currently has a source-verified experimental story that defeats its simple baseline.

## Contrarian result

**C3 should be HOLD, not treated as securely innovative.**  UCC 2025 already asks the central cross-condition timeout-transfer question, and EdgeStressBench now explicitly packages almost all of the planned apparatus.  The only remaining difference is a rigorous source-only detector-comparison protocol.  That can be a defensible undergraduate empirical boundary study, but only if it is presented as such and its exact overlap with EdgeStressBench is resolved.

**B1 remains HOLD, not a replacement.**  Its reliability/abstention mechanism collides with BLE RSSI+IMU filtering, while RSS-only has an obvious median+abstain baseline and physical non-identifiability.  **C2 remains HOLD.**  Soil-sensor uncertainty is real, but no authorized crop/irrigation protocol, reference measurement, or season/controlled planter plan has been supplied; a one-year benchtop demo would otherwise only be a dashboard around a threshold.

## Feasibility audit

| Requirement | C3 finding | Consequence |
| --- | --- | --- |
| End-2026 demo | `[K]` A three-peer benchtop service, one safe stressor, a contract trace, and fixed/percentile/phi baselines fit the stated schedule in principle. | Make this a procurement/logging gate, not evidence of the transfer claim.  Demonstrate process separation and observable restart/routing first. |
| 2027-H1 experiment | `[C]` Repeated runs on a finite policy family are plausible only after reducing the family or predeclaring enough independent source episodes. | Freeze target cells and policies before source tuning; do not add features after the demo. |
| Hardware/data/ethics | `[K]` No personal data, production connection, or safety actuation is needed; controlled service outputs supply labels. `[GAP]` exact SBC/AP/power-meter/restart mechanism and cost are still absent. | Select a three-board BOM and a low-risk restart/routing action before implementation. |
| Baseline availability | `[K]` timeout, percentile, phi, and one-signal baselines are straightforward. `[C]` Lifeguard can be run through an existing SWIM implementation, but this audit did not execute one. | If genuine three-peer Lifeguard cannot run, state it as topology-inapplicable and weaken the claim rather than substituting a scalar timeout. |
| Alternative feasibility | `[KILL]` B1 can be built cheaply but not yet distinguished; `[KILL]` C2 needs an agronomy/reference/data gate that has not been shown feasible for the schedule. | Do not replace C3 with either candidate on feasibility alone. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| UCC 2025 already studies edge timeout calibration under Pi/Jetson hardware, resource stress, and the false-positive/delay/overhead outcome family, and explicitly asks cross-scenario transfer of timeout settings. | `[KILL]` | Pourreza & Narasimhan, UCC 2025 VOR, 2025-12-31, https://doi.org/10.1145/3773274.3774280 | Sec. 1 and Sec. 2, pp. 1--3; Sec. 3, pp. 3--4; Secs. 4--6, pp. 4--9; conclusion p. 10. | Kills broad framing; does not itself verify C3's exact frozen-policy comparison. |
| EdgeStressBench is a 2026 follow-up with orchestration, parameterized stress, structured measurement, heterogeneous devices, replication-aware modes, and an announced artifact. | `[K]` for metadata/abstract; `[GAP]` for details | Pourreza & Narasimhan, MobiSys Workshops 2026, DOI https://doi.org/10.1145/3812836.3814778; OpenAlex VOR metadata, 2026-06-02; Semantic Scholar abstract retrieved 2026-08-28. | Published pp. 300--306; full PDF and repository retrieval blocked, so section/page and implementation details were not read. | Never claim a new stress framework; exact detector/split collision remains unverified. |
| Lifeguard is a local-health-aware SWIM protocol rather than a scalar timeout. | `[K]` | Dadgar et al., arXiv:1707.00788v2, 2018-04-03, https://arxiv.org/pdf/1707.00788 | Secs. III--IV, pp. 2--7; Sec. V, pp. 7--10. | Requires group-membership topology. |
| Purely asynchronous failure detection cannot offer both perfect accuracy and timeliness without additional assumptions. | `[K]` | Chandra & Toueg, *JACM* 43(2), 1996, https://doi.org/10.1145/226643.226647; Fetzer, *IEEE TC* 52(2), 2003, https://doi.org/10.1109/TC.2003.1176979 | Chandra & Toueg Sec. 2, pp. 225--231; Fetzer Sec. I, pp. 99--101. | Limits only universal claims; finite injected comparison is allowed. |
| BLE proximity reliability filtering from RSSI plus local IMU is established. | `[K]` | Filus et al., *Scientific Reports* 12, Art. 2440, 2022-02-14, https://doi.org/10.1038/s41598-022-06201-y | Abstract; “System overview”; “Results.” | Component collision for B1, not proof against a precisely restricted RSS-only panel. |
| C3 has a 1,344-member policy family and lacks registered source episode count/multiplicity control. | `[K]` / `[GAP]` | C3 locked protocol, 2026-08-28, `research/active/04-c3-locked-protocol.md`. | “Exact empirical claim (Amber)” parameter bullets. | Arithmetic is derived from the frozen family; missing evaluation quantities are protocol gaps, not literature facts. |

## Queries and failed searches

Queries executed 2026-08-28:

- `"fault detection" "resource stress" edge computing telemetry timeout 2024 2025 2026`
- `"failure detector" "resource usage" "phi accrual" 2024 2025 2026`
- `"cross-device" "failure detection" edge resource telemetry 2025`
- `"resource metrics" "failure detection" "cross workload" edge`
- `"EdgeStressBench" GitHub`
- `BLE RSS proximity abstention uncertainty edge sensing 2024 2025 2026 paper`
- `low cost soil moisture irrigation decision uncertainty sensor disagreement 2024 2025 2026 paper`

Failed/limited retrievals:

- ACM direct PDF URLs for UCC 2025 and EdgeStressBench returned Cloudflare HTTP 403 in this round.  The UCC official page exposed substantial article text; EdgeStressBench claims above are limited to its official metadata/abstract and page range.
- GitHub repository search for `EdgeStressBench` returned no repository under that exact name, despite the abstract's artifact-release statement.  This is `[GAP]`, not evidence that the artifact is absent.
- No source obtained in this round establishes that EdgeStressBench did, or did not, run C3's exact frozen-family, source/target split, or all named detector baselines.
- No new 2024--2026 primary source was obtained that saves B1 or C2 from their stated baseline and feasibility gates.

## Decision

**HOLD.**  Keep C3 only as an **Amber, conditional empirical-boundary study**.  Before declaring it locked for thesis execution, perform one decisive retrieval gate: obtain and inspect the EdgeStressBench paper/artifact, then compare its exact task, policy tuning, target split, topology, and metrics line by line with C3.  In parallel, reduce or statistically register the 1,344-policy source-selection process and predeclare at least two target cells, or explicitly narrow the written conclusion to a single target cell.

Do not promote B1 or C2 as replacements: both remain **HOLD** and require new direct-neighbor plus feasibility evidence.

HOLD
