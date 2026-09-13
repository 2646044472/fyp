# Active Edge Direction Search

## Current goal

Find one undergraduate-FYP-feasible edge research direction with a real story, a falsifiable claim, an auditable distinction from direct literature, and a useful negative-result path.

The scope is intentionally broad: edge AI, sensing, systems, reliability, privacy, networking, resource management, and human-in-the-loop edge workflows are all eligible. No modality, application, hardware board, or algorithm family is preselected. Candidates should be computer-science contributions first, with a real story and a modest, non-duplicative connection to Bob Zhang's public work when that improves advisor fit.

## Current state

- Gate: Gate 1 - physical feasibility and paper-identity decision. No thesis is locked yet. `PRF-TR` is the only conditional candidate; the next decision is based on the Pi bring-up and fixed baseline matrix, not another broad mechanism search.
- Direction: **The palm/biometric branch has no surviving standalone FYP candidate.** P2-CTB is KILL: its planned direct-ROI protocol does not exercise target capture, ROI, presentation-attack detection, or a controlled sensor effect, while Yan 2024 materially occupies the resulting digital endpoint. P1/P3-P6 remain killed or audit-only by direct neighbors. **BIA-1 is also KILL as a thesis:** the available X-Palm design can at most support a broad-domain report, and ISO/IEC 19795-10:2024 plus recent shift-diagnosis work make its proposed certificate routine evaluation hygiene. The Pi matcher remains an engineering/runtime demonstration only.
- **Post-audit direction state (2026-09-03):** `START-WIT`, `CAUSE-NULL`, `OFFLINE-REV-NULL` and `PIN-WIT` are **KILL as positive FYP directions**. `START-WIT` combines established motor start supervision/direct speed feedback with early-time-series reject methods. `CAUSE-NULL` is established FDI fault isolability and sensor placement when formalized, while `OFFLINE-REV-NULL` is standard cache freshness/revocation handling. `PIN-WIT` is established interconnect testing, BIST and diagnostic test-pattern selection under a finite harness-fault model. After the weak-network audit, `PRF-TR` is the only **conditional PIVOT**: a finite physical-versus-digital action-rank evaluation or negative-result study for a non-personal edge inspection record. No thesis is locked or called novel. The next gate is the existing Pi bring-up and baseline matrix, not another mechanism search.
- **Advisor fit (boundary, 2026-09-03):** [GAP] the available Bob Zhang/PAMI material supports only general context around incomplete or unreliable observations and conservative decisions. It may motivate the problem framing, but it must not appear as novelty or contribution evidence for `PRF-TR`.
- Candidate status: P1 HOLD only as a data-gated protocol appendix; P2-CTB KILL; P3 KILL (broad scheme; audit only); P4 KILL; P5 KILL (generic uncertainty); P6 KILL/PIVOT; BIA-1 KILL standalone/preflight only. Earlier EBR-AIM, C3, S1/S2, SAP and AIV remain historical KILL/PIVOT evidence and are not the current direction.
- New reference-intervention round: PHT-2R is KILL. Automated pH/EC one- and two-point drift handling already covers the offset/sensitivity mechanism, uncertainty-driven calibration scheduling is a direct neighbor, and fixed maximum-separation two-point calibration is D-optimal under the proposed affine equal-noise model. LENS-RC is KILL as a thesis: chart metrology/self-test, passive camera-health monitoring and costly-observation routing are established; a reference chart can only support an optional, bounded camera-path preflight, never scene-record truth.
- New systems/lifecycle round: RWE is KILL because standard secure-update state machines already verify the manifest, expose pending-verify state, self-test and rollback after interrupted updates. SDC-X is PIVOT only as a labelled fault-injection/negative benchmark: heterogeneous re-execution is DMR/N-version redundancy, and agreement cannot certify correctness outside a stated independence/fault model. DCC-SPLIT, REUSE-WIPE and OFT are KILL controls.
- New storage/power round: FSD-WIT is KILL as a thesis. Physical power-cut plus recovery-oracle testing, bounded crash-state checking and a two-phase valid-prefix scan already occupy the proposed method and decision; a low-cost microSD experiment remains a configuration-characterization or negative appendix only. POF-ADM is instrumentation only; comparator/reset signals do not witness storage or acquisition truth.
- Remaining TTA lead: the no-label shadow-update `accept / keep / abstain` residual is KILL. Existing work covers label-free adaptation accuracy/model selection and proxy-risk alarms; with only inputs, logits, proxies and telemetry, target label mechanisms can reverse the source/candidate risk order without changing the observations. Allowing delayed labels instead collides with existing budgeted risk controllers.
- Outside-family round: QNN-DecisionGuard and active acoustic path self-check are KILL as known verification/self-diagnosis families. AL-FactorQueue is KILL: an observable factor is a transparent stratification baseline and an unobservable one cannot inform the queue; its scarce-label stream action is already occupied. UPM-EdgeBound is KILL: it restates known no-assumption target-risk non-identifiability, and ordinary telemetry leaves the counterexample unchanged.
- Transfer-decision round: TRC-X is KILL as a thesis. `release / do-not-release / trial-only` is ordinary acceptance/reliability demonstration sampling. Four to six independent boards cannot support a useful sampled-device-family bound, while exhaustive testing of only the purchased finite matrix is a table, not a transfer contribution. MFD-Release and MQ-Guard are direct diagnostic/calibration collisions; UOD-ReleaseBound and FIP-Transfer remain negative-result appendices only.
- Physical-observation/RF round: CSI baseline gates, magnetometer geometry witnesses, mmWave clutter checks and air-sensor diagnosis are KILL as occupied calibration/self-diagnosis families. UWB-RL-CAUSE is also KILL: multi-link UWB online trustworthiness already separates link/node/system state, fine-grained CIR/range credibility already has retain/delete/mitigate decisions, and passive target/reference radio summaries cannot identify a general physical root cause.
- Historical leads: prior work on risk-audited sensing and common-cause sensor degradation is available in ../archive/2026-08-edge-sensing/; it is a source of constraints and baselines, not a default thesis topic.
- Known constraints: [K] the user confirms that affordable components may be self-purchased; [K] the FYP runs for one year, with a runnable demo by 2026-12 and experiment expansion/optimization in 2027-H1. [K] The current user-confirmed core imaging inventory is a Raspberry Pi and Camera NoIR v2. Earlier RGB-camera/IR-illuminator inventory statements are [GAP] until physically verified; PRF-TR must not require them. Exact board model, delivery timing, power instrument, and budget remain [GAP] for any future candidate. No personal data, production service, or safety actuation is permitted.

