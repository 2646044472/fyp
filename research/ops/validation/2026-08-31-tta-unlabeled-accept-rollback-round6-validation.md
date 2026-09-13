# Validation Audit: 2026-08-31 TTA unlabeled accept/rollback

## Decision investigated

Whether the remaining Amber residual in
`.research/tta-unlabeled-accept-rollback/FINDINGS.md` can be a low-cost edge
FYP: a local edge node runs a frozen checkpoint and one or more **shadow TTA
updates** on an unlabeled stream, then emits `accept update / keep checkpoint /
abstain` by first diagnosing whether an observable proxy is valid for true
target risk.  The residual explicitly excludes a generic shift trigger,
generic adaptation algorithm, a confidence threshold, and a generic
trigger-adapt-rollback controller.

## Claim under test

**Amber claim under test.** Given only the current inputs, source/candidate
logits, unlabeled proxy losses, and inexpensive device telemetry, a local
controller can identify an *observable proxy-validity region* in which it is
safer to accept a shadow update than retain the checkpoint, and abstain outside
that region.  It would be evaluated by true held-out labels, but those labels
would not be available to the controller at decision time.

The claim is materially stronger than an empirical correlation result: it asks
the controller to choose the lower-risk model on a new target regime.  The
proposed observation set does not include an independently validated label,
physical witness tied to the semantic task, or an intervention whose outcome
reveals correctness.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | AETTA estimates adapted accuracy from unlabeled prediction disagreement and gives a recovery case study.  Kim et al. select TTA hyperparameters/checkpoints using unlabeled model agreement.  Schirmer et al. turn an unlabeled proxy into a sequential TTA-risk alarm.  These are exactly the candidate's source/candidate prediction, proxy, choose/recover components. | A specifically named commodity sensor telemetry feature is not present in those vision papers.  Adding it is only new information if it is independently shown to change the relation between proxy and task loss; no such observable is named or measured in the current candidate. | High for collision; high for the unresolved witness requirement. |
| Exact-claim collision | AETTA's stated task is label-free accuracy estimation after TTA and its recovery case chooses a recovery from that estimate.  NeurIPS 2024 agreement-on-the-line evaluates adaptation choices including checkpoints without OOD labels.  NeurIPS 2025 detects when an evolving TTA model must be taken offline under an unlabeled stream. | None for the no-label `accept candidate because the proxy is valid` endpoint.  The 2025 paper explicitly leaves an *unsupervised diagnostic of proxy-assumption violation* for future work, but future work is not evidence that the same endpoint is identifiable or available to this FYP. | High for the broad endpoint collision; high that the alleged distinction is only a gap. |
| Boundary / impossibility | The 2025 monitor requires its proxy-separation Assumption 1 and states that checking it for a proxy on a given stream requires a labeled test stream.  With the candidate's observations, two target label mechanisms can produce the same inputs, logits, proxy and telemetry while reversing whether the update helps.  Shadow execution changes computation, not information about labels. | A restricted result could be defined **only** after adding a verified structural assumption, e.g. delayed random target labels, an independent task-validity witness with premeasured error, or a mathematically specified invariant class.  No present hardware/data plan supplies one. | High. |

## Assumption and identification audit

Let `O` denote every decision-time observation named by the residual: target
inputs `X`, source and candidate predictions/logits, proxy scores, timing,
memory/energy/thermal telemetry, and the controller's random seed.  A shadow
policy is a measurable map `a(O)` to `{accept, keep, abstain}`.

**[KILL] Observational counterexample (formal derivation).** Consider a binary
target stream with the same realised `X=x` and therefore the same `O=o` in two
worlds.  Let the source checkpoint predict `0` and the shadow candidate predict
`1` on each item.  In world A, `P(Y=0 | X=x)=1`; accepting the candidate incurs
unit loss and keeping the source incurs zero loss.  In world B,
`P(Y=1 | X=x)=1`; those losses reverse.  Every proxy derived from `O`, including
source/candidate disagreement, entropy, dropout disagreement, drift score and
hardware telemetry, is identical in the two worlds.  Thus `a(o)` must take the
same action in both worlds, and cannot certify which model has lower target
risk.  Randomization merely randomizes the same unavoidable error.  This is a
conditional-label/semantic-shift counterexample, not an assertion that all
restricted covariate-shift settings fail.

