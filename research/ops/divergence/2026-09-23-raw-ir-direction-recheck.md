# Divergence Packet: 2026-09-23 RAW-JPEG-GATE and IR-CAUSE recheck

## Decision investigated

Re-evaluate the two strongest hardware-adjacent candidates using the current
charter, candidate register, prior validation packets, primary papers, and
Raspberry Pi documentation. The question is not whether either can produce a
working Pi demo. It is whether a finite pilot could support an undergraduate
FYP claim that is more than an implementation appendix.

**Short decision:** neither candidate is promoted. `RAW-JPEG-GATE` remains
`HOLD` as a capability-gated, finite action-sufficiency study. `IR-CAUSE` is
`PIVOT`: its broad mechanism is killed by direct active-diagnosis and
adaptive-acquisition neighbors; only a narrow physical value-of-information
pilot with a deliberately useful non-identifiability result survives.

## Search boundary

The audited candidate definitions were frozen as follows:

- **RAW-JPEG-GATE:** after one exposure of a printed maintenance marker, use a
  scalar from the same-exposure Bayer/RAW stream to choose `retain`, `unknown`,
  or `reacquire`. Compare against JPEG luma/blur/saturation, decoder
  confidence, a combined JPEG score, fixed two-shot/always-reacquire, and
  matched bytes, latency, and joules. The endpoint is exact payload equality,
  not generic image quality or object-detection AP.
- **IR-CAUSE:** after an ambiguous visible capture, decide whether an IR-on
  observation adds enough information to change the same `retain`, `unknown`,
  or `reacquire` action for two fixture-assigned worlds: clean low visible
  light versus the same target behind a declared transparent cover/film. The
  endpoint is action loss on exact payload truth, not a general cause label,
  camera-health diagnosis, or modality-selection method.

The search was limited to primary or official records available by
2026-09-23. I inspected the current active definitions in
`research/active/01-candidate-register.md`,
`research/active/13-raw-jpeg-gate-preflight.md`, and
`research/active/14-ir-cause-working-prospectus.md`, plus
`research/ops/validation/2026-09-03-ir-cause-raw-jpeg-gate-validation.md` and
`research/ops/validation/2026-08-31-round15-systems-raw-validation.md`.

## Recent-paper limitation map

### RAW-JPEG-GATE

1. **RAW is already an active vision representation, not an unoccupied edge
   idea.** Chen, Tai and Ma use RAW characteristics and a RAW Corruption
   Benchmark for harsh-environment object detection, with mAP as the endpoint
   ([KILL] for “RAW is generally more robust”). Berdan et al. reconstruct
   sensor-specific RAW and train compact edge object detectors, again with
   detection accuracy/efficiency as the endpoint ([KILL] for RAW restoration
   or generic edge-RAW claims).
2. **Task-aware RAW processing is an occupied mechanism family.** The 2026
   TA-ISP paper learns a compact RAW-to-RGB, task-oriented representation and
   reports AP, parameter count, FLOPs, and latency for detection and
   segmentation. A learned RAW quality score, adaptive ISP, or task-aware
   representation would collide directly. The residual candidate is only a
   non-learning, same-exposure, exact-marker sufficiency test.
3. **RAW/JPEG itself is an active compression target.** Raw-JPEG Adapter
   transforms RAW before JPEG and evaluates reconstruction fidelity at matched
   bitrates. This does not use the proposed retain/reacquire action, but it
   kills a claim that merely preserves RAW information under a constrained
   JPEG link.
4. **The official Pi stack makes the pilot plausible but also exposes the
   main feasibility risk.** Picamera2 supports main, lores, and raw streams,
   but queued frames can precede a capture request by up to a frame period;
   raw formats and sensor modes must be queried per camera. Therefore
   “RAW and JPEG from one exposure” is not established by nominal support.

### IR-CAUSE

1. **Active intervention for hidden perception faults is already formalized.**
   Han et al. formulate passive and active fault detection/isolation, treat
   control inputs as interventions, define effective information, and select
   actions with a causal-bandit/MCTS procedure. This directly occupies the
   general “IR reveals the cause” or “choose an informative next observation”
   framing.
