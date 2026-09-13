# Validation Audit: 2026-08-28 D1 and D2 self-purchased ToF bench candidates

## Decision investigated

Whether D1 (condition-aware trustworthy ToF clearance) or D2 (action-conditioned active self-test) can pass a direct-neighbor, identifiability, and self-purchased-bench feasibility gate. This is a falsification pass, not a novelty search. It reads the active charter/register and the divergence packet. It does not assess historical candidate E.

## Claim under test

- **D1:** A calibrated `clear / uncertain` policy using VL53L5CX per-zone range/status plus condition features can meet a declared held-out false-clear target across unseen material--lighting--angle cells, when a distance threshold cannot.
- **D2:** At equal interruption/energy budget, a risk-triggered servo reference-target self-test reduces false-safe decisions over passive residual/status, startup wait, and periodic testing for predeclared proximity-sensor faults.

Neither candidate may claim a real functional-safety certification: the proposed rig only drives an LED or simulated stop and is not a certified safety channel.

## Three-round novelty audit

| Candidate / round | Evidence for collision | Evidence for a remaining distinction | Confidence |
| --- | --- | --- | --- |
| D1 component collision | Caroleo, Albini, and Maiolino (2026) characterise the same VL53L5CX family under lighting, material, range, orientation, drift, and status outcomes. Conformal Risk Control (CRC) already post-processes a predictor into a monotone-risk-controlled set-valued output. | The characterisation paper does not evaluate a `clear / uncertain / inspect` policy, while CRC is modality-agnostic. This is an application gap, not a new component. | High collision; no novelty inference. |
| D1 exact-claim collision | The ST datasheet supplies a manufacturer-status / threshold baseline; SuperBat (2024) already uses VL53L5CX for resource-constrained obstacle avoidance in transparent/reflective environments. | Within the bounded queries below, I did **not** verify a primary paper with the exact single-sensor, held-out condition-cell false-clear / inspection frontier. Absence is [GAP], not distinction evidence. | Medium; audit incomplete. |
| D1 boundary / identifiability | CRC's guarantee explicitly requires exchangeable loss functions and a loss non-increasing with its conservativeness parameter; it also gives a counterexample for non-monotone losses. Holding out whole material--light--angle cells violates the ordinary exchangeability story. | A pre-registered *finite-family empirical rate* or binomial interval is identifiable if each deployment cell is sampled independently by object/setup, not by correlated frames. It cannot become a claim about arbitrary unseen materials. | High. |
| D2 component collision | An official SICK optoelectronic-safety-device patent describes periodic self-tests using defined-reflectance reference targets and functional monitoring; SNRepair already treats bias, drift, complete failure, and precision degradation with diagnosis/self-calibration. Active fault diagnosis also formalises diagnostic actions chosen to resolve ambiguity. | The candidate's moving cheap reflector and equal joule/interruption comparison are more specific, but this is a test protocol combination, not a demonstrated new mechanism. | High collision. |
| D2 exact-claim collision | The official patent's reference-target self-test has the same physical principle: failed/incorrect reference detection implies a sensor fault and triggers a safe output. | I did **not** verify an exact 2024--2026 primary paper with a servo-moved reflector, VL53L5CX, and false-safe-at-equal-energy endpoint. That missing exact hit is [GAP], never novelty. | Medium. |
| D2 boundary / identifiability | A reference ray can pass while the monitored envelope has an occupancy-dependent blind spot; a good self-test response therefore does not identify the false-safe rate for dark, transparent, thin, or off-axis objects. A frozen I2C value is identifiable by age/stream-count watchdog without a servo. | The protocol can identify detection of only a finite, explicitly injected fault family, provided the test target and fault injection are independently verified. It cannot support a generic `safe-to-close` conclusion. | High. |

## Assumption and identification audit

### D1

**[KILL] Unseen-cell coverage is not identified from the proposed split.** Let `x` contain 64-zone range/status plus light, temperature, age, and motion summary, and let `y` be `clear` or `occupied`. If an occupied thin/transparent/off-axis target and a clear scene can produce the same `x`, no local decision rule can separate their labels. Data from other material--light--angle cells do not determine the error rate in that cell. A held-out cell is deliberately non-exchangeable with calibration data; CRC's ordinary result instead assumes an exchangeable collection of loss functions and a loss monotone in conservativeness (Angelopoulos et al., 2024, Sec. 1.1, Eqs. 3--4; Sec. 2.4, Eq. 16).

**[K] Manufacturer tests do not give the desired environmental guarantee.** The official VL53L5CX datasheet conditions its range characterisation on targets filling the FoV, only 17% and 88% Munsell targets, nominal 23 C, and a 90% detection-rate criterion; it explicitly says the remaining measurements may be outside specification (DS13754 Rev. 13, Sec. 7.2.1, p. 20). This directly prohibits treating status-valid readings as a safety certificate for the proposed object family.

