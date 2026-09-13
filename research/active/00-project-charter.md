# Project Charter

## Research goal

Select one computer-science edge-computing FYP direction that is meaningful, novel in a scoped and auditable sense, feasible for an undergraduate project, and modestly adjacent to Bob Zhang's research where that increases advisor fit.

## Quality bar

- A concrete user, decision, error consequence, and reason edge constraints change the problem.
- A claim that a direct baseline can refute.
- A literature distinction defined by task, observation model, action, evaluation endpoint, or guarantee.
- A core CS contribution in an algorithm, systems mechanism, data/evaluation protocol, reliability/privacy/resource method, or explicit theoretical boundary.
- A minimum experiment achievable with confirmed data, hardware, compute, time, ethics, and advisor support.
- A negative-result or pivot path that remains scientifically useful.

## Explicit non-goals

- Choosing a topic merely because it can run on a Raspberry Pi or another edge board.
- Treating a model swap, quantization result, dashboard, demo, or dataset transfer as a research contribution.
- Claiming global novelty or treating lack of search results as evidence.
- Locking a topic before the feasibility gate.
- Treating Bob Zhang's prior papers, lab affiliation, or a hardware prototype as the innovation. His research should guide advisor fit and direct-neighbor search, not replace the gap.

## Confirmed execution window

- [K] One-year FYP. A runnable benchtop demo is required by 2026-12; the 2027-H1 period is available for held-out cells, repetitions, analysis, and optimization.
- [K] Affordable components and sensors may be self-purchased.
- [KILL] The former C3 three-peer SBC topology is retained only as a possible replication appendix, not as a default FYP dependency or evidence of a contribution.

## Current biometric gate [Amber]

- **P2-CTB is superseded and KILL.** A direct generated ROI sent to a target matcher does not measure a target-device/sensor/presentation pathway; Yan 2024 already evaluates template reconstruction across algorithms/datasets. A Pi target only adds resource measurements. It must not be resumed by changing the decoder or enlarging a device/model matrix.
- **BIA-1 is KILL as a standalone direction.** X-Palm's compound scanner/mobile design permits only a broad-domain result, not a named device/sensor effect. ISO/IEC 19795-10:2024 already requires the factor controls, uncertainty and non-unique-attribution disclosure that BIA-1 would automate; recent shift diagnosis/decomposition work occupies the generic method family. Retain it only as a preflight/appendix.
- The palm branch remains a set of controls, reproducibility artifacts and an optional Pi demo. The broader edge search resumes; no new biometric method is to be promoted without a separately authorised, controlled data resource and a distinct task/action/endpoint.

## Current reference-intervention gate [Amber]

- **PHT-2R is KILL.** Cho et al. (2024) already automate one- and two-point pH/EC normalization for offset and sensitivity drift, while Hurst et al. (2025) occupy uncertainty-driven calibration scheduling. Under the candidate's own stable affine, equal-noise model, the widest valid pair is the fixed D-optimal design; `accept / unknown` is only calibrated interval reporting.
- **LENS-RC is KILL as a thesis; preflight only.** ISO 12233:2024 and IEEE 1858-2023 establish controlled chart image-quality measurement; Ma et al. (2026) is a direct passive camera-health baseline; costly chart acquisition is a standard partial-monitoring decision. A chart is evidence about the camera/lens/illumination path, not independent truth about a scene-derived record. A small, non-personal bench may still test a named camera-path condition, but neither outcome reserves the FYP slot.

## Current systems/lifecycle gate [Amber]

- **RWE is KILL.** RFC 9019 and ESP-IDF's documented `pending-verify`, self-test, rollback and anti-rollback behavior already implement the benign interrupted-update recovery decision. A reader of the same immutable manifest/boot state is redundant under the stated non-adversarial model; a later mutable-app fault is outside both observations.
- **SDC-X is PIVOT only as a labelled negative benchmark.** Duplicate/heterogeneous execution is an established DMR/N-version mechanism. A two-board match proves correctness only under an explicit fault-independence model, while disagreement does not identify the correct result. It must not be promoted by counting seeded software corruptions as field hardware incidence.

