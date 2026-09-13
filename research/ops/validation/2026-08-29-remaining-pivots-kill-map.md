# Validation Audit: 2026-08-29 remaining PIVOT/HOLD candidates

## Decision investigated

Whether the five remaining entries in the canonical register -- C4, E, D1, AS1, and R1 -- contain a defensible low-cost edge *research mechanism*, rather than an already-studied controller, a standard conservative baseline, or a finite measurement/replication exercise.  This is a negative audit; it does not propose a replacement direction.

## Claim under test

- **C4:** a node decides `send raw / process then send / suppress` using a decision margin, under a latency and compute/transmission budget, to reduce threshold-action loss.
- **E / AS1:** a low-power sentinel decides whether to activate an expensive verifier, with a full-support audit/reference and a tri-state result.
- **D1:** a low-cost multi-zone ToF node emits `clear / uncertain` from a finite, pre-registered material--light--angle boundary map.
- **R1:** a locally persisted evidence record makes a temperature/outage trace `known-safe / known-violation / indeterminate` more useful than a conventional logger.

All apparent distinctions remain **Amber at the start of this audit**.  A missing exact paper is not evidence of novelty.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | [KILL] C4's raw-versus-local-processed choice under computation/communication latency and constrained resources is the central model of Ballotta et al.  E/AS1's continuous low-power sentinel, selective high-power activation, variation trigger, fixed schedule comparator, energy/fidelity accounting, and low-cost node appear together in Marinov et al.  D1's physical ToF testing over geometry, size, material/reflectivity, speed, background and field of view is directly implemented by Gimpelj and Munih.  R1's event/provenance fields are conventional durable-journal fields, and three-valued incomplete-trace semantics pre-date the candidate. | [GAP] C4 has not named a physical signal or loss unavailable to Ballotta's formulation.  E/AS1's independently surviving original-time reference is a stronger evaluation control than Marinov's signal-quality replay; D1 uses a multi-zone rather than the neighbor's point/multi-pixel units.  These are apparatus/evaluation differences, not yet a mechanism or endpoint difference. | High for C4/E/AS1/D1 components; high for R1's ledger/semantics. |
| Exact-claim collision | [KILL] Ballotta et al. give the same source observations/action alternatives and optimize the same latency--accuracy monitoring trade-off.  Marinov et al. explicitly use a continuous CO2/environment sentinel to decide when a high-power particulate sensor is on, compare continuous/scheduled/adaptive modes, and measure energy/fidelity.  Gimpelj and Munih's controlled robot-workspace study is itself a finite condition map used to inform conservative safety sensing.  R1's exact state vocabulary is not copied verbatim, but a conventional B-journal plus its own verifier reproduces every declared input. | [GAP] None of these papers proves the exact proposed held-out condition split, tri-state vocabulary, or December benchtop hardware.  Those differences cannot support a contribution unless the candidate first names an action, observation, or endpoint the cited work and the simple baseline cannot implement. | High C4/E/AS1/D1; high for the B-journal equivalence; medium for an exact R1 application-paper collision. |
| Boundary / impossibility | [KILL] With a skipped verifier interval, a short target excursion and no excursion can have identical online observations unless the sentinel has a validated predictive relation.  Under schedule-independent event timing, equal-budget regular periodic sampling has the smallest maximum blind gap and is a known adversarial baseline.  A ToF return alone cannot identify whether an apparent distance change arose from target geometry, reflectivity/background, optical configuration, or an unobserved condition.  A durable trace cannot distinguish healthy plausible readings from a sensor fault that produces the same recorded values. | A finite, separately instrumented physical *measurement* can map these ambiguities for stated cells.  It cannot establish a general safety/reliability guarantee, and its result is not a new controller if a conservative status/threshold or periodic policy matches it. | High under the stated observations; no field-prevalence claim is made. |

## Assumption and identification audit

### C4

Let the decision be thresholding an estimate at deadline `d`.  If the proposed loss is determined only by (i) raw/processed estimation error and (ii) delivery latency, `send raw`, `process`, and `suppress` are already a finite action set in the monitoring optimization.  `Suppress` has no separate observation or restoration effect in C4's current story: it is just the Bayes/threshold decision to withhold an update.  [KILL] Therefore a decision-margin rewrite cannot itself distinguish C4 from the cited latency--accuracy allocation problem.  A new claim would need a physical action loss, a verified measurement of staleness at the decision owner, and a non-equivalent action that is not a relabelled scheduling choice; none is specified.

