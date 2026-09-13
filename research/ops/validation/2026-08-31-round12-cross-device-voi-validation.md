# Validation Audit: 2026-08-31 round-12 cross-device transfer and active-IR candidates

## Decision investigated

This audit attempts to kill the newest cross-device/cross-illumination
divergence candidates (`XFER-ACT`, `PANEL-GATE`, `LUX-VOI`, `CAL-SCHED`, and
`REAL-DIG-RANK`) and the surviving optical candidates (`IR-CAUSE`,
`PRF-TR`, `PHY-MASK`, `FULL-CAP`, and `POL-GLARE-VOI`).  The assumed platform
is the purchased Raspberry Pi 5B (8 GB), official RGB Camera Module 3,
official NoIR camera, and an IR illuminator.  The proposed endpoint is a
non-personal, static printed marker record with actions `retain`, `reacquire`,
or `unknown`; there is no production, biometric, medical, or safety action.

## Claim under test

The strongest proposed claim is that a cheap edge node can use a source-camera
preview or a physical intervention to choose a lower-cost capture action whose
false-retain risk remains useful after changing camera path, lamp spectrum,
cover state, or a synthetic/physical fault.  The claim would be scientific
only if the action, cost, and held-out evaluation endpoint differ from prior
adaptive sensing, calibration monitoring, and synthetic-corruption work.  A
Pi deployment, a new panel, a new threshold, or a new RGB/NoIR data table is
not itself a contribution.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Lens (ICLR 2025), AdaptiveISP (NeurIPS 2024), AdaptiveAE (ICCV 2025), CM-ASAP (MIPR 2024), and Rampure et al. (arXiv 2026) already combine preview/quality features, adaptive camera or modality actions, and a compute/capture budget. Moravec & Šára (2024) already combine a cheap calibration witness, online verification, and a downstream failure endpoint. Agnihotri et al. (CVPRW 2025) already combine synthetic and real corruption rankings. | A finite RGB/NoIR marker action audit with an independent payload oracle and measured joules is not the same input/output tuple in the inspected papers. This is a bounded empirical protocol distinction, not component novelty. | High for generic methods; medium for the finite optical endpoint. |
| Exact-claim collision | `PANEL-GATE` and `CAL-SCHED` are reference-target sufficiency and trigger decisions, which are ordinary calibration monitoring. `LUX-VOI` is an exogenous quality feature for sensor selection, a direct sensor-control variant. `REAL-DIG-RANK`/`PHY-MASK`/`FULL-CAP` restate the synthetic-versus-real robustness question. `IR-CAUSE` as causal diagnosis collides with Han et al. (2025) active FDI and Ma et al. (2026) camera-health transfer. | `XFER-ACT` can remain distinct only by testing *rank preservation of a finite action set* across a purchased RGB/NoIR pair, with no population-transfer or causal claim. `IR-CAUSE` can remain distinct only as incremental information from an IR-on intervention for two pre-labelled physical worlds. | High for the broad claims; medium for the narrowly scoped tests. |
| Boundary / impossibility | A clean low-visible-light scene and a transparent cover or water film can be adjusted to have the same RGB preview, luma, blur, lux and metadata while requiring different actions. Equal-lux lamps can have different spectra, so a scalar lux sensor cannot identify spectral utility. A panel is spatially and spectrally unrelated to the marker scene. Sequential RGB/NoIR captures are not synchronized by Pi software. | Independent cover/fault labels, an exact preprinted payload checked by a separate oracle, fixed/logged exposure and white balance, static targets, timing/energy logs, and held-out lamp/material cells make a *finite* risk table identifiable. They cannot support a general camera-family transfer theorem or general cause diagnosis. | High for the counterexample; empirical effect remains [GAP]. |

## Candidate-by-candidate kill map

