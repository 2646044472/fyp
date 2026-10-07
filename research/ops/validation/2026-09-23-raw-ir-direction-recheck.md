# Validation Audit: 2026-09-23 RAW-JPEG-GATE and IR-CAUSE recheck

## Decision investigated

This recheck audits `RAW-JPEG-GATE` and `IR-CAUSE` against the newest available
direction material. The newest 2026-09-23 divergence packet,
`research/ops/divergence/2026-09-23-beyond-palm-residual-divergence.md`, does
not introduce a new RAW or IR claim; it keeps these candidates in the older
physical-intervention branch. The operative candidate definitions are therefore
the 2026-08-31 packet
`research/ops/divergence/2026-08-31-pi5-physical-intervention-divergence-round10.md`,
the 2026-09-03 joint validation
`research/ops/validation/2026-09-03-ir-cause-raw-jpeg-gate-validation.md`, and
the current preflight
`research/active/13-raw-jpeg-gate-preflight.md`.

This file is a validation-only artifact. It does not edit `research/active/` or
`.research/`.

## Claims under test

### RAW-JPEG-GATE

On a declared printed-marker size and light/material cell, a scalar computed
from a same-exposure RAW10 frame lowers exact-code false-retain at a fixed
retry/storage/latency budget relative to JPEG luma/blur/saturation, decoder
confidence, and fixed reacquisition controls. The current preflight explicitly
limits the claim to one purchased Raspberry Pi 5B / Camera Module 3 path and
does not claim general RAW quality, camera health, detection, transfer, or
security.

### IR-CAUSE

For a static printed marker, an optional IR-on capture adds identifiable
information for a declared clean-low-visible-light versus transparent-cover
contrast and improves retain/unknown/reacquire action loss at matched capture,
latency, and energy cost over passive quality, an IR-ratio rule, fixed two-shot,
and always-reacquire. If the two physical worlds have indistinguishable
permitted observations but different best actions, the valid result is a finite
non-identifiability finding, not a cause-diagnosis method.

No general RAW robustness, contamination diagnosis, camera-health, adaptive
sensing, authentication, payment, safety, or cross-camera claim is accepted.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | IR intervention, screen/confirm/escalate acquisition, adaptive exposure and camera-parameter selection are already represented by Han et al., Bian et al., Lens, and AdaptiveAE. Passive optical-health monitoring is represented by Ma et al. RAW detection/restoration and mobile RAW processing are represented by Chen et al. and ReRAW. | The proposed tests use a small Pi path, inert printed payloads, fixture-assigned physical cells, and an action frontier rather than a new model. That is a bounded protocol distinction, not component novelty. | High collision for any method claim; medium confidence that the exact finite endpoint is not directly duplicated in the inspected sources. |
| Exact claim | “IR causes a hidden fault” and “RAW is more reliable” are both killed as broad claims by the direct neighbors above. A policy that selects a second view under budget is also a known action family. | The residuals are: same-exposure RAW scalar versus JPEG-only controls under exact-code action loss; and optional IR-on versus fixed two-shot/always-reacquire under independently staged two-world cells. No inspected source jointly evaluates this exact Pi/marker/cost endpoint. | Medium-high collision risk; the remaining distinction is evaluation scope, not a strong mechanism claim. |
| Boundary / impossibility | A low-light scene and a transparent cover can be staged to match visible observations, and RAW can merely expose the same clipping/exposure information already available to a JPEG quality score. A second capture may be dominated by fixed two-shot or always-reacquire. | A finite experiment is identifiable only with independent physical labels, independent payload truth, frozen controls, proven exposure pairing, held-out cells, and charged capture/processing cost. A null, rank tie, or two-world overlap is a legitimate result. | High confidence in the boundary; empirical incremental value remains [GAP]. |

## Component, exact-claim, and boundary audit

### RAW-JPEG-GATE: same-exposure pairing

The claim requires a RAW scalar and JPEG evidence from the same exposure. A RAW
file and a nearby JPEG are not enough: close timestamps can represent different
requests, different sensor frames, or different 3A states. The experiment must
record a request/frame identifier or an equivalent pipeline witness, sensor
mode, frame duration, exposure time, analogue gain, digital gain if exposed,
white balance, and capture timestamps. A static target does not repair a
pairing failure; it only hides motion as a confound.