### E / AS1

Let `S_t` be the sentinel, `V_t` the expensive verifier, and `A_t in {wake, skip}`.  For an interval with `A_t = skip`, worlds containing a short verifier-only excursion and no excursion can share the same `S` trace.  [KILL] A policy cannot label both cases truthfully as `no event` from these observations.  An original-time reference fixes *offline scoring* only; it provides no online information.  If events are independent of the schedule/sentinel, the regular maximum-gap periodic schedule is the mechanism-eliminating baseline.  If they are sentinel-predictable, the claimed advantage is conditional on that measured relationship and is already the premise of variation-triggered sensing.

### D1

For a ToF reading `z`, an unobserved combination of target geometry, material/reflectivity, background, field of view, illumination, angle, and sensor state can yield the same `z`.  Consequently a map built from enumerated cells can justify only a conservative action on those cells; it cannot identify the physical cause or generalize to an unenumerated object/setup.  Gimpelj and Munih show the operative ambiguity experimentally: geometry, gap width, speed, background contrast and reflective materials alter the observed profiles, and their discussion recommends conservative configuration choices for the same false-negative/false-positive asymmetry.  [KILL] Without a new observable or intervention, `status + threshold + invalid => uncertain` is the primary baseline; an added condition-aware rule is killed when that baseline has the same finite frontier.

### R1

For any declared persisted fields, create a healthy execution and a stuck/bias/thermal-contact fault execution with the same sample values, read-statuses, resets, supply state, and delivery log but different true threshold exposure.  The R1 policy sees the same history.  [KILL] It cannot soundly release one as `known-safe` and withhold the other.  A crash-atomic B-journal containing the fields listed in the earlier R1 audit plus R1's exact compatible-history verifier implements the same information state.  The remaining experiment is a crash-window/rate-envelope boundary measurement, not a provenance mechanism.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Ballotta, Peserico, Zanini & Dini, *To Compute or Not to Compute? Adaptive Smart Sensing in Resource-Constrained Edge Computing*, IEEE TNSE 11(1), 2024, pp. 736--749 | Sensors send raw measurements or process on board before transmission; formulation embeds computation and communication latency; dynamic allocation/selection. | Network monitoring performance under constrained computation; numerical experiments. | C4's raw/timely versus local-processed/accurate alternatives, resource constraint and decision timing. | [KILL] generic decision-margin scheduling and any claim whose threshold-action loss is a monotone restatement of estimation accuracy plus lateness.  It leaves only a named non-equivalent physical action/loss, which C4 lacks. |
| Marinov, Tsonev, Donchev, Karadzhov & Gadzhev, *Digital-Twin-Assisted Adaptive Sensor Scheduling for Energy Optimization in Battery-Powered Indoor Air Quality (IAQ) IoT Nodes*, Electronics 15(11):2395, 2026 | Continuous low-power CO2/environment sentinel; selectively activated high-power particulate sensor; variation trigger and schedule; continuous/scheduled/adaptive modes. | Energy consumption/battery lifetime and measurement fidelity; low-cost hardware plus a hardware-level twin. | E/AS1's two-fidelity wake decision, edge energy story, policy family and frontier. | [KILL] generic selective wake, support/variation trigger, and energy/fidelity claim.  An independent original-time reference is only an evaluation distinction until it changes an online action/guarantee. |
| Gimpelj & Munih, *Assessing Geometry Perception of Direct Time-of-Flight Sensors for Robotic Safety*, Sensors 25(14):4385, 2025 | Direct ToF configurations, controlled scene measurements over shapes/sizes/gaps, speed, background, materials and reflective surfaces. | Geometry/perception errors and conservative safety-relevant sensor configuration. | D1's finite material/condition boundary-map object and conservative `uncertain` story. | [KILL] a ToF physical condition map or conservative configuration as the research contribution.  It leaves only a rigorously demonstrated new observable/action/endpoint, not a board or zone-count swap. |
| Loreti, Bracciale & Bianchi, *StableSENS*, IEEE Internet of Things Journal 6(6), 2019, pp. 9908--9918 | Equal-count sensing schedules and event detection. | Under schedule-independent events, analyses missed-event risk as interval variability changes. | AS1's equal verifier-budget event-observability comparison. | [KILL] any universal claim that adaptive/irregular verification beats periodic at the same budget.  Does not rule out a finite, independently measured sentinel-predictive condition. |
| Wang, Ayoub, Sokolsky & Lee, *Runtime Verification of Traces under Recording Uncertainty*, RV 2011/LNCS 7186, 2012, pp. 442--456 | Abstract incomplete record; `true / false / undecided` verdicts over compatible histories. | Sound temporal verdicts under recording uncertainty. | R1's three-state compatible-history semantics. | [KILL] a generic three-state or gap-propagation theoretical contribution; it leaves a physical measurement only. |