| Candidate | Direct collision or failure | Decisive kill test and simplest baseline | Feasibility and status |
| --- | --- | --- | --- |
| `XFER-ACT` | Cross-sensor color-constancy/calibration already maps camera responses (Yue & Wei 2024; Punnappurath et al. 2025). Lens and Rampure already adapt camera/modality actions under a budget. A source-calibrated policy may therefore be only a renamed transfer threshold. | Freeze five controls: always RGB, always NoIR+IR, fixed RGB-then-NoIR+IR, scalar brightness/blur/IR-ratio threshold, and an oracle that knows the cell. Measure per-cell false-retain/unknown/energy and rank actions on held-out camera/lamp cells. Kill if the fixed two-shot or scalar rule is Pareto-optimal, or if no preregistered rank inversion repeats in three sessions. | Existing hardware and a printed code are feasible; no second board or training is required. It cannot justify a new-camera guarantee. **PIVOT (Amber finite audit).** |
| `PANEL-GATE` | Chart metrology and online calibration monitoring already use reference targets to trigger recalibration. Moravec & Šára (2024) explicitly report lightweight single-frame monitoring and downstream SLAM correlation; Punnappurath (2025) warns that one X-Rite chart under-represents materials. A panel may not witness local glare/focus. | Compare six-to-twelve patch panel, one gray/white patch, a scalar brightness/blur test, and a fixed per-device threshold at equal one-shot cost. Test held-out marker materials and cover states. If gray/white or fixed threshold matches, or panel state is confounded with marker state, kill the thesis claim. | Very easy to build, but it is a preflight/characterization study, not a distinct mechanism. **KILL thesis; preflight only.** |
| `LUX-VOI` | Sensor-selection papers use image-derived quality and illumination state; Zhang et al. (2024) actively illuminates a low-cost camera. Lux is only photopic illuminance and discards spectral power distribution. | Add a <$10 BH1750 only after image-only controls are frozen. Compare image-only luma/blur/AE, lux-plus-image, and fixed two-shot across equal-lux lamps with different spectra. If lux is redundant or fixed two-shot dominates, kill; equal-lux/opposite-spectrum cells are a built-in non-identifiability test. | Cheap sensor and lamps are feasible, but calibration, spectral control, and meter accuracy consume the schedule. **KILL thesis / PIVOT instrumentation.** |
| `CAL-SCHED` | Triggering a reference check from a quality statistic is standard online calibration scheduling. Moravec & Šára (2024) state the purpose is to detect decalibration and trigger calibration only when needed; Hurst et al. 2025 and related monitoring methods occupy uncertainty-driven scheduling. | Compare periodic every-N captures, every-frame panel, scalar quality threshold, and sequential trigger under the same bounded lamp/focus drift. If a fixed period or scalar threshold reaches the same false-retain/capture frontier, there is no scheduling contribution. | Mechanical drift fixture is feasible but requires long runs and repeatable drift; no new edge method remains. **KILL.** |
| `REAL-DIG-RANK` / `PHY-MASK` / `FULL-CAP` | Agnihotri et al. directly ask whether synthetic corruptions proxy real-world robustness and find aggregate correlation can be strong while corruption-specific correlation fails. Liao et al. (CVPRW 2025), MultiCorrupt (2024), MSC-Bench (2025), and SensorFault-Bench (2026) already benchmark simulated missing/noisy/crashed sensors and model rankings. | Freeze a deterministic decoder and compare digital zero/noise/blur ranks with cable, cover, saturation, and illumination cells. Use Kendall/Spearman with session bootstrap, plus fixed two-shot and scalar quality controls. Correlation or a tied frontier is a null; only a repeatable inversion can justify a bounded warning. | Lowest implementation risk and useful as an appendix, but it is not a method or universal “simulation is invalid” result. **PIVOT (negative benchmark).** |
| `IR-CAUSE` | Ma et al. (arXiv 2607.14760v1, 2026) monitor camera health/occlusion and transfer thresholds across cameras; Han et al. (arXiv 2509.18460v1, 2025) formalize active fault-diagnosis interventions. A causal-diagnosis framing is therefore occupied. | Construct two independently labelled worlds: clean low-visible-light and transparent cover/contamination at matched visible lux. Compare IR-on against fixed RGB->NoIR+IR, passive quality, IR-ratio, and always-reacquire. If pre-action observations overlap or IR does not reduce cause-confusion at matched cost, kill. | Owned cameras/IR, rigid fixture, and static marker are feasible; labels and manual AE/WB logging are mandatory. **HOLD (Amber), only as finite incremental-information test.** |
| `POL-GLARE-VOI` | Tang et al. (CVPR 2024) use multi-angle polarization for transparent-film removal and downstream QR/OCR; PolarFree (CVPR 2025) and Laser Shield (DAC 2024) occupy physical/digital polarizer interventions. | Compare no filter, fixed filter, one angle chosen before capture, fixed two-shot, scalar quality, and digital deglare. If fixed filter/two-shot ties or angle/material labels are confounded, kill. | Polarizer sheet/mount is cheap, but each extra optical degree of freedom increases controls and collision risk. **HOLD/PIVOT (Amber finite VOI only).** |

## Assumption and identification audit

