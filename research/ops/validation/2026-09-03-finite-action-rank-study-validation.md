# Validation Audit: 2026-09-03 finite physical/digital action-rank study

## Decision investigated

Audit whether the finite action-rank study proposed in the latest physical-transfer protocol and the PRF-TR candidate row can be a valid undergraduate FYP contribution. The proposed setting is a local edge node that chooses retain, reacquire, or unknown for a printed, non-personal inspection indicator. Digital corruptions are compared with physically induced conditions using an exact predeclared payload, independently assigned physical cells, matched latency/energy accounting, and held-out cells.

This audit also separates a scientific question from a deployment gate. A gate that says “the Pi pipeline passes these checks” is assessed as an engineering artifact unless it yields a falsifiable technical result beyond the acceptance criteria.

Files read on 2026-09-03: AGENTS.md; research/active/README.md; research/active/00-project-charter.md; research/active/01-candidate-register.md; research/active/09-physical-transfer-pilot-protocol.md; research/active/11-cross-device-action-rank-pilot.md; research/active/12-pilot-execution-gates.md; research/ops/divergence/2026-09-03-contact-evidence-and-intermittency-divergence.md; and the latest PRF-TR entries in the candidate register and decision log.

## Claim under test

The strongest defensible claim is not “digital robustness tests are invalid” and not “the Pi has a reliable deployment certificate.” It is:

> For a named printed-code task, a frozen action set, a declared RGB/NoIR camera pair, and a finite matrix of lamp/material/fault cells, digital corruption rankings may or may not preserve the physical risk-cost ranking of retain, reacquire, and unknown.

The study can be a contribution only as a bounded, reproducible empirical evaluation of that claim. A new decoder, a new quality score, a new modality selector, a Pi implementation, or a pass/fail release checklist is not sufficient.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Adaptive camera control, adaptive exposure, and budgeted acquire/abstain actions are already explicit in Lens, AdaptiveAE, BCEA, and resource-aware active sensor acquisition. Synthetic-versus-real robustness comparison is already a named benchmark question in Agnihotri et al. | No inspected source has the exact purchased Pi RGB/NoIR pair, exact printed payload, the same physical cells, or the same joule-aware three-action endpoint. This is a finite apparatus/endpoint distinction, not component novelty. | High collision for any method claim; medium for the bounded evaluation endpoint. |
| Exact-claim collision | Retain / reacquire / unknown is a special case of answer/acquire/abstain. A fixed two-shot action is a standard conservative confirmation policy. Digital-to-physical ranking comparison is already the core question of synthetic-corruption proxy studies and wireless/emulation validation studies. | A thesis could still report a preregistered finite phenomenon: a rank inversion or rank preservation that survives held-out physical cells, remounts, and matched costs, and that is not removed by fixed two-shot or scalar quality controls. | Medium-high collision; the exact phenomenon remains [GAP]. |
| Boundary / identifiability | A post-capture brightness/blur/mask can share a decoder score with physically different states; an image-only policy cannot infer omitted physical causes. Equal nominal light or a shared camera score is not an independent truth channel. Repeated frames from one fixture do not create independent physical units. | Exact payload truth, preassigned cell labels, randomised sessions, logged exposure/WB/timing, and physically held-out cells make the finite endpoint measurable. They do not identify a general camera-family transfer rule or a causal fault label. | High for the boundary; no empirical effect yet. |

## Formalization and assumption audit

Let c denote a physical cell/session, x the complete captured episode, y(x) the exact predeclared payload, a an allowed action, and o(x,a) the observed result of that action. Let q(x,a) be the independently checked endpoint: 1 only when the decoded payload equals the predeclared payload, and 0 otherwise. The policy may output retain, reacquire, or unknown; the policy must not use q as a feature before deciding.

For a declared cost model, define

    L_c(a) = lambda_FR * FR_c(a) + lambda_U * U_c(a) + lambda_T * T_c(a) + lambda_J * J_c(a).

