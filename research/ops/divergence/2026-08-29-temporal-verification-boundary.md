# Divergence Packet: 2026-08-29 temporal verification boundary for wakeable sensing

## Decision investigated

Whether a low-cost, non-personal-data edge FYP can make a bounded and falsifiable **measurement-validity** claim: when a wakeable verifier becomes ready after the sentinel's decision time, does its later label refer to the original decision window at all, and can a predeclared original-time reference plus an excluded evaluation pool expose the resulting missed-event-risk error at a fixed verifier budget?

This is deliberately not a new wake policy, predictor, sensor fusion system, energy optimizer, label-imputation method, or time-tolerant detection metric.  It starts from the possibility that the reported evaluation target is physically unavailable under a common wake-and-verify setup.

## Search boundary

Queries run 2026-08-29:

- `2024 2025 sensor wake up delay warm-up event detection evaluation missed event ground truth paper`
- `2024 2025 time alignment delayed labels sensor event detection evaluation paper`
- `2024 2025 verification bias selective labels measurement sensor evaluation paper`
- `2024 2025 active sensing delayed observation label bias edge sensor paper`
- `site:proceedings.mlr.press 2024 selective labels evaluation randomized audits`
- `site:openreview.net 2024 adaptive labeling efficient out-of-distribution evaluation`

I read the active README/charter, the current adaptive-sensing divergence packet, and the AVS/VSB validation packet.  The primary sources inspected are Chang and Wiens (ICML 2024), Salles et al. (2024 journal version), and Gehrig et al. (Nature 2024).  WONS 2026 and Marinov et al. 2026 are read as direct adaptive-sensing neighbors from the preceding packets.  Mittal et al. (NeurIPS 2024) was inspected at the official abstract/metadata page only; its full text remains a [GAP].

## Recent-paper limitation map

1. [KILL] **A generic limited-label allocation contribution is occupied.** Chang and Wiens formalize selective labels as labels revealed by a testing/labeling decision and propose an EM correction.  Mittal et al. formulate adaptive label acquisition for efficient OOD evaluation.  A claim merely to select scarce verifier labels, reweight them, or replace missing labels is not distinct enough.

2. [KILL] **A generic temporal-tolerance score is occupied.** SoftED evaluates a detection according to its temporal proximity to an event.  Replacing a hard miss with a delayed-label tolerance window would be a metric variant, not a distinct physical result.

3. [K] **Time alignment can be a load-bearing experimental assumption.** Gehrig et al. use hardware synchronization, quantify synchronization error, and interpolate inter-frame labels only after excluding tracks that change between frames.  This supports treating label timing as a recorded experimental condition, but it does not study wake/readiness-censored labels.

4. [KILL] **Generic selective sensing is occupied.** WONS 2026 deactivates and reconstructs environmental sensing using history and correlated sensors.  Marinov et al. 2026 schedules high-power IAQ sensing from a sentinel.  A direction whose outcome is simply fewer wakes, lower energy, or better ordinary accuracy collides with this literature.