The official Pi documentation establishes that raw Bayer streams and camera
controls are available, but it does not by itself establish that the purchased
Camera Module 3 and selected API emit a JPEG and RAW file from one exposure.
`rpicam-raw` output capability and Picamera2 stream configuration are capability
facts, not pairing evidence. If pairing cannot be proven, the exact claim must
be downgraded to “RAW versus JPEG under sequential capture,” with exposure and
3A treated as a separate confound; it cannot be promoted as a same-exposure
information test.

### RAW-JPEG-GATE: independent payload truth

The payload registry must be generated and frozen before capture. Exact code
validity must come from an independent registry/decoder or a separately
recorded clean-reference procedure. Candidate decoder confidence is an input
to one baseline, never ground truth. The physical condition log must likewise
be assigned before capture; saturation, luma, blur, decoder confidence and RAW
statistics are observations, not labels for “bad” or “transparent cover.”

The current preflight’s QR/AprilTag registry and held-out cell design is
necessary. It is not sufficient if the same decoder supplies both a quality
feature and the target label, or if threshold selection reads held-out payload
equality. Any such leakage makes false-retain improvement circular.

### RAW-JPEG-GATE: baselines and ordinary intervention

The strongest baseline is not JPEG luma alone. It is the best frozen JPEG-only
policy made from luma, blur, saturation, decoder confidence, and their combined
score, compared with:

1. fixed single-capture retain;
2. fixed two-shot / always-reacquire;
3. conservative one-extra-capture escalation;
4. an offline oracle used only to report the action frontier.

The two-shot baseline is important because RAW and JPEG are not competing
actions if both are captured from the same request: the ordinary intervention
may simply be taking a second ordinary JPEG. If fixed two-shot reaches the same
false-retain target with fewer bytes, less unpacking, lower latency, and lower
energy, a RAW scalar is not the cause of the gain. If the system can choose
whether to acquire more evidence, `always-reacquire` must also be reported even
when it is operationally wasteful; otherwise a selective policy can win only
because the comparison omits the conservative option.

The predeclared loss `10*FR + 1*U + 0.1*J` is usable only if `FR`, `U`, and `J`
are defined before results are read and latency is reported separately. The
loss must not hide a large RAW storage or wall-time penalty behind a small
normalized joule coefficient.

### RAW-JPEG-GATE: RAW overhead and fairness

The cost ledger must include RAW bytes written, filesystem/storage rate,
unpacking, scalar computation, JPEG encoding if both products are produced,
capture wall time, dropped frames, idle/capture/process power, and any extra
buffering. A RAW statistic computed after writing a full RAW file is not
comparable to a JPEG score if the JPEG policy is allowed to operate on the
compressed stream while RAW incurs a storage and unpacking round trip. Conversely,
if both are available in memory from one request, that exact implementation
must be stated and the byte/storage cost still reported.

Thirty static captures are enough for a capability preflight, not for a thesis
effect claim. The proposed held-out improvement must repeat across independent
sessions and a held-out light/material cell, with confidence intervals at the
declared false-retain target. A single camera, marker family, and mount support
only a finite apparatus result.

### IR-CAUSE: independent labels and two-world identifiability

“Low visible light” and “transparent cover” must be set by a fixture log or
operator before capture. Lux is a covariate, not a cause oracle: equal visible
lux does not imply equal spectrum, reflectance, exposure, or film transmission.
The cover/film state, lamp/placement, camera path, illuminator state, exposure,
gain, white balance, geometry, and trigger-to-frame timing must be logged.

The target payload must be independently registered as above. A learned cause
classifier or IR ratio may be evaluated, but neither can define the cause label.
The intervention must be safe and physically repeatable; “turn IR on” is not a
counterfactual if the intervention also changes exposure, white balance,
camera path, or target geometry without those changes being measured.

The two-world test is the key boundary. Let `Z` be the permitted pre-action
observation and `a` an allowed action. If there exist clean-low-light and
transparent-cover worlds `c1`, `c2` with the same distribution of `Z` but
different optimal actions under the declared loss, then no policy using `Z`
alone can identify the cause or attain both oracle actions. An IR-on view can
break this equivalence only if its response differs in a repeatable held-out
cell and the extra capture cost is charged. If IR-on does not break it, the
negative result is stronger than a failed classifier: the proposed observation
model is insufficient for the proposed decision.

### IR-CAUSE: ordinary intervention dominance

