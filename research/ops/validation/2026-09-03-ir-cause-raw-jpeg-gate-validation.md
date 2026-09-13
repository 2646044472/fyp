# Validation Audit: 2026-09-03 IR-CAUSE and RAW-JPEG-GATE

## Decision investigated

This narrow validation audit covers only IR-CAUSE and RAW-JPEG-GATE. IR-CAUSE asks whether one IR-on intervention adds identifiable information for a named clean-low-light versus transparent-cover condition. RAW-JPEG-GATE asks whether a scalar from a same-exposure RAW frame improves a printed-marker retain / reacquire / unknown decision over JPEG evidence after RAW cost is charged. This audit does not modify research/active/.

## Claim under test

For IR-CAUSE, the bounded claim is that IR-on reduces exact-marker action loss on two independently labelled physical worlds beyond passive quality, an IR-ratio rule, fixed RGB-then-NoIR+IR two-shot, and always-reacquire at matched capture cost.

For RAW-JPEG-GATE, the bounded claim is that a scalar from one RAW exposure adds held-out information about exact-code failure beyond JPEG luma/blur/saturation and decoder confidence after RAW bytes, unpacking time, latency and joules are included.

No broad causal-diagnosis, camera-health, RAW-quality, object-detection, authentication, safety, or camera-family-transfer claim is accepted.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Active intervention and adaptive acquisition are established by Han et al. (active counterfactual perception diagnosis), Bian et al. (screen/confirm/escalate sensing), Lens (camera parameter selection), AdaptiveAE (sequential exposure), and CM-ASAP (adaptive modality/frame-rate). Passive lens-health monitoring is established by Ma et al.; RAW detection, restoration and uncertainty/quality are established by Chen et al., ReRAW and NTIRE RAW work. | A finite IR-on test with independently assigned cover/light labels and an exact printed payload is narrower than those mechanisms. A same-exposure RAW scalar versus JPEG action-cost test is narrower than RAW restoration or object detection. This is a protocol endpoint distinction, not component novelty. | High collision for broad mechanisms; medium for finite endpoints. |
| Exact-claim collision | IR-CAUSE as general cause diagnosis collides with Han, Bian and Ma. RAW-JPEG-GATE as a claim that RAW is generally more reliable collides with Chen, ReRAW and NTIRE RAW benchmarks. Any new adaptive selector, RAW quality score or Pi deployment is already occupied. | The residual IR claim is only incremental value of one named intervention on a blocked two-world marker task. The residual RAW claim is only whether RAW changes a finite action frontier after cost. No inspected source establishes this exact Pi marker endpoint. | High for broad claims; medium-high collision risk for residual tests. |
| Boundary / impossibility | Clean low light and a transparent cover can be adjusted to produce the same RGB preview, luma/blur, metadata and visible-lux reading while requiring different actions. Passive observations cannot identify the cause. JPEG decoder confidence may already suffice for a fixed marker; RAW may only restate clipping/exposure, and RAW overhead can remove its benefit. | The finite test is identifiable only with preassigned physical labels, independent payload truth, frozen or logged exposure/WB, proven RAW/JPEG exposure pairing, frozen thresholds and held-out cells. A null is a valid negative result. | High for the boundary; empirical gain is [GAP]. |

## Assumption and identification audit

