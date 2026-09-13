# Validation Audit: 2026-08-29 sensor-state / action protocol

## Decision investigated

**PIVOT** the proposed low-cost, non-personal benchtop inspection/maintenance-record protocol rather than promote it.  The proposal separates (i) physical/timing sensor health, (ii) scene/target observability, and (iii) task sufficiency, then selects `accept`, a harmless declared re-acquisition action, `calibration flag`, or `manual review` under a fixed action/latency/energy budget.

## Claim under test

> [C] With low-cost RGB/depth/optional-NIR observations and local telemetry, an explicit state-separated decision protocol reduces harmful automatic accepts at no greater fixed action budget than always-fuse, fixed fallback, and a quality/confidence router, on held-out partial physical degradation and hard-but-healthy scene cells.

This is not audited as a new fusion architecture, board deployment, or modality combination.  The key question is whether the **state decomposition adds decision-relevant information or a testable action consequence beyond a router using the same observations**.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | [KILL] RASMF (preprint v1, 2026) already combines a confidence-triggered selective sensor, quality descriptors, availability/missingness, cross-modal disagreement, an OOD safeguard, four output actions including referral, action cost, latency, degradation conditions, and a cost-sensitive neural router. MAMMOTH (IROS 2026 accepted, arXiv v1) already combines real robot multimodal fusion, per-modality routing, explicit missing-modality handling, collisions and manual takeovers. | [K] Neither work independently labels physical/timing health, healthy-but-hard scene observability, and task sufficiency in a low-cost tabletop record workflow. RASMF uses simulated corruptions; MAMMOTH masks complete modality tokens. This is a *scope difference*, not evidence that the proposed combination is new. | High collision; remaining distinction Amber. |
| 2. Exact task--input--action--constraint--endpoint collision | [KILL] RASMF is the strongest neighbor: image-plus-acoustic inspection; its router takes image probability, entropy, availability and descriptors, and chooses image, acoustic, joint, or referral by minimum expected action loss with sensing cost. It measures error, calibration, action cost, latency and degradation robustness. | [GAP] RASMF has no physical low-cost RGB/depth apparatus, no actual re-acquisition/calibration action outcome, and does not use truly collected partial faults. The proposed record user, target, harm, intervention and label source are still unspecified, so an exact collision cannot be ruled in or out. | Exact collision is not proven; current claim is under-specified. |
| 3. Boundary / identification | [KILL] A state label derived only from the same passive observation vector cannot improve on a Bayes-consistent cost-sensitive policy supplied that vector: the protocol is another function of the same information. RASMF's learned router is the practical baseline for this argument. Passive RGB/depth measurements can also be observationally identical under a sensor fault and a hard but healthy scene, so a causal `calibration` versus `reacquire` action is not identified without an independent diagnostic observable or an intervention. | [C] A held-out-cell *empirical* result remains possible if an explicit structured policy generalizes more reliably than an equally informed router under a predeclared distribution shift. It needs independent fault truth and genuine post-action outcomes; no theorem or cited experiment establishes this advantage. | High for the no-new-information boundary; low for a structured-generalization benefit. |

## Assumption and identification audit

Let `X` be every RGB/depth/NIR frame, quality feature, timestamp, driver status and telemetry available at decision time; let `A` be the four permitted actions; and let `L(A,Y)` be the predeclared record-error plus action-cost loss.  A quality router that receives all of `X` can implement `argmin_a E[L(a,Y) | X]`.  A separated policy that first computes `H_hat(X)`, `O_hat(X)`, and `T_hat(X)` and then chooses an action is also only a function of `X`.  Therefore [KILL] the proposal cannot claim that labels alone create lower attainable expected loss.  They can improve interpretability or finite-sample inductive bias, but those are separate empirical claims.

The more serious causal problem is [KILL] `X` may have the same realization under, for example, a camera exposure/synchronization fault and a healthy camera viewing a low-texture/reflective/occluded target; similarly a depth no-return can arise from device failure, surface geometry/material, or outside-range placement.  If the two situations have different desired recovery actions, no passive policy on `X` can consistently select the cause-specific action.  This is a direct observation-model counterexample, not a universal theorem about all instruments.

To escape this boundary, the next protocol must predeclare one of the following rather than adding a latent-label classifier:

1. [C] an independent **measured** health observable (for example, manufacturer-exposed timing/error telemetry plus a fixed calibration witness), with a false-positive/false-negative characterization separate from the scene task;
2. [C] a harmless action whose post-action observation can distinguish the two hypotheses, with recovery success and action cost measured; or
3. [C] a narrower non-causal decision: `accept` only when task sufficiency is supported, otherwise `manual review`, with no claim to select sensor repair versus scene re-acquisition.

