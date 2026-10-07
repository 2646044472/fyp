# Divergence Packet: 2026-09-24 STAGE-RISK

## Decision investigated

`STAGE-RISK` asks whether, in a frozen edge palm transaction pipeline,

```text
capture -> ROI -> quality -> matcher -> unknown policy -> action
```

stage dependence makes an independent product of stage rates, or a single matcher FAR/FRR, a poor predictor of end-to-end wrong-action, completion, or p95 time. The proposed residual is a stage-conditioned risk estimator or minimal calibration protocol evaluated at equal capture opportunity and retake budget.

This packet is deliberately narrow. JSONL logging, a dashboard, ordinary reliability reporting, a new matcher, and a new biometric dataset are not contributions.

**Decision:** `HOLD/PIVOT`. ISO/IEC 19795 and transaction-level biometric metrics occupy the measurement vocabulary and much of the evaluation problem. One bounded residual remains: an empirical identifiability/dependence audit on the actual frozen edge action pipeline, with a predeclared estimator and a negative-result path. It must not be framed as a new reliability theory or calibration algorithm.

## Search boundary

### Required local reading

Read: `AGENTS.md`; `research/active/README.md`; `00-project-charter.md`; `01-candidate-register.md`; `39-round-24-cross-mechanism-reconciliation.md`; `40-round-25-targeted-reconciliation.md`; `36-palm-failure-localization-gate.md`; `37-palm-residual-direction-gate.md`; `38-direction-convergence-gate.md`; and the overlapping archive files `core/08-counterevidence-and-boundaries.md`, `core/17-research-direction-index.md`, `core/18-tta-without-ground-truth-state.md`, `log/39-problem-driven-second-audit.md`, `log/42-sensor-state-action-audit.md`, `log/43-common-cause-fusion-novelty-audit.md`, `log/44-edge-native-risk-audited-cascade.md`, and `log/45-adaptive-sensing-expansion-validation.md`.

### External search boundary

Primary/official searches covered biometric standards and operational metrics, transaction/multiple-attempt performance, operational biometric failures, compositional pipeline reliability, selective prediction, conformal risk control, and sequential biometric decisions. Searches included:

- `NIST biometric performance testing false accept false reject ISO 19795 operational transaction`
- `compositional reliability machine learning pipeline stage conditional risk`
- `end-to-end biometric transaction capture recognition action evaluation`
- `biometric failure to acquire operational transaction performance`
- `selective prediction risk coverage calibration abstention primary paper`
- `Czajka Bowyer 2015 biometric multiple attempts`
- `Murakami Takahashi 2009 sequential open set biometric`
- `NISTIR 8564 Project Clearprint transaction anomalies`

This is a bounded source audit through 2026-09-24, not a global novelty search.

## Is STAGE-RISK already occupied?

### ISO/IEC 19795: largely yes at the metric/protocol layer

[K] ISO/IEC 19795-1 defines biometric performance testing and distinguishes technology, scenario and operational evaluations. Its scope and definitions separate quantities such as false match/non-match, failure to acquire/enrol and throughput. The official ISO Online Browsing Platform page inspected was the current DIS record:

https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:19795:-1:dis:ed-3:v1:en

The introduction/scope and definitions around clauses 3.6 and 3.10 were checked. The exact final-edition status must be rechecked before normative citation.

**Implication:** “measure every stage and report an end-to-end completion rate” is not a new research mechanism. A proposed study must identify an estimand that is not merely a renamed FTA/FTE/FMR/FNMR/throughput table, and must specify the operational population and action loss.

### NIST standards: yes for the single-comparison versus transaction boundary

[K] NIST SP 800-63B, Sec. 5.2.3, states that biometric comparison is probabilistic and that FMR does not by itself establish authentication confidence or account for presentation attacks:

https://pages.nist.gov/800-63-3/sp800-63b.html

[K] NIST SP 800-76-2, Secs. 10.2-10.4, pp. 46-47, distinguishes the FMR of one comparison from a transaction in which multiple samples/comparisons are permitted. Note 1 on p. 46 is directly relevant to why transaction false acceptance need not equal a single-comparison FMR:

