# Validation Audit: 2026-08-31 rounds 8--10 and RGB/NoIR re-openings

## Decision investigated

This audit tries to falsify the newest divergence candidates rather than
protect them: `CSI-BaselineGate`, `UWB-RL-CAUSE`, `MAG-GeometryWitness`,
`MMW-ClutterWitness`, `AQ-ReferenceFreeAudit`, `PLAR-Safe`,
`SCHED-PUB-STREAM`, `PSI-EVENT-JOIN`, `RVK-LOCAL-LEASE`,
`DP-BUDGET-MICROEDGE`, `CRDT-ESCROW-LIMIT`, `PRF-TR`, `IR-CAUSE`,
`FLICK-PHASE`, `PWR-WIT`, and `RS-DRIFT`.  I also checked the current
RGB/NoIR names (`ACR-MODE`, `ASI-IR`, `OPT-WIT`, `EV-EXPO`, `MOD-MISSING`,
`CAL-TRANSPORT`, `PHY-MASK`, `FULL-CAP`) and the synchronization/risk-routing
reframings.  The permitted endpoint is a non-personal, non-production bench
record; no navigation, access control, safety actuation, or human data are
assumed.

## Claim under test

The supplied candidates mostly claim that a cheap edge node can observe a
local signal, select/annotate an action, and remain reliable under a change of
device, load, environment, privacy state, or physical fault.  A candidate can
survive only if its observation, action, guarantee, and evaluation endpoint
remain distinct after comparison with recent primary work, and if an
independent truth source makes the claim testable.  A Raspberry Pi deployment,
new sensor board, new classifier, or replacing a simulator with a real board
is not by itself a distinction.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | OpenCSI already combines per-link quiet-period calibration, maturity/reliability and stale-baseline abstention; Peterseil's UWB framework combines link/node/system indicators and online anchor filtering; Medici/Aher and Ma occupy optical health; Lens, AdaptiveAE, CM-ASAP and QIC occupy adaptive sensor/action selection; DPack and Zhou occupy privacy-budget/LDP allocation; PEPSI, EVOKE and Basmer occupy private joining, revocation and schedule release. | A finite physical RGB/NoIR intervention with an exact printed-code oracle, or a paired physical-vs-digital action audit, is not the same endpoint in the inspected sources. This is an experiment boundary, not a new mechanism. | High for generic mechanisms; medium for the bounded optical protocol. |
| Exact-claim collision | `CSI-BaselineGate` repeats a baseline-age/reliability/abstain decision. `UWB-RL-CAUSE` repeats link/node/system trust and ranging-error credibility labels. `PLAR-Safe` and `DP-BUDGET-MICROEDGE` repeat private resource allocation and budget scheduling. `SCHED-PUB-STREAM` is a dynamic spelling of privacy/utility schedule publication unless its stream threat model changes the invariant. `ACR/ASI/EV/MOD` repeat adaptive camera, exposure, modality and Bayesian-risk routing. `RS-DRIFT/FLICK-PHASE` repeat timing measurement, rolling-shutter calibration or flicker correction. | `IR-CAUSE` still has a narrow possible difference: an IR-on physical intervention is tested for incremental information about two independently labelled causes. `PRF-TR/PHY-MASK/FULL-CAP` still have a finite paired ranking question, but broad synthetic-vs-real claims collide with Agnihotri/SensorFault-Bench. `POL-GLARE-VOI` is similarly finite and collision-prone. | High for KILL candidates; medium-high for the two optical audit pivots. |
| Boundary / impossibility | Passive CSI, UWB summaries, image quality, lux, power or schedule reports do not in general identify the hidden physical cause. Two worlds can share the same observation but require different actions. LDP reports also compose over repeated releases; an offline lease/CRDT cannot infer unavailable capacity. A fixed two-shot policy can dominate a learned selector. | A finite fixture-controlled test can be identifiable if cause labels, marker payload, timing, exposure/white balance, energy, and held-out cells are independent and frozen before tuning. It cannot establish a population transfer theorem or universal causal diagnosis. | High for the non-identifiability warnings; empirical effect still [GAP]. |

