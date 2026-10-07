# Divergence Packet: 2026-09-15 -- Pi palm latency and active IR/camera acquisition

## Decision investigated

The practical decision is how to turn the currently unusable Raspberry Pi palm
pipeline (laggy preview, missing/late detection box, video stalls) into a
responsive local demonstration while bringing a newly connected IR illumination
path into the experiment without falsely calling a model swap, Pi deployment,
or generic palmprint/palm-vein fusion a research contribution.

The user-confirmed near-term requirements are operational: make the live path
run, show a usable hand/ROI box, and begin IR plus camera capture. The research
question is narrower: after the apparatus is measurable, does one controlled
IR observation change a held-out palm-verification action frontier beyond
simple fixed controls? The system must first distinguish a capture/queue/ROI
bottleneck from a matcher bottleneck. A smaller model is a valid engineering
fallback, not evidence of novelty.

## Search boundary

- Search date: 2026-09-15. Read `AGENTS.md`, `research/active/README.md`,
  `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`,
  the 2026-09-13 divergence packets, the archived Pi/palm-vein and embedded
  palm logs, and `minutes/09-13-palm-payment-roadmap-update.md`.
- This overlaps palm, NoIR/NIR, edge runtime, ROI and active acquisition, so
  archive material was used as a constraint. It says Pi + NoIR + IR + local
  palm/vein matching is prior engineering, and the active register says broad
  adaptive acquisition, cross-spectral matching, generic fusion, a new ROI
  network and lightweight recognition are occupied.
- Primary/official sources inspected this round:
  - Raspberry Pi Camera documentation, retrieved 2026-09-15:
    https://www.raspberrypi.com/documentation/accessories/camera.html
  - Raspberry Pi camera software documentation, retrieved 2026-09-15:
    https://www.raspberrypi.com/documentation/computers/camera_software.html
  - *The Picamera2 Library*, PDF revised 2026-06-30, pp. 78--80:
    https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
  - Grosz, Godbole and Jain, *Mobile Contactless Palmprint Recognition: Use of
    Multiscale, Multimodel Embeddings*, arXiv:2401.08111v1, 2024-01-16;
    HTML Secs. I--IV:
    https://arxiv.org/html/2401.08111
  - Li et al., *SYEnet: Simple yet effective network for palmprint recognition*,
    Information Sciences 669 (2024) 120518, DOI:
    https://doi.org/10.1016/j.ins.2024.120518
  - Shao et al., *Efficient Deep Palmprint Recognition via Distilled Hashing
    Coding*, CVPRW 2019, official PDF, Secs. 1--4:
    https://openaccess.thecvf.com/content_CVPRW_2019/papers/CEFRL/Shao_Efficient_Deep_Palmprint_Recognition_via_Distilled_Hashing_Coding_CVPRW_2019_paper.pdf
  - Fan et al., *A Novel Hybrid Fusion Combining Palmprint and Palm Vein for
    Large-Scale Palm-Based Recognition*, IEEE TSMC 54(7), 2024, DOI:
    https://doi.org/10.1109/TSMC.2023.3346961
  - Pan et al., *SSFD-Net*, Digital Signal Processing 159 (2025) 105003, DOI:
    https://doi.org/10.1016/j.dsp.2024.105003
  - TensorFlow Lite performance-measurement documentation, retrieved
    2026-09-15, sections "Benchmark tools", "Native benchmark binary" and
    "Profiling model ops":
    https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/g3doc/performance/measurement.md
- Key queries:
  - `"lightweight" "palmprint recognition" 2025 paper`
  - `"efficient" "palmprint recognition" 2024 paper mobile`
  - `palm vein Raspberry Pi NoIR 850 nm low cost primary paper`
  - `site:openaccess.thecvf.com palmprint lightweight recognition 2024 2025 efficient model paper`
  - `Raspberry Pi Camera Module v2 NoIR documentation IMX219 infrared filter official`
  - `Raspberry Pi Picamera2 camera controls frame rate resolution documentation official`
  - `site:github.com tensorflow lite Raspberry Pi performance benchmark official documentation delegates`
