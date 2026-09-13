---
topic: edge-evidence-admission
created: 2026-09-05
last_verified: 2026-09-05
status: active
depth: medium
related:
  - physical-failure-synthetic-transfer-boundary
  - edge-camera-physical-performance-candidates
sources:
  - url: https://doi.org/10.1007/978-981-99-3626-7_10
    fetched: 2026-09-05
  - url: https://arxiv.org/abs/2606.16667
    fetched: 2026-09-05
  - url: https://www.gov.mo/en/news/287554/
    fetched: 2026-09-05
---

# Edge Evidence Admission

## Decision

**PIVOT only.** Camera-record admission is a usable story frame, but it is not an innovation claim by itself. Under a constrained edge budget, decide whether one visual observation is sufficient to release a non-personal record, whether to acquire one more observation, or whether to defer to review.

This reframes PRF-TR rather than creating a separate hardware-dependent thesis. Promote only if a held-out physical boundary is not reproduced by fixed two-shot capture, a scalar quality gate, always-review, or a standard image-quality-assessment (IQA) admission rule.

## Direct-neighbor correction

- [K] Dong, Lu and Chen, *Image Quality Assessment for Construction E-inspection: A Case Study* is a formally published 2023 Springer conference chapter (pp. 125-133; DOI metadata verified through Crossref and OpenAlex). Its title and cited IQA references establish it as a strong direct neighbor for a generic construction e-inspection image-quality story.
- [GAP] The chapter is non-open-access in the sources inspected. Its complete task, action policy, experimental protocol and limitations have not yet been read; prior search snippets about uploader re-submission must not be used as central evidence.
- [KILL] Even without assuming its exact action policy, "edge implementation of image-quality assessment for inspection photographs" is not a standalone FYP contribution. The chapter, established no-reference IQA literature, and generic image-quality workflows make this a baseline-level direction.
- [PIVOT] The residual question is stricter: on a preregistered exact-record task, does a source-fitted *digital* quality/fault test preserve the cost-risk order of fixed actions under *held-out physical optical conditions*? The IQA admission rule is a mandatory baseline, not the proposed method.

## Research story

At a humid or intermittently lit site, an edge camera is asked to create a local inspection or asset record. The costly error is not merely a wrong class label: a wrong record can associate the next action with the wrong asset or condition, while a needless second capture or human review consumes time, energy and operator attention.

After the first capture the node chooses:

1. `retain`: release the record.
2. `reacquire`: take one declared RGB or NoIR+IR capture.
3. `unknown/review`: do not release an automated record.

The question is whether digital image tests calibrated on clean data preserve the cost-risk ordering of those actions when the failure is produced by a physical optical condition.

## Contribution boundary

- A preregistered paired physical/digital action-risk protocol, not a new detector.
- Independent exact-payload or fixture truth separated from the deployable policy.
- Equalized capture, latency, storage and energy accounting.
- A blocked-session result reported as rank inversion, rank preservation, or non-identifiability.

The claim must remain finite: one RGB/NoIR setup, declared optical cells, one non-personal record task, and the tested baselines. No universal physical-failure theorem, maintenance-completion claim, or general abstention guarantee.

## Why this framing survives the application audit

Application-first variants such as floor wetness, filter replacement, frost, PV soiling, turbidity or print-failure stopping are natural detector-to-action continuations, and their technical endpoints are already occupied or require a domain sensor that becomes the real source of truth.

The evidence-admission framing keeps camera and edge constraints central while making the endpoint a decision and evaluation question. Macao is legitimate workflow motivation, not novelty evidence: its World Heritage Monitoring Centre explicitly combines systematic data collection, mobile applications and durable monitoring records, while local asset-management systems advertise QR/mobile maintenance records. Neither source establishes an accessible deployment partner or research gap.

## Kill criteria

- Fixed two-shot is Pareto-optimal after measured cost.
- A scalar brightness/blur/decoder gate matches the proposed policy.
- A standard IQA admission rule matches the proposed policy.
- The physical cell label or oracle is not independent of the deployable observation.
- The effect disappears under blocked session/remount/lamp analysis.
- The claim reduces to ordinary abstention or acquisition without a distinct physical observation boundary.

## Current disposition

**PIVOT.** Keep only as the story-level framing for the finite PRF-TR pilot. The research claim is physical-versus-digital action-rank validity; the workflow framing is not a method. Hardware is only needed when the selected physical experiment is ready; connectivity is not a research gate.
