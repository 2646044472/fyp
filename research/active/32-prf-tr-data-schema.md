# PRF-TR Minimum Data Schema and First Pilot

## Purpose

This file turns `PRF-TR` into a reproducible first gate. It is an experiment
specification, not evidence that the direction has already passed. The study
must remain finite: one confirmed Raspberry Pi Camera NoIR v2 path, one
declared printed-marker family, named physical cells, blocked sessions, and no
population transfer claim. An extra camera path is optional, not required.

## Unit of analysis

The primary unit is a `session x physical-cell x action` record. A frame is an
observation inside a session, not an independent device or environment. The
minimum pilot uses 3 sessions, 4 physical cells, 20 attempts per action per
session, and a fixed target/payload registry. More frames from one static mount
do not replace a new session, remount, lamp, cover lot, or camera path.

## Pre-registered objects

### Physical truth

- `payload_id`: immutable identifier created before capture.
- `expected_payload`: expected code stored outside the policy process.
- `oracle_payload`: pre-capture reference result from an independent decoder or
  flatbed/phone check.
- `target_verified`: `oracle_payload == expected_payload`; targets with a false
  value are invalid and excluded before policy analysis.
- `decoded_payload`: output of the edge decoder for this episode.
- `decoded_exact`: `decoded_payload == expected_payload`.
- `physical_cell`: assigned before capture, never inferred from image quality.

The oracle result is used for evaluation only. The edge policy cannot read it
before choosing an action.

### Physical cells

The first four cells are:

1. `clean_high_light`
2. `clean_low_light`
3. `transparent_cover_glare`
4. one held-out `lamp`, `cover_lot`, `remount`, or optical-path cell

Record the actual fixture intervention, lamp identifier, cover identifier,
camera identifier/path, target distance, angle, and remount identifier. The
labels describe the staged fixture, not a claimed universal field taxonomy.

### Digital cells

Apply only predeclared transformations to clean captures:

- brightness reduction;
- blur;
- sensor-like noise;
- structured or random masking;
- frame omission/interruption.

Store the transformation name and severity in the manifest. Do not choose
severity after viewing scored physical results.

## Required episode fields

```text
session_id, attempt_id, payload_id, physical_cell, digital_cell,
bundle_id, first_capture_id, second_capture_id,
target_lot, lamp_id, cover_id, remount_id, camera_path,
distance_mm, angle_deg, illumination_state, illuminator_state,
exposure_us, analogue_gain, white_balance_state, frame_timestamp,
trigger_timestamp, action, action_sequence, frame_path_or_hash,
oracle_payload, target_verified, decoded_payload, decoded_exact, decoder_margin,
brightness_metric,
blur_metric, saturation_fraction, capture_latency_ms, decode_latency_ms,
bytes_written, energy_mj, reviewer_time_ms, exclusion_code, notes
```

`oracle_payload` and `target_verified` are target-registry/preflight fields;
they validate the printed object but are never policy inputs. `decoded_payload`
and `decoded_exact` are episode-level post-action evaluation fields and must
not be fed into a pre-action selector. If raw frames are retained, use a
manifest and hash; do not silently change the storage policy between cells.

## Actions and controls

Every action uses the same decoder and expected-payload semantics:

- `visible_noir_only`: one fixed NoIR-camera capture under the declared visible
  lamp with the IR source off;
- `noir_ir_only`: one fixed NoIR-camera capture with fixed IR, only if the
  optional illuminator path is included;
- `fixed_visible_then_ir`: visible-light capture followed by NoIR+IR, only if
  the optional illuminator path is included;
- `scalar_gate`: brightness/blur/decoder-confidence rule followed by one
  predeclared second capture;
- `random_action`: fixed random seed and declared action probabilities;
- `always_review`: local review procedure with fixed time cost;
- `oracle_cell_action`: evaluation upper control only, never a deployable input.

The first pilot does not search architectures or tune a learned selector. The
two-shot and always-review controls are adversarial baselines, not optional
comparators.

### Action-consistent replay

For each `session_id x physical_cell x bundle_id`, pre-capture two ordered
frames with the same locked fixture state. The policy sees only
`first_capture_id` initially; it may receive the distinct `second_capture_id`
only after choosing `reacquire`. Digital cells apply their fixed transform
separately to each slot. A second decode of the first frame is not a
reacquisition. The full rule and stop condition are recorded in
`minutes/09-05-prf-tr-action-replay-integrity.md`.

## Cost and outcome definition

For each cell and action, report:

- false retain: a retained result with `decoded_exact = false`;
- unknown/review rate;
- exact-code success;
- reacquisition count; a value above zero requires a distinct second capture
  identifier in the episode record;
- decision-to-completion latency;
- bytes written/transmitted if applicable;
- measured energy in mJ.

The primary endpoint is the outcome vector:

```text
R(a) = (
  false_retain_rate,
  unknown_or_review_rate,
  reacquisition_count,
  decision_to_completion_latency,
  bytes_written,
  measured_energy
)
```

Report the Pareto frontier: an action is dominated when another declared action
is no worse on every reported component and better on at least one. This is the
primary digital-versus-physical comparison. Before held-out scoring, freeze a
small family of scalar cost scenarios as a secondary illustration. Do not tune
or choose a scenario after inspecting held-out physical results. If review time
is part of the story, include it explicitly rather than treating review as
free.

## Blocking and analysis

Before any threshold fitting, block one physical cell/session combination as
held out. Fit thresholds only on source cells. Then compare:

1. digital-cell Pareto frontier;
2. held-out physical-cell Pareto frontier;
3. whether a source-selected non-dominated action becomes physically dominated;
4. whether a fixed two-shot or scalar rule dominates after cost accounting.

Use bootstrap resampling over sessions or remounts, not individual frames.
Report per-cell tables and confidence intervals. A frontier failure counts as
evidence only if it repeats across at least three independent sessions, is not
explained by a fixed baseline, and remains under the preregistered secondary
cost scenarios.

## First-week acceptance gate

Pass the gate only when all items below are true:

- the confirmed NoIR path produces repeatable static captures under the
  declared visible-light condition;
- the independent payload registry and oracle agree on clean controls;
- exposure, white balance, timing and camera-path metadata are recorded;
- the four physical cells can be re-created from the fixture log;
- every declared control can be run without changing decoder settings; optional
  IR controls are excluded until a fixed IR path is installed and logged;
- the cost ledger records capture/decode time and, if claimed, energy;
- one source/held-out split is frozen before scored analysis.

If any item fails, report an apparatus or identification failure, not model
accuracy and not a positive research result.

## Lock and kill rules

Promote the empirical claim only if a held-out physical frontier failure is
repeatable and survives fixed two-shot, scalar-quality and always-review
controls. Preserve the study as a negative-result FYP if digital and physical
frontiers agree with useful confidence intervals or if the two worlds are
observationally indistinguishable.

Kill the positive mechanism claim if the fixed controls are Pareto-optimal,
the oracle or physical labels are not independent, costs cannot be measured,
or the effect disappears after remount/session blocking. Do not respond to a
null by adding a larger model, another camera, or more digital corruptions.

## Current feasibility status

The user currently confirms a Raspberry Pi and Camera NoIR v2. Any extra
camera and IR illuminator are [GAP] rather than required inventory. The
workspace contains no PRF-TR physical data, acquisition log, or energy log.
Therefore this schema is ready for single-camera bring-up, but the FYP
direction remains `PIVOT (Amber)` until the first gate is actually run.
