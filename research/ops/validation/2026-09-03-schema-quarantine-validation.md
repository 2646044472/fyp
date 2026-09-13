# Decision investigated: whether SCHEMA-QUARANTINE is a defensible Pi-edge FYP claim that local schema ID, units, calibration epoch, provenance, range constraints, and a small fixture check can decide `accept / convert / quarantine` for sensor records while the schema registry is unavailable.

# Validation Audit: 2026-09-03 SCHEMA-QUARANTINE

## Claim under test

The divergence packet proposes a mobile repair node that protects an offline maintenance trace from firmware, units, calibration, aggregation-operator, or field-meaning changes. It claims that a local semantic guard can reduce semantic mis-merges at fixed CPU, bytes, and delay beyond syntax-only schema resolution, metadata-only checks, range checks, and declared unit conversion.

The decisive distinction is whether local observations establish semantic compatibility, rather than merely parseability, provenance, or numerical plausibility. RMS-versus-peak and calibration-meaning changes are the required adversarial cases.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component | Avro schema resolution/fingerprints, SSN/SOSA observation/procedure/property descriptions, SensorThings observed-property/unit fields, PROV provenance, and calibration terminology are established. | A Pi cache combining these fields is deployment/integration unless it gains an independent semantic witness. | High |
| Exact claim | `accept / convert / quarantine` is ordinary compatibility validation: resolve known schemas, convert only declared units, and quarantine unknown/incompatible contracts. | No new semantic observation, formally restricted transformation class, or application loss different from standard data-quality gating is defined. | High |
| Boundary | A hidden RMS/peak or calibration change can preserve schema ID, unit, range, timestamp, provenance trace, and every finite permitted record. | A signed semantic-version contract or an independent waveform/reference witness can restrict the ambiguity, but then the result is conditional on that added source/fixture contract. | High |

## Assumption and identification audit

Let the Pi observe `O`: cached schema/fingerprint, schema ID, units, calibration epoch, provenance fields, firmware label, timestamps, ranges, and a finite record trace. Consider two producers with identical `O`.

1. World A reports RMS current in amperes using calibration `f_A`.
2. World B reports peak current, or a changed calibration `f_B`, but retains the same schema ID, unit string `A`, epoch label, provenance values, ranges, and the finite observed values.

For any finite trace, World B can choose inputs or a changed implementation that agrees with World A on that trace and differs later. The local decision must therefore be the same. If it accepts the merge, it is wrong in one world. A range check cannot distinguish `1 A RMS` from `1 A peak`; the unit has not changed. A schema fingerprint proves the bytes match a known schema, not the measurement procedure or aggregation operator. Provenance proves only the stated lineage if its producer/signing chain is trusted; it does not prove a buggy or malicious producer's semantic claim.

[KILL] Hidden semantic compatibility is not identifiable from syntax, metadata, units, ranges, and a finite passive trace alone. The proposed local check may detect declared drift, but cannot certify undeclared meaning preservation.

The fixture check narrows rather than removes this boundary:

- A one-point calibration fixture cannot identify an affine calibration change `y = a x + b`; at least two independent, time-paired reference levels are required for that restricted model.
- A DC or single sinusoid fixture is not a general RMS/peak witness. To test the stated operator, use a trusted raw-waveform reference or at least two signals with different crest factors and precomputed RMS/peak truth. This only validates the declared fixture family.
- For an unrestricted firmware semantic change, no finite fixture set proves equivalence on future inputs. A signed immutable semantic contract/procedure version, enforced by change control, is the minimum general witness; a signature from the changed firmware itself is insufficient under a firmware-bug/compromise threat.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Apache Avro 1.11.3 | Writer/reader schemas, names, defaults, aliases, fingerprints, schema resolution. | Parse/resolve compatible serialized records. | Syntax-only schema compatibility and cached-registry baseline. | [KILL] New schema-resolution mechanism. It does not certify physical meaning. |
| W3C SSN/SOSA 2017 | Observation, ObservableProperty, Procedure, Sensor, Result, FeatureOfInterest. | Semantic description of sensing observations. | Record-level sensor meaning/procedure vocabulary. | [KILL] Carrying semantic fields as a new data model. Leaves enforcement/witness question. |
| OGC SensorThings API Part 1: Sensing 1.1 | Datastream, ObservedProperty, Sensor, unitOfMeasurement, Observation. | Interoperable IoT sensing API. | Unit/property/procedure metadata carried with observations. | [KILL] Metadata packaging and local cached validation. |
| W3C PROV-DM 2013 | Entity, Activity, Agent and derivation provenance. | Provenance interchange model. | Firmware/calibration/source lineage fields. | [KILL] A provenance-chain contribution; provenance is not numerical comparability. |
| JCGM 200:2012 VIM | Measurement procedure, calibration, metrological traceability. | Calibration vocabulary and conditions. | Calibration-epoch and meaning-change framing. | [KILL] Treating calibration labels as a novel semantic model. Leaves only a specific independently witnessed calibration test. |

