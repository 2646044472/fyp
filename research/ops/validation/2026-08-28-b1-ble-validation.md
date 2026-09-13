# Validation Audit: 2026-08-28 B1 BLE proximity record / abstain

## Decision investigated

Whether **B1** -- an asset operator records or abstains on low-cost BLE proximity using a finite physical-panel RSS boundary -- is a defensible edge FYP contribution rather than a reimplementation of RSSI smoothing, proximity classification, or a BLE deployment.  The audited scope is the active charter: one-year FYP, a benign demo by 2026-12, low-cost self-purchased components, no production deployment, no safety actuation, and no personal data unless separately approved.

## Claim under test

The claimed contribution is a pre-registered, RSS-only rule that emits `record` or `abstain` for a local asset-proximity event, then shows on a held-out physical panel that it reduces wrong retained records at a matched manual-review budget relative to an RSS rolling median plus a fixed abstention band.

The claim is *not* a new BLE ranging model, RSS smoothing filter, edge deployment, or generic confidence/reliability score.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | `[KILL]` Filus et al. combine BLE RSSI, local sensing, reliability metrics, and filtering of unreliable proximity results, with most processing on the phone.  He et al. combine RSSI-window distributions and IMU to handle multipath/carriage bias, including a Pi Zero and ESP32 deployment.  Cortesi et al. combine low-power BLE asset tags, local RSSI estimation at the wearable edge, asset-user matching, and a `SURE / UNSURE` trust decision. | B1 deliberately excludes IMU, a learned model, multiple users, and cloud matching.  Excluding those components does not constitute a mechanism. | High. |
| Exact-claim collision | `[KILL]` Cortesi et al., *IEEE Internet of Things Journal* 12(3), 2025, is a direct task neighbor: determine which operator used an active industrial asset with BLE RSSI; the wearable pre-processes RSSI at the edge; an assignment gets `SURE` or `UNSURE`; experiments use physical indoor/outdoor conditions and independent truth.  Its trust rule is an abstention-equivalent action in the same asset-record story. | B1's wording is narrower: one local RSS-only record/abstain rule and a source-frozen, held-out physical panel instead of EKF plus multi-user assignment.  This is only an evaluation restriction.  It is not an established technical distinction, and the audit found no evidence that it changes the observation model or endpoint enough to sustain a thesis. | High for task collision; medium for the conclusion that a reviewer will treat the panel as insufficient. |
| Boundary / impossibility | `[KILL]` RSS-only proximity is not identified across unrestricted physical conditions.  Cortesi et al. report that an RSS observation at 6 m can also occur below 0.5 m, making their empirical RSS-distance map non-bijective.  A rule seeing only the same RSS window must take the same action in both worlds, although their correct records differ. | A finite, declared condition panel can estimate conditional error for precisely those cells.  It cannot justify a guarantee, an unmeasured-device claim, or an arbitrary-room transfer claim. | High. |

## Assumption and identification audit

1. **The real decision story is already published.** `[KILL]` Cortesi et al. use BLE-enabled low-power devices to attribute active tools to operators.  Their reported decision variables include an operator-asset assignment and a `SURE / UNSURE` trust level; `UNSURE` explicitly marks elevated risk of an incorrect assignment.  B1's `record / abstain` differs chiefly in vocabulary.

2. **RSS-only cannot tell physical cause from record truth.** `[KILL]` Let an observation be a finite RSS window \(O\).  The Cortesi measurements exhibit a near/far overlap: a 6 m reading can also occur at less than 0.5 m.  Hence there can be a near target world and a far/attenuated world with the same available \(O\), but opposite correct record labels.  Any RSS-only policy \(a(O)\) must choose the same action for both.  Median filtering changes variance, not this observational ambiguity.

3. **The finite panel solves only measurement, not transfer.** `[K]` A panel containing fixed tag models, positions, orientations, obstructions, and rooms gives an honest empirical boundary *only inside that declared panel*.  `[GAP]` B1 presently supplies neither an independent truth process nor a blocked selection rule.  If the same panel chooses its threshold and measures its retained-error rate, the claimed transfer result is invalid.

4. **The original asset-operator story creates an ethics/data contradiction.** `[KILL]` Cortesi's realistic validation used workers/wearables, OptiTrack ground truth, and video.  The current charter excludes personal data.  A tabletop replacement with anonymous tags is feasible, but it no longer validates the claimed operator-attribution story; it becomes a generic tagged-object proximity benchmark.

