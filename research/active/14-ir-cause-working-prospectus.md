# Working Prospectus: Weak-Network Edge Maintenance Evidence Verification

## Status

**Conditional working direction, 2026-09-03.** The FYP direction is weak-network edge maintenance evidence verification. The IR action is one candidate mechanism inside the pilot, not the thesis title by itself. This prospectus does not claim global novelty and does not lock the thesis until the physical pilot passes the promotion criteria.

## Real problem

A technician in a factory room, temporary work site or mobile repair setting records evidence about a non-personal equipment label or maintenance indicator. Network access may be weak or unavailable, and the local node must decide whether the evidence is sufficient to retain the record, acquire one additional observation, or mark the episode unknown. A false retained record can cause a wrong maintenance handover or a repeated site visit; an unnecessary reacquisition consumes latency, energy and technician time. The edge constraint matters because the decision must be made locally without uploading raw images to a remote quality service.

## Research question

When a local maintenance image is ambiguous, can a cost-aware edge evidence policy decide whether one additional optical observation is justified under held-out physical conditions, after capture cost is charged?

The named physical contrast is:

- clean target under low visible light;
- the same target behind a declared transparent cover or film.

The contrast is a test condition, not a claim that the camera can generally diagnose contamination or material state. A 3D-printed equipment box or panel is only a repeatable demo fixture; it is not the contribution.

## Narrow claim under test

For the purchased Pi 5B and RGB/NoIR camera pair, a preregistered local evidence policy reduces conditional maintenance-record action loss on held-out light/cover cells beyond fixed RGB, fixed NoIR+IR, fixed RGB-then-NoIR+IR two-shot, passive quality, IR-ratio and always-reacquire controls at matched capture, latency and energy budgets. The first policy under test is the IR-on intervention.

The claim is allowed to fail. A null, rank-preservation result or two-world non-identifiability result is scientifically useful and closes the stronger claim.

## What this is not

- not a new causal-diagnosis framework;
- not generic adaptive sensing or modality selection;
- not passive camera-health monitoring;
- not a camera-family transfer guarantee;
- not a RAW, object-detection, authentication or safety-system claim;
- not a claim that Pi deployment itself is the contribution.

## Formal decision object

Let `c` be the fixture-assigned physical cell, `z` the pre-intervention observation and logged controls, `a` an allowed capture action, and `L(c,a)` the fixed loss. The oracle action is `argmin_a L(c,a)`. The edge policy must use only the permitted prefix `z`; it cannot inspect `c`. The central test is whether IR-on changes the attainable action-risk frontier on blocked cells, not whether a classifier can name `c`.

Primary loss:

`L = 10 * false_retain + 1 * unknown + 0.1 * normalized_joules`

Keep latency, exact-code success and reacquisition rate as separate reported outcomes. Freeze the loss and thresholds before reading held-out results.

## Minimum experiment

1. Generate and register printed QR/AprilTag payloads before capture.
2. Assign physical cells before capture using a fixture log: clean/high-light, clean/low-light, transparent cover, and one held-out lamp or cover placement.
3. Use a rigid mount and static target. Log camera path, exposure, gain, white balance, trigger-to-frame delay, illuminator state and power where measurable.
4. Collect at least three independent sessions, with at least 20 captures per action per session and a blocked held-out cell.
5. Use one decoder and an independent exact-payload oracle. Decoder confidence is an input or baseline, never ground truth.
6. Compare fixed RGB, fixed NoIR+IR, fixed two-shot, passive brightness/blur/decoder-quality, IR-ratio, conservative one-extra-capture escalation, random and an offline cell-label oracle.

## Promotion and kill gates

Promote the working direction to a thesis lock only when all conditions hold:

- physical labels and payload truth are independent and repeatable;
- the IR action is implemented and measured at the declared cost;
- a held-out action-cost improvement repeats across sessions and at least one held-out light/cover cell;
- fixed two-shot, always-reacquire and simple scalar controls do not remove the improvement;
- the result survives remount or placement repetition.

Kill the positive thesis claim if the two worlds remain observationally overlapping with different best actions, if fixed two-shot or always-reacquire is Pareto-optimal, if IR-ratio/passive quality matches, or if the effect disappears under repetition. Report the finite null/boundary result instead of adding a larger model.

## Feasibility and ethics

The current charter records a Pi 5B, RGB camera, NoIR camera, IR illuminator and adapter hardware as available [K]. The study uses inert printed targets and transparent covers only [K]. Camera revision, illuminator specification and eye-safety details, rigid fixture, power measurement and exact capture API remain [GAP]. No personal biometric data, production service or safety actuation is required.

## Backup path

`RAW-JPEG-GATE` remains a separate feasibility gate. It can replace this direction only if the purchased camera produces a stable same-exposure RAW/JPEG pair and RAW improves the cost-inclusive held-out action frontier over JPEG and fixed reacquisition controls. Otherwise it is an engineering or negative appendix.

## Evidence checked

- [Active direction state](README.md)
- [Physical RGB/NoIR transfer protocol](09-physical-transfer-pilot-protocol.md)
- [Cross-device action-rank pilot](11-cross-device-action-rank-pilot.md)
- [Focused validation audit](../ops/validation/2026-09-03-ir-cause-raw-jpeg-gate-validation.md)
