# Validation Audit: 2026-08-28 common edge-FYP claims (no supplied candidate packet)

## Decision investigated

Gate 1 asks whether any presently supplied direction can be promoted. At audit start, `research/active/01-candidate-register.md` contained no candidate and `research/ops/divergence/` had no packet. This audit therefore investigates a **kill map**, not a positive direction: common low-cost edge-sensing/reliability claims which must not enter the register without a narrower, falsifiable difference. Status labels below distinguish supported facts `[K]`, empirical results `[E]`, conjectures `[C]`, and unresolved matters `[GAP]`.

Scope of the search: original or official versions available on 2026-08-28; Google/ArXiv/IEEE queries logged below. I read the task, system model/assumptions, evaluation, and conclusion/limitations where the full text was available. No absence-of-results finding is used as novelty evidence.

## Claim under test

The following recurring claim families are under test:

1. "We quantize/prune/distil a model and deploy it on Raspberry Pi/MCU."
2. "We combine edge, gateway, and cloud inference adaptively for reliability/energy."
3. "We schedule sampling/offloading from latency, energy, privacy, or freshness."
4. "We fuse RGB/NIR/ToF or several sensors to improve edge reliability."
5. "We use confidence/uncertainty/abstention to make the edge system safe."
6. "We train/adapt privately with federated learning at the edge."

No one of these is currently an active proposal. Any future candidate must specify: decision-maker, action, error harm, observation variables, fixed deployment budget, target loss, and a direct baseline capable of refuting its claim.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | `[K]` Francy and Singh combine CNN compression (structured/unstructured pruning and dynamic quantization) with edge-device evaluation. `[K]` de la Fuente et al. combine TinyML compression, ESP32/gateway/cloud hierarchy, and adaptive inference location for industrial condition monitoring. `[K]` Sathyavageeswaran et al. combine local/MEC decision, update freshness, and MEC-use cost. | A future candidate might differ only if it couples a **measured sensor-failure signal** to a predeclared safety action/loss under a bounded resource policy. Whether such a combination is free of collision is `[GAP]` until its exact task and observations exist. | High for the three generic combinations; low for any residual distinction. |
| 2. Exact-claim collision | `[KILL]` A claim whose endpoint is accuracy/latency/model size after compression has direct collision with Francy and Singh. `[KILL]` A claim whose endpoint is adaptive local/gateway/cloud placement balancing accuracy, latency, and battery for predictive maintenance is directly overlapped by ESN-PdM. `[KILL]` A claim of deriving a generic fresh-update/offload policy with MEC-use cost is directly overlapped by the AoI MDP work. | The collision does **not** establish that an operational reliability decision is impossible. A candidate would need a different input (e.g., observed sensor-health signature rather than only service state), a different action (safe fallback/inspection/defer), and an endpoint tied to harmful errors rather than only aggregate accuracy/AoI. `[GAP]` no supplied statement to compare. | High for stated generic claims; cannot rate residual claim. |
| 3. Boundary / impossibility | `[KILL]` A sensor-failure claim is unidentifiable if the planned observations contain only a model score: the same score distribution may arise from a hard but valid input, distribution shift, or failing sensor. `[KILL]` A safety claim is untestable if it has no action cost and no labelled/counterfactual failure condition. `[K]` Online selective classification with limited feedback gives a tight trade-off between mistakes and excess abstention; it rules out treating free abstention and scarce labels as an unconstrained safety win. | A falsifiable boundary study remains possible if the candidate injects or measures a declared fault class, separates it from task changes, reports selective risk and coverage plus energy/latency, and includes an abstain/fallback action with cost. This is a conditional design requirement, not established novelty. | High for logical identification failures; medium for transfer of the selective-learning bound to any future sensing protocol. |

**Novelty status:** all six broad claim families are `Red` as central claims. A sensor-health-conditioned, decision-aware reliability claim is only `Amber` at most, because it has not passed exact-claim or boundary audits against a defined candidate.

## Assumption and identification audit

