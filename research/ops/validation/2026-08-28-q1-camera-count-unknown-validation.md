# Validation Audit: 2026-08-28 Q1 low-cost camera `count / unknown`

## Decision investigated

Whether Q1 should advance from HOLD (Amber): a low-cost local camera records a tabletop passage as `count` or `unknown`; a source-frozen detector-margin plus observable image-quality rule is tested on a held-out camera/degradation block against margin-only, quality-only, and periodic review.

## Claim under test

At a fixed manual-review (`unknown`) budget, a frozen combined detector-margin plus image-quality rule has fewer wrong retained counts than each one-signal rule on a pre-registered held-out physical camera/degradation block.

The claimed contribution is **not** a new detector, camera deployment, RGB fusion, or a generic selective-classification method.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | Gao, Stevens and Cielniak combine detector count/confidence, image quality, image clarity and other condition features into a counting-confidence model (Secs. 1, 3.1--3.5, pp. 1--3). Aher combines camera degradation/quality evidence with downstream detector reliability and fallback interfaces (Secs. I--III, pp. 1--3). | Q1's named features are fewer and its output is an abstention action rather than a scalar confidence. That is an implementation/action wrapper, not evidence of a new component. | High |
| 2. Exact-claim collision | Gao's physical lab counting task has a camera image, count decision, quality/clarity/environmental covariates, and a confidence target; its test experiment assesses the multi-factor model against a detector-information baseline (Sec. 4.1 and 4.6, pp. 3--5). | [GAP] The inspected text specifies a 7:3 train/test split but does not state a source-only, held-out-*camera-and-condition* block; it does not explicitly turn the score into `unknown` at a review budget. Absence of that statement is not proof that the protocol is new. | High collision / low confidence in residual distinction |
| 3. Boundary / impossibility | Selective classification formalizes precisely the retain-versus-abstain risk/coverage trade-off and shows the target depends on the deployment distribution (Liang et al., Secs. 1--2, pp. 1--3). A finite source policy cannot identify behavior on arbitrary unobserved physical conditions. | Q1 can honestly estimate only the stated finite target blocks; it cannot claim a guarantee for other cameras, scenes, or degradations. | High |

## Assumption and identification audit