**Permissible pivot.** Freeze a finite deployment family before collection, block by object and physical setup, report `false clear` and `inspect` rates with intervals per cell, and call the result a *measured boundary map*. It must not promise distribution-free or unseen-material coverage. A test-set scan over thresholds or learned feature policies also needs a calibration/test split at the **object/setup** level, not at the frame level.

### D2

**[KILL] Passing a self-test is not a sufficient observation for scene safety.** Denote a reference-test result by `r`. A single fixed reflector tests only one optical geometry. If `(x, r)` has the same distribution for a healthy sensor facing the reference target and a contaminated/misaligned sensor that still sees the target but misses part of the protected envelope, the false-safe risk cannot be identified from `r`; a model cannot restore missing information. The SICK patent itself treats reference targets as one measure among redundant/diverse evaluation, contamination monitoring, watchdogs, and architecture (DE102021103952A1, description paras. [0003]--[0005], [0016]--[0028]).

**[KILL] Fault labels are intervention labels, not evidence of operational prevalence or coverage.** Diffuser cover, frozen values, fixed offset, and warm-up are acceptable scripted bench interventions only. Unless each is linked to a distinct observable response and every claimed scenario is sampled, a score over these injected cases estimates only the protocol's artificial fault distribution. It does not demonstrate protection from unmodelled/common-cause failures.

**Simple baseline likely removes the main mechanism.** Pre-register and compare these before building any learned/risk-triggered policy:

1. manufacturer `target_status`, target count, range threshold, and `invalid or stale => uncertain`;
2. frame sequence/age watchdog plus I2C error counter for stale/frozen-output faults;
3. fixed warm-up exclusion using the vendor-recommended initialisation/power sequence;
4. periodic static reference-target check at the same test rate; and
5. a passive background residual where the background is known.

For a frozen-bus fault, (2) should dominate a moving reflector in cost and delay. For an optical fault that changes the reflector response, (4) directly tests whether event-triggering adds anything over equal-rate periodic testing. If either baseline equals the proposed false-safe / false-inspect frontier, D2 is killed as a mechanism.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Caroleo, Albini & Maiolino, *Sensors* 2026 | Three VL53L5CX sensors, ambient-light sensor, thermistor; controlled variations in time, illumination, material, range, and orientation. | Measurement error/reliability characterisation, including status/rejected measurements. | D1's sensing conditions and hardware family overlap; no action policy endpoint. | Kills treating condition features or a new failure map as novel. Leaves a tightly measured decision-boundary study only. |
| STMicroelectronics, VL53L5CX DS13754 Rev. 13 (Sep. 2024) | 8x8 ToF, low-power host wake threshold, motion indicator; defined test conditions. | Device characterisation and operating specification. | Supplies direct `status + threshold + invalid=>uncertain` baseline. | Requires D1 to beat this simple baseline and forbids extrapolation beyond its conditions. |
| Angelopoulos et al., ICLR 2024, *Conformal Risk Control* | Calibration labels; set-valued/post-processed decision controlled by a monotone parameter. | Expected bounded risk on a new exchangeable point. | D1's abstention / false-clear calibration component. | Kills a generic set-valued/conformal methodological claim; exposes exchangeability and monotonicity prerequisites. |
| Kalenberg et al., *SuperBat*, IEEE ISSE 2024 | VL53L5CX plus ultrasonic, lightweight onboard obstacle avoidance on a nano-UAV. | Reliability in unexplored indoor environments with transparent/reflective obstacles. | Same low-cost ToF reliability story, but different fusion/action/evaluation. | Kills generic low-cost-ToF robust-obstacle-avoidance framing; leaves single-sensor decision-boundary comparison [GAP]. |
| Jachmann et al. / SICK, DE102021103952A1 (published 2022; official patent record) | Optical receiver, defined-reflectance reference targets, periodic self-test; watchdog/redundant processing. | Detect failures and force safety-related output in optical safety devices. | D2's physical reference-target self-test principle. | Kills reference-target self-test as D2's contribution and demonstrates why one test is only a component of a broader safety architecture. |
| Sinha & Das, *IEEE Sensors Journal* 2023, SNRepair | Historical healthy data; DRL fault diagnosis and self-calibration for bias/drift/complete failure/precision degradation. | Fault type classification and calibration. | D2's generic failure-family diagnosis. | Kills generic sensor-fault-diagnosis / calibration contribution; full paper details were inaccessible in this pass [GAP]. |
| Al Saati et al., *Science Robotics* 2024, s-FEAST | Diagnostic actions selected for informative observations under safety constraints. | Active estimation/isolation of ambiguous sensor/actuator faults in a spacecraft simulator. | D2's generic “risk-trigger diagnostic action” component. | Kills any generic active-diagnosis scheduling claim; application/actuation remains different. |