## Candidate-by-candidate kill map

| Candidate | Direct collision / failure | Strongest kill test and baseline | Feasibility and decision |
| --- | --- | --- | --- |
| `CSI-BaselineGate` | OpenCSI, arXiv 2607.26665v1 (2026-07-29), uses quiet-period Z-score, baseline maturity, stale-baseline abstention and cross-generation/room transfer. This is the same observation/action family. | Compare target-only CSI, OpenCSI-style per-link gate, fixed rebootstrap and optional auxiliary link on time-blocked episodes. If OpenCSI or rebootstrap matches false-retain at equal unknown rate, the auxiliary link adds no contribution. | Two ESP32s and a rail truth are feasible, but a Pi FYP would be a reproduction and adds hardware outside the purchased camera story. **KILL.** |
| `UWB-RL-CAUSE` | Peterseil et al., Sensors 24:5268 (2024), pp. 4--5, 10, 12--13 and 15--17, already define link/node/system trustworthiness and select trusted anchors. Yang et al., Measurement 256:117721 (online 2025-03-26), abstract, explicitly classifies sources of ranging error and evaluates credibility/mitigation. | Target-link CIR/FQA/RSS, multi-link trust indicators, periodic reference, and an equally informed classifier must be compared. A shared metal/RF obstruction can alter target and references together, so the proposed root-cause labels are not identifiable in general. | Four UWB nodes, CIR extraction and synchronized fault fixtures are an additional hardware project. **KILL** as thesis; at most replication appendix. |
| `MAG-GeometryWitness` | Mondoskin et al. (Frontiers 2026, Secs. 1--5) give low-cost vector calibration/error budgets; Ousaloo et al. (Sensors and Actuators A 393, 116852, 2025 abstract) already give calibrated low-cost magnetic localization. | Calibrated dipole/localization plus residual threshold is the decisive baseline. Board rotation and target displacement can generate the same 3-vector at one sensor, defeating unrestricted cause attribution. | Cheap hardware, but no research distinction and requires encoder/fixture calibration. **KILL.** |
| `MMW-ClutterWitness` | Banik et al., Asilomar 2024, pp. 218--222, occupy collaborative mmWave self-calibration; Sheng et al., HomeOSD, Sensors 24:2911 (2024), occupy low-cost appliance-state detection. A fixed reflector is ordinary calibration, not scene truth. | Compare passive state detector, periodic/always reflector, standard self-calibration and an equally informed classifier against an optical/encoder truth. If clutter affects reference and target together, no separation follows. | 24/60-GHz hardware, motor fixture and ground truth are costly and schedule-risky. **KILL.** |
| `AQ-ReferenceFreeAudit` | Wang & Peng, Sensors 26:4526 (2026), abstract and publisher Sec. 5.1, explicitly propose Pi 5 on-device reference-free multi-pollutant self-diagnosis, local fallback and bench fault injection. | Use their agent/rule baseline and construct same trace/telemetry with different gas truth. Equal traces imply no reference-free attribution. | Safe gas/reference truth, ventilation and chemical handling are unsuitable for the stated early demo. **KILL.** |
| `PLAR-Safe` | Zhou et al., IEEE IoT Journal 11(4), pp. 6537--6550 (2024), official repository abstract, combine federated RL, LDP and joint resource allocation. *Linear optimization with local differential privacy for resource sharing* (online 2026), Secs. 2.2--2.2.2, directly formulates private resource sharing. DPack (EuroSys 2025), pp. 1194--1205, treats privacy budget as a finite scheduling resource. | Give a coordinator the same randomized-response bits and compare exact posterior/lower-confidence-bound, non-private oracle, and FCFS. A robust/Bayes rule using identical reports absorbs a proposed policy; repeated reports invalidate a single-release privacy claim by composition. | Synthetic containers are easy, but a real confidentiality owner/adversary and non-vacuous one-sided deadline bound are [GAP]. **PIVOT** only to a negative privacy--deadline frontier experiment. |
| `SCHED-PUB-STREAM` | Basmer et al., AAAI 2025, pp. 26446--26453, Secs. 3--5, already model inverse-scheduling attacks and privacy/utility-preserving schedule perturbations. Wang et al., JPDC 189 (2024) 104882, Secs. 2--5, already schedule privacy levels, deadlines and edge/cloud resources. | Basmer perturbation + ordinary time-bounded lease is the baseline. If both preserve no-double-reservation and the stated attacker cannot infer the private priority, streaming is deployment detail; if timing/order leaks it, encryption does not remove the endpoint. | Containers/SBCs feasible, but the required dynamic threat model is not specified. **KILL** unless a protocol-level invariant is first proven distinct; current status **KILL**. |
| `PSI-EVENT-JOIN` | PEPSI, USENIX Security 2024, pp. 6453--6470, Secs. 1--3.3, supports private intersection and arbitrary functions for constrained clients; this directly implements merge/separate/manual-review based on private intersection. | PEPSI/circuit-PSI plus the same threshold at equal bytes/leakage is decisive. | Functional Pi demo is feasible, but engineering only. **KILL.** |
| `RVK-LOCAL-LEASE` | EVOKE, USENIX Security 2024, pp. 1279--1295, Sec. 4.2 pp. 1283--1284 and Sec. 6.3 pp. 1288--1289, already provides accumulator/witness revocation, peer offline updates and stale-state disablement. | Reimplement EVOKE state machine with the same stale-peer/allow/deny trace. A renamed lease has identical state/action. | Feasible but no claim distinction. **KILL.** |
| `DP-BUDGET-MICROEDGE` | DPack, EuroSys 2025, Secs. 1--3 and 6.2/6.4/8, gives privacy-knapsack scheduling, DPF/FCFS/optimal baselines, Kubernetes implementation and fairness/efficiency. | Run DPack algorithms and exact small-instance solver on same budget/CPU traces. A Pi placement or scalar priority cannot be the contribution. | Small trace replay feasible; edge deployment does not alter claim. **KILL.** |
| `CRDT-ESCROW-LIMIT` | Bounded-counter/escrow is the standard construction for partition-safe finite tokens. A recent primary source was not retrieved; this is [GAP], not evidence of novelty. Existing edge resource-allocation literature already supplies competing centralized/offline baselines. | Standard bounded-counter/escrow CRDT with identical token cap and partition trace is the mandatory baseline. If it preserves the cap and availability, the proposed rule is eliminated. | Very feasible but source chain and threat model are incomplete. **PIVOT** to a baseline/teaching replication, not a thesis. |
| `PRF-TR` / `PHY-MASK` / `FULL-CAP` | Agnihotri et al., CVPRW 2025, arXiv 2505.04835v1, Secs. 1, 3, 4.1--4.2, 5, already ask whether synthetic corruptions proxy real robustness. Liao (2025), MultiCorrupt (2024), MSC-Bench (2025), Park (CVPR 2025) occupy synthetic missing/fault/routing benchmarks; SensorFault-Bench, arXiv 2605.10822v1 (2026-05-11), adds disjoint fault-transfer and ranking disagreement. | Freeze a decoder and exact printed-code oracle. Compare digital corruption rank to paired physical cells using Kendall/Spearman with session bootstrap; include always RGB, always NoIR+IR, fixed two-shot, scalar brightness/blur/IR-ratio and oracle. High correlation kills the distinction; rank inversion is only a bounded warning. | Existing Pi pair, static target, covers/lamp and optional meters are feasible. **PIVOT** as finite negative-capable audit, not a method or universal simulation claim. |
| `IR-CAUSE` | Passive camera health/occlusion is occupied by Ma, Yan & Wu, arXiv 2607.14760v1 (2026-07-16), Secs. I--VIII and X--XIII, including camera-disjoint threshold transfer (Supplementary XII). Active counterfactual FDI is occupied at the framework level by Han et al., arXiv 2509.18460v1 (2025-09-22), Sec. 1 and abstract. | Make two independently labelled worlds: clean low visible light and transparent cover/contamination at matched visible lux. Compare IR-on intervention against fixed RGB->NoIR+IR, passive quality, fixed ratio, and always-reacquire. If pre-action observations overlap while optimal actions differ, cause identification is impossible; if IR does not lower cause-confusion at matched cost, kill. | Owned cameras/IR plus rigid fixture and independent lux/cover labels are feasible; no learning needed. **HOLD / Amber** only as finite incremental-information test. |
| `FLICK-PHASE` | Ren et al., arXiv 2404.12055v1 (2024), Sec. 1 and abstract, already use active exposure for fiducial markers. Fukuda et al., JAFST 2024, Vol. 29(2), pp. 135--153, already measure exposure/inter-frame/readout with LED/PIC; Otsuka et al., APCC 2024, pp. 365--370, occupy LED rolling-shutter synchronization; Shan et al., VCIP 2025 record occupies flicker removal (full PDF [GAP]). | Independent photodiode phase plus fixed anti-flicker exposure, fixed IR, and fixed recapture are baselines. If the lamp has no repeatable modulation or fixed settings tie, the phase policy is unnecessary. | Photodiode/ADC and a PWM lamp are purchasable, but it is instrumentation/action scheduling with high collision. **KILL** as thesis; timing oracle can support optical pilot. |
| `PWR-WIT` | No directly inspected 2024--26 Pi-camera paper proves a power trace as an image-validity witness [GAP], but power telemetry is an instrumentation signal and standard brownout/health controls are direct baselines. Recent Pi 5 pose work reports concurrent multimeter power logging and thermal flags (Sensors 26:5188, 2026, Table 3 and power-measurement method). | Use programmable, safe supply droops and an external LED/oscilloscope truth. Compare image-only brightness/blur, frame-valid metadata, and power trace at equal byte/energy cost. If the trace is not time-aligned or image-only ties, kill. | Electrical safety and programmable droop add risk; USB meters often undersample transients. **PIVOT** to measurement characterization only; not a method. |
| `RS-DRIFT` | Zhang et al., arXiv 2608.01509v1 (2026-08-02), Secs. 1--5, occupy target-free rolling-shutter self-calibration; Fukuda 2024 occupies LED timing measurement; Otsuka 2024 occupies synchronization. | Compare factory constants and one-time calibration against per-session LED estimate under temperature/load/mode changes. If no drift or factory metadata ties, kill. | Sequential Pi cameras are unsuitable for fast-motion claims; LED fixture is feasible. **KILL** as thesis; retain only as a confound check. |
| `ACR-MODE` / `ASI-IR` / `EV-EXPO` / `MOD-MISSING` | Lens, arXiv 2503.02170v3 (2026-05-19), Secs. 3.1--3.2, 4--5, already selects camera parameters by model confidence and capture cost. AdaptiveISP (NeurIPS 2024, Sec. 3, pp. 4--9), AdaptiveAE (ICCV 2025, pp. 25176--25185), CM-ASAP (MIPR 2024, pp. 207--213), Rampure et al. arXiv 2606.17376v1 (2026-06-16), Secs. III-A and V, and Chaichi Mellatshahi et al. ICASSP 2026, Bayesian compute+error risk, occupy adaptive modality/exposure/risk routing. | Fixed RGB, fixed NoIR+IR, fixed two-shot and scalar brightness/blur/IR-ratio rules must be beaten at matched cost. Generic router or Pi deployment is eliminated. | Current hardware can run a demo but does not support a thesis mechanism. **KILL.** |
| `OPT-WIT` / `CAL-TRANSPORT` | Ma et al. 2026 occupies passive clean-reference camera-health/occlusion and cross-camera threshold transfer; Medici et al., Acta IMEKO 2025, uses sharpness for IR-camera contamination diagnosis; Aher, arXiv 2605.05439v1 (2026-05-06), uses single-RGB degradation-aware health. | Compare passive state machine, scalar quality and one-time calibration. Only active IR with independent labels remains; otherwise direct collision. | Feasible as preflight, not thesis. **KILL.** |
| RGB/NoIR synchronization/registration | RocSync, arXiv 2511.14948 (2025), supplies millisecond RGB/IR synchronization and downstream alignment; Kim & Baek, arXiv 2411.18025v1 (2024), supplies pixel-aligned RGB--NIR stereo. Full section/page audits for these records are [GAP]. | LED/photodiode timing is a confound measurement, not a new sync method. Static sequential marker only; motion claim requires oracle. | Pi docs confirm dual cameras but no synchronized 3A guarantee. **KILL** standalone sync; log timing in the finite audit. |

