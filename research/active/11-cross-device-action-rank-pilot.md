# Cross-device action-rank pilot (pre-registration draft)

## Decision under test

A lab maintainer scans a non-personal printed marker after an RGB or NoIR camera path is installed. The edge node chooses `retain`, `reacquire`, or `unknown`. A false retain corrupts the local maintenance record; an unnecessary reacquisition costs capture time and energy.

## Narrow claim

Within the purchased RGB/NoIR pair and declared lamp/material cells, a policy calibrated on a source cell preserves or fails to preserve the ordering of three capture actions on held-out cells. This is a finite boundary result, not a camera-family transfer guarantee.

## Formal decision object

Let `c` be the independently assigned physical cell, `z` the pre-action observable prefix, `a` an allowed capture action, and `L(c,a)` the preregistered false-retain/unknown/energy loss. The best action with access to the cell label is `a*(c) = argmin_a L(c,a)`, while any edge policy without that label is `pi(z)`. The pilot estimates whether `argmin_a E[L(c,a) | z]` agrees with `a*(c)` on the finite cell family. A minimal boundary exists when two cells `c1 != c2` have overlapping (or deliberately matched) `z` but different `a*(c)`; then no policy of `z` alone can be correct for both. This is a target-functional identification test, not a claim that the latent cell itself can be recovered.

## Setup

- Static QR or AprilTag payloads printed in at least two material lots; verify payload independently with a flatbed or phone oracle.
- Rigid fixture with fixed distance/angle. Physical cells are assigned before capture: clean, transparent film, opaque cover, low visible light, IR illuminator on/off. Do not infer these labels from the Pi image.
- Record camera path, lamp identity, lux (if available), manual or logged exposure/white balance, frame timestamp, latency, and inline USB energy.
- Treat sequential RGB/NoIR inter-capture delay as a measured blocking factor: log the trigger-to-frame interval for every action and include a moving-target or LED timing control only to quantify temporal confounding. Do not claim synchronization or registration as the contribution.
- Block one camera/lamp/material combination as held-out before any threshold tuning. Repeat each cell across at least three sessions.

## Actions and controls

1. RGB-only capture.
2. NoIR + IR capture.
3. Fixed RGB-then-NoIR+IR two-shot.
4. Scalar brightness/blur/IR-ratio threshold.
5. Random action and an oracle that sees the independent cell label.

All actions use the same decoder and return exact-code success, `unknown`, or false retain. The two-shot baseline is allowed its extra capture cost and is the primary adversarial control.

## Analysis

- Compute per-cell false-retain, exact-code success, unknown rate, latency and joules.
- Report Kendall tau/Spearman ordering of action risks between source and held-out cells, with bootstrap intervals over sessions.
- Define the cell-level loss for action `a` as `L_c(a) = 10 * FR_c(a) + 1 * U_c(a) + 0.1 * J_c(a)`, where `FR` is false-retain rate, `U` is unknown rate, and `J` is joules normalized to the RGB-only median. The coefficients encode the declared story (false retain is ten times an unknown) and a modest energy penalty; they are fixed before seeing held-out outcomes. Report a sensitivity sweep, but do not retune the primary decision after observing results.
- The source policy chooses `argmin_a L_source(a)` using only source cells. A held-out rank inversion is counted only when the held-out minimizer differs from the source minimizer and the bootstrap 95% interval for the loss difference excludes zero in at least three repeated sessions.
- A positive mechanism-level observation is a preregistered, repeatable held-out action-rank inversion where the source policy selects a cheaper action but the fixed two-shot/scalar controls do not remove the risk-cost advantage. If no inversion occurs, report rank preservation and its interval as the result.
- A null or rank preservation result is still valid: it bounds the purchased pair and documents whether digital or source-cell tuning transports. Do not call it proof of general transfer.

## Statistical unit and minimum sample

The experimental unit is a session-by-cell pair, not an individual frame. Use at least three independent sessions per blocked cell, with 20 or more marker captures per action per session; bootstrap over sessions and report the full per-cell table. This is a feasibility minimum for a finite audit, not a population-power claim. If the decoder fails on the independent oracle or the session count cannot be reached, the gate is unresolved rather than positive.

## Identification and kill tests

- Construct a minimal two-world counterexample before fitting a policy. Let the observable prefix be `z = (RGB preview, camera path, lamp ID, exposure/WB metadata, and optional photopic lux)`. World `D` is low visible light with a clean optical path, so `NoIR+IR` can reduce false-retain risk; world `F` has a transparent cover/film that leaves the RGB preview and photopic lux matched but attenuates or scatters the IR path, so the same action can remain unsafe and a physical clean/reacquire action is preferred. The hidden state is assigned by the fixture, never inferred from `z`. If the measured `z` distributions overlap while the empirically best actions differ, no policy using only `z` can certify the action; report the overlap and the two-world non-identifiability rather than fitting a more complex router. Equal-lux matching is optional and must be described as a stress test, since CIE lux is photopic and is not an NIR witness.
- Kill the thesis if fixed two-shot, always-reacquire, or scalar quality matches the held-out risk-cost frontier; if camera swap is inseparable from IR-cut modality; or if physical labels/oracle are not independent.
- Do not add a lux sensor, second camera, or larger model before this gate passes.

## Feasibility and ethics

The existing Pi 5B, RGB camera, NoIR camera, IR illuminator and adapters are sufficient. Additional purchases are limited to a rigid mount, transparent-cover/fixture kit, safe light source, optional lux meter and USB power meter. The study uses non-personal printed targets and has no production or safety actuation.
