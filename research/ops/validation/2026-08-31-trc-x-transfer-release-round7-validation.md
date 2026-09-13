# Validation Audit: 2026-08-31 TRC-X crossed-cell transfer release certificate

## Decision investigated

Whether **TRC-X** can be retained as an undergraduate FYP claim: before a frozen local edge alert/record policy is copied to a replacement low-cost sensing unit, a technician uses a finite, labelled, pre-registered unit x load x injected-fault test matrix to issue `release`, `trial-only`, or `do-not-release`.  Its asserted distinction is a cluster-aware, one-sided bound on false release for a declared population, with `trial-only` when too few distinct devices support a device-transfer statement.

## Claim under test

The candidate is not a new classifier or diagnosis method.  Its only possible research claim is that a new, cluster-aware acceptance rule is needed for policy transfer across low-cost devices and conditions, and that this rule gives a useful false-release bound with 4--6 independently purchased units.

This audit tests that narrow claim, not the practical value of doing a conservative pre-deployment bench check.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | Reliability-demonstration/assurance testing already chooses a pass/fail rule from a finite test plan, explicitly trades consumer and producer risks, and admits sequential plans. Kim and Wilson's 2025 treatment defines a plan by `(n,c)` and compares classical, Bayesian assurance, assurance-RDT and SPRT plans (pp. 1--2, Secs. 1--2). Bernburg et al. (2024), Sec. Abstract, derives sequential acceptance plans for future-population reliability. Zheng et al. (2023), Secs. 1--3, explicitly combine qualification sampling, acceptance sampling, cost and unit heterogeneity. | TRC-X observes frozen-policy decision loss rather than lifetime/degradation. That only changes the definition of a test failure; no distinct estimator, action mechanism, or guarantee was supplied. | High collision; high confidence. |
| 2. Exact-claim collision | The proposed action maps exactly to established sample-disposition logic: NIST describes an acceptance plan as a sampling scheme plus decision rules; a double/multiple/sequential plan yields `accept`, `reject`, or `no decision / take another sample` (NIST Sec. 6.2.2). `release / do-not-release / trial-only` is that same disposition with different labels. The target is likewise a future-population release decision under explicit risk constraints, which Bernburg et al. (2024) already formulate. | No inspected source used the exact phrase “frozen edge anomaly policy copied to a replacement board” or the exact unit-load-fault labels. That is an application wording difference, not evidence of a distinct task/action/endpoint. | High collision; medium-high confidence because application-specific exact-neighbor search cannot prove absence. |
| 3. Boundary / impossibility | If the target is a **sampled future device population**, repetitions within a tested device are not independent device draws. Standard binomial assurance itself assumes independently tested items with common success probability (Kim and Wilson 2025, p. 1, Sec. 1). Under arbitrary unit effects, observed results from 4--6 units do not identify the untested-device failure rate without a sampling frame and a hierarchical/exchangeability model. If the target is the **finite observed matrix**, exhaustive testing gives a deterministic matrix result, not a transfer claim about an additional replacement unit. | A model-based, prior-dependent assurance report is possible if the manufacturer population, unit-sampling mechanism, exchangeability/hierarchical model, and link from seeded faults to intended use are all supplied. TRC-X supplies none, and 4--6 units cannot empirically validate those assumptions. | High; decisive for the claimed bounded transfer guarantee. |

## Assumption and identification audit

Let `m` be the number of independently sampled physical devices and collapse every repeated load/fault trial on a device to the conservative device outcome: did this unit fail any named acceptance cell?  Even under the favourable i.i.d.-device Bernoulli model, observing zero failed devices gives the exact one-sided 95% Clopper--Pearson upper limit

`p_U = 1 - 0.05^(1/m)`.

Thus `m=4` gives `p_U = 0.527`, and `m=6` gives `p_U = 0.393`.  To report a 95% upper limit no greater than 0.20 with zero device failures requires at least 14 independent devices; for 0.10 it requires at least 29.  More load/fault replicates on the same 4--6 boards can establish within-board behaviour, but cannot reduce this device-level binomial bound without adding a model that links cells and boards.  The arithmetic is a direct consequence of `Pr(0 failures | p)=(1-p)^m=0.05`; it is not an empirical finding.