1. **Hidden physical cause.** Let (W_1) be a clean lens under low visible light and (W_2) a transparent cover under brighter visible light. By adjusting lamp intensity, cover transmission, and exposure, both can produce the same RGB preview (O), metadata (M), and even the same scalar lux (L), while the best action differs (`NoIR+IR` for (W_1), reacquire/clean for (W_2)). Thus no passive policy (a=f(O,M,L)) can certify both worlds. This is a construction, not an empirical claim.
2. **Spectral confounding.** Lux is photopic; two lamps with equal lux can have different near-IR power and marker reflectance. A lux-only policy can therefore reverse action utility on held-out spectra. A cheap meter is an explanatory measurement unless the experiment controls spectral composition.
3. **Panel sufficiency.** A matte panel can show exposure or gross color drift but cannot witness scene-specific specular glare, local focus, or cover-induced scatter. A panel policy requires a held-out marker oracle; panel accuracy itself is not target truth.
4. **Sequential cameras.** Camera Module 3 has an IR-cut filter while the NoIR variant omits it (Raspberry Pi Camera Module 3 product brief, p. 3). Pi camera software allows multiple camera operation but does not guarantee synchronized 3A or simultaneous exposure. Moving-target fusion is invalid without an LED/photodiode timing oracle; use a static target for the minimum test.
5. **Independent truth.** The payload must be generated and stored before capture and verified by an independent decoder/reference capture. Model confidence, panel score, or a post-hoc image statistic cannot serve as the ground-truth label.
6. **Cost accounting.** Report capture latency and joules per episode, not nominal sensor count. If an IR-on intervention costs a second capture and the fixed two-shot control has the same risk, a learned selector has no value.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap; what remains | 
| --- | --- | --- | --- |
| Baek et al., *Lens: Adaptive Camera Sensor for Vision Models*, ICLR 2025, arXiv:2503.02170v3 (19 May 2026), https://proceedings.iclr.cc/paper_files/paper/2025/file/ec14daa5c50745f83fb27f685f8dfc22-Paper-Conference.pdf | Unlabelled image/model output; selects camera parameters using VisiT confidence and candidate exposure settings; Secs. 2.2, 3.1--3.2, 5 | Image/model accuracy under sensor-control settings, fixed/random/auto-exposure baselines; paper pp. 4--9 and 11--12 | Kills generic preview-to-action and confidence routing. It does not test a physical RGB/NoIR cause label; exact finite action-rank endpoint remains [GAP]. |
| Xu et al., *AdaptiveAE*, ICCV 2025, pp. 25176--25185, official PDF https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV_2025_paper.pdf | Previous LDRs plus semantic/illumination features; A3C chooses ISO/shutter and number of frames; Secs. 3.3--3.4, p. 25180 | HDR quality, motion blur/noise, exposure-time budget; pp. 25176--25185 | Kills adaptive exposure/burst thesis. Marker exact-code risk and physical fault cells are outside its endpoint but do not make exposure scheduling novel. |
| Rampure et al., *Contactless Respiratory Monitoring on Heterogeneous Mobile Robots*, arXiv:2606.17376v1 (16 Jun 2026), https://arxiv.org/abs/2606.17376 | Mean brightness (B) chooses RGB or NIR/thermal/low-light; Sec. III-A, lines 51--59; SQI filters windows | RR error and operating-distance envelope across three robots and modalities; abstract, Secs. I, III-A, V | Directly kills brightness-triggered RGB/NoIR routing as a thesis. A static printed-code endpoint is different only as a finite audit. |
| Moravec & Šára, *High-recall calibration monitoring for stereo cameras*, Pattern Analysis and Applications 27:41 (published 13 Apr 2024), https://link.springer.com/article/10.1007/s10044-024-01264-1 | Single stereo frame, epipolar robust-kernel statistic and resampled-variance confirmation; abstract and Secs. 1--2 | Decalibration alarm/recall and downstream SLAM correlation; abstract reports 91%/82% recall, 94.7%/87.5% accuracy and Spearman 0.78 | Kills panel-trigger/calibration-monitoring mechanism. It does not prove a panel cannot be useful for the Pi marker, so that residual is a preflight test only. |
| Yue & Wei, *Effective cross-sensor color constancy using a dual-mapping strategy*, JOSA A 41 (2024), https://opg.optica.org/josaa/abstract.cfm?uri=josaa-41-2-329 | White-point observations from training/testing sensors; dual mapping with a 0.003 MB MLP; abstract and Tables 1--3 | Cross-sensor angular error under D65; Tables 1--3 | Kills “RGB-to-NoIR color mapping” as the technical difference. It does not evaluate action risk or physical cover labels. |
| Punnappurath et al., *Improved Mapping Between Illuminations and Sensors for RAW Images*, arXiv:2508.14730v1 (20 Aug 2025), https://arxiv.org/abs/2508.14730 | RAW responses from four cameras, 390 illuminations and 18 scenes; illumination/sensor mapping; Secs. 1--3 and Appendix C | Cross-camera/illumination RAW mapping; authors caution diagonal transforms and one chart fail on non-neutral materials | Kills chart-only/sensor-transfer color claims. A finite exact-code action test remains only an empirical boundary. |
| Agnihotri et al., *Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?*, arXiv:2505.04835v1 (7 May 2025), CVPR 2025 SynData4CV Workshop, https://arxiv.org/abs/2505.04835 | Cityscapes synthetic common corruptions vs ACDC real weather; Secs. 1, 3, 4.1--4.2, 5 | Segmentation model performance and correlation; abstract/HTML reports strong aggregate correlation with corruption-specific failures | Kills broad physical-vs-digital invalidity. A paired Pi optical/action endpoint can only report a device-specific inversion/null. |
| Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv:2509.18460v1 (22 Sep 2025), https://arxiv.org/abs/2509.18460 | Passive/active fault diagnosis; selects control inputs by effective-information criterion; abstract and Sec. 1 | Fault diagnosis under interventions | Kills IR-CAUSE as a general causal framework. A two-world IR incremental-information replication is narrower, and must explicitly say so. |

