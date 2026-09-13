# Round 22 Reconciliation: PRF-TR as the Conditional Direction

## Decision investigated

Whether a finite physical-versus-digital action-rank study can serve as the
one-year undergraduate FYP direction after the weak-network maintenance,
evidence-sufficiency, and emulator-transfer candidates were audited.

## Evidence checked

- [PRF-TR divergence packet](../ops/divergence/2026-09-03-contact-evidence-and-intermittency-divergence.md)
- [CONTACT-EVIDENCE/RF-EMUL-RANK validation audit](../ops/validation/2026-09-03-contact-evidence-rf-emul-rank-validation.md)
- [Offline maintenance-photo validation audit](../ops/validation/2026-09-03-offline-maintenance-photo-story-validation.md)
- [Historical cross-device transfer pilot](11-cross-device-action-rank-pilot.md)
- [Physical transfer execution gates](12-pilot-execution-gates.md)

## Reconciled result

`PRF-TR` is the only remaining **HOLD (Amber)** candidate. It is not a new
decoder, adaptive-sensing method, network protocol, or general robustness
claim.

The concrete story is deliberately modest: an engineer is preparing a
field-maintenance camera pipeline and must decide whether its digital fault
tests are sufficient to release a local capture policy. In the field, the
device must choose whether a non-personal printed inspection indicator can be
retained, reacquired once, or sent for local review before the worker leaves a
weak-network site. A false retain contaminates the local record; reacquisition
and review consume time and energy. The printed payload and expected value are
known before capture, so an independent exact-payload check can provide truth
for the **record-reading** task. It does not prove that a part was installed,
that a repair was completed, or that a person is authorised.

The research question is:

> Do digitally injected camera faults preserve the ordering of the three
> capture actions on the named Pi Camera NoIR v2 fixture, or can physical conditions
> reverse the action ordering at equal false-retain, latency, and energy cost?

The contribution, if the data support it, is a bounded empirical finding about
decision transfer from digital tests to physical edge conditions. The result
must be stated only for the declared Camera NoIR v2 path, marker family,
physical cells, and held-out sessions. It is not a claim about all cameras,
all factories, or synthetic corruptions in general.

## Exact object

- **Actor:** a maintenance-record operator or local edge logger.
- **Decision:** `retain`, `reacquire`, or `unknown/review`.
- **Physical truth:** exact equality between the pre-generated payload and an
  independent decoder/oracle result.
- **Physical cells:** clean, low visible light, transparent cover/glare, and at
  least one held-out lamp, cover lot, or remount. A second camera path is
  optional future instrumentation, not a current requirement.
- **Digital cells:** only predeclared brightness, blur, noise, masking, and
  frame-loss transformations applied to clean captures.
- **Primary endpoint:** whether the best action on digital cells predicts the
  best action on held-out physical cells under a fixed preregistered loss.
- **Secondary endpoints:** false retain, exact-code success, unknown rate,
  reacquisition count, latency, bytes, and joules.

## What is actually innovative

The innovation is conditional and empirical, not algorithmic:

1. The decision endpoint is action loss, not image accuracy alone.
2. Digital and physical conditions are compared through the ordering of the
   same actions, with capture cost charged to every policy.
3. Physical condition labels and payload truth are assigned independently of
   the policy and blocked by session/cell before threshold tuning.
4. A rank-preservation, rank-inversion, or two-world non-identifiability result
   is accepted as the scientific outcome.

This is enough for a defensible undergraduate empirical study only if a
repeatable held-out inversion survives the strongest fixed baselines. It is not
enough for a method paper if the two-shot or scalar-quality policy dominates.

## Mandatory baselines and kill criteria

Compare fixed RGB, fixed NoIR+IR, fixed RGB-then-NoIR+IR two-shot,
brightness/blur/IR-ratio thresholding, random action, and always-review. Use a
single decoder and charge latency/energy/bytes consistently.

Kill the positive thesis claim if any of the following holds:

- fixed two-shot or always-review is Pareto-optimal;
- a scalar brightness/blur/decoder rule matches the proposed policy;
- physical labels or the exact-payload oracle are not independent;
- source-cell tuning does not reproduce on held-out sessions/cells;
- automatic exposure, illumination state, or unlogged optional-camera changes
  confound the result; or
- the pilot cannot produce a nontrivial digital fault family and a repeatable
  physical comparison.

If killed, keep the measured result as a bounded negative benchmark: state
whether the declared digital tests preserved or failed to preserve action
rankings on the purchased setup, and identify the tested boundary. Do not
replace a null with a larger model search.

## Feasibility gate

The current user-confirmed Pi and Camera NoIR v2, printed targets, rigid
fixture, and local capture script are sufficient for the single-camera first
gate. Visible light is required; an IR illuminator is optional for a declared
second observation. The first work is bring-up, independent payload
verification, exposure/WB and illumination logging, power measurement if
joules are primary, then the fixed baseline matrix. No additional camera,
model, network protocol, or biometric data is needed.

The weak-network setting is contextual unless contact outage or upload delay is
explicitly measured. It must not be used as evidence for a networking
contribution.

## Status

**HOLD (Amber).** This is the current conditional direction for the FYP
discussion and pilot. It becomes a thesis lock only after the physical gate
produces either a repeatable held-out action-rank inversion or a deliberately
framed, sufficiently rich negative result approved as the paper identity.