The first two are not automatically contributions: historical active fault diagnosis and reference-target self-tests are established components. They would only make a defensible **boundary protocol** if they supply a new, independently measured observation and are evaluated against the equally informed router.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Fallahy, Rezazadeh, Caputo & De Luca, *Reliability-Aware Selective Multimodal Fusion for Concrete Crack Detection Under Sensor Degradation*, Preprints.org v1, posted 2026-07-28 | Image first; conditional acoustic acquisition; reliability descriptors, availability, calibrated uncertainty, disagreement and OOD safeguard. Router actions are image, acoustic, joint, referral. | Inspection decision, error/calibration, sensing/action cost, preprocessing/forward latency and 16 simulated degradation/missingness conditions. | Very close decision structure: quality/availability to selective sensing/fallback/referral under cost. | [KILL] Kills any claim that adaptive quality-aware sensing, referral, action-cost reporting, or a learned cost router is the contribution. [K] Leaves physical partial-fault collection and actual recovery/calibration outcomes open; its own Sec. 4.6 says simulated degradation, no physical delay and no statistical superiority to simpler fusion alternatives. |
| Kotian, Subramanyan & Sundaram, *MAMMOTH*, arXiv:2607.12965v1, 2026-07-14; accepted IROS 2026 | RGB, thermal, point cloud and velocity; per-modality routing; trajectory actions; full-modality dropout during training/inference. | Nine hours data, five unseen real off-road environments, collision rate, goal success and manual takeover/undesirable behavior. | Multimodal reliability/fallback, task-level harm and real deployed actions. | [KILL] Kills generic claims that modality routing/missing-modality robustness or task-risk action evaluation are absent. [K] Its fault model is complete token masking, not independent partial health/scene/task labels; its H100/Jetson/robot setup is not a low-cost tabletop experiment. |
| Murphy & Hershberger, *Handling Sensing Failures in Autonomous Mobile Robots*, 1999 technical report | Hypothesize causes, conduct active tests and bind recovery to cause. | Robot sensing-failure diagnosis and recovery. | Cause-separated diagnosis followed by recovery is the historical component of the proposal. | [KILL] Kills a claim to have introduced causal active diagnosis or cause-specific recovery. [GAP] It is not a modern multimodal edge benchmark or a direct hardware/action-cost collision. |
| Tao et al., *Variance-Guided Spatial Attention Fusion for Robust End-to-End Driving under Asymmetric Sensor Degradation*, arXiv:2608.24366, 2026-08-25 | Camera/LiDAR reliability maps, physically grounded simulated local corruption, sensor trust gating, closed-loop action. | CARLA driving score, route completion and infractions under complete and localized degradation. | Recent component collision for partial rather than whole-modality degradation and reliability conditioning. | [KILL] Removes any claim that partial-degradation-aware weighting is itself a fresh component. [GAP] Simulation-only driving paper; exact text beyond the official arXiv record was not fully inspected, so it is not load-bearing for an exact collision. |

## Strongest simple baseline

The mandatory `B2` is not a confidence threshold alone.  It is RASMF's cost-sensitive direct router adapted to the candidate's declared action set: feed it **all** state-protocol inputs, including any telemetry/witness available to the structured policy; train only on source cells to choose the minimum expected predeclared loss; then freeze it before the held-out fault/scene cells.  Compare it with:

- `B0`: always acquire/fuse;
- `B1`: fixed single-modality or fixed fallback;
- `B2`: equally informed cost-sensitive quality router plus `manual review`;
- `B3`: state-separated policy with exactly the same information and action/cost budget.

[KILL] If `B3` does not beat `B2` on automatic-accept harm at matched review/re-acquisition rate, the claim that explicit state separation is useful fails.  If `B3` wins only because `B2` lacks a telemetry field or receives a different action budget, the comparison is invalid.  RASMF Sec. 2.6 is particularly damaging because its router already maps quality/availability and prediction uncertainty to four actions using an expected-loss objective.

## Contrarian result

[KILL] The proposed state hierarchy is vulnerable to being a human-readable reparameterization of the same evidence that the direct router already consumes.  RASMF also reports no statistical superiority to simpler fusion alternatives (Sec. 4.6), so adding a richer hierarchy without a new measured observable is more likely to add annotation and validation burden than a defensible effect.

## Feasibility audit

