# Divergence Packet: 2026-09-02 alternatives for two Raspberry Pis

## Decision investigated

Whether the newly available Raspberry Pi 4 and Raspberry Pi 5 (8 GB) plus camera/USB-Gadget setup support research directions other than palm recognition or generic RGB/NoIR adaptive sensing. The decision investigated here is **which bounded, falsifiable alternatives deserve a validation pass**; no direction is promoted as novel.

## Search boundary

Local constraints read first: `research/ops/agent-divergence.md`, `research/active/README.md`, `research/active/00-project-charter.md`, and `research/active/01-candidate-register.md` (2026-09-02). The active files already kill generic adaptive sensing, privacy, runtime-stress, storage-fault, active-viewpoint and palm-recognition mechanisms. The hardware confirmed by the coordinator is Pi 4 + Pi 5 8 GB, USB Gadget networking, and NoIR v2; RGB camera, IR illuminator, meters, and fixed mount are treated as [GAP] until re-confirmed.

Web queries (year pinned): `2025 edge computing Raspberry Pi federated continual learning resource constraints`; `2025 ICCV cooperative perception communication efficient collaboration robust`; `2025 split inference intermediate feature reconstruction attack`; `2025 Raspberry Pi federated learning WiFi Ethernet measurements`.

## Recent-paper limitation map

* [K] Li et al., *Resource-Constrained Federated Continual Learning: What Does Matter?*, NeurIPS 2025, evaluates more than ten FCL methods, six datasets, and memory/computation/label-rate constraints. The paper's PDF Secs. 1-3 (pp. 1-5) report that methods fail under severe compute/label constraints and that the benchmark used 1,000+ GPU hours. This is a strong warning against proposing another FCL algorithm, but leaves a small-device, real-network replication/negative endpoint.
* [K] Hayek et al., *Federated Learning over 5G, WiFi, and Ethernet: Measurements and Evaluation*, arXiv:2504.04678v1 (2025-04-07), abstract and Sec. 3 as exposed in the official record, deploy Raspberry Pis and instrument aggregation/training/uplink/downlink; their measured 5G uplink is roughly 23% of a round and 17.8x WiFi. A two-Pi USB/Wi-Fi study therefore cannot claim that basic FL instrumentation is new.
* [K] Liu et al., *mmCooper*, ICCV 2025, official CVF abstract (paper pp. 28396-28406) combines multi-agent/multi-stage communication-efficient and collaboration-robust cooperative perception under calibration errors. A two-camera Pi implementation is not a new cooperative-perception method; only an exact-marker, physical-fault action audit could remain.
* [K] Xia et al., *Theoretical Insights in Model Inversion Robustness and Conditional Entropy Maximization for Collaborative Inference Systems*, CVPR 2025, pp. 8753-8763, abstract and Secs. 1-4. It proves a conditional-entropy lower bound on reconstruction MSE and evaluates four datasets. This occupies new privacy-defense theory; a Pi split-inference experiment can only be a bounded leakage/negative audit.
* [K] Qiu et al., *Revisiting the Privacy Risks of Split Inference: A GAN-Based Data Reconstruction Attack via Progressive Feature Optimization*, arXiv:2508.20613v1 (2025-08-28), abstract and Secs. 1-4. It reports reconstruction attacks on deeper/OOD models. A new attack or privacy guarantee would collide; an honest finite measurement on the Palm demo is still possible.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| FCL-PI-NB | Two local nodes learn a non-personal stream of printed targets. A stale model can retain the wrong target; sending all images violates the local-data constraint. | Under a fixed Pi CPU, memory, label and link budget, report the accuracy-retention/energy frontier of FedAvg, FedProx, replay and distillation on a two-node incremental stream; claim only a reproducible failure boundary, not a new optimizer. | Li et al. NeurIPS 2025 (Secs. 1-3); Hayek et al. arXiv:2504.04678 (abstract/Sec. 3); Flotilla, JPDC 2025 (publisher abstract). | If a tiny static model plus FedAvg has no forgetting or a desktop simulator predicts the Pi trace, the research endpoint collapses to an engineering benchmark. | Pi 4 + Pi 5, existing printed-marker/palm-derived non-personal subset, Wi-Fi/USB link; no new hardware. Training must be small and local. |
| COOP-MARK | Two viewpoints inspect a printed maintenance marker when one view is shadowed/occluded. False retain corrupts a lab record; transmitting two full images consumes the link budget. | With an exact external marker oracle and paired physical fault cells, sending a code/confidence or a tiny feature from the second Pi reduces false-retain at fixed bytes/latency versus single-view, JPEG late fusion, fixed two-shot, and majority vote. This is a finite action audit, not cooperative-perception novelty. | mmCooper ICCV 2025; Edge-assisted progressive state estimation, TMC 2025, DOI 10.1109/TMC.2024.3509716. | Fixed two-shot or scalar quality dominates; viewpoint faults are not independent; or a compressed JPEG/control baseline matches. Then report a null/replication appendix. | Two Pis and two cameras if available; otherwise one camera moved between captures. Requires rigid mount, printed marker, transparent cover/occluder, and independent labels. |
| SPLIT-LEAK-AUDIT | Pi 4 captures locally and Pi 5 receives an intermediate representation over USB/Wi-Fi. A developer may assume raw-image privacy while the receiver can reconstruct it. | For one frozen lightweight vision model, quantify the utility/bytes/latency versus reconstruction risk of raw-JPEG, logits, intermediate features, PCA features and bounded noise; do not claim a defense. | Xia et al. CVPR 2025 (pp. 8753-8763); Qiu et al. arXiv v1 2025; Wang et al. CIS, arXiv:2212.06428. | If feature inversion is impossible at the chosen model or raw-JPEG is Pareto-optimal, the result is a useful negative boundary but not a thesis mechanism. | Two Pis, USB Gadget link, existing camera and non-personal marker images; optional attacker laptop. Avoid personal/biometric data. |
| LINK-OUTAGE-REPLAY | Two edge nodes exchange event summaries over an intermittently disconnected USB/Wi-Fi link. A duplicate or late summary can corrupt a local experiment log. | Compare append-only event IDs, sequence windows, and a source-side replay cache under controlled link cuts; claim only a measured duplicate/missing-event frontier for this protocol. | Existing active register kills generic outage observability and hash-chain/provenance mechanisms (S1/S2, CHAIN-REPLAY, RWE). | If TCP ordering plus a local SQLite journal gives the same endpoint, or cuts cannot be externally labelled, kill as a thesis and retain as systems hygiene. | No added hardware; two Pis and a controllable network namespace. Strong negative-result path, but low novelty probability. |

