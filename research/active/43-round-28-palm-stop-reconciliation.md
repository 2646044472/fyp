# Round-28 PALM-STOP Reconciliation (2026-09-24)

## Decision

`PALM-STOP` is **KILL as a new stopping algorithm**. Palm quality/frame curation and generic video early-exit/frame-selection mechanisms occupy the proposed components. Retain only `PALM-STOP-NULL`: a finite Palm-specific risk-latency-energy boundary audit for online stopping versus fixed-frame and fixed-recapture controls.

## Exact surviving question

Given a live VIS Palm stream, can a calibration-frozen online rule decide `accept(id)`, `unknown`, or `continue/recapture` using only observations available at time `t`, while preserving a predeclared false-accept/unknown ceiling and reducing capture-to-decision time or energy relative to fixed-N frames and fixed recapture?

This is not a new temporal model, quality estimator or sequential decision framework. It is useful only if the Palm full-path experiment exposes a reproducible risk-latency-energy boundary or proves that safe stopping is not identifiable from current observations.

## Required controls and validity conditions

- fixed-N frame policies;
- best-frame oracle reported only as an upper bound, never as a causal baseline;
- fixed recapture and always-continue;
- scalar quality and score/margin-only controls;
- person-held-out and session-held-out episodes;
- independently authorized unknown/mate-absent labels where permitted;
- no future frames, final identity, post-action result or test-set confidence in the stopping rule;
- all-start denominators, action authorization, idempotency, latency and charged capture/compute energy.

## Project ordering

1. Freeze the VIS Palm Payment executable and collect the all-start trace.
2. Confirm that a complete time-ordered frame sequence can be recorded per eligible episode, with consent, independent unknown labels and a reproducible capture-cost account. The current payment checkout consumes one latest frame and does not retain a sequence; its live preview is not a stopping-policy dataset.
3. Only after that capability gate, consider `PALM-STOP-NULL` alongside `E-BOUND-X` (if three disjoint visits and consent are feasible); neither is preselected as the thesis.
4. Reopen `VIS-GUIDE` only after the fixed path is stable.
5. Gate `NIR-MISS-X` and `PA-FULLPATH` behind hardware, ethics and full-path capability checks.

## 2026-09-24 Implementation correction

[E] `code/palm_demo/camera.py` keeps only `latest` and its frame ID; `code/palm_demo/workflow.py` invokes `capture()` once per checkout. No time-ordered frames, per-frame matcher outcomes or replayable tracklets are persisted by this path. The earlier characterization of `PALM-STOP-NULL` as the lowest-cost first research audit was a conjecture, not demonstrated feasibility. Treat it as a capability-gated hypothesis, not the default next experiment.

## Kill conditions

Close the positive stopping claim if fixed-N, fixed recapture or always-continue matches the frontier; if future-frame leakage is present; if unknown/action labels are unavailable; if the current observation is not sufficient to certify safe stopping; or if the result is only ordinary quality/frame selection.

## Evidence boundary

The direct audit is `research/ops/validation/2026-09-24-palm-stop-validation.md`. It records Palm video/frame-selection neighbors, generic early-exit collisions, leakage checks, controls, feasibility and the required negative-result path. No exact-paper absence is treated as novelty evidence.

## Decision

PIVOT
