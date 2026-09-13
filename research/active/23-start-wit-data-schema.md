# START-WIT Pilot Data Schema and Analysis Rules

> **Superseded (KILL, 2026-09-03):** this schema is historical control context,
> not an active thesis data plan.

## Purpose

Define the episode-level record before hardware collection. The schema keeps
physical truth, policy observations, policy actions and post-hoc measurements
separate. It is part of the feasibility gate, not a thesis contribution by
itself.

## Experimental unit

One row is one complete start-command episode. Do not treat overlapping sensor
windows from one episode as independent samples.

Required grouping fields:

```text
episode_id, session_id, fixture_id, motor_id, load_id, mount_id,
condition_id, random_seed, operator_id
```

`operator_id` may be a pseudonymous operator code; no personal data is needed.
If there is only one motor, record that limitation explicitly and do not make
a cross-motor generalisation claim.

## Pre-command fixture fields

```text
condition_id
condition_description
load_id
load_mass_or_brake_setting
mount_id
mount_description
power_supply_id
ambient_temperature_c
network_mode
```

`condition_description` describes how the physical episode was staged. It is
not given to the policy. `network_mode` is descriptive until upload delay and
a remote baseline are measured.

## Timing fields

```text
command_ts_monotonic_ns
current_first_ts_monotonic_ns
accel_first_ts_monotonic_ns
truth_first_ts_monotonic_ns
decision_ts_monotonic_ns
truth_deadline_ts_monotonic_ns
clock_sync_method
```

Use one monotonic clock domain where possible. Wall-clock timestamps may be
stored for debugging, but latency calculations use monotonic timestamps.

## Independent truth fields

```text
truth_rule_version
truth_pulse_or_rpm_threshold
truth_started_before_deadline   # true / false / unresolved
truth_first_threshold_ts_ns
truth_quality
truth_exclusion_reason
```

The primary truth is binary. `unresolved` is excluded from the primary metric
and reported as an instrumentation result. It must never be converted to the
policy action `inspect`.

## Policy observation fields

Store raw or losslessly encoded sensor samples locally where storage permits:

```text
current_samples_path
acceleration_samples_path
current_sample_rate_hz
acceleration_sample_rate_hz
current_drop_count
acceleration_drop_count
sensor_config_hash
```

The policy may derive features from prefixes only. The independent truth stream
and post-command relay state must not be available through the policy process,
filesystem or message queue.

## Action fields

Record one action for each policy and one common maximum deadline:

```text
policy_id
action                 # running / failed-to-start / inspect
decision_ts_monotonic_ns
observation_duration_ms
cpu_time_ms
ram_peak_bytes
local_bytes_written
energy_joules
```

For a reproducible audit, save policy version, configuration hash and random
seed next to the episode record. Thresholds and model parameters must be
frozen before the held-out load/mount cell is evaluated.

## Derived outcomes

Let `y` be the binary truth and `a` the action:

| Truth `y` | Action `a` | Derived outcome |
|---|---|---|
| started-before-deadline | running | correct running |
| started-before-deadline | failed-to-start | false failed-start |
| started-before-deadline | inspect | unnecessary inspect |
| not-started-before-deadline | running | false running |
| not-started-before-deadline | failed-to-start | correct failed-start |
| not-started-before-deadline | inspect | necessary inspect |

Use the preregistered loss:

```text
L = 10 * false_running
  + 2 * false_failed_start
  + 1 * inspect
  + 0.1 * normalized_joules
```

Report the two kinds of error separately. Do not silently count every
`inspect` as an error: it is a deliberate action with a cost.

## Split and analysis

- Split by complete physical cells, not by windows: hold out one load/mount
  combination before freezing thresholds.
- Use at least three collection sessions and preserve session identifiers.
- Report per-session and pooled results; a pooled result alone is insufficient.
- Compare the fixed-window maximum deadline and sensor budget across policies.
- Plot action loss against decision latency and inspect rate; include an
  always-`inspect` reference point.
- Use bootstrap intervals over complete episodes only if the episode count is
  adequate; otherwise report the raw per-session table and label uncertainty as
  descriptive.

## Minimum data gate

Before any positive claim, require:

1. At least 20 valid episodes in each training condition and 10 valid episodes
   in each held-out condition as a practical pilot minimum.
2. At least two distinct load settings and one accelerometer remount.
3. No unresolved truth episodes in the primary held-out comparison, or an
   explicit exclusion analysis showing their effect.
4. Stable sensor timestamps and no unexplained sample loss that differs by
   policy.
5. Repeat of the held-out comparison in a separate session.

These counts are a feasibility minimum, not a power calculation or a license
for population-level generalisation.

## Stop conditions

Stop the positive mechanism analysis if:

- fixed fusion or one sensor is Pareto-optimal on the held-out cells;
- the effect appears only after random window splitting;
- truth quality changes with the policy condition;
- `inspect` is used as a hidden third truth label;
- the result cannot be reproduced in a separate session.

Then report a bounded null or run the preregistered `CAUSE-NULL` paired-world
test. Do not respond to a failed gate by increasing model size.

## Status

**HOLD (Amber).** Schema ready before collection; no empirical data are present.