* `[KILL]` Let `Y` be the operational state, `X` the sensor stream, `F` a sensor-fault state, `A` the edge action, and `L(Y,A)` the decision loss. From `X` or a model confidence alone, `F` cannot be identified without an observation model or labels/controlled fault protocol that separates `P(X | Y,F=1)` from `P(X | Y,F=0)` and from environmental/task shift. A lower error after synthetic Gaussian noise alone demonstrates robustness to that injection, not field fault detection.
* `[KILL]` If abstention/fallback is permitted but its delay, energy, operator burden, and false-alarm cost are not measured, "safer" has no operationally testable meaning. The relevant simple action may be a fixed threshold, always-local, always-offload, or fixed-period recalibration.
* `[GAP]` Available device, sensor, energy meter, data rights, test environment, FYP duration, and ethics approval are unconfirmed in the charter. Therefore feasibility cannot be passed; public data alone does not prove that a claimed physical sensor degradation mechanism is observable.
* `[K]` Sathyavageeswaran et al.'s theorem depends on a specific model: generate-at-will source, geometric local service, one-slot MEC service, negligible transmission time, and scheduler knowledge of service state (Sec. II, pp. 1-2). A future system cannot cite its threshold result as validation unless those assumptions are measured or defended.
* `[K]` The online selective-classification paper explicitly assumes limited feedback and proves a tight mistake/abstention tradeoff (abstract and Sec. 1, pp. 1-2). This makes labels/follow-up outcomes part of the research design rather than an afterthought.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Francy & Singh, *Edge AI: Evaluation of Model Compression Techniques for CNNs*, arXiv:2409.02134v1, 2024-09-02. https://arxiv.org/pdf/2409.02134 | CIFAR-10 image input; ConvNeXt; structured/unstructured pruning and dynamic quantization; deploy final model to an edge device. | Model size/parameters/MACs, accuracy, and inference time; abstract p. 1, Secs. III-IV pp. 5-12. | Compression plus edge deployment and accuracy/latency endpoint. | `[KILL]` deployment-only or "new compression mix" claims without a new decision target. Leaves open a claim evaluated on decision loss under measured sensing failures. |
| de la Fuente, Radrigan & Morales, *Enhancing Predictive Maintenance in Mining Mobile Machinery through a TinyML-enabled Hierarchical Inference Network*, arXiv:2411.07168v2, 2024-11-16. https://arxiv.org/pdf/2411.07168 | Vibration time series; on-sensor/on-gateway/cloud choice; TinyML optimization; alarm from condition state. | Industrial case study: accuracy, inference latency, energy; system/motivation pp. 1-2; method Sec. III pp. 6-8; evaluation Sec. V pp. 12-15; conclusion/future work p. 16. | Edge/gateway/cloud adaptive location for condition monitoring, with accuracy-latency-energy trade-off. | `[KILL]` generic hierarchy/adaptive offloading for predictive maintenance. Leaves open only a different causal observation/action/endpoint, after a direct replication baseline. |
| Sathyavageeswaran, Yates, Sarwate & Mandayam, *Timely Offloading in Mobile Edge Cloud Systems*, arXiv:2405.07274v1, 2024-05-12. https://arxiv.org/pdf/2405.07274 | Time-stamped updates; scheduler sends each to local server or MEC, can abort local work. | Infinite-horizon average cost combining AoI and MEC-use frequency; Secs. I-II pp. 1-2, baseline/threshold policies Sec. III pp. 3-4, optimality Sec. IV pp. 4-6. | Generic local-versus-edge offloading under freshness/cost. | `[KILL]` an unqualified "adaptive scheduling reduces latency/energy/freshness" claim. Requires comparison to fixed/age/service-threshold policies and a defensible non-geometric, measured observation model. |
| Ji et al., *Tiny Machine Learning: Progress and Futures*, arXiv:2403.19076v2, 2024-03-28. https://arxiv.org/pdf/2403.19076 | Survey of TinyML architectures, compilers, inference/training. | Sec. V, pp. 17-18 identifies expensive/difficult supervision for on-device domain adaptation and summarizes co-design constraints. | Not a direct experimental neighbor; identifies the labels and resource assumptions routinely hidden by a TinyML proposal. | `[K]` supports feasibility risk, not a collision finding. A proposal cannot treat future-work prose as a gap without later-paper checks. |
| Chen et al., *Online Selective Classification with Limited Feedback*, NeurIPS 2021, https://papers.nips.cc/paper_files/paper/2021/file/79b6245ff93841eb8c120cec9bf8be14-Paper.pdf | Edge device classifies locally or queries a costly cloud model; limited feedback; may abstain. | Mistakes and abstention; abstract and Sec. 1 pp. 1-2; lower/tight tradeoff stated in abstract. | Confidence-based local-versus-cloud routing/abstention under resource constraint. | `[KILL]` generic confidence cascade or abstain/offload claim without comparing selective risk, coverage, and feedback assumptions. Leaves open sensing-fault observability measured in a physical task. |

