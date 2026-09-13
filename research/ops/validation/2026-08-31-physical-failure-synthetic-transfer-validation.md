# Validation Audit: 2026-08-31 Physical camera failure vs synthetic corruption transfer

## Decision investigated

Audit the proposed Pi 5 RGB + NoIR family: whether policies or model rankings learned/evaluated with digital missing-modality masks and image corruptions transfer to physically induced camera/optical failures. The intended minimum setup is two sequential official cameras, a fixed non-personal printed marker, and an external marker oracle.

## Claim under test

Candidate PHY-MASK claims that, under a fixed capture-time/energy budget, synthetic zero/random masks or post-hoc noise do not preserve action ranking or risk on physically induced cells (camera unplug/reconnect, lens cover, blocked/saturated IR, and frame interruption). Candidate FULL-CAP makes the narrower benchmark claim that digital corruption severity does not reliably predict the ordering of exact-marker errors from real capture changes. A positive result would be a bounded physical-vs-digital transfer boundary, not a new fusion model or a general field-fault guarantee.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Liao et al. (CVPRW 2025) already combine missing/noisy modality cases and robustness metrics; MultiCorrupt (2024) and MSC-Bench (2025) already combine camera/LiDAR crash, frame loss, alignment, weather and sensor corruption; Park et al. (CVPR 2025) route queries among modality experts under camera drop/occlusion. | None of these uses Pi RGB/NoIR, a controlled optical intervention, or a known-code decision with measured acquisition cost. This is a hardware/endpoint boundary, not component novelty. | High for generic robustness; medium for the bounded protocol. |
| Exact-claim collision | Agnihotri et al. (CVPRW 2025, arXiv v1) directly asks whether synthetic corruptions are a proxy for real-world corruptions, finding Pearson 0.759 for mean performance and weak per-corruption correlations (brightness/night 0.270, fog/fog 0.349). SIDL (AAAI 2025) supplies real dirty-lens images paired with clean references. | Their endpoints are semantic segmentation or restoration, not action selection at a capture budget with an independently printed code. Liao/MSC-Bench use simulated failure on public driving datasets and no physical capture. The exact Pi decision endpoint remains distinguishable but unverified as useful. | High that broad claim collides; medium that bounded endpoint remains open. |
| Boundary / impossibility | A cable pull, blocked lens, low lux, IR saturation and missing frame can be observationally confounded after ISP processing. A synthetic mask can have the same pixel marginal while differing in timing, exposure state, dropped metadata and energy. Without independent physical labels and an external marker oracle, no transfer statement is identifiable. | A rigid stand, lux measurement, manual/logged AEC/AWB state, explicit fault-cell labels, and exact decoded marker equal to a preprinted source make a finite paired test identifiable. It still cannot identify general camera health or unseen failure mechanisms. | High for the identifiability warning; medium for reproducibility across modules. |

## Assumption and identification audit