- No claim below is global novelty. `[GAP]` means unresolved only under the
  stated source chain and search date.

## Recent-paper limitation map

| Work | Exact pages/sections read | What it already occupies | Consequence for this decision |
| --- | --- | --- | --- |
| Raspberry Pi Camera Module 2 NoIR official documentation | Camera Module 2, lines 132--143, retrieved 2026-09-15 | The Camera Module 2 is an 8 MP IMX219; its NoIR variant has no IR filter and captures visible plus IR. | IR-on is an illumination/capture-state intervention on this sensor, not proof of a separate visible/NIR camera pair, palm-vein channel, or synchronized multimodal apparatus. |
| Raspberry Pi camera/Picamera2 documentation | Camera controls: `shutter`, `gain`, `awbgains`, `denoise`, `tuning-file`, lines 994--1132; Picamera2 manual pp. 78--80 | Exposure, gain, AWB, denoise, crop, sensor timestamp and frame-duration metadata/control are available parts of the capture apparatus. | Auto exposure/gain, AWB, high-quality denoise and full-resolution copying can confound IR-on/off comparisons and create apparent video stalls. Freeze/log them before comparing any model. |
| Palm-ID, arXiv:2401.08111v1 | HTML Secs. I--IV; system description and efficiency/evaluation text | Complete mobile local palm pipeline: capture, ROI, enhancement, CNN+ViT embeddings, quality handling, template reduction and 1:1/1:N use cases. The reported 18 ms extraction figure is on an AMD EPYC search host, not a Pi end-to-end latency. | Replacing the present network with Palm-ID-scale components is not a credible Pi baseline. A full mobile-style learned stack is a poor first repair; stage timing must decide whether any learned embedding belongs in the live path. |
| SYEnet, Information Sciences 2024 | Publisher abstract and introduction summary displayed for DOI record | Lightweight/open-environment palm recognition and dedicated ROI extraction are established model families. | A new "lightweight palm model" or "light ROI net" would collide. A frozen small model can be compared only as an engineering artifact. |
| Shao et al., CVPRW 2019 | Secs. 1--4 | Efficient palm recognition via compact/distilled hashing for mobile/wearable settings is an established efficiency family. | Compact templates, distillation/hashing and fast gallery search are baselines, not the FYP identity. |
| Fan et al., IEEE TSMC 2024; Pan et al., DSP 2025 | Abstract, method/experiment descriptions recorded in the 2026-09-13 packet | Palmprint+palm-vein fusion, adaptive confidence weighting and missing-modality representation/recovery are direct families. | Do not train fusion or hallucinate a missing vein modality before proving the actual NoIR+IR observation is repeatable and has incremental value over fixed two-shot and VIS recapture. |
| TensorFlow Lite performance measurement documentation | "Benchmark tools", native binary and operation-profiling sections | Model comparison can separately measure initialization, warm/steady inference and memory; operation profiling exists. | A one-FPS number cannot diagnose the live stall. The local experiment needs capture, ROI, preprocessing, inference, matching, UI/display and queue-age measurements as separate stages. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| `E0-STAGE-NULL` | A palm-payment demo user sees frozen video or a delayed box; a stale frame can be matched after the hand has moved, and an over-large model makes the entire terminal unusable. | `[E]` Produce a frozen Pi-specific stage ledger and bounded root-cause map for the current artifact: `capture -> queue -> ROI -> preprocess -> embed -> search -> UI`. Select the smallest fixed profile that meets a declared fresh-frame/p95 transaction target. This is an engineering gate, not a novel scheduler. | TFLite benchmark tooling; prior embedded/mobile palm systems. | Kill any explanatory statement if timestamps cannot identify the latest displayed/captured frame, thermal state is uncontrolled, or a single uninstrumented FPS counter is the only evidence. If model time is less than a small fraction of end-to-end time, a model swap cannot be credited. | Immediate; no data collection beyond synthetic/replay images and consented demo samples. **PROMOTE as an engineering prerequisite, never as thesis.** |
| `L1-SPLIT-PREVIEW` | The user needs a live guide box without a video freeze, while identification only needs one stable palm ROI per transaction. | `[C]` A two-rate architecture -- low-resolution, frame-dropping preview/hand box; then one explicit full-quality ROI capture for verification -- improves the finite `(fresh-preview age, failure-to-acquire, p95 transaction time, FMR/FNMR, peak RSS)` frontier over the current every-frame full pipeline and fixed low-resolution-only verification. | Generic adaptive acquisition and mobile guide/retry systems; `ASI-IR`/adaptive routing are already KILL as mechanism claims. | Fixed low-resolution verification matches; high-resolution every-frame is already fresh; or the split only hides stale frames while capture-to-decision latency worsens. The claimed result must be stage logs, not visual impression. | High demo value and low hardware burden. **PIVOT to deployment characterization**, because the architecture is established. |
| `L2-MATCHER-TRIAGE` | A smaller matcher may be needed so a local 1:N transaction can finish, but a false match/unknown trade-off must be visible. | `[C]` At a frozen ROI and identity/session protocol, compare a deterministic traditional baseline (the existing Fast-CC-style matcher, if it is actually reproducible) with at most one legally obtained fixed compact embedding model. Report the transaction frontier including model load, warm inference, matching, accuracy, template bytes, RSS, temperature and input energy. | Palm-ID; SYEnet; distilled-hashing palm recognition. | Kill it as a research direction if a fixed baseline satisfies the interaction target, if weights/data licences are unclear, if any threshold is tuned on held-out sessions, or if only inference time rather than the transaction path improves. | Necessary only after `E0-STAGE-NULL`. **KILL as thesis; engineering model-selection gate.** |
| `IR0-APPARATUS-TRUTH` | IR has been connected, but treating a brighter NoIR image as a vein modality can create a false biometric/security claim. | `[E]` With fixed geometry, capture paired IR-off/IR-on frames and log illuminator current/state, wavelength/manufacturer data, distance/angle, exposure, analogue gain, AWB/gains, denoise/tuning, frame timestamps and thermal state. Determine whether the target supplies stable repeatable NIR structure at all. | Existing Pi NoIR palm-vein boxes; Fan 2024 and Pan 2025 show that generic palmprint/vein fusion is already occupied. | Kill the palm-vein wording if repeated IR frames do not show stable same-hand structure across sessions, or if the apparent change is explained by AE/gain/blur/exposure. IR remains NIR-assisted illumination only. | Immediate engineering experiment. Requires illumination safety/specification and a rigid mount. **PROMOTE as Gate 0 only.** |
| `IR1-INCREMENT` | A user has an ambiguous VIS/NoIR-under-visible observation. Acquiring IR may avoid a failed transaction but adds latency, power and a second capture. | `[C]` After a declared ambiguous first observation, a one-time IR-on capture changes the held-out `FMR/FNMR/failure-to-acquire/retry/latency/joules` frontier beyond `VIS(or IR-off) only`, `IR-on only`, fixed `VIS then IR`, fixed VIS recapture, equal-score fusion and `unknown`. This is a finite action-value evaluation, not learned multimodal fusion or causal diagnosis. | Fan 2024 fusion; Pan 2025 missing-modality recovery; Fei et al. 2024 VIS-NIR matching; Bian et al. 2026 active acquisition (already audited in active state). | Fixed two-shot, fixed VIS recapture, simple IR-ratio/quality gate or equal-score fusion is non-dominated; IR values are not repeatable; capture order explains effect; or session/identity blocking removes it. | Medium. First requires `IR0`; 3--5 people are protocol smoke testing only, not a FAR claim. **PIVOT (Amber), high negative-result value.** |
| `IR2-RING-INTERACTION` | A ring/accessory or wet/glare-like surface condition may either harm or help the IR path, causing a false payment refusal or a false confidence increase. | `[C]` On one declared NoIR+IR fixture, determine whether protocol-assigned ring/accessory-by-illumination cells produce a repeatable stage-localized degradation or action-rank change beyond no-ring, ordinary augmentation, fixed crop, score-only gating and fixed two-shot. | Open-environment ROI/augmentation and generic active illumination are occupied. The 2026-09-13 `RING-CELL` audit is the direct local predecessor. | No repeatable ring effect; identity/ring/session confounding; effect vanishes under a fixed guide; or simple controls dominate. Do not claim a new ring model. | Medium ethical/protocol burden, low hardware burden. **HOLD only after live pipeline and `IR0`; useful finite null path.** |

