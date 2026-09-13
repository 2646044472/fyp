# Validation Audit: 2026-08-31 adaptive sensing and task-aware compression

## Decision investigated

Audit the divergence candidates **NOIR-SIDEINFO**, **PROG-RET**, **TASK-CODEC-NULL**, and the secondary candidates **ROI-QP** and **DCT-QR**. The audit asks whether any candidate survives three novelty rounds and a contrarian feasibility/baseline check on the purchased Raspberry Pi 5B with RGB Camera Module 3, NoIR camera and IR illuminator.

## Claim under test

- **NOIR-SIDEINFO:** for a static printed maintenance indicator, a sequential NoIR image available as decoder-side side information reduces transmitted RGB bytes at the same exact-code success, false-retain risk and total latency/energy as independent JPEG/WebP, ROI crop, and a decoded-code message.
- **PROG-RET:** a deterministic base-layer/enhancement protocol stops after an early layer when the marker is decisively readable and requests enhancement otherwise, reducing expected bytes/latency at a fixed false-retain ceiling against fixed low/high JPEG and progressive JPEG/WebP.
- **TASK-CODEC-NULL:** on small high-contrast printed indicators, a learned task-aware codec gives no statistically significant, cost-inclusive improvement over tuned JPEG/WebP plus ROI crop. This is a bounded negative result, not a universal claim.
- **ROI-QP:** finder-pattern/ROI-aware quantization lowers bytes per exact-code success over uniform JPEG on held-out placement, scale and illumination.
- **DCT-QR:** selected JPEG DCT coefficients can issue `retain / unknown / reacquire` with the same exact-code safety and lower Pi CPU/latency than full decode plus QR.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Decoder-side side information, progressive transmission, task-aware rate allocation, ROI quantization and compressed-domain inference are each established components. Yin et al. ICRA 2024 (DOI 10.1109/ICRA57147.2024.10611242) and D-CAN 2025 (DOI 10.1016/j.dcan.2024.06.001) use multi-view decoder side information; Ge et al. CVPR 2024, pp. 26036-26045, controls task-relevant coded elements; Della Fiore et al. TFIC EUSIPCO 2025, pp. 1382-1386, optimizes OCR text preservation; Tu et al. TOMM 2024, DOI 10.1145/3678471, studies reconstruction-free compressed-domain vision. | No inspected paper jointly uses a Pi 5 RGB/NoIR pair, exact printed payload as the action endpoint, and matched capture/encode/transmit cost. This is only a scoped empirical distinction, not novelty evidence. | High for component collision; medium for the bounded endpoint. |
| Exact-claim collision | **NOIR-SIDEINFO** is very close to Yin/D-CAN: independently encode one view and exploit another at the decoder. Their endpoints are image rate-distortion/reconstruction on KITTI Stereo/Cityscapes, not QR exact-code actions. **PROG-RET** is close to *Deep learning-based image compression for wireless communications* (npj Wireless Technology 2025, DOI/URL below), which reports progressive layers and waiting time, and to Kim et al. *Progressive Learned Image Compression for Machine Perception* (arXiv v1 2025-12-23), which adds adaptive decoding by downstream confidence. **ROI-QP/TASK-CODEC-NULL** overlap TFIC, DMTUIC ECCV 2024 and ICLR 2025 causal task grouping. **DCT-QR** overlaps Tu TOMM 2024 and compressed-domain OCR/vision. | The exact fixed action is `retain / unknown / reacquire` for a known printed payload, with a physical RGB/NoIR observation model and an explicit false-retain ceiling. That endpoint remains [GAP] in the sources inspected; it could still be an application/benchmark rather than a method contribution. | High collision for generic method claims; low-to-medium for the finite marker endpoint. |
| Boundary / impossibility | Side information is useless when NoIR is uncorrelated with RGB under a cover/light cell, when registration error exceeds marker tolerance, or when the receiver must also receive NoIR. Progressive early stopping is unsafe if a low-quality layer yields a plausible but wrong payload and no independently trusted checksum exists. ROI is vacuous when the ROI crop itself costs as many bytes or finder geometry is not available before coding. DCT decisions cannot reconstruct a payload if the retained coefficients discard finder/module detail. | A finite physical test can honestly identify only the byte-risk-latency frontier for declared static cells. It cannot establish a general semantic-compression guarantee, general camera transfer, or causal fault diagnosis. | High for the counterexamples; all broad claims fail the boundary round. |

## Assumption and identification audit

