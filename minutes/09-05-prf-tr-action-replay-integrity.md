# PRF-TR Action-Consistent Replay Rule

## Decision investigated

Whether physical and digital evaluations give `reacquire` the same information
and cost semantics.

## Problem

[KILL if uncorrected] Re-running a decoder or a digital transformation on one
image is not a second capture. It gives an apparent `reacquire` action no new
observation, no capture variability, and potentially no real capture cost. A
physical recapture is a new frame. Comparing those two objects would make an
action-frontier conclusion uninterpretable.

## Required capture bundle

For every `session_id x physical_cell x bundle_id`, collect two ordered static
captures before policy scoring:

1. `capture_slot_1`: the policy-visible initial frame;
2. `capture_slot_2`: a separately captured candidate recapture frame.

Both slots use the same locked camera configuration and declared fixture state.
Record their frame IDs/hashes, timestamps, exposure/gain/WB state, and the
capture/decode/byte/energy ledger. `capture_slot_2` must remain hidden from a
policy until that policy chooses `reacquire`.

A static fixture makes this an **offline counterfactual replay**, not evidence
that online recapture changes the scene. That limitation must be stated in the
paper. It is acceptable only because the research claim is about the finite
capture-policy evaluation under declared static optical cells.

## Digital counterpart

Digital fault evaluation starts from clean capture bundles, not a single clean
image. Apply the predeclared transformation separately to slot 1 and slot 2,
with a logged transformation seed/parameters for each slot. A policy that
reacquires consumes transformed slot 2. It must not receive a second decode of
transformed slot 1.

## Action semantics

| Action | Information revealed | Charged cost |
| --- | --- | --- |
| `visible_noir_only` | slot 1 only | slot-1 capture/decode/bytes/energy |
| `scalar_gate` without reacquire | slot 1 only | slot-1 cost |
| `scalar_gate` with reacquire | slot 1, then slot 2 | both slots plus decision cost |
| fixed two-shot, if optional IR is installed | slot 1 and slot 2 | both slots |
| `always_review` | slot 1 plus declared review outcome | slot 1 plus fixed review cost |

Unused slot-2 cost is not charged to a policy, even though all bundles are
precollected for offline evaluation. The data record must retain the raw
slot-level cost so counterfactual accounting can be recomputed.

## Analysis invariants

- Every completed decision episode references one non-empty `bundle_id`.
- An episode records `action_sequence`, `first_capture_id`, and, when used,
  `second_capture_id`.
- A `reacquisition_count > 0` requires a distinct `second_capture_id`.
- `final_capture_id` identifies which slot produced the episode's terminal
  decoder output: slot 1 with no reacquisition, slot 2 after reacquisition.
- `reacquire` is never a terminal outcome. After slot 2 is revealed, the
  episode must end as `retain`, `review`, or `unknown`; otherwise a frontier
  could incorrectly treat an unresolved item as neither false-retain nor
  review.
- The same bundle may be replayed by multiple frozen baselines, but it is one
  paired experimental unit rather than multiple independent physical scenes.
- Bootstrap/resampling remains over sessions/remounts, never over slot-level
  frames.

## Kill condition

If the fixture cannot produce repeatable paired captures under a fixed state,
or if slot 2 leaks into a policy before the policy selects it, do not report a
physical-versus-digital action comparison. Report an apparatus failure or
restrict the study to one-capture `retain / review` actions.

## Decision

**REQUIRED for PRF-TR promotion.** This prevents the `reacquire` comparison
from silently becoming an image reprocessing benchmark.

## Schema reconciliation needed [GAP]

The executable frontier TSV now requires `final_capture_id` and supports at
most one reacquisition because the frozen bundle has two slots. The active
data-schema document predates this clarification. It must be reconciled by the
coordinator only after the required role outputs are available; do not collect
episodes against the older abbreviated field list.
