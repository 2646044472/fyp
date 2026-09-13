# Validation Audit: 2026-08-28 C1 and C3 candidate-specific audit

## Decision investigated

Whether the two supplied Gate-1 candidates in `research/ops/divergence/2026-08-28-low-cost-edge-reliability-divergence.md` have an auditable distinction and a minimally feasible experiment:

* **C1:** calibration-age-aware selective CO2 alert: `alert / no-alert / inspect` should reduce false-safe threshold decisions at a fixed inspection budget.
* **C3:** resource-informed edge-service failure suspicion: a lightweight `healthy / resource-stressed-suspect / fail-slow-suspect` state machine should improve the false-failover versus detection-delay Pareto frontier.

This is a falsification audit. It does not assert that either candidate is novel. Evidence is `[K]` when directly supported, `[E]` for a reported empirical result, `[C]` for the candidate hypothesis, `[GAP]` for unverified information, and `[KILL]` for a condition defeating the present claim.

## Claim under test

**C1 exact claim.** Given low-cost CO2 readings, temperature/RH/pressure where available, calibration age, and a residual model, a three-action policy reduces reference-labelled false-safe decisions relative to a calibrated point estimate plus fixed threshold and fixed-margin abstention, at fixed inspection rate.

**C3 exact claim.** Given heartbeat timing and local CPU, memory, I/O, and temperature signals, a fixed-compute three-way state machine improves false failovers and time-to-detect versus a static timeout and adaptive-percentile timeout, on held-out device/workload/fault combinations.

## Three-round novelty audit

| Candidate / round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| C1 - 1. Component collision | `[K]` Cai et al. combine low-cost SenseAir K30 units, a Picarro reference, environmental correction, long-term drift correction, and a 30-month field series (Secs. 3-6, pp. 4873-4879). Barrett and Mishra compare point-calibration models and evaluate time drift in a co-located low-cost NDIR deployment (Secs. I-IV, pp. 1-8). Russo et al. add a 2026 metrological calibration/uncertainty protocol for low-cost NDIR sensors (Secs. 1-4). | `[C]` The proposed action loss, inspection budget, and chronological selective-decision endpoint differ from point calibration. Components alone do not establish this as a contribution. | High collision; low confidence in residual difference. |
| C1 - 2. Exact-claim collision | No primary paper found in the audited 2024-2026 chain that exactly uses calibration age plus residual risk to choose `alert/no-alert/inspect` for an indoor ventilation decision. This is **not** novelty evidence. `[KILL]` More importantly, the supplied public artifact cannot evaluate that exact claim: it is an outdoor/urban co-location record, not classroom ventilation; the publicly inspected Picarro series has non-missing values no higher than 739.61 ppm, below common high-CO2 ventilation-action regimes. | A different, authorized indoor deployment with a traceable reference and predeclared action threshold could test the claim. Such a deployment, reference access, threshold authority, and ethical/operational permission are `[GAP]`. | High that current public-data experiment fails; unresolved for a new deployment. |
| C1 - 3. Boundary / impossibility | `[KILL]` Calibration age alone cannot identify a threshold error. The same age and corrected reading can arise with a benign sensor, a drifting sensor, or a changed indoor source/ventilation condition. If the reference is absent at decision time and no observable quality signal separates these cases, a policy cannot know whether an `inspect` is warranted. `[K]` Cai et al. show sensor-specific drift and environmental dependence, rather than a universal age-to-error relation (Secs. 5-8, pp. 4877-4881). | A limited empirical claim is identifiable only for the declared sensor type/site distribution and only against contemporaneous reference labels. It must report per-sensor, future-time calibration and risk rather than pooled random splits. | High logical risk. |
| C3 - 1. Component collision | `[K]` Pourreza and Narasimhan already study edge heartbeat timeouts under CPU overload, memory contention, disk I/O, cache thrashing, page faults, thermal signals, Pi 4B/Jetson Nano, and multiple workloads. Their related work explicitly names phi-accrual, Lifeguard, SafeTimer, and adaptive distribution/percentile-based detectors. `[K]` Lifeguard incorporates local-health awareness specifically to reduce false failure detection. | A fixed, transparent three-way state machine with pre-registered held-out device/workload/fault tests is not shown by the supplied direct neighbor to be identical. But substituting one resource-aware heuristic for another is not a claim distinction by itself. | High component collision; Amber for exact claim. |
| C3 - 2. Exact-claim collision | `[K]` The UCC 2025 paper's stated endpoint is exactly the timeout false-positive/detection-delay trade-off under resource stress, which C3 reuses. `[K]` Its 2026 forward citation, *EdgeStressBench*, makes reproducible resource-stress workload orchestration, injection, and system measurements an open-source artifact, including Pi and Jetson examples. `[KILL]` C3 cannot claim its stress harness, device matrix, or basic resource signatures as contribution. | A narrowly stated **boundary result** can remain different: whether any resource feature beats phi-accrual, percentile timeout, and a one-feature threshold under one public EdgeStressBench protocol, and where this fails to transfer. No paper in the bounded 2024-2026 primary chain inspected establishes that exact comparison. `[GAP]` bounded chain only. | High collision for broad detector/systems claim; medium for boundary pivot. |
| C3 - 3. Boundary / impossibility | `[KILL]` In an asynchronous observation model, a healthy service delayed by local contention and a fail-slow service can have identical local heartbeat/resource traces up to the action time. Any detector restricted to those traces makes the same action in both worlds. Hence no uniform correct three-way classifier is possible without an added observation (remote probe, redundant task, or cost-conservative delay). `[K]` phi-accrual uses heartbeat arrival distribution adaptively, and Lifeguard explicitly models the detector's own local health; these establish strong non-static baselines. | A conditional empirical distinction is testable: resource telemetry may add predictive value for a named fault process, workload, device, and horizon. It must be reported as conditional, not a universal reliability result. | High for the boundary; medium for empirical residual. |