1. **Receiver-side information:** NOIR-SIDEINFO must specify whether the receiver already possesses NoIR. If NoIR bytes are transmitted, count both streams; otherwise the experiment tests a distributed-camera deployment assumption rather than compression alone. [KILL] A claim of RGB-byte reduction that omits NoIR acquisition/transmission cost is not identified.
2. **Sequential registration:** Pi's two cameras are not guaranteed synchronized for 3A or exposure. Static targets are valid; moving targets, flicker and timing claims require an external timing oracle. Registration must be measured with a printed fiducial, not assumed. [K] Raspberry Pi Camera Module 3 product brief, p. 3, distinguishes IR-cut RGB from NoIR; Raspberry Pi camera documentation describes multi-camera operation but does not provide a synchronized-3A guarantee: https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief and https://www.raspberrypi.com/documentation/computers/camera_software.html.
3. **Exact-code oracle:** Use an independently printed payload and post-action decode only for scoring. If the proposed stopping rule uses the ground-truth code or a checksum derived from it, false-retain is leaked and the claim is invalid. A marker finder/decoder confidence is not an independent truth witness. [KILL]
4. **Rate/latency budget:** Compare equal total bytes, capture time, encoder/decoder time and energy. A lower image bitrate with an extra NoIR capture or CNN encoder is not a Pareto gain.
5. **Held-out worlds:** Hold out marker placement/scale, lamp spectrum, transparent cover and low-light cells. Equal RGB luma can correspond to different NoIR utility; a single scene cannot identify side-information value.
6. **Learned baseline reproducibility:** TASK-CODEC-NULL is only credible if a published codec and training/checkpoint are available, or if the null is explicitly a baseline-only study. Re-training a large codec on a tiny marker set risks overfitting and is not required for a minimum FYP.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Yin et al., *Cross View Capture for Distributed Image Compression with Decoder Side Information*, ICRA 2024, pp. 9300-9305, DOI 10.1109/ICRA57147.2024.10611242, https://dblp.org/rec/conf/icra/YinSRDL024 | Multi-view images; primary/side view and decoder cross-view attention | Rate-distortion/MS-SSIM on KITTI Stereo; abstract reports 0.978 at 0.15 bpp | Component and observation collision with NOIR-SIDEINFO | Kills generic “decoder-side second camera compression” novelty. Leaves only finite exact-code/physical-cost endpoint, with synchronization and registration still open. |
| Yin et al., *Learned distributed image compression with decoder side information*, D-CAN 2025, Vol. 11(2), pp. 349-358, DOI 10.1016/j.dcan.2024.06.001, https://www.sciencedirect.com/science/article/pii/S2352864824000683 | Independently encoded image and decoder-only side information | Image reconstruction/rate on KITTI Stereo and Cityscapes; abstract explicitly identifies constrained-device synchronization challenge | Direct conceptual overlap with NOIR-SIDEINFO | Kills a distributed-source-coding method claim. Full ablations were not accessible in this audit [GAP]. |
| *Deep learning-based image compression for wireless communications*, npj Wireless Technology 2025, https://www.nature.com/articles/s44459-025-00019-6 | Progressive learned layers over a simulated Rayleigh wireless channel | Waiting time, robustness and rate; Kodak images; conclusion/future-work discusses broader channels, mobility and edge timing | Direct progressive-transmission overlap with PROG-RET | Kills generic progressive edge communication novelty. Leaves a small deterministic physical marker stopping audit only. |
| Kim et al., *Progressive Learned Image Compression for Machine Perception*, arXiv v1 2025-12-23, https://arxiv.org/abs/2512.20070 | Fine-grained progressive bitstream and confidence-based adaptive decoding | Downstream classification at multiple decode levels | Exact action/control overlap with PROG-RET (adaptive stop based on prediction confidence) | Kills learned adaptive-progressive claim; static exact-code and cost-inclusive negative result remain unverified. |
| Ge et al., *Task-Aware Encoder Control for Deep Video Compression*, CVPR 2024, pp. 26036-26045, https://openaccess.thecvf.com/content/CVPR2024/html/Ge_Task-Aware_Encoder_Control_for_Deep_Video_Compression_CVPR2024_paper.html | Hyperprior features control skip/no-skip coding modes and GOP for detection/tracking | Task rate-accuracy and decoding efficiency | Component collision with ROI-QP/TASK-CODEC-NULL | Kills generic task-aware encoder-control contribution; not a static QR endpoint. |
| Guo et al., *Which Tasks Should Be Compressed Together?*, ICLR 2025, official paper, https://proceedings.iclr.cc/paper_files/paper/2025/hash/27a61686fc5928a43c8211f7da70ac75-Abstract-Conference.html | Task grouping and conditional-entropy representation compression | Multi-task rate/accuracy on Taskonomy-style tasks | Component collision with TASK-CODEC-NULL | Kills causal/task-grouping novelty; leaves a deliberately bounded null on a non-neural marker task. |
| Della Fiore et al., *TFIC: End-to-End Text-Focused Image Compression for Coding for Machines*, EUSIPCO 2025, pp. 1382-1386, https://eusipco2025.org/wp-content/uploads/pdfs/0001382.pdf | Image codec optimized for OCR text loss | OCR text extraction at low bitrates; Secs. I, III-IV; Sec. V reports OCR-module and tuning dependence | Strong exact-task-family collision with ROI-QP/TASK-CODEC-NULL | Kills “compression preserves machine-readable text” as a new claim. QR exact-code and Pi cost remain a narrower endpoint; no assumption of novelty. |
| Tu et al., *[compressed-domain machine vision]*, ACM TOMM 2024, DOI 10.1145/3678471, https://doi.org/10.1145/3678471 | JPEG/compressed features without reconstruction | Machine-vision task accuracy and compute | Direct mechanism collision with DCT-QR | Kills compressed-domain inference method novelty; leaves only whether selected coefficients are actually cheaper for this tiny Pi decoder. |
| Chen et al., *RAW Image-Based Object Detection in Snow*, AAAI 2024, Vol. 38(2), pp. 1063-1071, https://ojs.aaai.org/index.php/AAAI/article/view/27867; Berdan et al., *ReRAW*, CVPR 2025, pp. 11833-11843, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_RGB-to-RAW_Image_Reconstruction_via_Stratified_Sampling_for_Efficient_Object_CVPR_2025_paper.html | RAW/linear representation for detection and edge reconstruction | Detection robustness/rate and RAW-to-RGB reconstruction | Broad RAW/task-aware representation collision if TASK-CODEC-NULL expands to RAW | Kills a broad “RAW is better for edge task compression” story; does not test exact marker bytes on Pi. |

