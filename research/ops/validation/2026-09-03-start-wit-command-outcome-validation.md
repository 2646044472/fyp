# Validation Audit: 2026-09-03 - START-WIT command-outcome verification

## Decision investigated

Whether `START-WIT` should remain a conditional edge-computing FYP direction:
after a low-voltage motor start command, a frozen policy reads only short
motor-current and accelerometer prefixes and emits `running`,
`failed-to-start`, or `inspect`, with an independent optical mechanical witness
used only for evaluation. The audit reads `research/active/15` through `24`,
the active charter/register, the 2026-09-03 maintenance divergence packet, and
the prior direct-neighbor records. It writes only this new file.

## Claim under test

For a declared benign low-voltage fixture, a sequential current-plus-
acceleration policy improves the maintenance-record action-loss/latency
frontier at fixed maximum observation time, inspection budget, sensor budget,
and energy over current-only, acceleration-only, fixed-window fusion, and
always-`inspect`, using an optical tachometer or photointerrupter as withheld
truth.

The permitted claim is a bounded command-outcome/run-proof experiment. It is
not a motor-health classifier, predictive-maintenance model, causal fault
diagnosis method, network contribution, or safety guarantee.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Current-signature motor diagnosis on an inexpensive edge platform is already demonstrated by de las Morenas et al. (2023). Pi deployment of a servo-motor diagnosis pipeline using acceleration/voltage, teacher-student compression, quantization and GUI operation is already reported by Zhou et al. (published 2024-12-24; 2025 issue). Baddou et al. (published 2026-08-19) combine current/vibration, operating-condition shifts and confidence/deployability assessment. Bian et al. (published 2026-08-10) already use low-cost screening, high-information confirmation, escalation and resource costs. | The exact proposed combination of a post-command binary mechanical outcome, an `inspect` action, a short deadline, an independent withheld mechanical witness, and action-loss evaluation was not established in the inspected sources. This is a scoped search boundary, not a novelty result. | High collision for sensors/edge/active acquisition; medium for the exact endpoint. |
| Exact-claim collision | Start-up transient analysis is itself a mature motor-diagnosis setting. The 2025 TMCSA paper uses current during startup to diagnose broken rotor bar and eccentricity faults; Machines 2023, 11(10), 958 acquires 5-second startup current traces for inter-turn-short-circuit diagnosis; the 2024 Electronics paper treats automatic transient separation as a first step for motor diagnosis. These works make “first 2-5 seconds of current/vibration contains useful motor evidence” non-distinct. Industrial pump-controller documentation also exposes motor current as a run-verification signal, so the operational endpoint is not new in the general sense. | No inspected academic source was found with the exact `running / failed-to-start / inspect` record action and the proposed cost function. However, replacing a binary classifier with a reject/inspection action is a standard selective-classification/control framing unless the physical endpoint or measured frontier adds something that a fixed threshold already lacks. | High for ordinary classification; medium-high for exact action wording. |
| Boundary / impossibility | A fixed fusion rule can reproduce any deterministic sequential policy when the complete prefix is available. If early stopping is the only claimed mechanism, it must show a strict held-out latency/action-cost improvement; otherwise the sequential policy is an implementation variant. Current and acceleration can change because of load, mounting, supply sag, or fixture resonance while the command outcome is unchanged. Conversely, a motor can rotate while a pump produces no flow, a fan produces insufficient airflow, or a valve fails to reach its intended position. | A finite shaft-rotation endpoint is identifiable with an independent optical witness if the marker, optics, timing, and truth rule are independently validated. A broader equipment-success endpoint is not identified by a tachometer alone. A paired process-change versus sensor-bias construction can support the `CAUSE-NULL` fallback, but no such data exist yet. | High for the boundary; high that the current story must be narrowed. |

## Assumption and identification audit

1. **The endpoint must be rewritten as shaft rotation, not equipment success.**
   The protocol says “pump/fan/valve” and “whether the command took effect,” but
   the proposed witness observes only a marked rotor. Rotation is a valid truth
   target for a fan/motor fixture; it is not proof of pump flow, pressure,
   valve position, or downstream process effect. A claim about those effects
   requires a separate flow/pressure/position witness. Until then, `running`
   must mean `shaft crossed the declared RPM/pulse rule before deadline`.