## Reading order

1. [00-project-charter.md](00-project-charter.md)
2. [01-candidate-register.md](01-candidate-register.md)
3. [02-decision-log.md](02-decision-log.md)
4. [03-evidence-ledger.md](03-evidence-ledger.md)
5. [05-ebr-aim-prospectus.md](05-ebr-aim-prospectus.md)
6. [06-p2-ctb-prospectus.md](06-p2-ctb-prospectus.md) (superseded hypothesis)
7. [07-palm-direction-matrix.md](07-palm-direction-matrix.md)
8. [08-biometric-second-round-gate.md](08-biometric-second-round-gate.md)
9. [14-ir-cause-working-prospectus.md](14-ir-cause-working-prospectus.md) (current conditional working direction)
10. [15-start-wit-working-prospectus.md](15-start-wit-working-prospectus.md) (current primary candidate)
11. [16-start-wit-pilot-protocol.md](16-start-wit-pilot-protocol.md) (first feasibility/kill gate)
12. [17-direction-gate-decision.md](17-direction-gate-decision.md) (current direction and continue/kill rules)
13. [18-direction-comparison.md](18-direction-comparison.md) (surviving-direction decision matrix)
14. [19-minimum-hardware-bom.md](19-minimum-hardware-bom.md) (feasibility-gate procurement and wiring)
15. [20-start-wit-advisor-one-pager.md](20-start-wit-advisor-one-pager.md) (advisor-facing research direction)
16. [21-start-wit-direct-neighbor-contrast.md](21-start-wit-direct-neighbor-contrast.md) (task/input/action/endpoint collision audit)
17. [22-start-wit-preregistration.md](22-start-wit-preregistration.md) (truth/action separation and pilot hypotheses)
18. [23-start-wit-data-schema.md](23-start-wit-data-schema.md) (episode schema and analysis rules)
19. [24-start-wit-acquisition-architecture.md](24-start-wit-acquisition-architecture.md) (synchronised policy acquisition and truth isolation)
20. [25-start-wit-policy-spec.md](25-start-wit-policy-spec.md) (transparent baselines and sequential policy)
21. [26-round-18-reconciliation.md](26-round-18-reconciliation.md) (independent divergence/validation reconciliation)
22. [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md) (superseded next-audit state)
23. [28-round-20-null-boundaries-reconciliation.md](28-round-20-null-boundaries-reconciliation.md) (current direction status and search reset)
24. [29-round-21-pin-wit-reconciliation.md](29-round-21-pin-wit-reconciliation.md) (PIN-WIT closure and evidence-needed reset)
25. [30-round-22-prf-tr-reconciliation.md](30-round-22-prf-tr-reconciliation.md) (current conditional physical-versus-digital action-rank direction)
26. [31-round-23-prf-tr-final-validation.md](31-round-23-prf-tr-final-validation.md) (final validation gate and paper identity)
27. [32-prf-tr-data-schema.md](32-prf-tr-data-schema.md) (minimum data schema and first pilot)
28. [33-prf-tr-research-prospectus.md](33-prf-tr-research-prospectus.md) (advisor-facing research prospectus and long-term gate plan)
29. [34-prf-tr-advisor-one-pager-cn.md](34-prf-tr-advisor-one-pager-cn.md) (Chinese advisor one-page brief)
30. Historical context only when relevant: [../archive/2026-08-edge-sensing/README.md](../archive/2026-08-edge-sensing/README.md)

