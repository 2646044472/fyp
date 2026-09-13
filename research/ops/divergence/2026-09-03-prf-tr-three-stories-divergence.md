# Divergence Packet: 2026-09-03 PRF-TR Three Deployment Stories

## Decision investigated

Whether the existing physical-versus-digital camera-failure audit can be turned into a defensible undergraduate FYP by changing the **paper identity and operational decision**, rather than by inventing a new decoder or adaptive sensing algorithm. I compared three sharply different stories:

1. `DEPLOY-GATE`: a commissioning/release gate for a fixed camera-and-decoder configuration;
2. `ACTION-RANK`: a finite physical-versus-digital transfer study for the action `retain / reacquire / unknown`;
3. `ACOUSTIC-RANK`: a non-optical analogue using a local microphone and an independently labelled non-personal machine event.

The packet is a divergence proposal only. It does not modify `research/active/`, the archive, or `.research/`.

## Search boundary

**Date and scope.** Searches were run on 2026-09-03. I inspected arXiv records and PDFs/preprints, official conference or publisher pages, an official standards page/preview, and primary dataset papers. The boundary was: edge or embedded sensing; real versus synthetic/physical corruptions; camera deployment/health validation; active reacquisition or fault diagnosis; and non-personal acoustic or vibration sensing. No global novelty claim is made.

**Hardware and data assumed.** The current charter confirms a Raspberry Pi 5B, RGB camera, NoIR camera, IR illuminator, adapters, a one-year FYP window, and no personal data, production service, or safety actuation. A rigid fixture, non-personal printed marker and optional power/light instruments are allowed. A microphone, machine fixture, or independent tachometer is *not* confirmed as owned or attached to a real workflow.

**Current protocol read.** I read `research/active/09-physical-transfer-pilot-protocol.md`, `10-polarization-glare-pilot-protocol.md`, `11-cross-device-action-rank-pilot.md`, and `12-pilot-execution-gates.md`. The common admissible endpoint is an independently decoded exact printed payload. The current strongest controls are fixed RGB, fixed NoIR+IR, fixed two-shot, scalar quality thresholds, random action, and an oracle upper control. The protocol already forbids a universal claim that synthetic corruptions are invalid.

**Search queries.**

- `synthetic corruptions reliable proxy real-world corruptions semantic segmentation Agnihotri`
- `camera deployment acceptance validation physical lighting occlusion edge vision`
- `camera health monitoring downstream task physical state camera`
- `active perception fault diagnosis reacquire intervention edge vision`
- `sensor fault benchmark clean ranking worst scenario fault-time error`
- `industrial machine sound dataset operational environmental domain shift MIMII`
- `physical synthetic corruption transfer acoustic sensor decision`
- `exact marker difficult lighting adaptive exposure reacquisition`

## Recent-paper limitation map

### 1. The broad synthetic-versus-real claim is already occupied

[K] Agnihotri et al., *Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?* (arXiv v1, 2025-05-07), compares real and synthetic corruption performance and reports strong mean correlation but weaker, corruption-specific relationships. The paper's object is model robustness evaluation, not an edge action policy, but it directly kills the sentence “digital corruption tests do not represent reality.” The residual must be a finite, named camera pair, named physical cells, and an independently measured operational endpoint.

### 2. Marker decoding and difficult-light robustness are not the contribution

[K] DeepArUco++ (Image and Vision Computing 152, 105313, 2024; arXiv:2411.05552) already studies detection, corner refinement and decoding of square fiducial markers under challenging lighting, including synthetic-to-real mismatch and wrong IDs from difficult image conditions. [K] Ren, Lensgraf and Quattrini Li (arXiv:2404.12055, 2024) already study active exposure control for field fiducial markers. A Pi decoder, IR image enhancement, exposure heuristic, or “confidence below threshold means retry” would be a component collision.

### 3. Active diagnosis and screen/confirm acquisition are direct neighbours

