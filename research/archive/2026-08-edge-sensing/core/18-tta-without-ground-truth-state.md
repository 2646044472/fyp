# Unlabeled TTA Trigger, Accept, and Rollback: Research State

Last updated: 2026-08-27. Status: Gate 5 novelty review - Amber / pivot required.

## Project Charter

- **research_goal:** Find a defensible FYP research direction in edge reliability, not a generic TTA deployment demo.
- **field_scope:** Online/continual test-time adaptation for compact vision models operating on an unlabeled stream; decision actions are `hold source`, `adapt`, `accept candidate`, `rollback`, and `abstain/escalate`.
- **explicit exclusions:** Offline domain adaptation, source-label retraining, cloud-only MLOps, and methods whose only difference is a new corruption dataset.
- **available resources:** Existing FYP notes emphasize Pi-class edge measurement and low-cost vision sensing. Exact board, camera, time, and advisor constraints remain unverified.
- **target identity:** An empirical reliability/protocol contribution. No publication tier is promised.

## Central Research Question

> Given only an unlabeled target stream and local model telemetry, can a resource-limited vision device distinguish `adaptation likely helps`, `adaptation likely harms`, and `not identifiable`, then make trigger/accept/rollback decisions that reduce offline-measured harmful updates at a fixed energy and abstention budget?

## Formal Objects

- **[D]** Source model: `f_0`; candidate adapted model at time `t`: `f_t`; unlabeled recent stream: `U_t = {x_{t-w+1}, ..., x_t}`.
- **[D]** Online information set: `I_t` consists only of `U_t`, model predictions/logits/features, adaptation loss/gradients, hardware telemetry, and past accepted checkpoints. It excludes target labels and future data.
- **[D]** Offline evaluator: latent task loss `R_t(f)` is measured only after the run with held-out labels; it is never available to the policy.
- **[D]** Actions: `hold`, `adapt`, `accept`, `rollback`, `abstain`.
- **[T]** Empirical target: relative to always-adapt, never-adapt, shift-trigger-only, and fixed-period reset baselines, reduce the rate of accepted harmful updates `1[R_t(f_t) - R_t(f_ref) > delta]` while reporting task risk, coverage, recovery delay, energy, and memory.

## Why This May Be Important

Existing TTA commonly relies on unsupervised proxy losses or shift scores. A score can show that the input distribution changed, yet it cannot by itself show whether updating improves the actual task. This gap matters when erroneous self-training accumulates and the device has no labels to validate a new checkpoint.

## What Is Known `[K]`

- Recent work already includes lightweight unlabeled shift detection to trigger edge TTA (OD-TTA), uncertainty/sample filtering (EATA/PALM), and reset/restoration mechanisms in continual TTA. These are baseline families, not presumed gaps.
- The existing project already rejected generic edge TTA + rollback as too broad; this audit must establish a distinct target object: unlabeled *model acceptance* rather than only update scheduling.
- AETTA (CVPR 2024) already estimates post-adaptation accuracy from unlabeled target data and demonstrates model recovery. Hybrid-TTA (ICCV 2025) and OD-TTA already cover dynamic shift-triggered adaptation mode selection.
- NeurIPS 2025 risk monitoring provides a conditional target-label-free alarm, while Drift2Act (2026 preprint) provides drift-to-action control with delayed labels. Neither makes an unconditional no-label target-risk comparison identifiable.

## Active Assumptions `[A]`

- A compact model and a stream with independently held-out labels can be assembled for offline evaluation.
- The lab can measure a meaningful local task/action cost, rather than only classification accuracy.
- Hardware telemetry or multi-sensor evidence adds information beyond logits. This is unverified.

## Candidate Hypotheses `[C]`

1. A single unsupervised signal cannot uniformly certify that adaptation improves unknown target risk under arbitrary label/conditional shifts.
2. A decision policy may still be useful under explicit, measurable structure: a validated invariant, a source-calibrated proxy, or sparse delayed labels.
3. A viable pivot is an assumption-audit protocol: identify proxy failure under physical common-cause sensor shifts, abstain outside the validity region, and compare the result with AETTA-style recovery and label-assisted risk control.

## Evidence Required

1. Recent primary TTA papers on update triggers, acceptance/selection, reset/rollback, and their own limitations.
2. Theory or counterexamples concerning unsupervised risk estimation, label shift, and impossibility of reliable model selection without labels.
3. A direct-neighbor table with exact information sets and decision consequences.
4. Reproducibility/compute audit for the closest edge baseline.

## Kill Conditions `[KILL]`

1. A recent paper already uses the same unlabeled information set to certify/choose accepted versus harmful adaptations and evaluates the same online risk-cost protocol.
2. The only proposed difference is hardware deployment, a different model, or a synthetic corruption.
3. The needed extra evidence is unavailable on the planned device, or labels are secretly used by the online policy.
4. The evaluator cannot distinguish a truly helpful adaptation from a calibration-only or class-collapse artifact.

## Current Gate

`Gate 5 - Novelty Audit`: Amber. The broad no-ground-truth controller is rejected. Only the narrower proxy-validity / assumption-audit pivot may proceed to feasibility review.

## Unique Next Action

Decide whether the planned hardware and workflow provide an independently observable proxy-validity signal or a legitimate delayed-label budget. If neither exists, kill this TTA candidate.