## Strongest simple baseline

Use a layered deterministic control, not a weak syntax-only comparator:

1. **Cached syntax baseline.** Resolve Avro writer-to-reader schema only when a cached allow-listed fingerprint/version is valid; otherwise quarantine.
2. **Signed metadata baseline.** Require a cached signed semantic envelope containing source identity, observed-property URI, quantity kind, unit, aggregation operator and time window, procedure/firmware version, calibration epoch and calibration-function digest, and provenance/change-control digest. Accept only an exact approved contract match.
3. **Conversion baseline.** Convert only predeclared reversible mappings whose quantity kind, property, aggregation operator, procedure, and calibration validity are unchanged. Celsius/Fahrenheit may qualify; RMS/peak does not without a declared waveform model.
4. **Range/rate baseline.** Reject physically impossible values or rate changes, but never use plausibility to infer hidden semantic equality.
5. **Otherwise quarantine.** Registry absence, unknown contract, expired calibration, missing signature, or any semantic-field mismatch yields `quarantine`.

This is stronger than all controls named in the packet separately because it uses every permitted local metadata field and applies the correct conservative action. A proposed guard must show fewer independently labelled mis-merges or unnecessary quarantines than this baseline under the same cache, signature trust root, byte/CPU budget, and held-out transition cells. If it accepts only declared contracts, it is this baseline. If it accepts hidden changes, the two-world counterexample defeats its correctness claim.

## Contrarian result

[KILL] SCHEMA-QUARANTINE has no remaining positive method claim as framed. Standards already describe schema resolution, sensing semantics, units, procedures, provenance, and calibration vocabulary. A local guard can either trust and compare an explicit semantic contract, in which case the layered baseline is sufficient, or infer semantic preservation from metadata/trace, which is impossible for hidden RMS/peak or calibration-meaning changes.

The honest residual is a bounded negative result: demonstrate that a cached schema, unit string, range, and provenance trace do not witness aggregation/procedure meaning, and quantify which independently signed contract fields or fixture references are necessary in one declared sensor/transition family. That is a protocol/benchmark appendix, not a Pi-local semantic-inference thesis.

## Feasibility audit

