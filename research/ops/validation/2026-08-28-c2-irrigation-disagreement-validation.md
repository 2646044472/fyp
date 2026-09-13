# Validation Audit: 2026-08-28 C2 soil-moisture / water-balance disagreement

## Decision investigated

Whether C2 can advance as a low-cost edge-computing FYP: a small-farm operator observes one cheap capacitive soil-moisture probe, a local water-balance estimate, and an actuation/weather log, then selects `irrigate / wait / inspect` when probe and model disagree.  The proposed contribution is a bounded disagreement-aware decision rule that reduces water waste and plant-risk cost at a fixed water budget.

This is a falsification audit.  Constraints used: affordable equipment can be self-purchased; a benign demo is needed by 2026-12 and repeated experiments can extend through 2027-H1; no personal data or safety-critical production actuation.  The candidate is not evaluated as a garden-automation demo.

## Claim under test

The claim can only be meaningful if, on predeclared planter/soil/crop/fault cells, disagreement between (a) a low-cost probe and (b) a water-balance model identifies an impending wrong `irrigate` decision sufficiently better than a cheap hysteretic threshold plus `wait / inspect` rule.  The endpoint must be externally measured water use and plant/soil state, not merely agreement with the model or a prettier dashboard.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | **[KILL]** Aranda et al. already combine low-cost capacitive soil sensors, a physical Hydrus 1D water-flow model, bias/noise correction and a high-precision reference in a drip-irrigated farm.  Their Sec. 4 explicitly evaluates irrigation-control consequences under biased versus corrected readings.  Dominguez-Nino et al. already combine FAO water balance and capacitance-sensor feedback for automated irrigation. | A three-action *deferral* vocabulary and a deliberately tiny single-planter rig are not shown identical in those papers.  That is an application/protocol difference, not yet a technical mechanism. | High component collision; low confidence in a substantive remainder. |
| Exact-claim collision | **[KILL]** Conde et al. (2024) already use soil moisture, rain, temperature, irrigation and forecasts to give practical irrigation instructions while accounting for human intervention.  Boukri et al. (2026) already deploy an ESP32, low-cost capacitive sensor, environmental inputs, threshold irrigation and remote/manual oversight.  Aranda's simulated MPC evaluates the very asymmetric harms in C2: high probe reading gives insufficient irrigation/stress; low reading gives excess water/pump cost. | **[GAP]** I did not retrieve a primary paper that uses exactly one cheap probe *versus* a local water-balance residual to decide `irrigate / wait / inspect`, with the candidate's matched water/plant-risk budget.  A failed exact-phrase search is not novelty evidence. | High collision with the decision setting; medium exact-mechanism risk because the narrow residual wording was not located. |
| Boundary / impossibility | **[KILL]** From one probe value and one model prediction alone, residual sign/magnitude does not identify whether the probe is biased, the irrigation-flow/input log is wrong, the model parameters are wrong, or spatial soil/root-zone variation is real.  Aranda requires a ThetaProbe reference to validate correction and notes unknown irrigation amounts/model-input limits; Raheja et al. show output varies across sensors, compaction and EC.  Thus two worlds can expose identical `(probe, model)` disagreement while the correct irrigation action differs. | A conditional *empirical* claim is identifiable only if an independent original-time truth channel is specified, such as destructive gravimetric samples across replicate planters plus measured irrigation mass and a predeclared proxy for plant stress.  That is absent from C2 and cannot be recovered by synthetic offsets alone. | High for the observability objection; no universal impossibility theorem is claimed. |

## Assumption and identification audit

1. **Disagreement is a symptom, not a labelled fault.**  `[KILL]` A residual `r_t = probe_t - model_t` can arise from sensor offset/dry contact, model hydraulic parameters, wrong emitter flow, rain/ET input error, sensor placement relative to wet bulb, or actual local spatial heterogeneity.  Aranda, *Sensors* 2024, pp. 2--4 (PDF pp. 2--4), explicitly treats both observation and model-parameter bias and requires physical constraints; pp. 19--21 validates against ThetaProbe.  The candidate has only one measurement and no stated independent reference.

2. **Synthetic injected fault labels do not establish the story's real fault rate.** `[KILL]` An artificial offset, missing sample, or dry-contact event labels the injector, but not the actual cause of an ordinary field disagreement.  It can support a limited injected-fault benchmark only.  It cannot substantiate a claim that the policy protects small-farm irrigation against naturally occurring uncertainty without external soil/plant truth.

3. **`inspect` has no operational definition or cost.** `[GAP]` C2 does not specify whether inspection is a gravimetric sample, a commercial reference probe, a human visual check, or a manual volume/line-flow audit; nor its duration, water consequence, or availability.  The cost budget and resulting decision loss are therefore not computable.