## Current storage/power gate [Amber]

- **FSD-WIT is KILL as a thesis.** CrashMonkey/ACE, Pathfinder (2025) and physical power-fault recovery testing already supply the bounded crash, external-oracle and recovery-check method family. For deterministic synthetic records, a two-phase valid-prefix scan implements `retain / unknown` directly; for real sensor values it cannot establish acquisition truth. A one-card study cannot establish cross-card transport, especially for consumer media with mutable BOM/controller configurations.
- **POF-ADM is instrumentation only.** A power-fail comparator/reset marker can stratify a cut experiment but cannot observe an opaque card commit or a sensor's semantic value. It survives only if a preregistered equal-unknown-rate comparison proves incremental value over the valid-prefix baseline.

## Current adaptation gate [Amber]

- **Unlabeled TTA accept/rollback is KILL.** AETTA, agreement-based TTA selection and Schirmer et al.'s risk monitor occupy label-free accuracy/model-selection/proxy-alarm claims. Under only input, prediction, proxy and telemetry observations, identical observations can have opposite source-versus-candidate true-risk order. A delayed-label controller is a different, already occupied action family. No adaptive update may be claimed reliable without a named, independently testable semantic witness or restricted-shift theorem.

## Current outside-family gate [Amber]

- **AL-FactorQueue is KILL.** TActiLE already has the online irreversible stream, finite label-batch, local constraint and post-retraining endpoint. If a physical factor is known before review, fixed factor quota/stratified sampling is the decisive baseline; if it is not known, it cannot be an online selection input. Unseen factor-cell performance is not identified without a separately justified structural relation from factor to task labels.
- **UPM-EdgeBound is KILL.** Its unlabeled target-risk impossibility is an instance of Garg et al.'s result. Keeping device telemetry constant leaves two worlds with identical trace and opposite risk. A new contribution would require a named physical witness and a proof of its sufficiency/minimality against a restricted shift family; no such object exists yet.
- **QNN-DecisionGuard and ASV-PathCheck are KILL as mechanisms.** Quantisation verification and active acoustic sensor self-diagnosis are existing families; board substitution, a test bench or a router does not change the direct endpoint.

## Current transfer gate [Amber]

- **TRC-X is KILL as a thesis.** Reliability demonstration/acceptance sampling already implements future-population `accept / reject / no decision` under stated consumer-risk and population assumptions. With 4--6 independent device units, even zero device failures leave an optimistic 95% i.i.d. device-failure upper bound of 0.527--0.393. Repeating load/fault cells does not create new device samples; exhaustively testing the finite purchased matrix removes the transfer claim.
- **MFD-Release and MQ-Guard are KILL.** Cross-machine fault diagnosis and low-cost calibration/recalibration are direct task families. **UOD-ReleaseBound and FIP-Transfer are negative appendices only:** the former restates known no-label target-risk non-identifiability, while the latter cannot turn seeded-fault coverage into field-fault transfer without a separately validated mapping.

## Current RF / physical-observation gate [Amber]

- **UWB-RL-CAUSE is KILL as a thesis.** Peterseil et al. (2024) already use local UWB link/node/system indicators, CIR anomalies and sequential untrusted-anchor filtering; Yang et al. (2025) already perform CIR/range credibility, fine-grained error-source classification and retain/delete/mitigate decisions. The residual target-path versus infrastructure-cause label is not identifiable from passive target/reference radio summaries, and any deterministic policy is reproduced by an equally informed classifier.
- **CSI-BaselineGate, MAG-GeometryWitness, MMW-ClutterWitness and AQ-ReferenceFreeAudit are KILL.** Existing CSI abstention, magnetic calibration/localization, mmWave self-calibration/state detection and edge gas-sensor self-diagnosis respectively occupy their direct mechanism families.

## Remaining constraints [GAP]

- Exact camera revision, illuminator specification, power-measurement instrument, mount, delivery timing, and budget ceiling.
- Data access, collection permission, and required labels.
- Team size, programming/theory strengths, and advisor preferences.
- Compute budget and any deployment/network restrictions.