## Strongest simple baseline

The strongest baseline is not another neural codec:

1. Detect/crop the printed marker locally.
2. Transmit the decoded payload plus a short integrity code, or transmit a high-quality ROI JPEG if a human-readable image is required.
3. For uncertainty, use fixed `RGB -> NoIR+IR -> unknown/reacquire` or always-high JPEG.

This baseline can dominate NOIR-SIDEINFO whenever the receiver needs only the code, dominate PROG-RET whenever Wi-Fi latency is below the full-frame budget, and dominate TASK-CODEC-NULL/ROI-QP whenever ROI crop plus tuned JPEG has the same exact-code frontier. Any proposed method must report the constrained case where a receiver genuinely requires pixels and code-only transmission is disallowed.

## Contrarian result

The audit does not support a positive adaptive-compression thesis. **NOIR-SIDEINFO is the only candidate that remains HOLD Amber**, because the exact physical endpoint was not found in inspected sources; this is a search-boundary result, not a novelty claim. **PROG-RET should be PIVOT**, because progressive learned machine compression and confidence-based stopping directly occupy its mechanism. **ROI-QP and DCT-QR are KILL as positive methods** and may survive only as negative/engineering controls. **TASK-CODEC-NULL is HOLD only as a preregistered bounded null**: a statistically powered result that tuned JPEG/ROI beats or ties a published task-aware codec, after counting Pi cost, would be useful; failure to reproduce a codec is not evidence that task-aware compression fails.

## Feasibility audit