## Assumption and identification audit

1. **Hidden-cause ambiguity.** A low-visible-light clean lens and a transparent
   cover/water-film lens can be adjusted to produce the same RGB preview,
   brightness/blur and ordinary metadata while needing different actions. A
   passive policy therefore cannot certify cause. IR on/off is informative only
   if the independently labelled physical response differs after exposure and
   white balance are frozen/logged.
2. **Sensor-path confounding.** The Camera Module 3 standard has an IR-cut
   filter while NoIR omits it (Raspberry Pi product brief, p. 3). Thus an
   RGB/NoIR ``device transfer`` is simultaneously a spectral-path change; two
   units do not support a camera-family guarantee.
3. **Timing.** Raspberry Pi's camera documentation permits multiple cameras but
   does not guarantee synchronized 3A. Any moving-target RGB/NoIR claim needs an
   LED/photodiode timestamp; otherwise use a static target only.
4. **Independent truth.** A printed QR/ArUco/AprilTag payload must be generated
   before capture and checked by an independent oracle. Model confidence, panel
   brightness or a post-hoc image statistic is not scene truth.
5. **Resource/privacy claims.** LDP privacy is per release and composes over
   repeated reports; a privacy parameter without an adjacency, attacker,
   release count and utility bound is not a result. A schedule trace can leak
   timing/order even if payloads are encrypted. A CRDT cap can guarantee token
   safety but cannot guarantee availability under partitions.