## Strongest simple baseline

- **C4:** compute the deadline-feasible raw and processed actions from measured latency/error models, choose the lower declared action loss, and suppress only when the same fixed threshold says no update is needed.  This is a direct scalar instance of the existing allocation formulation; no learned margin is required.
- **E / AS1:** at each verifier-on budget, a phase-randomized, fixed maximum-gap periodic schedule; `event` only on supported readings and `unknown` otherwise.  Add always-on and sentinel-only controls.
- **D1:** vendor status/validity plus a fixed conservative distance threshold, with every invalid/out-of-support frame `uncertain`.  A condition-aware method must beat it on the pre-registered finite cells under equal latency/energy.
- **R1:** B-journal (epoch, sequence, local time/error bound, read status/value, supply/reset state, commit state, delivery state) plus R1's identical conservative verifier.

## Contrarian result

**[KILL] None of C4, E, D1, AS1, or R1 is promotable as currently phrased.**  C4, E/AS1 and D1 fail component and exact-task/endpoint collision checks; R1's proposed state is subsumed by a durable journal and established incomplete-trace semantics.  Their honest residuals are finite replications or measurement boundaries:

- C4: show whether a scalar physical action loss is actually non-equivalent to existing latency/accuracy allocation.
- E/AS1: use a continuous independent reference and report that a sentinel lacks (or has) predictive value beyond periodic inspection for a specified physical condition family.
- D1: use the ToF ambiguity map only as a preflight control, not thesis mechanism.
- R1: measure flash/reboot/rate-envelope ambiguity windows against B-journal.

These residuals can produce useful negative evidence, but none passes the FYP direction-lock gate without an additional, audited mechanism.

## Feasibility audit