2. **`failed-to-start` is not automatically a safe negative conclusion.** A
   motor can rotate below the intended operating condition, start late, stall
   after the deadline, or rotate while the load is mechanically ineffective.
   The preregistration's binary rule is usable only if the decision target is
   explicitly “started-before-deadline,” with all other cases mapped to
   `inspect` or excluded by a fixed truth-quality rule. Otherwise the three
   actions conceal several incompatible physical states.

3. **The proposed action is close to selective classification.** Given a
   complete current/acceleration prefix, early stopping is a policy over the
   same observations. The fixed-window fusion classifier plus a calibrated
   reject/inspect threshold is the decisive baseline, not merely a fixed
   classifier. The pilot must report whether sequential stopping changes the
   Pareto frontier after charging the same feature computation, sensor time,
   storage, and energy. A lower average latency alone is insufficient if it
   increases false `running` actions or only stops on trivially easy episodes.

4. **The network story is currently unmeasured.** The active documents correctly
   say that disconnection is a context constraint. No local-versus-upload
   deadline, remote/cloud decision, upload delay distribution, or synchronization
   action is presently specified. The title and claim must not include
   “weak-network improvement” until those quantities are measured.

5. **Truth independence is physical, not merely software isolation.** An
   optical sensor is a different modality from current and vibration, but its
   marker can fall off, become occluded, or be mechanically coupled to the
   same mount. The truth logger needs manual start/stop validation, a fixed
   pulse/RPM rule, separate storage/runtime permissions, and a truth-quality
   exclusion analysis. A relay confirms command delivery, not mechanical
   completion.

6. **The INA219 is a feasibility risk for transient current evidence.** TI's
   INA219 Rev. G datasheet (SBOS448G, revised December 2015) specifies
   programmable ADC conversion times of 84, 148, 276, and 532 microseconds for
   single conversions, but its averaging table reaches 68.10 ms for 128
   samples; the device also converts shunt and bus quantities at different
   times. The active BOM does not freeze conversion mode, averaging, shunt,
   effective sample rate, or whether bus-voltage reads are interleaved. A Pi
   poll loop cannot be treated as a current waveform recorder. The first gate
   must measure actual timestamped current samples and replace INA219 with an
   analog shunt/ADC if the declared prefix cannot resolve the command event.

7. **The accelerometer is capable but mount-sensitive.** ADXL345 Rev. G
   supports selectable ranges and output data rates up to 3200 Hz, but the
   measured signal depends on axis orientation, mounting stiffness, balance,
   rotor speed, and fixture resonance. A single remount is a minimum stress
   test, not evidence of transfer to other motors. The policy must not use
   `mount_id`, load condition, relay state, or truth timestamps as hidden
   covariates.

8. **One motor and staged failures cannot support broad generalization.** A
   single fan with a blocked-rotor condition can show a repeatable bench result
   while saying nothing about pumps, valves, different motor controllers, or
   real maintenance. The candidate must name the fixture population and report
   the one-motor limitation. A second motor is not required for the preflight,
   but the absence of one must be a declared boundary rather than hidden by
   random episode splits.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| de las Morenas, Moya-Fernandez & Lopez-Gomez, *The Edge Application of Machine Learning Techniques for Fault Diagnosis in Electrical Machines*, Sensors 23(5):2649, version of record 2023-02-28. https://www.mdpi.com/1424-8220/23/5/2649 | Motor-current signature features; Arduino acquisition and edge inference | Broken-rotor-bar/fault diagnosis using public data and a different-machine test; abstract and Secs. 1-2 | Current-based low-cost edge motor diagnosis | Kills current-plus-edge as a component contribution. The exact command-outcome endpoint remains open only as a bounded empirical question. Full publisher retrieval was rate-limited during this audit; detailed section/page ablations remain [GAP]. |