An `observable abstention region` is also a function of `O`.  It can reduce the
frequency of decisions, but it cannot certify that an accepted point belongs to
world A rather than B.  If it abstains on every ambiguous `o`, it is the
conservative baseline below, not a model-selection contribution.

Schirmer et al. make this limitation concrete rather than remove it.  Their
Assumption 1 requires the proxy to separate high- and low-loss examples and to
remain stable across time-varying test distributions (Sec. 3.2, PDF p. 4).
Their Sec. 6, PDF p. 10 states that verifying Assumption 1 for a given proxy
requires a labeled test stream and calls unsupervised violation diagnostics
future work.  Therefore a proposed telemetry diagnostic cannot be called a
validity certificate merely because it correlates with failures in a planted
bench condition.

**[KILL] Shadow-update non-intervention.** Running candidate weights on the
same already observed `X` creates additional logits but does not reveal `Y` or
change the physical scene.  It does not break the counterexample.  Its only
new quantities are the already-occupied disagreement/accuracy-estimation
family.  An actual intervention would need an outcome outside `O` (for example,
a correctly timed independent reference measurement), turning the project into
a separately specified sensing-action study rather than this TTA direction.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Lee et al., **AETTA**, CVPR 2024, pp. 28643-28652 | Unlabeled stream; target prediction versus dropout inferences; predicts adapted accuracy; recovery case study. | Accuracy-estimation error across six TTA methods and recovery based on estimate. | Label-free post-adaptation performance estimate and recovery/rollback decision. | **[KILL]** Generic shadow-disagreement/proxy estimate plus rollback.  It leaves no evidence that a new sensor telemetry score identifies proxy validity. |
| Kim et al., **Test-Time Adaptation Induces Stronger Accuracy and Agreement-on-the-Line**, NeurIPS 2024, 37 pp. | Adapted candidate models across learning rate, steps, batch size and checkpoints; unlabeled model agreement. | OOD accuracy estimation and choosing TTA strategy/hyperparameters without OOD labels. | Direct collision with multiple shadow updates/checkpoints, agreement proxy, and unlabeled model selection. | **[KILL]** Recasting the candidates as `shadow` does not change input, action, or endpoint.  Its empirical laws are not universal guarantees; the paper notes further theoretical conditions are needed (Sec. 2, PDF p. 3). |
| Schirmer et al., **Monitoring Risks in Test-Time Adaptation**, NeurIPS 2025, 34 pp. | Unlabeled features plus source calibration data; evolving TTA model; uncertainty proxy and online proxy thresholds; risk alarm/offline action. | Sequential true running-risk threshold violation with an assumption-dependent confidence sequence. | No-label TTA risk proxy, online thresholding, model evolution, and take-offline/fallback decision. | **[KILL]** Generic observable-risk/abstention monitor.  It leaves only a *verified* way to test proxy separation, which the candidate lacks; the paper says labeled target data are required to verify the assumption (Sec. 6, PDF p. 10). |
| Lamaakal et al., **Drift-to-Action Controllers**, arXiv:2603.08578v1, 2026 | Unlabeled monitor/belief plus uniformly sampled delayed labels; actions include adaptation, label query, rollback, abstain/handoff and retraining under budget/cooldowns. | Anytime-valid current-risk upper bound, safety violations, recovery, operational cost. | Exact controller action set, resource story, risk gate and fallback, once any target supervision is admitted. | **[KILL]** The label-assisted escape hatch.  It leaves no no-label certificate; its safety theorem requires randomly sampled labeled windows (Sec. 4.2-4.6, pp. 4-5). |
| Danilowski et al., **BoTTA**, SenSys 2026, pp. 465-477 | Periodic on-device TTA on Pi 4B/Jetson; limited samples/classes/diverse and compound shifts; energy, latency, memory. | Practical on-device TTA benchmark; target accuracy measured offline. | Pi-class deployment, periodic shadow/adaptation, small data and hardware profiling. | **[KILL]** A board/runtime/energy demo as contribution.  It also shows a dangerous feasibility fact: no assessed method significantly improved the source model in its low-data regime (Sec. 10). |
| Li et al., **Exploring Human-in-the-Loop TTA**, arXiv:2405.18911v1, 2024 | Candidate models from TTA settings; active selection of sparse annotations; labels used for model selection and supervised updates. | TTA error under annotation budgets and wall-clock adaptation cost. | Sparse-label model selection after shadows/candidates are formed. | **[KILL]** A generic small-human-label selection or validation policy.  It leaves only a different, named physical source of labels, which current scope forbids/does not supply. |

