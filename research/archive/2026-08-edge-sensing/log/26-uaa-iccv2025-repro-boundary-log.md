# UAA ICCV 2025 Reproducibility and Scope Log

Last updated: 2026-08-21. This is a focused read of the open ICCV 2025 paper, its supplementary material, and the linked author repository. UAA is relevant to difficult-sample recognition, but not to PAD or edge deployment.

## Sources inspected

| Artifact | Access result | Observation |
| --- | --- | --- |
| [ICCV 2025 paper](https://openaccess.thecvf.com/content/ICCV2025/papers/Jin_Unified_Adversarial_Augmentation_for_Improving_Palmprint_Recognition_ICCV2025_paper.pdf) | Open full paper | UAA uses adversarially optimized geometric transformation and an identity-preserving palmprint generation module to create difficult samples. The motivation is recognition failure under positional/size/angular changes, overexposure, blur, shadows, and wrinkles. |
| [Supplement](https://www.openaccess.thecvf.com/content/ICCV2025/supplemental/Jin_Unified_Adversarial_Augmentation_ICCV_2025_supplemental.pdf) | Open supplementary PDF | Reports experiments on MPD, XJTU-UP, and BJTU, including ablations over optimization steps and augmentation ratio. Identity consistency is evaluated with cosine similarity from a pretrained recognizer on 10k paired original/augmented samples; the supplement reports `C_geometric = 0.88`, `C_textural = 0.92`, and `C_combined = 0.80`. These are augmentation-consistency measures, not biometric verification or PAD metrics. |
| [Author repository](https://github.com/Ukuer/UAA) | Cloned at review time | The repository contains only a README stating that code will be released soon; no implementation, weights, dataset, or environment was present. Do not cite it as an available implementation. |

## What transfers to this project

1. Capture quality must be treated as a structured variable. The paper's failure taxonomy supports logging geometry, exposure, blur, shadows, and skin wrinkles rather than reporting one pooled accuracy.
2. A difficult-sample result is not a liveness result. UAA changes training samples and tests recognition generalization; it does not present bona fide/PAIS protocol, APCER/BPCER, IAPMR, or a sensor-boundary analysis.
3. The training method is not an edge novelty. The paper uses a differentiable spatial transformer, a GAN-style identity-preserving generator, adversarial optimization, and dynamic sampling. Those operations are training-time machinery and should not be placed in the Pi capture loop without a separate resource study.
4. The reported identity-consistency cosine values should not become a deployment threshold. They are internal augmentation checks with a pretrained recognizer, not FMR/FNMR or a calibrated `1:1` decision.

## Consequence for B0--M

The current protocol should first collect a B0 degradation table: distance/pose bins, exposure state, blur/ROI failures, session, and bona fide matcher outcomes. If a later model uses augmentation, it must be compared at a frozen verification threshold and fixed capture/attack split. Any PAD claim still requires separate PAIS, blind material/session holdout, APCER/BPCER and final IAPMR; UAA cannot supply those metrics.

## Wording

Use: “UAA shows that difficult geometry and texture are recognition-generalization problems worth measuring in our capture protocol.”

Do not use: “UAA provides palm liveness,” “the UAA GitHub implementation is available,” or “UAA proves the Pi model will generalize.”

