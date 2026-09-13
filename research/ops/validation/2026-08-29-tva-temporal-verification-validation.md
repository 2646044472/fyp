# Validation Audit: 2026-08-29 TVA temporal-verification admissibility audit

## Decision investigated

Whether TVA should advance from Amber/HOLD: a low-power sentinel decides at time `t0` whether to wake a verifier; after verifier readiness at `tr`, a post-ready observation is used to label an event in the earlier target interval `W = [t0, t0 + w]`.  TVA proposes to expose error in the naive miss-rate estimate with interval logs, an independently time-synchronised original-time reference, and a reserved reference-only evaluation pool at equal verifier budget.

## Claim under test

The claim is that, on predeclared duration/readiness cells, the proposed protocol is a distinct edge-sensing contribution because it either (a) identifies a nonzero error in the naive `Pr(missed event)` estimate or (b) returns `not label-admissible` rather than false precision.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Cao et al. explicitly model finite sensor warm-up before reliable readings and state that a short-lived event is detected only when it intersects a waking period.  SmartON evaluates catch and energy against a ground-truth system that catches all events.  Time-synchronised reference instrumentation and direct logger comparison are established sensor-network evaluation practice. | TVA names the issue "label admissibility" rather than detector coverage.  The inspected work does not use that phrase or exactly the same two-stage bench. | High that the physical components and measurement controls are established; low that terminology makes a material difference. |
| Exact-claim collision | No inspected paper states the exact proposed estimator wording: post-ready verifier labels for an earlier sentinel window, with a reserved reference-only pool.  However, the claimed result is a direct consequence of the established overlap condition, and the proposed controls are standard measurement/reference controls rather than a new action or estimator. | A hardware-bounded report of a particular board/sensor pair's readiness-duration cells could be a useful replication result. | Medium.  The 2024-2026 forward-citation chain has a retrieval gap, so this is not a global absence claim. |
| Boundary / impossibility | If `tr > t0 + w`, construct two traces with the same sentinel decision, same interval log, and identical physical state from `tr` onward: one has a transient event wholly in `W`; the other has no event.  A verifier that starts at `tr` produces the same observation in both.  The original-time event label and hence the miss rate are not identifiable from the online records. | Adding a continuous external reference identifies the *bench truth* for those trials, but it does not make a delayed verifier an observation of the original interval. | High for the stated observation model. |

## Assumption and identification audit

### The decisive observation boundary [KILL]

Let the online record be `R = (sentinel trace, t0, tw, tr, verifier samples on [tr, tr+q])`.  For a transient event `E1` entirely inside `W` and a no-event trace `E0`, choose the same sentinel output (a false negative in `E1`) and equal post-`tr` state.  Then `R(E1) = R(E0)` while `Y_W(E1) = 1` and `Y_W(E0) = 0`.  No function of `R` can recover `Y_W` without one of the following extra assumptions: continuous reference coverage, an observation overlapping every relevant part of `W`, or a verified event-persistence model.  This is the same physical overlap limitation formalised for low-duty-cycle sensing by Cao et al.; it is not a new estimator boundary.

### Interval logging does not create a research mechanism [KILL]

`t_decision`, `t_wake`, `t_ready`, and verifier integration bounds are necessary provenance.  A fixed rule already implements the honest report: if the verifier did not continuously observe the target interval (or a predeclared, validated persistence condition does not hold), report `unknown/not label-admissible`; otherwise evaluate its measurement error against the reference.  The interval log cannot reveal a transient that happened before readiness.  Consequently, TVA's proposed abstention outcome is a direct baseline, not evidence that an "admissibility-aware" protocol contributes beyond instrumentation.

### The reference-only pool is either an offline oracle or remains selectively labelled [KILL]