| Zhou et al., *A Deployment Method for Motor Fault Diagnosis Application Based on Edge Intelligence*, Sensors 25(1):9, published 2024-12-24, version of record. https://www.mdpi.com/1424-8220/25/1/9 | Acceleration/voltage acquisition, teacher-student model, quantized student and Raspberry Pi 4B GUI | Servo-motor fault classes; accuracy, confusion, model size, inference time/memory and deployment; abstract, Secs. 1-2 and 6 | Pi motor diagnosis and cloud-edge workflow | Kills Pi deployment and compressed model framing. It does not establish the exact withheld optical witness/action-loss endpoint. The paper's broad-device future work cannot be treated as a gap proof. |
| Baddou et al., *Towards a Resilience-Oriented Framework for Fault Diagnosis Under Varying Operating Conditions*, Sensors 26(16):5239, version of record 2026-08-19. https://www.mdpi.com/1424-8220/26/16/5239 | Vibration/current, physics-aware and data-driven branches, confidence and escalation layer | Six bidirectional speed/torque/radial-force shifts; classification, PCI, SDI, ECR and deployability categories; Secs. 3.4, 3.6.4-3.6.5 and 6 | Multi-sensor reliability/deployability under held-out operating conditions | Kills generic “sensor fusion plus inspect/escalate under shift.” The paper assumes rotating-speed information and uses diagnostic classes, so the shaft-outcome boundary remains narrower but high-risk. |
| Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, version of record 2026-08-10. https://www.mdpi.com/1424-8220/26/16/5065 | Low-cost screen, high-information confirmation, uncertainty/OOD gate, watchdog and commissioning | Five-stress/CWRU/Paderborn fault warning; activation, Macro-F1, blind interval and resource cost; abstract, Secs. 1, 3.1, 5.1, 6 and 8 recorded in the prior local audit; current publisher record/abstract verified | Screen/confirm/escalate action family with edge resource cost | Kills generic “wake/confirm/inspect based on cheap sensors.” It leaves only a declared shaft-outcome endpoint if fixed two-shot/always-inspect and fixed reject controls fail. Full current retrieval was rate-limited; detailed ablation pages remain [GAP] in this round. |
| *Automatic Fault Diagnosis System for Induction Motors During Transient Conditions*, Energies 18(24):6439, 2025, version/date not recovered from the accessible record. https://www.mdpi.com/1996-1073/18/24/6439 | Startup transient motor current; Gabor, STFT, Wigner-Ville and CWT; real-time speed estimation | Broken-rotor-bar and mixed-eccentricity diagnosis during startup; abstract and Conclusions | Startup current prefix as informative diagnostic evidence | Kills “startup prefix is an unoccupied observation regime.” It is fault diagnosis rather than command success, so it does not by itself prove exact overlap with START-WIT. Exact publication date and full section/page audit remain [GAP]. |
| *Detection of Inter-Turn Short Circuits in Induction Motors under the Start-Up Transient by Means of an Empirical Wavelet Transform and Self-Organizing Map*, Machines 11(10):958, 2023. https://www.mdpi.com/2075-4702/11/10/958 | Three Hall current sensors; 5-second startup transient; FPGA data acquisition | Healthy plus three short-circuit severities under multiple frequencies; current-only transient diagnosis; Secs. 2.1-2.2 | Five-second startup current acquisition and staged motor conditions | Kills a claim that collecting a 5-second current prefix is itself novel. Its FPGA/current-only setup leaves Pi/action-cost/independent mechanical truth unresolved. |
| Martinez et al., *Start-Up and Steady-State Regimes Automatic Separation in Induction Motors by Means of Short-Time Statistics*, Electronics 13(19):3850, 2024. https://www.mdpi.com/2079-9292/13/19/3850 | Magnetic stray-flux time series, short-time statistics, PSO window selection and variance threshold | Automatic transient/steady-state separation across frequencies and startup times; Secs. 2-4 | Temporal segmentation of startup evidence and fixed-window timing | Kills “short sequential temporal evidence” as an unoccupied generic mechanism. It does not evaluate the proposed action loss or optical truth. |
| Sulzer, PCX register manual, version/date not visible in the retrieved manual record. https://www.sulzer.com/-/media/files/products/pumps-accessories/pump-controllers/product-information/manuals/pcx_register_manual_81300048.ashx?la=sv-se | Controller configuration includes motor-current run indication and a run-verification signal; records start-to-full-flow timing | Operational pump run verification and flow-related timing; manual p. 103 and register fields 5129-5141 | Existing engineering practice for “did the pump run?” | Kills a broad real-world story that run verification is an unexplored operational need. It is not a research-paper collision and does not settle whether the proposed finite edge action frontier is useful. |

## Strongest simple baseline

The strongest baseline is a calibrated **fixed-window current-plus-acceleration
reject policy**, not merely a fixed-window classifier:

1. collect the complete permitted prefix up to the common deadline;
2. estimate `P(started-before-deadline | current, acceleration)` with a frozen
   logistic model, shallow tree, or thresholded physical features;
3. emit `running` only above the false-running constraint;
4. emit `failed-to-start` only below a separately frozen threshold;
5. emit `inspect` in the middle band.