[K] Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems* (arXiv v1, 2025-09-22), formalizes passive and active FDI, including control selection by Effective Information. [K] Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning* (Sensors 26(16):5065, published 2026-08-10), combines low-cost screening, confirmation acquisition, uncertainty/OOD escalation, watchdogs, and resource costs. These papers kill a new causal-diagnosis or generic adaptive-acquisition mechanism. They do not by themselves establish the exact finite RGB/NoIR marker endpoint, so a bounded action audit remains an empirical possibility.

### 4. Deployment validation and passive camera health already have standard forms

[K] ISO 12233:2024 defines digital-camera resolution and spatial-frequency-response measurement and explicitly frames test-chart measurement as useful for manufacturing testing and quality-control monitoring. [K] Wischow et al., *Monitoring and Adapting the Physical State of a Camera for Autonomous Vehicles* (arXiv:2112.05456, 2021), connects camera physical condition to downstream object-detection capability and parameter adaptation. [K] Ma, Yan and Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions for Camera Tamper Monitoring* (arXiv:2607.14760 v1, 2026-07-16), gives a recent auditable passive health monitor with explicit in-scope/out-of-scope camera fault signatures. Therefore a chart, blur score, lens-health index, or passive camera-release classifier is not a defensible new method. A deployment story can survive only as a question about whether **physical cell evidence changes a release decision beyond these controls**.

### 5. Fault-stress benchmarking already uses rank disagreement as a useful endpoint

[K] Windmann et al., *Benchmarking Sensor-Fault Robustness in Forecasting* (arXiv v1, 2026-05-11), defines SensorFault-Bench with eight fault scenarios, a disjoint fault-transfer split, worst-scenario fault-time error, and clean-MSE versus fault-time ranking disagreement. It is forecasting rather than marker decoding and does not settle the proposed optical action endpoint, but it kills any broad claim that “ranking models under faults” is itself new. The optical study must distinguish its action, observation model, and exact independent oracle from the benchmark.

### 6. A non-optical analogue already has rich domain-shift and anomaly neighbours

