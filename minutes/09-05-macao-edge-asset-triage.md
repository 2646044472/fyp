# Macao Edge-Only Asset Triage

**Date:** 2026-09-05  
**Decision investigated:** Which Macao-grounded, edge-only story could supply
a real research asset rather than another generic edge demo?

## Bottom line

No Macao-specific direction is promoted. The strongest **asset lead** is a
non-personal food-waste measurement workflow in a campus canteen, hotel, or
restaurant. It is not smart-bin hardware, food recognition, demand prediction,
or a new scheduling algorithm. Those are occupied application families.

The possible research object is narrower:

> Can an edge station decide whether a meal-service waste record is valid to
> close, must remain unresolved, or needs reconciliation when container/tare,
> weighing, and local-delivery events disagree?

This is a proposal for an access/feasibility gate, not a paper claim. Its
novelty risk is now **Red** after a direct data-processing neighbor check.

## Candidate asset lead: FW-EPISODE

### Real story [C]

A canteen or hotel sustainability worker compares food waste between meal
services to decide whether a menu, production quantity, or staff practice
should change. One service can contain a bin replacement, wrong tare, missed
weighing, scale reset, or delayed local upload. The edge station must choose
close, unresolved, or reconcile for that service record.

A wrong close is not merely a bad sensor reading: it creates a false
comparison across services and can make a reduction intervention look useful
or useless when it is not. Unresolved and reconcile consume staff time but
preserve the validity of the decision record.

### Why the local story is plausible [K]

- Macao's environmental authority reports active food-waste collection and
  on-site processing programmes involving schools, hotels, restaurants,
  hospitals and other institutions; it also reports smart food-waste
  collection equipment in local programmes.
- A Macao case study examined residents and restaurants, so the problem is
  locally researched as a waste-management issue, not invented for a board.
- A 2026 field study of healthcare and hotel kitchens found that staff-entered
  food-waste tracking could underreport substantially; its result makes
  record validity a real empirical concern, not proof that a new edge method
  exists.

### Direct-neighbor warning [KILL risk]

Korhonen and Kaila (2015) already process 27,865 real household waste-container
weight measurements, identify missing and inconsistent low/high values as
errors, and turn collection-point data into reliable waste-generation
information. That directly defeats any claim whose contribution is simply
cleaning, detecting errors in, or making waste-scale data trustworthy.

The only hypothesised difference is a meal-service decision with a declared
three-way action (close / unresolved / reconcile), explicit container/tare
identity, and independently audited service truth. [GAP] The literature has
not yet been audited for that exact action/endpoint. This is too narrow and
too uncertain to select before a workflow owner confirms access.

### Evidence needed before promotion [GAP]

1. Permission for at least three independent service sessions, preferably
   several each week.
2. A workflow owner who already uses the resulting comparison to make a named
   operational decision.
3. Independent truth: calibrated control weighing at service close, a
   container/tare inventory and observer log, plus a collection or processing
   receipt where available. The edge policy cannot label its own correctness.
4. Non-personal protocol: no staff identity, customer data, or kitchen video.
5. A direct-neighbor audit of measurement-workflow integrity, not just
   food-waste sensing papers.

### Minimal edge setup [C]

A load-cell scale, unique labelled reusable containers, local persistent event
log, optional NFC/container scan, and a Pi or ESP32 gateway are sufficient.
No camera is required. The first comparison must include the current manual
procedure and fixed declared closure rules before any learned policy.

### Kill conditions [KILL]

- No real workflow owner or post-decision outcome exists.
- A calibrated close-of-service weight and fixed container log already settle
  every episode; then a new edge decision rule adds no information.
- The only available data are self-entered categories/weights without an
  independent service-level audit.
- Direct-neighbor work already establishes the same event-integrity action
  and endpoint.

## Leads rejected before access effort

| Story | Reason not to pursue now |
| --- | --- |
| Low-cost heritage temperature/humidity network | [KILL] Macao already operates a World Heritage Monitoring Centre, and recent work already builds low-cost Pi/ESP32 heritage monitoring systems. A Pi dashboard or sensor network would be a repeat. |
| Smart laundry cycle/availability monitor | [KILL] Recent work already demonstrates commodity embedded cycle-phase monitoring and reservation; no remaining action endpoint is identified. |
| 3D-printer fault/finish monitor | [KILL] Edge multimodal fault detection and online quality assurance are directly occupied. |
| Hotel-linen or reusable-item RFID scan | [KILL] RFID read-rate error detection, profile monitoring, metallic-environment read-rate improvement and read-rate-driven scheduling are established. A Pi reader deciding retain / retry / manual count changes the story but not the mechanism. |
| Construction-noise node | [HOLD] Macao has monitoring/reporting practice, but no authorised site, independent compliance endpoint, or non-generic task has been identified. |

## Sources inspected

- Macao Environmental Protection Bureau, Chinese food-waste reduction and
  collection overview, accessed 2026-09-05:
  https://www.dspa.gov.mo/richtext.aspx?a_id=1533635494
- Liang et al., *Uncovering residents and restaurants' attitude and willingness
  toward effective food waste management: A case study of Macau*, Waste
  Management 130 (2021), DOI: https://doi.org/10.1016/j.wasman.2021.05.021
- Korhonen and Kaila, *Waste container weighing data processing to create
  reliable information of household waste generation*, Waste Management 39
  (2015), pp. 15-25, DOI: https://doi.org/10.1016/j.wasman.2015.02.021.
  Abstract inspected through PubMed 25765610.
- *How accurate are food waste tracking systems? Insights from healthcare and
  hotel kitchens*, Resources, Conservation & Recycling 226 (2026), DOI:
  https://doi.org/10.1016/j.resconrec.2025.108689
- Macao Cultural Affairs Bureau, World Heritage Monitoring Centre announcement,
  2022-11-16: https://www.icm.gov.mo/gb/news/detail/20782
- Palomeque-Gonzalez, *A Modular, Low-Cost IoT System for Environmental and
  Behavioural Monitoring in Cultural Heritage Sites*, arXiv:2508.00849, 2025:
  https://arxiv.org/abs/2508.00849
- Venkadasamy, *Design and Evaluation of an IoT-Based Smart Laundry Management
  System with Real-Time Machine-State Monitoring*, 2026:
  https://nbn-resolving.org/urn:nbn:de:bsz:120-qucosa2-974043
- Krajewski et al., *Smart additive manufacturing: An IoT-driven framework for
  predictive failure detection and sustainable operation*, Additive
  Manufacturing Frontiers 5(2), 2026, DOI:
  https://doi.org/10.1016/j.amf.2025.200264
- Lin et al., *Improving RFID Read Rate Reliability by a Systematic Error
  Detection Approach*, RFID Eurasia 2007, DOI:
  https://doi.org/10.1109/RFIDEURASIA.2007.4368118
- Buettner, *Read rate profile monitoring for defect detection in RFID
  Systems*, RFID-TA 2011, DOI: https://doi.org/10.1109/RFID-TA.2011.6068621
- Buettner et al., *Improving UHF RFID read rates by juggling selected bits*,
  IEEE RFID 2016, DOI: https://doi.org/10.1109/RFID.2016.7488021
- Huang et al., *ReaDmE: Read-Rate Based Dynamic Execution Scheduling for
  Intermittent RF-Powered Devices*, IEEE RFID 2021, DOI:
  https://doi.org/10.1109/RFID52461.2021.9444321

HOLD (Red): do not buy hardware or call this a paper direction. Revisit only
after a real workflow owner confirms access and an exact-action neighbor audit
finds a defensible distinction from the 2015 record-processing work.
