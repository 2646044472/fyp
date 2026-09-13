# PRF-TR Research Prospectus

## Working title

**When Digital Camera Fault Tests Mislead Edge Inspection Decisions: A
Physical-versus-Digital Action-Frontier Study on Raspberry Pi Camera NoIR v2**

Chinese working title:

**数字摄像头故障测试能否指导边缘现场检查决策：基于树莓派 Camera NoIR v2
采集的物理与数字故障动作前沿研究**

## One-sentence problem

An engineer preparing a field-maintenance camera pipeline needs to know whether
cheap digital fault tests are sufficient to choose among `retain`, `reacquire`,
and `unknown/review` when the deployed edge camera encounters physical optical
conditions that cannot be reproduced exactly in software.

## Real story and boundary

The motivating operator is a release/maintenance engineer, not a hypothetical
security authority. A field device reads a non-personal printed inspection
indicator before the worker leaves a weak-network site. A false retained code
contaminates the local record; a reacquisition or review consumes time, energy,
and operator attention. The weak network explains why the first decision is
local, but no networking contribution is claimed unless network variables are
measured separately.

The experiment verifies only whether the printed payload was read correctly. It
does not prove that a part was installed, that a repair was completed, that a
worker is authorised, or that an employment/legal status is valid. No face,
palm, payment, production control, or safety actuation is part of this project.

### Reality check for the story

This is not an invented use of a camera in a maintenance workflow. Official
field-service documentation describes the surrounding operations: SAP Asset
Manager scans barcodes to navigate to technical objects, maintenance requests,
and orders; SAP's offline workflow supports local work orders and serialized
parts; Salesforce documents offline-first field work; and ServiceNow documents
offline task execution, asset lookup by barcode, and later synchronization.
These sources support the existence of the workflow, not the proposed research
claim. They do not show that digital fault rankings are sufficient for the
physical `retain / reacquire / review` decision, which remains the empirical
question in this project.

Sources checked on 2026-09-03:

- [SAP scanning function](https://help.sap.com/docs/SAP_MAINTENANCE_ASSISTANT/ed7f0ed509a34d69b614ac3e5fe20cba/d5832374a577457886ca148d24c88818.html?locale=en-US), SAP Maintenance Assistant User Guide, version 2508.
- [SAP Asset Manager 1911 features](https://help.sap.com/doc/85db4f0cef7744fc81ff3c3d82c3a24a/1911/en-US/SAMApplication_1911.pdf), sections on offline local work orders and serialized PRT equipment.
- [Salesforce Field Service Mobile App](https://help.salesforce.com/s/articleView?id=service.mfs_overview.htm&language=en_US&type=5), offline-first field work and offline capability.
- [ServiceNow offline mobile experience](https://www.servicenow.com/docs/r/xanadu/field-service-management/mobile-experience-fsm.html), offline task execution, asset handling, and synchronization.

The project therefore uses a real workflow as motivation while keeping the
measured endpoint deliberately narrower: record-reading correctness, not proof
of work completion or asset identity beyond the predeclared code.

## Research question

> On a fixed Raspberry Pi Camera NoIR v2 setup, do digital brightness, blur, noise,
> masking, and frame-loss tests preserve the false-retain versus
> review/reacquisition/cost frontier of `retain`, `reacquire`, and
> `unknown/review` under held-out physical low-light, glare,
> transparent-cover, and optical-path conditions?

### Subquestions

1. Do digital and physical cells preserve the same non-dominated action set
   before any arbitrary scalar loss is chosen?
2. Does a source-cell policy transfer to a held-out lamp, cover lot, remount,
   or camera-path condition?
3. Can a physical condition be indistinguishable from another condition using
   only the pre-action observations available to the edge policy?
4. Does any apparent benefit survive fixed two-shot, scalar-quality, and
   always-review controls after real capture cost is charged?

## Claim and non-claim

### Allowed claim

For the named marker family, purchased camera path, declared physical cells,
and blocked sessions, report whether the digital test family preserves,
changes, or fails to identify the non-dominated action frontier. A repeatable
held-out frontier failure, including a digital-selected action that is
physically dominated by a fixed control, is a bounded empirical result.
Frontier preservation or non-identifiability is an equally valid negative
result.

### Prohibited claims

- no new decoder or image-enhancement method;
- no generic adaptive-camera or conformal-abstention method;
- no camera-family or factory-wide transfer guarantee;
- no universal statement that synthetic corruptions are valid or invalid;
- no camera-health certificate or maintenance-completion proof;
- no security, biometric, payment, immigration, or safety claim;
- no claim that Raspberry Pi deployment itself is novel.

## What may count as the contribution

The contribution is conditional and empirical:

1. A decision endpoint based on a false-retain/cost Pareto frontier rather
   than image accuracy alone or one arbitrary scalar loss.
2. A paired physical/digital evaluation in which the same actions and actual
   capture/decode costs are compared.
   Each action is replayed from a hidden two-frame capture bundle, so a
   declared reacquisition reveals a separately captured second frame rather
   than reprocessing the first one.
3. Independent physical-cell labels and an exact predeclared payload oracle,
   with source/held-out blocking before policy fitting.
4. A reproducible boundary result showing frontier preservation, frontier
   failure, or non-identifiability for a specified edge optical path.

This contribution is sufficient for an undergraduate evaluation or negative-
result FYP only if the advisor approves that paper identity. It is not a
method-paper contribution without an additional result that is not currently
known.

## Formal objects

- `c`: preassigned physical cell/session;
- `x`: complete episode capture;
- `z`: pre-action observations available to the policy;
- `a`: one allowed action;
- `q(x,a)`: whether the action's decoded payload equals the pre-registered
  payload, after the printed target has independently passed reference
  verification;
- `pi(z)`: deployable policy without access to physical-cell labels or oracle;
- `R_c(a)`: observed outcome vector containing false-retain, unknown/review,
  extra capture count, latency, bytes, and measured energy where available.

The primary result is the Pareto frontier of `R_c(a)`. An action is dominated
when a comparator is no worse on every declared component and better on at
least one. This avoids treating an invented review-to-joule exchange rate as a
physical discovery. A small, preregistered family of scalarizations is
secondary: it must be fixed before the held-out cell, reported as scenario
analysis, and never selected after looking at physical results. The oracle
frontier/action is an evaluation upper control, not a deployable input.

## Minimum experiment

### Physical setup

- Raspberry Pi and Camera NoIR v2;
- controlled visible illumination with the IR source off;
- optional fixed IR illuminator only for the declared IR-on action;
- rigid camera/target mount;
- non-personal printed QR/AprilTag marker family;
- stable lamp/diffuser;
- transparent cover/film and opaque-cover fixtures;
- optional inline USB power meter if energy is a primary endpoint.

### Physical cells

1. clean/high visible light;
2. clean/low visible light;
3. transparent-cover/glare;
4. one held-out lamp, cover lot, remount, or optical-path cell.

The cell is assigned by the fixture log before capture. A decoder score,
brightness value, lux value, or image-quality metric is not a physical label.

### Actions and baselines

- fixed visible-light capture on the NoIR camera with IR off;
- fixed NoIR capture with declared IR illumination, if that optional path is
  included;
- fixed visible-light capture followed by the declared IR-on capture, if the
  optional IR path is included;
- scalar brightness/blur/decoder-confidence gate followed by one fixed second
  capture;
- fixed random action;
- always-review procedure;
- cell-label oracle for evaluation only.

The first experiment uses one frozen decoder and no architecture search. Every
action is charged for its actual capture, decode, latency, storage, and energy
where measured.

Each static bundle contains an initial and candidate-recapture frame captured
before policy scoring. This makes the experiment offline counterfactual replay
rather than a claim that a live recapture changes the scene. The second frame
is hidden until a frozen policy selects `reacquire`; digital transformations
must be applied separately to both frames.

### Data and analysis

Use at least three independent sessions per cell and 20 attempts per action per
session as a feasibility minimum. The primary unit is a session-by-cell-action,
not an individual frame. Freeze source/held-out groups before threshold fitting.
Report false-retain, exact-code success, unknown/review rate, reacquisition
count, latency, bytes, joules, frontier membership, and scenario-specific
action agreement with bootstrap intervals over sessions/remounts.

## Falsification and decision gates

### Bring-up gate

The confirmed Camera NoIR v2 path must produce repeatable static captures; the
independent payload oracle must agree on clean controls; exposure, white
balance, timing, and illumination state must be logged. No second camera is a
prerequisite.

### Identification gate

The physical cell log and payload registry must be independent of the policy.
At least one matched-observation low-light/glare pair must be attempted. If the
permitted observations overlap while the best actions differ, report
non-identifiability rather than fitting a larger selector.

### Research gate

Promote the positive empirical claim only if a held-out frontier failure:

- repeats across at least three sessions;
- survives remount or another blocked physical cell;
- remains after fixed two-shot, scalar-quality, and always-review comparison;
- is not explained by timing, auto-exposure, label leakage, or free digital
  transformation cost; and
- is visible in the primary Pareto analysis and remains under a preregistered,
  nontrivial family of false-retain/review/capture-cost scenarios.

### Kill/pivot gate

Kill the positive mechanism claim if fixed two-shot, scalar quality, or
always-review is Pareto-optimal; if labels/oracle are not independent; if costs
cannot be measured; or if the effect disappears under blocking. Preserve the
finite result as a negative evaluation if it shows rank preservation or a
well-defined non-identifiability boundary. Do not answer a null by adding a
larger model or more arbitrary digital corruptions.

## Literature and novelty position

The load-bearing audit is recorded in:

- [finite action-rank validation](../ops/validation/2026-09-03-finite-action-rank-study-validation.md);
- [three deployment stories](../ops/divergence/2026-09-03-prf-tr-three-stories-divergence.md);
- [Round 23 final validation](31-round-23-prf-tr-final-validation.md).

The inspected direct neighbors occupy the broad mechanisms: adaptive camera
control, adaptive exposure, budgeted acquire/abstain, active diagnosis,
fiducial decoding under difficult light, and broad synthetic-versus-real
robustness evaluation. Therefore the project must claim only the finite
physical-cell/action-risk endpoint, not a new mechanism. Lack of an exact
published Pi tuple is recorded as a search boundary, not proof of novelty.

## Data, compute, ethics, and supervision

### Data

Generate non-personal marker payloads before capture and keep the registry
separate from policy logs. Store capture manifests, physical-cell labels,
exposure controls, timing, hashes, and post-action oracle results. No personal
dataset is required.

### Compute

The first gate uses deterministic image statistics and an existing marker
decoder. A Pi 5B is sufficient for capture and runtime measurements; a laptop
is sufficient for bootstrap analysis. No GPU training is required.

### Ethics and safety

Use only inert printed targets and low-voltage/non-actuated fixtures. Confirm
IR illuminator specifications and avoid eye exposure. Do not use palm/face
data, worker-status inference, payment decisions, production equipment, or
safety interlocks.

### Advisor decisions needed

The supervisor should approve one of two paper identities before scored data:

1. a finite physical-versus-digital action-frontier evaluation; or
2. a deliberately framed negative-result/non-identifiability study.

The supervisor should also approve the frontier components, a small scenario
family for the secondary scalar analysis, whether measured energy is mandatory,
and whether the constructed maintenance story is acceptable as a bench proxy.
A real repeated maintainer/release workflow would strengthen the story but is
not currently documented.

## Schedule

- **September 2026:** connect Pi, verify camera mapping, prepare marker registry,
  mount, and run clean controls.
- **October 2026:** collect clean/low-light/cover cells; log exposure, timing,
  and costs; freeze the source/held-out split.
- **November 2026:** run held-out lamp/cover/remount sessions and bootstrap
  action-risk rankings.
- **December 2026:** deliver the static demo and lock the paper identity based
  on the research gate.
- **January-June 2027:** expand repetitions and cells only if the core result
  survives; otherwise write the bounded null and stop model expansion.

## Current status

**PIVOT (Amber), feasible but not empirically verified.** The current user-
confirmed core inventory is a Raspberry Pi and Camera NoIR v2. Any extra
camera and an IR illuminator are optional and remain [GAP] until physically
verified or purchased. The workspace has a complete protocol, schema,
literature audit, and kill path, but no physical PRF-TR data, acquisition log,
or power log. The next authoritative milestone is the single-camera bring-up
gate, not another literature round.
