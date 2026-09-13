# Validation Audit: 2026-08-28 R1 outage-provenance thermal evidence

## Decision investigated

Whether R1 should pass from Amber to a low-cost edge FYP direction.  R1 is a local temperature node which, during an offline outage, emits `known-safe`, `known-violation`, or `indeterminate` from a persisted record of samples/read failures, reboot epochs, supply state, and delivery state.  The proposed rig is an insulated non-hazardous bench; an independently powered reference logger is used only after the fact for scoring.

## Claim under test

For a fixed thermal-container and fault family, a source-local provenance record reduces reference-labelled benign episodes sent to `indeterminate`, without increasing reference-labelled violating episodes released as `known-safe`, at the same sampling and radio budget as retained latest value, MQTT QoS plus persisted sequence/epoch, online imputation, and `any gap => indeterminate`.

The claim must **not** mean that provenance establishes real product safety, or that it is a new logger/protocol.  A `known-safe` verdict can only mean *sound relative to the stated sensor-health, clock, persistence, rate-envelope, and fault assumptions*.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for a remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | [KILL] WHO's 2025 data-logger specification already requires relative time, a timekeeping-resumption marker (`RTCW`), temperature, supply availability, error records, battery state, on-board storage, power-outage recording, and optional CRC/hash/signature. It also defines heat, power, and external-monitor-disconnect alarms. This is the substantive content of R1's proposed evidence ledger. Runtime-verification work already evaluates an incomplete recorded trace with a three-valued `true / false / unknown` semantics. | [GAP] I did not find a primary paper combining this exact low-cost physical thermal rig, equal-budget comparison, and R1's stated endpoint. That absence is not a novelty result. | High component collision; low confidence that any mechanism remains. |
| Exact-claim collision | [K] Bagchi, Jenamani and Routray study missing-value estimation specifically for multivariate reefer IoT data (2024), and their 2025 short COMSNETS continuation again targets missing IoT data for reefer monitoring. The accessible official records describe imputation, not safe-release/indeterminate decisions. [K] The WHO logger and data-standard documents specify temperature-exposure, power, and disconnected-monitor records/alarm states in the same application area. | [GAP] The full PDFs for the 2024/2025 Bagchi papers could not be obtained, so their exact observations, outage model, and decision endpoint were not checked page by page. R1's proposed *evaluation endpoint* may differ, but the candidate has not identified a mechanism beyond a standard durable record followed by a conservative decision rule. | Medium-high risk; exact collision unresolved because primary text is inaccessible. |
| Boundary / impossibility | [KILL] If a healthy primary sensor and a stuck/plausible-reading primary sensor produce the same samples, read status, reboot, supply and delivery records, but the reference temperature histories differ in exposure, any deterministic R1 policy receives the same input in both worlds. It cannot soundly release `known-safe` in one and avoid an unsafe release in the other. Likewise, if two trajectories compatible with an outage gap and the claimed rate envelope have different threshold exposure, `known-safe` is not identifiable. The three-valued semantics is the appropriate conservative outcome, not a new guarantee. | A finite fault model, calibrated rate envelope, bounded timestamp error, crash-atomic persistence model, and independently logged reference trace make a conditional *boundary measurement* testable. It cannot support a claim beyond those cells. | High. |

## Assumption and identification audit

