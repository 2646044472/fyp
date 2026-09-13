---
topic: printed-authentication-cdp-boundary
status: superseded/kill
searched_at: 2026-08-31
sources: [WACV, arXiv, EUIPO]
---

# Printed Authentication / Copy-Detection Patterns

## Summary

RGB/NoIR verification of a printed copy-detection pattern is an attractive real story with an independent genuine/copy label, but it is not an open thesis endpoint in the inspected source set.

## Findings

- Oleksiyuk et al. (arXiv v1 2026-05-29, Secs. 1-6) combine the digital template, enrolled physical capture, cross-camera translation, printer stochasticity and heterogeneous low-end mobile verification. They report strong performance on small CDP regions and list domain adaptation/zero-shot generalisation as future work.
- Atoki et al. (WACV 2026) use printer-signature-conditioned diffusion and evaluate unseen counterfeit types. A new detector, printer classifier, or low-cost Pi deployment would collide with these endpoints.
- EUIPO's official technology guide describes mobile-phone CDP authentication as an established anti-counterfeiting workflow: https://euipo.europa.eu/anti-counterfeiting-and-anti-piracy-technology-guide/marking-technologies/copy-detection-patterns

## Decision

**KILL.** Keep CDPs only as the independent marker/oracle apparatus for the physical-transfer audit. Do not allocate a thesis slot to CDP authentication itself.

## Sources

- https://arxiv.org/abs/2605.31292
- https://openaccess.thecvf.com/content/WACV2026/html/Atoki_Diffusion-Based_Authentication_of_Copy_Detection_Patterns_A_Multimodal_Framework_with_WACV_2026_paper.html
- https://euipo.europa.eu/anti-counterfeiting-and-anti-piracy-technology-guide/marking-technologies/copy-detection-patterns