6. **Physical power/flicker.** A low-rate USB meter can miss microsecond or
   millisecond droops; a photodiode improves timing but does not establish that
   a capture is semantically valid. Both are witnesses requiring independent
   marker/oscilloscope truth.

## Direct-neighbor table

| Work | Inputs/actions | Target/evaluation | Exact overlap and residual |
| --- | --- | --- | --- |
| Khamaisi, Sigg & Rodrigues, OpenCSI, arXiv 2607.26665v1 (2026-07-29), https://arxiv.org/abs/2607.26665 | Mesh CSI, quiet bootstrap, per-link Z-score/maturity, abstain/recover | Binary occupancy transfer across rooms and ESP32 generations; abstract, Secs. III-D, IV-E | Directly kills CSI baseline-gate reliability action. |
| Peterseil et al., Sensors 24:5268 (2024), https://www.digidow.eu/publications/2024-peterseil-sensors/Peterseil_2024_Sensors_TrustworthyUWBLocalization.pdf | UWB node/link/system metrics, CIR/RSSI, trusted-anchor selection | Trustworthiness and localization service; pp. 4--5, 10, 12--13, 15--17 | Kills multi-link trust/cause label; fixture-specific labels remain only a replication. |
| Yang et al., Measurement 256:117721 (2025), https://eprints.gla.ac.uk/362922/ | CIR/ranging features and credibility model | Fine-grained ranging-error source classification; author-hosted abstract | Direct exact-claim pressure for UWB-RL-CAUSE; full PDF sections [GAP]. |
| Basmer et al., AAAI 2025, https://doi.org/10.1609/aaai.v39i25.34844 | Perturbed schedules and constraint programming under inverse-scheduling attacker | Privacy and utility of published schedules; pp. 26446--26453, Secs. 3--5 | Kills static schedule-release mechanism; online-stream residual is unverified. |
| Tholoniat et al., DPack, EuroSys 2025, https://doi.org/10.1145/3689031.3696096 | DP budget as resource, DPF/FCFS/optimal, Kubernetes | Fairness/efficiency; pp. 1194--1205 | Kills DP-budget micro-edge mechanism. |
| Mahdavi et al., PEPSI, USENIX Security 2024, https://www.usenix.org/system/files/usenixsecurity24-mahdavi.pdf | Unbalanced PSI, arbitrary intersection functions | Private join/cardinality; pp. 6453--6470, Sec. 3.3 p. 6456 | Kills PSI event triage. |
| Mazzocca et al., EVOKE, USENIX Security 2024, https://www.usenix.org/system/files/usenixsecurity24-mazzocca.pdf | Accumulator/witness credential revocation with peer update | Offline IoT revocation; pp. 1279--1295, Sec. 4.2 | Kills local lease revocation. |
| Agnihotri et al., CVPRW 2025, https://arxiv.org/abs/2505.04835 | Synthetic corruptions versus real weather images | Segmentation correlation; Secs. 1, 3, 4.1--4.2, 5 | Kills broad physical-vs-digital proxy thesis; leaves exact-code finite audit. |
| Windmann et al., SensorFault-Bench, arXiv 2605.10822v1 (2026-05-11), https://arxiv.org/abs/2605.10822 | Value/timing/availability faults and disjoint fault split | Worst-scenario error/ranking disagreement; Secs. 1--5 | Kills generic fault-transfer benchmark claim. |
| Ma, Yan & Wu, arXiv 2607.14760v1 (2026-07-16), https://arxiv.org/abs/2607.14760 | Clean reference, luminance/gradient state machine, camera-disjoint threshold test | Lens occlusion and photometric transition monitoring; Secs. I--VIII, X--XIII, Suppl. XII | Kills passive OPT-WIT/CAL-TRANSPORT; active IR increment remains Amber. |
| Baek et al., Lens, arXiv 2503.02170v3 (2026-05-19), https://arxiv.org/abs/2503.02170 | Select camera parameters from unlabeled scene/model confidence under capture cost | Image accuracy/capture time; Secs. 3.1--3.2, 4--5 | Kills generic ACR/ASI/EV action router. |
| Xu et al., AdaptiveAE, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Sequential ISO/shutter actions and exposure budget | HDR quality/motion/noise; pp. 25176--25185 | Kills sequential exposure/burst mechanism. |
| Rampure et al., arXiv 2606.17376v1 (2026-06-16), https://arxiv.org/abs/2606.17376 | Brightness-threshold RGB/NIR/thermal/low-light choice | Respiratory valid-window reliability; Secs. III-A, V | Strong direct collision for brightness-adaptive modality selection. |
| Han et al., arXiv 2509.18460v1 (2025-09-22), https://arxiv.org/abs/2509.18460 | Passive/active perception interventions selected by Effective Information | Counterfactual fault diagnosis; abstract/Sec. 1 | Kills generic active-causal diagnosis; IR-CAUSE survives only as an empirical optical intervention. |

