# Connector Visual-Function Story: Red-Team Decision

## Decision investigated

Whether a Pi Camera NoIR v2 could support a primary FYP direction in which a
technician uses visible corrosion/appearance of a benign low-voltage connector
to choose `retain / rework / electrical retest`.

## Proposed story

A maintainer sees discoloration or surface deposits on a replaceable,
non-production connector exposed to a humid environment. Retaining a bad
connector may cause an intermittent bench record or later rework; rejecting a
good connector wastes labor and material.

## What the camera could observe

- External color, deposit area, scratches, seating geometry, and visible
  corrosion on a declared connector family.
- The deployable policy would not see contact resistance, internal mating
  condition, force, or the physical fault label.

## Independent truth and strongest baseline

- [K] Connector reliability work treats electrical contact resistance (ECR),
  impedance, and contact-state measurements as the functional endpoint, rather
  than surface appearance alone. Song, Hilmert, and Kiel's 2025 state-analysis
  review specifically combines ECR mapping with material analysis to distinguish
  failure mechanisms. Source inspected: article abstract/search record,
  https://doi.org/10.1016/j.engfailanal.2025.109427.
- [K] Swingler and McBride report that sample-material laboratory results did
  not correlate with commercially tested multi-contact connectors; a terminal
  can also recover from a high resistance at one interface, while terminal
  failure depends on all contact interfaces. Source inspected: abstract and
  bibliographic record, pp. 670-676,
  https://doi.org/10.1109/TCAPT.2002.808007.
- [K] A current direct engineering direction measures cable-port reflection or
  resistance/impedance to assess connector degradation in situ, rather than
  relying on appearance. Source inspected: abstract/search record,
  https://doi.org/10.1016/j.measurement.2026.121345.

The natural simple baseline is therefore a low-voltage four-wire contact-
resistance/continuity test. It observes the proposed functional target more
directly than the camera, and it is cheap enough for a bench fixture.

## Identification audit

[KILL] A visual-only policy cannot establish functional connector health when
hidden contact force, internal mating state, and multi-contact topology vary.
That is not a new edge-computing boundary: it is the ordinary distinction
between surface inspection and electrical condition measurement.

[GAP] A narrowly defined remote-access workflow might make an image useful as
a *screening* signal before a physical test. No such user-owned workflow,
access constraint, fault prevalence, or maintenance budget is currently
documented. Without it, comparing a camera to the direct electrical test is an
instrumentation exercise, not a CS contribution.

## Kill conditions met

1. The direct functional baseline is stronger, cheaper, and more interpretable
   than the proposed image signal.
2. The candidate's apparent novelty is a visual proxy for an established
   electrical-condition problem.
3. A physical camera fixture would add a new dataset but not a distinct
   observation/action/endpoint claim.

## Decision

**KILL as a primary FYP direction.** Retain only as a teaching demo or a
negative control illustrating why visual evidence should not be mistaken for
functional truth. It should not displace `PRF-TR`, whose independent oracle
matches the actual record-reading decision rather than introducing a stronger,
cheaper alternative sensor.