2. **Screen/confirm/escalate under edge cost is already a direct action
   pattern.** Bian et al. use cheap screening, high-information confirmation,
   uncertainty/OOD escalation and a watchdog under resource constraints.
   Changing the sensor to RGB/NoIR and the endpoint to a printed marker does
   not by itself create a new method.
3. **Passive optical health monitoring is also occupied.** Ma et al. use a
   clean-only reference, luminance/gradient statistics, a streaming state
   machine, false-alarm controls, and camera-disjoint threshold tests for
   lens occlusion and photometric transitions. This kills passive
   contamination/health monitoring as the IR contribution.
4. **Adaptive camera/exposure routing is occupied.** Lens selects camera
   parameters under capture cost, while AdaptiveAE selects sequential exposure
   actions for HDR quality/motion/noise. A generic IR-on policy, exposure
   router, or adaptive sensing claim would be a reimplementation or small
   endpoint substitution.
5. **The remaining distinction is empirical and narrow.** A preassigned
   transparent-cover cell, an independently registered exact payload, and a
   fixed action-loss comparison could still answer whether this particular
   intervention changes the action frontier. That is a bounded apparatus
   study, not a causal-diagnosis framework.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work and collision | Falsification / kill test | Feasibility and thesis status |
| --- | --- | --- | --- | --- | --- |
| RAW-JPEG-GATE | A disconnected curator must decide whether to retain a printed maintenance indicator. False retain corrupts a handover; reacquisition costs time, storage and energy. | At fixed false-retain target and matched cost, a scalar from the same-exposure RAW stream improves the `retain/unknown/reacquire` frontier over the best JPEG-only evidence and fixed reacquisition. | Chen AAAI 2024, ReRAW CVPR 2025, TA-ISP CVPR 2026 and Raw-JPEG Adapter occupy RAW robustness, RAW edge perception, task-aware ISP and RAW/JPEG representation preservation. Exact marker-action endpoint remains [GAP], so this is not killed outright. | Kill if no stable RAW mode; pairing is not proven; JPEG/decoder confidence ties; fixed two-shot or always-reacquire is Pareto-optimal; RAW unpacking/storage/latency/energy removes the gain; effect fails on a held-out lamp/material/session. | Existing Pi/camera path can run a finite pilot. However, until Gate 0 and matched-cost pilot pass, it is a preflight or negative appendix, not a defensible thesis. **HOLD**. |
| IR-CAUSE | A weak-network maintenance node decides whether an ambiguous optical record is sufficient. Wrong retention causes a bad handover; unnecessary extra capture consumes operator time and energy. | For two independently staged physical worlds, one IR-on intervention reduces exact-payload action loss beyond passive quality, IR ratio, fixed two-shot, conservative escalation and always-reacquire at matched cost. | Han arXiv 2025 occupies active counterfactual FDI; Bian Sensors 2026 occupies screen/confirm/escalate acquisition; Ma arXiv 2026 occupies passive optical health monitoring; Lens/AdaptiveAE occupy adaptive camera action. | Kill if fixed two-shot/always-reacquire dominates; IR ratio or passive quality ties; cover/light labels are not independent; matched worlds remain observationally overlapping with different optimal actions; result disappears under remount or held-out cover/lamp. | Hardware is plausible, but the causal story and generic adaptive mechanism are not. Only the finite endpoint plus a non-identifiability/null result is defensible. **PIVOT**. |

## Exact task/action/endpoint collision audit