## Top two formalizations

### `IR0-APPARATUS-TRUTH`: IR path validity before fusion

- **[D] Decision:** decide whether the installed IR path is admissible as an
  NIR observation for a later palm experiment, or only as illumination for a
  low-light demo.
- **[A] Assumptions:** a fixed camera and mount; the IR device has a recorded
  wavelength, electrical setting and geometry; every capture records actual
  exposure/gain/AWB/denoise/tuning and sensor timestamp; repeated same-hand
  frames span at least separate sessions. The user must obtain/retain the
  illuminator safety documentation. No image is called a vein label merely
  because it is captured with a NoIR sensor.
- **[T] Target:** characterize paired IR-off/IR-on repeatability and whether
  same-hand spatial structure remains stable after exposure normalization.
  The target is hardware truth, not an identity accuracy gain.
- **Observable outcome:** raw/captured frame hash; illuminator state; exposure,
  analogue gain, colour gains/AWB state, frame duration, sensor timestamp;
  ROI success; blur/saturation; a development-frozen texture/contrast
  repeatability statistic; temperature; capture latency; and measured energy
  where an inline meter is available.
- **Counterexample:** IR-on produces a brighter or lower-noise image, but its
  apparent vessel-like pattern changes with AE/gain, focus or placement. This
  cannot support a palm-vein or independent-modality claim.
