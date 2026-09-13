# Validation Audit: 2026-08-29 Independent-Witness and Intervention Candidates

## Decision investigated

Validate the divergence packet `2026-08-29-sensing-action-identifiability.md`, especially `SAP` (state-separated sensing-action protocol) and `AIV` (action-identifiability-first sensing). The proposed story is a non-personal tabletop inspection station used by a laboratory technician: accept a component record, perform one declared reference/fixture re-acquisition, or send the episode to review. This audit treats every novelty statement as Amber and tests whether an independent witness or one physical intervention creates a defensible difference from equally informed passive routers.

## Claim under test

For a fixed false-accept and operator/capture budget, a policy that uses a separately measured diagnostic witness (for example, a reference patch) or a declared second fixture pose should lower false accepted records or unproductive retries on crossed physical-fault versus healthy-hard-scene cells, compared with an equally informed cost-sensitive router, a fixed retry, and manual review. The claim is not that a new fusion network or a generic adaptive-sampling rule is better.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Active diagnosis has long connected sensing-failure hypotheses, tests, and recovery actions (Murphy & Hershberger, 1999, Secs. 1-5, PDF pp. 1-17). Adaptive acquisition planning explicitly models state, action, reward and sequential sensor poses (Jung et al., 2024, “Definition of acquisition planning problems”, Sec. 2; “Methodical approach”, Sec. 3). ActiveInspect selects new views/modalities, crop, reference context, or termination (Wang & Wu, 2026, Secs. 2.3-3.2). | The proposed tabletop protocol would use partial, physically induced events and a human-safe finite action set rather than robot navigation or a VLM. That is a scope distinction only. | High for components; Amber for a scoped protocol contribution. |
| Exact-claim collision | Resource-Aware Safety-First Active Sensor Acquisition (Sensors 26(16):5065, 2026) already formulates cheap screening followed by high-information confirmation when uncertain/OOD, with a watchdog and resource-cost endpoint (publisher Abstract; full section/page retrieval is `[GAP]`). ActiveInspect reports budgeted evidence selection and learned termination for industrial defect decisions, and explicitly calls physical closed-loop acquisition a future extension (Secs. 3.2, 5.5, 7). Adaptive acquisition planning evaluates acquisition count, coverage and travel cost against simple heuristic/analytic baselines (Secs. 4-5). | None of the retrieved sources simultaneously specifies `device health × scene observability × task residual` labels plus a fixed human reference action on a low-cost tabletop station. This combination is unresolved, not established novelty. | Medium. Exact modern collision search remains incomplete; no promotion allowed. |
| Boundary / identification | With the same passive tuple `x`, a hierarchy of health/scene/task labels is only a reparameterization; an equally informed Bayes cost-sensitive router can choose the same action. A reference patch observes the sensing chain, not target observability; a second pose changes the observation and is generic active perception. If two latent conditions induce the same distribution of `(x, x')` but have different optimal actions, no policy using that intervention can identify them. | A genuine distinction could survive only if (i) the witness is available online and independent of the task image, (ii) the intervention has a predeclared transition and measurable post-action outcome, and (iii) the baseline is allowed the same action budget and candidate observations. | High for the boundary; empirical separation is still `[GAP]`. |

## Assumption and identification audit

