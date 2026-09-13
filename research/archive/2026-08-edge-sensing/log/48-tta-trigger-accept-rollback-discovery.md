# TTA Trigger, Accept, and Rollback Discovery Log

Date: 2026-08-27. Purpose: record primary-paper evidence for the question in [`../core/18-tta-without-ground-truth-state.md`](../core/18-tta-without-ground-truth-state.md). Search snippets and unverified claims do not count as conclusions.

## Scope and search vocabulary

- Test-time adaptation, online TTA, continual TTA, on-demand TTA, model selection, model acceptance, checkpoint selection, rollback, restoration, reset, drift detection, uncertainty, selective prediction, risk estimation, label-free evaluation, and unsupervised model selection.
- Include 2023--2026 primary papers plus foundational impossibility or identifiability work.
- Read the actual paper, supplement, repository, or official proceedings page before adding a source-level conclusion.

## Direct-neighbor matrix

| Paper | Primary artifact read? | Online information | Decision it makes | Uses target labels online? | Reports actual harmful-update detection? | Edge/resource evidence | Limitation relevant to this project |
| --- | --- | --- | --- | --- | --- | --- |
| AETTA, CVPR 2024 | Yes | Dropout prediction disagreement | Estimates accuracy; recovery case study | No | Heuristic estimation/recovery | No Pi-class report in this audit | Blocks generic label-free accuracy estimation + rollback. |
| Hybrid-TTA, ICCV 2025 | Yes | Temporal input correlations | Detects shift and selects tuning mode | No | No | Not the focus | Blocks dynamic shift trigger as the contribution. |
| Monitoring Risks in TTA, NeurIPS 2025 | Yes | Unlabeled loss proxy plus source calibration | Sequential alert on risk violation | No target labels | Conditional risk alarm | Not edge-specific | Proxy-loss separation is not verified label-free. |
| Drift2Act, 2026 preprint | Yes | Unlabeled monitors plus randomly sampled delayed labels | Adapt, abstain, rollback, retrain under budget | Yes, sparse delayed labels | Anytime-valid risk certificate | System-level cost protocol | Blocks a label-assisted drift-to-action controller unless physical evidence changes the result. |
| ASR, ICLR 2026 | Yes | Prediction concentration and inconsistency | Selective source reset | No | Controlled proxy study only | No Pi report in this audit | Confident wrong predictions and class imbalance can break the proxy. |

## Current interpretation

1. **[K]** Trigger-only, label-free accuracy estimation/recovery, and conditional no-target-label monitoring have direct neighbors.
2. **[K]** A controller with operational actions and a risk certificate has a direct 2026 neighbor when sparse delayed labels are available.
3. **[C]** No statistic built only from `I_t` can universally choose the lower target-risk model, because target label mechanisms can differ while all unlabeled observables match.
4. **[GAP]** No direct work was found in this audit that validates an observable proxy-validity test for RGB/NIR/ToF under correlated physical failures. This is not a novelty claim; it is the only pivot worth checking.

## Contrarian / impossibility pass

Questions to settle:

1. Can covariate shift, label shift, and a class-conditional error change be observationally indistinguishable from `I_t` while requiring opposite accept/rollback actions?
2. Does any existing theorem or empirical work already show that unsupervised TTA model selection is unreliable?
3. What additional observable can break that ambiguity: delayed label, independent sensor, verified invariant, temporal consistency, or human review?

## Evidence status

Persistent source synthesis: [`.research/tta-unlabeled-accept-rollback/FINDINGS.md`](../../.research/tta-unlabeled-accept-rollback/FINDINGS.md). Next work must derive an experiment that can falsify the assumed proxy invariance on actual hardware.