[K] Purohit et al., *MIMII Dataset: Sound Dataset for Malfunctioning Industrial Machine Investigation and Inspection* (DCASE/Zenodo dataset paper, 2019), supplies non-personal industrial-machine sounds with normal and abnormal machine conditions. [K] Koizumi et al., *MIMII DUE: Sound Dataset for Malfunctioning Industrial Machine Investigation and Inspection with Domain Shifts Due to Changes in Operational and Environmental Conditions* (WASPAA 2021, DOI:10.1109/WASPAA52581.2021.9632802), explicitly adds operational and environmental domain shifts. This makes an acoustic anomaly detector, a new noise augmentation, or a Pi microphone demo a poor thesis mechanism. An acoustic analogue could only be an action-rank/transfer audit, and it still lacks a confirmed user-owned repeated workflow in this project.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| `DEPLOY-GATE` | A technician or integrator decides whether a fixed RGB/NoIR printed-marker capture configuration may be released for a named non-personal station. A false release lets bad codes enter a local maintenance log; an unnecessary “do not release” decision costs a commissioning visit. Edge matters because commissioning has a time/energy budget and raw frames cannot be sent to a remote quality oracle. | Does adding a small, preregistered set of **physical** failure cells to a digital-corruption/quality gate change the release decision or its held-out false-retain bound, compared with a chart/IQA gate and a digital-only gate? The contribution is a deployment-validation protocol or empirical boundary, not a new gate learner. | ISO 12233:2024 chart/SFR metrology; Wischow et al. 2021 camera-condition monitoring; Ma et al. 2026 passive camera-health monitoring; Agnihotri et al. 2025 synthetic-versus-real robustness audit. | Kill if digital-only, ISO-style chart/IQA, or fixed two-shot controls make the same release decision on blocked physical cells; if the physical sample is too small to make a non-vacuous decision; if the gate only detects a known chart failure; or if no independent repeated commissioning decision exists. | Existing Pi/cameras and printed targets suffice. Needs a predeclared installation-like station, held-out covers/lamp cells, independent exact-code oracle, and a defensible commissioning actor. Without a real commissioning workflow, it is only a lab validation protocol. |
| `ACTION-RANK` | A local maintenance logger sees one printed indicator and chooses `retain`, `reacquire`, or `unknown`. False retain corrupts a work record; reacquisition costs latency, energy and operator attention. Edge matters because the decision is made at capture time without a cloud quality oracle. | On a finite, blocked RGB/NoIR setup, do digital-corruption cells preserve the ordering of capture actions on physical cells? More specifically, can a source-calibrated cheaper action be shown to lose on a held-out physical cell while fixed two-shot, scalar-quality and always-reacquire controls do not erase the risk-cost advantage? | Agnihotri et al. 2025 (proxy validity); SensorFault-Bench 2026 (fault-time ranking disagreement); DeepArUco++ 2024 (marker under hard lighting); Ren et al. 2024 and Bian et al. 2026 (active capture/control). The distinction is the finite action endpoint plus an exact independent payload oracle, not a generic transfer or adaptive method. | Kill if source and physical action rankings agree within the declared interval; fixed two-shot, scalar brightness/blur/IR-ratio, or always-reacquire is Pareto-optimal; the two physical worlds have overlapping permitted observations but different best actions; or labels/oracle are not independent. | Highest current feasibility: owned Pi and cameras, non-personal targets, simple decoder, controllable cover/light cells. Needs rigid mount, exact payload manifest, logged exposure/WB/timing, and preferably inline energy measurement. It still needs a real story or should be labelled a finite benchmark rather than field maintenance research. |
| `ACOUSTIC-RANK` | A maintenance operator decides whether a non-personal machine-sound clip should enter a local log, be recorded again, or be inspected. False retain records a false “normal” event; repeated recording costs time/energy. The acoustic sensor can be mounted outside a machine enclosure where an optical view is unavailable. | For a named microphone/fixture, do digitally injected noise, clipping, dropout and reverberation preserve the action ranking induced by physically blocked, shifted or contaminated microphone captures? The endpoint is action loss against a synchronized non-optical witness, not anomaly-classifier AUC. | MIMII 2019 and MIMII DUE 2021 occupy industrial sound/anomaly and domain-shift datasets; SensorFault-Bench 2026 occupies fault-stress/ranking evaluation; active sensor acquisition literature occupies screen/confirm actions. The residual is only a finite acoustic physical-vs-digital audit. | Kill if a direct tachometer/contact sensor is allowed and solves the decision more cheaply; if a fixed full-window recording or ordinary energy/SNR threshold dominates; if MIMII labels cannot support the operational action; if the microphone fault and machine state are not independently separable; or if no repeated real workflow is available. | Medium/low. Requires a microphone, a safe non-personal machine fixture, synchronized independent truth, acoustic safety/noise control, and a real repeated process. No current resource or workflow confirms these. Do not purchase hardware for this candidate before an access check. |

## Top two formalizations

### A. `ACTION-RANK`: finite physical-versus-digital action transfer

**[D] Objects.** Let `c` be a preassigned physical cell (clean, low visible light, transparent cover, glare, opaque occlusion, IR blocked, or frame interruption); `z` be the policy-visible prefix and logged camera controls; `a` be one allowed action in

\[
 A = \{\text{RGB},\ \text{NoIR+IR},\ \text{fixed two-shot},\ \text{reacquire},\ \text{unknown}\}.
\]

Let `y(c,a)` be the independent exact-payload outcome, not the decoder confidence, and let `L(c,a)` be a preregistered loss such as

\[
 L(c,a)=\lambda_{FR}FR(c,a)+\lambda_UU(c,a)+\lambda_JJ(c,a),
\]

where false-retain, unknown/reacquisition and measured joules encode the story. The cell oracle defines `a*(c)=argmin_a L(c,a)` only for analysis; it is not available to the runtime policy.

