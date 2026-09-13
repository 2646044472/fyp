# Pilot execution gates and timeline

## Scope

This is an execution aid for the finite RGB/NoIR action-rank audit. It does not promote a thesis or imply population-level transfer.

## Hardware inventory

Already available: Raspberry Pi 5B (8 GB, 64 GB), official RGB camera, official NoIR camera, IR illuminator, adapters and cables.

Minimum additions: rigid camera/target fixture, non-personal printed QR/AprilTag sheets in two material lots, transparent film or clear cover sheets, opaque cover, and a stable lamp or diffuser. The exact illuminator wavelength/power and camera revisions must be recorded before capture.

Conditional additions: inline USB power meter only if joules are a primary endpoint; lux meter only for logging, never as an NIR witness; photodiode/LED timing board only if a temporal/flicker cell is included. Do not purchase another camera or a larger model before the existing pair passes the action-rank gate.

## Stop/continue gates

1. **Bring-up gate:** both camera paths capture repeatable static frames, the decoder returns the independent marker payload, and exposure/white-balance settings are logged or manually fixed.
2. **Baseline gate:** fixed RGB, fixed NoIR+IR, fixed two-shot, scalar brightness/blur/IR-ratio, random and oracle controls are measured on clean, low-light and transparent-cover cells.
3. **Identification gate:** independent physical labels and an exact-code oracle are available; a matched RGB preview can be constructed for at least one low-light/glare two-world test.
4. **Transfer gate:** source-cell thresholds are frozen, held-out camera/lamp/material cells are blocked, and each cell has repeated sessions. A repeatable held-out rank inversion or a clearly bounded null is required by the decision date.
5. **Lock gate:** promote only if the selected policy has a preregistered risk/energy advantage that fixed two-shot and scalar baselines do not match. Otherwise lock the result as a negative benchmark and pivot the FYP to evaluation/protocol work, not a new model.

## Schedule aligned to the FYP window

- September 2026: bring-up, fixture, exact payload/oracle and baseline capture.
- October 2026: physical cells, exposure/timing logs, two-world identifiability test and frozen source policy.
- November 2026: held-out device/lamp/material repetitions, rank and risk-cost analysis.
- December 2026: runnable demo showing the finite decision and its abstention/reacquisition path; freeze the thesis claim based on the lock gate.
- 2027 H1: add repetitions, held-out lamps/material lots, optional power/timing instrumentation, and optimization only after the claim survives.

## Ethics and data

Use only printed non-personal targets and synthetic maintenance records. No face/palm data, production service, or safety actuation is required. Store raw frames locally with a manifest of capture settings and physical labels.