**Novelty status:** C1 is `Red` in its current public-data/classroom form. C3 is `Amber` only as a negative/boundary study after the baseline and artifact requirements below; its broad "resource-informed detector" framing is `Red`.

## Assumption and identification audit

### C1

* `[KILL]` The public Figshare artifact for Cai et al. v3 contains two workbooks, each with Picarro plus three K30 columns. I inspected the OpenXML headers and values in memory: the files are `1-Picarro-SENSEIAP-Calib-Drift.xlsx` and `2-Picarro-SENSEIAP-Drifted.xlsx`; headers are reference/Picarro and `K30`, `K30_2`, `K30_3`. The required raw temperature/RH/pressure fields do not occur in these published tables. The data description says file 1 has environmental correction and drift calibration and file 2 has environmental correction without long-term drift calibration. Dataset metadata: https://doi.org/10.6084/m9.figshare.29310890.v3, version 3, posted 2025-06-13, CC-BY 4.0.
* `[KILL]` The reference series has 18,229 numeric rows after excluding blank cells but includes zero-valued missing/sentinel entries; its largest non-zero/observed value in the inspected column is 739.61 ppm. This cannot instantiate the candidate's classroom high-CO2 false-safe/ventilate story without inventing a lower operational threshold or synthetically changing labels.
* `[GAP]` The candidate presumes an `inspect` action and a calibration residual model can be executed at a facility. Who inspects, response time, inspection capacity, and threshold authority are not known. Without action cost, any method can reduce false-safe events by inspecting all cases.
* `[KILL]` Random train/test splits leak future calibration state. A valid test must keep whole later blocks and ideally whole physical sensors/sites untouched. With only three co-located K30s, sensor-level transfer is statistically fragile.

### C3