**[A] Assumptions.** Physical labels are assigned by the fixture script before capture; the payload truth is checked by an independent decoder or flatbed/phone oracle; exposure/white balance and trigger timing are fixed or logged; source and held-out lamp/material/device cells are blocked before threshold tuning; the target is static so sequential RGB/NoIR timing is measured rather than silently ignored.

**[T] Candidate empirical claim.** A source-calibrated action ordering or policy can fail to transport from declared digital cells to a held-out physical cell, and the failure remains after comparison with fixed two-shot, scalar quality, random and always-reacquire controls. The claim is deliberately finite: it is about the purchased camera pair and declared cell family, not camera populations or all physical failures.

**Observable outcome.** Per session and cell: exact payload validity, false-retain, unknown, action latency, joules, trigger-to-frame interval, exposure/gain/WB, and action-loss ranking. The primary unit is a session-by-cell pair, not an individual frame.

**Minimal counterexample.** Construct two preassigned worlds with matched RGB preview and permitted metadata: `D`, clean optical path with low visible light where IR helps; and `F`, transparent film/cover whose visible appearance is matched but whose IR path is attenuated/scattered. If their observed `z` distributions overlap while their best actions differ, no policy of `z` alone can certify both. This is a target-functional non-identifiability result, not evidence for a larger model.

**Negative-result value.** A rank-preservation result bounds the purchased setup and tells the field that the digital test suite is adequate for this action endpoint under the declared cells. A Pareto tie kills the mechanism and leaves a reproducible physical-transfer benchmark. Both results are useful if the protocol and exclusions are frozen before data collection.

### B. `DEPLOY-GATE`: release decision under a finite physical commissioning budget

**[D] Objects.** Let `q` be a commissioning evidence set of at most `m` captures; `g(q)` be a release action in `{release, reject, collect-more}`; `theta` be a fixed camera/decoder configuration; and `R_theta(P)` be the future false-retain risk over a declared station-cell distribution `P`. The independent payload oracle supplies the outcome labels for the commissioning and held-out cells.

**[A] Assumptions.** The release target is a named non-personal station, not an unknown population; the physical-cell distribution is declared before the gate; chart/IQA, digital-only, fixed two-shot and always-physical-test baselines are available; release is a documented commissioning decision, not a post-hoc researcher label; the station has a real budget that prevents exhaustive physical testing.

**[T] Candidate empirical claim.** A small physical-cell sample changes the release/no-release decision or gives a materially less misleading held-out risk estimate than digital-only and chart/IQA gates at equal commissioning cost. This is not a new confidence-bound theorem unless the sampling assumptions and non-vacuous finite-sample calculation are supplied.

**Observable outcome.** Gate decision, held-out exact-code false-retain and availability, number of physical captures, commissioning time/joules, and disagreement between digital-only and physical-aware release decisions. The gate must be evaluated on a blocked station cell, not on the same captures used to choose thresholds.

**Minimal counterexample.** Two configurations have identical chart SFR and JPEG quality but differ in a local transparent-cover/IR interaction that changes exact-code failure. If the physical sample contains no such cell, a digital/chart gate cannot distinguish them. Conversely, if the physical sample always includes it and the fixed test wins, the proposed value of the gate disappears.

**Negative-result value.** A null establishes that a cheap chart/digital test is sufficient for the declared station family, avoiding unnecessary physical commissioning. A non-vacuous positive requires more than a lower-quality score: it requires a changed release decision and held-out outcome at matched commissioning cost.

## Candidate-specific execution sketches

### `DEPLOY-GATE`

