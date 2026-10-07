# Validation Audit: 2026-09-24 STAGE-RISK

## Decision investigated

This audit tests `STAGE-RISK`, a proposed edge Palm Payment direction in which a Pi records capture, ROI, identification/open-set, unknown-threshold and mock-action stages, estimates a per-stage risk, and combines the stages to predict or control end-to-end transaction risk.

The charitable version of the proposal is:

> Given a live palm transaction, can an edge device use stage-wise evidence to decide `commit / retry / unknown / refuse`, or produce a calibrated end-to-end risk certificate, with lower wrong-action risk or lower completion cost than fixed thresholds and direct episode-level measurement?

The current route and constraints were checked before this audit: the user-confirmed project is a consented Pi 5 visible-light capture, live ROI, identifier-free open-set 1:N and idempotent simulated-account transaction by December 2026. It is not a production payment or payment-grade security claim. This packet writes only to `research/ops/validation/`; it does not modify `research/active/`, `research/archive/`, or `.research/`.

## Claim under test

### Strong positive claim [C]

For a fixed Palm Payment pipeline, stage-specific risks from capture, ROI, matcher/open-set decision and action can be calibrated and composed into a useful transaction-risk estimate or online policy. The method would supposedly identify which stage caused risk and improve the `wrong action / correct completion / unknown / time` frontier over fixed unknown threshold, fixed recapture, direct end-to-end empirical frequency, independent stage multiplication, and ordinary stage-stratified logistic or isotonic calibration.

### Weaker evaluation claim [C]

An all-start stage trace may reveal that marginal FAR/FRR/FTE/FTX values or component timings are misleading for a full transaction because stage reachability, retry policy, gallery membership and person/session dependence alter the final action outcome.

The weaker claim is a useful audit only. It is not a new risk estimator unless a new observation, action, guarantee or identifiable theorem survives the baselines below.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | **[KILL]** ISO/IEC 19795-1:2021 already defines biometric performance evaluation around comparisons, transactions, failure-to-enrol/acquire and operating conditions; ISO/IEC 19795-10:2024 requires factor controls, uncertainty, threshold reporting and disclosure when a differential cannot be uniquely attributed. NIST IR 7544 covers biometric quality and acquisition/enrolment error suppression. Palm-ID already combines mobile palm acquisition, ROI, quality rejection/recapture, open-set 1:N and component timing. | The exact local stage labels `capture -> ROI -> 1:N -> unknown -> mock debit` are apparatus-specific. That is a useful logging schema and an evaluation protocol, not an unoccupied mechanism. | High for a new method; high for a logging wrapper. |
| Exact-claim collision | **[KILL-leaning]** End-to-end biometric evaluation, sequential accept/reject/continue, quality-aware recapture and transaction error reporting already cover the proposed inputs and actions. Reliability block diagrams cover series-stage composition under explicit independence; selective prediction covers abstain/risk-coverage decisions; calibration papers cover logistic/temperature/isotonic probability calibration. Replacing “system failure” with “mock debit” changes the endpoint but does not create a method. | **[GAP]** No inspected source was verified to use the exact Pi 5 palm executable, identifier-free open-set 1:N, frozen unknown threshold and idempotent mock debit in one published experiment. This is a local measurement gap, not evidence of novelty. | High that the generic claim is occupied; medium that the exact local endpoint is unpublished. |
| Boundary and impossibility | **[KILL]** If only marginal stage rates are observed, the joint transaction outcome is not identified. Even with two stages having pass probabilities 0.9 and 0.9, perfect positive dependence gives joint pass 0.9 while conditional independence gives 0.81; both match the same marginals. Retries and policy selection create further dependence. If every eligible start and every transition are logged, the direct episode outcome is identifiable by empirical frequency, making a new composition rule unnecessary unless it improves a predeclared held-out action-cost frontier. | A theorem/negative result could remain: state the minimum trace required to identify end-to-end risk and show the failure of multiplying heterogeneous metrics. This is a protocol boundary or null result, not a positive stage-risk method. | High for non-identifiability from marginals; medium-high for a bounded empirical audit. |

## Assumption and identification audit

### 1. Stage multiplication is not generally valid