1. If the reference continuously records every trial and the pool is merely withheld until evaluation, it is a legitimate laboratory instrument but an offline oracle.  The claimed edge verifier budget excludes the reference's sensing, timing, storage, and calibration cost.  The experiment can measure the focal device, but cannot claim a resource frontier for the complete sensing system.  SmartON's ground-truth all-event system and Werner-Allen et al.'s colocated data loggers are direct precedents for this *evaluation control*.
2. If the reference is only sampled for a subset, selection must be random independently of sentinel output, readiness, duration, board condition, and unobserved event state, with nonzero inclusion probability for every estimand cell.  Otherwise it is the standard selective-label problem: the decision to test determines access to outcome labels.  Chang and Wiens explicitly formalise this setting.  A held-out pool cannot identify error in cells with zero reference coverage.
3. If the event source is a programmed actuator with an exact timestamp and duration, the actuator log itself already supplies original-time truth.  In that case the proposed reference is redundant and the result reduces to the deterministic readiness-duration overlap map (BMAP), not an edge method.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Cao, Abdelzaher, He, Stankovic, *Towards Optimal Sleep Scheduling in Sensor Networks for Rare-Event Detection*, IPSN 2005, DOI: https://doi.org/10.1109/IPSN.2005.1440887 | Duty-cycled sensors, finite warm-up/sample/processing interval, sleep schedule. | Detection delay and short-lived-event detection probability under energy/duty-cycle constraints. | Sec. II says readings are reliable only after finite warm-up and an event is detected only if its lifespan intersects a waking period. | **Kills the claimed physical boundary as new.** TVA can at most instantiate the known coverage condition for a particular board. |
| Luo and Nirjon, *SmartON: Just-in-Time Active Event Detection on Energy Harvesting Systems*, DCOSS 2021, DOI: https://doi.org/10.1109/DCOSS52077.2021.00018 | Wake frequency/action under energy constraints; image/audio event detection. | Total catches and energy efficiency; baseline `GT` catches all events; event duration is varied. | Uses an all-event ground-truth comparator at fixed sensing-energy evaluation, exactly the kind of external truth TVA calls a reference-only pool. | **Kills the reference-instrument/budget framing as distinct.** It does not make a post-ready observation a label for the past; it reports coverage directly. |
| Werner-Allen et al., *Fidelity and Yield in a Volcano Monitoring Sensor Network*, OSDI 2006, official paper: https://static.usenix.org/event/osdi06/tech/full_papers/werner-allen/werner-allen_html/osdi.html | Event-triggered wireless sensing, time rectification, reference loggers. | Sensor network assessed as an instrument using data fidelity, yield, event detection accuracy, and timing; it compares against colocated GPS-synchronised loggers. | Reference-instrumented audit of data timing/fidelity and missed events. | **Kills presenting a colocated original-time reference and measurement-validity audit as a new systems contribution.** TVA's two-device wake bench differs in domain but not in evaluation principle. |
| Chang and Wiens, *From Biased Selective Labels to Pseudo-Labels*, ICML 2024, PMLR 235:6286-6324, official PDF: https://raw.githubusercontent.com/mlresearch/v235/main/assets/chang24e/chang24e.pdf | A decision controls testing/label acquisition; observed proxy labels may differ from truth. | Bias-aware learning/evaluation with observed-label indicator and assumptions. | TVA's verifier-wake decision determines whether a post-decision label exists. | **Kills any new random-audit/propensity-correction mechanism.** It leaves only a physical coverage measurement, which the first three rows already constrain. |
| Gehrig et al., *Low-latency automotive vision with event cameras*, Nature 629 (2024), 1034-1040, https://doi.org/10.1038/s41586-024-07409-w | Event/RGB timing synchronisation and inter-frame ground-truth construction. | Hardware sync error is measured; tracks changing between frames are excluded before interpolation. | Shows temporal alignment/exclusion are already recorded label-construction conditions. | **Kills RLOG as a thesis component.** It does not exactly address a wakeable verifier. |
| Monjur et al., *SoundSieve: Seconds-Long Audio Event Recognition on Intermittently-Powered Systems*, MobiSys 2023, DOI: https://doi.org/10.1145/3581791.3596859; author version: https://arxiv.org/abs/2305.16445 | Intermittent samples over on/off cycles, energy/content-aware wake and imputation. | Classification of events whose samples are intermittently unavailable. | Explicitly treats missing parts of temporally extended events as a fundamental intermittent-sensing issue. | **Further reduces the novelty of an intermittent/late-observation story.** Its task is classification, not reference-label admissibility. |

