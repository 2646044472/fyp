---
topic: biometric-attribution-sufficiency
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - palm-template-transfer-boundary
sources:
  - url: https://standards.iteh.ai/catalog/standards/iso/c393f7c4-f721-4602-a96f-f84b35e020f9/iso-iec-19795-10-2024
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2303.02011
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2411.07940
    fetched: 2026-08-31
  - url: https://arxiv.org/html/2606.08437v2
    fetched: 2026-08-31
---

# BIA-1: biometric attribution-sufficiency certificate

## Summary

Superseded on 2026-08-31. The proposed certificate would decide whether an observed cross-domain performance gap can be attributed to a named device or sensor, or must be reported as attribution-insufficient. This is sound experimental discipline but not a defensible standalone FYP contribution: ISO/IEC 19795-10:2024 already requires the relevant differential-performance design, and generic distribution-shift diagnosis already covers the methodological family. X-Palm's scanner-versus-phone label is compound, so it cannot support the intended causal claim.

## Findings

### Experimental-design collision [KILL]

ISO/IEC 19795-10:2024, Clause 5.1 (pp. 4-5), Clause 5.2.4 (p. 8), and Clause 6.3 (p. 9), requires a differential biometric performance test plan to specify variables, data collection, manipulated/fixed/blocked factors, controls, uncertainty and statistical treatment. It warns that an operational evaluation with uncontrolled factors cannot uniquely establish the cause of a performance difference. The standard focuses on demographic differential performance, but the experimental-design logic is directly applicable to acquisition-factor attribution.

### Method-family collision [KILL]

Cai, Namkoong and Yadlowsky, "Diagnosing Model Performance Under Distribution Shift" (arXiv:2303.02011, Sections 3.2-3.3, pp. 7-9), formulate interpretable explanations for model performance differences under distribution shift. Roschewitz et al., "Beyond the Benchmark: Diagnosing Dataset Shift in Computer Vision" (arXiv:2411.07940, Section 5, pp. 12-13), state that broad shift types alone cannot identify whether an observed change arose from fine-grained acquisition conditions or population factors without suitable metadata. These sources occupy the generic diagnosis/certificate method family.

### Data identification failure [KILL]

X-Palm v2 (2026-06-22), Section 3.1, describes the smartphone domain as jointly varying device, pose, illumination, distance, perspective, background, occlusion and surface condition. Its 81 paired scanner/phone participants are not a cross-classified device-by-nuisance experimental design. The available paper/repository description therefore supports a broad-domain comparison, not an identifiable named-device or named-sensor effect. The EULA and full schema availability were not independently verified; that uncertainty does not rescue the missing design factors described in the paper.

## Strongest baseline

An ISO-style broad-domain report: declare the domain bundle, list known uncontrolled factors and metadata support, report uncertainty, and state that device-specific attribution is unsupported. This baseline implements the honest decision with no proposed new model. A certificate that merely automates that statement does not clear a research-contribution gate.

## Discarded approach

| Approach | Why dropped | Date |
|---|---|---|
| BIA-1 attribution-sufficiency certificate | Existing biometric differential-performance design and generic shift diagnosis occupy the method family; the candidate data cannot identify the named causal factor | 2026-08-31 |

## Open question

Could a different, separately licensed, controlled crossover dataset make a narrow acquisition-factor study possible? This is unresolved, but no such data is in scope and it would still need a distinct decision endpoint beyond reporting discipline.

## Timeline

- 2026-08-31 - divergence proposed BIA-1 only as a temporary residual after P2-CTB was killed.
- 2026-08-31 - independent validation killed BIA-1 as a thesis and retained its checklist only as a mandatory preflight/appendix.