FR is a wrong retained payload, U is an unknown outcome, T is decision-to-completion latency, and J is measured episode energy. The current protocol fixes 10*FR + 1*U + 0.1*J; this is acceptable as a preregistered operating point only if the story can justify why false retention is ten times worse than unknown and why the joule normalisation is meaningful. A sensitivity sweep over plausible weights is mandatory. A rank inversion that exists only for one arbitrary weight vector is weak evidence.

The oracle action is a*_c = argmin_a L_c(a) after observing the independently assigned cell. The deployable policy is pi(z), where z is the pre-action prefix. The study can estimate the finite risk table, but it cannot claim that pi identifies a hidden physical cause. If two cells have overlapping z distributions but different a*_c, the correct result is non-identifiability and unknown, not a more complex selector.

Required assumptions:

1. The payload is generated and stored before any scored capture. A phone, flatbed, or second fixed read may verify the physical print, but the candidate decoder cannot generate its own labels.
2. Cell labels such as clean, low-light, transparent-cover, saturation, or interruption are assigned by a fixture log before capture. They are not inferred from image quality or decoder confidence.
3. Physical and digital comparisons use the same semantic endpoint. Applying a digital corruption after capture is free in wall time and energy unless its compute/storage cost is explicitly charged; therefore a digital rank is not automatically a cost-matched action rank.
4. Reacquisition must include the real second capture, decode, and decision delay. Otherwise the fixed two-shot baseline is either unfairly penalised or the proposed policy receives free information.
5. A frame is not an independent sample merely because it has a new timestamp. The primary unit should be a randomised session-by-cell or remount-by-cell; bootstrap over sessions/cells, not thousands of repeated frames from one static setup.
6. Sequential RGB/NoIR captures are not synchronized multispectral observations. Static targets are valid for the minimum study; moving-target or registration claims require an external timing witness.
7. “Held-out cells” must mean held-out physical conditions or material lots that were blocked before threshold fitting. Repeating the same printed sheet under the same lamp is a repetition, not a new device-family sample.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Xu et al., Look Again Before You Abstain: Budgeted Conformal Evidence Acquisition for Reliable Vision-Language Models, arXiv v4, 2026-07-21, https://arxiv.org/abs/2606.16667 | Calibrated score; answer, abstain, or acquire more evidence by zoom/crop/intervention under a budget. | Claim-level hallucination risk, coverage, AUROC, and finite-sample validity; Secs. 1, 4.1-4.4, 5, App. B. | Same three-way acquire/abstain action pattern and budgeted evidence acquisition. | Kills a new generic triage wrapper. It leaves only a different physical endpoint and a finite measurement study. The paper also shows that calibration must include the complete acquisition pipeline. |
| Baek et al., Lens: Adaptive Camera Sensor for Vision Models, ICLR 2025, arXiv v3, 2026-05-19, https://arxiv.org/abs/2503.02170 | Unlabelled image/model state selects camera parameters using a model-specific quality indicator and capture-time budget. | Image accuracy and latency on ImageNet-ES datasets; abstract and Secs. 3-5. | Preview-to-camera-action routing under cost. | Kills a new quality-to-RGB/NoIR selector or model-confidence gate. It does not establish the exact physical marker endpoint. |
| Xu et al., AdaptiveAE: An Adaptive Exposure Strategy for HDR Capturing in Dynamic Scenes, ICCV 2025, official paper https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Previous LDR frames and scene/illumination features select ISO, shutter, and frame count. | HDR quality, motion blur/noise, and exposure budget; paper pp. 25176-25185, Secs. 3.3-3.4. | Sequential extra capture under a fixed budget. | Kills adaptive exposure/burst as the research mechanism. The printed-code exactness endpoint remains only a bounded evaluation difference. |
| Bian et al., Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning, Sensors 26(16):5065, published 2026-08-10, https://www.mdpi.com/1424-8220/26/16/5065 | Low-cost screening, high-information confirmation, uncertainty/OOD escalation, watchdog, and device/condition shift under resource cost. | Fault-warning performance, resource use, and held-out device/condition evaluation; Secs. 1, 3.1, 5.1, 6, 8. | Screen/confirm/escalate action family on edge hardware. | Kills generic “use a cheap preview to decide whether to reacquire” claims. A finite physical-vs-digital rank table remains narrower, but is not a method by itself. |
| Agnihotri et al., Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?, arXiv v1, 2025-05-07, https://arxiv.org/abs/2505.04835 | Synthetic common corruptions and real ACDC conditions evaluated on the same pretrained segmentation models. | Mean and corruption-specific performance correlations; Secs. 3, 4.1-4.2, 5. The paper reports aggregate Pearson 0.759, but brightness/night 0.270 and fog/fog 0.349. | Directly studies whether synthetic conditions preserve real-world robustness rankings. | Kills the broad digital corruption is invalid or digital corruption is reliable thesis. Leaves a device-specific marker/action audit as a bounded replication or extension. |
| Beuran, Nguyen & Shinoda, QOMB Wireless Network Emulation Testbed: Evaluation and Case Study, WiNTECH 2010, https://www.jaist.ac.jp/~razvan/publications/qomb_evaluation_case_study.pdf | Emulated wireless conditions are compared with simulations and real WLAN trials using repeated traffic experiments. | Throughput, congestion, and multi-hop behavior; pp. 1-4 and Sec. 3. The paper repeats each condition three times and reports differences/variability from real trials. | Methodology of freezing a model, testing it against a physical realization, and reporting transfer error. | Kills emulator-versus-physical comparison as a method in itself. It leaves a different application endpoint, but not a general physical-fidelity theorem. |
| NIST, Conformance Testing 101, updated 2022, https://www.nist.gov/itl/voting/conformance-testing-101 | A prescribed test suite checks implementation behavior against a written specification. | Pass/fail conformance, objective and reproducible test outcomes; paragraphs 1-5. | Deployment/acceptance gate framing. | Shows that a pass/fail gate is bounded by its specification and gives confidence, not proof over untested conditions. It supports an engineering gate, not an innovation claim. |
| NASA, Technology Readiness Levels, updated 2026-06-25, https://www.nasa.gov/directorates/armd/technology-readiness-levels/ | Readiness levels classify maturity from initial principles through prototype and operational proof. | TRL 3-6 cover analytical/laboratory proof, component testing, realistic simulation, and a functional prototype; article lines 254-266. | Prototype/deployment-readiness language. | Kills the idea that reaching a runnable Pi demo is research novelty. It leaves the demo as feasibility evidence. |