## Update rule

Only the coordinator may modify active/, after reading both the divergence and validation packets for the current round. Every claim entering this directory needs a source, scope, and status label: [K], [E], [C], [GAP], or [KILL].

## Historical Pi 5 RGB/NoIR round [superseded hardware assumption]

- [GAP / historical] Earlier notes state that the user had a Raspberry Pi 5B
  (8 GB RAM, 64 GB card), an official RGB camera, an official NoIR camera, an
  IR illuminator, and the required adapter/cable hardware. That inventory has
  not been reverified. The current executable protocol assumes only the
  user-confirmed Raspberry Pi and Camera NoIR v2.
- [K] Generic adaptive camera, exposure, frame-rate and modality-selection claims are occupied by Lens (ICLR 2025), AdaptiveISP (NeurIPS 2024), AdaptiveAE (ICCV 2025), CM-ASAP (MIPR 2024) and related multimodal selection. A Pi implementation does not create a thesis contribution.
- [KILL] A new task-aware frame filter, modality router, semantic compressor or RAW-to-RGB ISP is also a direct method-family collision: TKDE 2024 task-aware data selectivity, Raw-JPEG Adapter (arXiv 2025), and TA-ISP (CVPR 2026) already make the corresponding edge/RAW task-conditioning claims. Any remaining hypothesis must be a finite physical endpoint with a fixed action and matched cost, not a new adaptive algorithm.
- [KILL] ACR-MODE, BURST-COMP, EV-EXPO, MOD-MISSING and generic ASI-IR/OPT-WIT are adaptive-sensing or passive-health mechanisms occupied by direct neighbors. [PIVOT] CAL-TRANSPORT, PHY-MASK and FULL-CAP are bounded preflight/negative benchmarks. [HOLD/PIVOT] only the active IR-CAUSE exact-marker value-of-information test remains Amber.
- [K] The standard Camera Module 3 has an IR-cut filter while NoIR omits it, so they are distinct observation paths, not interchangeable RGB/NIR labels. Raspberry Pi product brief, p. 3: https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief
- [K] Pi 5 multi-camera operation does not guarantee synchronized 3A behavior. Static sequential targets are valid; moving paired-camera claims require an independent timing oracle. Raspberry Pi camera documentation: https://www.raspberrypi.com/documentation/computers/camera_software.html
- [GAP] Exact camera revision, illuminator wavelength/power/diffuser and eye-safety specification, mount geometry, OS image, and capture-energy measurement remain to be recorded.

## Physical-failure transfer round [Amber]

- [KILL] Broad claims that digital corruption, synthetic missingness or simulated camera faults fail to represent real-world robustness are already directly studied by Agnihotri et al. (CVPRW 2025), Liao et al. (CVPRW 2025), MultiCorrupt and MSC-Bench. [PIVOT] The only defensible residual is a finite, preregistered transfer audit on the confirmed Camera NoIR v2 path; an extra camera is optional instrumentation, not a prerequisite.
- [PIVOT] **PRF-TR / PHY-MASK / FULL-CAP** may compare policy/risk rankings on paired digital and physical fault cells using an exact printed-code oracle, independent fixture labels, and matched capture/energy budgets. They cannot claim a general physical-failure guarantee or universal simulation invalidity.
- [PIVOT (Amber)] **IR-CAUSE** may test whether an optional IR-on intervention adds identifiable information for a named low-light versus transparent-cover pair. It must beat a fixed visible-then-IR policy, conservative escalation and an IR-ratio threshold, or report non-identifiability.
- [HOLD (Amber), high collision] FLICK-PHASE requires a photodiode timing oracle and must survive rolling-shutter flicker/synchronization neighbors. [PIVOT] PWR-WIT is likely instrumentation unless supply telemetry changes false-retain at equal image-only cost. [PIVOT/KILL] RS-DRIFT is bounded downstream validation only because rolling-shutter self-calibration and timing apparatus are direct neighbors.
- [K] Validation's strongest direct neighbor is Agnihotri et al., *Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?*, arXiv v1 2025-05-07, Secs. 1, 3, 4.1-4.2, 5: aggregate proxy correlation can be high while per-corruption correlations are weak. This kills the broad claim but leaves the finite optical/action endpoint Amber.
- [GAP] No source inspected establishes the Pi-specific physical intervention protocol or its effect size. A physical pilot demonstrating a preregistered rank inversion is required before thesis promotion.
- The executable pre-registration draft is [09-physical-transfer-pilot-protocol.md](09-physical-transfer-pilot-protocol.md). It defines the independent marker oracle, physical/digital cells, matched-cost baselines, two-world test, and promote/kill criteria.

