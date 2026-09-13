---
topic: edge-camera-physical-performance-candidates
created: 2026-09-04
last_verified: 2026-09-04
status: active
depth: deep
related:
  - physical-failure-synthetic-transfer-boundary
  - macau-asset-record-workflow
sources:
  - url: https://doi.org/10.1016/j.apenergy.2026.127637
    fetched: 2026-09-04
  - url: https://doi.org/10.3390/su18084123
    fetched: 2026-09-04
  - url: https://doi.org/10.1016/j.applthermaleng.2026.131237
    fetched: 2026-09-04
  - url: https://doi.org/10.1016/j.ijrefrig.2024.02.011
    fetched: 2026-09-04
  - url: https://doi.org/10.1016/j.procs.2024.02.054
    fetched: 2026-09-04
  - url: https://doi.org/10.1017/wat.2026.10018
    fetched: 2026-09-04
  - url: https://doi.org/10.1016/j.device.2025.100927
    fetched: 2026-09-04
  - url: https://pmc.ncbi.nlm.nih.gov/articles/PMC6219047/
    fetched: 2026-09-04
  - url: https://doi.org/10.1007/s11694-026-04125-z
    fetched: 2026-09-04
  - url: https://doi.org/10.1007/s10844-020-00618-5
    fetched: 2026-09-04
  - url: https://doi.org/10.1016/j.mlwa.2021.100070
    fetched: 2026-09-04
  - url: https://doi.org/10.1038/s44172-026-00685-6
    fetched: 2026-09-04
---

# Edge-camera physical-performance candidate audit

## Summary

The search compared seven real workflows where an edge camera could observe an apparent condition but an independent physical outcome determines whether maintenance is worthwhile. Generic positive versions are already occupied: PV soiling/cleaning, frost/defrost control, filter clogging/replacement, 3D-print failure stopping, pipette monitoring, wet-floor risk, and water-turbidity estimation.

The strongest remaining research identity is still `PRF-TR`: a finite test of whether digital image faults preserve the risk-cost ordering of fixed actions under named physical optical conditions. This is a bounded evaluation or negative-result study, not a new detector or a new abstention mechanism.

## Findings

PV soiling is not an open camera-to-action story. Recent work directly predicts soiling-induced power loss from panel images, combines visual classification with inverter-level energy validation and a cleaning energy-balance decision, and separately optimizes low-cost sensing configurations for cleaning decisions. A Raspberry Pi camera experiment that detects dirty panels or recommends cleaning would therefore be a direct continuation.

Frost/defrost is similarly occupied. Recent refrigeration work uses image-based frost detection and thickness estimation, while newer work combines frosting recognition with system performance or fan-current effects. An edge camera that classifies frost or triggers defrost is not a distinct direction without a new endpoint or independently justified physical boundary.

Filter maintenance has both physical and commercial precedents. Pressure-drop and fan-energy consequences of filter loading are measured in HVAC studies; machine-learning control systems trigger cleaning or replacement from pressure-drop deviation; and commercial edge-vision providers already market clean/dirty/replace camera workflows. A Pi camera filter-replacement classifier is not a research gap.

3D printing has an especially high collision risk. On-device failure detectors already pause or alert on FDM faults, and recent academic work frames real-time visual monitoring and stop/mitigation decisions. A camera-on-Pi print-failure system would be an implementation project unless it changes the task, observation model or evaluation endpoint substantially.

Laboratory liquid handling also has established image-based malfunction monitoring, image-derived volume estimation, gravimetric verification and recent low-volume verification work. A camera that decides whether pipetting succeeded would need a very specific new physical question and laboratory access; the generic story is already occupied.

Wet-floor and slip-risk monitoring has direct camera classification, visual friction estimation and low-cost edge implementations. A Macau hotel-floor wetness detector or cleaning alarm would therefore be a safety application of known methods, not a clean thesis contribution.

Water-turbidity estimation is now also directly demonstrated on a Raspberry Pi-class edge node with an RGB camera and physical turbidimeter validation. A rainwater first-flush or post-storm turbidity classifier could still be a local application study, but the edge-camera-plus-independent-water-truth pattern is already occupied and the exact Macau workflow is unverified.

In contrast, the PRF-TR endpoint deliberately does not predict the physical condition or control the asset. It asks whether a **source-fitted digital test ranking** predicts which fixed capture action is best on a held-out physical cell. The action semantics, independent payload oracle and blocked-session analysis are the distinguishing objects. The closest generic action families remain existing abstention/acquisition work, so no claim is made for inventing `reacquire` or `review`.

## Insights

- The common failure in application-first topic search is that the physical outcome is either already measured directly by a standard sensor or already controlled by a published visual system. Adding Pi and edge inference does not change that.
- A stronger CS question appears when the camera is not asked to estimate the physical state: test whether a cheap digital proxy preserves the ranking of actions under a reality shift. This makes the evaluation endpoint, not the application label, carry the research identity.
- Macau is most useful as motivation for humid/rain-prone maintenance records and offline local operation. It should not be used as a novelty claim or as proof of a specific deployment.

## Strongest objection

PRF-TR may still collapse to an expensive characterization study if fixed two-shot or always-review is Pareto-optimal, or if digital and physical conditions preserve the same action order. That null would be scientifically useful only if the physical cells, payload oracle, costs and blocked sessions are independently auditable; otherwise it is merely a demo.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| PV soiling-to-cleaning camera system | Recent image-to-power-loss, inverter-validated cleaning and cost-optimal monitoring work directly cover the endpoint. | 2026-09-04 |
| Frost/defrost edge camera | Image frost measurement and performance-guided defrost recognition are directly occupied. | 2026-09-04 |
| HVAC filter clean/dirty/replace camera | Pressure-drop control, filter performance studies and commercial edge workflows cover the action. | 2026-09-04 |
| 3D-print failure camera | On-device failure detection and real-time stop/mitigation systems are established. | 2026-09-04 |
| Pipette success camera | Image-based pipette monitoring and independent gravimetric/photometric verification are established. | 2026-09-04 |
| Wet-floor/slip-risk camera | Camera wetness/friction estimation and edge implementations are established, with safety-claim concerns. | 2026-09-04 |
| Rainwater turbidity edge camera | Pi-class RGB plus physical turbidimeter validation already exists; local workflow remains unverified. | 2026-09-04 |

## Open questions

- Does the supervisor accept a finite evaluation or negative-result paper identity rather than require a new model?
- Can PRF-TR produce a rank inversion or a clearly quantified rank-preservation/null result on physical cells?
- Which non-personal marker and exact record workflow best communicates the story without implying maintenance completion or safety certification?

## Timeline

- 2026-09-04 - Compared seven alternative edge-camera physical-performance stories; retained PRF-TR as the strongest conditional direction and killed generic application versions.