Let an eligible transaction episode have stage indicators `C` (capture succeeds), `R` (valid ROI), `I` (acceptable identity/unknown decision) and `A` (action is safe/correct). The final correct-action probability is:

```text
P(C and R and I and A)
= P(C) P(R | C) P(I | C,R) P(A | C,R,I),
```

not `P(C)P(R)P(I)P(A)` unless the required conditional structure and denominators are actually established. FAR, FRR, FTE and FTX normally use different trial populations and conditioning events; multiplying them mixes denominators and can count a stage that was never reached. Latency is not a probability and cannot be multiplied into transaction risk.

The independent series product is a valid baseline only for a declared series model whose component events are independent or conditionally independent under the same episode population. It is a comparison, not a contribution.

### 2. Marginal stage metrics do not identify dependence

With `P(C)=P(R)=0.9`, two admissible joint distributions include:

- positively coupled stages: `P(C=1,R=1)=0.9`;
- independent stages: `P(C=1,R=1)=0.81`.

The same marginal stage reports therefore support different end-to-end completion rates. In a real pipeline, `R` is only observed after `C`, and `I` is only observed after both; the missing counterfactual branches are not recovered by a dashboard or by a calibrated score.

### 3. What an all-start trace can identify

If every eligible physical start is retained in the denominator and the trace records stage entry, stage outcome, retry count, threshold/version, gallery/account binding, final action and time, then the episode-level quantities are directly estimable:

```text
P(correct mock action | eligible start)
P(wrong identity/action | eligible start)
P(unknown or refusal | eligible start)
P(no completion | eligible start)
```

Conditional stage rates are also estimable for the reached population. This is already the direct empirical baseline. It does not identify a causal “stage responsible” explanation unless the stage interventions or an independently assigned factor are available. A failed transaction can have capture, ROI and matcher causes that are observationally confounded.

### 4. Calibration does not solve missing labels or selection

Stage-stratified logistic/isotonic calibration can map a score or feature vector to observed risk on a calibration split. It requires outcome labels, no leakage from the final test episodes, stable definition of the target event and enough independent person/session clusters. It does not recover wrong-action risk for never-reached stages, unobserved impostors or unlogged retry paths. Selective prediction can trade coverage for risk, but the abstain action and risk-coverage curve are established objects; the local labels `unknown / retry / refuse` do not make them new.

### 5. Causal attribution is a separate claim

