# Working Prospectus: Edge Verification of Shaft-Start Outcomes

> **Superseded (KILL, 2026-09-03):** post-audit evidence shows that direct
> tachometer/speed feedback is the stronger operational baseline and that the
> prefix/reject policy is established ETSC. This file is historical protocol
> context only; see [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md).

## Status

**Primary conditional candidate, 2026-09-03.** This is the next physical preflight because it matches the user's factory, temporary-site and mobile-repair context more closely than the optical marker branch. It is not yet promoted and must first survive direct-neighbor and baseline checks.

## Real problem

During a weak-network or disconnected repair visit, a technician sends a start command to a non-personal low-voltage motor or fan and must record whether its shaft crossed a declared rotation rule before the deadline. A false `running` record can cause the next maintenance step to be skipped; a false `inspect` result wastes a site visit. The local edge node must make the first decision before a remote service or later synchronization is available.

The equipment is a benign low-voltage tabletop fixture. It is not a safety interlock and does not represent a production machine.

## Research question

Can a low-cost edge node use the first 2--5 seconds of motor-current and accelerometer evidence to decide `running / failed-to-start / inspect` for a binary shaft-start outcome at lower action loss than one-sensor and fixed-full-prefix reject baselines under held-out loads and mounting conditions?

## Narrow claim under test

For a declared low-voltage motor fixture and independently measured shaft-start outcome, a frozen sequential evidence policy improves the maintenance-record action frontier at fixed latency, inspection and sensor budgets over current-only, vibration-only, fixed-full-prefix reject and always-inspect controls.

This is a shaft-start evidence study, not a claim about pump flow, pressure, valve position, downstream equipment success, a new fault-diagnosis framework, predictive-maintenance model, motor classifier or safety guarantee.

## Formal decision object

Let `c` be the binary physical command outcome (`started-before-deadline` or
`not-started-before-deadline`), `z_t` the permitted current/acceleration prefix
through time `t`, `a` the record action, and `L(c,a)` the fixed record loss. The
policy may stop early and emit `running`, `failed-to-start` or `inspect`; it
cannot use the independent relay/tachometer channel at decision time. The
primary endpoint is action loss, not F1 alone. `Inspect` is an action, never a
truth class.

Primary loss:

`L = 10 * false_running + 2 * false_failed_start + 1 * inspect + 0.1 * normalized_joules`

Freeze the weights and decision deadline before held-out testing. Report detection latency, error type, inspect rate, CPU/RAM, bytes and energy separately.

## Minimum fixture

- Pi 5 or a Pi-plus-MCU acquisition path;
- small low-voltage DC fan or motor with manual emergency stop;
- inline current sensor and accelerometer mounted independently from the motor control line;
- independent optical tachometer or relay/contact truth channel withheld from the policy;
- staged conditions: normal shaft start, blocked/failed shaft start, variable load, altered mounting and power/network interruption;
- local event manifest with command time, truth time, sensor timestamps and link state.

The independent truth channel must not be inferred from the same current or vibration stream. No human or worker data are required.

## Controls and evaluation

1. current-only fixed-window rule;
2. vibration-only fixed-window rule;
3. fixed-full-prefix current plus vibration reject policy;
4. sequential early-stop policy using the same observations;
5. always-inspect upper-coverage control;
6. offline oracle using the independent truth channel only for reporting.

Hold out at least one load condition and one remounted sensor condition. Use repeated command episodes as the experimental unit, not arbitrary windows. Simulate link-unavailable and link-available states only as a logged constraint; do not claim a network contribution unless local-versus-upload behavior is explicitly measured.

## Promotion and kill gates

Promote only if the sequential policy produces a repeatable held-out action-loss or latency-cost advantage that current-only, vibration-only and fixed-full-prefix reject do not match, with independent truth and remount repetition.

Kill the positive mechanism claim if a fixed-full-prefix reject policy or a single sensor is Pareto-optimal, the independent truth channel is coupled to the sensed signal, the result depends on one motor/load, or the task becomes ordinary supervised classification. If process-change and sensor-bias worlds can be made observationally identical, pivot to the `CAUSE-NULL` negative-result study.

## Feasibility and risk

The main feasibility risk is not compute; it is obtaining an independent
shaft-start truth channel and preventing current/load, vibration/mount and
control timing from being conflated. The second risk is direct collision with
resource-aware screen/confirm and sensor-fault diagnosis work. The candidate
therefore remains Amber until the smallest baseline matrix is run.

## Backup and non-goals

`IR-CAUSE` remains a lower-cost optical backup using the existing RGB/NoIR hardware. `OFFLINE-MERGE`, palm authentication, worker-status inference, payment authorization and generic offline synchronization are excluded. A 3D enclosure may improve repeatability and demonstration quality, but it is not a contribution.

## Evidence checked

- [Maintenance weak-connectivity divergence packet](../ops/divergence/2026-09-03-maintenance-weak-connectivity-divergence.md)
- [Maintenance-story validation audit](../ops/validation/2026-09-03-ir-cause-story-and-concrete-endpoint.md)
- [Project charter](00-project-charter.md)