This baseline has the same observations and can approximate the best possible
action rule for the finite fixture. Add `always-inspect`, current-only,
acceleration-only, fixed two-sensor fusion, and an **always-wait-to-deadline**
control. The proposed sequential policy must beat this full-prefix reject
baseline on the held-out load/remount cell at equal error loss, not just beat
weak single-sensor thresholds.

## Contrarian result

The positive mechanism claim is currently too close to ordinary supervised
classification plus abstention. The only defensible remainder is a bounded
measurement study with the endpoint renamed to `shaft-start verification` and
the network language removed until measured. The most likely outcomes are:

- fixed fusion is Pareto-optimal, killing the sequential-policy claim;
- current-only is sufficient, killing the multi-sensor claim;
- optical truth is stable only for rotor motion, forcing the narrower endpoint;
- INA219 timing is inadequate, forcing a faster current path or killing the
  current-prefix claim;
- load/mount changes reverse the action ranking, supporting a finite null or
  the `CAUSE-NULL` paired-world study;
- the policy wins only on random windows or staged failure type, which is a
  data-leakage/ordinary-classification result rather than promotion evidence.

No source inspected establishes a global exact-claim collision with the
literal START-WIT action tuple. That unresolved search result is insufficient
for promotion because the components, startup observation regime, reject
action family, and operational run-verification need are already occupied.

## Feasibility audit

- **Hardware:** Pi 5 plus a guarded 5 V fan is suitable for a bring-up, but
  Pi-only polling is not adequate for a timing claim until jitter and drops are
  measured. A small MCU for policy acquisition and a separate truth logger are
  reasonable instrumentation, not contributions.
- **Current channel:** INA219 is a 12-bit I2C monitor with programmable
  conversion/averaging. The official Rev. G datasheet is dated December 2015;
  its 128-sample setting reaches 68.10 ms and current/bus conversions are not
  simultaneous. Freeze a no-averaging or declared averaging mode and report
  effective samples/sec. If the motor event is shorter than the measured
  resolution, use an analog shunt plus MCU ADC or remove current from the
  positive claim.
- **Acceleration channel:** ADXL345 Rev. G supports up to 3200 Hz ODR, but the
  real signal depends on mount and axis. Record orientation, range, ODR,
  fixture resonance checks, and remount identity.
- **Truth:** use a separate optical sensor/input-capture logger, marker
  validation, manual stop trials, a fixed RPM/pulse rule, and permissions that
  prevent policy access. A relay is a command marker only.
- **Data:** the active minimum of 20 valid training episodes per condition and
  10 held-out episodes is a feasibility minimum, not statistical power. Three
  sessions, two loads, one remount, complete-episode splits, and a repeated
  held-out session are mandatory for a positive claim.
- **Labels:** `inspect` must remain an action. Do not exclude ambiguous truth
  episodes selectively by policy output; predeclare truth-quality exclusions
  and report them.
- **Safety:** low-voltage guarded rotor, emergency stop, current-limited
  supply, and no mains/production connection. A pump/valve should not be
  claimed unless an independent flow/position witness is added.
- **Time:** the December 2026 demo is feasible only as a shaft-start offline
  demonstrator. The full FYP direction should remain unlocked until the
  instrumentation and held-out baseline gate passes.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Low-cost edge motor-current diagnosis is established. | [KILL] | de las Morenas et al., Sensors 23(5):2649, 2023-02-28, https://www.mdpi.com/1424-8220/23/5/2649 | Abstract and Secs. 1-2 in official PDF/HTML record | Arduino/current/fault endpoint; full paper section audit was rate-limited in this round. |