* `[KILL]` `healthy`, `resource-stressed`, and `fail-slow` are latent labels. CPU/RAM/I/O/temperature signals do not label the causal state by themselves. Fault injection must declare whether a delayed response still completes, whether the process is stopped, and the exact operational ground truth before a detector is evaluated.
* `[KILL]` Failover is a consequential action, not a classifier label. Evaluation must predeclare its cost: lost work/restart time, false-failover interruption, and delay to detect fail-stop or fail-slow. Reporting F1 alone cannot decide the stated Pareto claim.
* `[K]` Pourreza and Narasimhan's study already shows resource-stress effects vary by workload and device, so pooled random traces cannot establish cross-device transfer. Their official record states six workloads, five stressors, Pi 4B/Jetson Nano, and up to 30% fault-free false positives under static thresholds; moderate thresholds reduce no-fault positives by about 40-60% but can miss/slow genuine slowdowns (abstract and Secs. 1, 4-6; pp. 1-9). https://doi.org/10.1145/3773274.3774280
* `[GAP]` The exact protocol/code URL for UCC 2025 was not discoverable from the paper's official landing page. EdgeStressBench is an available downstream artifact, but its repository/artefact version, hardware dependencies, and whether it contains the UCC timeout detector are unverified in this round.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Cai et al., *A 30-month field evaluation of low-cost CO2 sensors using a reference instrument*, Atmos. Meas. Tech. 18, 4871-4884, published 2025-09-29, version of record. https://doi.org/10.5194/amt-18-4871-2025 | Three K30 units, BME environmental telemetry, Picarro reference; environmental correction, drift correction and periodic calibration. | Concentration bias/RMSE over 30 months; Secs. 3-6, pp. 4873-4879; long-term/seasonal drift Secs. 7-8, pp. 4879-4882; data availability p. 4882. | C1's low-cost CO2, calibration-age/drift, reference labels, and longitudinal setup. | `[KILL]` a calibration or periodic-correction contribution. Leaves only an action-loss protocol, but the supplied public data cannot test its classroom threshold story. |
| Barrett & Mishra, *Statistical Study of Sensor Data and Investigation of ML-Based Calibration Algorithms for Inexpensive Sensor Modules*, IEEE TIM 73, Art. 1003310, published 2024-03-18. DOI: https://doi.org/10.1109/TIM.2024.3372211; author version: https://research.aber.ac.uk/files/89972946/Statistical_Study_of_Sensor_Data_and_Investigation_of_ML-Based_Calibration_Algorithms_for_Inexpensive_Sensor_Modules_Experiments_From_Cape_Point.pdf | Co-located NDIR CO2 and site truth; RF/SVR/1D-CNN/1D-CNN-LSTM calibration; performance drift over time. | Calibration prediction and time drift, Secs. I-IV pp. 1-8; discussion/conclusion Secs. V-VI pp. 8-10. | C1's residual-model component. | `[KILL]` a new ML calibration model or drift predictor. Does not prove a three-action threshold decision is already studied. |
| Russo et al., *Metrological Characterization of Low-Cost CO2 Sensors for Environmental Monitoring Applications*, Sensors 26(12):3685, published 2026-06-09. https://doi.org/10.3390/s26123685 | Three SCD30 NDIR sensors, two reference analyzers, controlled 350-950 ppm dilution; calibration and uncertainty protocol. | Calibration RMSE/MAE, repeatability and uncertainty; Secs. 2-4, pp. 3-12; Sec. 5 pp. 12-13. Official full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC13306425/ | CO2 sensor reliability, reference comparison, environmental variables, and calibration uncertainty. | `[KILL]` a generic uncertainty/calibration claim. Its 350-950 ppm range is a useful warning that a real C1 needs a threshold-supporting reference dataset. |
| Pourreza & Narasimhan, *When Timeouts Fail: Revisiting Fault Detection under Resource Stress in Edge Computing*, UCC 2025, pp. 1-10, published 2025-12-01. https://doi.org/10.1145/3773274.3774280 | Pi 4B/Jetson Nano, six workloads, heartbeat timeouts, CPU/memory/disk/cache/page-fault stress and thermal signals. | Static timeout false positives, detection latency and resource costs; Secs. 1-2 pp. 1-3; related adaptive detectors Sec. 3 pp. 3-4; methodology/results Secs. 4-6 pp. 4-9; conclusion p. 10. | C3's scenario, signals, target trade-off, hardware class, and stress matrix. | `[KILL]` broad claim of discovering timeout brittleness, measuring resource signatures, or merely adding resource-aware adaptation. Leaves a strictly controlled comparative boundary result. |
| Dadgar, Phillips & Currey, *Lifeguard: Local Health Awareness for More Accurate Failure Detection*, arXiv:1707.00788, 2017. https://arxiv.org/pdf/1707.00788 | SWIM membership protocol uses local-health-aware probe and suspicion timeouts. | False positives and detection time in controlled and real settings; Abstract, Secs. 1-4, pp. 1-10. | Local resource/health signal to mitigate false failures. | `[KILL]` claims that local-health awareness itself is a new mechanism. Requires a like-for-like baseline despite older publication. |
| Pourreza & Narasimhan, *EdgeStressBench: A Framework for Reproducible Evaluation of Edge Systems Under Resource Stress*, MobiSys 2026 Workshops, pp. 300-306, published 2026-06-02. https://doi.org/10.1145/3812836.3814778; official bibliographic record: https://dblp.org/rec/conf/mobisys/PourrezaN26 | Parameterized stress injection, tracing, workload orchestration, system metrics; Pi and Jetson example. | Reproducibility framework and open-source artifact; Abstract/Sec. 1 pp. 300-301; framework/evaluation Secs. 3-5 pp. 302-305; conclusion p. 306. | C3's proposed experimental machinery and reproducible stress matrix. | `[KILL]` a testbed contribution. It is a mandatory starting artifact/baseline, not proof that C3's detector outcome is covered. |