## Strongest simple baseline

For camera candidates the dominant control is frozen `RGB -> NoIR+IR`
two-shot, with deterministic exact-code decoding and `unknown/reacquire` on
failure. Also run always-RGB, always-NoIR+IR, fixed filter/phase, scalar
brightness/blur/IR-ratio thresholds, random action, and an oracle. The loss
must be fixed before held-out results (for example false-retain weighted 10,
unknown weighted 1, energy normalized by RGB-only median weighted 0.1). If the
two-shot or scalar rule is Pareto-optimal, a learned/adaptive mechanism is
unnecessary.

For resource/privacy candidates, compare the exact posterior or robust
lower-confidence rule using the same reports, non-private oracle, FCFS, and a
standard lease/escrow CRDT. For UWB/CSI compare the published trustworthiness
or stale-baseline rule before adding a second link. For power/flicker, compare
factory metadata, fixed anti-flicker exposure, and image-only quality at equal
measurement cost.

## Contrarian result

The strongest adversarial conclusion is that almost every candidate is an
endpoint rename or a hardware demonstration. Even if an auxiliary sensor or
intervention improves a finite table, a fixed two-shot/periodic policy may
match it, and two physical worlds can invalidate any passive cause guarantee.
The most credible positive residual is not a new selector: it is an empirical
observation that a named IR-on intervention changes exact-marker risk on
held-out, independently labelled cover/illumination cells. If that effect is
absent, the honest result is a non-identifiability or rank-preservation report.