## Strongest simple baseline

For both candidates, the strongest required baseline is the frozen conservative controller:

```text
if frame_age exceeds deadline or I2C/stream status fails: uncertain
else if any protected-zone status is invalid: uncertain
else if min_valid_range <= clearance_threshold: uncertain/occupied
else: clear
```

For D2, add a static fixed-rate reference check and a frame-age watchdog. The proposed D1/D2 policy must be tuned only on a training/calibration set, run once on held-out object/setup blocks, and compared at a matched inspection/test-rate and externally measured joule budget. If it does not improve the false-clear / interruption frontier with uncertainty intervals, it has no remaining mechanism claim.

## Contrarian result

- **D1: PIVOT, not PROMOTE.** The hardware and story are feasible, but the headline must change from a set-valued rule with coverage across unseen cells to a finite-condition *empirical reliability-boundary protocol*. A positive learned-policy result is not defensible unless it beats the status/threshold baseline on pre-held-out objects/setups. A null result is useful: it would show the vendor-status baseline is enough, or that no low-inspection `clear` decision is identifiable in the declared family.
- **D2: KILL as proposed mechanism; PIVOT only as a measurement appendix.** Reference-target testing and active fault diagnosis are already established components, while its self-test response does not certify the envelope. The only defensible residual is a small, explicitly non-safety **fault-coverage characterisation**: which injected failures are noticed by status/watchdog/periodic reference checks, and which remain indistinguishable. That result should be a D1 feasibility/control appendix, not an independent thesis direction.

## Feasibility audit

| Requirement | D1 | D2 |
| --- | --- | --- |
| Self-purchase | [K] The user confirms affordable components can be bought. ST lists the chip as active/in-volume-production; an off-the-shelf VL53L5CX breakout is available, but the exact board/vendor/delivery are [GAP]. | Adds only a micro-servo and fixed reference target, so physical purchase is plausible; exact mount/repeatability/energy instrument remain [GAP]. |
| Data / labels | [K] Fully local object episodes can use a fixed rail position or an independent external reference only for offline labels. No human subject is necessary. | [K] Scripted interventions and commanded reference position are collectable; [KILL] they label only injected fault families, not operational failure coverage. |
| Ethics / harm | [K] LED or simulated stop only is low risk; no real lock, conveyor, or safety interlock may be controlled. | Same. Servo pinch points need a simple guard and low torque. |
| Compute / time | [K] Status/threshold/logistic rules and blocked binomial analysis run on a laptop/Pi-class host. [GAP] FYP deadline/effort remain unconfirmed. | [K] Finite-state baseline is inexpensive. A learned scheduler is unjustified before the simple-baseline test. |
| Power measurement | [GAP] An inline USB meter may lack timing/resolution for short ToF/servo events. Measure repeated fixed-duration batches with a verified instrument; report meter resolution and variance. | [GAP] Servo inrush and separate supply can invalidate a single USB-port joule claim. Meter the servo supply or exclude energy from the research endpoint. |

## Evidence ledger

