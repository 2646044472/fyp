# START-WIT Minimal Pilot Protocol

> **Superseded (KILL, 2026-09-03):** retain only as a bounded replication/control
> protocol; it is not a thesis feasibility gate. See
> [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md).

## Decision investigated

Whether a local edge node can verify whether a non-personal low-voltage motor
shaft starts before a declared deadline, using a short current and acceleration
prefix. This is a feasibility and falsification gate for
`START-WIT`, not a thesis lock.

## Real scenario

A technician at a factory room, temporary site or mobile repair visit starts a
small fan or DC motor while the network is unavailable. The node must create a
local `running`, `failed-to-start` or `inspect` record before the next repair
step. A false `running` record can skip necessary work; an unnecessary
`inspect` creates a repeat visit. The tabletop fixture is only a safe proxy for
the shaft-start decision.

## Minimum bill of materials

- Raspberry Pi 5B and a separate low-voltage 5 V fan or small DC motor;
- INA219 or INA226 inline current/voltage monitor;
- ADXL345 or MPU6050 accelerometer mounted on the motor housing;
- independent reflective optical tachometer or photointerrupter aimed at a
  marked rotating surface;
- low-voltage switch/relay module and manual emergency stop;
- rigid base, removable load/brake, reflective tape and protective guard;
- optional USB inline power meter for the Pi, used only for system-cost
  accounting.

Do not use mains voltage, exposed rotating parts or a safety-critical machine.
The tachometer is the shaft-start truth channel and must not be provided to
the decision policy. Current and acceleration are the policy observations.

## Episode protocol

1. Assign the physical condition before capture, but keep the evaluation truth
   binary: `started-before-deadline` or `not-started-before-deadline`. The
   policy action `inspect` is not a ground-truth class. Keep the condition log
   outside the policy input.
2. Issue a timestamped start command while the network is disconnected. Store
   the event locally; no cloud result may be consulted before the deadline.
3. Capture current, acceleration, command state, timestamps and link state for
   a fixed maximum of 5 seconds.
4. Use the optical tachometer only for the withheld truth label and post-hoc
   timing validation. Define `started-before-deadline` by a preregistered
   minimum pulse/rpm threshold and deadline. A staged borderline case is still
   assigned one binary truth by that rule; if the truth sensor cannot resolve
   it, exclude it from the primary analysis rather than relabel it `inspect`.
5. Repeat across at least three sessions, two load settings and one remount of
   the accelerometer. Hold out one load/remount combination before thresholds
   are frozen.

The first pilot should use scripted low-voltage conditions, not real worker or
production records.

## Policies and controls

- current-only fixed-window rule;
- acceleration-only fixed-window rule;
- fixed-full-prefix current plus acceleration reject policy;
- sequential early-stop policy using the same two streams;
- always-inspect control;
- offline truth oracle for reporting only.

All policies must use the same maximum observation window, command deadline and
available sensor budget. The early-stop policy cannot access the tachometer,
relay state after actuation, or network status as a proxy for the outcome.

## Primary outcomes

Use the fixed loss:

`L = 10 * false_running + 2 * false_failed_start + 1 * inspect + 0.1 * normalized_joules`

Report separately: error type, exact shaft-start accuracy, decision latency,
inspect rate, dropped samples, CPU/RAM, local bytes and energy. The experimental
unit is a complete command episode, not an arbitrary sliding window.

## Independence and identification checks

- The tachometer must measure mechanical rotation, not electrical command state.
- Current and acceleration timestamps must be checked against a separate
  command-time marker; do not infer timing from packet arrival alone.
- Vary load without changing the truth-label mechanism. Vary sensor mounting
  without changing the command outcome schedule.
- Construct a process-change versus sensor-bias pair. If the permitted current
  and acceleration traces can be made indistinguishable while the true cause
  differs, do not claim cause diagnosis; return `inspect` or pivot to
  `CAUSE-NULL`.
- A network outage is a context constraint. Do not claim a networking result
  unless upload delay, local deadline and a cloud/remote baseline are measured
  explicitly.

## Promotion and kill criteria

Keep `START-WIT` Amber only if the independent truth channel is repeatable and
the sequential policy gives a held-out action-loss or latency-cost improvement
that current-only, acceleration-only and fixed-full-prefix reject do not match. The
effect must repeat across sessions and survive the held-out load/remount cell.

Kill the positive mechanism claim if a single sensor or fixed fusion is
Pareto-optimal, the optical truth is coupled to current/acceleration, the result
depends on one motor/load, or the endpoint reduces to ordinary supervised
classification. If the paired process-change/sensor-bias construction is
successful, pivot to the scoped negative-result `CAUSE-NULL` study.

## First-week gate

- Day 1: motor, current monitor, accelerometer and tachometer bring-up;
- Day 2: verify independent pulse truth against manual start/stop trials;
- Day 3: collect normal and failed-start episodes under one load;
- Day 4: collect a second load and remount condition;
- Day 5: run frozen current-only, acceleration-only and fixed-fusion baselines;
- Decision: continue only if independent truth is stable and at least one
  held-out condition creates a meaningful, repeatable decision trade-off. A
  baseline tie is a kill result, not a reason to add a larger model.

## Current status

**HOLD (Amber).** This protocol makes the next gate executable; it does not
establish novelty or justify a production maintenance claim.