5. **The proposed edge argument is not distinct.** `[K]` Cortesi's wearable performs local RSSI processing to reduce transmission, specifically contrasting raw-data transmission with local distance calculation.  Moving B1's rule to an ESP32/Raspberry Pi or retaining data locally therefore does not create an edge-specific endpoint.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Cortesi et al., *A Proximity-Based Approach for Dynamically Matching Industrial Assets and Their Operators Using Low-Power IoT Devices*, IEEE Internet of Things Journal 12(3), pp. 3350--3362, 2025; accepted manuscript / arXiv:2412.13600v1, 2024-12-18. [Official accepted manuscript](https://www.research-collection.ethz.ch/server/api/core/bitstreams/b6200c08-4192-45cf-b404-7a5b99beab5d/content), [DOI](https://doi.org/10.1109/JIOT.2024.3479458) | BLE tag RSSI, asset activity, local wearable EKF, server assignment; `SURE / UNSURE` trust decision. | Asset-user record; indoor/outdoor physical prototype; OptiTrack and video truth; confidence/precision/recall plus energy. | Same user story, low-cost BLE observation, local processing, imperfect proximity, record confidence, and physical evaluation. | `[KILL]` B1's story and triage mechanism.  A new rule or board cannot repair it.  Leaves only a deliberately modest replication/negative measurement, not a direction. |
| Filus et al., *Cost-effective filtering of unreliable proximity detection results based on BLE RSSI and IMU readings using smartphones*, Scientific Reports 12, 2440, 2022-02-14. [Official article](https://doi.org/10.1038/s41598-022-06201-y) | RSSI metric, IMU activity metric, joint metric; filter unreliable proximity output locally. | Static anchors / moving device; evaluates unreliable-result filtering. | Same reliability-filter / abstention family, though B1 is RSS-only and single local record. | `[KILL]` generic claim that local BLE reliability filtering or filtering based on RSS changes is new.  It reports that RSS-only filtering itself can work, so adding no IMU is not a new principle. |
| He et al., *Tackling Multipath and Biased Training Data for IMU-Assisted BLE Proximity Detection*, INFOCOM 2022, pp. 1259--1268; arXiv:2201.03817v1, 2022-01-11. [Author manuscript](https://arxiv.org/pdf/2201.03817) | RSSI-window histogram, IMU/carriage features, proximity classifier; Pi Zero and ESP32 implementation. | Crowded/semi-dynamic/static sites, held-out test period, false-detection and resource outcomes. | Same multipath/carriage transfer failure and low-resource BLE sensing family; different learned inputs/action. | `[KILL]` a claim that physical multipath transfer or small-board BLE reliability is unstudied.  Leaves no RSS-only mechanism. |
| Kariminejad et al., *Impact of Model Uncertainty and Sensor Deployment Geometry on the Precision of BLE RSSI-Based Indoor Positioning*, IEEE Sensors Journal 26(2), pp. 2181--2193, 2025. [Official repository / final-publication DOI](https://repository.tudelft.nl/record/uuid:a820d378-5932-4b92-bd20-e56c307c8d6a) | RSSI model uncertainty and sensor geometry; CVT deployment. | Positioning precision across two deployments. | It is a less direct task neighbor, but it shows uncertainty and physical layout are already central variables in recent BLE RSSI evaluation. | `[KILL]` generic physical-panel / layout-uncertainty claim.  B1 cannot turn condition enumeration into innovation. |

## Strongest simple baseline

**RSS rolling median plus a fixed abstention band** is the first required baseline.  It must be tuned only on source cells and evaluated untouched on all targets.  The more damaging baseline is the direct neighbor's inexpensive **local 1-state EKF plus `UNSURE` distance-separation threshold**: Cortesi et al. define `UNSURE` whenever the matched and second-nearest estimated distances differ by less than 0.75 m (Sec. IV-B, p. 6), then report the false-sure / true-unsure outcomes.  If B1 cannot beat either at equal retained-record and abstention budget, there is no residual mechanism.

Even if B1 were to beat a median rule on one panel, the result would only show that its chosen thresholds describe that panel.  It would not show a transferable contribution unless rules, source cells, thresholds, target cells, and review budget were all frozen before target capture.

## Contrarian result

**B1 is killed as a standalone FYP direction.**  The decisive 2025 direct neighbor already implements the operational asset-operator matching story with low-power BLE/RSSI, edge-local processing, an explicit confidence-to-uncertainty decision, physical experiments, energy accounting, and independent truth.  B1's remaining finite-panel wording narrows scope but does not introduce a new observation, action, guarantee, or evaluation endpoint.

The honest pivot is an appendix-level **negative measurement**: under a small declared tabletop panel, quantify where RSS-only median/EKF confidence cannot distinguish near from far/obstructed conditions, using a non-personal tracked jig as truth.  That may inform a later candidate's measurement protocol; it is not a replacement thesis and must not claim general BLE impossibility.

## Feasibility audit

| Requirement | Finding | Consequence |
| --- | --- | --- |
| Hardware and demo | `[K]` Two ESP32/nRF52-class BLE tags and a local receiver are inexpensive; a tabletop jig and no-person test can be assembled before 2026-12. | Feasibility makes a replication/measurement demo possible, not a research contribution. |
| Ground truth | `[GAP]` A credible asset-operator version needs participant/action truth; the direct neighbor used OptiTrack plus video. | Under the no-personal-data constraint, use anonymous tagged objects and a measured jig only, then state that the result does not validate human operator attribution. |
| Data and computation | `[K]` An RSS median, EKF, and finite threshold grid require negligible compute/data. | This increases feasibility but makes a novel algorithm claim even less plausible. |
| Ethical scope | `[KILL]` The stated operator-attribution story requires identity/behaviour collection if implemented literally; video truth adds another data-governance requirement. | Do not collect people or present a tabletop tag task as evidence about workers without approval. |
| Useful negative path | `[E]` The published direct neighbor itself observes uncertainty indoors and reports overlapping RSS-distance observations. | A bounded negative result is possible, but it belongs as evidence for a different sensing candidate, not a promoted B1 thesis. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Low-power BLE/RSSI asset-operator matching with local wearable preprocessing is already studied. | `[KILL]` | Cortesi et al., IEEE IoT Journal 12(3), pp. 3350--3362, 2025; accepted manuscript dated 2024; DOI: https://doi.org/10.1109/JIOT.2024.3479458 | Abstract p. 1; Sec. I, pp. 1--2; Sec. III, p. 4; Sec. V, p. 7; Sec. VII, pp. 10--11. | The system forwards aggregated values to a server, so it does not prove an all-local implementation.  It does prove B1's story, BLE sensing, local preprocessing, and real physical evaluation are not a new combination. |
| `SURE / UNSURE` operates as a trust/abstention decision, based on closeness to the next-best match. | `[KILL]` | Cortesi et al. accepted manuscript / arXiv:2412.13600v1, 2024-12-18. | Sec. IV-B, p. 6, Eqs. (9)--(13); Sec. VI-C, pp. 9--10. | It is multi-user matching rather than B1's one-event record action.  It is nevertheless a stronger direct decision baseline. |
| B1's RSS-only observation is physically non-identifying under unbounded rooms/obstructions. | `[KILL]` | Cortesi et al. accepted manuscript / arXiv:2412.13600v1. | Sec. VI-A, p. 8: 6 m readings also occur below 0.5 m; the map is "no longer bijective." | An empirical counterexample, not a universal mathematical lower bound.  It is sufficient to prohibit B1's broad transfer claim. |
| RSS/IMU reliability filtering of BLE proximity is already established and RSS-only filtering is included. | `[KILL]` | Filus et al., published version, 2022-02-14, https://doi.org/10.1038/s41598-022-06201-y | Abstract; “Data processing,” Results, and Conclusion sections (online article, no stable printed page numbers). | Older than the requested recent window, but a direct foundational component collision. |
| Multipath, carriage bias, RSSI-window features, false detections, and low-resource BLE deployment were evaluated in a direct BLE proximity paper. | `[KILL]` | He et al., INFOCOM 2022; arXiv:2201.03817v1, 2022-01-11, https://arxiv.org/pdf/2201.03817 | Sec. I, pp. 1--2; Sec. III-A, pp. 3--4; Sec. VI, pp. 8--10; conclusion p. 11. | IMU/DNN and human carriers differ from B1, but rule out the broad hardware/physical-transfer framing. |
| Recent BLE RSSI work explicitly studies measurement-model uncertainty and deployment geometry. | `[K]` | Kariminejad et al., IEEE Sensors Journal 26(2), 2025, DOI https://doi.org/10.1109/JSEN.2025.3637898 | Official repository record, abstract, lines 74--78; full PDF availability noted but full text not inspected in this audit. | Exact methods/results beyond the abstract are `[GAP]`; use only as a recent adjacent lead, not load-bearing proof. |

## Queries and failed searches

Queries executed 2026-08-28:

- `2024 2025 BLE RSSI proximity detection uncertainty abstain reliability paper`
- `"BLE RSSI" "abstention" proximity`
- `"Bluetooth Low Energy" RSSI "reject option" proximity`
- `"BLE" RSSI "uncertainty" "proximity detection" paper 2024 2025`
- `2025 2026 BLE RSSI asset operator matching uncertainty abstain paper`
- `2024 2025 BLE RSSI proximity selective classification reject paper`
- citation-chain queries for DOI `10.1038/s41598-022-06201-y` and DOI `10.1109/INFOCOM48880.2022.9796716`.

Failed/limited searches:

- No 2024--2026 source was found that supplies B1 with a distinct RSS-only `record / abstain` mechanism plus a source/target physical-panel transfer protocol.  This is **not** evidence that no such source exists.
- The publisher record for Cortesi et al. was not directly retrievable, so exact evidence was read from ETH Zurich's official accepted manuscript and arXiv; the bibliographic VOR metadata were cross-checked through the ETH record/DOI.
- The full text of Kariminejad et al. was not inspected; its abstract is not used to establish B1's kill decision.

## Decision

**KILL.**  Do not promote B1, and do not rescue it by changing boards, removing IMU, switching from a phone to an ESP32, adding a finite physical panel, or calling local retention an edge contribution.  The nearest 2025 original paper already contains the asset-operator decision, RSSI processing, confidence/uncertainty output, physical validation, and energy story.  Preserve only the non-personal RSS ambiguity experiment as a possible negative-evidence appendix for a different candidate.

KILL