1. **Observation model.** The standard Camera Module 3 has an IR-cut filter and the NoIR variant omits it (Raspberry Pi product brief, p. 3). They are distinct optical paths, but sequential captures are not synchronized and the NoIR image is mixed visible/NIR. Any moving-target result is invalid without an independent timestamp oracle.
2. **Independent target.** The printed QR/AprilTag/ArUco payload must be generated before capture and decoded independently from the same physical sheet; a confidence score from the tested model is not an oracle. Store the source payload and exact equality result, not only a predicted class.
3. **Independent fault label.** For every episode record `fault_cell` from the intervention script (camera disconnected, lens cover, IR blocked/saturated, or intentional frame interruption), plus lux, distance, illuminator state, exposure/gain/WB mode, frame timestamp and power. A post-hoc image-only label is circular.
4. **Two-world counterexample.** A low-lux clean lens and a transparent cover with a water film can produce similar RGB/NoIR brightness/blur; the same pixel statistics can therefore correspond to different physical labels. The experiment must report this as a non-identifiability result if a fixed two-shot ratio or marker oracle cannot separate them.
5. **Scope.** “Synthetic ranking transfers” means only the preregistered marker decoder/action set and finite fault cells. It cannot be extrapolated to autonomous driving, safety actuation, semantic truth, or arbitrary sensor failures.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Agnihotri et al., *Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?*, arXiv:2505.04835v1 (7 May 2025), CVPR 2025 SynData4CV Workshop, https://arxiv.org/abs/2505.04835 | Cityscapes images plus 15 synthetic common corruptions; real ACDC weather images; no physical intervention | Semantic-segmentation mIoU, GAM, and Pearson correlations; Secs. 1, 3, 4.1-4.2, 5 (HTML) | Directly occupies the synthetic-vs-real proxy question. Mean correlation supports proxy use, while corruption-specific failures show it is not universal (Sec. 4.2). | Kills any broad “digital corruption is not representative” thesis. Leaves a sensor/optical-fault plus fixed action/energy endpoint open, but only Amber.
| Liao et al., *Benchmarking Multi-modal Semantic Segmentation under Sensor Failures*, arXiv:2503.18445v1 (24 Mar 2025), CVPRW 2025, https://arxiv.org/abs/2503.18445 | DELIVER/CARLA modalities; zeros entire or random modality portions and adds Gaussian/salt-pepper noise; Sec. 3.2.1-3.2.3 | mIoU^Avg/E for EMM/RMM and noisy modality; Secs. 3.2, 4.2, 5, pp. 1577-1583 in CVPRW version | Direct simulated missing/noisy failure benchmark and modality ranking. | Kills “first missing-modality robustness benchmark” and any fusion-model contribution. Leaves physical transfer validation as a negative benchmark only; DELIVER is simulator-generated (Sec. 3.1, lines 71-79).
| Beemelmanns et al., *MultiCorrupt*, arXiv:2402.11677v1 (18 Feb 2024), https://arxiv.org/abs/2402.11677 | nuScenes camera/LiDAR with ten synthetic corruption types including misalignment, weather, and sensor noise | Five multimodal 3D detectors; robustness by corruption type; abstract and Secs. 1-3 | Occupies multi-sensor synthetic corruption stress testing. | Kills a generic “systematically test sensor corruptions” claim. No physical camera fault, known code, or low-cost edge action endpoint.
| Hao et al., *MSC-Bench*, arXiv:2501.01037v1 (2 Jan 2025), https://arxiv.org/abs/2501.01037 | nuScenes val with 16 synthetic camera/LiDAR corruptions: camera crash, frame lost, temporal/spatial misalignment, fog/snow; Table I and Sec. III pp. 2-3 | NDS/mAP and model rankings; camera crash and frame-lost definitions are explicitly simulated (PDF pp. 1-3) | Occupies compound sensor-failure benchmark and model-ranking analysis. | Kills a generic camera-crash/frame-loss benchmark. Leaves the physical-vs-synthetic validity question, but only for a much smaller externally labelled endpoint.
| Park et al., *Resilient Sensor Fusion Under Adverse Sensor Failures via Multi-Modal Expert Fusion*, CVPR 2025 pp. 6720-6729, arXiv:2503.19776, https://arxiv.org/abs/2503.19776 | Camera/LiDAR features; adaptive query router chooses camera, LiDAR, or fused expert under camera drop, occlusion and other failures (abstract/Sec. 1) | nuScenes-R detection NDS under failure cells | Direct adaptive response to sensor failures, though all failures are dataset-level and no physical intervention is performed. | Kills a claim that adaptive routing under failure is new. Leaves physical ranking-transfer measurement as a protocol, not a routing architecture.
| Choi et al., *SIDL: A Real-World Dataset for Restoring Smartphone Images with Dirty Lenses*, AAAI 2025, pp. 2545-2554, https://doi.org/10.1609/aaai.v39i3.32257 | iPhone 12 Pro fixed setup; real water drops, fingerprint, dust, scratch and mixed dirty films, each paired with clean reference; Secs. Introduction, Dataset pp. 2545-2547 | Restoration PSNR/SSIM and model comparison; 300 scenes/1,588 degraded images | Direct physical optical-contamination dataset and clean-reference protocol. | Kills a dirty-lens dataset/restoration novelty claim. Leaves a narrow active IR intervention for exact-code acceptance, but OPT-WIT/ILLUM passive claims collide.
| Dünkel et al., *CNS-Bench*, ICCV 2025 pp. 19978-19988, arXiv:2507.17651v1 (23 Jul 2025), https://arxiv.org/abs/2507.17651 | Diffusion/LoRA-generated continuous nuisance severities; no physical sensors | Failure points and changing model rankings across nuisance scales; abstract/Introduction | Occupies continuous severity and ranking-change benchmark logic. | Kills a generic “continuous corruption severity changes model ranking” claim. Leaves physical capture as a distinct source, but a Pi benchmark must avoid presenting severity curves as new by themselves.

## Strongest simple baseline

Use a fixed two-shot policy: RGB with IR off, then NoIR with a fixed IR pulse; decode with a deterministic QR/AprilTag library and accept only exact equality, otherwise `unknown`/reacquire. Compare against always-RGB, always-NoIR+IR, preview brightness/blur threshold, random action, and oracle fault-cell choice. Report exact-code accuracy, false-retain rate, abstention/reacquisition count, latency, and joules per episode. If this fixed policy is Pareto-optimal, any learned selector is unnecessary. For FULL-CAP, compare digital corruption severity rank with physical-cell rank using Spearman/Kendall correlation and bootstrap confidence intervals; pre-register a minimum effect and a null threshold.

## Contrarian result