- **Actor and decision:** a technician or system integrator decides whether a fixed marker-capture configuration is ready for one named station.
- **Failure consequence:** false release admits wrong codes to a maintenance record; false rejection triggers another commissioning visit. No safety, legal, identity or payment claim.
- **Edge constraint:** local commissioning time and energy are bounded; raw frames are not sent to a remote evaluator. This constraint matters only if a remote oracle is genuinely unavailable or too late.
- **Inputs:** a small physical commissioning set, digital transformations of clean captures, chart/SFR or simple quality features, decoder output, exposure/WB/timing and energy.
- **Action:** `release`, `reject`, or `collect-more`; the action is an operational gate, not a semantic class.
- **Primary metric:** held-out false-release probability at a fixed commissioning budget, with availability and cost as secondary axes.
- **Strongest baseline:** a fixed ISO-style chart/quality gate plus digital corruptions; an always-run physical test is an upper-coverage control.
- **Smallest experiment:** two camera configurations or two named station conditions, one chart/quality set, one transparent-cover/low-light two-world pair, and three blocked commissioning repetitions. This is a gate test, not enough for a population claim.
- **Data/hardware/compute:** existing Pi/cameras, marker sheets, cover film, rigid fixture, stable lamp; no training required. A truly external integrator or repeated station access is the critical missing resource.
- **Advisor requirement:** someone able to review acceptance sampling, evaluation design and the distinction between an engineering validation protocol and a method paper.
- **Kill condition:** no documented actor decision, gate decisions are determined by a known chart metric, or physical samples are too few to make the release conclusion non-vacuous.
- **Pivot value:** retain as the commissioning chapter of `ACTION-RANK`, or publish only a bounded protocol/negative result.

### `ACTION-RANK`

- **Actor and decision:** a local logger decides whether to retain one marker record, reacquire through the other camera path, or mark it unknown.
- **Failure consequence:** false retain corrupts a non-personal maintenance record; a reacquire consumes measurable latency, joules and operator attention.
- **Edge constraint:** the decision must occur before a remote review and without a cloud quality oracle. A weak-network story is invalid until capture deadline and upload delay are measured.
- **Inputs:** RGB/NoIR frame prefix, decoder status, scalar quality, camera controls, physical cell identity only for offline analysis.
- **Action:** RGB, NoIR+IR, fixed two-shot, reacquire, or unknown, with declared capture budget.
- **Primary metric:** conditional action loss and its Pareto frontier; report exact-code false-retain separately from unknown and energy.
- **Strongest baseline:** fixed RGB-then-NoIR+IR two-shot and always-reacquire; scalar brightness/blur/IR-ratio is the strongest no-learning selector.
- **Smallest experiment:** clean, low-light and transparent-cover cells; one held-out lamp/material cell; at least three sessions and 20 captures per action/session as a feasibility minimum; independent payload truth.
- **Data/hardware/compute:** owned Pi/cameras and non-personal targets; rigid mount and exact manifest; optional inline power meter. No model training in the first gate.
- **Advisor requirement:** review of causal leakage, action-cost design, blocked splits and whether a finite empirical boundary is acceptable as an FYP identity.
- **Kill condition:** rank preservation, fixed two-shot Pareto dominance, non-identifiable worlds, or loss of independent labels/oracle.
- **Pivot value:** a clean negative benchmark that prevents future use of misleading digital corruption tests, or a configuration-specific optical intervention result if a named IR effect survives.

### `ACOUSTIC-RANK`

- **Actor and decision:** a technician decides whether a non-personal sound clip from a named machine event can enter a local log, should be recorded again, or requires inspection.
- **Failure consequence:** a false normal/accepted clip hides a machine event in the record; re-recording costs time and energy.
- **Edge constraint:** the microphone is outside an enclosure and the node must decide locally; a contact sensor or remote audio review is presumed unavailable. This presumption must be confirmed, not invented.
- **Inputs:** short waveform prefix, microphone telemetry, local energy/latency, and a predeclared event schedule. Digital cells add noise, clipping, missing frames and reverberation; physical cells use obstruction, mount change and environmental noise.
- **Action:** `retain`, `re-record`, or `unknown`; independent truth is a synchronized tachometer/command schedule or an independently labelled normal/abnormal event.
- **Primary metric:** false-retain and event-loss risk at equal capture/energy budget; AUC is secondary and should not be the thesis endpoint.
- **Strongest baseline:** direct tachometer/contact witness if allowed, then fixed full-window recording, energy/SNR threshold, and always-re-record.
- **Smallest experiment:** one safe low-voltage fan, one microphone placement, one independent truth channel, two physical perturbations, matched digital perturbations, and held-out mounting/noise sessions.
- **Data/hardware/compute:** new microphone, fixture, timing logger and acoustic treatment; MIMII/MIMII DUE can supply literature context but do not substitute for a repeated local workflow.
- **Advisor requirement:** signal-processing and experimental-measurement support, plus permission to operate the fixture repeatedly.
- **Kill condition:** direct witness solves the operational decision, no independent event label is available, or the study collapses into ordinary acoustic anomaly detection.
- **Pivot value:** only a negative physical-versus-digital audit or a reproducible control comparison; do not buy the apparatus before access and decision records are confirmed.

