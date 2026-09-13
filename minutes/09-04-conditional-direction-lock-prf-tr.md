# Conditional Direction Lock: Weather-Resilient Edge Record Admission

**Date:** 2026-09-04  
**Status:** `PIVOT (Amber)` -- this is the conditional FYP direction for the first physical gate, not a thesis-lock or a novelty claim.

## Direction in plain language

An asset-maintenance technician at a humid/rain-prone site uses an edge camera
to read a **non-personal printed asset/inspection indicator** before a local
record is released. After the first capture, the node must choose exactly one
action:

1. `retain`: create the local record;
2. `reacquire`: take one declared additional RGB or NoIR+IR capture;
3. `unknown/review`: do not create a machine-released record; request a fixed
   human check.

The local/Macao facilities story is motivation only. The experiment does not
claim that any named employer uses this device, that a repair was completed,
or that the tag proves physical asset state.

## Why the decision matters

- **False retain:** the local maintenance/inspection record receives an
  incorrect payload. This causes later rework or incorrect record association.
- **Unnecessary reacquire:** consumes a second capture, latency, storage and
  measured energy.
- **Unnecessary review:** consumes a declared human-review slot/time cost.

The problem is not QR detection accuracy. It is whether cheap *digital* image
fault tests tell an engineer the correct action under *physical* low light,
glare, transparent-cover and optical-path conditions.

## What is independently observed

The deployable policy may use only the capture(s), declared metadata and
frozen image statistics/decoder score. It cannot see:

- `expected_payload`: generated before all capture;
- `oracle_payload`: a separate phone/flatbed or independently configured
  decoder result;
- `payload_exact`: whether the output equals the pre-generated payload;
- `physical_cell`: fixture condition assigned before capture;
- source/held-out session allocation.

This separation is the project’s credibility requirement. `unknown/review` is
an action, never a truth label.

## Actual research question

> For one fixed Pi RGB/NoIR capture setup and declared physical cells, do
> digital brightness/blur/noise/mask/frame-loss tests preserve the
> risk-cost ranking of `retain`, `reacquire` and `unknown/review` actions on
> held-out physical sessions?

## Minimum contribution if it survives

- A finite, reproducible physical-versus-digital action-risk dataset and
  protocol.
- Matched action semantics and actual capture/decode/time/energy accounting.
- A held-out result of one of three honest forms: rank preservation, rank
  inversion, or non-identifiability.

It is **not** a detector, a new RGB/NoIR fusion method, a camera-health
certificate, a synthetic-to-real theorem, a network contribution, or a
maintenance-completion system.

## First experiment and weekly capacity

### Screening week

Run three deployable controls (`rgb_only`, `noir_ir_only`,
`fixed_two_shot`) across four physical cells with one session and ten attempts
per cell/action: `1 x 4 x 3 x 10 = 120` captures. This is a fixture and
instrumentation gate, not a result.

### Confirmation weeks

After the screening gate, use four deployable controls (add `scalar_gate`) at
three sessions, four physical cells and twenty attempts per cell/action:
`3 x 4 x 4 x 20 = 960` captures. Collect this across two or three weeks so a
session/remount remains a real independent unit. The full six-action research
matrix would be `3 x 4 x 6 x 20 = 1,440` captures and should not be attempted
until the smaller matrix passes its instrumentation check.

### Required cells

1. clean/high visible light;
2. clean/low visible light;
3. transparent cover/glare;
4. one frozen held-out lamp, cover lot, remount or optical-path condition.

## Non-negotiable baselines

- fixed RGB;
- fixed NoIR+IR;
- fixed RGB then NoIR+IR two-shot;
- scalar brightness/blur/decoder-confidence gate;
- always review;
- physical-cell oracle for evaluation only.

## Existing Pi script boundary

`code/palm_demo/tools/camera_capability_preflight.sh` is useful only for the
RAW/JPEG **capability preflight**. It records installed `rpicam` tooling,
camera-list output, trial files and elapsed capture time. It does **not**
record the RGB/NoIR physical mapping, pre-generated payload registry, physical
cell label, decoder result, action sequence, review outcome, source/held-out
allocation, or a per-episode cost ledger. It cannot therefore be used as
PRF-TR research data.

When the Pi is reachable, first run that script to prove camera availability.
Only after manually logging camera mapping and adding a separate PRF capture
manifest may any episode enter the screening matrix. A failed hostname check
on 2026-09-04 means this physical feasibility gate is still unverified.

## Continue / kill decision

**Continue toward a finite empirical paper only if** a predeclared digital
action ranking reverses on held-out physical sessions, repeats across at least
three sessions/remounts, and remains better than fixed two-shot, scalar quality
and always-review after costs are included.

**Stop the positive claim immediately if** fixed two-shot, a scalar gate or
always-review is Pareto-optimal; truth/physical labels are not independent;
costs cannot be measured; or the effect vanishes under blocked session/remount
analysis. Preserve the result as a finite negative evaluation only if its
scope stays explicit.

## Why this is now the working direction

The additional Macao application search eliminated drainage, trap-empty,
cleaning-record and heritage-dampness stories as primary technical directions:
they are ordinary detectors, hybrid-sensing systems or weak-proxy studies.
By contrast, this direction has a distinct decision endpoint, exact
independent truth, no personal data, a Pi/NoIR-compatible first fixture, and a
useful null path. Its remaining weakness is paper identity: it needs advisor
approval as a bounded evaluation/negative-result FYP before any claim of
research novelty.