## Strongest simple baseline

The strongest baseline for every optical candidate is a deterministic fixed
policy: capture RGB with IR off, then capture NoIR with a fixed IR pulse, and
retain only when the known payload exactly matches; otherwise return
`unknown/reacquire`. Run this against always-RGB, always-NoIR+IR, a scalar
brightness/blur/IR-ratio rule, random action, and an oracle that knows the
physical cell. Match capture count, exposure limits, latency and joules.

For `REAL-DIG-RANK`, the decisive baseline is not a learned model: a frozen
decoder plus Kendall/Spearman rank and a session-bootstrap interval. For
`PANEL-GATE`/`CAL-SCHED`, compare periodic checks and a one-patch threshold
before any sequential or learned policy. For `LUX-VOI`, image-only luma/blur
and logged auto-exposure metadata must receive the same timing budget.

## Contrarian result

The most likely result is a null. On a static marker, the fixed two-shot
policy may dominate because the second NoIR/IR capture directly observes the
information that an adaptive preview tries to predict. A second likely null is
that cable-disconnect, digital zero-mask, lens-cover, and low-light cells have
the same action rank, reducing `PHY-MASK`/`FULL-CAP` to a small reproduction.
For `IR-CAUSE`, the likely negative is that matched low-light and cover worlds
remain indistinguishable after the fixed exposure/white-balance protocol, so
the honest output is `unknown` rather than a cause label. These nulls have
value only as preregistered finite bounds; they do not establish universal
simulation failure or causal diagnosis.

## Feasibility audit