## Pareto comparison

| Dimension | `DEPLOY-GATE` | `ACTION-RANK` | `ACOUSTIC-RANK` |
| --- | --- | --- | --- |
| Story importance | Medium: real commissioning decision, but must be attached to an actual station | Medium-high: immediate retain/reacquire decision and concrete record harm | Potentially medium-high for maintenance, but currently hypothetical |
| Exact novelty status | Amber/Red: chart and camera-health validation are established; residual is changed release decision | Amber: exact finite optical action endpoint remains a search gap, not a novelty claim | Red/Amber: acoustic anomaly/domain-shift work is extensive; residual action endpoint is unverified |
| Current feasibility | High bench feasibility, low workflow feasibility | Highest: all core observation hardware is owned | Low/medium: new sensor, fixture and workflow access |
| Strong negative-result value | High if it shows digital/chart gate suffices | High: rank preservation or two-world non-identifiability is a bounded audit/FYP result | High in principle, but label/access risk is large |
| Main risk | Becomes a standard QA checklist or vacuous acceptance-sampling exercise | Becomes a benchmark with no real actor, or fixed two-shot wins | Repeats MIMII-style anomaly detection or is solved by direct tachometer |
| Recommended role | Secondary deployment chapter/control | Only candidate worth a physical pilot | Do not purchase or promote before workflow evidence |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Synthetic and real corruption performance can correlate in aggregate while corruption-specific relationships are weaker. | [K] | Agnihotri, Schader, Sharei, Kaçar and Keuper, *Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?*, arXiv v1, 2025-05-07. https://arxiv.org/abs/2505.04835 | Sec. 1, Sec. 3, Secs. 4.1-4.2, Sec. 5; PDF pp. 1, 3-9 | Semantic-segmentation benchmark; does not prove the RGB/NoIR marker endpoint. It kills a universal proxy-invalidity claim only. |
| Fiducial detection/decoding under difficult lighting and synthetic-to-real mismatch are already studied. | [K] | *DeepArUco++: Improved detection of square fiducial markers in challenging lighting conditions*, Image and Vision Computing 152, 105313, 2024; arXiv:2411.05552. https://arxiv.org/abs/2411.05552 | Secs. 1, 3, 4, 5 and Sec. 5.6; PDF pp. 1-10 | Marker family and decoder differ from this setup; the direct collision is the task/mechanism, not every exact hardware configuration. |
| Active exposure control for field fiducial markers is a direct neighbour to IR/exposure routing. | [K] | Ren, Lensgraf and Quattrini Li, *Improving the perception of visual fiducial markers in the field using Adaptive Active Exposure Control*, arXiv v1, 2024. https://arxiv.org/abs/2404.12055 | Abstract, Sec. 1, method and experiment sections; PDF pp. 1-8 | Their action is exposure control for marker localization; the finite action-rank endpoint remains narrower but cannot claim a new adaptive exposure method. |
| Active physical-fault diagnosis can select interventions using a causal information criterion. | [K] | Han, Taheri, Chung and Hadaegh, *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv v1, 2025-09-22. https://arxiv.org/abs/2509.18460 | Abstract, Secs. 1-4, active FDI/EI formulation and robot experiment; PDF pp. 1-12 | Robot exploration and fault hypotheses are different; this still occupies generic causal active-diagnosis wording. |
| Resource-aware edge systems already use low-cost screening, confirmation acquisition, uncertainty escalation and watchdogs. | [K] | Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, published 2026-08-10. https://www.mdpi.com/1424-8220/26/16/5065 | Secs. 1, 3.1, 5.1 and 8 | Fault-warning application and hardware differ; the claim that screen/confirm/reacquire is itself novel is not available. |
| Camera chart/SFR testing is a defined digital-camera quality-control procedure. | [K] | ISO 12233:2024, Digital cameras — Resolution and spatial frequency responses, edition 5, published 2024-09. https://www.iso.org/cms/live/live/en/sites/isoorg/contents/data/standard/08/86/88626.html?browse=tc | Abstract, Purpose 0.1 and technical background preview pp. vi-2 | The full standard is paywalled; the official record/preview is sufficient for the existence and scope of the metrology baseline, not for every implementation detail. |
| Physical camera condition can be monitored and linked to downstream task capability. | [K] | Wischow, Gallego, Ernst and Börner, *Monitoring and Adapting the Physical State of a Camera for Autonomous Vehicles*, arXiv v1, 2021-12-10. https://arxiv.org/abs/2112.05456 | Abstract, Secs. 1-4 and vehicle experiment; PDF pp. 1-12 | Autonomous-vehicle deployment differs; it directly occupies passive camera-health and downstream-task adaptation components. |
| A recent passive monitor defines bounded lens-occlusion and photometric-transition predicates and evaluates false alarms/recall on controlled and public audits. | [K] | Ma, Yan and Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions for Camera Tamper Monitoring*, arXiv v1, 2026-07-16. https://arxiv.org/abs/2607.14760 | Abstract, Secs. 1-5 and limitations/out-of-scope discussion | Surveillance-camera setting and predicates differ; it blocks a new passive health index, not the finite exact-marker action study. |
| Fault-time rankings can disagree with clean-error rankings under a standardized sensor-fault protocol. | [K] | Windmann, Wittenberg, Manca, Dix, Brandt and Niggemann, *Benchmarking Sensor-Fault Robustness in Forecasting*, arXiv v1, 2026-05-11. https://arxiv.org/abs/2605.10822 | Abstract, Secs. 1-5, taxonomy, disjoint transfer split and metrics | Forecasting/CPS task, not optical capture. It blocks generic “rank disagreement under faults” language while leaving a different exact action endpoint. |
| Industrial sound datasets already cover machine malfunction and operational/environmental domain shifts. | [K] | Purohit et al., *MIMII Dataset: Sound Dataset for Malfunctioning Industrial Machine Investigation and Inspection*, 2019 dataset paper. https://doi.org/10.33682/m76f-d618 | Dataset description, machine classes, normal/abnormal protocol and recording setup | Public dataset access and labels do not create a local actor decision or independent deployment record for this FYP. |
| Acoustic domain shift due to operating and environmental conditions is directly benchmarked. | [K] | Koizumi et al., *MIMII DUE: Sound Dataset for Malfunctioning Industrial Machine Investigation and Inspection with Domain Shifts Due to Changes in Operational and Environmental Conditions*, WASPAA 2021. https://doi.org/10.1109/WASPAA52581.2021.9632802 | Secs. II-V, dataset conditions, domain-shift protocol and tables | Strong direct neighbour for an acoustic robustness/dataset story; it does not evaluate the proposed retain/re-record action loss. |
| The current Pi protocol requires exact independent payload truth, physical labels, held-out cells, fixed two-shot controls and measured timing/energy. | [K] | Project-local protocol: `research/active/09-physical-transfer-pilot-protocol.md`, `11-cross-device-action-rank-pilot.md`, `12-pilot-execution-gates.md`, version present on 2026-09-03. | Entire files, especially Observation and truth; Actions and baselines; Two-world check; Stop/continue gates | Local project requirement, not external literature evidence. No sensor data or hardware log is currently present. |
| No named Bob Zhang paper inspected here establishes the exact printed-marker physical/digital action endpoint. | [GAP] | Project archive Bob Zhang/PAMI audit and current charter; no new novelty claim. | `research/archive/2026-08-edge-sensing/core/12-bob-zhang-lab-audit.md` and current `00-project-charter.md` boundary notes | Advisor fit is thematic only: incomplete/unreliable observations and conservative decisions. It is not evidence of novelty or a contribution. |

