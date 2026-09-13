# Validation Audit: 2026-09-03 offline maintenance-record photo decision

## Decision investigated

Whether a weak-network factory/site/mobile-maintenance story makes the following a defensible edge FYP contribution: a local node photographs a non-personal printed component label, then chooses `accept`, one controlled optical recapture, or `manual review` under clean-low-light versus transparent-cover/glare cells, with exact label/work-order truth and matched latency/energy.

## Claim under test

The strongest charitable claim is not that a Pi, a 3D box, or offline storage is new. It is: a pre-action local observation can justify one named second optical observation and improve held-out maintenance-record action loss over fixed capture policies and manual review.

The claimed maintenance label must be separated from the physical machine state. A pre-generated QR/AprilTag can establish that the *printed record was decoded correctly*. It cannot establish that a part was installed, that work was completed, or that the work order is semantically valid.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Lens selects camera parameter candidates from unlabeled scene/model evidence under capture-latency tradeoffs. BCEA implements `answer / abstain / acquire` under a budget. Ren et al. actively optimize camera exposure for visual fiducials in adverse/low lighting. Tang et al. use transparent-film optical observations for industrial QR/OCR. | The proposed path uses a fixed cheap RGB/NoIR/IR fixture, a non-personal maintenance record, and exact code equality rather than VLM claims, localization, or film reconstruction. This changes scope, not the active-acquisition mechanism. | High. |
| Exact-claim collision | A generic `accept / recapture / review` policy is an instance of budgeted evidence acquisition. A generic preview-to-IR/exposure choice is an instance of adaptive camera control. A transparent-cover QR/OCR detector/restorer directly collides with turning the story into transparent-film recognition. | No inspected source jointly evaluates the exact purchased RGB/NoIR path, a frozen action set, independently assigned low-light/cover cells, exact-code false-retain, and joules. This is a narrow protocol gap, not evidence of an unoccupied method. | High for method claim; medium for finite protocol. |
| Boundary and impossibility | Low light and a transparent cover can yield the same allowed pre-action observation (preview, luma/blur, metadata, even photopic lux) while the best action differs. Offline operation does not change that observation model. A fixed two-shot may bypass the ambiguity; if it does, no router is needed. | A finite action-risk table is identifiable if physical cells are assigned before capture, exact payload truth is independent, exposure/WB/timing are fixed or logged, and the target is static. It identifies only this fixture/action family, never general camera health, cause, field completion, or a transfer guarantee. | High. |

## Assumption and identification audit

1. **Offline is narrative, not a new input.** If the local node never compares an online service with the local decision, weak connectivity changes deployment convenience only. It cannot establish a new visual decision mechanism.
2. **The action must change information.** A same-settings retry has no declared discriminating observation model; it is a repeat sample and needs a stochastic-noise hypothesis. The only defensible controlled recapture is specified in advance, for example `NoIR + fixed IR`, manual exposure change, or a fixed polarizer. Otherwise “recapture” is an unbounded search action.
3. **Cause is not identified.** The fixture label (`clean low light` versus `transparent cover`) is not recoverable merely because an image is hard. IR response, luma, lux, decoder confidence, and blur are observations, not causal labels. If the policy claims to diagnose the cause, it is killed by a paired-world counterexample.
4. **Runtime truth is ambiguous.** If the expected work-order label is cached locally, exact equality turns the task into structured-code read verification; it does not verify the part or repair. If the expected label is not locally available, “exact work-order truth” exists only offline for evaluation and cannot support runtime acceptance. Both interpretations must be stated before data collection.
5. **Manual review must be operationalized.** Define a fixed local review artifact, reviewer input, latency and cost. A human who is allowed to use an unrestricted external work-order system is a stronger, unmatched oracle; that invalidates the matched-cost comparison.
6. **Two-camera timing is a blocker for motion claims.** The standard Camera Module 3 and NoIR are different optical paths; Pi multi-camera software does not guarantee synchronized 3A. The audit is admissible only for static labels unless a separate timing oracle is introduced.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Baek et al., *Lens: Adaptive Camera Sensor for Vision Models*, ICLR 2025; arXiv:2503.02170v3, 2026-05-19, https://arxiv.org/abs/2503.02170 | Unlabeled image/model confidence; chooses camera parameter candidates with capture-latency tradeoff | Model accuracy on physical sensor/light perturbations; Secs. 3.1-3.2, 5 | Preview-to-capture-action selection under a resource constraint | Kills generic adaptive RGB/IR/exposure routing. Leaves only a non-general finite fixture audit. |
| Xu et al., *Look Again Before You Abstain*, arXiv:2606.16667v4, 2026-07-21, https://arxiv.org/abs/2606.16667 | `answer / abstain / acquire`; crop/zoom/claim-specific intervention with fixed acquisition budget | Selective risk/coverage; Secs. 3, 4.2-4.4, 5 | Same three-action evidence-acquisition structure | Kills a conformal or generic abstention/acquisition wrapper. It also shows a policy and threshold must be calibrated jointly after acquisition. VLM claims differ from fixed-code reading. |
| Ren, Lensgraf & Quattrini Li, *Improving the perception of visual fiducial markers in the field using Adaptive Active Exposure Control*, arXiv:2404.12055v1, 2024-04-18, https://arxiv.org/abs/2404.12055 | Marker ROI and gradient score drive repeated exposure actions | Marker detection/localization under low and adversarial light; Secs. 3-4, Tables 1-6 | Active optical control for fiducial reading under difficult lighting | Kills a new adaptive exposure or marker-readability mechanism. The proposed action-loss endpoint and static maintenance story differ only in evaluation scope. |
| Tang et al., *Learning to Remove Wrinkled Transparent Film with Polarized Prior*, CVPR 2024, pp. 24987-24996, https://openaccess.thecvf.com/content/CVPR2024/html/Tang_Learning_to_Remove_Wrinkled_Transparent_Film_with_Polarized_Prior_CVPR_2024_paper.html | Four polarization observations, film prior, reconstruction | Industrial QR reading and text OCR under transparent film; Secs. 3-5, especially 5.3 | Transparent-film plus QR/OCR physical problem | Kills film-removal, glare-restoration, or transparent-cover QR/OCR novelty. A single RGB/NoIR action audit must not claim restoration. |
| Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv:2509.18460v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Passive/active fault diagnosis; selects interventions by effective information | Fault detectability/isolation; Secs. II-C, IV-D, V | Active intervention to infer a hidden perception cause | Kills causal-diagnosis framing for low-light versus cover. Leaves only a decision outcome that avoids cause claims. |
| Ma, Yan & Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions for Camera Tamper Monitoring*, arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Reference statistics and event state machine | Lens cover/photometric transition alarms; Secs. III-VI and Supplementary V/XII | Passive optical-path/photometric discrimination and threshold transfer | Kills camera-health monitoring and generic threshold-transfer language. Its declared out-of-scope cases also demonstrate that simple global statistics cannot identify every cover/defocus condition. |