1. **The target unit must be a passage episode, not a frame.** Adjacent frames from a passage share object, lighting, blur and detector state. Frame-random splits leak the target condition and make uncertainty artificially small. Q1 must pre-register whole-episode and camera/condition blocks.
2. **The true count requires an independent label.** A policy cannot be evaluated against the same camera trace used to choose `count`. A feasible non-human setup is a fixed, single-lane object carrier with a pre-recorded object manifest plus an independently timestamped overhead reference used only after decisions are logged. [GAP] The precise target-overlap setup must show that the manifest remains valid when overlap is induced.
3. **Quality is not causally specific.** Low exposure, partial occlusion, pose and overlap can all yield the same blur/exposure/margin vector while producing different count errors. Therefore no score-only policy can identify the error state in such indistinguishable cases; it must abstain or accept residual risk. This is a limitation of the observation model, not a reason to train a larger model.
4. **The source policy family needs selection control.** Selecting quality metric, normalization, thresholds, conjunction rule and review-budget calibration after looking at target cells invalidates transfer. The Gao paper itself selects IQA/ICA methods from condition data (Sec. 3.3, pp. 2--3), illustrating why Q1 must keep target blocks inaccessible during selection.
5. **“Raw video stays local” does not create an edge research constraint by itself.** The same score can be computed remotely and video discarded after inference. Q1 has no latency, bandwidth, energy, or local-unavailability endpoint that changes the decision problem. A board demonstration would therefore be deployment evidence only.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Gao, Stevens & Cielniak, *Counting with Confidence*, IFAC-PapersOnLine 2025 | Mean detector-box confidence and predicted count; image quality, complexity, uniformity and average-gradient clarity; polynomial regression outputs counting confidence. | Bionic-insect water-trap images, conditions including stirring speed, soil and density; 7:3 data split; MSE/R2 versus a detector-information baseline. | Count reliability from detector confidence plus observable image-quality/condition factors on a physical lab bench. | **[KILL]** Q1's proposed combined-signal mechanism. It leaves only a tightly specified transfer-evaluation distinction, which is [GAP]. |
| Aher, *Safety-Critical Camera Reliability Monitoring for ADAS*, arXiv:2605.05439v1, 2026-05-06 | Single RGB camera degradation/severity/uncertainty; evaluates camera-health signal against IQA, detector confidence and OOD baselines; supports fallback. | Synthetic 12-mode degradation and zero-shot adverse weather; detector-coupled early-warning. | Lens occlusion, motion blur, illumination/exposure and a camera reliability action are all direct components. | **[KILL]** a generic claim that image quality plus detector confidence is a fresh camera-reliability mechanism. Domain, learned monitor and endpoint differ. |
| Liang, Peng & Sun, *Selective Classification Under Distribution Shifts*, TMLR 2024 / arXiv:2405.05160v2 | Predictor plus thresholded confidence selector emits prediction or abstention. | Risk--coverage under in-distribution, label and covariate shifts. | Q1's `count / unknown` at a review budget is a task-specific selective-classification endpoint. | **[KILL]** generic abstention-under-shift claim; it leaves only a bounded physical empirical test. |
| Traub et al., *Overcoming Common Flaws in the Evaluation of Selective Classification Systems*, NeurIPS 2024 / arXiv:2407.01032v2 | Confidence score and rejection threshold. | Warns that fixed-point and AURC-only assessment can mis-rank methods; proposes task-aligned risk/coverage evaluation. | Q1 must not report only one tuned `unknown` threshold or raw accuracy. | **[KILL]** weak evaluation; does not itself duplicate camera counting. |

## Strongest simple baseline

**Gao-score-to-abstain baseline:** reproduce the published counting-confidence feature family (at minimum detector confidence/count + NIQE-like quality + clarity), fit/choose it **only on Q1's source episodes**, then threshold its score so exactly the same source-calibrated review budget emits `unknown` on target episodes. Compare it with margin-only, quality-only, periodic review and the proposed conjunction.

[KILL] If this direct-neighbor baseline equals or beats the combined two-signal rule, Q1 has no mechanism contribution. If it loses, the result still does not establish novelty automatically: the residual claim is merely that a deliberately smaller source-frozen rule transfers more robustly on the stated finite blocks.

## Contrarian result

**KILL Q1 as an independent research mechanism.** The nearest 2025 original paper already makes the central combination: detector/count information plus image-quality/clarity and physical condition information to predict count reliability. Recasting its score as `unknown` under a fixed review budget is a thresholding decision, not a sufficiently different CS mechanism. The only defensible residue is a narrowly auditable *cross-camera physical-transfer evaluation protocol*. That residue is not yet an FYP direction because:

- it has no demonstrated edge-dependent endpoint;
- no exact-protocol collision audit can be closed by a null search; and
- its main positive outcome could be duplicated by the Gao-score-to-abstain baseline.

**Pivot rule:** retain Q1 only as evaluation discipline for a different candidate: freeze all policies on source cameras, hold out whole camera/condition episodes, use independent truth, and report wrong-retained-count versus review budget. Do not promote the Q1 policy itself.

## Feasibility audit