That makes the candidate fork unavoidable:

1. **Finite declared population = the purchased boards x named cells.** Test every cell and the local oracle can truthfully say which cells passed. There is no statistical false-release bound to invent, no unobserved replacement device, and a fixed full-factorial pass/fail table subsumes the method.
2. **A larger / future device family.** The sampling frame, independence/exchangeability of boards, and relationship from injected faults to use-time loss become load-bearing. Without them, construct two worlds with identical tested 4--6 boards and opposite untested-board outcomes. Every permitted observation is identical; a device-family release conclusion is therefore not identified.

The candidate's use of reversible software/signal injection adds a second boundary. It labels performance on the injected fault distribution only. Unless a pre-specified mechanism maps those injected faults to the deployment fault population, a result cannot be interpreted as a reliability/transfer rate for field failures. Existing reliability work does not rescue that inference: it states its parametric lifetime/degradation and population assumptions rather than deriving them from a fault matrix.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| H. Bernburg, C. Elster, K. Klauenberg, *Flexible Bayesian reliability demonstration testing*, 2024 | Device test outcomes over time; derive zero-failure and sequential acceptance sampling plan. | Demonstrate future population reliability at specified probability; application on utility meters. | Future-population reliability release, consumer protection, cost-aware sequential testing. | Kills treating a release rule plus `trial-only`/more testing as a new action family. It has a lifetime-process model, whereas TRC-X has none. |
| H. Kim, A. G. Wilson, *Comparing Risks for Binomial Reliability Assurance Test Planning*, 2025 | Binary test results, `(n,c)` plans, classical/Bayesian/RDT/assurance and SPRT alternatives. | Producer/consumer risk trade-off under a common-probability, independent-item model. | Named false-release/consumer-risk criterion and matched-cost test-plan comparison are standard. | Kills a generic one-sided bound or adaptive sample-count contribution; exposes the unprovided independence/common-population assumption. |
| H. Zheng, J. Yang, Y. Zhao, *Reliability demonstration test plan for degraded products subject to Gamma process with unit heterogeneity*, 2023 | Qualification and acceptance sampling, stress/degradation observations, random unit heterogeneity, cost. | Decide qualification/acceptance with consumer/producer risk. | Accounts for unit heterogeneity when making acceptance decisions. | Kills “cluster-aware unit effect” as a new component. It is not an exact policy-loss endpoint, but that replacement does not create a new statistical principle. |
| H. Zheng et al., *Accelerated Degradation Data Analysis Based on Gamma Process With Random Effects*, 2025 | Product-level measurements across stress levels with random effects and interval inference. | Predictive reliability indices under explicit Gamma-process/stress/random-effect assumptions. | Repeated measurements nested in product and stress require a unit-level random-effect model. | Leaves only a fully specified model-based version, which is infeasible to validate from 4--6 purchased devices and unrelated injected faults. |
| NIST/SEMATECH e-Handbook, Sec. 6.2.2, *Lot Acceptance Sampling Plans* | Single/double/multiple/sequential sample and acceptance/rejection/no-decision rule. | Lot disposition and producer/consumer risks. | Exact three-way decision topology. | Kills the semantic relabelling of `no decision` as `trial-only`; a fixed stratified plan is the required baseline. |

## Strongest simple baseline

**Pre-registered fixed full-factorial acceptance table.**  Freeze the policy; enumerate every declared board, load and injected-fault cell; collect the independent oracle; release only if every required cell meets the predeclared loss threshold, otherwise do not release. If inspection remains desired, use NIST's ordinary double/multiple plan: `trial-only` means “no decision, collect the next predeclared device/cell.”

