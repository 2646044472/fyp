# Validation Audit: 2026-09-02 Pi 4/Pi 5 alternatives

## Decision investigated

Whether the newly available Raspberry Pi 4 and Raspberry Pi 5 (8 GB), USB-gadget link, and NoIR/RGB camera setup supports a defensible non-palm FYP direction beyond the already scoped physical RGB/NoIR pilot.

## Claim under test

Candidate families considered were: (a) `RAW-JPEG-GATE`, using a same-exposure RAW scalar to decide `retain / reacquire / unknown`; (b) `NOIR-SIDEINFO` and `PROG-RET`, using the second board/camera or progressive packets to reduce transmitted bytes/latency; (c) `IR-CAUSE`, using IR-on as value-of-information for low light versus a named transparent-cover condition; and (d) a plausible alternate, `PI-COLLAB`, in which Pi 4 and Pi 5 exchange frames/features for cooperative marker or object decisions. The test is whether any family has a task, observation, action, constraint, and endpoint not already occupied by direct work and identifiable with the available hardware.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | RAW robustness/edge detection is already studied by Chen, Tai & Ma (AAAI 2024) and ReRAW (CVPR 2025); task-oriented and progressive communication are established by Shao, Zhang & Zhang (arXiv v1 2022) and Hsu et al. (arXiv v1 2026); active sensor choice/diagnosis is already represented in the active README's Lens, AdaptiveISP, AdaptiveAE, Bian et al. chain. | A same-exposure exact printed-marker action test, or a fixed two-world IR intervention, is narrower than these methods. | High for broad mechanisms; medium for narrow endpoint. |
| Exact-claim collision | `PI-COLLAB` is a two-camera edge-analytics system with feature/temporal fusion, the same basic action as TOCOM-TEM Secs. II-III and IV; RCP-Bench (CVPR 2025), Secs. 3.1-3.2, already evaluates multi-device camera corruption and temporal misalignment. `PROG-RET` overlaps progressive edge semantic transmission (Hsu et al., abstract). | The purchased Pi pair could supply a finite, non-personal physical marker benchmark with exact payload oracle and matched joules. No inspected source establishes that exact Pi/RGB/NoIR cell. | Medium-high collision; remaining distinction is empirical only. |
| Boundary/impossibility | Decoder confidence and image quality are not independent truth; a hidden cover/low-light state can produce overlapping RGB/lux observations. NoIR modality and camera swap are confounded. A second board cannot identify which camera is right without an external oracle. | Independent printed payload, fixture-assigned cover/light labels, logged exposure, and held-out sessions make a finite endpoint testable. | High for general guarantees; medium for finite pilot. |

## Assumption and identification audit

1. **Hardware availability:** Pi 4 is confirmed; Pi 5 8 GB is expected tomorrow. NoIR v2 is confirmed; RGB camera, illuminator wavelength/power, rigid mount, lux/power meter, and exact Pi 5 camera revision remain [GAP].
2. **RAW gate:** the protocol in `research/active/13-raw-jpeg-gate-preflight.md` requires a stable RAW10/Bayer path, same-exposure RAW/JPEG pairing, fixed 3A, and measured bytes/time/energy. If any fails, RAW is only an engineering note.
3. **Two-world IR test:** `IR-CAUSE` is identifiable only as a named low-light versus transparent-cover pair with labels assigned before capture. If the RGB/metadata prefix overlaps and the best action differs, no passive router can certify the cause; report non-identifiability.
4. **Two-board collaboration:** Pi 4/Pi 5 agreement is not truth. It needs an independent payload oracle; disagreement cannot identify the correct result. The boards also have different sensor modalities if one is NoIR, so a modality effect is confounded with a device effect.
5. **Ethics/data:** use non-personal printed targets. Palm data remain a control/development resource, not a new thesis direction.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Chen, Tai & Ma, *RAW Image Enhancement for Object Detection in Harsh Environments*, AAAI 2024, Vol. 38(2), pp. 1063-1071, DOI https://doi.org/10.1609/aaai.v38i2.27867 | RAW detector pipeline and RAW Corruption Benchmark | Detection mAP under harsh environments, including LOD-Snow; reports +13.9 mAP | Kills “RAW is generally more robust/useful on edge” | Leaves only the narrow same-exposure marker sufficiency test, not a RAW method claim. |
| Berdan et al., *ReRAW: RAW Image Reconstruction for Efficient Object Detection*, CVPR 2025, pp. 11833-11843, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_RAW_Image_Reconstruction_for_Efficient_Object_Detection_CVPR_2025_paper.html | RAW input/reconstruction for edge detection | Detection accuracy and efficiency | Kills RAW edge-efficiency novelty | Leaves a bounded decoder/action audit. |
| Shao, Zhang & Zhang, *Task-Oriented Communication for Edge Video Analytics*, arXiv v1 2022-11-25, https://arxiv.org/abs/2211.14049, Secs. I, II, III, IV, V | Multi-camera video, feature extraction, temporal entropy side information, server fusion | Rate-performance tradeoff for occupancy and object detection; Sec. IV reports bitrate/accuracy | Directly occupies Pi4/Pi5 feature/temporal collaboration and side-information claims | Leaves only a fixed printed-marker physical transfer/negative benchmark. |
| Hsu, Cheng & Papagianni, *Progressive Semantic Communication for Efficient Edge-Cloud VLMs*, arXiv v1 2026-04-29, https://arxiv.org/abs/2604.26508, abstract | Progressive visual-token layers over bandwidth-constrained link | Edge-cloud latency versus semantic consistency at 1 Mbps | Directly overlaps `PROG-RET`'s progressive stopping/semantic transmission | Leaves a control experiment using JPEG/ROI/code-only; no codec thesis. |
| Du et al., *RCP-Bench: Benchmarking Robustness for Collaborative Perception Under Diverse Corruptions*, CVPR 2025, pp. 11908-11918, https://openaccess.thecvf.com/content/CVPR2025/html/Du_RCP-Bench_Benchmarking_Robustness_for_Collaborative_Perception_Under_Diverse_Corruptions_CVPR_2025_paper.html, Secs. 3.1-3.2 | Multi-device camera inputs; 14 camera corruptions, five severities, global/ego/CAV interference | Robustness of collaborative detectors under corruption and temporal misalignment | Kills generic “two Pi cooperative camera robustness” benchmark/method | A non-personal exact-marker cell can be a small replication appendix only. |
| Ren, Lensgraf & Quattrini Li, *Improving the Perception of Visual Fiducial Markers in the Field using Adaptive Active Exposure Control*, arXiv v1 2024-04-18, https://arxiv.org/abs/2404.12055, Secs. 1-4 | Active exposure control for fiducial markers under harsh illumination | Marker localization under field lighting against AEC/GEC | Kills a new adaptive exposure/marker router | Leaves fixed exposure controls in the physical pilot. |