## Strongest simple baseline

The decisive baseline is **frozen source checkpoint + no unverified update**:

1. Use a source-calibrated, declared finite-support/OOD rule only to emit
   `serve checkpoint` or `unknown`.
2. Never accept a shadow candidate without a delayed random target-label audit
   (or another independently validated semantic witness).
3. If labels are permitted, use uniform delayed-label sampling and the
   Drift2Act-style upper-risk gate; compare `keep / adapt / rollback / abstain`
   at the same label and action budget.

For the no-label candidate, this baseline is not merely conservative
engineering.  Under the counterexample it is the only policy that avoids a
false assertion that the update has lower target risk.  If the proposed policy
accepts beyond this baseline, it can be wrong in an indistinguishable world; if
it does not, its purported accept/rollback contribution disappears.  When
labels are introduced, the direct neighbor supplies the same action family and
certificate.

## Contrarian result

**[KILL] The narrow Amber residual does not survive.**

The apparently open phrase "diagnose when a proxy-to-risk assumption is valid"
contains the unobserved conclusion it tries to obtain.  The closest primary
paper both provides the strongest available unlabeled monitor and explicitly
states that validity of the relevant proxy assumption needs labeled target data
to check.  The formal two-world construction shows why a telemetry/logit-only
diagnostic cannot repair this in the stated unrestricted setting.  The
shadow-update variation is occupied by AETTA/agreement-based model selection;
the label-assisted variation is occupied by Drift2Act/HILTTA.

This is an informative negative result: a later physical sensing candidate may
use it as a gate.  Before treating a local proxy as a risk certificate, it must
pre-register (a) the independent observation or sampled label that makes the
proxy-risk link testable, (b) the shift class it excludes, and (c) an
equal-budget frozen/unknown baseline.  That lesson is not itself a new TTA FYP
mechanism.

## Feasibility audit

