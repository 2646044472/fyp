# Decision investigated: whether START-WIT should remain a positive FYP candidate

## Validation Audit: 2026-09-03 START-WIT post-audit

## Decision investigated

Whether the remaining positive START-WIT claim should remain a thesis
candidate: a frozen sequential policy consumes the first 2--5 seconds of motor
current and accelerometer data, then records running, failed-to-start, or
inspect for a binary, optical-tachometer-defined shaft-start deadline. The
claim is tested against one-sensor, fixed-full-prefix reject, and
always-inspect controls under held-out load and remount conditions.

## Claim under test

The claimed residual is not motor diagnosis: it is that low-cost, local,
prefix-based fusion creates a nontrivial action-loss/latency improvement for
post-command shaft-start verification. This audit tries to determine whether
the physical truth channel, the action-loss endpoint, fixture cost, and
hold-out design make that residual more than an implementation or a bounded
replication.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Schneider's TeSys Tera documents start-command check, start time, locked-rotor/stall supervision, fault action, restart inhibition, and speed-switch/current based monitoring. Microchip's fan-fault note uses a tachometer as the direct running/fault signal. Zhou et al. use current plus accelerometer acquisition and a Raspberry Pi motor-fault deployment. Tavenard--Malinowski and TEASER formulate early time-series decisions with earliness/accuracy trade-offs; Hatami--Chira adds a costed reject option. | No inspected work was found with exactly this low-voltage fan, current-plus-acceleration prefix, optical-tachometer label, and stated three record actions. That missing exact tuple is not evidence of a research gap. | High for component collision; medium for exact-tuple search boundary. |
| Exact-claim collision | START-WIT's practical decision is command issued -> wait for evidence -> accept running/fault/stop/restart. TeSys motor-management supervision already implements the command/start-time/fault-action portion. Its shaft-speed feedback mode and Microchip's tachometer path are more direct observations of the claimed physical event than current/vibration proxies. P3 is a standard thresholded early-decision/reject policy applied to a new fixture. | The prospectus uses a maintenance-record loss and an optical witness withheld from policy. The inspected industrial documents do not express this exact loss matrix or comparison protocol. These are evaluation choices, not a distinct observation, action, or guarantee. | High. |
| Boundary and necessity | If an optical tachometer can be mounted for independent truth on the declared fixture, a timer plus tachometer pulse is an available local runtime policy and directly observes the shaft-start predicate. If it cannot be mounted in the intended mobile-repair deployment, the benchtop proxy result has no established transport link to that deployment. Current and acceleration cannot by themselves distinguish all mechanical-start, coupling, sensor-mount, load, and electrical worlds; the proposed load/remount split tests only a few selected worlds. | Optical truth is still valuable for honest offline evaluation. A narrowly stated one-fixture result could quantify how often proxy policies agree with that witness, but it cannot establish a new general verification mechanism. | High for the dilemma; high that the residual is bounded rather than a positive mechanism. |

## Assumption and identification audit

### The truth-channel dilemma

[K] A shaft-start predicate is directly observable with a tachometer or speed
switch. Microchip describes a fan tachometer output as a pulse train proportional
to speed and uses its absence/frequency to detect a fan fault. Schneider's
TeSys Tera has speed-switch monitoring that is explicitly intended to determine
whether the motor is running. Therefore a tachometer pulse before deadline
policy is the decisive operational baseline whenever the optical channel is
physically installable.

[KILL] With that channel available, withholding it from the runtime policy
creates an artificial information restriction. A cheap MCU counter plus a
predeclared deadline implements the physical decision without classifier,
current sensor, accelerometer, prefix-score calibration, or an action-loss
optimizer. Current and acceleration may remain useful as diagnostic telemetry,
but this does not establish their necessity for the asserted shaft-start record.

[GAP] If the intended story instead assumes no speed/tachometer sensor can
remain installed in field use, the proposal needs an independently supported
observation model explaining why the labelled bench hardware represents that
field case. No inspected source supplies such a bridge. The optical label does
not prove that current/acceleration under an arbitrary load and mount identify
shaft start outside the declared fixture.