https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-76-2.pdf

[K] NIST's *Fundamental issues in biometric performance testing* discusses why technology/scenario performance cannot be directly read as operational performance, including user behavior and unobserved impostor claims, pp. 19-21:

https://www.nist.gov/system/files/documents/2021/05/26/fundamentalissues_final.pdf

**Implication:** the problem statement “FAR/FRR alone does not predict wrong action” is already occupied as a measurement warning. It can be used as motivation, not novelty.

### Operational transaction studies: strong direct neighbor

[K] NISTIR 8564, *Project Clearprint: Operational Performance Anomalies in Biometric Systems* (June 2025), studies operational fingerprint transactions and separates packaging, orchestration, capture and matching issues. Executive Summary p. 1, Introduction/Background/Methods pp. 2-10, anomaly classes pp. 7-9, results pp. 10-13 and conclusion p. 13 were inspected:

https://doi.org/10.6028/NIST.IR.8564
https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958476

It reports 78 sanitized transactions and explicitly limits generalization because the sample is small/anecdotal and the testbed does not reproduce the full operational orchestration layer.

**Implication:** a Palm pipeline stage trace and an operational failure taxonomy are direct neighbors. The only possible residual is not “we found hidden stages”; it is a predeclared, held-out test of whether a small conditional joint-risk estimator improves a concrete action decision beyond the standard metrics and controls.

### Existing statistical/policy neighbors occupy the generic method

- Czajka and Bowyer, 2015, *Statistical analysis of multiple presentation attempts in iris recognition*, DOI `10.1109/CYBConf.2015.7175982`, treats repeated attempts as non-identically distributed and shows later-attempt effects. This blocks a generic “attempts are dependent” claim.
- Murakami and Takahashi, WIFS 2009, DOI `10.1109/WIFS.2009.5386482`, uses sequential biometric accept/reject/continue decisions. This blocks a generic sequential policy claim.
- Geifman and El-Yaniv, NeurIPS 2017, formalizes selective risk and coverage; SelectiveNet, ICML 2019, gives a learned reject option. URLs: `https://proceedings.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf` and `https://proceedings.mlr.press/v97/geifman19a.html`.
- Angelopoulos et al., *Conformal Risk Control*, arXiv:2208.02814, supplies a direct held-out calibration baseline: `https://arxiv.org/abs/2208.02814`.
- Moskovitch and Jagadish, *Reliability at Multiple Stages in a Data Analysis Pipeline*, CACM manuscript, frames end-to-end reliability across pipeline stages: `https://www.cs.bgu.ac.il/~yuvalmos/docs/cacm.pdf`.
- The recent unreviewed preprint *What Two Gates Buy You: Selective-Risk Guarantees and the Non-Identifiability of Abstention Cascades* gives an especially close collision warning: `https://zenodo.org/records/21837226`. It states a product law under conditional independence and a two-world non-identifiability counterexample. It must be treated as a direct neighbor, not as novelty support.

## Unique surviving boundary

The only boundary worth retaining is:

> For a **specific frozen edge action pipeline**, do stage-conditioned observables and an explicit episode-linked joint-risk estimator predict an authorized terminal action outcome better than (a) the ISO/NIST-style component/transaction metrics, (b) product of marginal stage rates, (c) matcher score/margin and quality thresholds, (d) fixed retake/unknown, and (e) standard selective/conformal calibration, **at equal eligible capture opportunities and equal retake budget**?

This is an apparatus-specific empirical question with a possible negative result. It is not a claim that ISO metrics are wrong, nor that a new metric family is needed globally.

## Exact observations, actions and metrics

### [D] One episode and observed variables

One eligible, consented physical presentation starts one episode, even when no frame is produced. Record linked, same-episode values:

- `C`: frame captured;
- `R`: valid ROI from that frame;
- `Q`: quality outcome and reason;
- `M`: top/second identity, scores, margin and matcher state;
- `U`: frozen unknown/retake state;
- `A`: `mock_commit`, `unknown`, `retake_exhausted` or `system_error`;
- `T`: stage timestamps and capture-to-terminal-action time;
- `Z`: only pre-action context: camera profile, exposure/gain/AWB, background/placement condition, attempt index, ROI/quality state and Pi load/thermal state.

