# PRF-TR Pi bring-up

`prf_tr_bringup.sh` records a single static Camera NoIR v2 capture episode for
the PRF-TR physical gate. It is not a decision policy and does not make a
maintenance record.

On the Pi, first verify the Camera NoIR v2 index manually:

```bash
rpicam-hello --list
rpicam-hello --camera 0 -t 0
```

Create a one-line file containing the expected payload before capture. Keep
that registry outside any later policy-fitting path.

```bash
printf '%s\n' 'ASSET-EXAMPLE-001' > expected_payload.txt
chmod +x prf_tr_bringup.sh
./prf_tr_bringup.sh \
  --out prf-tr-screening \
  --session s01 --attempt a001 --cell clean_high_light \
  --camera 0 --camera-label noir_visible --illumination visible_on_ir_off \
  --expected-payload expected_payload.txt
```

For more than one printed target, freeze the registry before capture with
`prf_tr_targets.py`. This tool does not create QR codes and cannot verify a
target by running the Pi decoder. Its verification input must come from an
independent pre-capture reference scan, such as a phone or flatbed decoder.

```bash
printf '%s\n' 'ASSET-001' 'ASSET-002' > payloads.txt
python3 prf_tr_targets.py create \
  --out prf-tr-screening/target-registry.tsv \
  --payloads payloads.txt

# oracle.tsv has exactly: payload_id<TAB>oracle_payload
python3 prf_tr_targets.py verify \
  --registry prf-tr-screening/target-registry.tsv \
  --oracle-results oracle.tsv \
  --out prf-tr-screening/target-registry-verified.tsv
```

Keep false `target_verified` rows in the verification audit, but exclude them
from decision analysis. The analysis tool rejects them rather than silently
turning a target-printing error into a decoder error.

For each subsequent capture, change the attempt ID and log only a preassigned
physical cell. `episodes.tsv` is a capture manifest, not the full research
schema. Add action, reacquisition, review, energy and source/held-out fields
before using any episode in the PRF-TR analysis.

## Freeze the schedule before capture

Use `prf_tr_plan.py` to create an immutable, shuffled TSV plan before any
physical capture. It assigns the source/held-out split from predeclared cell
IDs, repeats every session/cell/action combination, and refuses to overwrite
an existing plan.

```bash
python3 prf_tr_plan.py \
  --out prf-tr-screening/episode-plan.tsv \
  --sessions s01,s02,s03 \
  --cells clean_high_light,clean_low_light,cover_glare,held_out \
  --held-out-cell held_out \
  --attempts 20
```

The plan does not choose an action at runtime or label image quality. It is a
capture-order artifact that prevents choosing the held-out physical condition
after looking at results. Each action row shares a `bundle_id` with the other
action rows for the same session/cell/attempt. That ID links frozen policy
replays to the same hidden initial/recapture capture bundle. Run its local
tests with:

```bash
python3 code/prf_tr/test_prf_tr_plan.py
```

## Freeze physical capture bundles

The plan contains one row per policy replay, but the physical fixture must be
captured only once per shared `bundle_id`. Create a deduplicated bundle manifest
before capture. It assigns only independently verified payload IDs and fixes
the assignment seed, so targets cannot be selected after observing a difficult
cell.

```bash
python3 prf_tr_bundles.py \\
  --plan prf-tr-screening/episode-plan.tsv \\
  --registry prf-tr-screening/target-registry-verified.tsv \\
  --out prf-tr-screening/capture-bundles.tsv

python3 code/prf_tr/test_prf_tr_bundles.py
```

Each `capture-bundles.tsv` row is one physical two-slot capture unit. Its
`capture_slot_1_id` and `capture_slot_2_id` must be carried into every later
policy replay for that bundle; they are not independent action samples.

The default plan includes only actions executable with the confirmed NoIR path.
After a fixed IR illuminator has been installed and logged, explicitly opt in
to the two IR actions:

```bash
python3 prf_tr_plan.py \
  --out prf-tr-screening/episode-plan-with-ir.tsv \
  --sessions s01,s02,s03 \
  --cells clean_high_light,clean_low_light,cover_glare,held_out \
  --held-out-cell held_out \
  --actions visible_noir_only,noir_ir_only,fixed_visible_then_ir,scalar_gate,random_action,always_review \
  --attempts 20
```

## Validate capture provenance

Before frontier analysis, validate that collected rows still match the frozen
plan, use the planned bundle IDs, and refer only to independently verified
target IDs. The full episode schema already contains the required
attempt_id and payload_id fields; the short frontier TSV is not sufficient for
this check.

Use partial validation during collection. Add require-complete only after the
planned matrix has been collected.

```bash
python3 code/prf_tr/prf_tr_validate.py \
  --plan prf-tr-screening/episode-plan.tsv \
  --registry prf-tr-screening/target-registry-verified.tsv \
  --episodes prf-tr-screening/episode-details.tsv \
  --out prf-tr-screening/provenance-summary.tsv \
  --require-complete

python3 code/prf_tr/test_prf_tr_validate.py
```

## Summarize completed decision episodes

After a policy run, create one TSV row per completed decision episode with the
following columns:

```text
session_id, bundle_id, physical_cell, action, final_decision, action_sequence,
first_capture_id, second_capture_id, final_capture_id, target_verified, decoded_exact,
reacquisition_count, total_latency_ms, bytes_written, energy_mj
```

`target_verified` is the pre-capture independent check that the printed target
matches the registered payload; it must be `true` for every analyzed episode.
`decoded_exact` is whether this episode's edge decoder output matches that
registered payload. `final_decision` must be `retain`, `review`, or `unknown`.
A reacquisition is an intermediate action recorded in `action_sequence` and
`reacquisition_count`; it must resolve to one of the final decisions after the
second frame is revealed.
`final_capture_id` identifies the frame that produced `decoded_payload` and
`decoded_exact`. With no reacquisition it must equal `first_capture_id`; after
the single supported reacquisition it must equal `second_capture_id`.
`first_capture_id` is always required. A positive `reacquisition_count`
requires a non-empty `second_capture_id` different from the first capture.
`prf_tr_frontier.py` first summarizes within each session, then weights those
session summaries equally when computing false-retain, review, re-capture,
latency, byte, and optional energy metrics. It marks the non-dominated actions
in each physical cell. It rejects duplicated action/bundle rows and rejects a
comparison when policies in the same session/cell do not replay the same frozen
bundle IDs. It does not compute confidence intervals or choose a scalar cost
weight; that analysis remains session-blocked and preregistered.

```bash
python3 code/prf_tr/prf_tr_frontier.py \
  --episodes prf-tr-screening/decision-episodes.tsv \
  --out prf-tr-screening/frontier.tsv

python3 code/prf_tr/test_prf_tr_frontier.py
```