The most likely result is not a new method but a null: for a static printed marker, fixed illumination and manual controls, simple brightness/blur plus the fixed two-shot policy may predict or dominate all adaptive choices. A second likely null is that cable disconnect and full-frame zeroing have the same action rank, making the benchmark merely a small replication of Liao/MSC-Bench. Such nulls are useful only if the test is explicitly framed as a finite transfer audit with a preregistered stopping/kill rule; they do not justify “physical failures are fundamentally different.”

## Feasibility audit

- **Hardware:** Current Pi 5B, RGB, NoIR and IR illuminator are sufficient for static sequential cells. Buy only a rigid mount, lux meter/calibrated light source, USB inline power meter, and transparent-cover/fixture kit. No second similar camera is needed.
- **Data/ethics:** Printed non-personal codes and material swatches avoid personal data, consent, and biometric risks. The external source payload gives a cheap ground truth.
- **Compute:** A frozen OpenCV/AprilTag/ZXing decoder and small quality features run on Pi; training can be done on an existing desktop, but no deep model is required for the minimum audit.
- **Timing/control:** Pi multi-camera capture and 3A behavior are not guaranteed synchronized. Keep target static or add an LED/photodiode timestamp oracle before testing motion.
- **Labels:** Fault intervention script, lux, power, and exposure metadata are mandatory. Without them, kill the causal/physical claim and retain only an image-quality table.
- **Time:** A 2x2x4 matrix (camera path x lux x cover/fault cell) with repeated episodes is feasible for a December 2026 demo; held-out covers/distances and board re-mount repetitions fit 2027 H1. Generalizing beyond the purchased pair is infeasible.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Synthetic corruption can correlate strongly with real-world robustness in aggregate but fail per corruption. | [K] | Agnihotri et al., arXiv v1 7 May 2025, https://arxiv.org/abs/2505.04835 | HTML Sec. 4.1-4.2 and Sec. 5; Pearson 0.759 overall, 0.270 brightness/night, 0.349 fog/fog | Semantic segmentation and weather shifts, not physical camera faults.
| Entire/random missing and noisy modalities are already benchmarked using zeroing/noise simulations. | [K] | Liao et al., arXiv v1 24 Mar 2025, https://arxiv.org/abs/2503.18445 | Sec. 3.2.1-3.2.3, 4.2, 5; CVPRW pp. 1577-1583 | DELIVER is CARLA-generated; no physical intervention.
| Camera crash/frame loss and compound sensor corruption are established benchmark cells. | [K] | Hao et al., arXiv v1 2 Jan 2025, https://arxiv.org/abs/2501.01037 | PDF Table I, Sec. III, pp. 1-3 | nuScenes offline simulation; no edge action or optical path.
| Physical dirty-lens artifacts have a paired clean-reference dataset. | [K] | Choi et al., AAAI 2025, DOI above | PDF pp. 2545-2547, Dataset section and Table 1 p. 2546 | iPhone setup; restoration endpoint, not exact-code reliability.
| Sensor-failure adaptive routing is already a learned fusion family. | [K] | Park et al., CVPR 2025, arXiv:2503.19776 | Abstract and Sec. 1; CVPR pp. 6720-6729 | LiDAR/camera and nuScenes-R; failure is simulated.
| A finite physical-vs-digital transfer test with an independent code oracle is identifiable in principle. | [C] | Proposed protocol; Raspberry Pi official camera docs/product brief, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | Product brief p. 3; Pi camera software docs accessed 2026-08-31 | Requires measured controls and static target; not yet empirically verified.
| Digital rankings will reverse on physical cells. | [C] | PHY-MASK/FULL-CAP hypothesis | No source; empirical gate required | Must stay Amber until repeated held-out physical cells show a preregistered inversion.

## Queries and failed searches

- `2024 2025 physical sensor failure benchmark synthetic corruption real-world camera missing modality primary paper`
- `2024 2025 real versus synthetic image corruption camera sensor failure transfer benchmark`
- `2025 multimodal sensor failure real physical corruption missing camera benchmark`
- `2024 2026 camera reliability physical fault injection synthetic corruption edge vision`
- `real-world camera failure dataset physical lens occlusion sensor benchmark 2025`

Searches found strong simulated-failure benchmarks (Liao, MultiCorrupt, MSC-Bench, MoME), the direct synthetic-vs-real proxy study (Agnihotri), and SIDL’s physical contamination dataset. No verified primary paper was found using Pi RGB/NoIR cable/illumination faults with an external known-marker action endpoint. This absence is [GAP], not evidence of novelty. The 2026 GM engineering fault-injection article was treated as an industry lead rather than load-bearing academic evidence.

## Decision

**PIVOT.** Kill PHY-MASK/FULL-CAP as broad thesis claims about the superiority of physical faults or universal simulation invalidity. Retain only a bounded, preregistered physical-vs-digital transfer audit with exact printed-marker truth, explicit fault labels, fixed two-shot and quality-threshold baselines, and a useful null-result path. Do not promote to a thesis until a pilot demonstrates a repeatable action-rank inversion or a clearly measured physical mechanism that changes the decision frontier.

PIVOT
