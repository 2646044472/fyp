---
topic: active-viewpoint-edge-boundary
status: superseded/kill
searched_at: 2026-08-31
sources: [NeurIPS, Applied Soft Computing]
---

# Active Viewpoint / Pan-Tilt Verification

## Summary

A pan-tilt camera that rotates to resolve an ambiguous printed marker has a plausible edge story, but the core mechanism is already active-viewpoint planning.

## Findings

- Huang et al. (NeurIPS 2024) select unknown viewpoints using predicted representation disparity and report gains over random/sequential selection: https://papers.neurips.cc/paper_files/paper/2024/hash/2360da01c2ed6592bb691326424de184-Abstract-Conference.html.
- Dai et al. use uncertainty-driven 3-DoF pan-tilt view planning to reduce visual tracking failure: https://doi.org/10.1016/j.asoc.2021.107459.
- Therefore a new next-best-view score, confidence-triggered rotation, or Pi deployment is a component collision. Only a finite exact-marker retain/reacquire audit could remain as an appendix.

## Decision

**KILL.** Do not buy a pan-tilt mechanism for a thesis until the physical-transfer pilot demonstrates a distinct action endpoint.