The trace can say where the pipeline stopped. It cannot by itself say what would have happened if the camera exposure, hand placement, ROI model, threshold or gallery had been changed. A one-factor intervention or randomized prompt is required for that counterfactual. Without it, “stage-risk attribution” is post-hoc categorization, not diagnosis.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| ISO/IEC 19795-1:2021, *Biometric performance testing and reporting -- Part 1: Principles and framework*, official preview, https://www.iso.org/standard/73515.html | Biometric comparison/transaction protocols, mated/non-mated trials, failure-to-enrol/acquire and operating conditions | Error rates, throughput, uncertainty, protocol and reporting; definitions in the official preview, Sections 6.4--6.5 and 7--8 | **High** for “stage metrics plus transaction endpoint” as a new evaluation idea | Kills generic evaluation novelty. Leaves a local apparatus-specific audit if the protocol is explicitly scoped and honestly reported. |
| ISO/IEC 19795-10:2024, Edition 1 (published 2024-10), https://www.iso.org/standard/81223.html and accessible catalogue copy https://standards.iteh.ai/catalog/standards/iso/c393f7c4-f721-4602-a96f-f84b35e020f9/iso-iec-19795-10-2024 | Predeclared factors, controls, ground truth, thresholds, uncertainty and factor/group variation | Differential biometric performance and limits on attribution; Clauses 5.1, 5.2.4 and 6.3, pp. 4--5, 8--9 in the accessible copy | **High** for a risk certificate that claims to identify capture/ROI/device causes without controlled factors | Kills causal/attribution wrapper. Leaves an explicit insufficiency/negative result. |
| Tabassi & Grother, *Biometric Quality: The last 1%*, NIST IR 7544, 2008-11, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Acquisition quality, quality assessment and error suppression | Failure-to-acquire/enrol and quality intervention; Sections 2.1.1--2.1.3 and 4--6 | **High** for quality-to-recapture stage logic | Kills “quality stage is new”; leaves local capture-path characterization. |
| Grosz, Godbole & Jain, *Palm-ID*, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Mobile palm images, ROI, quality filtering/recapture, embedding search and open-set 1:N | FNIR/FPIR, rank, quality and component timing; Sections II-F/G, III-B--D, IV-A/B and V | **High** for the core capture/ROI/recognition cascade | Kills a new palm stage pipeline. The Pi full transaction remains a finite local endpoint only. |
| Murakami & Takahashi, *Sequential Biometric Authentication Using Multiple Samples*, IEEE WIFS 2009, DOI https://doi.org/10.1109/WIFS.2009.5386482 | Sequential scores and accept/reject/continue behavior, including non-enrollee/open-set handling | Sequential decision performance; Sections 2--4 | **High** for retry/continue/unknown policy | Kills a new sequential stage policy. Leaves a bounded user/interface evaluation. |
| Reliability block diagram series model, IEC 61078:2016 catalogue record, https://www.iso.org/standard/61196.html | Series/parallel component success/failure composition with declared structure and assumptions | System reliability from component reliabilities | **Medium-high** for independent stage multiplication | Kills product-of-stage-rates as a contribution. Leaves a counterexample showing why its assumptions fail for biometric episodes. |
| Guo et al., *On Calibration of Modern Neural Networks*, ICML 2017, PMLR v70, https://proceedings.mlr.press/v70/guo17a.html | Scores/probabilities and calibration methods, especially temperature scaling | Expected calibration error, reliability diagrams and held-out calibration | **High** for score-to-risk calibration | Kills generic calibration novelty. Leaves only a local calibration audit with sufficient independent labels. |
| Zadrozny & Elkan, *Transforming classifier scores into accurate multiclass probability estimates*, KDD 2002, DOI https://doi.org/10.1145/775047.775151; Niculescu-Mizil & Caruana, JMLR 2005, https://www.jmlr.org/papers/volume5/niculescu-mizil04a/niculescu-mizil04a.pdf | Classifier scores and held-out logistic/isotonic probability mapping | Brier/log loss and calibration quality | **High** for proposed logistic/isotonic stage calibration baseline | Kills calibration as a new method; leaves a finite comparison of calibration error and action risk. |
| Geifman & El-Yaniv, *Selective Classification for Deep Neural Networks*, arXiv:1705.08500v2 (2017), https://arxiv.org/abs/1705.08500 | Prediction plus abstention/coverage control | Risk-coverage trade-off and selective error | **High** for `commit / unknown / abstain` as a generic action family | Kills generic selective-prediction novelty. Leaves only the local full-transaction endpoint and cost accounting. |

## Strongest simple baseline

The strongest baseline is not a single product formula. It is a locked comparison matrix:

1. **Direct episode frequency:** include every eligible start; compute final correct action, wrong action, unknown/refusal, no completion and p95/p99 time directly, with person- and session-clustered uncertainty.
2. **Independent series product:** multiply stage conditional pass rates only when the same denominator and declared independence assumption are used; report it as a misspecified comparison when the direct trace disagrees.
3. **Stage-stratified logistic calibration:** fit on a training/calibration split using stage scores, quality, retry count and declared metadata; test on person/session-held-out episodes.
4. **Isotonic calibration:** fit the same target with monotone calibration; reject it if calibration data are too sparse or if it overfits identities/sessions.
5. **Fixed unknown threshold:** freeze the threshold before the test set; use fixed one-retake/quality rejection and conservative refusal controls.
6. **Always-continue / always-refuse controls:** include these to expose whether a claimed policy merely changes coverage without improving the action-risk frontier.

If a proposed STAGE-RISK estimator or controller cannot beat the direct empirical frequency plus fixed-threshold controls at matched completion, retry and compute cost, it has no remaining positive claim.

## Contrarian result

### Strong negative result that survives

`STAGE-RISK` can leave a useful theorem boundary, but only in this restricted form:

> **Marginal stage metrics do not identify end-to-end transaction risk under unknown dependence, retries or selective reachability. End-to-end risk becomes identifiable from an all-start episode trace, but stage causal attribution still requires an intervention or independent witness.**

This result is falsifiable with a synthetic counterexample and a real trace. It tells the project when not to multiply FAR/FRR/FTE/FTX or report a risk certificate. It does not justify a new estimator, a new calibration algorithm, or a thesis claim that stage logging itself is novel.