| Source | Inputs and allowed action | Endpoint actually evaluated | Consequence for candidates |
| --- | --- | --- | --- |
| Chen, Tai & Ma, *Guiding a Harsh-Environments Robust Detector via RAW Data Characteristic Mining*, AAAI 2024, Vol. 38(2), pp. 1063-1071 | RAW-derived characteristics and detector pipeline | Object-detection mAP on harsh-environment/LOD data | Kills broad RAW robustness language; does not establish exact-marker action sufficiency. |
| Berdan et al., *ReRAW*, CVPR 2025, pp. 11833-11843 | RGB-to-RAW reconstruction, then compact RAW detector training | RAW reconstruction quality and downstream object-detection accuracy/efficiency | Kills RAW restoration or generic edge-RAW contribution; marker retain/reacquire remains a different endpoint. |
| Chen et al., *Task-Aware Image Signal Processor for Advanced Visual Perception*, CVPR 2026, pp. 33672-33681 | RAW input and learned RAW-to-RGB task-oriented representation | Detection/segmentation AP, parameters, FLOPs and latency | Kills learned/task-aware RAW representation or ISP framing. A fixed scalar action audit is still narrower. |
| Afifi, Zhang & Brown, *Raw-JPEG Adapter*, arXiv:2509.19624v1, 2025-09-23 | RAW, invertible pre-processing, JPEG compression and decoder-side reconstruction | PSNR/SSIM/MS-SSIM, compression ratio/BPP and reconstruction fidelity | Kills RAW/JPEG compression as the contribution. It does not decide retain/reacquire from a same-exposure scalar. |
| Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv:2509.18460v1, 2025-09-22 | Perception outputs, fault hypotheses and control-input interventions | Fault detection/isolation and effective information; active versus passive FDI | Kills IR-CAUSE as general causal diagnosis or informative-action selection. Leaves only a fixture-specific intervention test. |
| Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, 2026-08-10 | Cheap screen, confirmation acquisition, uncertainty/OOD state and watchdog | Fault-warning action under activation/latency/resource constraints | Kills generic screen/confirm/escalate IR acquisition. Different sensor stack does not remove action-family collision. |
| Ma, Yan & Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions for Camera Tamper Monitoring*, arXiv:2607.14760v1, 2026-07-16 | Clean reference, luminance/gradient statistics and streaming state machine | Recall/FPR, false-alarm-constrained occlusion/transition detection and camera-disjoint threshold transfer | Kills passive optical cause/health monitoring; active IR increment remains an empirical [GAP]. |
| Baek et al., *Lens: Adaptive Camera Sensor for Vision Models*, arXiv:2503.02170v3, 2026-05-19 | Unlabelled image/model state and camera-parameter actions | Vision quality versus capture-time/parameter trade-off | Kills generic preview-to-camera-action routing. |
| Xu et al., *AdaptiveAE: An Adaptive Exposure Strategy for HDR Capturing in Dynamic Scenes*, ICCV 2025, pp. 25176-25185 | Sequential ISO/shutter/frame actions | HDR quality, motion and noise under exposure constraints | Kills adaptive exposure/burst as the contribution; fixed IR intervention remains only a task-specific audit. |
| Raspberry Pi, `rpicam-raw` documentation, accessed 2026-09-23 | Raw Bayer output and selectable sensor modes | Software/hardware format contract, not a research endpoint | Supports a capability preflight only; it does not prove stable purchased-unit pairing. |
| Raspberry Pi, *Picamera2 Manual*, current PDF accessed 2026-09-23, Sec. 4.2.2 and pp. 16-18, 81-82 | Main/lores/raw streams, queued frames, raw formats, sensor modes and metadata | Capture/configuration behavior | Confirms the exact measurements required: queue policy, sensor format, exposure/gain/WB, black levels, frame IDs and pairing. |
| Raspberry Pi Camera Module 3 product brief, RP-008151-DS, 2025-10-06, p. 3 | Standard/NoIR optical variants and nominal RAW10 capability | Product specification | Supports hardware hypothesis only; not evidence of action benefit or measured pairing. |

## Top two formalizations

### RAW-JPEG-GATE

- **[D] Decision:** `d ∈ {retain, unknown, reacquire}` after one exposure.
- **[A] Allowed observations/actions:** JPEG-derived scalars and, for the
  candidate, a scalar from a proven same-exposure RAW stream; no future frame,
  payload oracle, or offline cell label may enter the online decision. The
  action may request one reacquisition but cannot inspect the answer before
  logging the decision.