1. **The sensor is a missing observation channel.**  R1's ledger records whether the node acquired/persisted/delivered a value; it does not establish that a plausible value is physically correct.  A stuck-at, bias, thermal-contact, or shared-supply failure yields an observationally identical ledger to a healthy node unless the fault model excludes it or an independent channel is available.  Therefore the label must be `known-safe under F`, never unqualified safe.
2. **A thermal rate envelope is load-bearing.**  The proposed `sup_{h in H(O)}` release rule requires a pre-calibrated bound on temperature change for every claimed container, fill level, opening/heat input and ambient condition.  A pilot-derived average slope is not a bound.  Any target condition outside the calibration block is `indeterminate` by construction.
3. **Time/persistence are separate assumptions.**  A reboot epoch alone does not prove a sample was written before a crash.  The experiment must specify an atomic record format, commit acknowledgement, maximum timestamp error through resets, flash write-failure behavior, and what a torn final row means.  The official WHO specification itself treats uninterrupted time keeping and the `RTCW` resumption marker as explicit requirements, not a consequence of a counter.
4. **Delivery is not acquisition.**  MQTT QoS 1 offers at-least-once delivery and permits duplicates; it does not state whether a sensor read was attempted, failed, or durably persisted.  Conversely, delivery state cannot repair a missing local sample.  R1 may measure that distinction, but it must compare with a journal that explicitly records the same local state.
5. **Reference truth must survive the injected fault independently.**  A second logger is not ground truth merely because it is continuous.  It needs separately verified power/timekeeping, known response lag and uncertainty against the threshold, synchronized or bounded clock offset, and a log proving it stayed alive while the primary was interrupted.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| WHO/PQS/E006/DL01.3, *Data logger and machine-to-machine interface for Equipment Monitoring Systems*, revision 27 May 2025 | Relative time; `RTCW` after timekeeping disruption; temperature, supply availability, error data, battery, local storage; continuous/essential recording through power outages; integrity fields. | Official required logger behavior for vaccine cold-chain equipment. | Very high component/application overlap with R1's epoch, sample/read, supply and persisted-provenance record. | [KILL] a claimed new evidence-recording mechanism or “logger that makes outages auditable.” It leaves only a bounded comparative evaluation, not a new protocol. |
| WHO/PQS/E006/DS01.2, *Data standard for cold chain equipment monitoring systems*, 30 Nov. 2023 | Heat, freeze, door, power-outage and external-monitor-disconnect states; continuing/acknowledged alarm codes. | Standardizes temperature-exposure and power/connectivity states for this exact domain. | High on state vocabulary and decision story, though it does not use R1's three verdict names or equal-budget endpoint. | [KILL] presentation of thermal/power/disconnect state logging as the contribution. Leaves the question whether a named low-cost fault model supports more releases than a conservative gap rule. |
| Wang, Ayoub, Sokolsky & Lee, *Runtime Verification of Traces under Recording Uncertainty*, RV 2011 / LNCS 7186 (2012), pp. 442--456 | Abstract logged snapshots; outputs true / false / undecided by quantifying over concrete traces consistent with the record. | Sound temporal-property verdicts under recording uncertainty; simulated evaluation. | R1's `known-safe / known-violation / indeterminate` definition over all compatible histories is the same semantic pattern. | [KILL] a formal three-state verdict or compatible-history rule as R1's theoretical innovation. Physical temperature/rate modelling is different but must be framed as an application/measurement. |
| Leucker et al., *Runtime Verification for Timed Event Streams with Partial Information*, RV 2019 / LNCS 11757, pp. 273--291; arXiv:1907.07761v1 | Timed streams with known data gaps and imprecision; abstract events propagate uncertainty; reset can recover subsequent computation. | Sound outputs over incomplete traces, with implementation/evaluation. | Same observation problem: gaps, imprecise time/values, reset recovery, and conservative output. | [KILL] generic gap-propagation / reset-recovery algorithm claim. It leaves a physical calibration study only. |
| Bagchi, Jenamani & Routray, *A Novel Data Transformation for Improving Predictive Accuracy of Online Missing Value Imputation During Reefer Container Monitoring*, IEEE Sensors Journal 24(22), 15 Nov. 2024, pp. 38286--38297; and *Missing Value Imputation for IoT Data: With Applications to Reefer Container Monitoring*, COMSNETS 2025, pp. 805--807 | Reefer IoT streams with missing values; imputation methods. | Predictive missing-value accuracy / deployment for reefer monitoring in the immediately adjacent application. | Same outage/missing-data cold-chain context, but accessible official metadata does not prove a three-state release endpoint. | [KILL] any imputation contribution; [GAP] for exact R1 collision because the primary full texts were not obtainable. Online imputation is a required baseline, not evidence that filling a gap is safe. |

## Strongest simple baseline

**B-journal: durable write-ahead event ledger plus the identical conservative verifier.**  At every scheduled index it atomically appends `(epoch, index, local-time-or-error-bound, read-status, value-or-null, supply state, reset reason, journal-commit flag, message sequence, publish/PUBACK state)`.  The gateway deduplicates by `(epoch,index)`, then applies R1's same declared rate envelope and the same `sup/inf` compatible-history rule.  It uses QoS 1 for transfer but makes no learned prediction.

