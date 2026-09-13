---
topic: edge-selective-observation-audit
created: 2026-08-28
last_verified: 2026-08-29
status: active
depth: deep
related:
  - tta-unlabeled-accept-rollback
sources:
  - url: https://www.sciencedirect.com/science/article/pii/S0888327025012385
    fetched: 2026-08-28
  - url: https://www.sciencedirect.com/science/article/pii/S0304407624001921
    fetched: 2026-08-28
  - url: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7102071
    fetched: 2026-08-28
  - url: https://pmc.ncbi.nlm.nih.gov/articles/PMC13306937/
    fetched: 2026-08-28
  - url: https://www.nature.com/articles/s41598-026-36884-6
    fetched: 2026-08-28
  - url: https://proceedings.mlr.press/v267/chen25al.html
    fetched: 2026-08-28
  - url: https://proceedings.mlr.press/v297/sadhuka26a.html
    fetched: 2026-08-28
  - url: https://proceedings.mlr.press/v23/dasgupta12/dasgupta12.pdf
    fetched: 2026-08-28
  - url: https://arxiv.org/pdf/2605.29533
    fetched: 2026-08-28
---

# Edge Selective Observation and Common-Cause Risk

## Summary

Recent work confirms that adaptive/event-triggered sensing and selective-label correction are active, mature neighboring areas. The unresolved opportunity is narrower: a low-power trigger changes which safety events are observed at all, so the system must estimate full-population no-wake risk rather than report accuracy only on triggered samples.

Common-cause degradation is also explicitly recognized in a 2026 sensor-centric safety survey: duplicated sensors can fail together under shared glare, fog, calibration, or observability limits. This supports the story and evaluation need, but not a claim of method novelty.

The current status of both project candidates is Amber: promising research questions, requiring direct-neighbor and identification audits before promotion.

## Findings

The 2025 Smart Adaptive Trigger Sensing paper frames event-triggered sensing as a trade-off between missed and false triggers under dynamic environments. It uses feedback control, Bayesian optimization, lightweight models, and a digital twin on a low-power node, reporting approximately 30% higher F-beta than conservative manual settings and 2-3 orders lower computational overhead than exhaustive processing. This kills generic claims about adaptive thresholds, low-power trigger sensing, or energy-efficient wake-up. It leaves open whether the trigger-induced unobserved population can be audited and whether a downstream safety risk bound, rather than trigger F-beta, is controlled.

The 2025 Journal of Econometrics tax-audit paper and a July 2026 selective-audit working paper show that selective labels are a general statistical problem: outcomes are observed only after a decision allocates scarce audit capacity. They use institutional or randomized/full-support arms, longitudinal structure, inverse-propensity or doubly robust estimation, and explicit sensitivity/bound analysis. These papers are strong methodological neighbors. They imply that an edge sensing proposal must state positivity/support, ignorability or sensitivity assumptions, and whether the audit arm reaches every no-wake stratum. A phrase such as “randomly audit a few no-wake frames” is not sufficient identification by itself.

The 2026 Sensor-Centric Survey of Autonomous Driving ties sensor physics, uncertainty propagation, integrity monitoring, and action-level safety together. It explicitly warns that redundant sensors remain vulnerable to common-cause insufficiencies, such as cameras blinded by the same glare or LiDAR attenuated by the same fog, and calls for calibrated, observable, actionable uncertainty and scenario-indexed validation. This is a strong problem-level motivation for separating sensor health, scene observability, task confidence, and residual observability. It also means that confidence-aware fusion and sensor health monitoring alone are already crowded.

Recent multisensory causal-inference work models whether cues arise from a common cause or separate causes and averages fusion and segregation estimates according to posterior causal structure. This is a conceptual near-neighbor for false-consensus handling, but it is not evidence that a low-cost RGB/NIR/ToF edge safety action protocol, with physical degradation episodes and equal resource budgets, has been solved.