- **Hardware:** Pi 5B, RGB Camera Module 3, NoIR and IR lamp suffice for static cells. No extra sensor is needed. A USB power meter is useful but not required for a first bytes/latency gate; purchase only if the pilot shows a real energy tradeoff.
- **Capture:** sequential cameras require a rigid mount, manual/frozen exposure and static printed targets. Record registration error and metadata. Moving scenes, flicker and synchronized-camera claims are out of scope.
- **Data/ethics:** print 20-50 marker layouts, vary distance/angle, lamp/cover/low-light cells; no personal data or production decisions. Independent fixture labels are required for cover/light states.
- **Compute:** JPEG/WebP, ROI crop and progressive chunking are Pi-feasible without training. Learned codec reproduction may need an offline GPU and is optional; a published checkpoint must be frozen before test data.
- **Measurement:** shape a local Wi-Fi link with fixed rate/loss; record bytes, p50/p95 latency, encode/decode CPU time, retries, exact-code error, false-retain, unknown/reacquire and energy if available.
- **Timeline:** a December 2026 demo is feasible for the static pilot and deterministic policies. A learned codec, if retained, must be an optional comparison after the baseline gate; 2027-H1 can add held-out cells and repetitions.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Decoder-side side information is an established distributed-compression mechanism. | [K] | Yin ICRA 2024, DOI 10.1109/ICRA57147.2024.10611242; Yin D-CAN 2025, DOI 10.1016/j.dcan.2024.06.001 | Official records/abstracts; ICRA pp. 9300-9305; D-CAN Vol. 11(2), pp. 349-358 | D-CAN full method/ablations were not fully accessible; scope is still sufficient to kill generic component novelty. |
| Progressive machine-oriented compression and adaptive decode are active direct neighbors. | [K] | npj Wireless Technology 2025, https://www.nature.com/articles/s44459-025-00019-6; Kim arXiv v1 2025-12-23, https://arxiv.org/abs/2512.20070 | npj Introduction/Results/Conclusion; Kim abstract | Simulated channels or classification, not Pi exact-code endpoint. |
| Task-aware/ROI/OCR compression is established. | [K] | Ge CVPR 2024, pp. 26036-26045; Guo ECCV 2024, pp. 1-4 and 10-13; Guo ICLR 2025 official abstract; TFIC EUSIPCO 2025, pp. 1382-1386 | Sections/pages listed above | These papers do not prove a small-marker null; they establish collision risk. |
| Compressed-domain inference is established. | [K] | Tu et al. ACM TOMM 2024, DOI 10.1145/3678471 | Official record/abstract, pp. 1-19 | Full text was partially inaccessible; exact DCT implementation comparison remains [GAP]. |
| RGB and NoIR are distinct optical paths and sequential multi-camera capture is not a synchronized-3A guarantee. | [K] | Raspberry Pi Camera Module 3 product brief, p. 3; Raspberry Pi camera docs | Product brief and multi-camera documentation | Exact camera revision and raw mode remain [GAP]. |
| NoIR side information improves exact-marker rate at matched cost on Pi. | [C] | Candidate hypothesis | No inspected source measures it | Requires preregistered pilot. |
| A deterministic progressive stop rule lowers expected bytes at fixed false-retain. | [C] | Candidate hypothesis | No inspected source measures this physical endpoint | Must compare code-only, fixed-high and progressive JPEG controls. |
| Task-aware learned compression has no cost-inclusive gain on the marker workload. | [C] | Candidate null | No inspected source tests this workload | Do not generalize beyond declared marker/cover/light cells. |
| Any side-information gain is identifiable from one static paired scene. | [KILL] | Counterexample: matched RGB/lux/blur but different cover/material worlds can produce different NoIR utility | Two-world reasoning; no external theorem needed for the finite audit | Requires held-out interventions and independent labels; no causal claim. |

## Queries and failed searches

Queries used: `decoder side information multi-view image compression 2024 2025 edge`; `progressive image compression machine perception 2025`; `task-aware ROI OCR image compression 2024 2025`; `compressed-domain QR OCR DCT coefficients`; `NoIR side information compression`; `QR task-aware JPEG Pi`; `RGB NIR distributed compression edge marker`.

Searches found multi-view codecs, OCR/task-aware codecs, progressive learned compression, RAW representation and compressed-domain vision, but no primary paper jointly evaluating Pi 5 RGB/NoIR, exact printed-code action, and matched bytes/latency/energy. This absence is [GAP], not evidence of global novelty. D-CAN and ACM TOMM full texts were only partially accessible; detailed failure-case comparison remains unresolved.

## Decision

- **NOIR-SIDEINFO: HOLD (Amber).** Run only a capability and matched-budget pilot. Kill if code-only/ROI JPEG/fixed two-shot ties, NoIR must also be transmitted, or registration/coverage removes the gain.
- **PROG-RET: PIVOT (Amber).** Keep as a deterministic stopping benchmark, not a new progressive codec. Kill if fixed-high JPEG or code-only transmission is Pareto-optimal.
- **ROI-QP: KILL as a positive thesis; PIVOT as a negative benchmark.** Existing task-aware/ROI/OCR methods occupy the mechanism family.
- **DCT-QR: KILL as a positive thesis; PIVOT as a low-level control.** Compressed-domain inference is established and Pi speedup may be negligible.
- **TASK-CODEC-NULL: HOLD only as a bounded negative-result protocol.** Promote only if the codec baseline is reproducible and the null is statistically powered and cost-inclusive.

Overall decision: **HOLD**. The next gate is a small static marker pilot measuring registration, bytes, exact-code risk and latency for independent JPEG, ROI JPEG, code-only, fixed two-shot and the NoIR side-information/progressive variants. If simple controls dominate, preserve that negative result and return to the bounded physical IR value-of-information pilot.

HOLD