- **Negative-result value:** it prevents a false multimodal premise. A stable
  null directs the demo toward IR-assisted palmprint capture and leaves the
  thesis gate closed, rather than inventing fusion.

### `IR1-INCREMENT`: one IR acquisition against equal-cost controls

- **[D] Decision:** after a first capture, choose `decide`, `recapture under
  the first illumination state`, `capture once with IR on`, or `unknown`.
- **[A] Assumptions:** true identity/mated-versus-non-mated outcome is external
  to the policy; a fixture assigns low-light/accessory/pose cells before
  capture; capture order is randomized or balanced; the threshold and one
  extra-capture budget are fixed on development sessions; identity and session,
  not frames or score pairs, are independence units.
- **[T] Target:** on held-out sessions/cells, compare the Pareto outcome vector
  `(FMR, FNMR, failure-to-acquire, extra captures, p95 transaction latency,
  energy)` for static one-shot, fixed two-shot, one VIS recapture, IR-only,
  equal-score fusion, scalar quality/IR ratio and a transparent one-IR rule.
- **Observable outcome:** the complete `IR0` ledger plus enrollment/probe
  session, condition, matcher score(s), decision, retry outcome, 1:N rank,
  correct identity indicator and resource stages.
- **Counterexample:** a fixed second shot dominates; equal-score fusion fully
  reproduces an adaptive rule; a lower exposure under the original lamp gives
  the same effect; or held-out identities/sessions reverse the result.
- **Negative-result value:** establishes that this cheap acquisition path does
  not add independent decision information at its actual cost. That is a useful
  bounded result and a direct reason not to train a fusion network.

## Concrete sequence for the current practical issue

This is an experiment/work-order sequence, not a research claim by itself.

