# Validation Audit: 2026-08-31 AL-FactorQueue and UPM-EdgeBound

## Decision investigated

Try to falsify the only two PIVOTs in `2026-08-31-outside-family-divergence-round6.md` before either consumes the undergraduate FYP slot:

1. **AL-FactorQueue**: retain/request labels for an online edge stream using a pre-action physical-factor witness, claiming lower held-out unseen-factor-cell error than random, uncertainty, or diversity selection.
2. **UPM-EdgeBound**: claim a useful boundary result that unlabeled inputs, predictions, and resource telemetry cannot support a distribution-free target-error/`continue` guarantee, then characterize a minimal extra witness.

The currently active charter was read.  It permits a cheap non-personal benchtop demo, but specifically rejects a board deployment, a new dataset, or generic label-free adaptation as a research contribution.  Both decisions below remain **Amber** until all three audits pass; neither passes.

## Claim under test

| Candidate | Claimed distinction | Necessary precondition |
| --- | --- | --- |
| AL-FactorQueue | A physical-factor coverage state, available *before* asking for a label, causes better error on factor cells withheld from training than ordinary online active learning. | The factor must be observable at queue time, and there must be a defensible relation from factor coverage to semantic labels in cells that have no labels yet. |
| UPM-EdgeBound | A distribution-free impossibility/boundary over the trace \(O=(x,f(x),r)\), plus a minimal witness that restores identification. | The boundary must be narrower or practically stronger than known unlabeled target-accuracy impossibility results; the added witness must be both identified and not a renamed existing shift assumption or delayed-label controller. |

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| AL-FactorQueue: component | Pavan, Galimberti, Roveri's TActiLE takes an irreversible on-device stream, makes an online keep/discard decision for a bounded batch, requests oracle labels, retrains, and compares random, uncertainty/informativeness, diversity, and preemption.  HALO also combines active selection with domain shift. | TActiLE does not expose a declared physical-factor metadata field or report the proposed factorial hold-out. | High collision; the metadata field alone is not a new action. |
| AL-FactorQueue: exact claim | The principal action/constraint/endpoint, ``which arriving samples get a scarce label to improve a later model under edge memory/latency,'' directly overlaps TActiLE.  If factor IDs are known before selection, selecting quota per ID is ordinary stratified/coverage sampling, an explicit simple baseline rather than an adaptive-sensing mechanism. | A narrowly specified, independently measured factor may create a different *experimental protocol*.  No primary source in this pass establishes that it creates a distinct active-learning guarantee. | High that the proposed FYP claim is not yet distinct; residual protocol claim is [GAP]. |
| AL-FactorQueue: boundary | For any policy that observes only \((x,f(x),z)\), where \(z\) is the pre-action factor, two worlds can have the same distribution of those observables and opposite labels on a held-out factor cell.  Thus factor coverage alone cannot guarantee lower unseen-cell error without a structural assumption relating \(z\) to \(p(y\mid x,z)\).  A truly unseen factor *combination* has no label evidence for its interaction. | A pre-registered causal/invariance model and labels on sufficient factor combinations could make a scoped empirical design possible, but then it is no longer distribution-free and must be independently audited. | High for the counterexample; exact useful assumption remains [GAP]. |
| UPM-EdgeBound: component | Garg et al. formalize target accuracy estimation from unlabeled data and give possibility/impossibility results.  Nguyen et al. formalize label-free deployment failure monitoring; Chen, Zaharia, Zou identify a restricted joint-shift model. | Adding ordinary resource telemetry to the trace is not an independent semantic label witness. | High. |
| UPM-EdgeBound: exact claim | The candidate's central sentence is exactly an unrestricted unlabeled target-risk non-identifiability statement.  Garg et al.'s Sec. 3 already supplies this mathematical boundary for arbitrary target conditional shift.  The specified \(f(x)\) is a deterministic function of the already-observed \(x\), and telemetry may be held identical in the counterexample. | A theorem that is genuinely about a *specified physical* witness, a restricted shift family, and a new operational decision could differ.  No such witness/family is defined here. | High collision for the proposed statement; residual is [GAP]. |
| UPM-EdgeBound: boundary | Let a deterministic binary classifier see one repeated input \(x_0\), emit \(f(x_0)=0\), and have fixed telemetry \(r_0\).  In environment \(E_0\), set \(Y=0\); in \(E_1\), set \(Y=1\).  Both induce the same law of \((X,f(X),R)\), but risks are 0 and 1.  Any trace-only policy has the same output law in both, so no non-vacuous distribution-free upper bound or `continue` certificate is valid in both.  This is a direct instantiation, not a new theorem. | Delayed labels, an independent reference, or a stated label-/joint-shift model breaks the premise, but each changes the candidate and is already an established problem family. | High. |