## Strongest simple baseline

For communication: transmit the exact decoded code (or ROI JPEG) rather than raw/feature/progressive packets; compare against fixed two-shot capture. For sensing: fixed RGB-then-NoIR+IR two-shot, scalar brightness/blur/IR-ratio thresholds, and always-reacquire. These controls are cheaper, easier to audit, and likely Pareto-optimal on a static printed target. Any learned router or codec must beat them after Pi CPU, bytes, latency, and joules are charged.

## Contrarian result

The two boards add useful instrumentation but do not by themselves create a new research object. Pi 4/Pi 5 collaboration is likely a systems demo; a board-agreement result cannot certify scene truth. `RAW-JPEG-GATE` and `NOIR-SIDEINFO` are credible feasibility preflights but broad claims are directly occupied. `IR-CAUSE` has the clearest bounded research question because it can return a positive held-out action-rank inversion or a principled two-world non-identifiability/null result. A second plausible direction, `PI-COLLAB`, should be avoided as a thesis unless a new independent oracle or nonstandard endpoint is introduced.

## Feasibility audit

- Pi 4 + NoIR already captures and serves the debug UI; Pi 5 can be added as a second node.
- Required additions for the finite pilot: rigid mount, repeatable printed targets, transparent-cover fixture, safe IR illumination, and preferably inline USB power measurement. A lux meter is optional logging, not an information guarantee.
- RAW requires Camera Module 3/selected API capability; NoIR v2 raw support and same-request pairing must be measured, not assumed.
- At least three independent sessions and held-out lamp/cover cells are needed. With fewer, the result is unresolved rather than positive.
- No personal biometric capture is needed; do not use users' palms for the research endpoint.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Task-oriented multi-camera feature/temporal communication is established | [K] | Shao et al., arXiv v1 2022-11-25, https://arxiv.org/abs/2211.14049 | Sec. I contributions, Sec. II system model, Sec. III-A/B, Sec. IV, Sec. V | Simulation/edge analytics tasks, not Pi marker hardware. |
| Progressive edge visual transmission is established | [K] | Hsu et al., arXiv v1 2026-04-29, https://arxiv.org/abs/2604.26508 | Abstract and implementation description | VLM semantic consistency, not exact marker decoding. |
| Collaborative camera-corruption benchmarking is established | [K] | Du et al., CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Du_RCP-Bench_Benchmarking_Robustness_for_Collaborative_Perception_Under_Diverse_Corruptions_CVPR_2025_paper.html | Secs. 3.1-3.2 (PDF pp. 11910-11911) | Autonomous-driving datasets and simulated/bench corruptions. |
| RAW broad robustness/edge detection is occupied | [K] | Chen et al., AAAI 2024, DOI above; Berdan et al., CVPR 2025 | AAAI pp. 1063-1071; CVPR pp. 11833-11843 | Does not test exact printed markers. |
| IR intervention can remain a finite value-of-information test | [C]/[GAP] | `research/active/09-physical-transfer-pilot-protocol.md`, `11-cross-device-action-rank-pilot.md` | Protocol sections “Two-world check”, “Promotion and kill criteria” | No inspected paper establishes the Pi-specific effect; independent physical labels are mandatory. |

## Queries and failed searches

- `site:arxiv.org RAW JPEG exact marker transmission edge camera raw 2025` (found broad RAW detection/reconstruction, no exact Pi marker paper).
- `site:openaccess.thecvf.com synthetic real corruption proxy physical sensor robustness 2025` (found RCP-Bench/CNS-Bench; broad proxy/benchmark family occupied).
- `site:arxiv.org progressive visual transmission task-oriented communication edge 2025` (found TOCOM-TEM and progressive VLM communication).
- `site:arxiv.org NoIR camera transparent cover infrared marker detection` (no primary source establishing the exact Pi NoIR/transparent-cover endpoint; absence is not novelty evidence).

## Decision

Do not promote a new generic non-palm mechanism. Keep `IR-CAUSE` (and, secondarily, `RAW-JPEG-GATE`) as bounded preflights with explicit kill criteria. Treat `PI-COLLAB`, `NOIR-SIDEINFO`, and `PROG-RET` as engineering/negative controls unless a held-out physical experiment demonstrates an unexplained action-cost effect.

PIVOT