This is stronger than “MQTT QoS alone”: QoS is transport semantics; the ledger directly preserves every R1 input.  It has the same bytes to within encoding, no additional sensing, and can run on the same MCU/flash.  If B-journal matches R1, R1 has no systems or decision mechanism.  Since R1 currently describes precisely such a persisted record, the burden is on R1 to name an observation unavailable to B-journal; none is currently named.

Required secondary baselines:

1. retained last value with timestamp only;
2. QoS 1 + epoch/sequence journal, using a fixed `any unresolved gap => indeterminate` rule;
3. B-journal + rate-envelope verifier;
4. source-only online imputation, which must never turn an imputed value into `known-safe` unless the prior observation model proves that implication.

## Contrarian result

**[KILL] R1 is not a new local-provenance mechanism.**  The state fields are already specified in the closest operational standard, and the three-way evidence semantics and uncertainty propagation are established runtime-verification techniques.  The exact R1 record can be encoded by B-journal without a new algorithm.  A measured advantage over retained latest value or `any gap => indeterminate` would demonstrate that a complete local record is preferable to an incomplete one, not that R1 introduced a distinguishable method.

The honest residual is a **PIVOT**: pre-register a finite measurement question, “For this container, sampling interval, rate envelope and non-adversarial reset/read/loss fault family, which fields are necessary and sufficient for a sound trace verdict, and at what gap duration does every policy become indeterminate?”  It is useful even if B-journal equals every variant, but it must be presented as a boundary/replication study, not a new safety logger or generally transferable reliability method.

## Feasibility audit

| Item | Result | Gate consequence |
| --- | --- | --- |
| Hardware/ethics | [K] A benchtop insulated box, low-cost primary node, independent logger, controllable Wi-Fi loss and non-hazardous power/reset injection are plausible within the stated one-year window. No human data or safety actuation is required. | Feasible for a December demo, contingent on a BOM/pilot. This is feasibility, not contribution evidence. |
| Labels | [GAP] “Violation” requires a fixed threshold and exposure-duration rule plus a reference trace whose power, time, response lag, calibration and failure independence are demonstrated. The primary's own ledger cannot label its correctness. | Do not collect the main dataset until the reference/clock protocol and fault injection matrix are frozen. |
| Flash/reboot validity | [GAP] No actual MCU/flash endurance, atomic-append, brown-out/torn-write, RTC drift or reset-reason trace has been tested. | A crash-consistency pilot is mandatory. A counter increment is not adequate evidence of an acquired sample. |
| Physical scope | [KILL] A bench temperature box cannot certify a pharmaceutical/vaccine cold chain or estimate fault prevalence. WHO documents establish why temperature records matter, not that this rig meets their product specification. | Story must say “simulated temperature-sensitive asset record,” with no compliance or safety certification claim. |
| Evaluation | [GAP] The proposed primary endpoint needs episode-level confidence intervals, source/target or held-out fault/thermal cells, and a rule for repeated policy comparisons. Otherwise an apparent reduction in `indeterminate` may be a selected easy trace. | Register cells and scoring before implementation; report per-fault coverage and unsafe-release counts, not aggregate accuracy only. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Cold-chain logger standards already specify relative time, time-disruption recovery, temperature/supply/error data, local storage and outage operation. | [K] | WHO/PQS/E006/DL01.3, 27 May 2025, official PDF: https://extranet.who.int/prequal/key-resources/documents/pqs-performance-specification-e006dl012-data-logger-and-machine-machine-0 | Contents p. 1; Secs. 4.1--4.2.5, pp. 5--7; Secs. 4.2.6--4.2.8, pp. 9--10. | Product-performance standard, not a paper and not proof of exact R1 endpoint. It is decisive for component novelty. |
| Cold-chain data standard already records heat, power and disconnected-monitor conditions. | [K] | WHO/PQS/E006/DS01.2, 30 Nov. 2023, official PDF: https://extranet.who.int/prequal/key-resources/documents/pqs-performance-specification-e006ds012-data-standards-cold-chain-0 | Sec. 4.2, p. 5 (PDF pp. 5--6): `HEAT`, `POWR`, `DCNT`, continuing/acknowledged alarms. | Does not define R1's compatible-history verifier. |
| A three-valued verdict for incomplete/abstract recorded traces is established. | [K] | Wang et al., RV 2011, LNCS 7186, 2012, pp. 442--456, DOI https://doi.org/10.1007/978-3-642-29860-8_35 ; author-accessible version: https://repository.upenn.edu/entities/publication/4614b8f7-efd0-4253-bc4e-1657f702ad6e | Sec. 1, p. 442; Sec. 2, pp. 443--445; Sec. 3, pp. 446--449; conclusion p. 455. | Different recorder and domain; kills a generic semantics contribution, not a physical experiment. |
| Known gaps/imprecise values can be propagated to sound outputs, with recovery after reset. | [K] | Leucker et al., RV 2019, LNCS 11757, 2019, pp. 273--291, DOI https://doi.org/10.1007/978-3-030-32079-9_16 ; arXiv:1907.07761v1, 10 Jul. 2019: https://arxiv.org/abs/1907.07761 | arXiv abstract; published Sec. 1, pp. 273--275; Sec. 3, pp. 278--284 (publisher HTML inspection of introduction/gap model). | It assumes exact knowledge of when information becomes unreliable/reliable; R1 must validate those facts rather than assume them. |
| MQTT QoS 1 is at-least-once and duplicates can occur; retain replaces the current topic message. | [K] | OASIS, *MQTT Version 5.0*, 7 Mar. 2019, official standard https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.pdf | Sec. 1, p. 11; Sec. 3.3.1.3, p. 54; Sec. 4.3.2, pp. 94--95. | Transport semantics do not establish local acquisition/persistence provenance. |
| Reefer-specific missing-value work is an immediate direct-neighbor family. | [K] bibliographic; [GAP] method/endpoint | Bagchi et al., IEEE Sensors Journal 24(22), 2024, pp. 38286--38297, DOI https://doi.org/10.1109/JSEN.2024.3466966 ; Bagchi et al., COMSNETS 2025, pp. 805--807, DOI https://doi.org/10.1109/COMSNETS63942.2025.10885730 | Official IEEE/Crossref metadata; full PDFs inaccessible on 2026-08-28. | Do not state that either paper fails to address a three-state decision until full text is inspected. |
| The three-state output cannot disambiguate equal observation histories with different true exposures. | [KILL] logical boundary | R1's declared observation model; consistent with Wang et al.'s all-consistent-traces semantics above. | Counterexample described in Assumption audit item 1. | This is a conditional indistinguishability argument, not a claim about field fault rates. |