## Strongest simple baseline

**C1.** Before any learned residual policy, compare all policies at the same inspection rate and same action horizon:

1. calibrated point estimate plus fixed threshold;
2. fixed time-since-calibration margin;
3. conformal/prediction interval or fixed-width interval plus `inspect` if it straddles the threshold;
4. periodic inspection at the same budget; and
5. always inspect / never inspect bounds.

`[KILL]` If fixed calibration-age margin or a prediction interval matches false-safe, false-alert, and delay on genuinely held-out future blocks, C1's residual model has no remaining contribution. The current public artifact cannot run this test for a classroom ventilation threshold.

**C3.** Compare under a matched action cost and at least one unseen device-workload-fault cell:

1. tuned fixed timeout;
2. adaptive percentile/ADR-type timeout;
3. phi-accrual detector;
4. Lifeguard/local-health-aware detector where the protocol topology permits it;
5. one-signal threshold (memory pressure alone, then CPU/I/O/thermal separately); and
6. remote-probe or redundant-task oracle upper bound, reported as unavailable at the edge rather than treated as a fair local baseline.

`[KILL]` If phi-accrual, Lifeguard, or one resource threshold reaches the same false-failover/detection-delay frontier with lower monitor overhead, the three-way state machine is eliminated. Static and percentile timeout alone are insufficient baselines because the direct neighbor already identifies stronger adaptive detector families.

## Contrarian result

**C1 is killed as stated.** The story is classroom/facilities ventilation, but its only confirmed public data are outdoor/urban, three co-located K30s and a Picarro reference; the inspected reference range does not reach a typical high-CO2 ventilation action region. It also lacks the exact raw environmental features promised by the claim. Reframing a 740 ppm outdoor value as a ventilation action would turn the story into an unverified convenience label. The honest pivot is a narrowly environmental measurement-quality analysis, not the stated harmful-decision claim.

**C3 must pivot away from a new detector/testbed claim.** The closest 2025 work already supplies the endpoint, hardware, stressors, and direct detector families; the 2026 forward citation supplies an open reproducibility harness. Its valuable residual is a pre-registered *boundary result*: under a stated stress/fault model, can any locally observable resource signal add value over phi-accrual and a single-signal rule, and does this transfer to an unseen device/workload? A no-transfer or one-signal-suffices result remains useful.

## Feasibility audit