- **[T] Target:** independently registered exact payload `y` for a declared
  marker family and physical cell `c`; fixed loss weights false-retain more
  heavily than unknown and charges bytes, wall time and joules separately.
- **Observable outcome:** held-out risk-coverage/action frontier, false-retain,
  unknown rate, reacquisition rate, bytes, processing latency, capture latency,
  and joules, with confidence intervals by session and blocked light/material
  cell.
- **Counterexample:** RAW and JPEG carry no incremental decision information,
  or RAW changes exposure/timing so the paired comparison is invalid. A null
  or cost-dominated result is the required negative-result path.
- **Negative-result value:** establishes only that JPEG evidence or fixed
  reacquisition is sufficient for this declared marker/hardware path; it must
  not be generalized to RAW in other cameras/tasks.
- **Finite-pilot gate:** first prove raw mode, Bayer format, black/white levels,
  frame identity, pairing, exposure/gain/WB logs, storage rate and energy on
  repeated static captures. Only then run held-out action evaluation. Without
  both gates, the result is an engineering appendix.

### IR-CAUSE

- **[D] Decision:** `d ∈ {retain, unknown, reacquire}` or, in the diagnostic
  sub-analysis, `cause ∈ {low-light, transparent-cover, unknown}`. The thesis
  endpoint must remain the action decision; the cause label is never treated
  as ground truth merely because IR ratio changes.
- **[A] Allowed observations/actions:** a visible/RGB prefix, logged exposure,
  gain, WB and geometry, then one declared IR-on intervention or no intervention.
  The policy cannot use the fixture label, exact payload, or future frame.
- **[T] Target:** fixture-assigned cell and independent exact-payload oracle;
  cells are assigned before capture and held out by lamp/cover placement or
  material lot. Cost includes capture, processing, latency and energy.
- **Observable outcome:** incremental action-risk frontier versus fixed RGB,
  fixed NoIR+IR, fixed RGB-then-NoIR+IR, passive quality, IR-ratio, random,
  conservative one-extra-capture and always-reacquire controls.
- **Counterexample:** construct clean-low-light and transparent-cover worlds
  with the same permitted pre-intervention observation and different optimal
  actions. If IR-on also produces overlapping distributions, the cause is not
  identifiable under the declared apparatus. This is a scientifically useful
  negative result, not permission to add a larger classifier.
- **Negative-result value:** separates “the intervention has no incremental
  value” from “the proposed cause cannot be identified from the available
  observations.” That distinction is stronger than reporting a low classifier
  accuracy, but it is still a finite physical boundary result.
- **Finite-pilot gate:** independent cell assignment, independent payload
  truth, fixed two-shot and always-reacquire controls, logged 3A/geometry and
  measured power. If any is missing, the result is a demonstration or
  replication, not a thesis claim.

## Comparison and recommendation

| Criterion | RAW-JPEG-GATE | IR-CAUSE |
| --- | --- | --- |
| Story fit | Concrete maintenance-record decision, but narrow and less aligned with the current Palm Payment route. | Same maintenance-record story, with a clearer reason for a second observation, but still separate from the committed Palm route. |
| Mechanism collision | High for broad RAW quality/robustness, moderate for exact marker-action sufficiency. | Very high for causal diagnosis, adaptive sensing and screen/confirm; moderate only for the named physical endpoint. |
| Independent truth | Exact printed payload is feasible; RAW/JPEG same-exposure identity is the central risk. | Exact payload is feasible; physical cover/light assignment and causal interpretation are the central risks. |
| Strongest baseline | JPEG quality/decoder controls plus fixed two-shot/always-reacquire. | Fixed two-shot/always-reacquire plus IR ratio and passive quality. |
| Negative-result strength | Good finite sufficiency result if the pair is valid and costs are measured. | Good non-identifiability/null result if matched worlds and intervention response are independently controlled. |
| Undergraduate feasibility | Capability preflight is cheap; a thesis needs extra measurement and a later held-out study. | Hardware is feasible; independent physical labels and controls make the pilot methodologically heavier. |
| Defensible now? | No. **HOLD** pending capability and matched-budget gates. | No as currently framed. **PIVOT** to finite value-of-information/non-identifiability study, otherwise kill. |

