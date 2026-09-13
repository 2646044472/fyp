# Research Direction Index

Last updated: 2026-08-27. This page is the entry point for the next direction-selection cycle. It preserves prior work; it does not claim that any candidate has passed novelty or feasibility review.

## Current decision

The broad candidate, an edge `trigger / accept / rollback` controller based only on unlabeled TTA evidence, has failed its first novelty audit. The only live conditional pivot is whether a device can observe when its proxy-to-risk relation is unsupported, then abstain rather than trust adaptation. It replaces neither the existing palmprint work nor the broader sensor-state protocol until it passes feasibility.

## Read order

1. [`16-research-first-direction-set.md`](16-research-first-direction-set.md): prior candidates and their direct-neighbor limits.
2. [`42-sensor-state-action-audit.md`](../log/42-sensor-state-action-audit.md): the relevant sensor-state/action evidence.
3. [`18-tta-without-ground-truth-state.md`](18-tta-without-ground-truth-state.md): current charter, evidence status, and kill conditions for the new audit.
4. [`../log/48-tta-trigger-accept-rollback-discovery.md`](../log/48-tta-trigger-accept-rollback-discovery.md): paper-by-paper reading record and current novelty verdict.

## Directory rules

| Location | Role | Update rule |
| --- | --- | --- |
| `core/` | Canonical, concise claim and decision state | Update only when primary evidence changes a conclusion. |
| `log/` | Detailed paper reading, searches, artifact checks, and rejected ideas | Add one log per material audit; do not promote unsupported results. |
| `.research/` | Persistent web-research memory maintained by `research-skill` | One topic entry; sources and contrarian result required. |
| `minutes/` | Meeting notes and local constraints | Do not turn unverified remarks into technical claims. |
| root notes | Scratch notes | `思路整理.md` is a proposal seed, not canonical evidence. |

## Active questions

| ID | Question | Decision changed by answer |
| --- | --- | --- |
| Q-TTA-1 | Which recent TTA work already performs unlabeled shift detection, update gating, reset/rollback, or model acceptance? | Determines whether the direction is Red. |
| Q-TTA-2 | Can a signal from unlabeled inputs identify whether adaptation improves the downstream task, rather than merely detects a shift? | Determines whether a positive safety claim is identifiable. |
| Q-TTA-3 | Do papers themselves identify this missing link, and can a Pi-class device reproduce the closest baseline? | Determines the FYP story and feasibility. |

## Current non-goals

- Do not rebrand domain-shift detection, entropy filtering, EATA-style sample selection, OD-TTA, or a reset heuristic as a new contribution.
- Do not use held-out target labels online; they may only form an offline evaluator.
- Do not present a simulated corruption benchmark as proof of real edge safety.
- Do not claim a direction is novel because search did not find a paper.
