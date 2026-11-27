# Palm station interaction prototype plan

## Objective
Make the first-time participant experience understandable without spoken coaching. Deliver a local, synthetic prototype for review before integrating with the station.

## Scope for this review
- Verification with explicit waiting, positioning, processing, result and hand-removal states.
- Hold each result until hand removal. Clear stale feedback on stop, navigation and simulated camera failure.
- Enrollment with a 5-second preview, at least 60 seconds of active capture, ten candidate groups, review, removal, replacement and explicit confirmation. Five selected groups represent the first enrollment template.
- Participant view prioritizes the camera and one instruction. Presenter controls simulate inputs and failures.
- Synthetic imagery, fictional identities and in-memory records only. Reload clears the demonstration.

## Visual design
Use an off-white workspace, navy camera panel, teal action color and amber retry state. Instrument Sans is the intended type family with a system fallback for offline use. Large camera framing is the signature element. Status includes text and an icon, visible keyboard focus and a polite live region. Respect reduced motion and small screens.

## Implementation sequence
1. Establish an isolated worktree and write this plan.
2. Test the state transitions for result locking, removal, errors, active capture timing and confirmation.
3. Build a dependency-free browser prototype under code/interaction-demo.
4. Verify the state tests, syntax and browser behavior, including narrow layout and keyboard operation.
5. Submit the prototype for user approval. Integration remains pending that approval.

## Review scenarios
- Start verification, place a hand, get a simulated match, keep the result stable, remove the hand and repeat.
- Simulate an unknown hand, poor positioning and an unavailable camera. Each state supplies a recoverable action.
- Start enrollment, pause and resume without counting paused time, complete capture, review ten groups, replace one and confirm.
- Stop or switch views during a pending result. No old response appears in the new session.
- Use keyboard controls and a narrow viewport without clipped actions.

## After approval
Map real camera and model events to the approved interaction states. Use actual image pairing and existing archive/template APIs. Calibrate any temporal aggregation and match threshold independently. Preserve the existing capture minimum unless a later experiment changes it explicitly. Run synthetic station regression checks and then fresh Pi 5 validation. Review neither changes a model nor establishes accuracy, latency or an acceptance threshold.

## Run and verify
From this directory, run `node --test state.test.mjs`. For local preview run `python -m http.server 8096 --bind 127.0.0.1`, then open http://127.0.0.1:8096. No dependencies, camera permission, checkpoints or datasets are required. All sample results and images are synthetic. The presenter can enable 6x rehearsal speed; the banner labels accelerated time.

## Prototype review status
Implemented the synthetic browser prototype and four state tests. Browser checks exercised matched and unrecognized presentations, removal reset, camera failure/retry, accelerated enrollment, ten-group review, three image views, removal/replacement, confirmation and narrow-screen layout. The browser runtime exposed a 480 CSS-pixel minimum during responsive testing; smaller widths have not been visually verified. The replacement button restores generated candidates immediately for rehearsal. Approval is pending before connecting real capture, selection or model APIs.