Chen, Li, and Mao's ICML 2025 selective-label paper formalizes that historic decision rules can make full-population classification risk unidentified; it supplies exact-identification conditions and partial-identification bounds under an instrumental-variable setting. Sadhuka et al.'s 2026 multi-stage-censoring work independently treats a costly funnel where ground truth appears only at the final stage and demonstrates the induced risk-estimation bias. These are direct methodological collisions with any claim that a wake policy plus inverse-propensity weighting alone is a new contribution. They do not evaluate a low-power physical sentinel, explicit sleep/wake state, or a full-population edge risk-energy-latency endpoint.

Dasgupta's selective-sampling counterexamples supply an additional boundary: adaptive sampling can leave parts of the population unrepresented even when every point has a shrinking query probability. For the cascade project, known inclusion probabilities and a full-support audit arm are necessary for an estimand, but they do not by themselves justify a learned controller, transfer claim, or low-risk bound under nonstationary physical causes.

## Insights

- The strongest E candidate is not a new trigger policy. It is a measurement-and-control protocol for action-dependent missingness: the wake decision censors the no-wake population, and a known-support audit arm is used to estimate or bound its safety risk.
- The strongest S-H candidate is not another fusion architecture. It is an operational decision rule that treats evidence dependence as a state and compares false-permit risk under equal latency, energy, and retry budgets.
- The most important feasibility gate is ground-truth support. Without an external reference covering no-wake episodes and physically induced failures, both candidates collapse into ordinary triggered-subset benchmarking.
- A valid E contribution cannot be the estimator alone: ICML 2025 and ML4H 2026 already make selective censoring and risk identification central objects. Its remaining question is a physical sensing protocol with predeclared inclusion, energy, readiness, and action-state logs.
- A valuable negative result remains available: if a fixed threshold, uniform audit, or always-on verifier dominates the proposed policy on the frozen risk-resource Pareto frontier, the study can reject the added complexity.

## Strongest objection

Selective-label theory may make the E contribution look like an application of inverse-propensity or doubly robust estimation: ICML 2025 covers risk identification/partial identification from selectively labeled data, and ML4H 2026 covers multi-stage censoring with costly funnel decisions. The project therefore needs an exact physical task/protocol distinction and must be prepared to report a replication or impossibility result instead of a new algorithm.

The stricter physical objection is time anchoring: an audit-time verifier frame can be negative even when an object was present at the sentinel's original decision time. Randomized inclusion fixes selection bias but not this measurement error. Therefore an E study cannot claim a safety-risk bound unless an independent reference measures the audit-frame-to-decision-time relation by motion/readiness stratum, or the estimand is narrowed to the audit-time event.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|

## Open questions

- Does any post-2026 paper evaluate trigger-induced no-wake safety risk with a full-support audit arm on a real camera/sentinel edge device?
- Can the proposed hardware expose actual wake/sleep state, sentinel telemetry, audit probability, and incremental energy rather than simulated masks?
- Are positivity and stationarity plausible across material, angle, illumination, motion, and device strata?
- Does a simple uniform audit match telemetry-stratified auditing at the same budget?
- Does the candidate's observable telemetry support an identification assumption beyond the full-support randomized audit, or should its output be a partial-risk bound rather than a point estimate?

## Timeline

- 2026-08-28 - merged latest-paper scan with existing E and S-H project state; both remain Amber pending direct-neighbor and identification audits.
- 2026-08-28 - added ICML 2025, ML4H 2026, and selective-sampling boundary evidence; E remains protocol-level Amber and cannot claim selective-label estimation as its innovation.
- 2026-08-28 - validation found generic wake-cascade/energy collision in Ballet et al. (arXiv:2605.29533v1, pp. 2-3, 9-10, 12-14) and added the time-anchor/label-fidelity kill condition. E is now only an Amber physical measurement-protocol pivot against uniform full-support audit.
- 2026-08-29 - AVS is killed by direct 2026 adaptive-sensing neighbors. TVA is killed because finite wake coverage makes the `UNKNOWN` condition deterministic and continuous reference logging is an established evaluation control. VSB is killed by a full official 2025 MEMS mount-integrity thesis; its ambiguity model remains a preflight condition only.
