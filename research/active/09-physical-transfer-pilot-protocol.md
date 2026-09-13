# Physical RGB/NoIR Transfer Pilot (pre-registration draft)

## Purpose

Test whether a small digital-corruption benchmark is an adequate proxy for named physical camera-path conditions on the purchased Raspberry Pi 5 setup. This is a gate, not a thesis commitment.

## Story and decision

A lab maintainer records a non-personal printed code on a local edge node and chooses `retain`, `reacquire`, or `unknown`. A false retain contaminates a measurement log; reacquisition consumes latency and energy. The edge constraint is the capture-time budget and the absence of a remote quality oracle.

## Observation and truth

- Target: fixed QR/AprilTag/ArUco sheet with a source payload stored before capture.
- Truth: deterministic exact-payload equality from an independent decoder, not the candidate quality score.
- Physical labels: scripted clean, low visible light, transparent film/water deposit, opaque lens cover, IR blocked/saturated, camera disconnect, and intentional frame interruption.
- Logged controls: lux at target plane, distance/pose, camera path, frame timestamp, exposure, gain, white balance, illuminator state, and per-episode energy.

## Actions and baselines

Compare at equal declared capture/energy budget:

1. always RGB;
2. always NoIR + fixed IR;
3. fixed RGB then NoIR + IR two-shot;
4. brightness/blur threshold followed by one recapture;
5. random action;
6. oracle action using the scripted physical-cell label (upper control only).

No learned selector is used in the first gate. A learned method can be considered only if it beats these controls on held-out cells.

## Paired digital cells

For each clean capture, create only predeclared post-capture transformations: brightness, blur, noise, zero mask, random mask, and missing frame. Do not tune transformation severity on the scored physical cells.

## Primary outcomes

- exact-code validity and false-retain rate;
- `unknown` and reacquisition rate;
- latency and joules per episode;
- Kendall/Spearman rank correlation between digital-cell and physical-cell policy outcomes, with bootstrap intervals.

## Two-world check

Construct matched visible-lux pairs for clean-low-light and transparent-cover states. If RGB/NoIR observations plus logged controls cannot separate the labels, report non-identifiability rather than a cause detector.

## Promotion and kill criteria

Promote only if a preregistered, repeatable physical-vs-digital action-rank inversion remains on held-out repetitions and is not explained by a brightness/blur baseline or fixed two-shot policy. Kill the thesis claim if rankings agree, the fixed policy is Pareto-optimal, labels/oracle are not independent, or the effect disappears under remount/repeat. A null becomes a bounded transfer audit/negative appendix.

## Minimum schedule

By December 2026: one fixed stand, one printed target family, at least four physical cells, repeated episodes, and a reproducible Pi capture/decoder script. In 2027 H1: held-out covers, distances, lux cells and remounts; no claim beyond the purchased camera pair.

## Procurement gate

Buy only a rigid mount, lux meter or calibrated light, USB inline power meter, and repeatable transparent-cover fixture. Defer a photodiode, programmable power supply, second camera, or larger model until the first pilot shows an unexplained timing/power effect.

## Status

**PIVOT / Amber.** This protocol is evidence-gathering infrastructure. It does not establish novelty or lock a thesis before the measured gate passes.