## Strongest simple baseline

The decisive baseline is a deterministic fixed policy, not a learned selector:

1. `RGB only`;
2. `NoIR + fixed IR only`;
3. `fixed RGB then NoIR + fixed IR` two-shot;
4. `RGB quality threshold -> one fixed second observation` using luma, saturation, blur, decoder margin, and an IR-ratio where available;
5. `always manual review`; and
6. offline physical-cell oracle, reported only as an upper reference.

All policies must use the same marker decoder, fixed expected-label semantics, and the same maximum capture/review budget. Report false retain, false unknown, review rate, total latency, joules and action-conditioned exact-code error. If fixed two-shot or always-review is Pareto-optimal, the proposed local router is unnecessary.

## Contrarian result

**KILL as a positive FYP mechanism.** The weak-network maintenance framing supplies a plausible use case but no distinct computational observation, action, or guarantee. The optical method family is already occupied: adaptive sensor control, evidence acquisition, active fiducial exposure, transparent-film QR/OCR, active fault diagnosis, and passive optical monitoring each cover a core part of the proposed claim.

The likely empirical outcome is also a null: for a static printed label, fixed two-shot acquires the only extra optical evidence without needing to infer whether the problem is low light or cover glare. If review cost is acceptable, always-review is the lower false-retain control. A learned score only has value if it beats both on held-out sessions after its own calibration is frozen.

## Feasibility audit