## Strongest simple baseline

Use the normal, frozen interval guard:

```
if verifier coverage does not cover the declared original-time target interval:
    report UNKNOWN (do not use verifier value as Y_W)
else:
    report verifier label, with calibration error measured against reference
```

For a controlled finite-duration event generator, replace the final comparison with the generator's timestamp log.  This baseline matches TVA's `not label-admissible` action, needs no learned method or excluded-pool estimator, and yields the same readiness-duration boundary map.  If TVA beats it, the extra action/assumption that enables this remains unspecified [GAP].

## Contrarian result

**[KILL] TVA does not survive as a standalone research direction.** Its positive hypothesis is predetermined whenever the protocol includes a cell in which a transient event finishes before readiness: the delayed verifier cannot observe that event.  Its negative hypothesis (no material distortion in the selected box) is only a component-specific measurement.  Both outcomes are honest and useful engineering evidence, but neither supplies a new edge action, observation model, endpoint, or guarantee beyond known duty-cycle coverage and standard reference-instrumented evaluation.

The only defensible remnant is **PIVOT BMAP**: a carefully documented, reproducible hardware measurement appendix for a later research candidate that has its own decision and mechanism.  It must not be described as a novel adaptive-sensing or reliability method.

## Feasibility audit

| Requirement | Audit |
| --- | --- |
| Hardware | A low-cost MCU, photogate/light source or wired pulse source, and a second reference logger are obtainable in principle [C].  However, a true original-time reference must be independently sampled and synchronised; using the same MCU clock, power rail, trigger line, or sensor physics creates common-mode error [GAP]. |
| Clock and readiness label | Firmware timestamps alone do not establish when the physical verifier produced a reliable sample.  A scope/logic-analyser signal tied to physical readiness, measured clock error, and an integration-window definition are required.  Gehrig et al. treat synchronization error and exclusion rules as experimental conditions, not incidental logs. |
| Ground truth | A programmed stimulus gives exact event timing but makes the central result tautological geometry.  A physical mechanical/light event needs a calibrated, independently time-aligned reference whose own detection error and bandwidth are reported. |
| Energy accounting | Matching the woke verifier's on-time is feasible.  It does not match total energy if a continuous reference is excluded; including the reference makes the always-on reference baseline dominant and defeats the claimed low-energy story. |
| Data/ethics/compute | Benchtop non-personal data and MCU-scale logging are feasible.  No special dataset or compute is needed. |
| Schedule | A December demonstration is feasible, but it demonstrates timing instrumentation and a known coverage limit.  It does not de-risk the missing thesis-level mechanism by the 2027-H1 evaluation window. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Duty-cycled sensors have finite warm-up before reliable readings; a short-lived event is detected only when it intersects a waking interval. | [K] | Cao et al., IPSN 2005, official author PDF: https://www.cs.virginia.edu/~stankovic/psfiles/IPSN2005_Paper.pdf ; DOI: https://doi.org/10.1109/IPSN.2005.1440887 | Sec. II, PDF pp. 1-2 (proceedings pp. 20-21), especially warm-up model and paragraph beginning "Finally, observe". | It treats spatial rare-event coverage, not a two-stage verifier, but establishes the required physical overlap boundary. |
| A ground-truth system that catches all events is used as the evaluation baseline for adaptive event detection; event duration and energy are explicit variables. | [K] | Luo and Nirjon, DCOSS 2021 author PDF: https://yuboluo.github.io/publication/06_smarton/06_SmartON.pdf ; DOI: https://doi.org/10.1109/DCOSS52077.2021.00018 | Sec. V.B-D, PDF p. 7 / proceedings p. 41: parameters, metrics, and `GT` baseline; Sec. VI.C, PDF pp. 7-8 / proceedings pp. 41-42. | Energy-harvesting scheduler, so not an exact TVA task; it directly undercuts treating all-event reference measurement as a new evaluation apparatus. |
| Sensor networks can be evaluated as scientific instruments using timing/data fidelity/yield and colocated reference loggers; a reference can expose missed events and timing error. | [K] | Werner-Allen et al., OSDI 2006, official USENIX paper: https://static.usenix.org/event/osdi06/tech/full_papers/werner-allen/werner-allen_html/osdi.html | Sec. 1, online pp. 1-2 (continuous sampling, data fidelity/yield, direct logger comparison); Sec. 3, p. 4 (colocated GPS logger); Secs. 5 and 7, pp. 7-10 (reference event comparison and known-timebase validation); Sec. 10, p. 12 (ground truth/self-validation lesson). | Field sensing rather than wake-on-demand, but directly precedes TVA's measurement-validity framing. |
| A decision controlling testing controls access to a label; naive use of observed proxies induces label bias. | [K] | Chang and Wiens, ICML 2024, PMLR 235:6286-6324, official PDF: https://raw.githubusercontent.com/mlresearch/v235/main/assets/chang24e/chang24e.pdf | Abstract and Secs. 1-3, PDF pp. 1-4. | Clinical selective labels rather than physical sensing.  It kills a generic selectively-labelled estimator, not the overlap physics. |
| Hardware synchronization error and exclusions in ground-truth construction must be explicitly characterised. | [K] | Gehrig et al., Nature 629 (2024), 1034-1040, official article: https://doi.org/10.1038/s41586-024-07409-w | Methods: "Comments on time synchronization" and "Ground truth generation for inter-frame detection", online article accessed 2026-08-29. | Different sensing hardware.  Supports only the instrumentation/control conclusion. |
| Intermittent sensing can leave portions of temporally extended events missing and those portions may not be recoverable by imputation. | [K] | Monjur et al., MobiSys 2023, author version: https://arxiv.org/abs/2305.16445 ; official DOI: https://doi.org/10.1145/3581791.3596859 | Abstract, arXiv v1 dated 2023-05-25; official MobiSys listing: https://www.sigmobile.org/mobisys/2023/accepted-papers.html | Audio classification, not prior-window label validity. |
| No later 2024-2026 paper exactly matching TVA's post-ready-label plus excluded-pool wording was found. | [GAP] | Queries below, run 2026-08-29. | Search results inspected, no complete citation graph available. | This is not evidence of novelty and does not counter the component/boundary kill. |

