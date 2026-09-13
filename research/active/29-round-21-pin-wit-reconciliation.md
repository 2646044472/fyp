# Round 21 Reconciliation: PIN-WIT Closure

## Decision investigated

Whether `PIN-WIT` can remain an undergraduate FYP direction after direct
audits of GPIO loopback, interconnect testing, BIST and adaptive diagnostic
test-pattern generation.

## Evidence checked

- [PIN-WIT divergence audit](../ops/divergence/2026-09-03-pin-wit-divergence.md)
- [PIN-WIT validation audit](../ops/validation/2026-09-03-pin-wit-validation.md)
- Active candidate register and Round 20 reconciliation.

## Reconciled result

[KILL] `PIN-WIT` is a finite interconnect-test and test-pattern design
problem, not a new edge mechanism. With a declared harness graph, allowed
stimulus words and finite fault set, faults with the same response under every
allowed word are indistinguishable to every adaptive policy. A fixed
fault-signature battery separates every separable staged class; adaptivity can
only change expected test order or cost under a separately justified prior.

A two-MCU responder supplies the same controllability/observability purpose
as established test-access or loopback designs. The current project has no
verified repeated harness-commission workflow, fault incidence, independent
field outcome, hard test deadline or energy constraint that could make a
known diagnostic-test formulation into a distinct FYP object.

## Search reset

The current hardware-first candidates are closed. Before generating another
candidate, obtain one accessible real workflow and record: the actor's repeated
decision, failure consequence, available independent outcome evidence, actual
operational restriction, and expected number of repeated cases. This is not a
request for a device specification; it is the minimum evidence needed to avoid
building another invented bench story around an established mechanism.

## Status

**`START-WIT`, `CAUSE-NULL`, `OFFLINE-REV-NULL` and `PIN-WIT`: KILL as
primary FYP directions. No live candidate remains.**