1. The clean-low-light and transparent-cover worlds can be observationally equivalent before the IR intervention. IR-on is not automatically a cause oracle; its response must differ empirically on independently staged worlds.
2. Cover/film/clean state must be assigned before capture by a fixture log or operator. Lux, luma, IR ratio, RAW saturation and decoder confidence are observations, not cause labels.
3. Generate the QR/AprilTag/ArUco payload before capture. Exact payload equality must be checked by an independent decoder or registry. Candidate confidence cannot serve as ground truth.
4. The standard Camera Module 3 has an IR-cut filter while NoIR omits it. RGB/NoIR is a spectral-path change, not a generic camera swap.
5. Raspberry Pi supports multiple-camera operation and software frame alignment, but 3A is not synchronized across cameras. Use a static target; moving claims need an external timing witness and exposure/WB logs.
6. A RAW stream and JPEG stream are not proven same-exposure by close timestamps. Record request/frame identifiers, exposure, gain, frame duration, WB and sensor mode. If pairing fails, downgrade the claim.
7. RAW capability requires recording actual Bayer order, packing, bit depth, black/white levels, frame size, dropped frames and storage rate. Nominal RAW10 support is not proof that the purchased unit and selected API provide a stable usable pair.
8. One Pi 5B and one RGB/NoIR pair support a finite path audit only, not a population or transfer guarantee.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Han et al., A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems, arXiv v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Passive observations plus selected interventions; effective-information action selection | Counterfactual perception-fault diagnosis; abstract and Sec. 1 | Active intervention for hidden perception causes | Kills IR-CAUSE as a general causal framework; leaves a finite marker experiment only. |
| Bian et al., Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning, Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Cheap screen, high-information confirmation, uncertainty/OOD escalation and watchdog | Fault warning under activation and latency cost; Secs. 1, 3.1, 5.1, 6, 8 | Screen/confirm/escalate action under edge budget | Kills generic adaptive IR acquisition; leaves only a bounded replication. |
| Ma, Yan & Wu, Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions, arXiv v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Clean reference, luminance/gradient statistics, state machine and camera-disjoint threshold test | Optical health/occlusion monitoring; Secs. I-VIII, X-XIII, Supplementary XII | Passive optical diagnosis and threshold transfer | Kills passive OPT-WIT, generic contamination monitoring and calibration transport; active IR increment remains [GAP]. |
| Baek et al., Lens: Adaptive Camera Sensor for Vision Models, ICLR 2025, arXiv v3, 2026-05-19, https://arxiv.org/abs/2503.02170 | Unlabelled image/model state selects camera parameters under capture cost | Vision accuracy and capture-time trade-off; Secs. 3.1-3.2, 4-5 | Preview-to-camera-action routing | Kills generic adaptive IR/modality selection. |
| Xu et al., AdaptiveAE, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Sequential ISO/shutter/frame actions under exposure budget | HDR quality, motion and noise; pp. 25176-25185, Secs. 3.3-3.4 | Sequential capture action optimization | Kills adaptive exposure/burst as the contribution. |
| Chen, Tai & Ma, RAW Image-Based Object Detection in Harsh Environments, AAAI 2024, https://doi.org/10.1609/aaai.v38i2.27867 | RAW detection pipeline and RAW Corruption Benchmark | Harsh-environment detection mAP; Vol. 38(2), pp. 1063-1071 | Broad RAW robustness claim | Kills RAW-is-generally-more-robust language; exact-marker gate remains unverified. |
| Berdan et al., ReRAW, CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_Efficient_RAW_Image_Restoration_for_Mobile_Object_Detection_CVPR_2025_paper.html | RAW restoration and mobile detection | Detection accuracy and efficiency; CVPR 2025 method/experiments | RAW edge-deployment benefit | Kills RAW restoration or generic edge-RAW claims. |
| Raspberry Pi, rpicam-raw, accessed 2026-09-03, https://www.raspberrypi.com/documentation/computers/camera/rpicam_raw.html | Raw Bayer capture and sensor modes | Format and capture behavior | Hardware/software capability contract | Leaves feasibility possible, but local mode and cost must be measured. |
| Raspberry Pi, Picamera2 manual, accessed 2026-09-03, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf | Main/JPEG and raw stream configuration; packed/unpacked formats | Stream/request configuration; Sec. 4.2 and request/stream sections | RAW/JPEG implementation path | Leaves implementation possible; exact Module 3 negotiation and pairing remain [GAP]. |
| Raspberry Pi Camera Module 3 product brief, dated 2025-10-06, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | Standard/NoIR optical variants and RAW10 specification | Product specification, p. 3 | Spectral-path difference and nominal RAW10 | Nominal capability only; not measured purchased-unit behavior. |

## Strongest simple baseline

For IR-CAUSE, use fixed RGB -> NoIR+IR two-shot, always-RGB, always-NoIR+IR, always-reacquire, IR-ratio threshold, brightness/blur/decoder-quality router and conservative one-extra-capture escalation. Charge the same capture, latency and joule budget. If fixed two-shot is Pareto-optimal, the adaptive IR action is unnecessary.

For RAW-JPEG-GATE, compare RAW saturation/occupancy/SNR with JPEG luma/blur/saturation, decoder confidence, combined JPEG score, fixed single capture, fixed two-shot and always-reacquire. Freeze thresholds on source cells and report false-retain, unknown, reacquisition, bytes, wall time and joules.

## Contrarian result

The likely IR-CAUSE result is non-identifiability or a null: matched worlds may remain indistinguishable, or fixed two-shot may directly obtain all useful information. The correct output would then be unknown or a bounded action table, not causal diagnosis.

The likely RAW-JPEG-GATE result is that JPEG/decoder confidence or simple luma/blur already controls exact-code failure, while RAW overhead removes any marginal benefit. A positive result would be limited to the declared marker, light and material cells on the purchased path.

## Feasibility audit