| Area | Finding |
| --- | --- |
| Hardware | [K] Pi 5 can parse Avro/JSON/CBOR, cache contracts, verify signatures, and run deterministic checks. Hardware does not add a semantic observation. |
| RMS/peak staging | [GAP] Low-cost temperature/light records cannot honestly create RMS/peak semantics. A credible physical version needs a signal source, a trusted waveform/reference instrument, and firmware/source logs. Synthetic records test a protocol parser only. |
| Calibration staging | [GAP] For affine calibration, stage at least two independently referenced levels, with source and witness clocks/logs separated. A single fixture point cannot distinguish gain from offset. Nonlinear/condition-dependent calibration needs a declared model and more references. |
| Labels | [GAP] Ground truth is the actual producer procedure, firmware build, calibration function, and independently measured input, not the record's own metadata. Do not label semantic compatibility from the same registry payload being evaluated. |
| Offline registry | [GAP] Cache age, trust root, revocation/update behavior, schema/contract fingerprinting, and what happens after an unknown transition must be frozen. An unavailable registry supplies no proof that a stale cached contract remains current. |
| Evaluation | [GAP] Split by firmware/procedure/calibration-transition cell, not random records. Hold out an aggregation/operator change and a calibration change from guard design. Compare false accept, false quarantine, conversion error, latency, bytes, and recovery after reconnection. |
| Story | [KILL] No named repair decision beyond generic trend merging is supplied. Without one, accept/convert/quarantine is ordinary data-quality classification. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Avro separates schema resolution from application semantics. | [K] | Apache Avro 1.11.3 Specification, released 2023, https://avro.apache.org/docs/1.11.3/specification/ | "Schema Resolution," "Single-object encoding," "Names," and "Sort Order" sections. | Direct syntax/fingerprint baseline. The specification does not claim physical sensor-meaning validation. |
| SSN/SOSA already models Observation, ObservableProperty, Procedure, Sensor, Result, and platform concepts. | [K] | W3C, Semantic Sensor Network Ontology, Recommendation, 19 October 2017, https://www.w3.org/TR/vocab-ssn/ | Secs. 3-4; SOSA Observation, ObservableProperty, Procedure, Sensor, Result, Platform. | Kills a new ontology/metadata-field claim, not a distinct independently witnessed decision endpoint. |
| SensorThings exposes sensing datastreams, observed properties, sensors, observations, and units. | [K] | OGC, SensorThings API Part 1: Sensing, Version 1.1, OGC 18-088r1, 2021, https://docs.ogc.org/is/18-088r1/18-088r1.html | Sec. 8 entity model; Datastream, ObservedProperty, Sensor, Observation and unitOfMeasurement definitions. | Direct IoT metadata/API family; it does not enforce a producer's truthfulness. |
| Provenance represents lineage but cannot alone establish comparability of a measurement procedure. | [K] | W3C, PROV-DM: The PROV Data Model, Recommendation, 30 April 2013, https://www.w3.org/TR/prov-dm/ | Secs. 3-5, especially entity/activity/agent and derivation relations. | The latter clause is an inference from provenance scope, not a claim quoted from PROV. |
| Calibration is a measurement operation with stated conditions/results, not a magic epoch label. | [K] | JCGM 200:2012, International Vocabulary of Metrology (VIM), 3rd ed., https://www.bipm.org/documents/20126/2071204/JCGM_200_2012.pdf | Sec. 2.39 "calibration" and associated notes; pp. 28-29 in the official PDF. | Supports the need for a calibration model/conditions; it does not prescribe the proposed protocol. |
| Same historical workspace boundary: authenticated transition metadata cannot prove numerical comparability without overlap/reference model. | [K] | Active candidate register, DCC-SPLIT row, read 2026-09-03: C:/Users/bankey/Desktop/code/fyp/research/active/01-candidate-register.md | DCC-SPLIT row. | Internal prior decision, not independent primary evidence; used to avoid relabeling the same boundary. |

## Queries and failed searches

Queries inspected:

- `"sensor data semantic schema evolution calibration unit conversion semantic interoperability"`
- `"RMS peak semantic change schema registry sensor firmware offline"`
- `"offline schema registry IoT sensor semantic validation provenance calibration"`
- `"site:avro.apache.org schema resolution single object encoding fingerprint"`
- `"site:w3.org/TR vocab-ssn observation procedure observable property result"`
- `"site:docs.ogc.org SensorThings unitOfMeasurement ObservedProperty Sensor"`
- `"JCGM 200 VIM calibration measurement procedure pdf"`

Failed or unresolved:

- [GAP] No audited primary paper was found for the packet's exact Pi-local `accept / convert / quarantine` endpoint. This is a search-boundary statement, not novelty evidence.
- [GAP] I did not establish a current full-text citation chain for a deployed offline schema-registry cache that detects undeclared RMS/peak or calibration changes. Standards already show why a cached schema/metadata design is a component collision, while the two-world counterexample decides the hidden-change claim.
- [GAP] No concrete sensor, calibration function class, waveform fixture, trust-root/update model, or downstream work-order action is committed by the packet.

## Decision

KILL SCHEMA-QUARANTINE as a positive FYP method. Use the existing syntax plus signed-semantic-contract plus conservative-quarantine baseline for any engineering implementation. Retain only a narrow negative benchmark if useful: show, on a preregistered source/fixture family, that cached syntax/units/ranges/provenance cannot certify hidden operator or calibration meaning, and report the minimum additional witness needed for the declared transformation class.

KILL