### Action loss does not create a technical residual

[K] A reject/abstain action with an explicit cost is an established decision
rule, and early time-series work already trades decision time against error.
The prospectus's 10 / 2 / 1 / 0.1 loss weights are not traced to a technician,
service process, or stakeholder study. Changing them can change which policy
is preferred. Without a source for those costs, the defensible report is a
Pareto table over false-running, false-failed-start, inspect rate, time, and
energy, not a uniquely optimal maintenance policy.

[KILL] Adding arbitrary asymmetric costs to standard early classification does
not provide a new algorithmic or systems mechanism. It only selects an
operating point from an existing error-delay-reject frontier.

### Low-cost edge fixture and the proposed generalisation split

[K] Zhou et al. already combine motor-current and accelerometer observations
with a Raspberry Pi edge deployment. TeSys and Microchip show that start/fault
supervision and tachometer counting are routine embedded functions. A Pi,
low-voltage motor, and local operation therefore establish feasibility, not a
CS distinction.

[KILL] Holding out one load and one accelerometer remount is necessary
experimental hygiene, but it is not a device-family, motor-family, coupling,
or field-workflow generalisation test. One motor unit also cannot distinguish
an apparent policy benefit from that unit's current waveform, rotor inertia,
mount resonance, or staged-failure implementation. A positive result would be
a finite fixture characterization; a tie against tachometer and full-prefix
controls is the more likely decision-relevant outcome.

### Earliest-decision control is under-specified

[K] Early classification literature treats the choice of decision time and
misclassification cost jointly. P3 checks fixed checkpoints, uses a calibrated
margin, and stops once a threshold is crossed. This is an ordinary instantiation
of that family. P2's reject band is also an ordinary cost-sensitive reject
control. Neither policy defines a new sequential method.

[GAP] The proposal does not state a real hard deadline for the bench user, a
measured network/remote alternative, or an operational reason why waiting for
the direct tachometer deadline is harmful. In the current benign tabletop
fixture, inspect and waiting through the full five seconds are both cheap.
That removes the claimed earliness pressure rather than merely making it an
edge constraint.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Schneider Electric, TeSys Tera, Start Command Check; Start Time, Locked Rotor, Stall pages | Motor-control state/current/speed-switch inputs; start supervision, trip/fault actions, restart inhibition | Whether commanded motor start completes within configured supervision logic | Same post-command operational question; vendor control has a more direct speed-switch option | [KILL] Treating post-command start confirmation, fault response, or restart practice as a new task/action family. It does not benchmark current+accel ML on this fixture. |
| Microchip, Fan Fault Detection using a PIC18F1XK22, DS90003122A | Fan tachometer pulse input; local fault threshold/action on MCU | Direct fan-running/fault detection from pulse frequency/pulse absence | Same physical shaft/fan-running predicate; stronger direct observation | [KILL] The claim that independent optical truth creates an otherwise unavailable low-cost local decision. It leaves only an artificial proxy-versus-direct-sensor comparison. |
| Zhou et al., Cloud-Edge Collaborative Diagnosis Method for Servo Motor Fault Status Based on Multi-Domain Features, Sensors 25(1):9 | Current-voltage module, acceleration sensor, features, Pi 4B student deployment | Motor fault-status classification; accuracy, resource use, deployment | Shares current/acceleration and low-cost edge motor-monitoring components, but not tachometer shaft-start action loss | [KILL] Pi deployment and multimodal motor sensing as contribution. It leaves no support for a separate field-relevant action mechanism. |
| Tavenard and Malinowski, Cost-Aware Early Classification of Time Series, ECML PKDD 2016 | Prefix observations; make a class decision at a selected time | Minimize classification cost plus delay cost | P3's core error/earliness decision form | [KILL] Claiming thresholded early prefix decisions plus delay loss as new. It leaves only a domain-specific empirical replication. |
| Schäfer and Leser, TEASER: Early and Accurate Time Series Classification, DMKD 2020 | Prefix time-series classifier with a trigger for early output | Earliness/accuracy evaluation on time series | Same stop/continue logic family, though not motor start verification | [KILL] New early-stop policy framing. It leaves a fixed fixture data point. |
| Hatami and Chira, Classifiers with a Reject Option for Early Time-Series Classification, 2013 | Early time-series class/reject decisions with classifier/reject costs | Accuracy, earliness, rejection and costs | P2/P3's inspect/reject and costed decision form | [KILL] Inspect as an algorithmic residual. It leaves only the externally defined maintenance workflow. |

