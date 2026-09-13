# PRF-TR Loss Specification Correction

**Date:** 2026-09-05  
**Decision:** A single fixed weighted loss must not be the sole primary
endpoint for PRF-TR.

## Problem found

Earlier drafts use a scalar such as:

```text
10 * false_retain_rate + 1 * unknown_rate + 0.1 * normalized_energy
```

The expression is useful for a preregistered operating point, but its
coefficients are not yet derived from an accessible operator or partner. A
claim that digital and physical cells reverse the "best action" under only one
such scalarization could be an artefact of arbitrary weights, rather than a
physical observation result.

## Correct evaluation object

For each physical or digital cell `c` and fixed action/policy `a`, record the
outcome vector:

```text
R_c(a) = (
  false_retain_rate,
  unknown_or_review_rate,
  extra_capture_count,
  capture_plus_decode_latency,
  bytes_written,
  measured_energy_if_available
)
```

The first result is the **Pareto frontier** over this vector: an action is
dominated when another action is no worse in every stated component and better
in at least one. This does not require inventing a monetary value for a human
review or joule.

Then define a small family of preregistered scalarizations, rather than one
post-hoc score. The report must state whether the digital and physical best
action agree over a declared range of false-retain priority, review cost and
capture-cost weights. Actual capture time, bytes and energy are measured; the
review term remains an explicit scenario parameter unless a real workflow
supplies a defensible value.

## What now counts as a meaningful result

1. **Frontier preservation:** the same policies remain non-dominated in source
   digital and held-out physical cells, across the declared cost scenarios.
2. **Frontier failure:** a policy selected from digital tests is physically
   dominated by a fixed baseline, or the preferred action changes over a
   preregistered, nontrivial cost range.
3. **Decision ambiguity:** all apparent changes occur only at a single
   arbitrary weight or disappear after session blocking; report no positive
   action-transfer claim.

## Required controls

- fixed NoIR-visible;
- fixed NoIR+IR, only when a fixed IR illuminator is included;
- fixed visible then NoIR+IR two-shot, only when a fixed IR illuminator is
  included;
- standard IQA/scalar-quality gate;
- always-review;
- random action as a sanity control;
- source/held-out sessions and independent payload/physical labels.

## Consequence for the direction

This correction strengthens the finite evaluation but does not create a new
method contribution. If fixed two-shot or scalar IQA is Pareto-optimal on
held-out physical cells, PRF-TR remains a bounded null and must not be promoted
as a thesis mechanism.

PIVOT: use frontier preservation/failure as the primary endpoint; retain one
advisor-approved scalar loss only as a secondary operating-point illustration.