## Assumption and identification audit

### AL-FactorQueue

The phrase **physical-factor witness** splits into two mutually exclusive cases.

1. **It is known before the label request** (e.g., the bench controller itself set illumination, distance, token print, or load).  Then factor membership is ordinary pre-label metadata.  The cheapest honest policy is a fixed quota/round-robin stratified sampler across factor cells, optionally followed by random selection within each stratum.  A learned score has no information advantage merely from receiving the same metadata.  It can only win empirically under extra assumptions about class/factor interaction, and must beat this quota policy and TActiLE at equal labels, queue capacity, retained bytes, and decision time.
2. **It is not known before the request** (e.g., the alleged physical condition has to be inspected by the technician to determine it).  It cannot be the queue's selection input.  Using it after human review to select or stratify is target leakage, not an online edge policy.

Even in case 1, an ``unseen factor cell'' creates a support problem.  Choose a cell \(z^*\) that is never labelled during selection.  Holding the observable stream and all labels outside \(z^*\) fixed, define one valid world with \(Y=f(X)\) on \(z^*\), and another with \(Y\ne f(X)\) there.  The selector's observations and selected set are identical, but the held-out error reverses.  Therefore coverage metadata does not identify the claimed improvement.  This is the same conditional-shift obstruction that blocks UPM; it is not repaired by calling a controlled nuisance variable a sensor witness.

### UPM-EdgeBound

The formal counterexample above also handles telemetry: choose the same (or a constant) resource-trace distribution in both worlds.  Since \(f(X)\) is computed from \(X\), observing logits or predictions cannot distinguish the worlds either.  Requesting review is a legitimate action, but it produces labels *after* the no-label decision and hence cannot justify a prior valid `continue` guarantee for the unrestricted class.

The possible ``minimal witness'' additions are already recognizable assumption families:

- delayed sampled labels: budgeted active learning/risk monitoring;
- label-shift or sparse-joint-shift restrictions: target-risk identification under a named statistical model;
- independent calibrated physical reference: reference sensing/calibration;
- second predictor disagreement: label-free failure monitoring under its stated disagreement assumptions.