## Strongest simple baseline

The decisive baseline is a non-learned fixed policy:

1. Capture RGB with fixed exposure/white balance.
2. Capture NoIR with fixed IR.
3. Run the same decoder and retain only an exact payload match; otherwise return unknown or request review.

This baseline must be compared with always-RGB, always-NoIR+IR, fixed two-shot, scalar brightness/blur/decoder-confidence, random action, and an oracle that knows the preassigned cell. The fixed two-shot policy is especially strong because it obtains the extra physical observation without asking a preview to predict its value. All actions must pay their actual capture, decode, latency, and energy costs.

For the digital/physical part, use a frozen decoder and two separate analyses:

- endpoint agreement: whether digital transformations preserve the ordering of exact-code error rates;
- decision-cost agreement: whether the same action remains optimal after real capture costs are included.

Do not merge these into one correlation number. A digital transformation can preserve the image error pattern while being free to apply, so it can rank actions differently from a physical reacquisition even when the visual endpoint agrees.

## Contrarian result

The most likely result is not a useful adaptive policy. On a static printed marker, fixed two-shot or always-reacquire may be Pareto-optimal once false retention is heavily penalised. If so, the action-rank study still gives a finite null, but it does not justify a new selector.

A second likely result is rank preservation for obvious conditions such as blur, brightness, and noise, with inversion only for one narrow physical condition. That would be an observation about the purchased camera/fixture pair, not evidence that synthetic testing is generally wrong. A third likely result is that the two worlds remain observationally overlapping; then the honest contribution is a non-identifiability boundary and the policy should abstain.