**Citation-chain audit:** for the three most direct items, I inspected the 2024 papers' related-work/reference framing and searched their title plus `cited by`, `replication`, `limitation`, and `2025/2026`. No authoritative, exhaustive forward-citation index was available in the audited sources. The absence of a verified later collision is `[GAP]`, not evidence of a gap. Before any candidate is promoted, the coordinator must repeat a bounded forward/backward chain from its one closest paper using an official/author index, OpenAlex/Crossref record, or the venue's cited-by link, and record the retrieved date.

## Strongest simple baseline

For any proposed sensor-health-aware edge policy, the minimum baseline suite is:

1. **Always-local lightweight model** and **always-offload/high-capacity model**; they expose whether routing has value.
2. **Fixed-period sampling/recalibration** and a **fixed confidence/quality threshold**; they test whether adaptation merely rediscovers a static rule.
3. **Age/service threshold offloading** from Sathyavageeswaran et al. where comparable; it is a stronger baseline than an arbitrary scheduler for freshness/cost.
4. **No sensor-health feature** with the same backbone, plus simple missing-channel masking/imputation; this isolates claimed sensing-reliability value from model capacity.
5. **Abstain/fallback** with the same coverage or the same action budget; otherwise a method can buy apparent safety simply by declining more decisions.

`[KILL]` If one of these matches the proposed policy's harm-weighted loss within uncertainty bounds while using no new mechanism, the proposed mechanism is not a defensible FYP contribution. Exact statistical thresholds remain `[GAP]` until the task, sample unit, and number of deployments are specified.

## Contrarian result

The strongest negative result is procedural but substantive: no currently registered candidate survives because none specifies a target that is distinguishable from (a) established compression/deployment evaluation, (b) adaptive hierarchy for condition monitoring, (c) generic local/MEC freshness-cost scheduling, or (d) selective local/cloud classification. A reliability story alone cannot repair this: without independently observable sensor-health evidence and an action-specific loss, the intended fault state is not identifiable from confidence alone.

The viable pivot class is **not** "add uncertainty/fusion." It is a bounded empirical failure-analysis question: under a predeclared, observable fault protocol and fixed edge budget, does a sensor-health-conditioned fallback reduce harm-weighted loss versus static quality threshold, missing-channel baseline, always-local, and always-offload? This remains `Amber` until an exact task/data/hardware statement passes all three audits.

## Feasibility audit

