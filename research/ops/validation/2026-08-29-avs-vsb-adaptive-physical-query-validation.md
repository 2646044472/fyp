# Validation Audit: 2026-08-29 AVS and VSB

## Decision investigated

Whether the divergence packet's two Amber candidates are sufficiently distinct and identifiable to enter the next gate:

- **AVS:** support-gated `virtual / wake-and-read / unknown` control for an intermittently active environmental sensor.
- **VSB:** after an ambiguous vibration window, choose two motor speeds to distinguish mechanical trend from an attachment/measurement change.

This is a red-team audit, not a novelty finding.  I read the current charter, active register, validation instructions, and the 2026-08-29 divergence packet before searching.  I searched original/official sources on 2026-08-29; a source whose full text or pages were not obtainable is marked `[GAP]` rather than used to establish an exact claim.

## Claim under test

AVS claims that a frozen support predicate based on companion observations, recent physical observations, and time since last physical read can improve the error--energy--unknown frontier over fixed dormancy and periodic sensing.

VSB claims that an ambiguity-conditioned pair of speed queries can improve the distinction between true mechanical trend and bad accelerometer attachment over fixed-speed/fixed-pair/longer-passive baselines.

## Three-round novelty audit

| Candidate and round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| AVS: component collision | Marinov et al. already combine a low-power continuously operating sentinel with selective activation of a high-power sensor, variation-triggering, schedule control, energy/fidelity evaluation, and fixed-schedule/continuous baselines. WONS 2026 already intentionally deactivates a target sensor and reconstructs its value from target history plus correlated companions on an ESP32. | AVS names a frozen *support* predicate and `unknown`; the inspected sources use variation-triggering/scheduling and report fidelity rather than this tri-state output.  That is a policy parametrization, not yet a distinct mechanism. | High collision; no positive novelty inference. |
| AVS: exact-claim collision | Marinov et al.'s stationary discrete-node case has independently controllable sensing elements, a continuously active low-power sentinel, selective high-power particulate-matter activation based on variation plus schedule, and continuous/fixed/adaptive comparisons.  This matches task, observation family, action family, energy constraint and fidelity endpoint closely. | The source's coordinator/digital twin differs from an on-node support predicate.  The divergence packet supplies no reason that moving threshold logic on-node changes the decision problem or endpoint. | High. |
| AVS: boundary/impossibility | With observations `(x_t, h_t, d_t)`, two physical worlds can have the same companion/history values but different current target value.  Before a completed physical read, every support predicate takes the same action in both worlds.  A predicate can only trade wake frequency against virtual/unknown error; it cannot certify transfer across relationship breaks. | A bounded, explicitly empirical held-out-cell result is testable if a continuously logged, separately calibrated reference is available.  It would be an application/replication result, not a general reliability claim. | High for the boundary; reference independence remains `[GAP]`. |
| VSB: component collision | Controlled multi-speed vibration measurement, sensor-mount effects, and low-cost MEMS self-detection of loose mounting already exist.  Karumanchi et al. use a MEMS accelerometer, controlled loose fixtures, a laser reference, and classifiers to distinguish secure from loose mounting.  Juzek and Slowinski empirically show that mounting changes vibration parameters and can falsify the apparent condition. | Neither retrieved primary paper was verified to choose a two-speed *adaptive* query after an ambiguous first window and score the particular `trend / measurement-uncertain / inspect` triage.  Failed retrieval is not novelty evidence. | Medium-high collision; exact action remains `[GAP]`. |
| VSB: exact-claim collision | The closest mounting paper directly targets the same competing explanation that VSB calls `attachment/measurement uncertain`: can the accelerometer determine whether its own fixture is loose?  Its single-feature resonance baseline is especially relevant. | The official record exposes abstract-level method/results but not the full six pages; exact selection protocol and all baselines are `[GAP]`.  Therefore this audit does not assert an exact protocol collision. | Medium. |
| VSB: boundary/impossibility | For one accelerometer, let the observed feature vector at speed `r` be `z(r) = H_m(r) S_f(r) + e`, where `m` is mount/attachment state and `f` is mechanical state.  With unknown speed-dependent mount transfer `H_m` and mechanical spectrum `S_f`, two queried speeds supply only two products; different `(m, f)` pairs can yield the same pair.  The divergence packet's own counterexample admits this.  Labels in a finite mount/load grid do not identify the causal factor outside that grid. | A finite, preregistered *indistinguishability map* is testable and valuable.  It must be reported as a boundary measurement, not as a mechanism that separates mounting from mechanical state in general. | High. |