## Strongest simple baseline

**P5: direct optical-tachometer deadline rule.** Start a timer on the command
trigger; emit running when the independent tachometer reaches the declared
pulse/RPM rule before deadline; otherwise emit failed-to-start (or inspect only
if the tachometer itself is unavailable/faulted). Implement it on the same MCU
that would timestamp the policy sensors. Report its sensor cost, latency, false
action rate, and failure modes.

This baseline is stronger than P0--P4 because it uses the physical witness
that defines the outcome. If it is inadmissible in deployment, document the
specific installation, optical-access, contamination, alignment, cost, or
maintenance restriction and test it as a missing-observation condition. The
current prospectus supplies no such restriction.

## Contrarian result

The residual positive claim is killed as a thesis mechanism.

1. The operational start-supervision and restart/fault action already exist in
   official motor-management practice.
2. The proposed sequential/reject mechanism is a direct instance of mature
   early time-series decision methods.
3. The independent optical witness either dominates at runtime or is withheld
   by design. In the latter case the result is a deliberately restricted
   proxy-policy benchmark, not evidence that current plus acceleration is a
   needed edge-verification method.
4. The proposed loss weights, deadline pressure, and field transport premise
   are unsupported. A one-motor load/remount split cannot repair those missing
   links.

A well-executed fixture can still produce useful [E] data: agreement and
failure maps for direct tachometer, current-only, accelerometer-only, fixed
fusion, and prefix policies. It must be reported as a bounded replication or
negative baseline, not promoted as the FYP's positive research contribution.
The honest next research path is CAUSE-NULL: construct paired physical and
sensor-bias worlds and measure the minimum independent witness needed to break
the ambiguity.

## Feasibility audit