| Requirement | Current finding | Gate consequence |
| --- | --- | --- |
| Data and fault labels | `[GAP]` No confirmed public dataset or permission provides both task labels and realistic, independently annotated sensor failure/degradation states. Synthetic perturbations are only a controlled stress test. | HOLD. Identify one dataset or collectable protocol before candidate registration. |
| Hardware and energy | `[GAP]` Board, sensors, accelerator, battery/power-meter access, and network-control access are unknown. | HOLD. No claim about edge energy or low cost is currently measurable. |
| Ethics and deployment access | `[GAP]` Human/industrial collection access and operating permissions are unknown. | HOLD. Avoid stories requiring live safety-critical control until permission and fallback are confirmed. |
| Compute and time | `[GAP]` FYP timeline/team/compute are unconfirmed. | HOLD. Start with a public-data, single-device minimal counterexample and reproduce closest baseline before new method work. |
| Reproducibility | `[K]` ESN-PdM supplies a concrete deployment-style neighbor, but its mining setting is not automatically reproducible for this project (case-study scope and data access must be checked; Secs. IV-V). | Do not promise replication until code/data license and hardware compatibility are verified. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Compression plus an edge-device accuracy/latency evaluation already exists. | `[K]` | Francy & Singh, arXiv:2409.02134v1, 2024-09-02, https://arxiv.org/pdf/2409.02134 | Abstract p. 1; Secs. III-IV pp. 5-12. | One image-classification study; enough to kill generic deployment novelty, not every task-specific reliability claim. |
| Adaptive sensor/gateway/cloud inference for PdM has an industrial case-study neighbor. | `[K]` | de la Fuente et al., arXiv:2411.07168v2, 2024-11-16, https://arxiv.org/pdf/2411.07168 | Abstract p. 1; motivation/contributions pp. 2-3; Sec. III pp. 6-8; Sec. V pp. 12-15; conclusion p. 16. | Mining vibration context; requires exact comparison for a future domain. |
| AoI-cost local/MEC scheduling admits threshold policies under stated assumptions. | `[K]` | Sathyavageeswaran et al., arXiv:2405.07274v1, 2024-05-12, https://arxiv.org/pdf/2405.07274 | Abstract p. 1; Sec. II pp. 1-2; Sec. III pp. 3-4; Sec. IV pp. 4-6. | Assumes geometric local service and one-slot MEC; do not overgeneralize theorem. |
| Feedback-limited selective local/cloud classification has a mistake-abstention lower-bound tradeoff. | `[K]` | Chen et al., NeurIPS 2021 PDF, https://papers.nips.cc/paper_files/paper/2021/file/79b6245ff93841eb8c120cec9bf8be14-Paper.pdf | Abstract; Sec. 1 pp. 1-2. | Not a sensor-failure paper; a formal warning against free abstention claims. |
| TinyML domain-adaptation labels can be expensive/difficult and co-design constraints matter. | `[K]` | Ji et al., arXiv:2403.19076v2, 2024-03-28, https://arxiv.org/pdf/2403.19076 | Sec. V pp. 17-18. | Survey, used for constraint discovery only, not a central collision proof. |
| A confidence-only system cannot distinguish sensor failure from task difficulty or shift without a separable measurement/label protocol. | `[KILL]` | Identification argument from the proposed observation model; no external theorem claimed. | This audit, Assumption and identification audit. | A logically sufficient counterexample; formalize for the selected task before any positive claim. |

## Queries and failed searches

Executed 2026-08-28:

* `site:arxiv.org 2024 edge AI model compression on-device inference benchmark` -> Francy & Singh (primary preprint); supports deployment collision.
* `site:arxiv.org 2024 edge computing adaptive inference scheduling mobile cloud edge` -> Sathyavageeswaran et al. and ESN-PdM (primary preprints); supports scheduling/hierarchy collisions.
* `site:arxiv.org 2025 edge AI privacy federated learning benchmark attack` -> no load-bearing primary paper selected because no supplied privacy candidate stated an exact claim. This is a failed/insufficient search, not evidence of remaining novelty.
* `"sensor failure" "abstention" edge machine learning 2024` and `"selective classification" "edge" sensor 2025` -> found selective-learning theory and non-primary leads, but no verified 2024-2026 primary exact collision for a **not-yet-defined** sensor-health-conditioned decision. `[GAP]`.
* `"sensor degradation" "edge" "uncertainty" machine learning 2024` and `site:arxiv.org/abs "sensor reliability" "edge" 2025` -> non-authoritative/insufficient leads; no conclusion made.
* Exact-title forward searches for the three direct neighbors plus `cited by`, `replication`, `limitation`, `2025`, and `2026` -> no authoritative exhaustive citation chain captured in this round. `[GAP]`; required before promotion of an exact candidate.

## Decision

**PIVOT**

No supplied candidate can be promoted because none existed at audit time. Treat deployment-only compression, generic edge/cloud scheduling, generic sensor fusion, confidence-only safety, and generic federated/privacy claims as pre-killed patterns. The next candidate, if any, must enter as `Amber/HOLD` with an exact sensor-fault observation model, safety action and harm-weighted endpoint, a matched simple-baseline suite, and a bounded citation-chain audit.