## Application re-opening: printed authentication [KILL]

- A natural RGB/NoIR story is edge verification of a printed copy-detection pattern (CDP): a clerk decides `genuine / counterfeit / inspect`, with a known digital template and physical genuine/copy labels. This has a real decision and cheap ground truth, but the research endpoint is already occupied.
- Oleksiyuk et al., *Authentication of Copy Detection Patterns via Cross-Camera Dual-Synthetic Referencing*, arXiv v1 2026-05-29, Secs. 1-6, explicitly combines the digital template, an enrolled physical capture, cross-camera translation, heterogeneous mobile cameras and low-end verification (https://arxiv.org/abs/2605.31292). Atoki et al., WACV 2026, uses printer-signature-conditioned diffusion for CDP authentication (https://openaccess.thecvf.com/content/WACV2026/html/Atoki_Diffusion-Based_Authentication_of_Copy_Detection_Patterns_A_Multimodal_Framework_with_WACV_2026_paper.html).
- [KILL] New CDP detector, RGB/NoIR fusion, printer classification, or low-cost Pi deployment is not a defensible thesis. A bounded physical-vs-digital capture audit could still be an appendix, but it does not replace PRF-TR's transfer gate.

## Active-diagnosis collision update [Amber]

- [KILL] A broad claim that an active sensing intervention is a new way to diagnose perception faults is occupied by Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv v1 2025-09-22. It formalizes passive/active FDI and selects control inputs by an Effective Information criterion (https://arxiv.org/abs/2509.18460, abstract and Sec. 1).
- [KILL] Generic system-centric edge sensor diagnosis/recovery is also occupied by Yu et al. (Measurement 2025), which combines anomaly classification, physical-source rules and local recovery (https://doi.org/10.1016/j.measurement.2025.119994).
- Consequently, **IR-CAUSE is not a causal-diagnosis method candidate**. It remains Amber only as a finite value-of-information measurement: does the specific IR-on action improve a named two-world marker decision at matched cost, relative to fixed two-shot and passive baselines? A positive result would be a bounded empirical boundary, not a new counterfactual framework.

## Active-viewpoint re-opening [KILL]

- A pan-tilt extension could let the edge node choose a new view when a marker is occluded or ambiguous. However, active viewpoint selection and uncertainty/information-gain planning are established: Huang et al. (NeurIPS 2024) select viewpoints using predicted representation disparity (https://papers.neurips.cc/paper_files/paper/2024/hash/2360da01c2ed6592bb691326424de184-Abstract-Conference.html), and uncertainty-driven pan-tilt view planning already targets tracking failure (Dai et al., https://doi.org/10.1016/j.asoc.2021.107459).
- [KILL] New pan-tilt planning, next-best-view scoring, or “rotate until confidence rises” is not a defensible thesis. A bounded exact-marker occlusion/action-cost audit could be an appendix, but it does not replace the physical-transfer gate.

## Polarization/material re-opening [Amber]

- [KILL] Generic polarization restoration, transparent-film removal, glare reduction, moisture/material classification, stress measurement, or polarizer-based security defense are occupied by Tang (CVPR 2024), PolarFree (CVPR 2025), Khandaker (2024), Laser Shield (DAC 2024), and recent material/stress benchmarks. A clip-on filter or Pi deployment is not a contribution.
- [HOLD (Amber)] **POL-GLARE-VOI** is a narrow value-of-information test: does one controlled polarizer intervention reduce false-retain for a printed marker behind a transparent cover, at matched capture/energy cost, against no-filter, fixed-filter, fixed-two-shot, scalar-quality and digital-deglare baselines?
- [PIVOT (Amber)] **POL-WET-STATE** can map dry/wet states for one declared surface family across held-out illumination, but cannot claim generic moisture/material sensing. **POL-STRESS-TRUST** is only a bounded exact-code failure sentinel; no stress magnitude or safety claim. **POL-TRANSFER-REAL** is another finite physical-vs-digital audit and should not replace PRF-TR.
- Independent labels, manual/logged exposure, filter angle, lux, energy and held-out specimen/lamp cells are mandatory. A single external polarizer is not a full-Stokes sensor; report intensity ratios only. If fixed filters or RGB quality features are Pareto-optimal, kill the candidate.
- A runnable pre-registration draft for the surviving optical endpoint is [10-polarization-glare-pilot-protocol.md](10-polarization-glare-pilot-protocol.md).

### Purchase rule

Only purchase hardware that adds an independent observation or a controlled intervention: a rigid camera/target mount, illuminance meter or calibrated light source, USB inline power meter, and a safe transparent-cover/fixture kit. A second similar camera or a larger model is not justified until it changes the observation model and survives direct-neighbor audit.
## Cross-device / cross-illumination transfer re-opening [Amber]

- [K] Cross-camera color transfer and adaptive camera control are occupied by CCMNet (ICCV 2025), Punnappurath et al. (2025), and Lens (arXiv v3, 2026). Online calibration monitoring and trigger scheduling are occupied by Moravec & Sara (2024) and Wei et al. (2024). These direct neighbors kill a new color-mapping, panel-sufficiency, or recalibration-scheduling mechanism.
- [PIVOT] **XFER-ACT** may remain only as a finite, preregistered RGB/NoIR action-rank audit: source-calibrated `RGB`, `NoIR+IR`, and fixed two-shot policies are evaluated on blocked device/lamp cells with an exact printed-code oracle and matched joules. It cannot claim a camera-family transfer guarantee; RGB/NoIR device swap is confounded with IR-cut modality.
- [KILL] **LUX-VOI** is not a thesis mechanism. CIE S 017:2020 defines lux as a photopic spectral weighting, so equal-lux spectra can yield different NoIR utility; image luma/AE metadata plus fixed two-shot controls are mandatory. A lux board is instrumentation only unless a matched-spectrum pilot shows incremental value.
- [KILL/PIVOT] **PANEL-GATE** cannot use a diffuse reference panel as scene truth for local marker glare/focus; **CAL-SCHED** is standard online calibration monitoring. **REAL-DIG-RANK** is a bounded negative benchmark because Agnihotri et al. (CVPRW 2025) already occupy the broad synthetic-versus-real proxy question.
- Strongest direct neighbor is Ma et al. (arXiv 2607.14760, 2026), which evaluates camera-disjoint threshold transfer for passive camera-health monitoring. The only residual worth testing is an active exact-marker intervention endpoint, not passive health or calibration.
- No lux sensor or extra camera should be purchased for a thesis claim until the existing pair produces independent labels, manual/logged exposure, held-out lamp/material cells, and a repeatable action-rank inversion against fixed two-shot and scalar-quality baselines.
- The execution gates and Sep 2026--H1 2027 timeline are in [12-pilot-execution-gates.md](12-pilot-execution-gates.md); the lock decision remains empirical.

## Current execution gate [2026-09-03]

- The canonical next step is now the `PRF-TR` minimum fixture described in
  [32-prf-tr-data-schema.md](32-prf-tr-data-schema.md), not the older
  `START-WIT` or optical pilot notes. Those notes remain historical backup
  evidence and are not a parallel purchase order.
- A workspace audit on 2026-09-03 found no `PRF-TR` physical data, acquisition
  code or hardware log. The current evidence is therefore a preregistered
  protocol only; no empirical result has been collected.
- Do not claim that the weak-network constraint improves anything until a local
  deadline, disconnected decision and upload-delay/remote baseline are
  measured. The first acceptance test is instrumentation and truth-channel
  stability, not model accuracy.
- The immediate order is: bring the Pi online, pass the first-week acceptance
  checks, collect the preregistered episodes, then decide whether `PRF-TR`
  continues as a finite evaluation or is retained only as a bounded null.

## Round-11 validation reconciliation [Amber]

- The independent packet [round11 validation](../ops/validation/2026-08-31-round11-validation.md) audited the newer CSI/UWB/magnetic/mmWave/gas, privacy/resource, physical-intervention, and RGB/NoIR synchronization/risk-routing branches.
- **KILL:** `CSI-BaselineGate`, `UWB-RL-CAUSE`, `MAG-GeometryWitness`, `MMW-ClutterWitness`, `AQ-ReferenceFreeAudit`, `SCHED-PUB-STREAM`, `PSI-EVENT-JOIN`, `RVK-LOCAL-LEASE`, `DP-BUDGET-MICROEDGE`, `FLICK-PHASE`, `RS-DRIFT`, generic RGB/NoIR adaptive or Bayesian-risk routing, passive optical health, and standalone synchronization.
- **PIVOT:** `PWR-WIT` is instrumentation-only; `CRDT-ESCROW-LIMIT` is a baseline/negative replication; `PRF-TR`, `PHY-MASK` and `FULL-CAP` are finite physical-versus-digital action audits; `PLAR-Safe` is only a negative privacy--deadline frontier.
- **HOLD (Amber):** `IR-CAUSE` only as a finite active-IR incremental-information test with independent physical labels. No candidate passes all three novelty audits. Full Yang/VCIP PDFs and a modern CRDT primary remain [GAP], not novelty evidence; RocSync and Kim--Baek full texts are now audited and their synchronization/alignment mechanisms are KILL.
- The next gate remains the preregistered finite Camera NoIR v2 pilot: exact printed-code oracle, independent fixture labels, logged exposure/white balance/timing/energy, held-out cells, and fixed two-shot/scalar baselines. Optional IR actions may be added only after the illumination path is installed and logged.

## Round-12 physical-frequency divergence [Amber]

- The independent divergence packet proposed `IR-MOD-ID`, `LUX-AMBIG`, `ABSENCE-PULSE`, `IMU-BLUR-ATTR` and `EVENT-DROP`. These are hypotheses only; none is promoted.
- **HOLD (Amber):** `IR-MOD-ID` may test whether a two-frequency IR challenge adds incremental information beyond fixed two-shot and IR-ratio controls on two independently labelled physical worlds. This is a finite action-risk experiment, not causal diagnosis or a new active-sensing framework.
- **PIVOT (Amber):** `LUX-AMBIG` is only a matched-spectrum negative identifiability benchmark. Lux is an explanatory measurement; it cannot be treated as an NIR witness, and a BH1750 should not be purchased before the image-only gate is frozen.
- **PIVOT/KILL:** `ABSENCE-PULSE` repeats established visual-challenge and semantic active-probing families; `IMU-BLUR-ATTR` repeats IMU-assisted blur/motion estimation; `EVENT-DROP` is infeasible on the current low-cost platform and is already benchmarked. They are not thesis mechanisms.
- Round-12 validation confirms `XFER-ACT` remains a finite action-rank audit, `POL-GLARE-VOI` remains Amber only against fixed-filter/two-shot controls, and `IR-CAUSE` is the sole live pilot gate. A fixed RGB-then-NoIR+IR policy remains the strongest adversarial baseline.
- [KILL] Ke et al. (2026) already combine transparent-material inspection, wavelength-controlled illumination, full-factorial imaging variables, and edge deployment. A Pi transparent-defect detector or white/red/NIR comparison therefore remains an engineering baseline, not a new direction.
- [KILL] Flash-Splat (2024), Flash-Split (2024) and Tang (CVPR 2024) occupy active flash/no-flash transparent-surface separation and polarization-plus-transparent-film QR recovery. `IR-CAUSE`, `IR-MOD-ID` and `POL-GLARE-VOI` must not claim those mechanisms or applications; only the finite equal-joule action-risk endpoint remains [GAP]/Amber.

## Round-15 systems/raw divergence [Amber]

- The independent divergence packet proposed `SLOW-CAP`, `RAW-JPEG-GATE`, `EXIF-WIT`, `FRAME-ADMIT`, `PRIV-STORE` and `CHAIN-REPLAY`. A dedicated validation packet has now audited the new candidates; no candidate is PROMOTE.
- **KILL thesis / PIVOT replication:** `SLOW-CAP` is a finite stress-conditioned camera action test, but UCC 2025, Bian 2026 and Pi 5 queue/timeout work occupy generic timeout, screen-confirm and frame-admission mechanisms. It may only reproduce a bounded Pi/workload result and must beat static-timeout, latency-only and always-retry controls on exact-code action loss.
- **HOLD (Amber):** `RAW-JPEG-GATE` is the most distinct new observation hypothesis: a RAW-domain saturation/SNR witness may predict exact-code failure beyond JPEG luma/blur/decoder confidence at matched bytes, latency and joules. This is [C]/[GAP] until the purchased Camera Module 3 exposes a usable raw mode and a pilot demonstrates incremental value.
- **PIVOT (Amber):** `EXIF-WIT` remains a metadata-consistency preflight because the full ISM 2025 protocol/limitations and exact Pi metadata path are not verified.
- **KILL:** `FRAME-ADMIT`, `PRIV-STORE` and `CHAIN-REPLAY` are operational/privacy/provenance mechanisms already occupied by Stubbs 2025, PrivateEye/Sogabe 2025, ZIRCON 2024, C2PA/NIST and WWW Companion 2026. They remain baselines or negative demonstrations only.
- The next gate is now a short raw-capability preflight in parallel with the static RGB/NoIR pilot: prove raw capture, record one exposure as RAW plus JPEG, and compare RAW witness, JPEG-only, decoder confidence and fixed reacquisition under a held-out light block. A null is a valid result; no direction is locked.
- `RAW-JPEG-GATE` is now the only new systems/raw HOLD (Amber), but remains conditional on the raw-capability gate and matched-budget pilot.
- The executable preflight is [13-raw-jpeg-gate-preflight.md](13-raw-jpeg-gate-preflight.md); it is a feasibility/kill gate, not a direction lock.
- [KILL broad RAW story] Chen, Tai & Ma, AAAI 2024 already run a RAW detection pipeline and a RAW Corruption Benchmark for harsh environments, reporting +13.9 mAP over RGB on LOD-Snow (AAAI Vol. 38(2), pp. 1063-1071; official abstract/DOI: https://doi.org/10.1609/aaai.v38i2.27867). Berdan et al., ReRAW, CVPR 2025, pp. 11833-11843, also target efficient edge object detection from RAW. Therefore `RAW-JPEG-GATE` cannot claim that RAW is generally more robust or edge-suitable; only the narrow same-exposure exact-marker sufficiency/action test remains [GAP]/Amber.
- [KILL broad RAW-uncertainty story] Afifi et al., *Time-Aware Auto White Balance in Mobile Photography*, ICCV 2025, already use raw noise/SNR and chromaticity/edge histograms as camera-control features (paper and supplementary, ICCV 2025). Kaparounakis et al., *Digital methods to quantify sensor output uncertainty in real time*, Communications Engineering 2026, already propagate representation uncertainty on low-power hardware and evaluate an edge-detection consequence (Secs. “Representation uncertainty”, “Real-time on-device sensor uncertainty computation” and “Edge detection on uncertain data”). Thus a new RAW uncertainty score or raw-domain reliability monitor would collide; only the exact-marker matched-cost sufficiency experiment remains [GAP].

## Fiducial-decoding collision update [KILL]

- [K] DeepArUco++ (Image and Vision Computing 152, 105313, 2024; arXiv 2411.05552) already combines synthetic Flying-ArUco-v2 training, real Shadow-ArUco difficult-light testing, marker detection/corner refinement/decoding, and throughput comparisons (Secs. 3-5). Its Sec. 5.6 reports black-scene hallucinations, wrong IDs from small corner shifts, and synthetic-to-real mismatch.
- [KILL] A new Pi marker decoder, difficult-light dataset, or synthetic augmentation is therefore not a thesis mechanism. The surviving endpoint remains the finite retain/reacquire/unknown action-cost audit in [11-cross-device-action-rank-pilot.md](11-cross-device-action-rank-pilot.md), with DeepArUco++/ArUco as decoder controls rather than the contribution.

## Temporal/flicker collision update [KILL]

- [K] Ren, Lensgraf & Quattrini Li, *Improving the perception of visual fiducial markers in the field using Adaptive Active Exposure Control* (arXiv:2404.12055, 2024), already applies gradient-based active exposure control to fiducial-marker localization under harsh illumination and compares against AEC/GEC ([paper](https://arxiv.org/abs/2404.12055), abstract and Sec. 1).
- [K] Fukuda et al. (JAFST 2024, Vol. 29(2), pp. 135-153) already build an LED/logic device that measures frame interval, exposure time and rolling-shutter scan speed across cameras ([official article](https://www.jstage.jst.go.jp/article/jafst/advpub/0/advpub_875/_article/-char/en)). Automated rolling-shutter calibration with an LED panel is also established ([Optics Letters](https://doi.org/10.1364/OL.474375)).
- [KILL] `FLICK-PHASE` or `RS-DRIFT` cannot be promoted as a timing/calibration mechanism. A photodiode or LED board may be purchased only as an independent timing oracle for the finite XFER-ACT/PRF-TR pilot; any downstream action benefit must beat fixed exposure and fixed two-shot controls.

## Resource-constrained sensor-selection collision [KILL]

- [K] Singhal et al., *Resource-Efficient Sensor Fusion via System-Wide Dynamic Gated Neural Networks* (SECON 2024, DOI 10.1109/SECON64284.2024.10934843), already jointly selects sensor/data sources, DNN branches, network placement and resources under latency, quality, reliability and energy objectives ([official record](https://research.chalmers.se/en/publication/545985), abstract). This occupies a generic “adaptive modality choice under edge budget” claim.
- [KILL] `XFER-ACT` must not be framed as a new sensor-selection or energy-aware routing method. Its only remaining distinction is a finite physical-fault/action-risk audit with an exact external marker oracle; if fixed two-shot or scalar-quality controls match, stop.

## Acquisition-abstention guarantee collision [KILL]

- [K] Xu et al., *Look Again Before You Abstain: Budgeted Conformal Evidence Acquisition for Reliable Vision-Language Models* (arXiv:2606.16667, 2026-06-15), defines the three-way `answer / abstain / acquire` action and shows that naive post-acquisition reuse of a pre-acquisition conformal threshold breaks risk control; recalibration on the post-acquisition score restores validity (Secs. 1, 4.3, 5; [paper](https://arxiv.org/abs/2606.16667)).
- [KILL] A conformal/abstention wrapper is not a new FYP mechanism. Any RGB/NoIR pilot that reports `retain / reacquire / unknown` must freeze thresholds on the complete action pipeline and treat fixed two-shot/always-reacquire as controls. The remaining contribution, if any, is only the finite physical observation boundary.

## Sensor-fault benchmark collision update [KILL]

- [K] Windmann et al., *Benchmarking Sensor-Fault Robustness in Forecasting*, arXiv:2605.10822v1 (2026-05-11), already provides a CPS-grounded sensor-fault benchmark with eight standardized value/timing/availability scenarios, a disjoint fault-transfer split, worst-scenario fault-time error, and explicit clean-MSE versus fault-time ranking disagreement ([paper](https://arxiv.org/abs/2605.10822), abstract and Secs. 1-5).
- [KILL] A broad `REAL-DIG-RANK` or `PRF-TR` claim that synthetic/clean rankings fail under sensor faults is occupied. The only residual is a finite camera-optical replication with an exact printed-code oracle and action/energy endpoint; it must state its distinction from SensorFault-Bench and may still yield only a bounded null.
- **Round-22 reconciliation (2026-09-03):** `CONTACT-EVIDENCE` is KILL: it reduces to a fixed sufficient predicate, established streaming/verifiable computation, or an unidentifiable physical-capture claim. `RF-EMUL-RANK` is PIVOT only as a finite emulator-to-physical negative audit. The weak-network story remains contextual for `PRF-TR`, not a separate networking contribution.
- **Current conditional candidate:** `PRF-TR` asks whether digitally injected camera faults preserve the ordering of `retain / reacquire / unknown` actions under named physical conditions, equal capture cost, and an independent exact-payload oracle. A repeatable held-out rank inversion that survives fixed two-shot, scalar-quality and always-review controls would be an empirical contribution; rank preservation or non-identifiability is the required negative result. No general synthetic-to-real, camera-family, maintenance-completion, or weak-network guarantee is allowed.
- **Round-23 validation (2026-09-03):** `PRF-TR` is **PIVOT**, not a method lock. It is viable only as a bounded evaluation/negative-result paper identity. The deployment gate is engineering infrastructure; the research endpoint is the held-out physical-versus-digital action ranking. A real maintainer/release workflow is still [GAP], so lab results must be labelled as a finite benchmark until such a workflow is documented.
- **Workflow grounding (2026-09-03):** Official SAP, Salesforce, and ServiceNow field-service documentation confirms that barcode/asset scanning, offline task execution, local work-order updates, and later synchronization are real workflow operations. This strengthens the motivating story only; it does not establish a PRF-TR research gap or replace a physical pilot.

## Active acquisition / device-shift collision update [KILL]

- [K] Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065 (published 2026-08-10), already combines low-cost screening, high-information confirmation, uncertainty/OOD escalation, a watchdog, device/condition shift and few-shot commissioning under resource costs ([official article](https://www.mdpi.com/1424-8220/26/16/5065), Secs. 1, 3.1, 5.1 and 8).
- [KILL] `ASI-IR` as a generic adaptive modality/energy method is occupied. `IR-CAUSE` is downgraded from `HOLD` to `PIVOT (Amber)`: only a finite physical exact-marker intervention test remains, and it must beat Bian-style conservative escalation translated into a fixed two-shot/always-reacquire control.

## Round-17 two-Pi alternatives and narrow validation [Amber]

- The 2026-09-02 divergence packet considered `FCL-PI-NB`, `COOP-MARK`, `SPLIT-LEAK-AUDIT` and `LINK-OUTAGE-REPLAY` as alternatives to the optical branch. None was promoted: FCL is an explicit negative/replication benchmark, cooperative marker exchange is a finite physical action audit, split-inference leakage is an appendix, and link replay is systems hygiene with low novelty probability.
- The 2026-09-03 validation audit confirms the broad mechanisms are occupied. `IR-CAUSE` is **KILL** as causal diagnosis, passive camera health, or generic adaptive sensing; it remains **PIVOT (Amber)** only as a finite IR-on incremental-information experiment. `RAW-JPEG-GATE` remains **HOLD (Amber)** only for a capability and matched-cost preflight.
- The strongest direct neighbors are Han et al. (2025) for active perception-fault diagnosis, Bian et al. (2026) for resource-aware screen/confirm acquisition, Ma et al. (2026) for passive optical health, Chen et al. (AAAI 2024) and ReRAW (CVPR 2025) for broad RAW claims. These kill broad method claims; they do not establish the exact Pi 5 printed-marker endpoint.
- The next gate is empirical and finite: verify independent payload truth, preassigned physical labels, logged exposure/WB/timing, fixed RGB -> NoIR+IR and always-reacquire controls, and (for RAW) a stable same-exposure RAW/JPEG pair with charged storage/unpacking/energy cost. A null or non-identifiability result is valid and should close the claim rather than trigger a new model search.
- No direction is locked. No additional camera, lux sensor, or larger model is justified before this gate produces a repeatable held-out action-cost effect.