## Formal claim boundaries and required controls

1. **No universal simulation-invalidity sentence.** The allowed sentence is: “On the declared RGB/NoIR pair, under the declared physical cells and matched action budget, the measured digital-to-physical action ranking did or did not transport.”
2. **No general camera-family transfer sentence.** The camera swap changes the IR-cut observation path and may confound modality with device. Block and report the exact pair only.
3. **No causal physical-fault diagnosis.** A transparent cover or low-light label is a fixture state for a finite test, not a proof that the logger can infer root cause from an image.
4. **No safety or production release claim.** `release` means a laboratory/bench configuration gate. The printed marker is a non-personal record key.
5. **No model search before controls.** First run fixed RGB, fixed NoIR+IR, fixed two-shot, scalar quality, random and oracle controls. A learned policy enters only after a held-out discrepancy survives.
6. **No hidden truth leakage.** Cell labels and exact payload truth are offline evaluation channels. They cannot be features of the runtime action policy.
7. **No ordinary frame count as sample size.** Independent sessions, remounts and held-out light/material cells are the experimental units needed for a finite claim.

## Queries and failed searches

### Queries that produced useful direct neighbours

- `"Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions"` -> Agnihotri et al., arXiv:2505.04835.
- `"DeepArUco++" challenging lighting` -> marker decoding and synthetic-to-real mismatch.
- `"active exposure control" fiducial markers` -> Ren et al., arXiv:2404.12055.
- `"counterfactual" fault diagnosis robot perception active FDI` -> Han et al., arXiv:2509.18460.
- `"safety-first active sensor acquisition" edge fault warning` -> Bian et al., Sensors 2026.
- `"clean-reference" camera tamper monitoring lens occlusion` -> Ma et al., arXiv:2607.14760.
- `SensorFault-Bench fault-time ranking` -> Windmann et al., arXiv:2605.10822.
- `MIMII DUE domain shifts operational environmental conditions` -> Koizumi et al., WASPAA 2021.