| Candidate | Hardware/data/ethics | Result |
| --- | --- | --- |
| C4 | [GAP] A low-cost board can demonstrate scheduling, but no physical stream, decision owner, threshold action, external deadline measurement, or loss model has been selected. | A December demo is plausible; a defensible empirical claim is not yet specified. |
| E / AS1 | [K] Benign sensor/pulse/reference rigs are purchasable and avoid personal data/safety actuation. [GAP] Reference timing, response lag, calibration around threshold, actual power measurement and independence from injected faults remain unvalidated. | A well-instrumented negative protocol is feasible, but it is not a new wake mechanism. |
| D1 | [K] A desk-scale ToF/material/light rig is feasible. [KILL] It cannot claim a certified protective envelope, robotics safety compliance, or general material coverage. | Feasible as a measurement control only. |
| R1 | [K] An MCU/flash/outage rig is feasible without personal data. [GAP] Atomic append behavior, torn-write recovery, RTC error and independently surviving reference trace must be experimentally validated. | Feasible as a bounded crash-consistency study only. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Raw versus local-processed sensing under compute/communication latency is an existing edge monitoring allocation problem. | [K] | Ballotta et al., final IEEE TNSE 11(1), Jan. 2024, pp. 736--749, DOI https://doi.org/10.1109/TNSE.2023.3306202 ; author-hosted final-version URL https://www.research.unipd.it/bitstream/11577/3496041/2/zanini.pdf | Abstract and Sec. I, pp. 736--737; Sec. II, pp. 738--740; Sec. III, pp. 741--743; conclusion, p. 747. | Author-hosted file was Cloudflare-blocked in this round; these exact pages were checked in the prior canonical validation packet.  The official DOI and final pagination are verified; do not assert its treatment of a new physical action not named by C4. |
| A continuous low-power sentinel can trigger selective high-power sensing, with adaptive/scheduled/continuous comparisons and energy/fidelity accounting. | [K] | Marinov et al., published 1 Jun. 2026, Electronics 15(11):2395, DOI https://doi.org/10.3390/electronics15112395 ; official PDF https://mdpi-res.com/d_attachment/electronics/electronics-15-02395/article_deploy/electronics-15-02395.pdf | Abstract, pp. 1--2; Sec. 2.2.1--2.2.3, pp. 7--9; Sec. 2.6.1--2.6.4, pp. 14--16; Sec. 3.4--4.4, pp. 23--34. | Its discrete high-power architecture is twin-evaluated rather than a full independent-reference physical verifier.  This leaves an evaluation gap, not a mechanism gap. |
| dToF physical measurement over geometry, gap, speed, background and reflective materials is already evaluated for a conservative robotic-safety context. | [K] | Gimpelj & Munih, published 13 Jul. 2025, Sensors 25(14):4385, DOI https://doi.org/10.3390/s25144385 ; official PDF https://mdpi-res.com/d_attachment/sensors/sensors-25-04385/article_deploy/sensors-25-04385-v2.pdf | Abstract, p. 1; Sec. 1, pp. 2--3; Sec. 2, pp. 3--7; Sec. 3, pp. 8--12; Sec. 4, pp. 12--16; Sec. 5, p. 17. | Single-point/dToF configurations, not D1's exact multi-zone module.  It directly occupies the finite condition-map contribution family. |
| At a fixed sample count and schedule-independent event timing, interval variability increases missed-event risk. | [K] | Loreti et al., IEEE IoT Journal 6(6), 2019, pp. 9908--9918, DOI https://doi.org/10.1109/JIOT.2019.2933335 | Sec. I, p. 9909 and Fig. 1/residual-lifetime argument; checked in the 2026-08-28 AS1 audit. | Conditional, not a universal theorem for informative sentinels. |
| Three-valued trace verdicts under recording uncertainty are established. | [K] | Wang et al., RV 2011 / LNCS 7186, 2012, pp. 442--456, DOI https://doi.org/10.1007/978-3-642-29860-8_35 ; official author-accessible record https://repository.upenn.edu/entities/publication/4614b8f7-efd0-4253-bc4e-1657f702ad6e | Sec. 1, p. 442; Secs. 2--3, pp. 443--449; conclusion, p. 455. | Different physical domain; it kills generic R1 semantics rather than a finite fault experiment. |
| The current candidates cannot distinguish the counterexample pairs described in the identification audit. | [KILL] logical consequence | Candidate observation models in the canonical register, read 2026-08-29. | C4/E/D1/AS1/R1 rows and their declared inputs/actions. | Conditional counterexamples; not an assertion about real-world event or fault frequency. |

## Queries and failed searches

- `2024 2025 "raw transmission" "local processing" sensor scheduling edge deadline paper`
- `"To Compute or Not to Compute? Adaptive Smart Sensing" Ballotta pdf`
- `2024 2025 adaptive sensing selectively wake high power sensor event detection energy paper`
- `2024 2025 time-of-flight sensor reflective material angle ambient light uncertainty detection paper`
- `2024 2025 edge sensing decision margin scheduling latency accuracy threshold action paper`
- `2024 2025 ToF sensor safety reflective geometry physical measurement error`

Limited retrievals:

- Ballotta's author-hosted PDF returned a Cloudflare challenge on 2026-08-29.  The final DOI, author/title, pages, and section mapping were corroborated by the prior validation packet; this audit does not rely on a new unverified claim beyond that already-read text.
- No inspected source establishes that an independent reference/logger is an online observation for E/AS1.  Treat it as offline evaluation only unless a future candidate changes the information flow.
- No result of these queries is treated as evidence that no other direct neighbor exists.

## Decision

**KILL.**  Do not advance any of C4, E, D1, AS1, or R1 as the locked FYP direction in its current form.  Each may supply a bounded negative-control or replication appendix, but none has survived all three Amber rounds as a distinct research mechanism.

KILL