- **Story:** [GAP] “benchtop inspection/maintenance record” does not yet identify a particular operator, inspected object, acceptance criterion, recovery action or concrete false-accept harm. It cannot currently satisfy the charter's real-decision gate. A harmless record error/rework cost is acceptable only when the user decision and cost are fixed before data collection.
- **Data and labels:** [KILL] RASMF's public data cannot establish this central claim: its paired image/audio records are indexed pairs, but Sec. 3.3 explicitly says matching confirms correspondence rather than simultaneous physical acquisition; its degradation/missingness is injected. A new collection needs synchronized raw frames, device telemetry, independently applied physical-fault labels, healthy hard-scene labels, task truth, action issued, and post-action recovery outcome. Random modality masks are insufficient.
- **Hardware:** [GAP] Affordable purchase permission and a one-year window are known, but no sensor SKU, telemetry API, calibration witness, power meter, actual setup action, budget or delivery status has been verified. The candidate cannot yet claim low-cost feasibility. MAMMOTH's H100 training and Jetson Orin robot do not transfer, but they also show that the claimed broad modality/action problem need not be lightweight.
- **Ethics and compute:** [C] A non-personal tabletop target and harmless re-acquisition action can avoid human-subject and safety-actuation scope. A small fixed task and conventional models may fit local hardware, but this is unverified until the target/labels/sensor API are specified.
- **Negative value:** [K] A preregistered non-superiority result against `B2`, stratified by independently labelled physical versus healthy-hard cells, is useful: it establishes that these observables do not justify cause-specific action. [C] This remains valuable only if cells, action losses and data split are predeclared and data are reusable.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| RASMF already has conditional sensing, reliability features beyond confidence, four action choices, cost accounting and a cost-sensitive router. | [KILL] | Fallahy et al., Preprints.org v1, posted 2026-07-28, https://www.preprints.org/manuscript/202607.2018 | Sec. 1.3, HTML lines 146-157; Sec. 2.1, lines 161-164; Sec. 2.6, lines 237-241; Sec. 2.7, lines 242-280. | Preprint, not peer reviewed; concrete image/audio rather than tabletop RGB/depth; direct component and baseline collision. |
| RASMF evaluates 4,094 paired samples, simulated availability/degradation, and reports its limitations: one dataset, simulated degradations, no physical sensing/communication/deployment delays, and no statistical superiority to simpler fusion alternatives. | [K] / [KILL] | Same RASMF v1 URL | Sec. 3.1-3.3, lines 281-295; Sec. 4.3-4.6, lines 327-363. | The stated limitations leave a physical-event protocol possible, but do not establish one. |
| MAMMOTH uses real robot multimodal fusion, modality-dropout masks, trajectory decisions and task harm endpoints; its dropout removes all tokens for a modality. | [KILL] | Kotian et al., arXiv:2607.12965v1, 2026-07-14, accepted IROS 2026, https://arxiv.org/html/2607.12965v1 | Abstract and Sec. I, lines 35-60; Sec. III-A/B, lines 73-94; Sec. IV, lines 111-126 and 144-167. | Full-token mask is not a physical partial-fault experiment; H100/Jetson Orin platform precludes feasibility transfer. |
| Cause hypothesis, active tests and recovery binding are established components. | [KILL] | Murphy & Hershberger, *Handling Sensing Failures in Autonomous Mobile Robots*, 1999, https://publications.ri.cmu.edu/storage/publications/pub_files/pub4/murphy_robin_1999_1/murphy_robin_1999_1.pdf | Abstract and recovery/failure-model sections, PDF pp. 1-9 (historical source recorded in archive audit). | Historical direct component, not a complete task/input/constraint collision. |
| Localized/asymmetric partial-degradation reliability gating is an active recent component line. | [K] / [GAP] | Tao et al., arXiv:2608.24366, 2026-08-25, https://arxiv.org/abs/2608.24366 | Official abstract read. | Full method/section mapping not retrieved; do not use for an exact-collision claim. |

## Queries and failed searches

Queries run on 2026-08-29:

- `"sensor health" "scene observability" "task confidence" recovery action multimodal perception`
- `"physical sensor degradation" "abstention" "reacquire" perception 2024 OR 2025 OR 2026`
- `"partial sensor failure" "active perception" recovery action multimodal robot 2024 2025 2026`
- `"sensor degradation" "quality-aware" "fallback" multimodal perception edge`
- `MAMMOTH robust multimodal off-road navigation sensor degradation missing modalities arXiv 2607.12965`
- `multimodal perception "sensor health" "recovery" "manual review" 2024 2025`
- `"sensor failure recovery" "quality" "abstention" robot perception paper`
- `"sensor degradation" "reacquisition" perception action`
- `site:arxiv.org sensor failure diagnosis recovery action "multimodal" 2025 robotics`
- `"physical sensor degradation" dataset "multimodal" 2024 2025`
- `"real sensor degradation" "multimodal" perception 2024 2025 paper`

Failed / unresolved:

- [GAP] No primary 2024-2026 source was retrieved that exactly joins low-cost RGB/depth hardware, **real partial** faults, separate health/scene/task labels, re-acquisition versus calibration actions, action cost, and record-error endpoint. Failure to retrieve this is not novelty evidence.
- [GAP] No specific affordable hardware/telemetry API or real dataset/labeling protocol has been verified for this candidate.
- [GAP] Citation-chain retrieval from MAMMOTH and RASMF was limited by their 2026 recency; future citations cannot yet settle the direct-neighbor question.

## Decision

Do not promote “state separation beats a quality router” as a direction. The only defensible next formulation is an Amber boundary/intervention question: *with an independently measured diagnostic observable and predeclared harmless re-acquisition action, does the observable change post-action record risk beyond an equally informed cost-sensitive router on blocked physical-fault versus healthy-hard-scene cells?*  Without that new observable plus real action outcome, reduce the work to a well-labelled negative benchmark/replication rather than an edge research contribution.

PIVOT