### Failed or insufficient searches

- `physical camera failure deployment gate printed marker edge Pi release decision`: no inspected primary paper matched the exact combination of a finite release action, RGB/NoIR path, exact printed-payload oracle, and matched commissioning budget. This is a search boundary, not a novelty result.
- `digital corruption action ranking retain reacquire unknown fiducial camera`: no exact collision was established in the inspected sources, but existing active acquisition, marker exposure control and robustness-benchmark papers occupy the component families. The residual is Amber only.
- `acoustic physical-vs-digital corruption retain rerecord independent witness edge`: no exact paper was established. MIMII/MIMII DUE and fault-benchmark work make the surrounding task family crowded; absence of an exact hit is not evidence of originality.
- `Bob Zhang physical-vs-digital marker deployment gate`: no exact advisor paper was found in the inspected archive map. Treat the connection as general unreliable-observation fit only.

## Decision

**PIVOT**

Keep `ACTION-RANK` as the only candidate worth the existing RGB/NoIR physical pilot, with `DEPLOY-GATE` as a secondary paper framing or evaluation chapter. Do not promote either before an independent held-out rank inversion or a non-vacuous release-decision change survives fixed two-shot, scalar-quality, chart/IQA and always-reacquire controls. Reject `ACOUSTIC-RANK` as a purchase or thesis direction until a real repeated workflow, independent truth channel and operational restriction are confirmed; its current value is a negative alternative, not a live branch.