| Item | Validation finding |
| --- | --- |
| Hardware | Existing Pi 5B, RGB/NoIR cameras and IR illuminator support a static fixture. Rigid mount, safe cover fixture and inline power measurement remain necessary. Illuminator wavelength/power/diffuser and actual camera revision are [GAP]. |
| Truth | Pre-generate the printed code and immutable local expected-label record before capture. Keep the physical fixture log separate from policy inputs. This supports label-read truth only, not maintenance-completion truth. |
| Network | A disconnected capture can be demonstrated, but it is not an evaluative variable unless a remote-quality baseline and outage timing are included. Do not claim an offline systems contribution from local-only capture. |
| Timing | Sequential RGB/NoIR is valid only for static target/covers. No fusion, moving-label, or synchronized-pair conclusion is feasible without an external timing measurement. |
| Cost | USB meters may not resolve fast switching transients. Report measured episode energy and latency; do not infer energy from capture count. Manual review must have a fixed local procedure and charged time. |
| Scope | A finite 2x2 low-light/cover pilot, held-out cover placement/lamp/session, and block bootstrap over sessions is feasible. It cannot support a claim about all factories, labels, covers, cameras, repair tasks, or weak networks. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Adaptive camera parameters can be selected per unlabeled scene/model under capture-latency constraints. | [KILL] | Baek et al., Lens, arXiv:2503.02170v3, 2026-05-19, https://arxiv.org/html/2503.02170v3 | Abstract; Sec. 3.1, lines 125-137; Sec. 3.2, lines 138-143; Sec. 5 | ImageNet-style task and parameter options, not maintenance labels; direct action-family collision. |
| Budgeted visual evidence acquisition already uses answer/abstain/acquire and requires post-acquisition calibration. | [KILL] | Xu et al., BCEA, arXiv:2606.16667v4, 2026-07-21, https://arxiv.org/html/2606.16667v4 | Sec. 3, lines 117-123; Secs. 4.2-4.4; Sec. 4.3, lines 153-160; Sec. 5, lines 194-243 | VLM claim verification, not edge code reading; kills the generic three-action/conformal method. |
| Active exposure control for visual fiducials under low/adversarial light and field conditions is established. | [KILL] | Ren et al., arXiv:2404.12055v1, 2024-04-18, https://arxiv.org/html/2404.12055v1 | Abstract; Sec. 3.1, lines 68-106; Sec. 4, lines 120-177; Sec. 5, lines 200-205 | Underwater localization and exposure control, not transparent cover or accept/review loss; kills exposure-control contribution. |
| Transparent-film optical processing has direct industrial QR/OCR evaluation. | [KILL] | Tang et al., CVPR 2024, pp. 24987-24996, https://openaccess.thecvf.com/content/CVPR2024/html/Tang_Learning_to_Remove_Wrinkled_Transparent_Film_with_Polarized_Prior_CVPR_2024_paper.html | Abstract; Secs. 3.1-3.5; Secs. 5.1-5.3, especially QR/OCR downstream evaluation | Four-angle polarization and reconstruction differ from Pi RGB/NoIR; kills film-removal/QR-readability novelty. |
| Active fault-diagnosis interventions and an information objective are established. | [KILL] | Han et al., arXiv:2509.18460v1, 2025-09-22, https://arxiv.org/html/2509.18460v1 | Abstract, lines 51-53; Sec. II-C, lines 102-106; Secs. IV-D and V, lines 189-216 | Robot perception and simulation; kills general causal-diagnosis language. |
| Passive cover/photometric monitoring declares a limited operating envelope and shows camera-disjoint threshold failure. | [KILL] | Ma et al., arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/html/2607.14760v1 | Sec. III/V; Supplementary V, lines 411-419; Supplementary XII, lines 511-516 | Camera tamper monitoring, not a local second-capture action; blocks passive health/transfer claims. |
| A broad synthetic-versus-physical robustness conclusion is unavailable from a small fixture. | [K] | Agnihotri et al., arXiv:2505.04835v1, 2025-05-07, https://arxiv.org/html/2505.04835v1 | Sec. 4.2, lines 106-115 | Reports strong aggregate but weak corruption-specific correlations; supports a finite audit only. |
| IR-on or another fixed optical recapture changes held-out maintenance-record action loss beyond fixed two-shot. | [C] | Proposed local experiment | No primary source inspected establishes this exact endpoint | Requires preregistration and repeated held-out sessions. |
| Clean-low-light and transparent-cover cells are distinguishable from the permitted pre-action observations. | [GAP] | Proposed local experiment | Not established before the physical pilot | A paired-world overlap is a valid negative result. |

## Queries and failed searches

Queries run or checked on 2026-09-03:

- `transparent cover glare low light image recapture quality assessment OCR 2025`
- `active illumination counterfactual fault diagnosis robot perception intervention information 2025`
- `adaptive camera sensor exposure modality selection edge capture cost 2024 2025`
- `printed fiducial marker adaptive exposure low light field 2024`
- `budgeted visual evidence acquisition answer abstain acquire intervention 2026`
- `industrial transparent film QR OCR primary paper 2024`

No inspected primary paper jointly uses the exact RGB/NoIR Pi fixture, maintenance-record action loss, transparent-cover versus low-light cells, independent work-order label, and matched joules. This is a retrieval gap, not novelty evidence. The audit found no valid basis to turn a printed label into proof of actual maintenance completion. A complete field workflow, local expected-label semantics, manual-review procedure, IR safety specification and power instrumentation remain unresolved.

## Decision

**PIVOT.** Kill the positive thesis claim that an offline maintenance-photo accept/recapture/review policy is a new edge method. Retain only a preregistered, finite empirical endpoint: on the named purchased fixture, does one *predeclared* second optical observation change the action-risk frontier beyond fixed two-shot, scalar quality and always-review controls? Report rank preservation, fixed-policy dominance, or two-world non-identifiability as the preferred honest outcomes. Do not call that endpoint causal diagnosis, camera health, transparent-film OCR, offline systems research, or proof of maintenance completion.

PIVOT