1. **Health witness.** A printed reference patch or fixed reference target can detect gross camera/ToF-chain changes, but it cannot establish that the target is observable. Consumer RGB/ToF devices may expose no calibrated timing, emitter, or temperature telemetry. If the witness is merely another image-quality score, it belongs in `x` and the router subsumes it.
2. **Second pose.** A two-detent fixture is a legitimate additional observation only if pose is physically repeatable and the post-action record outcome is measured. It is otherwise a manual retry, already covered by fixed-retry baselines and next-best-view literature.
3. **Labels.** Physical fault, healthy difficult scene, and task ambiguity must be generated and labelled independently (e.g., external reference measurement and known fixture settings). Inferring the labels from the same RGB/ToF trace creates circular validation.
4. **Fair information access.** The strongest baseline must see the same `x`, same candidate action set, same budget, and same post-action observations. Comparing SAP with a passive router that is forbidden to request the witness would manufacture the gap.
5. **Outcome.** Accuracy or AUROC alone is insufficient. The endpoint must include false accepted record, successful recovery after each action, p50/p95 capture-to-decision, energy/capture cost, and manual review/retry count. A lower model error with more unproductive interventions is not a win.
6. **Identifiability test.** Before training any policy, estimate whether the proposed witness changes the conditional distribution of task correctness or action loss after conditioning on `x`. If it does not, the scientifically correct result is an unidentifiability/negative benchmark.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Murphy & Hershberger, *A Model for Robust Sensor Planning*, 1999, official PDF https://publications.ri.cmu.edu/storage/publications/pub_files/pub4/murphy_robin_1999_1/murphy_robin_1999_1.pdf | Sensor-failure hypotheses from hardware, software, or environment; active tests selected to disambiguate causes and connected to recovery methods (Secs. 1-5, pp. 1-17). | Robust robot sensing and recovery planning. | Component-level collision with cause-aware tests and recovery. | Kills “diagnose root cause then select a test” as a concept. Leaves open a narrowly scoped, modern low-cost protocol only if its endpoint and observation model are materially different and measured. |
| Jung et al., *Adaptive acquisition planning for visual inspection in remanufacturing using reinforcement learning*, JIM, VOR 2024, DOI https://doi.org/10.1007/s10845-024-02478-0 | RGB-D/point-cloud acquisition; sequential pose actions, state and reward; acquisition count, surface coverage and travel cost (Secs. “Definition of acquisition planning”, “Methodical approach”, and computational results; HTML lines 102-112, 176-182, 339-349, 496-515). | Visual inspection of starter engines; compares RL with heuristic and analytic baselines (Sec. 5). | Physical re-acquisition and costed sequential inspection overlap. | Kills a claim that a second pose plus action cost is itself new. Leaves open partial sensor-health events and a non-robot, fixed human-action protocol, but only as an empirical boundary. |
| Wang & Wu, *ActiveInspect: GRPO-Optimized Multi-Sensor Evidence Selection for Industrial Defect Detection*, Sensors 26(15):4932, VOR 2026-08-04, DOI https://doi.org/10.3390/s26154932 | Initial RGB plus selectable view/modality, crop, normal-reference context, and termination; structured evidence memory and budget `B` (Secs. 2.3-2.4, 3.2, 3.7, 5.1-5.5). | Industrial defect detection; I-AUROC/P-AUROC/F1 versus observation count (Secs. 4.1-4.8). | Evidence selection, reference comparison, termination, and cost/quality frontier. | Kills multi-view/multi-sensor evidence selection and “reference check reduces uncertainty” as a generic claim. Its own Sec. 5.5 says actions are selected from pre-acquired pools and physical closed-loop cost/failure is future work, leaving only a narrow hardware-intervention gap. |
| Wang et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, VOR 2026-08-10, DOI https://doi.org/10.3390/s26165065 | Cheap low-rate signals screen each window; uncertain/OOD/alarm windows activate high-information channels; optional watchdog bounds blind intervals. | Five-stress/CWRU/Paderborn fault warning; Macro-F1, activation rate, resource cost and activation delay (publisher Abstract; full HTML was rate-limited, so section/page details `[GAP]`). | Directly overlaps low-cost edge screening, a one-step confirmation measurement, uncertainty/OOD gating, and resource-constrained endpoint. | Strongest current kill risk for SAP/AIV. A human-safe reference/pose can survive only if it supplies an independent observable and demonstrates a different post-action record endpoint, not merely another confirmation channel. |
| Xu et al., *Look Again Before You Abstain: Budgeted Conformal Evidence Acquisition for Reliable Vision-Language Model*, arXiv:2606.16667v1, 2026-06-15, https://arxiv.org/abs/2606.16667 | Answer/abstain/acquire under bounded compute; claim-specific visual interventions; post-acquisition recalibration (Secs. 1, 4.3-4.4, 5). | Risk-coverage and finite-sample hallucination guarantee. | Three-way selective decision plus additional evidence and a strict validity endpoint. | Kills an unqualified “acquire then abstain is safer” claim. Leaves open a physical-sensor risk endpoint, but the protocol must account for intervention-induced distribution shift rather than reuse a pre-action threshold. |
| Wang, Pan et al., *An On-Device Edge-AI Agent for Reference-Free Sensor Self-Diagnosis in Multi-Pollutant Personal Exposure Monitoring*, Sensors 26(14):4526, VOR 2026-07-13, DOI https://doi.org/10.3390/s26144526, https://www.preprints.org/manuscript/202606.1041 | On-device cross-channel physical-consistency checks and fallback; no co-located reference instrument (Secs. 3.2, 4.1, 5; HTML lines 192-193, 274-283, 296-302). | Sensor trust grading and offline quality control in a 30-day indoor deployment. | Independent physical consistency witness and local fallback. | Kills reference-free health grading as a generic mechanism. Its single-site/no-reference limitations leave a possible controlled, non-personal test, but do not establish the value of a second target capture. |