| Requirement | C1 | C3 |
| --- | --- | --- |
| Public data/artifact | `[K]` CC-BY Figshare v3 data are downloadable, but `[KILL]` columns/scenario/range do not support the exact classroom selective-alert protocol. | `[K]` EdgeStressBench reports an open-source artifact and uses Pi/Jetson examples. `[GAP]` repository revision and exact compatibility with UCC's timeout protocol need verification before implementation. |
| Labels/identification | `[KILL]` Reference labels exist only in an outdoor co-location, not for the claimed room/ventilation decision; sensor-level held-out generalization has n=3. | `[K]` controlled fault injection can label process state if specified; `[KILL]` resource telemetry alone does not label the latent cause. |
| Hardware/compute | `[GAP]` A K30/SCD30, a traceable reference, controlled indoor location, and energy measurement access are unconfirmed. A valid real test requires the reference. | `[GAP]` Pi/Jetson access is unconfirmed. Compute is modest, but reproducing several stress/workload/device cells has a real time cost. |
| Ethics/operations | `[GAP]` Indoor facility monitoring and any action affecting occupants need permissions; do not issue live ventilation commands. | No personal data; controlled fault injection still needs isolation from production services and a manual abort. |
| Negative-result value | Weak for the stated C1 story because the required data/action setting is absent. | Strong: a measured no-transfer boundary or single-metric equivalence is a legitimate constrained characterization. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Cai data provide 30-month co-location, environmental correction, drift correction, and public reference/K30 records. | `[K]` | Cai et al., AMT version of record, 2025-09-29, https://amt.copernicus.org/articles/18/4871/2025/amt-18-4871-2025.pdf; Figshare v3 https://doi.org/10.6084/m9.figshare.29310890.v3 | Abstract p. 4871; Secs. 3-8, pp. 4873-4882; data availability p. 4882; official dataset metadata inspected 2026-08-28. | Environmental/urban co-location, not indoor ventilation. |
| Cai public tables lack the C1 raw T/RH/pressure inputs and reference maximum is 739.61 ppm. | `[KILL]` | Official Figshare v3 artifact above, files 55356986 and 55356992, CC-BY 4.0. | Workbook header/value inspection on 2026-08-28; headers and range recorded in Assumption audit. | Zero/missing coding requires data cleaning; maximum claim is for inspected reference column, not a calibrated classroom concentration. |
| NDIR calibration and drift-model components have direct recent neighbors. | `[K]` | Barrett & Mishra, IEEE TIM 2024, DOI and author PDF above; Russo et al., Sensors 2026, DOI and PMC full text above. | Barrett Secs. I-IV pp. 1-8, V-VI pp. 8-10; Russo Secs. 1-5 pp. 1-13. | These papers do not by themselves evaluate C1's inspection policy. |
| Edge timeout detection under resource stress already uses C3's device class, resource signals, and decision trade-off. | `[K]` | Pourreza & Narasimhan, UCC 2025, https://doi.org/10.1145/3773274.3774280 | Official full-text record: Abstract; Secs. 1-6, printed pp. 1-9; article p. 10 conclusion. Publisher PDF page rendering was not downloadable in this audit. | Printed page/section mapping should be rechecked against downloaded CC-BY PDF before a paper claim. |
| C3 has a newer reproducibility-artifact collision. | `[K]` | EdgeStressBench, MobiSys Workshops 2026, https://doi.org/10.1145/3812836.3814778; https://dblp.org/rec/conf/mobisys/PourrezaN26 | Abstract/Sec. 1 pp. 300-301, framework/evaluation Secs. 3-5 pp. 302-305, conclusion p. 306, from official indexed metadata/abstract. | Exact repository URL/version not verified. |
| The forward chains contain recent cited work but do not certify absence of an exact collision. | `[K]` / `[GAP]` | OpenAlex records retrieved 2026-08-28: Cai `W4414611682`; UCC `W7117768918`; Barrett `W4392399436`. APIs: https://api.openalex.org/works?filter=cites:https%3A%2F%2Fopenalex.org%2FW4414611682 and https://api.openalex.org/works?filter=cites:https%3A%2F%2Fopenalex.org%2FW7117768918 | Cai chain returned 9 records, including Russo 2026; UCC chain returned EdgeStressBench 2026. | Citation databases are incomplete/dynamic. No absence claim is made. |

## Queries and failed searches

Queries executed 2026-08-28:

* `"sensor health" edge "fallback" reliability machine learning 2024`
* `"risk-aware" edge sensing "abstention" 2025`
* `"adaptive sampling" "sensor quality" edge 2024 2025`
* `"missing modality" "edge" sensor "reliability" 2024`
* `"When Timeouts Fail" edge devices Pourreza Narasimhan`
* `"3773274.3774280"`
* `"resource informed" "failure detector" "edge" 2024`
* `"adaptive timeout" "resource" "edge computing" 2024 2025`
* `"phi accrual" resource contention heartbeat timeout edge`
* `"Lifeguard" failure detector resource utilization timeout`
* `"EdgeStressBench" github` and `"EdgeStressBench: A Framework" artifact`
* `"A 30-month field evaluation of low-cost CO2 sensors" cited by 2026`
* `"low-cost CO2" "alert" "abstention" calibration`

Failed/limited searches:

* No official C1 paper was found that exactly implements calibration-age-aware `alert/no-alert/inspect` for classroom ventilation. This is `[GAP]`, not evidence of novelty.
* No accessible UCC 2025 PDF or public source-code link was obtained from the DOI landing page; section/page details rely on the official full-text record and cited metadata. `[GAP]`.
* No repository revision/DOI artifact archive for EdgeStressBench was verified. `[GAP]`.
* OpenAlex forward-citation retrieval is bounded to its indexed records on the stated date; it cannot establish a global absence result.

## Decision

**PIVOT**

**C1: KILL.** Its public data, observable variables, value range, and outdoor setting do not support the exact classroom false-safe/inspection claim. Do not promote it unless an authorized indoor reference deployment and an action-cost protocol are independently confirmed; that would be a new candidate, not validation of this one.

**C3: PIVOT/HOLD.** Do not promote a new detector or stress-testbed claim. It may continue only as an Amber boundary study using the current 2025/2026 artifacts and all six baseline families, with a pre-registered cross-device/workload/fault split. Kill it if phi-accrual, Lifeguard, or one resource signal matches the claimed frontier.

PIVOT