- **Hardware:** The owned Pi 5B, RGB, NoIR and IR illuminator support static sequential captures. A rigid mount, printed markers, transparent covers and matte/reflective material samples are sufficient. A lux meter, USB power meter, polarizer, or photodiode should be bought only when a pilot gate requires it. The illuminator wavelength, power, diffuser, and eye-safety specification remain `[GAP]`.
- **Data and ethics:** Printed codes and material swatches avoid personal data and consent. Independent payload and intervention logs are feasible. A phone/flatbed oracle is acceptable for exact payload verification if its capture is not used by the policy.
- **Compute:** OpenCV/AprilTag/ZXing decoding and scalar features run on Pi 5. No deep training is required for the minimum audit; desktop training would not rescue an unidentifiable endpoint.
- **Timing:** Static scenes are required because RGB and NoIR sequential frames have scene motion and 3A confounds. A photodiode can timestamp a lamp but cannot establish semantic marker truth.
- **Sample size:** A 2 camera-path x 3 illumination x 3 cover/fault cell pilot with at least three sessions and 20 captures/action/session fits a December 2026 demo. Held-out materials and remounts fit 2027 H1. A population claim over cameras or lamps does not.
- **Time/risk:** Panel, lux, scheduling and polarizer branches multiply fixtures and controls. Running all branches would dilute the FYP. The first gate should test fixed two-shot versus one active IR intervention on a tiny held-out matrix.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Generic adaptive camera control is occupied. | [K] | Baek et al., Lens, ICLR 2025, arXiv v3 19 May 2026, https://proceedings.iclr.cc/paper_files/paper/2025/file/ec14daa5c50745f83fb27f685f8dfc22-Paper-Conference.pdf | Secs. 2.2, 3.1--3.2, 5; pp. 4--9, 11--12 | One-camera benchmark; not a physical Pi fault study. |
| Adaptive exposure scheduling under a capture budget is occupied. | [K] | Xu et al., AdaptiveAE, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV_2025_paper.pdf | Secs. 3.3--3.4, p. 25180; paper pp. 25176--25185 | HDR endpoint, not exact marker. |
| Brightness-based heterogeneous RGB/NIR modality selection is occupied. | [K] | Rampure et al., arXiv:2606.17376v1, 16 Jun 2026, https://arxiv.org/abs/2606.17376 | Sec. III-A, lines 51--59; abstract and Sec. V | Three robots and human RR endpoint; direct mechanism collision. |
| Lightweight calibration monitoring with a reference/downstream endpoint is occupied. | [K] | Moravec & Šára, 2024, https://link.springer.com/article/10.1007/s10044-024-01264-1 | Abstract and Secs. 1--2; published 13 Apr 2024 | Stereo/SLAM, not marker capture; still kills generic monitoring. |
| Synthetic-vs-real robustness proxy question is occupied and can have both correlation and failures. | [K] | Agnihotri et al., arXiv:2505.04835v1, 7 May 2025, https://arxiv.org/abs/2505.04835 | Secs. 1, 3, 4.1--4.2, 5 | Semantic segmentation/weather; physical camera endpoint remains outside scope. |
| Cross-sensor illumination mapping and chart limitations are known. | [K] | Yue & Wei 2024, https://opg.optica.org/josaa/abstract.cfm?uri=josaa-41-2-329; Punnappurath et al. 2025, https://arxiv.org/abs/2508.14730 | Yue abstract/Tables 1--3; Punnappurath Secs. 1--3, Appendix C | Color/RAW endpoint; does not prove action-risk transfer. |
| Active interventions can be framed as information-seeking fault diagnosis. | [K] | Han et al., arXiv:2509.18460v1, 22 Sep 2025, https://arxiv.org/abs/2509.18460 | Abstract and Sec. 1 | General FDI framework; narrow IR marker test remains distinct only in scope. |
| A finite RGB/NoIR action-rank inversion exists. | [C] | `XFER-ACT` hypothesis | No inspected source establishes it | Must remain Amber until held-out pilot. |
| IR-on adds incremental information beyond fixed two-shot and scalar quality. | [C] | `IR-CAUSE` hypothesis | No inspected source establishes it | Requires independent cover/lux labels and matched-cost test. |
| Lux adds value beyond image-only quality. | [C] | `LUX-VOI` hypothesis | No inspected source establishes it | Equal-lux spectra are a designed counterexample. |

## Queries and failed searches

Queries run 2026-08-31:

- `2024 2025 camera cross-device calibration transfer reliability exact task action decision paper arXiv`
- `2024 2025 RGB NIR camera modality selection illumination sensor selection edge paper`
- `2024 2025 synthetic corruption real-world corruption ranking benchmark vision paper`
- `2024 2025 camera chart calibration sufficiency reference panel reliability paper`
- `2024 2025 external light sensor camera image quality prediction lux spectral distribution`
- `2025 value of information active illumination camera decision reliability`

No inspected primary source used the exact combination of Pi RGB/NoIR,
transparent-cover/low-light two-world labels, exact printed-code action risk,
and matched joules. This is a retrieval `[GAP]`, not evidence of novelty.
The full CM-ASAP paper, the quantitative pages of some MDPI contamination
papers, and a complete citation-chain audit for every RGB/NoIR paper remain
`[GAP]`. No candidate should be promoted while those gaps affect its exact
claim.

## Decision

- `XFER-ACT`: **PIVOT (Amber)**, finite action-rank audit only.
- `PANEL-GATE`: **KILL** as a thesis; optional camera-path preflight.
- `LUX-VOI`: **KILL** as a thesis; instrumentation or negative spectrum test only.
- `CAL-SCHED`: **KILL** as a thesis; conventional maintenance characterization.
- `REAL-DIG-RANK` / `PHY-MASK` / `FULL-CAP`: **PIVOT** to a bounded negative benchmark.
- `IR-CAUSE`: **HOLD (Amber)** only as an incremental IR value-of-information test.
- `POL-GLARE-VOI`: **HOLD/PIVOT (Amber)**; it must beat fixed-filter and fixed-two-shot controls.

No candidate passes all three audits. The only live thesis gate is the small,
pre-registered IR-on versus fixed-two-shot pilot; a rank inversion or
incremental information effect must be repeatable on held-out physical cells,
otherwise the project should report a useful null and pivot to the physical
versus digital transfer benchmark.

HOLD