## Strongest simple baseline

Use an **equally informed finite-action router** as the primary baseline. It receives the same passive tuple `x`, can choose `accept`, the same reference check, the same second pose, or `manual review`, and is evaluated with the same action budget and post-action observations. Implement at least:

- a calibrated quality-only router;
- fixed `one retry then review`;
- an empirical value-of-information table for each allowed action, fitted only on training cells;
- always-accept and always-review bounds.

If SAP is allowed a witness that the baseline cannot request, the comparison is invalid. If the finite-action router matches SAP's risk-cost frontier, explicit state labels add no demonstrated value.

## Contrarian result

The positive SAP claim is currently **not defensible as a model contribution**. The strongest direct neighbors already cover active acquisition, evidence selection, reference comparison, costed stopping, and edge confirmation. The only potentially surviving result is a protocol-level boundary:

> Under a fixed low-cost sensor and a declared one-step intervention, which pairs of physical-fault and healthy-hard-scene cells become action-distinguishable, and when does the additional observation change the empirical risk-cost optimum over an equally informed router?

This must remain Amber. A negative result (the witness does not change conditional action loss, or fixed retry is equal/better) is publishable-quality FYP evidence only in the modest sense of a reproducible boundary/benchmark; it must not be sold as a universal impossibility theorem.

## Feasibility audit