### What would be needed to avoid KILL

Only a materially different claim could reopen it: for example, a formally specified observation model with a nontrivial guarantee under dependence/selection, or a pre-registered intervention that changes action risk and beats the direct trace and all simple baselines at equal cost. No such theorem, intervention or independent witness is currently supplied.

## Feasibility audit

### Data and denominators

- **[GAP]** The current workspace contains an unresolved same-hand rejection and informal `FR 66`, but not a verified denominator, frozen threshold, per-stage counts or a complete all-start transaction trace.
- A bona fide-only sample can estimate capture/ROI completion and enrolled-user false reject behavior, but cannot estimate false accept, wrong identity or wrong mock debit without independently assigned mate-absent/impostor starts.
- Repeating frames from one person/session does not create independent transaction episodes. Confidence intervals must cluster by person and session; a small convenience cohort gives unstable unknown/wrong-action estimates.
- Calibration requires held-out people/sessions. Reusing the same episodes to choose the unknown threshold, fit isotonic/logistic calibration and report action risk is leakage.

### Repeated unknown and attack samples

- **[KILL-leaning]** A positive wrong-action or false-retain claim needs repeated, authorized mate-absent/unknown and, if claimed, presentation-attack episodes that reach the real capture and ROI path. One or two accidental unknowns cannot support a threshold or rare-event risk estimate.
- Physical attacks are outside the current Phase 1 commitment and require consent, safety review, material lineage and an explicit threat model. A simulated account debit is not evidence of payment security.
- If no lawful unknown/attack roster is available, the project must report a bounded no-attack/open-set feasibility result, not infer a safe stage risk.

### Hardware, time and implementation

- The Pi 5/VIS executable can log timestamps, stage outcomes, threshold/version and final mock action. That is feasible engineering instrumentation.
- It is not yet demonstrated that every physical start can be captured, timestamped and retained without selection by the current UI; this must be tested before an all-start denominator is claimed.
- By the December 2026 demo deadline, implementing and validating stage logging is feasible. A powered study of rare wrong-action risk, calibration stability, cross-session dependence and attack behavior is not established.
- No new sensor, attack material, payment infrastructure or risk-control hardware is justified by this candidate before the MVP trace exists.

### Ethics and privacy

- Palm images/templates and repeat visits require explicit consent, access control, retention/deletion rules and a clear separation between engineering identifiers and the identifier-free evaluation output.
- Any unknown/impostor or physical-presentation experiment needs participant safety, authorization and data-lineage decisions before collection. The mock-debit endpoint must remain visibly simulated.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Biometric transaction evaluation must separate protocol, failure and uncertainty rather than report one informal accuracy number. | [K] | ISO/IEC 19795-1:2021, https://www.iso.org/standard/73515.html | Official preview; definitions and Sections 6.4--6.5, 7--8 | Official full text is partly paywalled; only preview/scope is used. |
| Factor controls and uncertainty are required before attributing a performance difference to a factor. | [K] | ISO/IEC 19795-10:2024, https://www.iso.org/standard/81223.html; accessible catalogue copy above | Clauses 5.1, 5.2.4 and 6.3, pp. 4--5, 8--9 | Part 10 targets variation across demographic groups; the attribution boundary is used by analogy, not as a claim that it solves device causality. |
| Acquisition quality and recapture are established biometric controls. | [K] | NIST IR 7544, 2008-11, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Sections 2.1.1--2.1.3 and 4--6 | General quality guidance, not a Palm Payment paper. |
| Mobile palm ROI, quality and open-set recognition are already combined in a published pipeline. | [K] | Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Sections II-F/G, III-B--D, IV-A/B and V | Different hardware and transaction endpoint. |
| Sequential accept/reject/continue is an existing biometric decision family. | [K] | Murakami & Takahashi, IEEE WIFS 2009, https://doi.org/10.1109/WIFS.2009.5386482 | Sections 2--4 | Full text was read in the 2026-09-23 validation chain; not re-read in this turn. |
| Series composition requires a structural model and assumptions; multiplication is not automatic. | [K] | IEC 61078:2016, official catalogue, https://www.iso.org/standard/61196.html | Series/parallel reliability-block definitions and system-reliability clauses in the catalogue/standard record | The biometric dependence counterexample is derived here; IEC is not a biometric source. |
| Calibration methods such as temperature scaling and reliability diagrams are established. | [K] | Guo et al., ICML 2017, PMLR v70, https://proceedings.mlr.press/v70/guo17a.html | Sections 1--3 and experimental calibration sections | Neural-network setting; the collision is methodological. |
| Logistic/isotonic probability calibration is established. | [K] | Zadrozny & Elkan, KDD 2002, https://doi.org/10.1145/775047.775151; Niculescu-Mizil & Caruana, JMLR 2005, https://www.jmlr.org/papers/volume5/niculescu-mizil04a/niculescu-mizil04a.pdf | Calibration-method sections and experiments | Generic classifier calibration, not biometric-specific. |
| Abstention and risk-coverage are established selective-prediction targets. | [K] | Geifman & El-Yaniv, arXiv:1705.08500v2, 2017, https://arxiv.org/abs/1705.08500 | Sections 1--4 | A local unknown action is an application endpoint, not a new selective classifier. |
| The exact Pi 5 full-path transaction and all-start denominator are available. | [GAP] | Current charter/register and `minutes/09-13-palm-payment-roadmap-update.md`, local workspace | Current route and candidate rows; no verified completed all-start trace supplied | Must be measured, not inferred from the project plan. |