The Pareto choice is not to select a winner before data. `RAW-JPEG-GATE` has
the cleaner payload truth and weaker mechanism collision, but its decisive
same-exposure capability is unverified. `IR-CAUSE` has a stronger negative
result and a more explicit intervention, but its positive mechanism is already
occupied and its physical “cause” is easy to confound. Neither can be a
defensible FYP merely because a finite pilot was run; the pilot must first
survive its own falsification gate and then demonstrate an action-level result
that simple controls do not reproduce.

## Evidence ledger

| Claim | Label | Primary source/version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| RAW detector/RAW corruption work occupies broad RAW robustness. | [KILL] | Chen, Tai & Ma, AAAI 2024, https://doi.org/10.1609/aaai.v38i2.27867 | Official record and paper pp. 1063-1071; abstract, method and experiments | Detection mAP, not marker action. |
| RAW reconstruction and compact edge detection are occupied. | [KILL] | Berdan et al., CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_RGB-to-RAW_Image_Reconstruction_via_Stratified_Sampling_for_Efficient_Object_CVPR_2025_paper.html; PDF https://openaccess.thecvf.com/content/CVPR2025/papers/Berdan_ReRAW_RGB-to-RAW_Image_Reconstruction_via_Stratified_Sampling_for_Efficient_Object_CVPR_2025_paper.pdf | Abstract; Secs. 1-2, 3, 4-5; pp. 11833-11843 | Object detection and reconstruction; exact-code action remains different. |
| Task-aware RAW-to-RGB edge perception is occupied. | [KILL] | Chen et al., CVPR 2026, https://openaccess.thecvf.com/content/CVPR2026/html/Chen_Task-Aware_Image_Signal_Processor_for_Advanced_Visual_Perception_CVPR_2026_paper.html; PDF https://openaccess.thecvf.com/content/CVPR2026/papers/Chen_Task-Aware_Image_Signal_Processor_for_Advanced_Visual_Perception_CVPR_2026_paper.pdf | Abstract; Secs. 1-4; Sec. 5 conclusion; pp. 33672-33681 | Kills learned task-aware ISP framing, not a finite scalar sufficiency test. |
| RAW/JPEG compression is an occupied endpoint. | [KILL] | Afifi, Zhang & Brown, arXiv:2509.19624v1, 2025-09-23, https://arxiv.org/abs/2509.19624 | Abstract; Secs. 1-3; Sec. 4.1; Sec. 5 conclusion | Their endpoint is reconstruction fidelity/BPP, not retain/reacquire. |
| Active counterfactual perception-fault diagnosis is occupied. | [KILL] | Han et al., arXiv:2509.18460v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Abstract; Sec. 1; Secs. II-V; Sec. VI experiments; Sec. VII conclusion | Robot exploration and simulated faults, but action/diagnosis mechanism collides. |
| Resource-aware screen/confirm/escalate acquisition is occupied. | [KILL] | Bian et al., Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Secs. 1, 3.1, 5.1, 6 and 8 | Different sensor stack; direct action-family neighbor. |
| Passive optical health/occlusion monitoring with false-alarm controls is occupied. | [KILL] | Ma, Yan & Wu, arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Secs. I-VIII, X-XIII; Supplementary XII | Active IR increment not established by this source. |
| Adaptive camera action and adaptive exposure are occupied. | [KILL] | Baek et al., Lens, arXiv:2503.02170v3, 2026-05-19, https://arxiv.org/abs/2503.02170; Xu et al., AdaptiveAE, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Lens Secs. 3.1-3.2, 4-5; AdaptiveAE Secs. 3.3-3.4 and pp. 25176-25185 | Kills generic routing, not the finite named apparatus. |
| Picamera2 raw streams and queue behavior require explicit pairing controls. | [K] | Raspberry Pi, *Picamera2 Manual*, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf | Sec. 4.2.2; pp. 16-18; pp. 81-82; raw stream/sensor configuration and metadata tables | Current PDF was accessed 2026-09-23; exact installed version remains [GAP]. |
| Pi raw capture and Camera Module 3 nominal modes are documented. | [K] | Raspberry Pi `rpicam-raw`, https://www.raspberrypi.com/documentation/computers/camera/rpicam_raw.html; Camera Module 3 product brief RP-008151-DS, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | `rpicam-raw` raw-output/mode documentation; product brief p. 3 | Official website was Cloudflare-gated during direct retrieval; URLs and claims were cross-checked against the existing official-record packet. Nominal capability is not measured pairing. |
| Exact RAW incremental value for Pi printed-marker action is established. | [GAP] | Proposed `RAW-JPEG-GATE` pilot | No inspected primary source has this exact Pi 5, same-exposure, exact-payload, matched-cost endpoint | Retrieval gap is not novelty evidence. |
| IR-on identifies the two proposed physical worlds and improves action risk. | [GAP] | Proposed `IR-CAUSE` pilot | No inspected primary source establishes this exact RGB/NoIR, cover/low-light, exact-payload endpoint | Must allow non-identifiability and null outcomes. |