| Item | Audit result |
| --- | --- |
| Hardware | A Pi-class benchmark is feasible, but BoTTA already tests Pi 4B/Jetson resource use.  Hardware does not add an independent label or proxy-validity observation. |
| Data and labels | Standard corruption datasets can provide offline labels, but then the claimed live controller did not possess the information used to establish proxy validity.  A real task needs delayed random labels or an independent semantic reference; neither data source is committed. |
| Compute/time | A small TENT-style reproduction by December is technically plausible; multiple shadows, dropout passes and on-device backprop make the demo less rather than more distinctive.  BoTTA reports high resource costs for several methods. |
| Evaluation | To test the claim, split by physical/domain cells before proxy selection, hide labels from controller, and report false accepts.  But outcome labels are still necessary offline, and a planted image corruption only validates that planted family, not a general proxy certificate. |
| Ethics/story | A non-personal tabletop/benchmark task avoids ethics burden, but lacks a named operator, independent semantic truth process, and consequential action beyond a synthetic classifier score.  It therefore fails the FYP story/feasibility gate as currently specified. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| AETTA uses prediction disagreement to estimate TTA accuracy without labels and demonstrates recovery. | [K] | Lee et al., CVPR 2024, pp. 28643-28652. Official PDF: https://openaccess.thecvf.com/content/CVPR2024/papers/Lee_AETTA_Label-Free_Accuracy_Estimation_for_Test-Time_Adaptation_CVPR_2024_paper.pdf | Abstract and Sec. 1, PDF p. 28643; official proceedings record identifies pp. 28643-28652. | The audit did not verify a universal guarantee; this establishes task/action overlap only. |
| TTA improves agreement-on-the-line and uses it for unlabeled OOD performance estimation/model selection, but theoretical conditions remain needed. | [K] | Kim et al., NeurIPS 2024, PDF: https://papers.nips.cc/paper_files/paper/2024/file/d96fcc07d623a9eba68616629911143a-Paper-Conference.pdf | Abstract PDF p. 1; Sec. 2, PDF p. 3; Sec. 3/Fig. 2, PDF p. 4. | The paper reports empirical laws, not an unrestricted safety certificate. |
| The 2025 risk monitor assumes a proxy separates high/low loss across time; violating it makes bounds invalid/vacuous, and verifying it requires labeled target data. | [K] | Schirmer et al., NeurIPS 2025, PDF: https://proceedings.neurips.cc/paper_files/paper/2025/file/746960ad49ddb47248970a0e1404230c-Paper-Conference.pdf | Sec. 3.2, PDF pp. 4-5 (Assumption 1, Proposition 1); Sec. 3.4, p. 5; Sec. 5.2, pp. 7-8; Sec. 6, p. 10. | Central direct neighbor.  The label-requirement statement is their limitation, not a proof of every possible physical witness's failure. |
| Drift2Act uses delayed random target labels for an anytime-valid risk upper bound that gates adapt/rollback/abstain. | [K] | Lamaakal et al., arXiv:2603.08578v1, 2026-03-09: https://arxiv.org/html/2603.08578v1 | Sec. 1, p. 1; Secs. 4.1-4.6, pp. 4-5; Table A.1/Appendix A, pp. 9-10. | Preprint/workshop version; it is a direct method neighbor for any label-assisted pivot, not validation of an FYP's data access. |
| On-device periodic TTA has been benchmarked on Pi 4B/Jetson and low data can fail to improve a source model. | [K] | Danilowski et al., SenSys 2026, DOI https://doi.org/10.1145/3774906.3800498; author preprint arXiv:2504.10149: https://arxiv.org/html/2504.10149v3 | Sec. 4.1.5/9 resource evaluation; Sec. 5, Fig. 3; Sec. 10 takeaway (1). | Benchmark does not prove every small physical stream fails; it kills a hardware-only contribution and raises a preflight requirement. |
| Sparse human labels can select among TTA candidates/hyperparameters. | [K] | Li et al., arXiv:2405.18911v1, 2024-05-29: https://arxiv.org/html/2405.18911v1 | Sec. 1, pp. 1-2; Sec. 3.1, p. 4; Sec. 4.3/Appendix, reported annotation budgets. | Preprint; sufficient as a direct label-assisted neighbor, not a guarantee. |
| Identical unlabeled observations can reverse source-vs-candidate risk under conditional label shift. | [KILL] | Formal two-world construction in this audit; supported by the conditional proxy premise in Schirmer et al. | Assumption/identification audit above. | A logical counterexample under the candidate's unconstrained observation model.  It does not rule out an explicitly proven restricted shift family. |
| Device telemetry can independently validate proxy-to-risk alignment for the target task. | [GAP] | No primary source or named telemetry/error model supplied. | Not verifiable from current candidate. | The missing observable is the next gate, not affirmative evidence. |

## Queries and failed searches

Queries executed 2026-08-31:

- `site:openaccess.thecvf.com 2024 2025 test-time adaptation unlabeled risk estimation rollback AETTA`
- `site:proceedings.neurips.cc 2025 test time adaptation risk monitoring proxy confidence sequence unlabeled`
- `"shadow update" "test-time adaptation" 2024 OR 2025 OR 2026`
- `"test-time adaptation" "model selection" "unlabeled" 2025 2026`
- `"Reliable Test-Time Adaptation via Agreement-on-the-Line" arxiv`
- `"Drift2Act" adaptation abstention rollback retraining`
- `"randomly sampled delayed labels" "test-time adaptation" rollback`
- `"test-time adaptation" "anytime-valid" "rollback"`

Failed/negative retrieval observations:

- No primary paper was found that makes a generic Pi/thermal/logit telemetry
  vector an independently validated witness of **semantic target-label**
  correctness for a shadow TTA update.  This is not evidence of novelty; it is
  an unresolved requirement defeated by the counterexample unless a concrete
  restricted observation model is supplied.
- Searches for `shadow update` retrieve operations/MLOps language and ordinary
  multi-candidate selection, not an independently observed proxy-validity
  theorem.  The existing AETTA and agreement-on-the-line works already occupy
  the relevant no-label performance-selection mechanism.
- No current target task, physical sensor, label-delay process, or independent
  semantic witness is committed, so a reproducible FYP minimum experiment
  cannot be specified honestly.

## Decision

**KILL.** Do not promote or implement the remaining no-label
proxy-validity/observable-abstention/shadow-update direction as an FYP.  It is
either an occupied proxy-based TTA selection/recovery controller, an
unidentified target-risk claim, or, after adding labels, an occupied
label-assisted risk-control controller.  Retain only the negative boundary as
a screening rule for future candidates.