## Queries and failed searches

Queries run 2026-08-29:

- `site:dl.acm.org wake-up sensor readiness time event detection ground truth duty cycle evaluation`
- `site:ieeexplore.ieee.org duty cycled sensor delayed wake event detection missed events ground truth`
- `"wake-up" "ground truth" event detection sensor duty cycling`
- `"selective labels" sensor evaluation randomized audit ground truth edge sensing`
- `"event detection" "duty cycling" "ground truth system" sensor network paper`
- `"wake-up latency" "missed events" sensor system paper`
- `"short-lived events" duty cycling sensor detection missed event`
- `"event duration" "wake-up delay" sensor event detection`
- `"Towards Optimal Sleep Scheduling in Sensor Networks for" cited 2024 2025`
- `"SmartON: Just-in-Time Active Event Detection" cited`

The search recovered direct foundational coverage/ground-truth work and later intermittent sensing, but not a complete forward-citation graph for every source or a 2024-2026 paper using TVA's exact terminology.  That unresolved retrieval is recorded as [GAP], not claimed as a gap in the literature.

## Decision

**KILL.** Do not promote TVA as an FYP research mechanism.  Retain the interval record, independent reference, and readiness-duration experiment only as a BMAP measurement/negative-control appendix for another candidate with a separately defensible action and contribution.