- **Hardware:** A USB/Raspberry Pi camera, inexpensive ToF module, printed reference patch, and manually repeatable two-position fixture are plausible. Actual sensor-health/timing telemetry, stable ToF SDK behaviour, and an energy meter are `[GAP]`; the project must verify these before committing.
- **Data/labels:** Hundreds of episodes across target pose/material/background, controlled occlusion/exposure/ToF-no-return, and known fixture perturbations are feasible without people or production systems. External geometric truth is needed for task labels; otherwise health and hard-scene labels are confounded.
- **Compute:** A small calibrated classifier/router can run locally; reproducing ActiveInspect or any RL/VLM policy is not feasible or necessary. The minimum experiment should use frozen features and a finite policy.
- **Ethics/safety:** Non-personal tabletop parts and no motion/safety actuation keep the story low risk. Do not describe the output as a safety interlock or production acceptance.
- **Schedule:** A fixed protocol can produce a demo by 2026-12; crossed held-out cells and repetitions fit 2027-H1. A moving robot, analogue-front-end control, or hidden telemetry dependency does not.
- **Story quality:** “Technician decides whether to retain a bench record or spend one capture/review” is concrete. Harm is rework or corrupted maintenance/experiment records, not bodily safety. Edge matters only if the local decision must be made during capture with bounded latency/storage and no remote review assumption.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Active acquisition planning already defines sequential sensor poses, states, actions, rewards and cost/coverage endpoints. | [K] | Jung et al., JIM, VOR 2024, DOI above | “Definition of acquisition planning” Sec. 2; “Methodical approach” Sec. 3; computational results/benchmark Sec. 5; HTML lines 102-112, 176-182, 339-349, 492-515 | Uses simulated/robotic inspection and point clouds, not a fixed human fixture. |
| ActiveInspect already selects multi-view/multi-modal evidence, reference context and termination under a budget. | [K] | Wang & Wu, Sensors 26(15):4932, VOR 2026 | Secs. 2.3-2.4, 3.2, 3.7, 5.1-5.5, 7; official HTML https://www.mdpi.com/1424-8220/26/15/4932 | Physical acquisition cost is explicitly future work; no claim of exact SAP collision is made. |
| Edge active feature acquisition already screens cheap signals and activates high-information confirmation under resource constraints. | [K] | Wang et al., Sensors 26(16):5065, VOR 2026 | Publisher abstract only; full section/page retrieval `[GAP]` because MDPI endpoint returned HTTP 429 | Abstract reports 98.42% vs 99.02% Macro-F1, 77.59% activation, 19.27% lower normalized resource cost; domain is bearing fault warning. |
| Naive acquisition can invalidate a selective-risk guarantee; post-acquisition recalibration is needed. | [K] | Xu et al., arXiv:2606.16667v1, 2026-06-15 | Secs. 1, 4.3-4.4, 5; official HTML https://arxiv.org/html/2606.16667 | VLM claim-grounding, not physical sensing; used only for the validity/baseline lesson. |
| Reference-free on-device physical consistency grading exists, with explicit single-site/no-reference limits. | [K] | Wang et al., Sensors 26(14):4526, VOR 2026 | Secs. 3.2, 4.1, 5; https://www.preprints.org/manuscript/202606.1041 | Personal-exposure domain; no human data used in source, but it is a direct sensor-health mechanism neighbor. |
| Cause-aware active sensing-failure tests and recovery are a foundational formulation. | [K] | Murphy & Hershberger, 1999 | Secs. 1-5, official PDF pp. 1-17 | Older source; establishes component collision, not exact modern task collision. |
| Same passive observations cannot gain information from a relabelled state hierarchy. | [C] | Decision-theoretic identification argument in this audit | No external theorem asserted | Must be tested empirically; not a global impossibility claim. |
| A reference patch or second pose changes the action-optimal risk-cost frontier for this tabletop task. | [C]/[GAP] | Proposed SAP/AIV experiment | No source yet; requires preregistered intervention and post-action labels | This is the decisive unverified hypothesis. |

## Queries and failed searches

- `2024 2025 2026 active perception sensor failure diagnosis recovery action camera calibration inspection paper`
- `2024 2025 2026 active sensor diagnosis calibration witness reference target self-test decision action paper`
- `2024 2025 2026 visual inspection active re-acquisition quality uncertainty manual review action cost paper`
- `2024 2025 2026 sensor fault diagnosis active test selection measurement action edge primary paper`
- `2024 2025 2026 task-aware sensor management measurement action uncertainty abstention physical sensor degradation paper`
- `"sensor health" "recovery action" 2025 sensing`
- `"value of information" "active perception" sensor fault diagnosis 2024`

The exact full paper for Sensors 2026, 26(16):5065 could not be fetched from MDPI in this environment (HTTP 429); only its official publisher abstract and bibliographic/version record are used. I did not treat this retrieval failure as evidence of novelty. A broader citation-chain search for a paper combining all of `partial physical event + independent witness + separated labels + human re-acquisition + action-cost endpoint` remains incomplete `[GAP]`.

## Decision

- `CVB` and `AFE`: **KILL**. Generic calibration-validity and analogue-front-end adaptation are directly occupied by the 2024/2025 calibration and 2026 task-aware front-end neighbors already recorded in the divergence packet.
- `RCP`: **KILL**. Raw/local/suppress path allocation is directly occupied by Ballotta et al. (IEEE TNSE 2024).
- `SAP`: **HOLD (Amber)** only as a boundary/protocol experiment. It must first demonstrate an independently measured witness, a repeatable intervention, and a post-action record endpoint against the equally informed finite-action router. Without those, **KILL** as a relabelled quality router.
- `AIV`: **PIVOT (Amber)** into the empirical action-identifiability map, not a separate mechanism. Promote only after the intervention changes conditional action loss on held-out cells and survives the matched router baseline.

**Overall decision: PIVOT.** The candidate is not ready to lock. The next gate is a small intervention pilot that measures whether the proposed witness changes the optimal action at all; a null result is the planned negative/pivot outcome.

PIVOT