## Queries and failed searches

Queries run or rechecked on 2026-09-23:

- `RAW JPEG exact code retain reacquire edge camera action cost`
- `RAW image quality saturation SNR JPEG decoder confidence edge device`
- `RAW JPEG task-aware ISP object detection edge 2025 2026`
- `Raw-JPEG Adapter Afifi Zhang Brown arXiv`
- `ReRAW RGB-to-RAW efficient object detection edge CVPR 2025`
- `Task-Aware Image Signal Processor RAW CVPR 2026`
- `active infrared intervention camera fault diagnosis information gain`
- `counterfactual fault diagnosis robot perception intervention 2025`
- `resource-aware active sensor acquisition screen confirm edge fault warning`
- `lens occlusion photometric camera health monitoring clean reference 2026`
- `adaptive camera exposure modality selection edge cost 2025`
- `Raspberry Pi rpicam-raw RAW10 Camera Module 3 Picamera2 raw stream queue`
- `Picamera2 raw JPEG same capture request exposure metadata`

Failed or insufficient retrievals:

- No primary paper was found that jointly evaluates Pi 5 RGB/NoIR, a
  transparent-cover versus clean-low-light fixture, exact printed-payload
  truth, fixed two-shot controls, and matched joules. This remains [GAP], not
  novelty evidence.
- No primary source was found proving that a RAW stream and JPEG output from a
  purchased Module 3 are same-exposure without frame/request identifiers and
  exposure metadata. Picamera2's queue behavior makes assuming this unsafe.
- No primary source was found proving that IR-on separates the proposed two
  worlds after exposure, white balance, geometry and target reflectance are
  controlled. The observational-overlap counterexample remains live.
- The official Raspberry Pi documentation pages were Cloudflare-gated in one
  direct request; the official Picamera2 PDF and the prior official-record
  packet were available. Any installed software/API version remains [GAP].

## Decision

`RAW-JPEG-GATE`: **HOLD**. It can become a defensible undergraduate FYP only
if the capability preflight proves a reproducible same-exposure RAW/JPEG path,
then a held-out action frontier beats JPEG-only, decoder-confidence,
fixed-two-shot and cost-inclusive reacquisition controls. Otherwise report a
bounded JPEG-sufficiency/null result or engineering appendix.

`IR-CAUSE`: **PIVOT**. Kill its general causal-diagnosis, passive-health and
generic adaptive-sensing claims. Retain only a finite active-IR
value-of-information experiment with independent physical labels, independent
payload truth, fixed controls, matched cost, and an explicit two-world
non-identifiability result. If the experiment is not stable enough to establish
that boundary, reduce it to an appendix.

**Overall: PIVOT**
