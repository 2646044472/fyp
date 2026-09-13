# Divergence Packet: 2026-09-03 maintenance decisions under weak connectivity

## Decision investigated

Whether factory-room, temporary-site, or mobile-repair workflows can yield a non-personal edge-computing FYP direction other than palm/face, generic adaptive sensing, camera health, outage provenance, BLE/ToF, or generic sensor diagnosis. The packet deliberately includes one negative-result candidate.

## Search boundary

Required local files read: `AGENTS.md`, `research/ops/agent-divergence.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, and `minutes/08-17.md` on 2026-09-03.

The current evidence base was used without broadening the web search after the user's interruption. Relevant inspected source chains include edge active acquisition, active fault diagnosis, acoustic/sensor self-diagnosis, label-free target-risk identification, and secure/offline state handling. No people, biometrics, employment status, or safety actuation are assumed. A low-cost sensor, relay/tachometer fixture, NFC/RFID tag, or small 3D enclosure is allowed only as an observation or truth instrument; the enclosure is not a contribution.

## Recent-paper limitation map

| Mechanism | Evidence and limitation | Consequence |
| --- | --- | --- |
| Active maintenance measurement | Bian et al. (Sensors 2026) already combine low-cost screening, high-information confirmation, uncertainty/OOD escalation, watchdogs, device shift, and resource costs. Han et al. (2025) formalize active fault diagnosis and intervention selection. | A new `measure again / inspect` policy is not enough. A survivor needs a named physical endpoint and an independently labelled action outcome. |
| Sensor-path diagnosis | Yu et al. (Measurement 2025) combine anomaly classification, physical-source rules, and local recovery. Reinhardt et al. (SHM 2025) use active electromechanical sensor self-diagnosis. | A motor, microphone, or vibration sensor replacement does not create a new diagnosis mechanism. The useful residual is a narrow measurement-sufficiency or null study. |
| Offline data handling | RFC 9019 and ESP-IDF documented update state machines already cover pending verification, self-test, rollback, and interrupted-update recovery. The active register also records CRDT/replication and outage-provenance collisions. | A local queue, hash chain, or ordinary CRDT merge is systems hygiene unless the merge changes a named maintenance decision under a new fault model. |
| Unlabelled reliability claims | Garg et al. (NeurIPS 2022) establish target-accuracy non-identifiability under arbitrary target conditional shift. Nguyen et al. (NeurIPS 2025) occupy label-free model-failure monitoring using disagreement. | A telemetry/confidence alarm cannot be called a correctness certificate without a restricted shift family or an independent witness. This supports a concrete negative-result candidate. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| **START-WIT** | During mobile repair, a technician commands a non-personal pump/fan/valve to start while disconnected. A false `running` record causes the next maintenance step to be skipped; a false `inspect` wastes a visit. | With cheap motor current plus accelerometer observations during the first 2-5 seconds after a command, a frozen sequential policy can decide `running / failed-to-start / inspect` and reduce weighted record error at fixed latency and sensor budget versus current-only, vibration-only, fixed-window fusion, and always-inspect. Independent truth is a relay/tachometer or mechanically staged on/off fixture. | Bian 2026, Han 2025, and Yu 2025 occupy active acquisition and fault-diagnosis mechanisms. The only possible distinction is a bounded command-outcome endpoint, not a new diagnosis framework. | If current-only, vibration-only, or fixed-window fusion matches; if relay state is not independent of the sensed current; or if a staged load/environment change produces the same observations, hold/kill. | Low-cost current sensor, IMU, relay, small motor/fan, Pi/MCU, and USB power meter. No personal data. Main risk is that the result is a standard sensor-fusion classifier. **HOLD pending validation.** |
| **OFFLINE-MERGE** | A repair worker records non-personal asset status (`removed`, `replaced`, `returned`) on a phone/edge box at a site with no network. Two workers later reconnect and edits conflict; accepting the wrong final state corrupts inventory and creates a repeat visit. | Under a declared asset-state transition model, a local merge policy should preserve safety-relevant state invariants and expose `conflict / resolved / unknown`, compared with last-write-wins, append-only event replay, and a standard CRDT. The endpoint is invariant preservation on a finite repair trace, not generic synchronization. | Standard offline-first replication/CRDT work and the active register's `CRDT-ESCROW-LIMIT`, outage-provenance, and local-lease audits. | If a standard CRDT or event log preserves the same invariants and conflict visibility, kill. If the transition invariant is not independently checkable from a staged asset ledger, the candidate is not research. | Very feasible in software with tagged boxes/tools and scripted partitions, but low novelty probability and weak edge-specificity. **KILL as a thesis; retain as implementation control.** |
| **CAUSE-NULL** | A disconnected technician sees a changed temperature/current/vibration trace and must mark `equipment changed`, `sensor suspect`, or `unknown`. A wrong cause label sends the repair to the wrong component; inspection is limited. | Under observations limited to one cheap sensor, its local history, model output, and ordinary device telemetry, construct two physically staged worlds with identical observable traces but different ground-truth causes. Prove that no policy can reliably choose `equipment changed` versus `sensor suspect` without an independent witness; then test whether adding one named witness breaks the ambiguity. | Garg 2022 and Nguyen 2025 establish the general identification boundary for unlabelled target risk. Yu 2025 and Han 2025 are direct positive diagnosis neighbors. The proposed contribution is a scoped physical counterexample and minimal-witness test, not a new monitor. | If the paired worlds cannot be made observationally equivalent, or if one-sensor features already identify the cause across held-out loads, the null is falsified. If a second sensor is required but adds no measurable decision value, pivot to a clean impossibility/measurement paper. | Cheapest candidate: one sensor, a controllable fault/load fixture, and an independent reference used only for labels. Formalization is feasible; experimental control and a nontrivial witness result are the risks. **PIVOT as a negative-result direction.** |

## Top two formalizations

### START-WIT

- **[D] Decision:** after a start command, emit `running`, `failed-to-start`, or `inspect` for a non-personal machine.
- **[A] Allowed action:** read current and accelerometer streams for a fixed short window; optionally request one inspection. No remote service or safety actuation.
- **[T] Target:** correct command-outcome record under a fixed latency, energy, and inspection budget.
- **Observable outcome:** false-running, false-failed-start, inspect rate, latency, joules, and decision stability across held-out loads.
- **Counterexample:** current and vibration may both change because of load or mounting, while the relay/tachometer truth stays fixed; a fixed fusion classifier may match any proposed sequential policy.
- **Negative-result value:** a null would show that cheap cross-sensor evidence does not improve the maintenance record at matched cost, preventing a generic “edge sensor fusion” claim.

### CAUSE-NULL

- **[D] Decision:** `process changed`, `sensor suspect`, or `unknown` during an offline maintenance episode.
- **[A] Allowed action:** use only one sensor trace, its history, local prediction, and ordinary telemetry; the independent reference is withheld until evaluation.
- **[T] Target:** identify the physical cause, not merely detect that the trace changed.
- **Observable outcome:** identical permitted observation distributions in two worlds, but different cause labels and different repair actions.
- **Counterexample:** world A changes the machine load while the sensor is healthy; world B changes sensor gain/offset while the machine is unchanged. Choose the disturbances so the measured trace is identical. Any policy restricted to that trace has the same output distribution in both worlds.
- **Negative-result value:** gives a defensible boundary for what an offline technician device cannot infer, and identifies the smallest added witness to test next: a relay/tachometer, second modality, or controlled reference pulse.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Resource-aware screen/confirm acquisition under device and condition shift is already studied. | [KILL] | Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, published 2026-08-10, https://www.mdpi.com/1424-8220/26/16/5065 | Secs. 1, 3.1, 5.1, and 8 | Directly relevant to any generic technician `screen / confirm` policy; the proposed motor endpoint remains unverified. |
| Active interventions for perception fault diagnosis are an established mechanism. | [KILL] | Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Abstract and Sec. 1 | Robot perception rather than motor maintenance; still a direct mechanism collision for generic active diagnosis. |
| Local sensor diagnosis plus physical-source rules and recovery already exist. | [KILL] | Yu et al., Measurement 2025, DOI https://doi.org/10.1016/j.measurement.2025.119994 | Official abstract and proposed method/recovery description; full page extraction unresolved | Exact sensor and benchmark differ; use as a collision warning, not proof that START-WIT is identical. |
| Active acoustic/electromechanical sensor self-diagnosis is established. | [KILL] | Reinhardt et al., *Self-Diagnosis of Acoustic Emission Sensors: Electromechanical Impedance-Based Damage Detection*, SHM 2025, https://www.dpi-proceedings.com/index.php/shm2025/article/view/37335/0 | Official abstract and experimental-validation description | Supports the sensor-maintenance collision; full PDF section/page audit remains [GAP]. |
| Standard embedded update state machines already handle interrupted update verification and rollback. | [KILL] | RFC 9019, *A Firmware Update Architecture for IoT Devices*, 2021, https://www.rfc-editor.org/rfc/rfc9019.html | Secs. 3-5 | Not asset-record synchronization, but it blocks presenting ordinary local state machines as a new lifecycle mechanism. |
| Unlabelled target correctness is not distribution-free identifiable under arbitrary conditional shift. | [K] | Garg et al., *Leveraging Unlabeled Data to Predict Accuracy*, NeurIPS 2022, https://openreview.net/pdf?id=wcrff7Gh0RR | Sec. 3, “Accuracy Estimation: Possibility and Impossibility Results,” PDF pp. 4-5 | General statistical boundary; the physical paired-world construction is the proposed scoped instantiation. |
| Label-free deployment deterioration monitoring is an existing positive family. | [KILL] | Nguyen et al., *Reliably Detecting Model Failures in Deployment Without Labels*, NeurIPS 2025, https://papers.nips.cc/paper_files/paper/2025/hash/0bb251eba663f0345c0929f5bbbfb6dc-Abstract-Conference.html | Official abstract; full paper Secs. 1-3 were recorded in the local evidence packet | Direct neighbor for a positive alarm; exact comparison to a maintenance-cause endpoint remains [GAP]. |
| Ordinary offline merge and append-only event handling are not sufficient novelty claims. | [KILL] | Local active evidence: `research/active/README.md`, sections “Current systems/lifecycle gate” and “Round-11 validation reconciliation” | Local sections read on 2026-09-03 | The current packet does not claim a new CRDT result; a modern CRDT primary full-text audit remains [GAP]. |

## Queries and failed searches

Queries already executed or reviewed in the current round included:

- `2024 2025 actuator outcome verification motor current vibration edge maintenance`
- `2024 2025 industrial equipment start failure detection current vibration edge device`
- `2024 2025 mobile maintenance offline work order decision support edge computing`
- `2024 2025 edge computing industrial alarm triage event suppression operator`
- `2025 unsupervised accuracy monitoring impossibility unlabeled deployment distribution shift paper`

The search was stopped before a complete RFID/NFC asset-tracking audit and before a full modern CRDT primary-paper audit. No candidate is promoted from those unresolved areas. Search snippets and the absence of an exact collision are not novelty evidence.

## Decision

`START-WIT` is **HOLD** only for a small independent-truth preflight; it must beat current-only, vibration-only, and fixed-fusion controls or be closed. `OFFLINE-MERGE` is **KILL** as a thesis because the endpoint is too close to standard offline replication and active outage/state audits. `CAUSE-NULL` is the strongest divergence value: **PIVOT** to a scoped physical non-identifiability study if the paired-world construction can be made rigorous.

Overall status: **HOLD**

HOLD