## Assumption and identification audit

### AVS

1. **Evaluation truth is not specified.** A woken low-cost target sensor cannot automatically serve as independent truth for whether a preceding virtual value was out of tolerance.  AVS needs a continuously logged, separately calibrated reference and a clocked alignment/warm-up rule.  A second cheap sensor without a calibration/independence argument is not enough. `[GAP]`
2. **Wake is not instantaneous by definition.** The proposed evaluation treats a `wake/read` as an action.  Its sensor-specific start-up, stabilization, inclusion time, and energy must be measured and frozen.  Neither the AVS packet nor the inspected WONS protocol establishes those values for the eventual BOM. `[GAP]`
3. **Tri-state output does not remove the selective-label problem.** Physical truth is observed more often where the policy wakes.  Counterfactual virtual-error estimates for no-wake periods require the independent reference; otherwise a policy can appear reliable by labeling hard episodes `unknown` or by never observing its misses.

### VSB

1. **Two speed windows do not identify causal source.** The multiplicative counterexample above applies even with noiseless observations.  A policy could learn a class boundary for an enumerated fixture/mass grid, but cannot establish that it has separated physical mechanism from attachment without an extra observation, e.g. a calibrated reference accelerometer, mount-torque/fixture measurement, or independently measured motor excitation. `[KILL]` for the general separation wording.
2. **The proposed initial ambiguity trigger is post-selection risk.** The same first window selects both which episodes receive adaptive speed pairs and the policy's action.  Calibration, policy selection, and target evaluation must be split by whole fixture/load/day blocks; otherwise a search over speed pairs and features will select the apparent gain. `[GAP]`
3. **"Added eccentric mass" is not a generic fault ground truth.** It is an engineered imbalance condition.  The honest endpoint is recognition of an enumerated bench condition, not diagnosis of a motor fault or general maintenance trend. `[KILL]` for broader framing.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Marinov et al., *Digital-Twin-Assisted Adaptive Sensor Scheduling for Energy Optimization in Battery-Powered Indoor Air Quality (IAQ) IoT Nodes*, Electronics 15(11):2395, 2026 | Low-power continuous measurements plus high-power sensor state; continuous, fixed, clustering schedule, and variation-triggered selective activation. | Battery/energy and measurement-fidelity comparisons for mobile and stationary IAQ nodes; discrete-node case has a sentinel plus independently controlled high-power PM sensor. | AVS's task/action/constraint/endpoint family. | **KILL AVS as a generic support-gated wake contribution.** On-node versus central logic and `unknown` require a materially new observation/guarantee, not a changed threshold. |
| Attarha and Forster, *Sensing Without Sensing*, WONS 2026 | Target history plus correlated active sensors reconstruct readings while target is intentionally inactive; calibration fixes a maximum dormant phase. | Error versus dormancy and energy on ESP32 environmental deployments. | AVS virtual reading, companion observations, intentional deactivation, calibration and low-cost edge deployment. | Kills virtual-sensing, ESP32, companion-correlation, and fixed-dormancy components; leaves only a narrowly defined online abstention question. |
| Karumanchi et al., *Self-Detection of Mounting Looseness with a MEMS Accelerometer*, SSI 2025 | MEMS features/resonance to distinguish secure vs loose fixture, with controlled looseness and laser-vibrometer validation. | Mounting-integrity classification, including cross-material generalization. | VSB's attachment-versus-real-signal concern and low-cost MEMS bench setting. | Kills a generic "use vibration to tell loose mounting from valid signal" contribution.  Exact two-speed adaptive protocol is not verified from the unavailable full paper. |
| Juzek and Slowinski, *The impact of accelerometer mounting on the correctness of the results obtained in NDT-type tests*, Transport Problems 19(1), 2024 | Compare cyanoacrylate, magnet and wax mounts over more than 90 recorded time series. | Time/spectral parameters and information capacity under different mounts/axes. | Direct measurement-confounding premise for VSB. | Supports the counterexample: mount can alter apparent condition.  Does not itself test speed-pair selection. |
| Hummel, Hix, and Cardenas, *Mounted Accelerometer Frequency Response of Adhesive Products and Aluminum Frame Quick Mounts*, Vibration 8(4):61, 2025 | Mount method and sensor mass; sinusoidal excitation and a stud-mounted reference. | Frequency response and error threshold relative to a reference. | Speed/frequency dependence of mount transfer function. | Makes an unreferenced one-accelerometer causal-separation claim implausible; it leaves a multi-reference boundary study open. |