The proposed printed target also weakens the story if no real maintainer, release decision, or repeat-visit cost exists. A constructed “curator releases a Pi pipeline” is an evaluation narrative, not a confirmed workflow. The study should therefore describe itself as a benchmark/protocol unless a real repeated actor decision is documented.

## Deployment-gate audit

The following are engineering gates:

- both camera paths capture a frame;
- the decoder returns the predeclared payload;
- exposure, white balance, timing, and power logs are present;
- the fixture can reproduce its labelled cells;
- the demo meets a fixed latency or storage limit.

These gates are necessary and useful. They establish that the apparatus is runnable and that the measured result is interpretable. NIST defines conformance testing as checking implementation behavior against a specification, bounded by that specification; passing the suite does not guarantee behavior in untested areas. NASA’s TRL description similarly treats prototype demonstration as maturity evidence. Neither makes the gate a CS contribution.

To become research, the gate must be subordinate to a question such as: “Under which physical cells does a frozen digital test ranking fail to predict the action-risk ranking, and can that failure be detected by a specified independent observation at equal cost?” The result must be falsifiable before the run and useful whether the answer is inversion, preservation, or non-identifiability. “Pipeline passes” or “pipeline fails” alone is engineering-only.

## Feasibility audit

| Requirement | Finding | Consequence |
| --- | --- | --- |
| Hardware | Pi 5B, RGB, NoIR, and IR illuminator support static sequential captures. Rigid mounting and a power instrument remain needed if energy is a primary endpoint. | Feasible for a bench study; no extra camera or larger model is justified. |
| Independent truth | A predeclared printed payload supplies exact semantic truth. A separate reference read can verify the print. Decoder confidence and a panel are not truth. | Feasible if the payload registry is created before scoring. |
| Physical labels | Covers, lamps, masks, and interruptions can be assigned by fixture logs. They do not represent a field distribution automatically. | Held-out material/lamp/remount cells are mandatory; no population claim. |
| Matched cost | Sequential NoIR capture, IR power, decode time, storage, and reacquisition delay must be measured per action. Digital transformations are otherwise artificially cheap. | The current protocol needs a cost ledger before a rank claim is interpretable. |
| Sample units | Twenty frames per session are useful for estimating a cell rate, but they are not twenty independent devices or environments. | Report session/cell uncertainty and avoid frame-level significance. |
| Timeline | A static pilot and deterministic baselines are feasible within the stated FYP window. A broad camera-family or field-transfer claim is not. | Suitable as a bounded FYP evaluation or negative result, not as a general deployment certificate. |
| Real workflow | No authorised repeated maintainer/release workflow or field outcome record is currently documented in the charter. | Blocks PROMOTE under the project quality bar until either the workflow is supplied or the thesis is explicitly evaluation/protocol research. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Three-way evidence acquisition under a budget is an existing research endpoint, and calibration must include post-acquisition scores. | [KILL] | Xu et al., BCEA, arXiv v4, 2026-07-21, https://arxiv.org/abs/2606.16667 | HTML Secs. 1, 4.1-4.4; App. B, especially lines 129-160 and 339-343 | LVLM claim-level setting; it kills a generic acquire/abstain wrapper, not the exact optical apparatus. |
| Adaptive camera control from an unlabeled quality signal is established. | [KILL] | Baek et al., Lens, arXiv v3, 2026-05-19, https://arxiv.org/abs/2503.02170 | Abstract; Secs. 3-5 in the ICLR paper | Different endpoint, same preview-to-action mechanism. |
| Adaptive exposure/frame-count selection under capture cost is established. | [KILL] | Xu et al., AdaptiveAE, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | ICCV paper pp. 25176-25185; Secs. 3.3-3.4 | HDR target; not a printed marker, but direct mechanism collision. |
| Resource-aware screen/confirm/escalate acquisition is established. | [KILL] | Bian et al., Sensors 26(16):5065, 2026-08-10, https://www.mdpi.com/1424-8220/26/16/5065 | Secs. 1, 3.1, 5.1, 6, 8 | Official page was rate-limited during this pass; bibliographic record and section map were already present in the local audit. |
| Synthetic/physical robustness rankings can agree in aggregate and diverge by corruption. | [K] | Agnihotri et al., arXiv:2505.04835v1, 2025-05-07, https://arxiv.org/abs/2505.04835 | HTML Secs. 3, 4.1, 4.2, 5; lines 97-116 | Semantic segmentation/weather; not evidence for a Pi result. |
| Physical-versus-emulated comparison is an established evaluation methodology with repeatability limits. | [KILL] | Beuran et al., QOMB, WiNTECH 2010, https://www.jaist.ac.jp/~razvan/publications/qomb_evaluation_case_study.pdf | pp. 1-4, Sec. 3; repeated trials and real/emulated variability | Wireless throughput/MANET endpoint; not the exact marker task. |
| tc netem offers parameterised packet impairment and documents timing/slot limitations. | [K] | Linux tc-netem(8) manual, upstream snapshot 2026-05-24, https://man7.org/linux/man-pages/man8/tc-netem.8.html | Options and Limitations sections | Tool documentation; not a physical Wi-Fi fidelity guarantee. |
| A conformance/acceptance gate is bounded by its written specification and passing tests do not cover untested behavior. | [K] | NIST, Conformance Testing 101, updated 2022, https://www.nist.gov/itl/voting/conformance-testing-101 | Paragraphs 1-5 | Official guidance; supports engineering-only classification of a pass/fail gate. |
| Prototype demonstration is a technology-maturity level, not by itself a research result. | [K] | NASA, Technology Readiness Levels, updated 2026-06-25, https://www.nasa.gov/directorates/armd/technology-readiness-levels/ | TRL descriptions, lines 254-266 | Space-technology context; used only for the distinction between maturity and novelty. |
| A repeatable held-out rank inversion exists for the purchased RGB/NoIR setup. | [C]/[GAP] | PRF-TR / XFER-ACT hypothesis | No scored pilot data exists in the workspace as of 2026-09-03 | Must remain unclaimed until physical data are collected. |
| Fixed two-shot is Pareto-optimal. | [C]/[GAP] | Proposed control hypothesis | No scored pilot data exists | It is the principal kill test, not an assumed fact. |
| The printed-marker workflow is a real repeated deployment decision. | [GAP] | Current charter and protocols | No authorised actor, field log, or repeat-visit record is documented | Without this, use evaluation/protocol language. |

