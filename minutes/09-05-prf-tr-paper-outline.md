# PRF-TR Paper Identity and Outline

**Date:** 2026-09-05  
**Status:** Draft structure for the conditional PRF-TR FYP. No section below
may claim a result until the physical gate is run.

## Working title

**When Digital Camera Fault Tests Mislead Edge Inspection Decisions: A
Physical-versus-Digital Action-Frontier Study**

Chinese title:

**数字摄像头故障测试会否误导边缘视觉采集决策：物理与数字条件下的动作前沿研究**

## Paper identity

This is an empirical evaluation/negative-result paper, not a vision-model or
camera-control paper. Its object is the transfer of an evaluation decision:
whether a policy that is non-dominated under digitally transformed images
remains non-dominated on declared physical optical conditions.

The printed identifier is an exact, non-personal outcome oracle. It is not the
claimed innovation, and it does not certify maintenance completion.

## Required result formats

Exactly one of these result narratives may be used after the physical gate.

### A. Frontier failure

Digital tests make a fixed action/policy appear non-dominated, but on a held-out
physical cell it is dominated by a fixed baseline on the declared false-retain
and cost components. The failure must repeat across sessions/remounts and
remain under the preregistered cost scenarios.

**Contribution:** a bounded counterexample to relying on the declared digital
fault family for this edge capture policy.

### B. Frontier preservation

The same policies remain non-dominated under digital and physical cells with
useful uncertainty intervals, and fixed controls are sufficient.

**Contribution:** a bounded sufficiency result: for this declared fixture and
policy family, the digital test family did not mislead the release choice.

### C. Observation boundary

Two staged physical cells yield overlapping permitted pre-action observations
but have different optimal follow-up actions. No image-only router can choose
correctly without an added witness or fixed conservative policy.

**Contribution:** a concrete observation-boundary result, with the fixture,
observations, and non-identifiable states explicitly named.

No fourth narrative is allowed. In particular, do not replace a null result
with a new neural model, more arbitrary corruptions, or a broader deployment
claim.

## Proposed sections

1. **Introduction**
   - Field capture policies are often screened using digital image
     transformations, but physical optical conditions can alter the action
     tradeoff.
   - State the finite question and the non-claim immediately.

2. **Problem Definition**
   - Define the actor, `retain / reacquire / review` actions, exact payload
     oracle, physical/digital cells, outcome vector, Pareto dominance, and
     source/held-out protocol.

3. **Related Work and Boundary**
   - Synthetic-to-real corruption studies, adaptive acquisition, difficult
     fiducial capture, transparent-film/polarization work, and edge quality
     systems.
   - Explain that this paper evaluates a finite action frontier rather than
     proposing any of their mechanisms.

4. **Physical/Digital Evaluation Protocol**
   - Fixture, camera path, target registry, digital transformations, baseline
     actions, hidden two-frame capture bundles, cost ledger, blocking, and
     data exclusions.

5. **Results**
   - Per-cell physical and digital outcome tables.
   - Pareto frontiers with bootstrap intervals across sessions/remounts.
   - Digital-selected versus held-out physical action comparison.
   - The selected narrative A, B, or C only.

6. **Failure Analysis and Limits**
   - Exposure/WB, target class, cover/lamp/material limits, static-only scope,
     camera-specific conclusions, and why the record oracle is not proof of
     maintenance completion.

7. **Conclusion**
   - State only the named fixture/action boundary and the practical evaluation
     implication.

## Required figures and tables

| Artifact | What it must establish |
| --- | --- |
| Fixture diagram | Exact camera, cover, lamp, target, and held-out-cell geometry |
| Cell matrix | Which physical interventions and digital transformations were declared before scoring |
| Action definition table | Capture sequence, information available, and charged costs for every baseline |
| Outcome/frontier plot | False retain against review/reacquisition and at least one measured cost component |
| Digital-to-physical comparison | Whether each digital non-dominated action remains non-dominated physically |
| Session/remount uncertainty table | Independence unit and confidence intervals, not frame-level pseudo-replication |
| Boundary/failure figure | A concrete physical cell or observation overlap explaining the selected result narrative |

## Non-negotiable reviewer questions

The final paper must answer all of the following:

1. Why is the actor's action consequential rather than an arbitrary accuracy
   metric?
2. What truth exists independently of the decoder/policy?
3. Which physical conditions were held out before thresholds were frozen?
4. Does a simple fixed two-shot or always-review policy dominate?
5. Is any result robust to plausible false-retain/review/capture cost scenarios?
6. Why does the conclusion apply only to the declared fixture, not all cameras
   or synthetic corruptions?

## Minimum publishable evidence threshold

The FYP can be defended with narrative B or C if the protocol is clean and the
advisor accepts an evaluation/negative-result identity. A workshop-style
positive empirical submission requires narrative A plus a repeated held-out
frontier failure that survives the fixed controls. No venue or acceptance is
promised by this outline.