This baseline has the same inputs, same lab effort, the same local edge deployment, and a stronger statement about the *observed finite matrix* than a fitted cluster model.  If TRC-X instead samples cells, compare this table with a standard stratified sample over units as the primary sampling units and a conventional `(n,c)`/Bayesian assurance plan at equal cost. No candidate mechanism remains after this comparison.

## Contrarian result

**[KILL] TRC-X is a relabelled reliability acceptance/qualification exercise, not a distinct edge-research problem.**  Its honest deliverable could be a useful protocol appendix: “with six boards, the device-transfer question cannot be certified at the declared risk; here is the finite matrix that was actually tested.”  That is scientifically honest and directly answers the user's earlier concern about new-device/new-load/new-fault transfer, but it does not support a thesis claim about a new release certificate.

The claim cannot be repaired by a more elaborate hierarchical/Bayesian model unless its priors and exchangeability relation are independently justified. With only a small convenience purchase of same-model boards, the model supplies the conclusion rather than the experiment identifying it.

## Feasibility audit

| Requirement | Finding | Status |
| --- | --- | --- |
| Four to six nominally identical units | Affordable in principle, but the prompt supplies no manufacturer lot/sampling frame, no controlled BOM/firmware provenance and no independent replacement-unit supply rule. | [GAP] for population inference. |
| Device-transfer estimand | Six devices can quantify six devices. It cannot provide a practically tight, distribution-free 95% device-family bound; even zero device failures leaves an upper bound of 0.393 under the i.i.d. favourable model. | [KILL] for the proposed guarantee. |
| Load/fault replication | Feasible as a non-hazardous scripted bench. It increases cell coverage, not independent device count. | [K] feasible measurement; [KILL] as a substitute for devices. |
| Independent oracle | A separate logger/signal generator can be built, but the candidate does not yet name its failure semantics or prove the oracle independent of the injected fault path. | [GAP]. |
| Edge relevance | A frozen policy can run locally while disconnected, but the inferential object is an offline acceptance test. Moving the policy to an edge node does not change the acceptance-sampling statistics or decision endpoint. | [KILL] as a differentiator. |
| Time window | A December demonstrator could implement the bench matrix; it cannot change the above statistical or direct-neighbor collision. | [K] feasible demo; [KILL] research contribution. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Reliability assurance test plans already choose `(n,c)` from consumer/producer risk, model a finite count of binary failures, and assume independent items with a common success probability. | [KILL] | Kim & Wilson, [open-access version of record](https://onlinelibrary.wiley.com/doi/epdf/10.1002/asmb.2912), *Applied Stochastic Models in Business and Industry* 41 (2025), e2912; received 2024-03-31, accepted 2024-11-17. | PDF p. 1, Abstract and Sec. 1, especially pp. 1--2, lines 20--56; Sec. 2 begins p. 2. | The specific binomial model is not valid under unknown within-device dependence; that is precisely the candidate's identification problem, not a licence to count repeated trials as units. |
| Flexible RDT derives future-population zero-failure and sequential acceptance plans and applies them to utility meters. | [KILL] | Bernburg, Elster & Klauenberg, [official Wiley version](https://doi.org/10.1002/asmb.2863), *Applied Stochastic Models in Business and Industry* 40(4), 2024, pp. 996--1011; first published 2024-04-26. | Abstract, HTML lines 115--119; publication date lines 87--89. | It assumes a time-varying parametric lifetime/counting-process model. It establishes a direct action/endpoint neighbor, not a proof about injected fault matrices. |
| Acceptance sampling already has accept/reject/no-decision and sequential extensions. | [KILL] | [NIST/SEMATECH e-Handbook, Sec. 6.2.2](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc22.htm), current official web version retrieved 2026-08-31. | Sec. 6.2.2, lines 6--25. | Official guidance, not a research paper; used only for the direct action equivalence. |
| RDT with qualification/acceptance distinction, cost, random unit heterogeneity and risk-constrained decision rules is already published. | [KILL] | Zheng, Yang & Zhao, [publisher version of record](https://doi.org/10.1016/j.ress.2023.109617), *Reliability Engineering & System Safety* 240 (2023), Article 109617. | Publisher abstract and Introduction (official HTML), retrieved 2026-08-31; see title/abstract and the explicit QSP/ASP, unit-heterogeneity and decision-criterion text. | 2023, not 2024--2026; it is a direct foundational component collision. Its Gamma-degradation endpoint differs from policy loss. |
| Recent reliability modelling treats unit random effects and stress-level observations through an explicit parametric model; small samples/limited stress levels make accurate inference difficult. | [KILL] | Zheng, Yang, Kang & Zhao, [author-hosted version of record PDF](https://pure.tudelft.nl/ws/portalfiles/portal/236209467/Quality_Reliability_Eng_-_2025_-_Zheng_-_Accelerated_Degradation_Data_Analysis_Based_on_Gamma_Process_With_Random_Effects.pdf), *Quality and Reliability Engineering International* (2025), DOI [10.1002/qre.3730](https://doi.org/10.1002/qre.3730). | PDF pp. 1--3, Sec. 1, especially p. 2 lines 39--49 and pp. 2--3 lines 119--170; Sec. 2, p. 4, Eqs. (1)--(2), lines 201--235. | The Gamma-process model is not proposed for TRC-X. It demonstrates that a valid random-effect conclusion needs stated structural assumptions; it cannot validate arbitrary injected-policy loss from six devices. |
| A 2024 RDT method derives consumer-risk-aware sequential plans for future population reliability. | [KILL] | Bernburg et al., same official 2024 source above. | Abstract, lines 115--119. | The detailed full text was access restricted in this pass; use only what the official abstract states. |
| With zero failures on `m` independent devices, the 95% one-sided binomial upper bound is `1-0.05^(1/m)`; 4/6 devices yield 0.527/0.393, and 14/29 are needed for bounds <=0.20/<=0.10. | [K] mathematical derivation | Derived from the i.i.d. binomial model stated by Kim & Wilson 2025, PDF p. 1, Sec. 1. | Algebra shown in “Assumption and identification audit.” | Conditional on i.i.d. sampled devices and a binary unit-level endpoint. It is optimistic for TRC-X because its repeated cells are correlated and its sampling frame is unspecified. |

## Queries and failed searches

Queries run 2026-08-31:

- `site:onlinelibrary.wiley.com 10.1002/asmb.2863 flexible Bayesian reliability demonstration testing 2024 full text`
- `site:nist.gov reliability demonstration testing acceptance sampling finite population clusters multilevel`
- `"reliability demonstration" "random effects" acceptance sampling device 2024`
- `"clustered" "reliability demonstration testing" acceptance sampling`
- `"Reliability demonstration test plan for degraded products subject to Gamma process with unit heterogeneity" DOI`
- `"qualification sampling plan" "unit heterogeneity" "acceptance sampling plan" 2024`
- `"qualification" "transfer" "acceptance sampling" reliability device deployment`
- `2024 cross machine transfer validation deployment acceptance test fault diagnosis`

Unresolved rather than negative evidence:

- [GAP] I did not verify a 2024--2026 primary paper whose *application text* is exactly “release a frozen edge anomaly policy to a replacement low-cost board after a crossed fault matrix.” This is not a novelty result. The action/statistical claim is already covered by the direct RDT/acceptance-sampling neighbors above.
- [GAP] A real manufacturer sampling frame, controlled product configuration and target loss threshold for any prospective 4--6-board fixture were not supplied.
- [GAP] No inspected source justifies a mapping from reversible software/signal injection to the frequency of future field fault mechanisms in the proposed setting.

## Decision

**KILL.** TRC-X must not occupy the thesis slot.  Preserve its narrow negative result as a protocol/evidence-sufficiency appendix if useful: the correct conclusion from a 4--6 board crossed matrix is bounded performance on the observed matrix and, at most, an explicitly model-conditional acceptance calculation.  It is not a new cluster-aware release mechanism and cannot defend a useful new-device transfer guarantee.