1. **Freeze the failing artifact first.** Record Pi model/RAM, OS/kernel,
   camera driver/Picamera2 version, capture resolution/format, requested and
   observed frame duration, camera tuning file, model hash, input ROI size,
   interpreter/delegate/thread count, gallery size, display method and cooling
   state. A changed setting starts a new run.
2. **Build `E0` instrumentation before replacing the model.** For each frame or
   transaction, record `sensor_timestamp`, receive time, queue-enter/dequeue,
   ROI start/end, preprocessing start/end, inference start/end, match
   start/end, UI-presented time and frame ID. Compute preview age at display;
   discard queued old preview frames rather than rendering them later.
3. **Run four 60-second controlled profiles using one fixed replay clip and one
   static live hand:** capture only; capture + ROI box; capture + current
   matcher; capture + matcher + UI. Repeat after warm-up. The broken stage is
   the first profile whose p95 preview age or dropped-frame count fails the
   declared target. Do not infer cause from average FPS.
4. **Make the demo transactional.** Use a low-resolution preview/hand guide and
   one explicit stable-frame capture. Do ROI and matching once per attempt, not
   on every preview frame. The explicit action makes the UI predictable and
   permits a smaller `L2` matcher without freezing video.
5. **Only then test one smaller frozen matcher.** Compare it with the current
   baseline under identical ROI, gallery, threshold-fitting and replay/live
   protocol. Reject models with unavailable weights, unclear data licence or
   unmeasured initialization/RSS cost. Do not begin a model search.
6. **Install IR under an apparatus manifest.** Keep IR off/on as an externally
   logged state. Start with static target and manual/fixed exposure/gain/AWB;
   capture paired frames after controls have settled. Do not conduct continuous
   IR PWM/frequency experiments or learned fusion in this round.
7. **Pass `IR0` before `IR1`.** If repeatable IR structure and independent
   capture records are absent, label the result `NIR-assisted illumination` and
   retain IR only as a demo low-light aid. If present, preregister fixed
   one-shot/two-shot/recapture/fusion controls before collecting held-out data.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Camera Module 2 NoIR uses the 8 MP IMX219 and lacks an IR filter, so it captures visible plus IR. | [K] | Raspberry Pi, Camera documentation, retrieved 2026-09-15, https://www.raspberrypi.com/documentation/accessories/camera.html | "Camera Module 2", lines 132--143. | Does not specify the user device's actual revision/cable/tuning or prove vein visibility. |