5. [C]/[GAP] **The remaining boundary may be narrower.** In the inspected sources, no paper establishes whether a post-wake physical verifier observation is admissible as a label for the sentinel's earlier decision time, or reports the empirical distortion of a miss-risk estimate against a continuously time-synchronized, original-time reference on a fixed low-cost bench.  This is a bounded retrieval result, not evidence of novelty.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| TVA: temporal-verification admissibility audit | A benchtop equipment-test maintainer uses a low-power sentinel to decide whether a brief, predeclared mechanical/light interruption needs a high-rate verifier.  A `no event` record whose verifier only became ready after the interruption can understate a missed-event rate and mislead a maintenance-test decision.  No safety actuator or production claim is involved. | For preregistered event-duration and wake/readiness cells, the naive protocol that labels the original sentinel window from the post-ready verifier has a nonzero, reference-measured absolute error in its `Pr(missed event)` estimate.  A protocol that records the decision/wake/ready interval, uses a time-synchronized original-time reference, and keeps a reference-only excluded evaluation pool identifies that error or reports the cell as `not label-admissible`. | SoftED handles delayed *detections*, not delayed availability of an event label.  Chang/Wiens handle decision-selected labels, not a physical observation window that begins after the target window.  Gehrig et al. synchronize/impute labels for an event-camera system, but do not test a wakeable verifier. | **KILL** if post-ready labels and original-time reference labels agree within a preregistered tolerance in every held-out latency-duration cell, or if a fixed readiness rule gives the same admissibility/error map.  The latter means the claimed protocol adds no value beyond logging a known warm-up delay. | **HOLD (Amber).** A microcontroller sentinel, a deliberately delayed/wakeable verifier, and a continuous reference photogate/current probe can be built without personal data.  Exact parts, clock method, and whether a reference can be independently synchronized remain [GAP]. |
| RLOG: readiness-interval provenance record | The same maintainer wants to know which records may be evaluated as original-time observations. | Attach `t_decision`, `t_wake_command`, `t_ready`, and verifier integration interval to every record. | Standard timestamp/provenance instrumentation; Gehrig et al. already make temporal synchronization an explicit measured condition. | The log can show that a label is late, but cannot recover the unobserved original-time state.  It changes no action or evaluation endpoint by itself. | **KILL as thesis.** Retain as compulsory instrumentation for TVA. |
| RANDAUD: random reserved verifier probes | The maintainer reserves some verifier budget independently of sentinel output to estimate miss risk. | A new random-audit or propensity-correction estimator for selectively observed events. | Chang/Wiens 2024 and Mittal et al. 2024 are direct generic selective-label/adaptive-labeling neighbors. | A standard randomized holdout plus unweighted/known-propensity analysis matches it, or the claimed result needs assumptions about unseen events. | **KILL as mechanism.** A predeclared random/excluded pool is a control in TVA, not the contribution. |
| TSLACK: physical latency-tolerance score | The maintainer wants to credit a delayed verifier observation as a near miss rather than a miss. | A score that gives partial credit based on wake latency/event duration. | SoftED already defines temporal tolerance and soft detection scores. | Fixed tolerance constants or SoftED produce the same ordering. | **KILL.** Event duration and readiness may appear as explanatory covariates in TVA, never as a new metric. |
| BMAP: hardware-specific wake/readiness boundary map | A component buyer needs to know which short event durations cannot be judged by a particular sentinel-plus-verifier pair. | Map the finite region where verifier readiness begins too late to label the original time. | This is a component measurement rather than a new edge method.  Wake delay measurement is established engineering practice; Gehrig et al. demonstrate that timing error can be characterized. | A datasheet/readiness measurement suffices, or results fail to replicate across boards. | **PIVOT only.** It is valuable as TVA's negative result or a reproducible lab appendix, but not an independent thesis unless a later exact-neighbor audit finds a distinct endpoint. |

## Top two formalizations

### TVA: temporal-verification admissibility audit

- **[D] Decision and outcome:** At original decision time `t0`, a sentinel emits `verify` or `no-verify` for event `E[t0, t0 + w]`.  A wakeable verifier receives a command at `tw`, becomes physically ready at `tr`, and integrates over `V[tr, tr + q]`.  Its label `L` may be used only for a declared target time interval.
- **[A] Protocol conditions:** (i) event start/duration, wake delay, and board condition are randomized or blocked before analysis; (ii) a separate time-synchronized reference produces `Y0` for the original target interval; (iii) `Y0` is unavailable to the online sentinel/verifier; (iv) thresholds, exclusion rule, and a reference-only evaluation pool are frozen before held-out cells; (v) verifier energy/on-time is matched across naive and audited protocols.
- **[T] Falsifiable empirical claim:** On held-out latency-duration-board cells, `abs(miss_naive - miss_reference) > delta` for at least one preregistered cell, while the admissibility-aware report either estimates the reference miss rate within `delta` on labelled-admissible cells or returns `not label-admissible` rather than a false precision claim.
- **Counterexample / boundary:** Construct two physical traces identical after `tr`: one has a short event wholly in `[t0,tr)`, the other has none.  Both yield identical `(sentinel trace, t0, tw, tr, L)` if `L` observes only after `tr`, yet their original-time labels differ.  Without `Y0`, a persistence assumption, or an observation overlapping the target window, the original-time missed-event rate is not identifiable from those records.
- **Negative-result value:** If no distortion occurs in the entire declared operating box, this bounds the need for the extra audit in that box.  If distortion occurs only below a duration/readiness ratio, the result is a finite applicability boundary, not a claim about all wakeable sensors.

### BMAP: readiness-duration map (pivot)