The candidate must beat, or be shown to provide a different operating point
from, fixed RGB, fixed NoIR+IR, fixed RGB-then-NoIR+IR two-shot, always-reacquire,
passive brightness/blur/decoder-quality routing, an IR-ratio threshold, and a
conservative one-extra-capture rule. If fixed two-shot is Pareto-optimal for
false-retain, unknown, latency, and joules, the adaptive IR claim is killed.
If an ordinary camera/quality intervention (fixed exposure, better lamp,
background/cover control, or a fixed extra capture) removes the effect, the
result is an apparatus engineering finding, not a new edge method.

## Assumption and identification audit

| Assumption | Status | Consequence |
| --- | --- | --- |
| Purchased Module 3 exposes a stable RAW10/Bayer mode through the selected API. | [GAP] | Must run the capability probe; product specification is not a measured unit result. |
| RAW and JPEG are same-exposure or have a request-level witness. | [GAP] | Without this, RAW-JPEG-GATE exact claim is invalid and becomes sequential-capture only. |
| 3A controls remain fixed or are fully logged. | [GAP] | Do not pool cells if exposure/gain/WB changes. |
| Exact payload truth is independent of candidate confidence. | [C] protocol requirement | Any leakage kills the action comparison. |
| Physical cover/light states are independently assigned. | [C] protocol requirement | Observed quality values cannot substitute for cause labels. |
| IR-on response differs between the two worlds. | [GAP] | Needs held-out physical repetition; no paper or local data establishes it. |
| RAW processing/storage/energy can be measured fairly. | [GAP] | Uncharged overhead invalidates the action-frontier comparison. |
| A single apparatus result transfers to general cameras or maintenance scenes. | [KILL] | Scope must remain the named marker, cells, and purchased path. |

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Passive perception plus selected interventions and effective-information action selection | Counterfactual perception-fault diagnosis; Abstract and Sec. 1 | Active intervention for hidden perception causes | Kills general IR cause-diagnosis framing; leaves only a finite marker/action audit. |
| Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Cheap screen, confirmation sensor, uncertainty/OOD escalation, watchdog | Fault warning under activation/latency cost; Secs. 1, 3.1, 5.1, 6, 8 | Screen/confirm/escalate acquisition under edge budget | Kills generic adaptive IR routing; leaves a bounded physical replication or null. |
| Baek et al., *Lens: Adaptive Camera Sensor for Vision Models*, arXiv v3, 2026-05-19, https://arxiv.org/abs/2503.02170 | Image/model state selects camera parameters under capture cost | Vision accuracy and capture-time trade-off; Secs. 3.1-3.2, 4-5 | Preview-to-camera-action routing | Kills a new adaptive camera selector as the contribution. |
| Xu et al., *AdaptiveAE: An Adaptive Exposure Strategy for HDR Capturing in Dynamic Scenes*, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Sequential ISO/shutter/frame actions | HDR quality, motion, noise; Secs. 3.3-3.4 and pp. 25176-25185 | Sequential exposure/action optimization | Kills generic adaptive exposure/burst novelty. |
| Ma, Yan & Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions*, arXiv v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Clean reference, luminance/gradient statistics, state machine and camera-disjoint thresholds | Optical-health/occlusion monitoring; Secs. I-VIII, X-XIII, Supplementary XII | Passive cover/occlusion and photometric monitoring | Kills passive contamination/quality diagnosis as a new mechanism; active IR increment remains unproven. |
| Chen, Tai & Ma, *RAW Image-Based Object Detection in Harsh Environments*, AAAI 2024, https://doi.org/10.1609/aaai.v38i2.27867 | RAW detection pipeline and RAW corruption benchmark | Harsh-environment detection mAP; Vol. 38(2), pp. 1063-1071 | Broad RAW robustness | Kills “RAW is generally more reliable”; leaves a finite exact-marker sufficiency test. |
| Berdan et al., *ReRAW: Efficient RAW Image Restoration for Mobile Object Detection*, CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_Efficient_RAW_Image_Restoration_for_Mobile_Object_Detection_CVPR_2025_paper.html | RAW restoration and mobile detection | Detection quality and efficiency; method and experiments | RAW edge benefit under harsh input | Kills RAW restoration/mobile-processing novelty; does not answer the exact marker action frontier. |
| Raspberry Pi, `rpicam-raw`, official documentation, accessed 2026-09-23, https://www.raspberrypi.com/documentation/computers/camera/rpicam_raw.html | Raw Bayer capture and sensor modes | Format/capture capability | RAW feasibility contract | Leaves actual unit mode, pairing, throughput, and cost as [GAP]. |
| Raspberry Pi, *Picamera2 Manual*, current PDF accessed 2026-09-23, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf | Main/JPEG and raw stream configuration, request metadata, packed/unpacked formats; Sec. 4.2 and request/stream sections | Stream configuration and request behavior | Implementation route, not a same-exposure proof | Leaves the selected API's frame correspondence and negotiated mode to be measured. |
| Raspberry Pi Camera Module 3 Product Brief, dated 2025-10-06, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | Standard/NoIR optical variants and nominal RAW10 specification | Product specification, p. 3 | Spectral path and nominal RAW capability | Does not establish purchased-unit behavior or pair timing. |

