# P2-CTB Prospectus

## Status

**LOCKED WORKING DIRECTION, Amber innovation.** P2-CTB is a bounded security measurement study, not a new inversion algorithm and not a live attack. It asks whether template leakage from one low-cost edge system transfers to another heterogeneous system.

## Story

A campus or lab service uses a local palm matcher on a kiosk or phone and stores a biometric template rather than a raw image. If the template leaks, the attacker may reconstruct a presentation that is accepted by another device in the same organization or a different deployment. The harm is unauthorized acceptance plus long-lived privacy loss because a palm cannot be reset like a password. Edge heterogeneity is part of the risk question: different camera spectra, ROI preprocessing, quantization and small models may either block transfer or create a false sense of protection. The project uses public, de-identified data and an offline sandbox; it does not access a real service.

## Exact research question

Given a leaked source template `e_A = f_A(x_A)`, can an attacker trained only with a public surrogate set produce an image `x_hat` whose frozen target embedding `f_B(x_hat)` is accepted at B's pre-registered impostor FAR threshold, when B differs from A in device domain, sensor spectrum, or matcher model?

The central endpoint is attack acceptance rate by held-out source/target cell, not reconstruction image quality. Report same-device, cross-model, cross-device and cross-sensor cells separately.

## Formalization

- Source: `A = (D_A, S_A, M_A)` and leaked template `e_A`.
- Target: `B = (D_B, S_B, M_B)` with no target identities in attack training.
- Attack map: `g: e_A -> x_hat`, trained on public surrogate identities; optional target calibration is a separately reported condition and may not use held-out identities.
- Acceptance: `cos(f_B(x_hat), e_B) >= tau_B`, where `tau_B` is frozen from genuine/impostor development pairs at a chosen FAR.
- Cells: source/target device pair, source/target sensor or spectral domain, matcher-model pair, and optional protected-template transform.
- Outcomes: attack acceptance rate, impostor FAR, genuine FNMR/EER, reconstruction similarity, query/compute budget, and edge target latency/RAM.

## Hypotheses and kill tests

**H1 [C]:** At least one held-out cross-device or cross-sensor cell has attack acceptance above the matched impostor FAR by the preregistered practical margin, after same-device sanity succeeds.

**H0 [C]:** Transfer is at or below the impostor FAR, or a simple baseline matches the attack. This yields a finite transfer barrier: the source template alone does not provide a portable presentation under the tested preprocessing/model changes.

Kill the positive claim if same-device reconstruction cannot beat the baseline, if target identities leak into attack training, if source/target ROI or spectral transforms are uncontrolled, or if the only success comes from threshold retuning on the target test cell.

## Three-round novelty audit

| Round | Established collision | Remaining Amber distinction | Audit failure |
| --- | --- | --- | --- |
| Component | Yan 2024 palm reconstruction; Yang 2023 cross-template transfer; EMPalm 2025 cross-device side-channel leakage; CAAP 2026 physical cross-model/cross-dataset transfer. | Combine a leaked template with a fixed source-to-target device/sensor/model transfer matrix and a frozen edge matcher; no new attack component. | A new GAN, patch, query strategy or physical attack is claimed. |
| Exact claim | Yan already reports cross-algorithm/cross-dataset reconstruction; no inspected paper reports this exact palm template-to-presentation matrix across held-out devices and sensors. This is a search-bound [GAP], not absence proof. | Measure the transfer endpoint and its barrier, with source/target transformations explicit. | A later paper or code artifact has the same matrix/endpoint. |
| Boundary | ROI extraction, spectrum, normalization, quantization and model family can make transfer fail for non-security reasons. | Attribute failure to a declared transformation only after matched controls; test protected-template variants separately. | No paired identities, no independent target FAR, or no same-device control. |

## Minimum experiment

Use X-Palm if its academic EULA is approved; its repository documents 6,006 images from 103 people, 81 paired scanner/smartphone participants, 80+ smartphone models and self-contained benchmark scripts. Fallback datasets are MPD-v2 and XJTU-UP if access is granted. Start with 3.27M-parameter CompNet plus one second lightweight matcher; add a third only if the same-device sanity test is stable. The minimum attack is a small linear/MLP decoder trained offline; reproducing Yan's ProGAN is optional and cannot be substituted for a failed sanity check.

1. Freeze identity-disjoint train/development/test splits and target FAR thresholds.
2. Reproduce a same-device decoder/reconstruction baseline. Do not claim Yan-equivalent performance unless the implementation and threat model are checked.
3. Evaluate source-to-target transfer across device, sensor/spectrum and model cells, with no target-cell tuning.
4. Repeat with one published protected-template transform as a comparison, reporting EER, linkability/reissuance where implementable, and attack acceptance separately.
5. Run the frozen target matcher on a Pi-class ARM board only for latency, RAM and template-storage measurements; attack training remains offline on available GPU/CPU.

Required baselines: impostor random/nearest-neighbor image, same-device reconstruction, cross-model reconstruction, Yan-style reported protocol where reproducible, and a no-template-leak control. An oracle using target identities is prohibited except as an explicitly labeled upper bound.

## Data, compute, ethics

No new biometric collection is required. X-Palm is academic-use only and prohibits redistribution and re-identification; the EULA must be accepted before use. Reconstructed images stay local, are not published, and are evaluated only against frozen offline matchers. The minimum decoder can run on CPU; a desktop GPU is optional for a stronger comparison. The Pi is a target measurement device, not the training platform. Exact dataset approval, model-code compatibility, board availability and budget remain [GAP] until the pilot preflight.

## Timeline

- **September 2026:** obtain data permissions, freeze threat model, splits, FAR and metrics; run same-device decoder sanity.
- **October:** implement source/target device and model matrix; add ROI/spectrum controls and reproducible logs.
- **November:** run held-out transfer and protected-template comparison; apply the kill gate.
- **December:** demo a local matcher showing source-template leak, offline reconstructed presentation, target decision and a blocked-transfer case; no live access system.
- **January--June 2027:** expand device/model cells, confidence intervals, sensitivity to template protection and edge resource budgets; optimize only if H1 survives.

## Pivot

If H1 fails, the thesis becomes a negative transfer-barrier study. If data or model access fails, pivot to a reproducible cross-device EER/linkability audit (P1/P3) without inversion claims. If same-device reconstruction is infeasible, stop the attack line rather than replacing it with a new model and calling that innovation.