## Queries and failed searches

- `"A Novel Data Transformation for Improving Predictive Accuracy of Online Missing Value Imputation During Reefer Container Monitoring" pdf`
- `"Missing Value Imputation for IoT Data: With Applications to Reefer Container Monitoring" pdf`
- `"known-safe" "known-violation" indeterminate temperature monitoring IoT`
- `"three-valued" runtime monitoring incomplete traces sensor data`
- `site:who.int cold chain temperature monitoring data logger missing data power outage`
- `"data completeness" cold chain temperature monitoring missing records`

Failed/limited retrievals:

- IEEE full text for Bagchi et al. 2024 (document 10700599) and 2025 (document 10885730) was not accessible.  Their official metadata/DOIs and a forward-citation lookup confirm the bibliographic chain only; exact claim overlap remains [GAP].
- I found no verified 2024--2026 primary paper with R1's exact equal-budget `known-safe / known-violation / indeterminate` physical endpoint.  This is not evidence of absence.
- No primary source was found showing a special provenance datum unavailable to a conventional crash-atomic durable ledger; the contrary is the operative baseline argument, not a literature-absence claim.

## Decision

**PIVOT.**  Do not promote R1 as an innovative sensing/provenance protocol or a safe-release system.  It fails the component and theoretical-claim portions of the audit, and a durable journal plus the same verifier is a direct mechanism-eliminating baseline.  Retain only the narrowly framed, preregistered physical **boundary/replication** study if the coordinator needs a fallback: quantify when a documented low-cost trace supports a conditional verdict and when it cannot, with B-journal as the primary comparator and an independently surviving reference trace.  The Bagchi full-text check remains required before even this pivot is described as distinct from reefer missing-data work.