## Top two formalizations

### FCL-PI-NB (negative benchmark)

* **[D]** Each Pi receives a blocked non-personal image stream with class/domain increments and a declared label rate; CPU steps, RAM buffer, link bytes and joules are logged.
* **[A]** Per round choose one of frozen FedAvg, FedProx, replay, distillation, or no-update; no learned policy is introduced.
* **[T]** Fixed wall-clock, memory, label and communication budgets; held-out classes and lighting blocks are never used for updates.
* **Observable outcome:** final/average incremental accuracy, forgetting, bytes, energy, update time, thermal throttling and failed rounds.
* **Counterexample:** if a small static classifier plus FedAvg matches the best frontier, the proposed “resource-constrained FCL boundary” has no value beyond a local reproduction.
* **Negative-result value:** confirms or refutes whether the GPU-scale NeurIPS conclusions survive on two actual SBCs and a real link; it can close the direction cleanly.

### COOP-MARK (physical action audit)

* **[D]** A printed marker has independently assigned clean, shadow, transparent-cover, and occlusion cells; two fixed camera poses produce paired observations.
* **[A]** Each node may transmit `code+confidence`, a compressed ROI, or a full frame; the receiver chooses `retain / reacquire / unknown`.
* **[T]** Equal capture count and matched byte/latency (and energy if a meter is available); the exact printed code is an external oracle.
* **Observable outcome:** false-retain, false-unknown, reacquisition count, bytes, end-to-end latency and cross-cell action-rank changes.
* **Counterexample:** a fixed two-shot or quality-only rule ties or wins, or independent fault labels cannot be maintained. Then no cooperative mechanism is identified.
* **Negative-result value:** a bounded demonstration that two physical views do (or do not) add information beyond a simple baseline, without a universal sensor-fusion claim.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Resource and label budgets can collapse FCL methods | [K] | Li et al., NeurIPS 2025, PDF https://papers.neurips.cc/paper_files/paper/2025/file/721dbcfed36ef373f19a03e3e3130729-Paper-Conference.pdf | Abstract p. 1; Sec. 1 pp. 1-3; Secs. 2-3 pp. 3-5 | GPU benchmark; does not establish Pi behavior. |
| Pi FL instrumentation and link latency matter | [K] | Hayek et al., arXiv:2504.04678v1, https://arxiv.org/abs/2504.04678 | Official abstract and Sec. 3 as indexed in the author record | 5G/Wi-Fi/Ethernet testbed; two-node USB is a smaller setting. |
| Cooperative perception already addresses communication and calibration errors | [K] | Liu et al., mmCooper, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/html/Liu_mmCooper_A_Multi-agent_Multi-stage_Communication-efficient_and_Collaboration-robust_Cooperative_Perception_Framework_ICCV_2025_paper.html | Official CVF abstract; paper metadata pp. 28396-28406 | Full HTML was unavailable to this environment; section-level details remain [GAP]. |
| Intermediate features leak visual information | [K] | Xia et al., CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Xia_Theoretical_Insights_in_Model_Inversion_Robustness_and_Conditional_Entropy_Maximization_CVPR_2025_paper.html | Abstract; paper pp. 8753-8763; Secs. 1-4 | Four benchmark datasets, not Pi hardware. |
| Reconstruction attacks extend to deeper/OOD split models | [K] | Qiu et al., arXiv:2508.20613v1 (2025-08-28), https://arxiv.org/abs/2508.20613 | Abstract; Secs. 1-4 (8-page paper) | Attack implementation and hardware cost must be checked before any experiment. |
| A simple exact-marker oracle is feasible but not evidence of general scene truth | [C] | Local protocol design, informed by active `09-physical-transfer-pilot-protocol.md` | Local file, sections “oracle” and “matched-cost baselines” | Requires physical labels and a rigid fixture; currently unmeasured. |

## Queries and failed searches

Searches for a clearly unoccupied two-board Pi research mechanism in adaptive camera control, active viewpoint selection, generic sensor-health, and task-aware compression returned direct neighbors already recorded in `research/active/README.md`; those families were not re-proposed. Searches for “Raspberry Pi cooperative perception benchmark” yielded application/system papers but no evidence of a Pi-specific exact-marker action-rank endpoint; this is an unresolved [GAP], not a novelty claim.

## Decision

HOLD

The only alternatives worth a validation pass are FCL-PI-NB (explicitly a negative benchmark) and COOP-MARK (finite physical action audit). SPLIT-LEAK-AUDIT is a safe privacy appendix, not a thesis mechanism. LINK-OUTAGE-REPLAY should be kept only as systems hygiene unless a new independent source-side witness is found.

HOLD
