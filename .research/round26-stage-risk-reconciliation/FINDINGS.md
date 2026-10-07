---
topic: round26-stage-risk-reconciliation
created: 2026-09-24
last_verified: 2026-09-24
status: active
depth: deep
related: [palm-transaction-research-gate, round25-targeted-reconciliation]
sources:
  - url: https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:19795:-1:dis:ed-3:v1:en
    fetched: 2026-09-24
  - url: https://pages.nist.gov/800-63-3/sp800-63b.html
    fetched: 2026-09-24
  - url: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-76-2.pdf
    fetched: 2026-09-24
  - url: https://proceedings.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf
    fetched: 2026-09-24
  - url: https://arxiv.org/abs/2208.02814
    fetched: 2026-09-24
---

# Round 26 STAGE-RISK Reconciliation

## Summary

`STAGE-RISK` is killed as a positive method. Existing biometric standards and transaction metrics occupy the measurement vocabulary; reliability composition, selective prediction, calibration and stage logging occupy the proposed mechanism families. The only useful residual is `STAGE-NULL`: a negative identifiability audit showing that marginal stage rates do not determine terminal action risk without dependence and reachability assumptions.

## Findings

Two stages with the same marginal pass rates can have different joint pass rates under different dependence structures. In a live transaction, retries, gallery membership, unknown thresholds and stage reachability create further dependence. If every eligible start and transition is linked to the final action, direct episode-level frequency is identifiable; a new composition rule is unnecessary unless it wins a held-out action-cost comparison.

The minimum useful study is therefore a counterexample plus a frozen all-start trace. Candidate estimators include product-of-marginals, direct episode frequency, stage-stratified logistic/isotonic calibration and fixed unknown/retake/refusal controls. Any use of post-action labels or test-set confidence as an input invalidates the estimator.

## Insights

- The endpoint “mock debit” does not create method novelty by itself.
- The scientifically defensible contribution, if any, is a boundary on what can be inferred from incomplete stage summaries.
- A complete trace is stronger evidence than an inferred product of marginal rates, but the trace itself is an evaluation artifact unless it supports a new falsifiable result.

## Strongest objection

The all-start trace may simply reproduce standard operational biometric evaluation. If so, `STAGE-NULL` should be reported as a protocol sanity check or appendix, not protected as a thesis direction.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| Stage-conditioned risk estimator as a new method | Existing metrics, calibration and selective prediction cover the components; direct episode frequency is the simplest strong baseline. | 2026-09-24 |
| Stage log/dashboard as a CS contribution | Instrumentation and operational reporting are not a mechanism. | 2026-09-24 |

## Open questions

- Can the current executable record every eligible start before capture/ROI failure?
- Are there enough independent people and sessions for a held-out terminal action estimate?
- Does any stage-conditioned feature add information beyond fixed quality/margin/retake controls after configuration freeze?
- Can a randomized intervention identify stage attribution, or is only the negative dependence boundary observable?

## Timeline

- 2026-09-24 - divergence and validation agreed: kill the positive STAGE-RISK method; retain STAGE-NULL only as a bounded negative audit after the Palm all-start trace.
