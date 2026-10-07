---
topic: round28-palm-stop-reconciliation
created: 2026-09-24
last_verified: 2026-09-24
status: active
depth: deep
related: [round27-palm-only-reconciliation, palm-transaction-research-gate]
sources:
  - url: https://arxiv.org/abs/2401.08111
    fetched: 2026-09-24
  - url: https://arxiv.org/abs/2104.13400
    fetched: 2026-09-24
  - url: https://openaccess.thecvf.com/content/WACV2023/html/Seon_Stop_or_Forward_Dynamic_Layer_Skipping_for_Efficient_Action_Recognition_WACV2023_paper.html
    fetched: 2026-09-24
  - url: https://proceedings.neurips.cc/paper_files/paper/2022/file/c6e954799a0218f6d341ad5cbfb58999-Paper-Conference.pdf
    fetched: 2026-09-24
---

# Round 28 PALM-STOP Reconciliation

## Summary

`PALM-STOP` is killed as a new stopping algorithm. Palm quality/frame curation and generic video early-exit/frame-selection work occupy the mechanism. The only useful residual is `PALM-STOP-NULL`: a bounded Palm full-path audit of online stopping versus fixed-N, fixed recapture and always-continue under a fixed false-accept/unknown ceiling and matched capture/energy cost.

## Findings

The online rule must use only current observations. Best-frame selection over a completed tracklet is an oracle upper bound, not a causal baseline. The audit must use person/session-held-out episodes, independent unknown labels, all-start denominators and an idempotent action endpoint. A matched fixed policy, future-frame leakage or missing action labels kills the positive claim.

## Insights

- Continuous Palm capture is not currently a lower-cost demonstrated gate: the live preview keeps only its latest frame, and checkout consumes one frame. Episode sequences, per-frame observations and independent unknown labels would require a separately authorized capture protocol.
- The important Palm-specific question is whether current quality/margin/temporal agreement identifies future-safe stopping; a new early-exit network is not justified.
- If fixed-N or fixed recapture dominates, the null closes the branch cleanly.

## Strongest objection

The entire stopping question may be ordinary temporal quality selection or sequential biometric decision-making. The local Palm endpoint can be useful for engineering, but not enough for method novelty.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| New Palm temporal stopping model | Palm frame curation and generic video early-exit mechanisms occupy the claim. | 2026-09-24 |
| Best-frame oracle as a causal policy | It uses future frames and creates selection leakage. | 2026-09-24 |

## Open questions

- Does the current executable expose continuous frames and valid source-frame IDs at every start?
- Can independent unknown/mate-absent labels be collected without claiming a rare-error guarantee?
- Does online stopping beat fixed-N/fixed-recapture after charging all capture and compute costs?

## Timeline

- 2026-09-24 - Palm video stopping audit completed; method claim killed; PALM-STOP-NULL retained as a low-cost bounded audit.
- 2026-09-24 - implementation check corrected the low-cost assumption: no time-ordered checkout sequence exists in the current path; PALM-STOP-NULL is capability-gated, not first by default.