4. **Plant risk is not observable from the current proposal.** `[KILL]` A soil-moisture threshold is soil-, crop-, root-depth-, growth-stage- and placement-specific.  Recent field papers obtain field capacity/wilting point, local calibration, ET inputs and/or physiological reference measures; a one-pot moisture trace cannot establish a general "plant-risk" endpoint.  A claim limited to a named soil/crop/planter and a declared proxy could be testable, but it would no longer support the current small-farm story.

5. **The edge constraint is not load-bearing.** `[KILL]` The proposed decision can be evaluated on an ESP32 offline, but no source-verified intermittent-connectivity, latency, energy, or retained-data condition changes the decision frontier.  Boukri et al.'s 2026 low-cost deployment already includes ESP32 and remote monitoring; removing the cloud is an implementation choice, not yet an edge research constraint.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Aranda Britez et al., *Improving the Calibration of Low-Cost Sensors Using Data Assimilation*, *Sensors* 24, 7846, published 2024-12-08, https://doi.org/10.3390/s24237846; open VOR https://researchonline.ljmu.ac.uk/id/eprint/25192/1/Improving%20the%20Calibration%20of%20Low%20Cost%20Sensors%20Using%20Data%20Assimilation.pdf | SoilWatch capacitive sensor, Hydrus 1D, PF/IES, irrigation input, high-precision ThetaProbe; outputs corrected moisture for irrigation control. | Secs. 2--3, PDF pp. 4--22: calibration/field validation.  Sec. 4, pp. 23--25: simulated MPC with moisture limits, pump/water costs and over-/under-estimated sensor scenarios. | Low-cost soil sensing + physical/water model + mismatch/bias + irrigation harm. | **[KILL]** new calibration, data-assimilation, physical-consistency, or biased-sensor irrigation-control framing.  Leaves only a much weaker source-frozen three-action evaluation, which must beat its corrected-estimate/MPC and simple threshold baselines.  Data are "available on request" (p. 26), so it is not a ready raw-data artifact. |
| Conde, Guzman & Athelly, *Adaptive and predictive decision support system for irrigation scheduling: An approach integrating humans in the control loop*, *Computers and Electronics in Agriculture* 217, 108640, Feb. 2024, https://doi.org/10.1016/j.compag.2024.108640 | Soil moisture, rain, temperature, irrigation, forecasts, model/estimation/control; produces irrigation instructions accounting for manager intervention. | Official abstract and introduction/process-description text: https://www.sciencedirect.com/science/article/pii/S0168169924000310 (read 2026-08-28); DOI/venue confirmed by DBLP: https://dblp.org/rec/journals/cea/CondeGA24.html. | The operator decision, weather/model inputs, changing conditions and human-in-the-loop action are direct neighbors. | **[KILL]** generic `irrigate / wait / human check` decision-support story.  Exact residual-based abstention and one-probe apparatus are not verified from the accessible full text: **[GAP]**. |
| Raheja et al., *Designing and field calibration of low-cost microcontroller-based soil moisture sensor for subsurface drip-irrigation system*, *Scientific Reports* 15, 35948, VOR 2025-10-15, https://doi.org/10.1038/s41598-024-81288-z | Four low-cost capacitive probes, ESP8266, local calibration/empirical alternative, ET/FAO scheduling, commercial SM150T and gravimetric comparison. | Methods, web pp. 4--8: sensor placement, ET/FAO water balance, gravimetric truth and calibration; Results pp. 8--11: sensor-to-sensor/EC variation; Conclusion pp. 12--13: four sensors outperform one and further crop/EC study is needed.  Open VOR: https://www.nature.com/articles/s41598-024-81288-z | Cheap local sensing, water-balance scheduling, calibration, reference comparison and low-cost microcontroller are all present. | **[KILL]** low-cost board/sensor deployment as contribution; supports the identification failure of one uncalibrated probe.  It does not test C2's exact wait/inspect residual rule. |
| Boukri et al., *Analysis and experimental implementation of affordable smart irrigation system using IoT to reduce agricultural costs and minimize water usage*, *Applied Water Science* 16:36, VOR 2026-01-20, https://doi.org/10.1007/s13201-025-02727-4 | ESP32 + capacitive sensor + DHT11 + threshold pump logic + Blynk notification/manual control. | Sec. 2/implementation, pp. 3--7: 20%/80% threshold controller and user loop; Sec. 4, p. 9: 30-day water-use evaluation; Sec. 6, p. 12: sensor drift, Wi-Fi and soil-texture limitations. Open PDF: https://link.springer.com/content/pdf/10.1007/s13201-025-02727-4.pdf | Same cheap hardware class, real-time local sensor decision and user oversight. | **[KILL]** Pi/ESP32 deployment, threshold control, dashboard or low-cost water-saving demo.  Its raw data are on request (p. 12).  It leaves a properly identified reliability method only. |
| Dominguez-Nino et al., *Differential irrigation scheduling by an automated algorithm of water balance tuned by capacitance-type soil moisture sensors*, *Agricultural Water Management* 228, 105880, 2020, https://doi.org/10.1016/j.agwat.2019.105880 | FAO water balance locally adjusted by capacitance sensors; automated irrigation scheduling. | Official abstract, https://ideas.repec.org/a/eee/agiwat/v228y2020ics0378377419315641.html, read 2026-08-28: two-year orchard trial, automated sensor feedback, manual water balance and lysimeter comparison. | The exact composite "water balance + capacitive soil-moisture feedback" pre-exists. | **[KILL]** component combination.  The older date does not replace the 2024--2026 neighbor check; it shows C2's central architecture is established. |