## Feasibility audit

- **Pi RGB/NoIR:** Static captures, a rigid mount, printed marker, covers and
  safe IR diffuser are feasible by the December demo. Sequential dual-camera
  motion claims are not.
- **Measurements:** Lux is photopic illuminance, not an NIR witness; a lux board
  is instrumentation only. A USB power meter may miss transients. Add meters or
  photodiode only after a pilot shows they change the observation model.
- **New hardware branches:** UWB, mmWave, gas, magnetometer, programmable
  supply and multi-SBC privacy clusters all add procurement/control burden and
  do not survive the collision audit. They should not displace the existing
  camera pilot without a new independent evidence source.
- **Data/ethics:** Printed codes and inert materials avoid personal data and
  safety actions. Gas experiments require ventilation/reference chemistry and
  are rejected. Privacy scheduling requires a real non-personal confidentiality
  owner and attacker; synthetic secrecy is insufficient for a practical story.
- **Compute/time:** Classical decoding and threshold policies run on Pi 5. A
  frozen finite matrix fits a December 2026 demo; a transfer/cause claim needs
  held-out lamps/materials and repeated sessions in 2027 H1. Large model/RL
  training is not feasible or necessary.

## Evidence ledger

| Claim | Label | Primary source/version | Exact section/page read | Caveat |
| --- | --- | --- | --- | --- |
| CSI stale-baseline reliability/abstention is already implemented. | [KILL] | OpenCSI, arXiv 2607.26665v1, 2026-07-29, https://arxiv.org/abs/2607.26665 | Abstract; Sec. III-D; Sec. IV-E; cross-generation result | Preprint, binary occupancy scope. |
| UWB link/node/system trustworthiness and anchor filtering are established. | [KILL] | Peterseil et al., Sensors 24:5268, 2024, URL above | pp. 4--5, 10, 12--13, 15--17 | Different benign fixture, same observation/action family. |
| UWB error-source credibility classification is established. | [KILL] | Yang et al., Measurement 256:117721, online 2025-03-26, URL above | Author-hosted abstract | Full accepted PDF sections/pages [GAP]. |
| LDP/federated resource allocation is established. | [K] | Zhou et al., IEEE IoT J 11(4), 2024, https://doi.org/10.1109/JIOT.2023.3312118 | Official repository abstract/metadata | Full model/threat assumptions [GAP]. |
| Privacy budget scheduling is established. | [KILL] | DPack, EuroSys 2025, URL above | pp. 1194--1205, Secs. 1--3, 6.2, 6.4, 8 | Edge placement is not novelty. |
| Private intersection with functions is established. | [KILL] | PEPSI, USENIX Security 2024, URL above | pp. 6453--6470; Sec. 3.3 p. 6456 | Does not cover semantic near-match, but event-ID join is exact collision. |
| Offline IoT credential revocation is established. | [KILL] | EVOKE, USENIX Security 2024, URL above | pp. 1279--1295; Sec. 4.2 | Named lease is same state machine unless threat model changes. |
| Schedule privacy against inverse scheduling is established. | [KILL] | Basmer et al., AAAI 2025, URL above | pp. 26446--26453; Secs. 3--5 | Online stream distinction remains [GAP]. |
| Synthetic-vs-real robustness proxy and disjoint fault-transfer tests are established. | [KILL] | Agnihotri et al., arXiv 2505.04835v1 (2025-05-07); Windmann et al., arXiv 2605.10822v1 (2026-05-11) | Agnihotri Secs. 1,3,4.1--4.2,5; SensorFault-Bench Secs. 1--5 | Neither uses Pi exact-code action endpoint. |
| Passive camera-health and camera-disjoint threshold transfer are established. | [KILL] | Ma et al., arXiv 2607.14760v1 (2026-07-16) | Secs. I--VIII, X--XIII; Suppl. XII | Active IR incremental-information remains [C]. |
| Adaptive camera/exposure/modality/risk routing is established. | [KILL] | Lens 2026 version; AdaptiveISP NeurIPS 2024; AdaptiveAE ICCV 2025; CM-ASAP MIPR 2024; Rampure 2026; Chaichi Mellatshahi ICASSP 2026 | Sections/pages in direct-neighbor table | Some full PDFs/sections [GAP], but component/action collision is clear. |
| IR-on can identify low-light versus cover contamination. | [C] | Proposed IR-CAUSE pilot | No inspected primary source proves it | Requires independent labels and two-world test. |
| Physical and digital action rankings will invert. | [C] | Proposed PRF-TR/PHY-MASK/FULL-CAP pilot | No source; empirical gate | Must remain Amber until held-out repeated data. |
| Power trace improves image admissibility. | [C] | Proposed PWR-WIT | No direct Pi-camera primary study found | Meter bandwidth and temporal alignment [GAP]. |
| RGB/NoIR timing is synchronized enough for motion fusion. | [KILL] | Raspberry Pi camera docs; RocSync arXiv 2511.14948; Kim & Baek arXiv 2411.18025 | Pi multiple-camera/synchronization note; other full sections [GAP] | Use static target or independent timing oracle. |

