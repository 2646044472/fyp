# START-WIT Pilot Preregistration

> **Superseded (KILL, 2026-09-03):** retained only as a transparent control
> design; no positive thesis claim may be evaluated from it.

## Scope

This preregistration defines the first physical gate for `START-WIT`. It is a
feasibility and falsification test, not a thesis-lock or novelty statement.

## Primary question

Does a sequential policy using the first 2-5 seconds of motor-current and
accelerometer evidence improve the shaft-start maintenance-record action
frontier over fixed-full-prefix reject policies at the same maximum deadline
and sensor budget?

## Truth and actions

The independent mechanical truth is binary:

- `started-before-deadline`: the optical witness reaches a preregistered pulse
  or RPM threshold before the deadline;
- `not-started-before-deadline`: it does not.

The policy actions are:

- `running`;
- `failed-to-start`;
- `inspect`.

`Inspect` is neither a truth class nor a measurement failure. Borderline
episodes whose optical truth cannot be resolved by the fixed rule are excluded
from the primary analysis and reported separately.

## Hypotheses

- **H1 (positive):** sequential early stopping has lower expected action loss
  or lower latency at the same action-loss level than every simple baseline on
  at least one held-out load/mount cell, with the effect repeated by session.
- **H0 (kill):** current-only, acceleration-only, fixed fusion or always-
  `inspect` is Pareto-optimal on the held-out cells.
- **H2 (negative pivot):** a process-change world and a sensor-bias world can
  be staged with indistinguishable permitted observations while their true
  causes differ. If H2 is supported, pivot to `CAUSE-NULL` and do not claim
  cause diagnosis.

## Unit and conditions

- Unit: one complete command episode, not a random window.
- Sessions: at least three separate setup/collection sessions.
- Physical conditions: normal start, deliberate failed start, two load settings
  and one accelerometer remount.
- Hold-out: one complete load/remount combination is withheld before thresholds
  or model parameters are frozen.
- Connectivity: run the local decision with the network disconnected; record
  link state. Do not claim a networking result until local deadline and upload
  delay are separately measured.

## Policies

1. Current-only fixed-window rule.
2. Acceleration-only fixed-window rule.
3. Fixed-full-prefix current-plus-acceleration reject baseline.
4. Sequential early-stop policy using the same observations.
5. Always-`inspect` control.

The truth channel, relay state after actuation and network state cannot be read
by any policy. The maximum observation window and deadline are identical across
policies.

## Primary metric

Freeze the following loss before held-out evaluation:

`L = 10 * false_running + 2 * false_failed_start + 1 * inspect + 0.1 * normalized_joules`

Report action loss, latency, error type, inspect rate, sample drops, CPU/RAM,
local bytes and energy separately. Do not replace the primary metric with F1.

## Independence checks

- Optical truth measures physical rotation, not relay state or current.
- Command, current, acceleration and optical timestamps are recorded from a
  common timing reference or cross-checked against one.
- Load and mount changes do not alter how the truth label is generated.
- The policy process has no code path, file path or bus access to the truth
  stream.
- A manual trial confirms that the truth signal changes when the rotor stops.

## Kill and pivot rules

Kill the positive mechanism claim if H0 holds, the result depends on one motor
or one failure staging, or the task becomes ordinary motor-health
classification. Report a bounded null instead of increasing model size.

Pivot to `CAUSE-NULL` if the paired process-change/sensor-bias construction
supports observational indistinguishability. Return to `IR-CAUSE` only if the
motor fixture cannot be made safe and repeatable.

## Current status

**HOLD (Amber).** No data have yet been collected; all empirical claims remain
[GAP].
