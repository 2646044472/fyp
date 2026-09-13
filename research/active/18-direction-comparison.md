# Direction Comparison

> **Superseded decision (2026-09-03):** `START-WIT` is KILL as a positive
> direction. The current comparison gate is between unpromoted `CAUSE-NULL`
> and `OFFLINE-REV-NULL`; see
> [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md).

> **Further superseded (2026-09-03):** both `CAUSE-NULL` and
> `OFFLINE-REV-NULL` are also KILL as primary directions. See
> [28-round-20-null-boundaries-reconciliation.md](28-round-20-null-boundaries-reconciliation.md).

## Purpose

Compare the surviving directions before spending hardware budget. Scores are
the coordinator's current judgment from the active charter, candidate register,
divergence packet and validation packet; they are not empirical results and do
not establish novelty.

Scale: 1 = weak, 5 = strong. For collision risk, 5 = high risk.

| Candidate | Real-story fit | CS research core | Independent truth | One-year feasibility | Collision risk | Useful failure path | Current role |
|---|---:|---:|---:|---:|---:|---:|---|
| `START-WIT` shaft-start verification | 5 | 3 | 4 | 4 | 5 | 5 | Conditional physical preflight |
| `CAUSE-NULL` process-vs-sensor ambiguity | 5 | 4 | 4 | 3 | 3 | 5 | Fallback / possible pivot |
| `IR-CAUSE` active optical evidence | 3 | 3 | 4 | 5 | 4 | 4 | Existing-hardware backup |
| `RAW-JPEG-GATE` raw-vs-JPEG action test | 2 | 3 | 3 | 3 | 4 | 4 | Capability preflight only |
| Palm authentication / worker status | 2 | 3 | 1 | 1 | 5 | 1 | Killed |

## Interpretation

`START-WIT` is the best current bridge between the user's real maintenance
scenario and a measurable decision, but its positive claim is now limited to
shaft-start verification. Its weakness is collision risk: it must beat a
fixed-full-prefix reject baseline and cannot claim general equipment success.
A model that merely labels motor states is not enough.

`CAUSE-NULL` is more defensible as a scientific boundary if the paired physical
worlds can be constructed. It is less attractive as the first demo because the
negative result depends on demonstrating observational overlap carefully, not
just saying that one sensor is insufficient.

`WATERMARK-CLOSE` is KILL: without a source closure contract a receiver cannot
distinguish a delayed event from no event, while with such a contract standard
watermark/grace/sequence logic already supplies the decision. `SCHEMA-
QUARANTINE` is also KILL: signed semantic-contract comparison is the proper
conservative baseline for declared changes, while hidden procedure or
calibration meaning is not identifiable from local metadata and finite traces.

`IR-CAUSE` is cheaper because the cameras already exist, but its story is less
faithful to the user's factory/mobile-repair constraint and its active optical
mechanisms have stronger direct neighbors. It remains a practical backup, not
the main direction.

`RAW-JPEG-GATE` should not receive new hardware or thesis status before raw
capture capability, same-exposure pairing and cost-inclusive utility are
verified. It is a preflight, not the next research commitment.

## Decision

Use the following order:

1. Run the `START-WIT` trigger/rate and shaft-truth acceptance tests, then the
   fixed-full-prefix reject baseline pilot.
2. If the positive action frontier fails but paired process/sensor worlds are
   physically indistinguishable, promote `CAUSE-NULL` as a scoped negative
   result.
3. If the motor truth fixture is unsafe, unstable or unavailable, use the
   existing-hardware `IR-CAUSE` pilot as the only practical backup; do not
   revive the killed data-plane candidates.
4. Do not return to palm authentication, worker-status inference, payment
   security or generic offline synchronization without entirely new authorised
   data and threat-model resources.

## Lock condition

The FYP direction may be locked only after the first gate supplies:

- a repeatable independent truth signal;
- predeclared held-out load and sensor-mount cells;
- frozen simple baselines;
- an action-level result, not only accuracy/F1;
- a written explanation of how the result differs from ordinary motor-health
  classification;
- a safe tabletop demo that can run offline and synchronize later.

Until then, the project status remains **Gate 0 / conditional direction**.