Merely listing them is useful design hygiene, but it is not a new boundary contribution.  A survivor would need one fixed physical observation model and a proof that a clearly weaker/smaller witness is insufficient while the proposed one is sufficient.  No such pair is supplied.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Pavan, Galimberti, Roveri, **TActiLE: Tiny Active LEarning for wearable devices**, arXiv:2505.01160v1, 2025-05-02, [HTML/PDF](https://arxiv.org/html/2505.01160v1) | Unlabelled on-device stream; online retain/discard; finite batch sent to an oracle; retrain. | Test accuracy after retraining; per-sample selection time and memory; random and streaming baselines. | AL-FactorQueue's stream, finite queue, label action, local constraint, and model-improvement endpoint. | [KILL] Its Sec. II (PDF pp. 2-3) gives the online irrevocable selection formulation; Secs. IV-VII (pp. 3-8) give batch handling, random/preemption/uncertainty/diversity controls, accuracy, time and memory.  Factor IDs are only metadata/stratification unless they change the observation/action. |
| Franco et al., **Hyperbolic Active Learning for Semantic Segmentation under Domain Shift**, ICML 2024, PMLR 235:13864-13884, [official record/PDF](https://proceedings.mlr.press/v235/franco24a.html) | Select scarce labels under source-to-target domain shift. | Target-domain segmentation performance with limited labels. | Component collision with ``use selected labels to improve held-out shifted factor performance.'' | [KILL] as a generic domain-shift active-learning claim; it does not make the TinyML queue exact, nor does it validate factorial metadata as a new mechanism. |
| Garg et al., **Leveraging Unlabeled Data to Predict Accuracy**, NeurIPS 2022, [OpenReview PDF](https://openreview.net/pdf?id=wcrff7Gh0RR) | Unlabeled target inputs and a fixed model; estimate target accuracy. | Possibility/impossibility of target-accuracy estimation. | UPM's frozen model plus unlabeled observation target. | [KILL] Sec. 3, PDF pp. 4-5: arbitrary changes in target \(p(y\mid x)\) make target accuracy unidentifiable without further assumptions.  The proposed telemetry is held fixed by the simple two-world construction. |
| Nguyen et al., **Reliably Detecting Model Failures in Deployment Without Labels**, NeurIPS 2025, [official record](https://papers.nips.cc/paper_files/paper/2025/hash/0bb251eba663f0345c0929f5bbbfb6dc-Abstract-Conference.html) | Predictions of multiple models on unlabeled deployment data; alert on deterioration. | Failure-detection false-positive/sample-complexity guarantees under its disagreement assumptions. | Direct neighbor to any positive UPM label-free alarm/continue policy. | [KILL] of a generic label-free monitor.  Full-paper exact page extraction was unavailable in this pass, so the scope of each guarantee is [GAP], not used as the sole boundary evidence. |
| Chen, Zaharia, Zou, **Is Unsupervised Performance Estimation Impossible When Both Covariates and Labels Shift?**, NeurIPS 2022 DistShift Workshop, 2023-05-05 OpenReview version, [official page](https://openreview.net/forum?id=X1ZFG__-jo) | Restricted Sparse Joint Shift model; unlabeled target data plus stated structure. | Identifiable performance estimation under the restriction. | Candidate's proposed ``minimal added assumption restores identification.'' | [KILL] of presenting an unspecified added assumption as a new solution.  Abstract/Sec. 1, PDF pp. 1-3 distinguishes restricted identification from the unrestricted case; exact minimality relative to a chosen physical witness is unverified. |

## Strongest simple baseline

**AL-FactorQueue:** fixed factorial quota: allocate the check budget uniformly (or by a preregistered Neyman-style allocation when a pilot variance is honestly available) over the factor IDs that are observable before review, then choose randomly within each cell.  It uses less compute/memory than embeddings/diversity and directly enforces the claimed coverage.  Essential equal-cost baselines are: random, uncertainty, diversity, TActiLE Dual-RV, fixed factor quota, and factor quota + uncertainty within each stratum.  If quota matches the result, the claimed factor mechanism vanishes.

**UPM-EdgeBound:** constant `suspend` is the only distribution-free safe policy, and a constant \([0,1]\) risk interval is the only universally valid bound.  The two-world trace counterexample shows why.  Under a stated restricted model, compare a fixed periodic delayed-label audit and the corresponding published shift estimator before inventing a new policy.

## Contrarian result

- **AL-FactorQueue: KILL as stated.** It is a TinyML stream active-learning application with a controlled experimental covariate.  If the covariate is available before label request, a transparent stratified sampler is the decisive baseline; if not, it cannot be an action input.  The promised held-out unseen-cell improvement is non-identifiable without an additional causal/invariance assumption.  Turning the FYP into an honest factorial dataset/protocol can be a useful appendix, but does not meet the requested distinct research-mechanism gate.
- **UPM-EdgeBound: KILL as stated.** Its desired impossibility proof is already a direct instance of known unlabeled target-accuracy non-identifiability.  Adding normal telemetry does not change the construction.  A new, scoped witness-minimality theorem is conceivable but wholly unspecified; until it names a physical witness and restricted family, it is not a candidate and must not be called innovative.

## Feasibility audit

| Issue | AL-FactorQueue | UPM-EdgeBound |
| --- | --- | --- |
| Hardware/data/ethics | A camera, printed non-personal targets, and manual review are cheap and permitted.  But objective printed-token classes also invite a deterministic template/QR baseline that may erase the learning story.  Factor labels chosen by the experimenter are metadata, not independent sensing. | A synthetic or printed bench can demonstrate the indistinguishable-pair construction cheaply, with no ethics issue.  It cannot empirically establish a distribution-free theorem, and a physical data set cannot prove a unique ``minimal witness.'' |
| Evaluation validity | Must split by complete factor cells *before* selection, use repeated independent collection days, lock factor labels before review, and budget all storage/label/latency.  With few factorial cells, results will be dominated by which cells are withheld. | Must explicitly state the shift family.  Physical process changes will introduce unmeasured nuisance variables, so a negative empirical result cannot establish the claimed universal boundary. |
| One-year FYP value | A demo by 2026-12 is feasible, but the research question collapses to an active-learning benchmark unless a new observable/action is supplied. | The theorem/demo is feasible, but the theorem is already known; enough additional theory to prove a new minimal witness is high risk for the remaining schedule. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| TinyML stream AL makes online irrevocable batch-selection decisions and evaluates post-retraining accuracy, time, and memory against random/preemption controls. | [KILL] | Pavan, Galimberti, Roveri, [TActiLE](https://arxiv.org/html/2505.01160v1), arXiv:2505.01160v1, 2025-05-02. | Abstract/PDF p. 1; Sec. II, PDF pp. 2-3; Sec. IV, pp. 3-4; Sec. V, pp. 4-5; Sec. VI-C, p. 5; Secs. VII-A-C, pp. 6-8. | It uses image benchmarks and estimates Nicla Vision timing (Sec. VII-B), not the proposed tabletop bench.  That does not by itself create an action-level distinction. |
| TActiLE's evaluated selection methods include random, preemption, informativeness, and hybrid informativeness/diversity. | [KILL] | Same [TActiLE v1](https://arxiv.org/html/2505.01160v1). | Sec. VI-A, PDF pp. 5-6; Sec. VII-A, pp. 6-7; HTML lines 274-280. | Factor-stratified quota is not its reported baseline; it is required here precisely because the new candidate exposes factor IDs. |
| Limited-label active learning under domain shift is an established method family. | [K] | Franco et al., [official ICML 2024 record](https://proceedings.mlr.press/v235/franco24a.html), PMLR 235:13864-13884. | Abstract and paper pp. 13864-13865 (problem/contribution); detailed exact overlap to a finite TinyML queue is not claimed. | Component-collision evidence only. |
| Arbitrary target conditional shift makes target accuracy unidentifiable from unlabeled target data without identifying assumptions. | [KILL] | Garg et al., [OpenReview PDF](https://openreview.net/pdf?id=wcrff7Gh0RR), NeurIPS 2022. | Sec. 3, ``Accuracy Estimation: Possibility and Impossibility Results,'' PDF pp. 4-5. | Applies to UPM's unrestricted positive certificate.  The audit's constant-telemetry construction extends the observable trace but does not assert a new theorem. |
| A restricted joint-shift model can restore unsupervised performance identification only under stated structural assumptions. | [K] | Chen, Zaharia, Zou, [OpenReview version](https://openreview.net/forum?id=X1ZFG__-jo), NeurIPS 2022 DistShift Workshop, last modified 2023-05-05. | Abstract and Sec. 1, PDF pp. 1-3. | Used to show that ``add an assumption'' is an existing family; no claim about a particular hardware witness. |
| Label-free model-failure detection using model disagreement is a current direct-neighbor family. | [K] | Nguyen et al., [NeurIPS 2025 official record](https://papers.nips.cc/paper_files/paper/2025/hash/0bb251eba663f0345c0929f5bbbfb6dc-Abstract-Conference.html), 2025. | Official abstract; full paper Secs. 1-3/page numbers [GAP: retrieval not verified in this pass]. | Not load-bearing for the impossibility result; must be full-text checked before any later positive monitor claim. |

## Queries and failed searches

Queries executed/reviewed on 2026-08-31:

- `site:arxiv.org "active learning" "domain generalization" 2024 2025 physical factors`
- `site:proceedings.mlr.press active learning domain generalization 2024 2025`
- `"TActiLE" "Task-Agnostic" Active Learning Edge 2025`
- `"factor-aware" active learning domain generalization samples factor labels paper`
- `"active learning" "unseen factor" generalization`
- `"stratified sampling" active learning known domain labels domain generalization`
- `site:openreview.net unlabeled target accuracy impossibility conditional shift target risk identification`
- `"unlabeled data" "accuracy estimation" impossibility Garg NeurIPS 2022`

Failed/uncertain results:

- No inspected primary paper in this pass establishes the *exact* physical-factor queue formulation with the same finite benchtop setup.  This is [GAP], not evidence of novelty, and does not overcome the action-level TActiLE collision or factor-label leakage dichotomy.
- No primary source was found here proving that a particular low-cost physical factor is the unique/minimal witness for UPM.  This is [GAP]; it is the essential missing result, not a license to promote UPM.
- The full PDF/page-level details for Nguyen et al. (2025) were not verified during this pass.  The audit does not rely on them for its KILL decision.

## Decision

**KILL.** AL-FactorQueue is an active-learning/stratified-sampling application unless it gains a genuinely independent pre-action observable and a separately auditable structural guarantee; its present unseen-cell claim is not identified.  UPM-EdgeBound restates the established no-assumption unlabeled target-risk impossibility, and its ``minimal witness'' extension is undefined and directly adjacent to existing restricted-shift and delayed-label families.  Neither is eligible for promotion or thesis lock in this form.