## Queries and failed searches

Queries run/reviewed on 2026-08-31:

- `2024 2025 2026 CSI baseline reliability stale baseline edge Wi-Fi CSI trustworthiness OpenCSI`
- `2024 2025 UWB link node system trustworthiness CIR ranging error source classification`
- `2024 2025 local differential privacy edge resource allocation deadline scheduling`
- `2024 2025 privacy preserving schedule publication inverse scheduling edge online reservation`
- `2024 2025 CRDT escrow bounded counter edge resource allocation offline`
- `2025 2026 Pi 5 power supply camera transient image capture reliability`
- `2024 2025 rolling shutter flicker phase adaptive exposure fiducial marker`
- `RGB NoIR camera synchronization registration edge reliability risk router 2024 2026`

Failed or incomplete retrievals are explicit: no inspected primary source gave
an exact bounded-counter CRDT edge thesis distinction; the full Yang (2025)
accepted PDF sections, Shan VCIP 2025 PDF/limitations, RocSync full paper and
Kim--Baek full paper were not audited page-by-page. These are [GAP], not
novelty evidence. MDPI contamination/power pages can be rate-limited, so their
quantitative claims are not load-bearing here.

## Decision

`CSI-BaselineGate`, `UWB-RL-CAUSE`, `MAG-GeometryWitness`,
`MMW-ClutterWitness`, `AQ-ReferenceFreeAudit`, `SCHED-PUB-STREAM`,
`PSI-EVENT-JOIN`, `RVK-LOCAL-LEASE`, `DP-BUDGET-MICROEDGE`,
`FLICK-PHASE`, `RS-DRIFT`, `ACR-MODE`, `ASI-IR`, `EV-EXPO`,
`MOD-MISSING`, `OPT-WIT`, `CAL-TRANSPORT`, and standalone RGB/NoIR
synchronization are **KILL** as thesis mechanisms. `PWR-WIT` is **PIVOT** to
instrumentation only. `CRDT-ESCROW-LIMIT` is **PIVOT** to a baseline or
negative replication. `PRF-TR`, `PHY-MASK`, and `FULL-CAP` are **PIVOT** to a
finite physical-vs-digital action audit. `PLAR-Safe` is **PIVOT** only to a
negative privacy--deadline frontier. `IR-CAUSE` is **HOLD / Amber** only as a
finite active-IR incremental-information test against the fixed two-shot and
passive-health baselines. No candidate passes the three audits or should be
called novel. **HOLD**
