# Biometric Second-Round Gate (2026-08-31)

## Decision

**P2-CTB is KILL as a primary FYP direction. No biometric direction is currently locked.** This file supersedes P2's active status but preserves its prospectus as a traceable rejected hypothesis.

## What changed

P2 treated a generated, normalised palm ROI as a reconstructed presentation accepted by target B. That bypasses B's acquisition device, target ROI localisation, capture quality checks and any presentation-attack detection. It is therefore a digital matcher-input experiment, not evidence about cross-device, cross-sensor or physical transfer. Yan et al. already study palm template reconstruction with cross-algorithm and cross-dataset evaluation. See Yan 2024, publisher HTML `Introduction`, `Methodology`, `Experiments` and `Conclusions`: https://doi.org/10.1016/j.patcog.2024.110655.

X-Palm v2 supplies paired scanner/smartphone identities, but its smartphone domain deliberately combines hardware, pose, illumination, distance, perspective, background, occlusion and palm-surface condition. Its 112x112 ROIs are standardised before recognition. The dataset can establish a broad domain shift, but without support for each nuisance factor it cannot identify a named device, sensor, ROI or template-protection cause. See X-Palm v2, abstract, Secs. 2.1-2.4 and 3.2: https://arxiv.org/html/2606.08437v2.

EMPalm and CAAP have different observations (electromagnetic leakage and capture-aware physical patches). They do not prove that a stored-template leak behaves the same way, but they reinforce that a physical claim needs an explicit physical observation path rather than a direct ROI injection. See EMPalm Secs. 3-5: https://arxiv.org/abs/2510.07533 and CAAP Secs. III, V-B-F: https://arxiv.org/abs/2604.06987.

## Candidate status

| Candidate | Status | Reason |
| --- | --- | --- |
| P1 robustness versus linkability | HOLD | Needs licensed repeated paired devices, a published transform, and a frozen multi-template attacker; generic methods already collide. |
| P2-CTB template transfer | KILL | Positive endpoint materially collides; null is non-identifying under the planned data/protocol. |
| P3 protected templates | KILL broad / audit only | Existing transforms and ISO-style metric packages occupy the claim family. |
| P4 response-feedback attack | KILL | Existing reconstruction and capture-risk literature occupies the basic threat family. |
| P5 quality/uncertainty | KILL generic | Open-set/domain-shift methods are direct neighbors; only a control remains. |
| P6 cross-spectral/missing modality | KILL generic / PIVOT audit | Missing-modality methods collide and current RGB hardware cannot validate NIR. |
| BIA-1 attribution sufficiency | KILL standalone / preflight only | ISO-style factor/test reporting and generic shift diagnosis already occupy the proposed certificate; X-Palm lacks the required factor support. |

## BIA-1 disposition

- [D] A frozen matcher yields scores `s`; `d` is the observed broad domain; `v` is the claimed device/sensor factor; `u` contains recorded nuisance variables such as pose, illumination, distance and ROI path.
- [A] A factor-specific claim needs cross-classified or matched support over `u`, identity-disjoint splits, and a frozen FAR/FRR rule. Otherwise only a broad-domain association is observed.
- [KILL] The report may be useful project governance, but not a CS FYP contribution: ISO/IEC 19795-10:2024 already requires controlled-factor plans, uncertainty and non-unique-attribution disclosure; modern shift-diagnosis work occupies the generic method family.
- [N] Retain `broad-domain-only` and `attribution-insufficient` as mandatory reporting outcomes for future biometric experiments, not as thesis claims.

## Next gate

BIA-1 was killed after its focused validation. The Pi demo may continue as engineering work but cannot promote any biometric research claim. Future biometric work must use this preflight before claiming device, sensor, privacy or security effects.