## Strongest simple baseline

**Source-calibrated hysteretic moisture threshold plus deterministic `wait / inspect` band.**

At moisture below a predeclared lower threshold, irrigate; above an upper threshold, wait; inside the band or on missing/out-of-range readings, request the same inspection that C2 permits.  Tune both thresholds and the persistence/window on the same source episodes as C2.  This baseline has the same three actions, sensor, water budget and manual-review cost, but no water-balance residual or fault classifier.

The second required baseline is **a locally calibrated probe plus FAO/water-balance feedback**, not a raw fixed threshold: it is exactly the established architecture in Dominguez-Nino et al. and Narang et al.  If C2 cannot beat both at matched water, inspection and measured plant/soil-risk budgets, its disagreement signal is unnecessary.

## Contrarian result

**[KILL] C2 should not be promoted in its current form.**  Recent primary work already supplies the low-cost embedded irrigation system, human-in-loop recommendation, sensor/model calibration and the asymmetric water-stress/over-water story.  More importantly, C2's proposed observation does not identify which member of the sensor-model pair is wrong.  A residual-to-`inspect` policy can be a sensible conservative engineering heuristic, but without an independent decision-time or evaluation-time truth channel it cannot establish the claimed reduction in plant risk rather than simply transfer false confidence between two fallible estimates.

The most honest negative result is therefore not "the model was worse": it is a finite counterexample/measurement finding that, for the declared pot/soil/crop/fault cells, the residual adds no benefit beyond hysteresis + `wait / inspect`, or that inspection/reference frequency required to resolve disagreement removes the low-cost advantage.

## Feasibility audit