| Aspect | Finding |
| --- | --- |
| Hardware | [C] Two or more affordable cameras plus one local computer/SBC and a fixed object fixture are plausible. [GAP] No actual model, delivery date, edge inference throughput or power budget has been confirmed. |
| Data and labels | [C] A no-human tabletop fixture can produce controllable lighting, lens occlusion, pose and overlap. [KILL] Random frame labels are inadequate; independent episode truth and a camera/condition-block split are mandatory. |
| Ethics | [K] Using printed/tagged objects and retaining no people avoids human-subject and biometric scope. |
| Time | [C] A demo by 2026-12 is plausible. [GAP] Replicated cross-camera target blocks and correct episode-level uncertainty likely require the 2027-H1 window. |
| Compute | [C] Frozen lightweight detection plus quality features is modest. This says nothing about research distinction. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Detector confidence/count plus image-quality/clarity/condition inputs already form a physical counting-confidence model. | [KILL] | Gao, Stevens & Cielniak, *Counting with Confidence: Accurate Pest Monitoring in Water Traps*, IFAC-PapersOnLine 59(23), 2025, pp. 233--238, DOI https://doi.org/10.1016/j.ifacol.2025.11.792 ; accepted manuscript arXiv:2506.22438 | Abstract and Secs. 1, 2.1--2.2, 3.1--3.5, pp. 1--3; Sec. 4.1, p. 3; Sec. 4.6 and conclusion/limitations, pp. 4--5. | Different pest/water-trap domain, richer learned feature set, and confidence-regression output. The residual frozen held-out-camera protocol is unverified, not absent. |
| Camera degradation monitoring already treats lens occlusion, motion blur, exposure/illumination and detector reliability/fallback as connected components, and compares image-quality and detector-confidence baselines. | [K] / [KILL] | Aher, *Safety-Critical Camera Reliability Monitoring for ADAS via Degradation-Aware Uncertainty Pattern Analysis*, arXiv:2605.05439v1, 2026-05-06, https://arxiv.org/html/2605.05439 | Secs. I--III, pp. 1--3; Sec. IV-A, pp. 4--5; Sec. VI-C, pp. 8--9; Sec. VII, pp. 9--10. | Under review preprint; ADAS and learned health monitor differ. It is a component collision, not an exact Q1 protocol collision. |
| Retain/abstain at a fixed coverage/review trade-off is established selective classification under distribution shift. | [KILL] | Liang, Peng & Sun, *Selective Classification Under Distribution Shifts*, TMLR 2024; arXiv:2405.05160v2, 2024-11-27, https://arxiv.org/pdf/2405.05160 | Sec. 1, pp. 1--2; Sec. 2.1--2.2, pp. 2--3. | Classification rather than object counting; kills generic framing only. |
| AURC/fixed-threshold reporting can be misleading; selective systems need task-aligned multi-threshold assessment. | [K] | Traub et al., *Overcoming Common Flaws in the Evaluation of Selective Classification Systems*, NeurIPS 2024; arXiv:2407.01032v2, 2024-10-19, https://arxiv.org/pdf/2407.01032 | Sec. 1, pp. 1--2; Sec. 2.4, pp. 3--4; conclusion, pp. 8--9. | Evaluation guidance; not a camera-counting collision. |

## Queries and failed searches

Queries run 2026-08-28:

- `2024 2025 2026 camera object detection image quality aware uncertainty abstention degradation paper`
- `2024 2025 2026 edge camera object counting selective prediction image quality object detection paper`
- `"Selective Object Detection" reject option object detection uncertainty paper PDF`
- `"object counting" "abstention" camera paper`
- `"object counting" "image quality" "confidence" paper`
- `"Counting with Confidence: Accurate Pest Monitoring in Water Traps"`
- `"Counting with Confidence" pest monitoring original paper DOI`

[GAP] The exact Q1 source-only, camera-blocked `count / unknown` protocol was not verified in the inspected primary texts. This is a retrieval gap, **not** novelty evidence. Searches for a later primary citation chain of Gao's 2025 paper produced the original IFAC/arXiv record and non-primary mirrors, but no auditable subsequent primary paper; this likewise does not establish absence.

## Decision

**KILL.** Do not promote Q1 as the FYP's sensing/reliability contribution. It is at most a useful held-out physical-transfer evaluation pattern and a required baseline package for a future, differently motivated project.