## Historical Pi 5 RGB/NoIR adaptive-sensing gate [Amber]

- **ACR-MODE, BURST-COMP, EV-EXPO, MOD-MISSING and generic ASI-IR/OPT-WIT are KILL as thesis mechanisms.** Lens (ICLR 2025), AdaptiveISP (NeurIPS 2024), AdaptiveAE (ICCV 2025), CM-ASAP (MIPR 2024), QIC (SECON 2024) and Bian et al. (Sensors 2026) occupy adaptive camera-parameter, exposure, frame-rate, modality and resource-aware screen-confirm actions under device/condition shift.
- **CAL-TRANSPORT is PIVOT** to a bounded RGB-to-NoIR threshold-shift preflight; it cannot be called a transfer theorem or new algorithm.
- **PHY-MASK and FULL-CAP are PIVOT** finite physical-versus-digital negative benchmarks. They can test whether simulated missing/noisy masks or digital corruptions preserve action rankings on a printed-marker task, but cannot claim a general physical-failure guarantee.
- **IR-CAUSE is PIVOT (Amber)** only as a physical value-of-information hypothesis. It requires independently assigned clean/contaminated states, manual or logged AE/WB, an energy measurement, fixed two-shot/conservative-escalation controls, and a two-world identifiability test. Generic ASI-IR and passive OPT-WIT are killed; none is promoted or locked.

## Current physical-failure transfer gate [Amber]

- **PRF-TR / PHY-MASK / FULL-CAP are PIVOT only.** Agnihotri et al. (CVPRW 2025, arXiv:2505.04835v1, Secs. 1, 3, 4.1-4.2, 5) directly studies synthetic-versus-real corruption proxy validity; Liao et al., MultiCorrupt and MSC-Bench occupy simulated missing/noisy/crash/frame-loss benchmarks. The surviving claim is finite and auditable: paired digital/physical fault cells on the confirmed Camera NoIR v2 path, an exact printed-code oracle, and matched action/energy costs. No universal simulation-invalidity or physical-failure guarantee is allowed.
- **IR-CAUSE remains PIVOT Amber.** It can only ask whether an optional IR-on intervention adds information for a named low-light versus transparent-cover pair. It must beat fixed visible-then-IR, conservative escalation, an IR-ratio threshold, and passive quality controls, or return a two-world non-identifiability result.
- **FLICK-PHASE remains HOLD Amber with high collision risk; PWR-WIT is likely instrumentation; RS-DRIFT is PIVOT/KILL as a thesis.** Each needs an independent timing/power oracle and must show a downstream retain/reacquire frontier not reproduced by fixed settings.
- Promotion gate: preregister physical cells, independent intervention labels, lux/power/exposure logs, exact source payload, and a minimum repeatable action-rank inversion or mechanism-level effect. Otherwise report a bounded null/replication appendix and do not lock the FYP direction.

## Current cross-device transfer gate [Amber]

- [PIVOT] `XFER-ACT` is restricted to a finite RGB/NoIR action-rank audit on blocked camera/lamp/material cells with an independent exact-code oracle and matched capture energy. CCMNet (ICCV 2025) and Lens (2026) occupy camera-disjoint transfer and adaptive camera-control mechanisms, so no transfer guarantee or new color-mapping method is claimed.
- [KILL] `LUX-VOI` as a thesis, `PANEL-GATE` as a scene-risk certificate, and `CAL-SCHED` as a scheduling mechanism. CIE S 017 lux is photopic rather than NIR information; panels cannot witness local glare/focus; online calibration monitoring is established.
- [PIVOT] `REAL-DIG-RANK` is only a finite synthetic-versus-physical negative benchmark, since Agnihotri et al. (CVPRW 2025) occupy the broad proxy-validity question.
- The next gate is the preregistered [11-cross-device-action-rank-pilot.md](11-cross-device-action-rank-pilot.md). No extra camera or lux sensor is justified before the pilot produces independent labels and a repeatable held-out rank inversion against fixed two-shot and scalar baselines.