## Strongest simple baseline

For `RAW-JPEG-GATE`, the strongest baseline is a frozen JPEG-only quality
policy plus fixed two-shot/always-reacquire, not a hand-picked single scalar.
Thresholds must be frozen on source cells, evaluated on held-out cells, and
compared at the same false-retain target. The primary table must include exact
code success, false-retain, unknown, reacquisition count, bytes, wall time,
unpacking time, dropped frames, and joules. A RAW scalar that does not improve
the frontier after these charges is a null/engineering result.

For `IR-CAUSE`, the strongest baseline is fixed RGB-then-NoIR+IR two-shot,
always-reacquire, and a conservative one-extra-capture rule, alongside fixed
RGB, fixed NoIR+IR, passive quality, and IR-ratio controls. The offline physical
cell oracle is for reporting the attainable frontier only and cannot be used
online.

## Contrarian result

The most likely positive-looking result is a protocol artifact: RAW saturation
or linear occupancy appears useful because its frame had a different exposure,
or because the JPEG baseline was denied decoder confidence/second capture, or
because RAW bytes and unpacking were omitted from the cost. The corresponding
IR artifact is that film placement, exposure, white balance, or geometry changes
with IR, so a classifier learns the intervention setup rather than a cause.

The strongest negative result is therefore informative: JPEG/decoder quality or
fixed two-shot ties the RAW/IR policy, or two physical worlds remain matched in
the permitted observation model. In either case the correct deliverable is a
bounded apparatus result and an explicit sufficiency/non-identifiability
boundary, not a larger network or another sensor purchase.

## Feasibility audit

- **Hardware:** Pi 5B, RGB/NoIR cameras, an IR illuminator, printed targets and
  covers are recorded locally as available. Camera revision, illuminator
  spectrum/power, rigid fixture, and power instrument remain [GAP].
- **RAW capability:** official tools document raw Bayer capture and the product
  brief specifies RAW10, but the local preflight has not established the actual
  mode, Bayer order, packing, black/white levels, request pairing, dropped
  frames, storage rate, or energy.
- **Data/truth:** generated QR/AprilTag/ArUco payloads and inert covers avoid
  personal data, but independent payload equality and preassigned physical
  labels are mandatory.
- **IR safety:** illuminator wavelength, intensity, duty cycle, eye-safety
  boundary, and thermal behavior are unresolved. No people or biological
  targets should enter this pilot.
- **Measurement:** a USB power meter may miss fast capture transients. Energy
  claims require synchronized timing and repeatability; otherwise report
  device-level wall time and an explicitly limited power estimate.
- **Scope:** one camera path and one printed-marker family cannot support a
  general camera, maintenance, authentication, or security conclusion.
- **Schedule:** the capability probe can still be useful for the Palm-adjacent
  apparatus, but a positive thesis claim would require independent sessions,
  held-out cells, and remount/placement repetition beyond the preflight.

## Evidence ledger