| Requirement | Audit result | Consequence |
| --- | --- | --- |
| Independent label | Feasible on a tabletop fan/motor with optical tachometer, but only if the pulse rule, occlusion, threshold, latency, and truth-channel failures are logged. | It validates the benchmark label, not the proxy mechanism. |
| Policy sampling | [GAP] The proposed INA219 path has no measured effective sampling rate/jitter. Current waveform features and any spectral feature are unsupported until MCU acquisition is measured. | Do not collect modelling data before the 100-trigger/rate acceptance test. |
| Failure staging | [GAP] Blocked/failed shaft start could create electrical current, vibration, thermal, and mechanical regimes unlike a field start failure. | State staged worlds precisely; do not call them a general motor-failure distribution. |
| Timing pressure | [GAP] No measured technician deadline, remote-delay baseline, or cost of five seconds has been provided. | Remove weak-network/edge urgency from the claim unless measured. |
| Generalisation | One motor, selected load, and selected remount are finite cells only. | Do not make motor-, site-, or maintenance-family claims. |
| Safety | Low-voltage, non-production bench is appropriate, but it cannot justify a production/safety action claim. | Keep the scope as record/test evidence only. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Motor supervisors already check start command/state and enforce start-time/locked-rotor/stall actions. | [K] Schneider Electric, TeSys Tera Motor Management System User Guide, online documentation accessed 2026-09-03; Start Command Check, Start Time, Locked Rotor, Stall, and Speed Switch Monitoring pages. https://productinfo.se.com/tesys_tera_ug/tesys-tera-motor-management-system-user-guide/EN/TeSys-Tera-User%20Guide-DOCA0257-01.xml/ | Named feature pages above; no stable PDF pagination in the online guide. | Official product behavior, not a research paper; nevertheless it is a direct operational baseline. |
| A tachometer pulse directly reports fan speed/fault on a small MCU. | [K] Microchip, Fan Fault Detection using a PIC18F1XK22, DS90003122A (2015). https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/90003122A.pdf | pp. 1--3, especially Fan Tachometer Signal, Fan Fault Detection, and firmware flow. | Fan-specific and not a generic motor theorem; directly relevant to the proposed low-voltage fan fixture. |
| Current plus acceleration and Pi motor-monitoring deployment are already a complete component family. | [K] Zhou et al., Cloud-Edge Collaborative Diagnosis Method for Servo Motor Fault Status Based on Multi-Domain Features, Sensors 25(1):9, published 2024-12-24 / issue 2025. https://www.mdpi.com/1424-8220/25/1/9 | Secs. 2.1--2.3 (current-voltage and acceleration acquisition), Secs. 3.1--3.3 (features/model), Sec. 4 (Pi deployment/evaluation), conclusions. | Fault-status diagnosis rather than command-outcome verification; kills component/deployment novelty, not the exact tachometer protocol alone. |
| Cost-aware early class decisions are established. | [K] Tavenard & Malinowski, Cost-Aware Early Classification of Time Series, ECML PKDD 2016, LNCS 9852, pp. 632--647. https://doi.org/10.1007/978-3-319-46227-1_40 | Abstract; Secs. 1--3 (classification and delay cost formulation); Sec. 4 (experiments). | General time-series method, not motor-specific. |
| Prefix triggers for early accurate classification are established. | [K] Schäfer & Leser, TEASER: Early and Accurate Time Series Classification, Data Mining and Knowledge Discovery 34 (2020), pp. 1336--1362. https://doi.org/10.1007/s10618-020-00683-0 | Abstract; Secs. 1--3 (early-decision objective/method); Sec. 5 (evaluation). | General time series; the same stop/continue form is sufficient collision for P3's claimed mechanism. |
| Reject actions with classifier/reject costs are established in early time-series classification. | [K] Hatami & Chira, Classifiers with a Reject Option for Early Time-Series Classification, arXiv:1312.3989v1, 2013-12-14. https://arxiv.org/abs/1312.3989 | pp. 1--6, especially Secs. 2--4 on early classification, rejection, and cost evaluation. | Preprint rather than archival venue; it is primary work and supports the narrow methodological collision. |
| No inspected source established an exact, field-valid current-plus-acceleration proxy advantage over direct tachometer feedback for the proposed mobile-repair story. | [GAP] Searches listed below, conducted 2026-09-03. | Search boundary only. | Absence from these queries is not novelty evidence. |

## Queries and failed searches

Queries executed on 2026-09-03:

- site:siemens.com motor management start time monitoring locked rotor restart manual PDF
- site:se.com motor protection relay start time supervision locked rotor restart official manual PDF
- "motor start failure" detection current vibration acceleration "tachometer"
- "motor startup" "current and vibration" fault diagnosis paper
- "startup transient" motor "current" "vibration" fault diagnosis PDF
- site:ieeexplore.ieee.org motor startup current vibration fault detection
- "early classification of time series" earliness cost paper PDF
- "Early classification" "reject option" time series
- site:proceedings.mlr.press selective classification reject option cost paper
- "edge" "motor" "start" verification "tachometer" current sensor paper

Failed to establish from the inspected sources:

- a primary paper with precisely the proposed current + accelerometer prefix ->
  running / failed-to-start / inspect action matrix and independent optical
  truth on the same inexpensive fan fixture;
- a credible source showing that five-second local shaft-start confirmation
  materially changes a mobile-repair decision while a direct speed witness is
  unavailable;
- a source supporting the numerical loss weights or a population-level
  generalisation from one motor/load/mount configuration.

These failures are documented uncertainty, not a novelty claim.

## Decision

**KILL.** Do not promote START-WIT as a positive FYP mechanism. Retain the
fixture only as a bounded direct-witness-versus-proxy replication/control if
it is inexpensive, and move the research slot to the CAUSE-NULL physical
non-identifiability study.

KILL