## Strongest simple baseline

For **AVS**, reproduce Marinov et al.'s frozen variation-trigger and fixed schedule on the same physical node, include always-on, then let `unknown` abstain whenever the proposed support test abstains.  Unless the on-node predicate improves an independently referenced error--energy--coverage frontier with all thresholds frozen before target cells, there is no contribution beyond a decision-rule substitution.

For **VSB**, use either (a) the strongest fixed two-speed pair selected only on calibration cells, or (b) a passive equal-byte trace, plus the resonance-only mount-integrity rule in Karumanchi et al.  If either matches the adaptive pair under target fixture/load blocks, the proposed policy is eliminated.  In either case, a colocated reference accelerometer is the minimal check needed before interpreting an error as mechanical rather than attachment-related.

## Contrarian result

The adverse result is constructive but narrower than either candidate's original positive story:

- **AVS:** a fixed schedule or variation trigger reaches the same independently referenced frontier.  This would show that online support gating is not justified for the selected hardware/relationship-break cells.
- **VSB:** map cells in which secure-mount/changed-load and loose-mount/nominal-load produce overlapping two-speed observations.  This is a reproducible **measurement-limit** result, but it is not evidence that an adaptive policy can diagnose which cause is true.

## Feasibility audit

| Candidate | Status | Evidence and constraint |
| --- | --- | --- |
| AVS hardware/demo | **HOLD only as replication/control, not mechanism thesis** | ESP32 and low-/high-power environmental components are plausible and WONS used ESP32/SCD30/DHT11.  But independent truth, sensor wake/stabilization, energy instrument, target thresholds, and whether the selected physical sensor can be switched independently remain `[GAP]`.  The current 2026 demo deadline is realistic for a narrow replication, not for establishing a distinct contribution after the direct collision. |
| AVS ethics/data | Feasible in a non-personal bench/empty room. | Do not attach health or ventilation-control claims to records from an unvalidated low-cost reference. |
| VSB hardware/demo | **PIVOT only** | A guarded low-voltage motor, fixture and MEMS IMU can be bought; however a repeatable torque/attachment ground-truth fixture, speed feedback, physical guard, and reference accelerometer are needed.  Low-cost mounting self-detection already exists, and an added mass is only a bench label. |
| VSB time/compute | Feasible for a finite boundary map. | It is not feasible to justify a general mechanical-diagnosis claim from one motor and a finite set of mounts/loads.  The honest output is an explicitly bounded experimental map. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| 2026 IAQ work dynamically schedules high-power sensing using continuous sentinel information, variation-based triggering, fixed schedules, energy/fidelity comparisons, and a discrete sentinel-plus-selective-sensor case. | [KILL] | Marinov, Feradov, Abu-Alam, and Shabanski, *Digital-Twin-Assisted Adaptive Sensor Scheduling for Energy Optimization in Battery-Powered Indoor Air Quality (IAQ) IoT Nodes*, Electronics 15(11):2395, published 2026-06-01. Official DOI: https://doi.org/10.3390/electronics15112395 ; official PDF: https://mdpi-res.com/d_attachment/electronics/electronics-15-02395/article_deploy/electronics-15-02395.pdf | Abstract; Secs. 2.5-2.7 (strategies/decision/case mapping), 3.4 (discrete node), 4.3-4.4 (hybrid result and implications), inspected from official XML/PDF on 2026-08-29.  Article number has no stable printed page range in the retrieved record. | Direct collision with generic AVS; paper uses a central digital twin and variation/schedule logic, so it does not prove every on-node policy identical. |
| WONS 2026 intentionally deactivates target environmental sensors, reconstructs readings from target history and correlated companions, calibrates maximum inactive period, and demonstrates ESP32 deployment. | [K] | Attarha and Forster, *Sensing Without Sensing: Energy-Efficient Virtual Sensing for IoT-Based Environmental Monitoring*, WONS 2026, ISBN 978-3-903176-79-9, official IFIP PDF: https://dl.ifip.org/db/conf/wons/wons2026/1571220625.pdf | Abstract, printed p. 25; Sec. II, printed pp. 25-27; Sec. III, printed pp. 27-28; conclusion, printed p. 28. | It is not an exact online support-gated abstention protocol. |
| WONS's calibration is limited to 21 training days and at most seven assessed dormancy days; it treats seven days as its safe upper bound and reports increasing error with dormancy. | [E] | Same WONS 2026 official PDF. | Sec. III, printed p. 28, paragraph beginning "For both experiments" through Table I. | This limits that experiment; it is not proof that AVS's policy is novel or necessary. |
| A 2025 original SSI paper directly investigates a MEMS accelerometer's ability to classify its own mounting looseness from controlled secure/loose fixtures and laser-vibrometer reference, including material generalization. | [K] | Karumanchi et al., *Self-Detection of Mounting Looseness with a MEMS Accelerometer*, 2025 Smart Systems Integration Conference and Exhibition, pp. 1-6, 2025-04-08, DOI: https://doi.org/10.1109/SSI65953.2025.11107198 ; official Fraunhofer record: https://publica.fraunhofer.de/entities/publication/13369faf-ea98-40eb-ad8b-3473afbca6b4 | Official record abstract and metadata, inspected 2026-08-29. Full IEEE pages were not accessible: exact section/page content is `[GAP]`. | Strong component/direct-task neighbor, not an asserted exact collision with speed-pair action. |
| Mounting method changes measured vibration parameters and may falsify the apparent physical condition. | [K] | Juzek and Slowinski, *The impact of accelerometer mounting on the correctness of the results obtained in NDT-type tests*, Transport Problems 19(1):97-105, 2024, DOI: https://doi.org/10.20858/tp.2024.19.1.08 ; official index record: https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-7fffa836-f057-411a-9bec-299992a0cefb | Official abstract/metadata. Publisher full text was CAPTCHA-blocked; section/page details are `[GAP]`. | Supports confounding premise only. |
| Mount techniques change accelerometer frequency response and measurement accuracy; the study uses a stud-mounted reference and sinusoidal excitation. | [K] | Hummel, Hix, and Cardenas, *Mounted Accelerometer Frequency Response of Adhesive Products and Aluminum Frame Quick Mounts*, Vibration 8(4):61, 2025, DOI: https://doi.org/10.3390/vibration8040061 ; official article: https://www.mdpi.com/2571-631X/8/4/61 | Abstract, Sec. 2.3 and Sec. 4 as indexed on the official article, inspected 2026-08-29. Full rendered article intermittently returned HTTP 429; page-level verification is `[GAP]`. | It establishes a speed/frequency-sensitive nuisance transfer, not a formal lower bound by itself. |
| One accelerometer at two speeds cannot generally identify mount versus mechanical state when both are unknown speed-dependent transfer factors. | [KILL] | Algebraic counterexample stated in this audit; no external source required. | Assumption and identification audit above. | This is a model-class boundary. It does not rule out a finite, labelled classifier or a design augmented with an independent reference. |