## Queries and failed searches

Queries run or rechecked on 2026-09-03:

- budgeted evidence acquisition answer abstain acquire physical sensing edge 2025 2026
- adaptive camera sensor control capture budget Lens ICLR 2025
- adaptive exposure frame count budget ICCV 2025 AdaptiveAE
- resource-aware active sensor acquisition edge few-shot commissioning 2026
- synthetic corruptions real-world corruption ranking correlation benchmark 2025
- wireless network emulation validation physical trials repeatability QOMB
- deployment gate acceptance testing research contribution conformance specification
- technology readiness prototype demonstration research novelty gate

Failed to establish:

- an exact primary paper using this purchased Pi RGB/NoIR pair, exact printed payload, these physical cells, and matched joule-aware action ranking;
- a field distribution or authorised maintainer log for the proposed printed-indicator story;
- a non-arbitrary loss weight vector grounded in an actual operator’s false-retain versus reacquisition costs;
- a general theorem that a finite action ranking transfers to unseen cameras or physical conditions.

These are gaps, not evidence of novelty.

## Decision

PRF-TR / finite action-rank study: **PIVOT** to a bounded physical-versus-digital evaluation protocol. It is feasible as an undergraduate FYP if the thesis openly claims a finite empirical boundary or a useful null, freezes the exact payload and action semantics, uses independent session/cell units, charges real capture costs, and treats fixed two-shot and scalar-quality rules as adversarial baselines. It is not currently a promoted method contribution.

Deployment-gate framing: **KILL as a research contribution; retain as engineering infrastructure.** A pass/fail bring-up or release checklist can support the experiment and demo, but cannot occupy the innovation claim.

Overall status: **PIVOT**

PIVOT