Do not use future labels or terminal outcomes as online features. Preserve no-frame and no-ROI starts.

### [A] Allowed action

The online decision is frozen `commit`, `unknown`, or one permitted `retake`. The study action is a simulated, idempotent debit only. No real payment or security claim is allowed.

### [T] Estimands

For an eligible start and context `z`:

```text
p_wrong(z) = P(wrong mock action and A=commit | eligible start, Z=z)
p_complete(z) = P(completed terminal action | eligible start, Z=z)
q_t(z) = P(T > t | eligible start, Z=z)
```

The exact chain rule is:

```text
P(A,Y | Z) = P(C|Z) P(R|C,Z) P(Q|R,C,Z)
             P(M|Q,R,C,Z) P(U|M,Q,R,C,Z)
             P(A,Y|U,M,Q,R,C,Z).
```

The product baseline replaces relevant conditional factors with marginal or independently calibrated stage rates. A minimal candidate estimator is a small chain of calibrated conditional models, with only predeclared pairwise interaction terms. It is not a new neural model.

Primary decision metric:

```text
L = c_wrong * wrong_action + c_unknown * refusal_or_unknown
    + c_time * max(T - t0, 0)
```

Costs and `t0` must be fixed before test labels. Secondary metrics: held-out Brier score, log loss, calibration error, risk-coverage/action-loss curve, all-start completion, p95 time and CPU/RAM/energy overhead. Use person/session-clustered intervals, not frame-level iid intervals.

## Minimal counterexample and negative-result path

Let `B1` and `B2` be two stage failures. In both worlds:

```text
P(B1=1) = P(B2=1) = 0.10.
```

An independence product predicts `P(B1=B2=1)=0.01`. In World A, failures are common-cause and perfectly correlated, so the joint probability is `0.10`. In World B, failures are disjoint or independent, so the joint probability is near `0` or `0.01`. Stage marginals, single-stage FAR/FRR and mean time can be identical while the terminal joint risk differs by an order of magnitude. Exposure/background/ROI geometry could create such common cause, but that physical assertion is [C] until measured.

Stronger identifiability result: if the available log contains only stage marginals, timing histograms and coverage, construct two worlds with identical logs but different `P(wrong_action)`. Any estimator using only that log gives the same answer in both worlds and must fail in at least one. The minimum witness may be episode linkage, true claimed identity, stage-conditioned context, or terminal action outcome. If the proposed trace cannot obtain that witness, `STAGE-RISK` is killed as a positive estimator and retained only as `STAGE-NULL` negative evidence.

## Smallest falsification protocol

1. Freeze camera, ROI, quality gate, gallery, matcher, threshold, unknown rule, retry budget and mock action.
2. Collect all eligible starts, not accepted crops only; split calibration/test by person and session.
3. Compare: frozen production rule; product of marginal rates; matcher score/margin; quality-only; independent stagewise logistic/isotonic; chain-conditioned estimator; fixed retake; selective-risk and conformal-risk baselines where assumptions hold.
4. Match eligible starts, capture opportunity and retake budget. Report estimator CPU/RAM/energy separately.
5. Stop before thesis framing if a standard baseline matches, if stage context adds no held-out value, if action labels are unavailable, or if the result depends on random frame splits.

## Data, ethics, hardware and feasibility

The existing Pi 5 VIS route is sufficient for a pilot: camera, current ROI/matcher, monotonic timestamps, stage trace and an idempotent mock transaction. No IR/NoIR, attack material or new sensor is required. The hard constraint is independent action labels, especially unknown/wrong-action episodes; zero observed errors is only a one-sided upper bound. Use consented participants, identifier-free account IDs, local minimization/deletion and no real payment. A small pilot can test calibration and identifiability but cannot support a rare-error safety guarantee.

Advisor fit is limited to trustworthy vision, uncertainty and incomplete observations. No inspected Bob Zhang paper establishes this exact action-risk estimator; adjacency is not novelty.

## Kill conditions