| Claim | Label | Primary / official source and version | Exact section/page read | Scope / caveat |
| --- | --- | --- | --- | --- |
| VL53L5CX performance changes with illumination, material, range, orientation, and rejected/status outcomes; dark targets can cause degraded/unreliable results. | [K] | Caroleo, Albini & Maiolino, “On the characterisation of the time-of-flight VL53L5CX sensor ...”, *Sensors* 26(5):1639, version of record 2026-03-05: https://doi.org/10.3390/s26051639 ; official repository: https://ora.ox.ac.uk/objects/uuid%3Ae18c43e0-042c-4b46-a0c0-bb3e2e07497e | Secs. 3.4--3.7 and conclusion, pp. 8--15 in VOR; Sec. 3.6/3.7 text was independently visible in the official PMC mirror. | Controlled manipulator rig; not an action-risk or safety claim. |
| Vendor characterisation assumes full-FoV 17%/88% targets, nominal 23 C, 90% detection rate; remaining measurements may be outside specification. | [K] | STMicroelectronics, *VL53L5CX Datasheet*, DS13754 Rev. 13, Sep. 2024: https://www.st.com/resource/en/datasheet/vl53l5cx.pdf | Sec. 7.2.1, p. 20; note immediately below Table criteria. | Strong reason not to extrapolate vendor performance to the bench's arbitrary targets. |
| The device exposes low-power threshold wake, motion indication, and a known power state machine. | [K] | ST DS13754 Rev. 13, above. | Features p. 1; Secs. 3.1--3.3, pp. 8--10. | Establishes feasibility of threshold baseline, not its reliability. |
| CRC controls expected risk only for exchangeable loss functions and a monotone conservativeness parameter; non-monotone losses can fail arbitrarily badly. | [K] | Angelopoulos, Bates, Fisch, Lei & Schuster, “Conformal Risk Control,” ICLR 2024 / arXiv:2208.02814v4: https://arxiv.org/abs/2208.02814 ; official code: https://github.com/aangelopoulos/conformal-risk | Sec. 1.1, Eqs. (3)--(4), pp. 2--3; Sec. 2.4, Prop. 2, Eq. (16), p. 6. | Does not say D1 is impossible; it defeats an unqualified coverage guarantee across held-out physical cells. |
| Low-cost VL53L5CX+ultrasonic fusion has already been evaluated for lightweight onboard obstacle avoidance, including transparent/reflective obstacles. | [K] | Kalenberg et al., “SuperBat,” IEEE ISSE 2024, DOI: https://doi.org/10.1109/ISSE63315.2024.10741113 ; author record: https://www.research-collection.ethz.ch/entities/publication/37f53844-3b0b-44be-a0cf-175a30388bda | Abstract and experiment summary on official repository record; full PDF page/section access was blocked [GAP]. | It is a fusion/UAV paper, so it is component/story collision, not verified exact-claim collision. |
| Reference targets of defined reflectance and periodic self-tests are an established optical-safety-device mechanism; a failure can cause safety shutdown but is combined with watchdog/redundancy measures. | [K] | Jachmann et al. / SICK AG, DE102021103952A1 official patent record: https://patents.google.com/patent/DE102021103952A1/en ; US publication: https://patents.google.com/patent/US20220269237A1/en | Description paras. [0003]--[0005], [0016]--[0028]; claims 1, 5, 9--10. | Official technical prior art, not a peer-reviewed experiment; enough to defeat “reference-target self-test is new.” |
| Generic IoT fault diagnosis/self-calibration already covers bias, drift, complete failure, and precision degradation. | [K] | Sinha & Das, “SNRepair,” *IEEE Sensors Journal* 23(13):14915--14922, 2023, DOI: https://doi.org/10.1109/JSEN.2023.3277493 | Official abstract / publisher metadata; full text inaccessible in this pass [GAP]. | Does not establish an active optical reference test. |
| Active diagnostic actions under safety constraints are already a formal research topic. | [K] | Al Saati et al., “Online tree-based planning for active spacecraft fault estimation and collision avoidance,” *Science Robotics*, 2024, DOI: https://doi.org/10.1126/scirobotics.adn4722 | Abstract and Methods overview on official article page; exact PDF page was not retrievable [GAP]. | Different spacecraft simulator; kills D2's generic active-diagnosis contribution only. |
| A low-cost VL53L5CX on an ESP32-class system is physically usable in a simple sensing pipeline. | [K] | Piñeiro et al., “Low-Cost LiDAR-Based Monitoring System for Fall Detection,” *IEEE Access* 12 (2024):72054+, DOI: https://doi.org/10.1109/ACCESS.2024.3401310 | Sec. III.A--B, pp. 72058--72059 (hardware and 10 Hz trade-off). | Human fall detection is out of scope; source supports only hardware feasibility. |

## Queries and failed searches

Searches run 2026-08-28:

- `"VL53L5CX" reliability material illumination orientation 2024 2025 2026 paper`
- `"VL53L5CX" fault detection self-test 2024 2025 2026`
- `"time of flight" proximity sensor "self-test" diagnosis 2024 2025 paper`
- `selective classification conformal risk control abstention 2024 2025 sensor safety paper`
- `"SNRepair" "sensor fault diagnosis"`
- `"active fault diagnosis" "sensor" 2024 "self test"`
- `"VL53L5CX" "selective" classification sensing 2024 2025 2026`
- `"VL53L5CX" "uncertainty" obstacle detection 2024 2025`

Failed/limited retrieval: the official *Sensors* VOR and Oxford repository PDF were anti-bot blocked in one fetch route; its section text was checked through the official PMC mirror/search extract. The IEEE/SuperBat full text and SNRepair full text were not accessible here, so their uninspected details are explicitly [GAP]. No missing exact hit is treated as novelty.

## Decision

**D1: PIVOT. D2: KILL (with only a measurement-appendix pivot).** Do not promote either as a new sensing, abstention, or self-test mechanism. The only continuation that passes this audit is D1 reframed as a pre-registered finite-family empirical boundary study with matched conservative baselines and a useful null outcome; its third novelty round remains Amber until the statistical split and endpoint are frozen.

PIVOT