## Queries and failed searches

- `"virtual sensing" "wake" sensor scheduling edge 2024 2025 paper`
- `"Digital-Twin-Assisted Adaptive Sensor Scheduling" Marinov full text`
- `"active sensing" vibration "speed" fault diagnosis 2024 2025 paper`
- `"Adaptive sensor scheduling" "virtual sensing" 2025 IoT`
- `accelerometer mounting condition effect vibration measurements frequency response paper 2024 2025`
- `vibration sensor attachment looseness fault diagnosis indistinguishable sensor mounting mechanical fault study`
- `"Self-Detection of Mounting Looseness with a MEMS Accelerometer" PDF DOI`

The 2026 Marinov paper was retrieved as official MDPI XML/PDF after the publisher HTML returned HTTP 429.  The SSI 2025 full paper and Juzek 2024 full text were not accessible in this pass, so their exact sections/pages are explicitly unresolved.  Searches did not establish absence of a speed-pair method and must not be read as novelty evidence.

## Decision

**PIVOT.**  Mark **AVS as KILL** for a mechanism thesis: a 2026 primary paper already occupies the low-power-sentinel, selective high-power sensing, adaptive-trigger/schedule, energy--fidelity frontier; `support` and `unknown` are currently an insufficient decision-rule variation.  It may remain only as a reproduction/control.

Mark **VSB as PIVOT**, not PROMOTE: an honest FYP could map where two fixed/adaptive speed measurements fail to distinguish enumerated mount/load cells, using an independent reference.  Do not claim a general separation mechanism or maintenance diagnosis.  A speed-pair policy should not advance without first beating the fixed-pair/resonance baseline under blocked target cells and adding an independent observation that breaks the mount--mechanics confounding.

PIVOT
