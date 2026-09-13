# START-WIT Baseline and Sequential Policy Specification

> **Superseded (KILL, 2026-09-03):** early prefix/reject policies are an
> established method family; this is historical control documentation only.

## Purpose

Specify policies before collecting or inspecting held-out episodes. The goal
is to test the shaft-start action frontier, not search for a new classifier
architecture.

## Common notation

- `d`: preregistered maximum decision deadline, initially 5 seconds.
- `z_t`: current and acceleration samples available through time `t`.
- `y`: independent binary truth, `started-before-deadline` or
  `not-started-before-deadline`.
- `a`: action, `running`, `failed-to-start` or `inspect`.
- `F(z_t)`: frozen feature extractor using only samples up to `t`.

Every policy receives the same command trigger and maximum window. No policy
receives optical truth, relay state after actuation, fixture condition,
network state or post-deadline samples.

## Feature contract

Use a small declared feature vector rather than architecture search:

- current: mean, median, RMS, maximum, minimum and slope over the prefix;
- acceleration: per-axis mean/RMS, vector-magnitude RMS, maximum and slope;
- optional fixed-frequency spectral magnitude only if the sampling gate proves
  the rate is stable; record it as preregistered, not post-hoc.

All features are computed causally from the prefix. Missing samples are marked
and never silently forward-filled across an episode boundary.

## Policy P0: current-only

Fit a simple calibrated binary score from current features on non-held-out
conditions. Choose two action thresholds on a validation subset using the fixed
loss: high score -> `running`, low score -> `failed-to-start`, middle ->
`inspect`. Freeze thresholds before held-out evaluation.

## Policy P1: acceleration-only

Use the same procedure as P0 with acceleration features only. This controls
whether current contributes incremental evidence.

## Policy P2: fixed-full-prefix fusion with reject

Fit one simple calibrated score from current plus acceleration features after
waiting for the complete maximum window `d`. Use two frozen thresholds to emit
`running`, `failed-to-start` or `inspect`. This is the strongest simple full-
prefix reject baseline against which sequential stopping must compete.

## Policy P3: sequential early stopping

Use the same fused score construction as P2, evaluated at declared prefix
checkpoints, for example 0.5, 1, 2, 3, 4 and 5 seconds. At each checkpoint:

1. compute the score from data available so far;
2. emit `running` or `failed-to-start` only when its calibrated action margin
   exceeds the preregistered stopping threshold;
3. otherwise continue to the next checkpoint;
4. emit `inspect` at the maximum deadline if no stopping threshold is met.

The stopping threshold is selected on training/validation conditions only. P3
cannot inspect future samples, truth, fixture labels or network state.

This is an evaluation policy for the endpoint, not a claim of a new sequential
inference algorithm. If P3 does not beat P2 at equal action cost, kill the
positive mechanism claim.

## Policy P4: always inspect

Emit `inspect` at the declared command checkpoint without using policy sensors.
Include its action loss as a conservative reference point.

## Timing control

Optionally replay identical acquired streams to separate policy compute time
from sensor/acquisition time. Report replay and live-Pi timing separately; do
not use replay timing as end-to-end latency.

## Training and leakage rules

- Group by complete physical episode.
- Hold out one complete load/mount cell before threshold selection.
- Never choose a feature, checkpoint, threshold or loss weight after viewing
  held-out actions.
- If class proportions change for a pilot, report the sampling rule and keep
  the fixed action loss unchanged.
- Preserve raw streams and the exact policy configuration hash.

## Primary comparison

The positive result requires P3 to show a repeatable held-out advantage over
P0, P1 and P2 in at least one action-loss/latency trade-off across a separate
collection session. A change in F1 alone is not sufficient.

## Negative outcomes

- P2 dominates P3: sequential stopping adds no measured value; kill the
  positive mechanism claim.
- P0 or P1 dominates P2: one sensor is sufficient; kill the fusion claim.
- All policies perform poorly because truth or timing is unstable: fix the
  instrumentation, not the model.
- Results change only under random window splits: treat as leakage and discard
  the apparent gain.
- P3 is useful only for one motor/load: report a bounded fixture result or
  pivot to `CAUSE-NULL`; do not generalize.

## Status

**HOLD (Amber).** Transparent policy specification ready before data
collection; no empirical result exists.
