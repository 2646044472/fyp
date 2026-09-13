# Edge-Camera Direction Constraint (2026-09-04)

## User constraint

- `edge + camera` is the fixed technical boundary.
- A Raspberry Pi and Camera NoIR v2 are confirmed available. They are existing
  experimental resources, not a prerequisite that limits topic discovery.
- Additional low-cost cameras, illumination, fixtures, sensors, or actuators
  may be purchased when they provide independent truth or a controlled
  intervention for a named research question.
- The project should begin from a credible real-world story and a specific
  decision problem, not from a camera modality, model, or hardware feature.
- A viable topic must explain who makes the decision, what can go wrong, why a
  local edge decision is necessary, and what independently checkable outcome
  can evaluate it.
- The existing palm, payment, worker-status, and legal-status stories remain
  out of scope.
- Palm recognition is not a required modality or default application.

## Working story preference

The preferred candidate family is non-personal visual record release in a
maintenance, repair, return, inspection, asset handover, or sample-tracking
workflow. The edge camera may decide `retain`, `reacquire`, or
`unknown/review`; it must not claim proof of repair completion, staff identity,
authorization, legal status, payment, safety, or a production-control result.

## Candidate-screening rule

Treat RGB, NoIR, IR, RAW, polarization, compression, and any model as possible
observations or interventions. They are not the research topic by themselves.
Promote a candidate only when the real decision and evaluation endpoint remain
meaningful after replacing the chosen camera technique with a simple baseline.