| Picamera2 exposes camera metadata/control relevant to a fair IR comparison, including frame duration, exposure, sensor timestamp and crop. | [K] | Raspberry Pi, *The Picamera2 Library*, PDF revised 2026-06-30, https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf | "Camera controls", pp. 78--80: `ExposureTime`, `FrameDuration`, `FrameDurationLimits`, `ScalerCrop`, `SensorTimestamp`, denoise/sharpness fields. | Availability is camera/driver dependent; inspect `camera_controls` on the actual Pi. |
| Raspberry Pi camera software permits gain, AWB gains, shutter, denoise and tuning-file settings, so automatic image processing can confound an IR-on comparison. | [K] | Raspberry Pi camera software documentation, retrieved 2026-09-15, https://www.raspberrypi.com/documentation/computers/camera_software.html | "Camera control options", lines 994--1132, especially `shutter`, `gain`, `awbgains`, `denoise`, `tuning-file`. | This establishes controllability, not that a particular setting is optimal for palm imaging. |
| An end-to-end mobile palm system combining ROI, enhancement and CNN/ViT embeddings exists; its published CPU timing is not Pi end-to-end latency. | [K] | Grosz, Godbole, Jain, Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | HTML Secs. I--IV; abstract/efficiency description and system/evaluation sections. | The 18 ms/0.33 ms values reported in the paper use its stated EPYC search hardware. Do not transfer them to Pi. |
| Lightweight/open-environment palm recognition and dedicated ROI extraction are established model families. | [K] | Li et al., SYEnet, Information Sciences 669 (2024) 120518, DOI https://doi.org/10.1016/j.ins.2024.120518 | Publisher abstract and displayed introduction summary. | Full article methods/timing tables were not accessible in this round; used only to block a broad lightweight-model claim. |
| Compact/distilled palm embeddings for mobile/wearable efficiency are established. | [K] | Shao et al., CVPRW 2019, official PDF https://openaccess.thecvf.com/content_CVPRW_2019/papers/CEFRL/Shao_Efficient_Deep_Palmprint_Recognition_via_Distilled_Hashing_Coding_CVPRW_2019_paper.pdf | Secs. 1--4. | Historical direct neighbor; it does not give an actual Pi 5 capture profile. |
| Palmprint/palm-vein fusion and missing-modality learning are existing method families. | [K] | Fan et al., IEEE TSMC 54(7), 2024, DOI https://doi.org/10.1109/TSMC.2023.3346961; Pan et al., DSP 159 (2025) 105003, DOI https://doi.org/10.1016/j.dsp.2024.105003 | Method/experiment descriptions inspected in the 2026-09-13 divergence/validation source chain. | No source proves this NoIR+IR apparatus senses an independent vein modality. |
| TFLite tooling separates initialization, steady inference and memory, and supports operation profiling. | [K] | TensorFlow Lite performance measurement documentation, retrieved 2026-09-15, https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/g3doc/performance/measurement.md | "Benchmark tools", "Native benchmark binary", "Profiling model ops". | TFLite metrics omit camera/UI cost unless the application separately measures it. |
| The installed IR illumination has documented wavelength, irradiance/eye-safety status and repeatable palm-vein-relevant structure. | [GAP] | No inspected source or local apparatus log | Not applicable | Must be physically verified. Do not assume 850 nm, safe output, or vein visibility from the presence of an IR board. |
| The current failure is caused primarily by model inference rather than capture, ROI, display, blocking I/O, memory pressure or thermal throttling. | [GAP] | No current Pi stage ledger was found in the inspected workspace | Not applicable | The first `E0` run decides this; replacing the model before this result is not justified. |

## Queries and failed searches

The stated searches located the official camera/TFLite sources and the primary
palm-model/fusion neighbors above. They did **not** locate a primary source that
would make the following exact endpoint already established or demonstrably new:

- a Pi 5 Camera Module 2 NoIR, IR-on/off, transaction-level palm `decide /
  recapture / unknown` comparison with fixed equal-cost controls and
  identity/session blocking;
- a primary paper proving that this low-cost NoIR plus arbitrary connected IR
  illuminator produces repeatable palm-vein data; or
- a modern palmprint model with public lawful weights, a Pi-compatible runtime
  and a complete same-apparatus 1:N transaction benchmark that can be assumed
  to fit the current code.

This is not evidence of novelty or absence. The unresolved practical inputs are
the actual model/repository and its preprocessing, exact Pi OS/runtime,
camera resolution and frame queue implementation, IR wavelength/current/driver,
camera-to-IR geometry, safety documentation, power-meter availability, consent
and session access, and whether an actual visible-light camera exists alongside
the NoIR path.

## Decision

**PROMOTE the engineering gates `E0-STAGE-NULL`, `L1-SPLIT-PREVIEW` and
`IR0-APPARATUS-TRUTH` now.** They directly address the broken live system and
create the audit trail required for IR work. They are implementation and
measurement work, not a thesis contribution.

**HOLD/PIVOT `IR1-INCREMENT` as the only research-shaped follow-on.** It is
eligible only if the IR path is physically characterized and a finite,
held-out action advantage survives fixed two-shot, VIS recapture, equal-score
fusion and scalar controls. `L2-MATCHER-TRIAGE` is a useful way to pick a
slightly lighter model, but it is **KILL as a thesis direction**. `IR2` should
wait until the live and IR apparatus gates pass.

PIVOT