- Hardware: The active charter records Pi 5B 8 GB, official RGB and NoIR cameras, IR illuminator and adapter hardware as available [K]. Static capture is feasible. Camera revision, illuminator specification, rigid mount and power instrument remain [GAP].
- RAW: Official documentation exposes Bayer RAW and Camera Module 3 is specified as RAW10 [K]. The preflight must verify actual mode, packing, Bayer order, levels, pairing, dropped frames, storage and energy [GAP].
- Data: Generated printed payloads and inert covers avoid personal data. Independent payload and physical-condition logs are mandatory [K].
- IR labels: Clean versus declared transparent cover is stageable. Generic contamination severity or real camera-health labels are not justified. Equal lux is not equal spectrum, so lux is only a covariate.
- Measurement: A USB power meter may miss fast transients. Do not claim energy optimality until timing alignment and repeatability are measured.
- Schedule: A static pilot with three sessions and held-out light/cover cells fits the December 2026 demo. Promotion requires repeated held-out cells/remounts in 2027 H1. No population claim is feasible.
- Compute/storage: Classical decoding and scalar statistics fit Pi 5. RAW storage and unpacking are potentially dominant and must be charged. RAW reconstruction/restoration training is out of scope and already collision-heavy.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Active intervention for perception-fault diagnosis is established. | [KILL] | Han et al., arXiv:2509.18460v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Abstract and Sec. 1 | Kills general causal framing, not the finite endpoint. |
| Resource-aware screen/confirm/escalate acquisition is established. | [KILL] | Bian et al., Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Secs. 1, 3.1, 5.1, 6, 8 | Different sensor stack; action family overlaps. |
| Passive camera-health and camera-disjoint threshold transfer are established. | [KILL] | Ma et al., arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Secs. I-VIII, X-XIII, Supplementary XII | Active IR increment remains [GAP]. |
| Adaptive camera/exposure actions under cost are established. | [KILL] | Lens, arXiv v3, 2026-05-19, https://arxiv.org/abs/2503.02170; AdaptiveAE, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Lens Secs. 3.1-3.2, 4-5; AdaptiveAE pp. 25176-25185 | Kills generic adaptive IR/exposure routing. |
| Broad RAW robustness and RAW mobile processing are established. | [KILL] | Chen et al., AAAI 2024, https://doi.org/10.1609/aaai.v38i2.27867; Berdan et al., CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_Efficient_RAW_Image_Restoration_for_Mobile_Object_Detection_CVPR_2025_paper.html | Chen pp. 1063-1071; ReRAW method/experiments | Kills broad RAW claims; exact-marker sufficiency remains [GAP]. |
| Official Pi tools expose raw Bayer capture. | [K] | Raspberry Pi docs, accessed 2026-09-03, https://www.raspberrypi.com/documentation/computers/camera/rpicam_raw.html; Picamera2 manual, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf | rpicam raw-output/mode text; Picamera2 Sec. 4.2 and request/stream sections | Actual purchased-unit mode, pairing and throughput remain [GAP]. |
| Camera Module 3 nominally provides RAW10 and standard/NoIR differs by IR-cut filter. | [K] | Raspberry Pi product brief, dated 2025-10-06, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | p. 3 | Nominal specification, not measured behavior. |
| IR-on adds information beyond fixed two-shot and passive controls. | [C] | IR-CAUSE pilot hypothesis | No inspected source establishes it | Requires independent labels and held-out repetitions. |
| Same-exposure RAW scalar improves exact-marker action risk after cost. | [C] | RAW-JPEG-GATE pilot hypothesis | No inspected source establishes it | Must prove pairing and beat all listed baselines. |
| The two-world cause is identifiable from RGB/NoIR plus IR-on. | [GAP] | Proposed IR-CAUSE protocol | Not established before data collection | Matched-observation counterexample remains possible. |
| Purchased Pi 5 Camera Module 3 provides a stable usable RAW/JPEG pair. | [GAP] | Local capability preflight | Not run in this audit | Must be measured before promotion. |

## Queries and failed searches

Queries reviewed on 2026-09-03:

- active illumination counterfactual fault diagnosis robot perception intervention information 2025
- Pi 5 rpicam-raw RAW10 Camera Module 3 Picamera2 raw stream same request JPEG
- RAW image edge detection reliability JPEG quality saturation SNR 2024 2025
- RAW image quality uncertainty saturation camera reliability 2025
- adaptive camera sensor exposure modality selection edge capture cost 2024 2025
- transparent cover low light infrared illumination camera marker diagnosis exact code

No inspected primary source jointly evaluates Pi 5 RGB/NoIR, transparent-cover versus clean-low-light labels, exact printed-payload action loss, fixed two-shot control and matched joules. This is a retrieval gap, not evidence of novelty. The local purchased module was not run during this audit, so exact RAW mode, pairing, levels, storage, dropped frames and energy remain [GAP]. No inspected source proves that IR-on identifies the two proposed worlds after exposure/WB and geometry are controlled.

## Decision

IR-CAUSE: KILL as a general causal-diagnosis, passive camera-health or generic adaptive-sensing thesis. PIVOT only to a finite active-IR incremental-information experiment with independent physical labels, an independent payload oracle, fixed two-shot/always-reacquire/IR-ratio/passive quality baselines and matched cost.

RAW-JPEG-GATE: HOLD only as a capability and matched-budget preflight. Kill or reduce it to an engineering/null appendix if RAW is unstable, pairing cannot be proven, JPEG/decoder/fixed reacquisition ties, or RAW overhead removes the benefit. No broad RAW robustness claim survives.

Overall: HOLD