- **[D] Measurement:** For event durations `d` and verified readiness lags `r`, record whether `V[r,r+q]` overlaps the original event interval and whether the reference says the event persists.
- **[A] Claim constraint:** The output is a hardware/configuration-specific map, not a prediction of arbitrary real-world faults.
- **[T] Counterexample:** A different sensor warm-up or a persistent event distribution changes the map; it cannot justify a general `wake-and-verify is reliable` claim.
- **Negative-result value:** A null map establishes that temporal censoring is not material for the stated box, allowing the FYP to honestly pivot to replication/instrumentation.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Selective labels arise when a decision controls access to ground truth; the paper's model distinguishes the true label, observed proxy, and testing/labeling indicator. | [K] | Chang and Wiens, *From Biased Selective Labels to Pseudo-Labels*, ICML 2024, PMLR 235:6286-6324. Official PDF: https://raw.githubusercontent.com/mlresearch/v235/main/assets/chang24e/chang24e.pdf | PDF p. 1, Abstract and Sec. 1; p. 2, Sec. 2 and Fig. 1; pp. 3-4, Sec. 3. | It studies clinical-like test decisions and an EM learner, not a physical readiness interval.  It kills a generic selective-label method claim. |
| Adaptive labeling is already an evaluation-budget allocation problem. | [K] | Mittal, Ma, Joshi, and Namkoong, *Adaptive Labeling for Efficient Out-of-distribution Model Evaluation*, NeurIPS 2024. Official OpenReview record: https://openreview.net/forum?id=uuQQwrjMzb | Official abstract/metadata inspected 2026-08-29; full PDF was blocked by the publisher challenge, so sections/pages are [GAP]. | Use only as a direct-neighbor lead until a full-text audit.  Do not claim a distinction from its acquisition action. |
| SoftED introduces temporally tolerant event-detection evaluation and shows it can change evaluation/selection. | [K] | Salles et al., *SoftED: Metrics for soft evaluation of time series event detection*, Computers & Industrial Engineering 198 (2024) 110728; preprint: https://arxiv.org/abs/2304.00439 ; DOI: https://doi.org/10.1016/j.cie.2024.110728 | Preprint Sec. 1, pp. 1-3; Sec. 3, pp. 5-7; Sec. 4.3, pp. 10-12. | This is a detection-time tolerance metric, not proof about whether a delayed sensor observation labels a prior interval.  It kills TSLACK. |
| A recent low-latency sensing study explicitly measures hardware synchronization and treats label construction between frames as an approximation requiring exclusions/interpolation. | [K] | Gehrig et al., *Low-latency automotive vision with event cameras*, Nature 629, 1034-1040 (2024), https://doi.org/10.1038/s41586-024-07409-w | Methods, `Comments on time synchronization` and `Ground truth generation for inter-frame detection`, online article lines 336-359 / article Methods section inspected 2026-08-29. | Different hardware and an automotive detector; it supports the importance of timing/label construction but does not validate TVA. |
| WONS 2026 virtualizes intentionally inactive environmental sensor readings using correlated observations/history and a calibrated dormant limit on ESP32 testbeds. | [K] | Attarha and Forster, *Sensing Without Sensing*, WONS 2026, official IFIP PDF: https://dl.ifip.org/db/conf/wons/wons2026/1571220625.pdf | Abstract and Secs. II-III, printed pp. 25-28, audited in the preceding adaptive packet. | Kills an energy/virtual-sensing reframing.  It does not specify original-time label admissibility after physical wake. |
| Marinov et al. adaptively schedule high-power IAQ sensing from a continuous sentinel and evaluate energy/fidelity. | [K] | Marinov et al., *Digital-Twin-Assisted Adaptive Sensor Scheduling for Energy Optimization in Battery-Powered Indoor Air Quality IoT Nodes*, Electronics 15(11):2395, 2026-06-01, official PDF: https://mdpi-res.com/d_attachment/electronics/electronics-15-02395/article_deploy/electronics-15-02395.pdf | Abstract; Secs. 2.5-2.7, 3.4, 4.3-4.4, audited in validation packet 2026-08-29. | Kills generic sentinel-triggered high-power sensing, not a fixed-policy audit of time-censored labels. |
| The broad claim that TVA is novel or distinct from every physical-evaluation paper. | [KILL] | Searches and bounded sources above. | N/A. | No global novelty inference is permitted.  TVA remains Amber pending an independent exact-claim/citation-chain and boundary audit. |

## Queries and failed searches

- Searches returned broad virtual sensing, sensor scheduling, selective-label learning, and time-tolerant event metrics, but no inspected primary paper with all of: a wakeable physical verifier, label target fixed at the original sentinel time, a separately synchronized original-time reference, and an excluded evaluation pool at matched verifier budget.  This is a retrieval gap, not positive novelty evidence.
- `2024 2025 wake-up ground truth sensor event detection` found older wake-up delay measurements and generic event-monitoring systems.  They are not enough to establish TVA's exact empirical claim.
- The NeurIPS 2024 adaptive-labeling full text and any 2025-2026 citations specifically connecting it to physical sensor readiness remain [GAP].

## Decision

**HOLD.** TVA is the sole Amber candidate from this packet worth adversarial validation.  Its potentially defensible contribution is not "better adaptive sensing"; it is a predeclared, hardware-bounded validity test for the **meaning of a reliability label** when wake/readiness occurs after the decision time.  RLOG, RANDAUD, and TSLACK are **KILL** as thesis mechanisms; BMAP is **PIVOT** only.  Before promotion, an independent audit must (1) find the closest physical-test/evaluation direct neighbor and later citation chain, (2) try to show that interval logging or a fixed latency rule completely removes TVA's claimed contribution, and (3) check whether the fixed-budget comparison is identifiable without granting the offline reference an unfair role.

HOLD