Kill the positive claim if:

1. the endpoint is only renamed FMR/FNMR, FTA/FTE or throughput;
2. product, matcher-confidence, fixed quality/margin, fixed retake, selective prediction or conformal calibration matches/dominates at equal capture cost;
3. the estimator uses post-action or test-label leakage;
4. same-episode capture/ROI/matcher/action linkage is invalid;
5. enough independent action labels cannot be collected and no continuous proxy is authorized;
6. a fixed camera/ROI repair explains the effect;
7. the only deliverable is a log schema, dashboard or reliability table.

## Evidence ledger

| Claim | Label | Source/version | Exact reading boundary | Caveat |
| --- | --- | --- | --- | --- |
| Biometric testing distinguishes technology, scenario and operational performance, including acquisition and throughput quantities. | [K] | ISO/IEC DIS 19795-1 current ISO OBP page: https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:19795:-1:dis:ed-3:v1:en | Introduction/scope and definitions around clauses 3.6/3.10. | Current DIS page; final edition status must be checked. |
| FMR does not alone establish authentication confidence. | [K] | NIST SP 800-63B: https://pages.nist.gov/800-63-3/sp800-63b.html | Sec. 5.2.3, lines 574-587. | Digital identity guidance, not Palm-specific. |
| Single-comparison FMR differs from multi-sample transaction risk. | [K] | NIST SP 800-76-2: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-76-2.pdf | Secs. 10.2-10.4, pp. 46-47; Note 1 p. 46. | Fingerprint/iris/face specification. |
| Operational transaction anomalies can occur outside intrinsic matcher quality. | [K] | NISTIR 8564 (June 2025): https://doi.org/10.6028/NIST.IR.8564 | Executive Summary p. 1; methods pp. 2-10; anomalies pp. 7-9; results pp. 10-13. | 78 sanitized transactions; small/anecdotal and incomplete orchestration testbed. |
| Multiple attempts need not be iid. | [K] | Czajka and Bowyer 2015, DOI: https://doi.org/10.1109/CYBConf.2015.7175982 | Abstract and multiple-attempt experiment description. | Iris, not Palm. |
| Sequential accept/reject/continue is known. | [K] | Murakami and Takahashi WIFS 2009, DOI: https://doi.org/10.1109/WIFS.2009.5386482 | Secs. 2-4 in the local prior gate. | Recheck full text before final thesis citation. |
| Selective risk/coverage is known. | [K] | Geifman and El-Yaniv NeurIPS 2017: https://proceedings.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf | Sec. 2 and risk/coverage definitions. | Generic classifier baseline. |
| Conformal risk control is a direct calibration baseline. | [K] | Angelopoulos et al., arXiv:2208.02814: https://arxiv.org/abs/2208.02814 | Abstract and method/guarantee description. | Exchangeability/monotonicity and sample size must be checked. |
| Two-gate dependence and non-identifiability are already a close mathematical neighbor. | [K/GAP] | Zenodo v0.1: https://zenodo.org/records/21837226 | Abstract/summary: product law, dependence and identical-log/different-risk counterexample. | Unreviewed preprint; collision warning, not novelty evidence. |

## Unresolved uncertainties

1. The exact final ISO/IEC 19795-1 edition and normative wording need verification.
2. Full-text page checks for Murakami/Takahashi and Palm-ID remain required before a final literature claim.
3. The current Pi executable may not yet expose every pre-capture/early-ROI failure without changing the opportunity definition.
4. The local project may not have enough independent unknown-person mock-action episodes for a useful wrong-action estimate.
5. It remains unknown whether stage-conditioned variables add value after camera/ROI/threshold freezing.

## Decision

`STAGE-RISK` is **HOLD/PIVOT**. ISO/IEC 19795, NIST transaction metrics, operational biometric studies, sequential biometrics, selective prediction and conformal risk control occupy the broad claim. The only defensible boundary is a local, frozen-pipeline identifiability/dependence audit with an explicit action loss and equal-capture-cost comparison. The first gate is the negative counterexample/all-start witness check; do not fit a policy or claim a new metric before it passes.

PIVOT