| Claim | Label | Primary source and version/date | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| The current RAW claim is bounded to a same-exposure RAW scalar and exact-marker action loss. | [K] | `research/active/13-raw-jpeg-gate-preflight.md`, local, current 2026-09-23 | “Story and bounded claim”, “Policies and controls”, “Promotion and kill criteria” | Local protocol definition, not evidence of benefit. |
| The current IR claim is a finite active-IR incremental-information test, not general diagnosis. | [K] | `research/ops/divergence/2026-08-31-pi5-physical-intervention-divergence-round10.md`, local, 2026-08-31 | IR-CAUSE candidate, evidence ledger, decision | Older packet; no newer RAW/IR divergence packet found. |
| Broad active counterfactual fault diagnosis is occupied. | [KILL] | Han et al., arXiv v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Abstract; Sec. 1 | Does not kill a finite marker null/boundary study. |
| Resource-aware confirm/escalate sensing is occupied. | [KILL] | Bian et al., Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Secs. 1, 3.1, 5.1, 6, 8 | Different sensor stack; action family overlaps. |
| Passive optical-health monitoring is occupied. | [KILL] | Ma et al., arXiv v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Secs. I-VIII, X-XIII; Supplementary XII | Does not establish active IR value. |
| Adaptive camera/exposure action selection is occupied. | [KILL] | Baek et al., Lens arXiv v3, 2026-05-19, https://arxiv.org/abs/2503.02170; Xu et al., AdaptiveAE ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Lens Secs. 3.1-3.2, 4-5; AdaptiveAE Secs. 3.3-3.4, pp. 25176-25185 | Kills generic adaptive selector/exposure claims. |
| Broad RAW harsh-environment detection and mobile RAW restoration are occupied. | [KILL] | Chen et al., AAAI 2024, https://doi.org/10.1609/aaai.v38i2.27867; Berdan et al., CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_Efficient_RAW_Image_Restoration_for_Mobile_Object_Detection_CVPR_2025_paper.html | Chen Vol. 38(2), pp. 1063-1071; ReRAW method/experiments | Does not directly test printed-code action loss. |
| Pi official software exposes raw Bayer capture and stream configuration. | [K] | Raspberry Pi `rpicam-raw`, accessed 2026-09-23, https://www.raspberrypi.com/documentation/computers/camera/rpicam_raw.html; Picamera2 Manual, accessed 2026-09-23, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf | rpicam raw-output/mode documentation; Picamera2 Sec. 4.2 and request/stream sections | Capability only; same-exposure pairing remains [GAP]. |
| Camera Module 3 has nominal RAW10 and standard/NoIR optical variants. | [K] | Raspberry Pi Camera Module 3 Product Brief, 2025-10-06, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | p. 3 | Product specification, not a measured purchased-unit result. |
| Same-exposure pairing, independent truth, and cost-inclusive RAW benefit are established. | [GAP] | Local preflight and capability script | No completed Pi run or local checkout-equivalent trace inspected in this recheck | This is the decisive missing evidence. |
| IR-on separates the two physical worlds and improves action loss. | [GAP] | Local IR-CAUSE hypothesis | No held-out physical pilot inspected | No positive result can be inferred from the hypothesis. |

## Queries and failed searches

Queries used or inherited and rechecked on 2026-09-23:

- `Pi 5 rpicam-raw RAW10 Camera Module 3 Picamera2 raw stream same request JPEG`
- `site:raspberrypi.com/documentation rpicam raw output DNG RAW10 request JPEG Picamera2 manual`
- `RAW image edge detection reliability JPEG quality saturation SNR 2024 2025`
- `RAW image quality uncertainty saturation camera reliability 2025`
- `active illumination counterfactual fault diagnosis robot perception intervention information 2025`
- `adaptive camera sensor exposure modality selection edge capture cost 2024 2025`
- `transparent cover low light infrared illumination camera marker diagnosis exact code`
- `camera RAW JPEG same exposure frame identifier metadata libcamera Picamera2`

The inspected source chain did not jointly evaluate Pi 5 RGB/NoIR, independently
labelled transparent-cover versus low-light cells, exact printed-payload action
loss, fixed two-shot, and matched joules. That absence is a retrieval boundary,
not evidence of novelty. The local evidence also lacks a completed capability
run proving the purchased unit's RAW mode, same-exposure correspondence, 3A
stability, storage/processing overhead, and energy. No source inspected here
establishes that IR-on identifies the proposed two worlds after exposure,
white-balance, geometry, and timing controls.

## Decision

`RAW-JPEG-GATE`: **KILL as a positive thesis claim**. Retain only as a
capability preflight or finite negative/sufficiency appendix. A promotion would
require a completed same-exposure/request-witness run, independent payload
truth, frozen JPEG/decoder controls, fixed two-shot and always-reacquire
baselines, full RAW overhead/energy accounting, and repeated held-out gains.
Without those, an ordinary JPEG quality intervention or fixed reacquisition can
explain the result.

`IR-CAUSE`: **KILL as a general diagnosis/adaptive-sensing thesis**. Retain
only as a bounded active-IR action/identifiability pilot. It must either show a
held-out action-frontier improvement beyond fixed two-shot and ordinary quality
controls, or report the two-world non-identifiability/null result.

Overall: **PIVOT**

PIVOT