## Queries and failed searches

Queries run or rechecked on 2026-09-24:

- `ISO/IEC 19795-1 biometric performance testing reporting transaction failure to acquire`
- `ISO/IEC 19795-10:2024 biometric performance variation factor controls uncertainty attribution`
- `biometric end-to-end transaction evaluation capture recognition action failure`
- `biometric stage-wise risk FAR FRR FTE FTX product independent stages`
- `reliability block diagram series system product independent component reliability`
- `biometric selective prediction abstention risk coverage calibration`
- `isotonic logistic calibration biometric score risk held-out`
- `Palm-ID mobile palm ROI quality recapture open-set 1:N`
- `sequential open-set biometric accept reject continue transaction`

Failed or insufficient searches:

- No inspected primary source used the literal name `STAGE-RISK` for the exact Pi 5 palm/mock-debit setup.
- No source was verified to publish the exact combination of capture, live ROI, identifier-free open-set 1:N, frozen unknown threshold and idempotent mock debit on this local executable.
- This absence is a retrieval gap and local evaluation opportunity, not evidence that the generic method is novel.
- The full paid normative text of ISO/IEC 19795-1 and 19795-10 was not freely inspectable in this round; claims are limited to the official preview and accessible clause copy already used in prior workspace audits.

## Unresolved uncertainties

1. Whether the current Palm Payment executable can retain every eligible physical start, including starts that fail before a frame is saved.
2. The frozen matcher, gallery, unknown rule, retry policy and exact action-binding semantics.
3. The number of independent people, sessions and authorized mate-absent/unknown episodes available before the December 2026 demo.
4. Whether any future “stage attribution” claim will include randomized or counterbalanced interventions rather than observational logs.
5. Whether a later dataset can support person/session-held-out calibration; frame-level bootstrap is not sufficient evidence.

## Decision

`STAGE-RISK` is **KILL as a positive thesis method**. Its named components are occupied by biometric performance standards, transaction/error reporting, reliability composition, selective prediction, calibration and ordinary stage logging. The exact Pi endpoint is a feasible engineering/evaluation artifact, but changing the endpoint to a simulated mock debit does not establish a new CS contribution.

The only valuable surviving boundary is **PIVOT as a bounded negative-result audit**:

- demonstrate with a two-stage counterexample that marginal FAR/FRR/FTE/FTX-style rates cannot determine joint transaction risk without dependence and reachability assumptions;
- collect an all-start episode trace to estimate direct end-to-end outcomes;
- compare independent multiplication, direct empirical frequency, stage-stratified logistic/isotonic calibration and fixed unknown/recapture/refusal controls;
- report whether stage attribution remains unidentified without intervention.

Do not call the trace, dashboard, calibration wrapper or stage product a novel risk method. Do not collect repeated unknown/attack samples solely for this candidate before the MVP, consent and threat-model gates are satisfied.

PIVOT