| Requirement | Finding | Consequence |
| --- | --- | --- |
| Benign demo by 2026-12 | `[K]` A single pot, ESP32, capacitive probe, scale/flow log and manual pump override are inexpensive and technically buildable. | This demonstrates instrumentation only.  It does not validate a small-farm action or C2's claim. |
| Truth labels | `[KILL]` No existing raw dataset/artifact has been verified to contain C2's probe, full irrigation/log/weather inputs, model parameters, independent soil truth and plant-risk labels.  Aranda and Boukri state data are available on request; C2 has no secured access. | A new collection needs multiple replicate planters, destructive gravimetric samples or a calibrated reference, measured inflow/outflow, and a predeclared plant/soil endpoint. |
| Model inputs | `[KILL]` Hydrus/FAO-style water balance needs local soil hydraulic properties, emitter flow/rain/ET and crop/soil parameters.  Aranda's reported computation is offline (PF 19--104 minutes, p. 22) and needs reference validation; it is not a plug-in rule for an uncharacterized pot. | The FYP cannot honestly claim an inexpensive real-time physical-model controller unless it freezes a simpler model and independently audits its inputs. |
| Time and biology | `[GAP]` The user has one year, but no crop, soil, pot count, growth-cycle duration, reference device, watering authority or agronomy support is confirmed. | Without those commitments, repeated cross-cell causal measurements of stress/yield are unplanned.  A short demo risks becoming an uninformative threshold dashboard. |
| Ethics/safety | `[K]` No personal data are necessary; water/pump actuation is non-hazardous only with containment, low voltage, manual override and no claim of crop-production safety. | This does not repair the scientific identification gap. |
| Edge relevance | `[KILL]` No connectivity/energy/latency/data-retention constraint has been specified that makes local execution change the decision endpoint. | Treat edge deployment as implementation unless a genuine offline-continuity or local-data constraint is independently introduced and measured. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Low-cost capacitive sensor + Hydrus/PF/IES + reference validation already corrects bias; their irrigation-control analysis quantifies both excess-water and water-stress consequences of biased readings. | `[KILL]` | Aranda Britez et al., *Sensors* 24, 7846, VOR 2024-12-08, https://doi.org/10.3390/s24237846; open VOR PDF above. | Abstract/PDF p. 1; Sec. 1 pp. 2--4; Secs. 2--3 pp. 4--22; Sec. 4 pp. 23--25; Sec. 6 p. 26. | Sec. 4 is a simulation from farm data, not a direct C2 three-action trial.  Data are available on request (p. 26). |
| A low-cost ESP8266 capacitive-sensor system uses ET/FAO scheduling, gravimetric field calibration and a commercial reference; sensor-to-sensor, EC and compaction effects make universal calibration invalid. | `[KILL]` | Raheja et al., *Scientific Reports* 15, 35948, VOR 2025-10-15, https://doi.org/10.1038/s41598-024-81288-z | Methods pp. 4--8; Results pp. 8--11; Conclusions pp. 12--13; web VOR link above. | Sugarcane/SDI setting with four probes, not a one-pot FYP.  It substantiates a one-probe reference/placement gap rather than the exact action-rule collision. |
| A current low-cost ESP32 irrigation system already implements capacitive-sensor threshold control, real-time monitoring, notifications and manual control; it reports drift/Wi-Fi/soil-texture limitations. | `[KILL]` | Boukri et al., *Applied Water Science* 16:36, VOR 2026-01-20, https://doi.org/10.1007/s13201-025-02727-4 | Sec. 2 pp. 3--7; Sec. 4 pp. 9--10; Conclusion/future directions pp. 12--13. | Field/result claims are paper-specific and raw data are on request.  This kills deployment novelty, not a well-defined reliability boundary. |
| Human-in-the-loop, model/forecast/sensor irrigation recommendations are a direct current decision-support neighbor. | `[KILL]` | Conde, Guzman & Athelly, *Computers and Electronics in Agriculture* 217, 108640, 2024-02, https://doi.org/10.1016/j.compag.2024.108640 | Official abstract and introduction/process-description text at ScienceDirect (retrieved 2026-08-28); bibliographic record at DBLP. | Full publisher PDF was not accessible in this audit; exact section/page mapping is **[GAP]**.  Do not use it to claim exact residual-rule collision. |
| FAO water balance plus capacitance feedback for automated scheduling was already tested in an orchard. | `[KILL]` | Dominguez-Nino et al., *Agricultural Water Management* 228, 105880, published 2020, https://doi.org/10.1016/j.agwat.2019.105880 | Official abstract (URL above), read 2026-08-28. | Older foundational component collision; full paper access was restricted. |
| No primary source retrieved establishes C2's exact one-probe residual-to-`irrigate / wait / inspect` rule, its cost definition, or a source/target evaluation protocol. | `[GAP]` | Searches listed below, 2026-08-28. | Search boundary only. | Absence of a hit is not absence of prior work. |

## Queries and failed searches

Queries executed on 2026-08-28:

- `low cost soil moisture sensor irrigation decision water balance sensor fault detection 2024 2025 2026 paper`
- `soil moisture water balance sensor fault irrigation 2024 pdf`
- `soil moisture sensor fault detection irrigation 2024 2025 pdf`
- `irrigation scheduling soil water balance soil moisture sensor 2025 2026 decision support`
- `data assimilation low cost soil moisture irrigation 2024 Aranda`
- `Adaptive and predictive decision support system for irrigation scheduling DOI`
- `soil moisture sensor fault detection irrigation site:mdpi.com 2025`
- `Improving the Calibration of Low-Cost Sensors Using Data Assimilation cited by 2025 2026`
- `sensor disagreement irrigation soil moisture`

Limited/failed retrievals:

- The Conde 2024 publisher full text was access-restricted; exact-page and exact-residual-rule checks are therefore `[GAP]`.
- The 2026 olive-orchard SAAM paper (Bonet et al., *Agricultural Water Management* 324, DOI https://doi.org/10.1016/j.agwat.2026.110131) was found as a recent continuation of capacitive-sensor + ET0 balance scheduling, but its full text was restricted; it is not load-bearing evidence here.
- No public raw dataset/code was retrieved that can test C2's claimed target without new collection.  Aranda and Boukri report data on request; this is a feasibility blocker, not evidence against their results.
- No exact one-probe disagreement/triage paper was retrieved.  This remains `[GAP]`, not a novelty claim.

## Decision

**KILL.**  Do not spend the FYP on C2 as currently stated.  Its components and decision story are crowded; its key residual cannot identify fault versus model/soil variation; edge relevance is unproved; and its required independent truth, inspection cost and plant-risk endpoint are not secured.  Retain only the reusable protocol lesson: any future low-cost sensing candidate that acts on model/sensor disagreement must predeclare an independent truth channel, an inspection action/cost and hysteresis-plus-inspection baseline.

KILL