| Pi motor-diagnosis deployment is established. | [KILL] | Zhou et al., Sensors 25(1):9, published 2024-12-24, https://www.mdpi.com/1424-8220/25/1/9 | Abstract, Secs. 1-2 and 6 in official HTML record | Servo fault classes and Pi 4B deployment; not command outcome. |
| Multi-sensor operating-condition shift and deployability are established. | [KILL] | Baddou et al., Sensors 26(16):5239, version of record 2026-08-19, https://www.mdpi.com/1424-8220/26/16/5239 | Secs. 3.4, 3.6.4-3.6.5 and 6 | Fault diagnosis, not shaft-start verification; direct collision is family/endpoint-level. |
| Active screen-confirm acquisition under resource cost is established. | [KILL] | Bian et al., Sensors 26(16):5065, version of record 2026-08-10, https://www.mdpi.com/1424-8220/26/16/5065 | Secs. 1, 3.1, 5.1, 6 and 8 from prior local audit; publisher abstract/version notes rechecked 2026-09-03 | Current web retrieval was rate-limited; exact ablation pages remain [GAP]. |
| Startup transient current is a mature motor-diagnosis observation regime. | [KILL] | Energies 18(24):6439, 2025, https://www.mdpi.com/1996-1073/18/24/6439; Machines 11(10):958, 2023, https://www.mdpi.com/2075-1702/11/10/958 | Energies abstract/conclusions; Machines Secs. 2.1-2.2 | Exact Energies publication date not recovered; both are fault-diagnosis endpoints. |
| Startup/steady-state temporal segmentation is established. | [KILL] | Martinez et al., Electronics 13(19):3850, 2024, https://www.mdpi.com/2079-9292/13/19/3850 | Secs. 2-4 | Kills generic temporal-prefix mechanism; not exact action tuple. |
| INA219 supports programmable conversion and averaging, with 68.10 ms at 128-sample averaging. | [K] | Texas Instruments, INA219 datasheet SBOS448G, revised December 2015, https://www.ti.com/lit/gpn/ina219 | PDF pp. 5, 9 and 20; Table 5, Table 6 and Sec. 8.3.1.1 | Nominal chip behavior; breakout shunt, driver, mode and effective rate must be measured. |
| ADXL345 supports up to 3200 Hz output data rate. | [K] | Analog Devices, ADXL345 datasheet Rev. G, 2015-10-26, https://www.analog.com/media/en/technical-documentation/data-sheets/adxl345.pdf | PDF p. 3, Table 1; output-rate and measurement specifications | Nominal capability, not evidence that the mounted breakout produces a stable motor feature. |
| Raspberry Pi GPIO is 3.3 V and motors must not be connected directly. | [K] | Raspberry Pi official computer hardware documentation, current page accessed 2026-09-03, https://www.raspberrypi.com/documentation/computers/raspberry-pi.html | GPIO lines 2103-2180, especially GPIO output/input warnings | Wiring guidance only; exact relay module interface remains [GAP]. |
| The tachometer proves only the declared mechanical rotation rule. | [KILL boundary] | Proposed observation model and Sulzer PCX run-verification manual, https://www.sulzer.com/-/media/files/products/pumps-accessories/pump-controllers/product-information/manuals/pcx_register_manual_81300048.ashx?la=sv-se | Proposed protocol Secs. “Truth and actions” and “Independence”; Sulzer manual p. 103 | A run-verification signal/current threshold is operationally known; rotor truth does not prove flow/pressure/valve position. |
| A held-out action frontier advantage exists. | [C]/[GAP] | START-WIT hypothesis in active `15-24` | Active prospectus, preregistration, schema and acquisition architecture | No sensor data, acquisition code, or hardware log was present on 2026-09-03. |

## Queries and failed searches

Queries run or rechecked on 2026-09-03:

- `"motor startup" current vibration start failure detection command success verification`
- `"actuator" "command execution" verification motor current vibration sensor`
- `edge motor fault diagnosis current vibration Raspberry Pi primary paper 2024 2025 2026`
- `"motor start" "current" "accelerometer" fault diagnosis edge`
- `"motor start-up" vibration current detection paper`
- `"starting failure" motor current vibration paper`
- `"start-up transient" motor fault diagnosis current vibration`
- `"actuation verification" industrial motor sensor`
- `"motor run verification" current sensor tachometer pump`

The searches returned current-signature diagnosis, startup-transient diagnosis,
Pi deployment, active screen-confirm acquisition, and industrial run-
verification documentation. No inspected primary source jointly matched Pi,
current plus accelerometer, an independent optical witness, the exact three
actions, and the proposed action-loss endpoint. This is [GAP], not evidence of
novelty. The full publisher pages for several MDPI papers were intermittently
rate-limited; those unresolved full-text details are recorded above rather
than inferred from abstracts.

## Decision

Keep only a narrowed **shaft-start verification preflight** alive. Remove
“pump/valve success,” “weak-network contribution,” “motor diagnosis,” and
“new sensor-fusion method” from the claim. Promotion requires measured INA219
or replacement current timing, independent optical truth, fixed-full-prefix
reject baseline, held-out load/remount repetition, and a repeatable
action-level advantage. A baseline tie, one-motor dependence, truth coupling,
or endpoint reduction to ordinary classification kills the positive mechanism;
a successful process-change/sensor-bias paired-world construction should pivot
to `CAUSE-NULL`.

HOLD
