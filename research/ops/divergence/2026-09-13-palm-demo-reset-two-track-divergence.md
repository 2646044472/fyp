Decision investigated

# Divergence Packet: 2026-09-13 — palm-demo reset and two-track options

## Decision investigated

Given the authoritative 2026-09-04 Bob Zhang supervisor record, what should the group do **now** to deliver a portable palm-payment-like demonstration by December while keeping a defensible, falsifiable FYP contribution possible?

The supervisor constraint overrides the earlier practical direction but not the earlier negative evidence. Palm is now the mandatory application and demo substrate; it does not become novel merely because it is mandatory. All cross-device directions and end-to-end/physical-print attacks remain ruled out. The immediate deliverable is a local palm verifier whose acquisition and failure behavior can be inspected. The thesis contribution must be separately earned through a held-out experiment about open-environment recognition, multimodal observation, reacquisition, or a bounded negative result.

**Current recommendation:** build one modular VIS-first demo spine immediately; prepare IR as a logged second observation path rather than claiming palm-vein capability; promote `O1 RING-CELL` as the first research gate and keep `O2 IR-INCREMENT` as the supervisor-aligned second gate. Do not lead with learned fusion, a new ROI network, finger-ratio fusion, dorsal fusion, “edge deployment,” or a small-pilot accuracy number.

## Search boundary

- Workspace inspected on 2026-09-13: `research/active/README.md`, `00-project-charter.md`, `01-candidate-register.md`; the newest VIS/ROI divergence and validation packets; `code/palm_demo/README.md`, `BASELINES.md`, `data/SOURCE_MANIFEST.md`, `palm_demo.py`; relevant 08-17 and 09-04 minutes; and archived palm/Pi, payment, ROI, embedded-system and Palm-ID logs.
- User-supplied supervisor record is treated as authoritative for practical scope: Palm Recognition group; no cross-device thesis; no end-to-end or physical-print attack thesis; portable payment-like demo; accuracy and open-environment robustness including rings; early palmprint+palm-vein IR multimodality; possible same-feed finger ratios/dorsal features; immediate IR illumination and comprehensive review.
- Literature scope: contactless palmprint systems, open-environment ROI, image quality, palmprint/palm-vein fusion, missing modalities, hand geometry/dorsal hand features, and biometric evaluation standards. Primary papers and official standard records carry central claims. Reviews only establish collision breadth.
- Search date is 2026-09-13. No global novelty statement is made. `[GAP]` means unresolved within the sources, queries, and date below.
- Privacy/security boundary: local, consented verification prototype only. No payment processing, financial authorization, PAD/liveness, template-protection, demographic fairness, production FAR, or access-control security claim.

## Mandatory demo architecture versus optional thesis contribution

### Mandatory demo architecture — complete regardless of thesis option

1. **Capture and interaction:** portable hood/fixture; hand guide; RGB/VIS first; camera, illumination, exposure/gain, distance/pose prompt, frame/session/attempt ID and retry reason logged. Add independently switchable IR illumination only after wavelength, irradiance/eye-safety evidence and actual sensor response are recorded.
2. **ROI and quality:** keep a fixed/manual or simple landmark ROI as the diagnostic baseline. Log ROI success, coverage, rotation, scale, blur, brightness/saturation, hand segmentation/landmark confidence, rings/accessories and physical condition assigned by the protocol. Do not call these quality values independent biometric truth.
3. **Recognition:** keep pinned Fast-CC as the always-runnable baseline; enroll and perform local `1:1` verify; separate enrollment, development-threshold and held-out session data. Add a stronger matcher later only beside Fast-CC and only with lawful weights/data and a frozen artifact.
4. **Decision/UI:** show `accept / one guided recapture / unable-to-decide` for the demo. This is conservative demo behavior, not a new policy or certified security property. Show stage timing and reason codes; never display “palm vein verified” unless the hardware and a separate vein pipeline establish that modality.
5. **Data and evaluation:** machine-readable manifest for participant/hand/session/attempt/camera/illumination/condition/ROI/action/hash; consent and deletion path; mated/non-mated trial construction; threshold frozen on development sessions; report FMR/FNMR, failure-to-acquire, retries and p50/p95 transaction time with identity/session as the independence unit.
6. **Portability:** offline startup, repeatable install bundle, fixed power supply, mount geometry, health check, deterministic replay image and a five-minute demo script. Payment-like means interaction form only; it does not include accounts, settlement, authorization, PAD or commercial security.

### Optional thesis contribution — choose only after gates

The contribution is one of the bounded claims below, not the architecture above. A positive result must beat transparent fixed controls on held-out identities and sessions. A null must close the claim rather than trigger an unregistered model search.

## Recent-paper limitation map

| Primary work | Version/sections inspected | What it occupies | Residual relevant to this reset |
| --- | --- | --- | --- |
| Grosz, Godbole & Jain, *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv:2401.08111, v1 2024-01-16; IEEE TIFS 2024, DOI `10.1109/TIFS.2024.3413631` | Open HTML Secs. II-A--II-G, III-C--III-E, IV-A--IV-B | End-to-end mobile capture, ROI, enhancement, complementary embeddings, compact templates, quality rejection, authentication/search and cross-database/time-separated evaluation. | A Pi implementation, local quality gate, compact template, or mobile-like UI is a baseline. It does not report this Pi's capture-to-decision/energy or rings as a controlled held-out factor. |
| Chai et al., *Joint Finger Valley Points-Free ROI Detection and Recurrent Layer Aggregation for Palmprint Recognition in Open Environment*, IEEE TIFS 20 (2025), 421--435, DOI `10.1109/TIFS.2024.3516539` | Secs. I--II, III-B pp. 426--427, IV pp. 429--433, V p. 433 | FVP-free adaptive ROI, complex backgrounds, illumination and free-pose recognition; open-/closed-set and cross-dataset testing. | “Robust/open-environment ROI” and a new ROI net are occupied. A finite accessory-by-environment failure/action study with fixed baselines remains an evaluation question, not a method claim. |
| Zhang et al., *HGAIQA*, IEEE TIM 73 (2024), 1--13, DOI `10.1109/TIM.2024.3485454` | Official abstract and publication metadata; full sections unavailable in this pass | Bob Zhang-aligned quality assessment using hand geometry, flatness, brightness and sharpness, evaluated through quality removal/EER. | Same-feed geometry/quality is advisor-aligned but not an empty method space. It can be a preregistered witness/control for recapture, not automatically a thesis contribution. |
| Jin et al., *Unified Adversarial Augmentation for Improving Palmprint Recognition*, ICCV 2025 | Official CVF PDF, Secs. 1, 3, 4.1--4.3 and evaluation tables | Robust palmprint recognition through unified adversarial augmentation and identity-disjoint/open-set protocols under variations. | “Augmentation improves robustness” has high collision risk. A factor-held-out physical ring/environment result must compare against ordinary augmentation, not rename it. |
| Fan et al., *A Novel Hybrid Fusion Combining Palmprint and Palm Vein for Large-Scale Palm-Based Recognition*, IEEE TSMC 54(7), 2024, 4471--4484, DOI `10.1109/TSMC.2023.3346961` | Abstract, method description and experiment/result sections as recorded in the validation packet | Palmprint+palm-vein coarse certainty/uncertainty decisions and adaptive weighted fusion for accuracy and efficiency. | Generic palmprint-vein fusion and confidence weighting are occupied. The residual is whether a **verified low-cost IR observation** adds held-out value at matched capture cost. |
| Pan et al., *SSFD-Net*, Digital Signal Processing 159 (2025) 105003, DOI `10.1016/j.dsp.2024.105003` | Abstract, proposed method, experiments/missing-rate ablations and conclusion | Shared/specific feature disentanglement and cross-modal transformation for palmprint+palm-vein recognition with a missing modality. | Missing-modality recovery/fusion is occupied. A simple IR-off/on physical incremental-information audit may still return a useful null. |
| Fei et al., *Learning Frequency-Aware Common Feature for VIS-NIR Heterogeneous Palmprint Recognition*, IEEE TIFS 2024, DOI `10.1109/TIFS.2024.3441945` | Official metadata/abstract and archived boundary notes | VIS-NIR cross-spectral palmprint matching and common-representation learning. | Cross-spectral matching is not the contribution. The local question must concern same-transaction observation value or a bounded failure boundary. |
| Shen et al., *Embedded Palmprint Recognition System Using OMAP 3530*, Sensors 12(2), 2012, 1482--1498, DOI `10.3390/s120201482` | Full text Secs. 2--5, especially apparatus and timing/results | A real embedded camera/illumination/UI/local-matching appliance with constrained hand positioning. | A box, LEDs and local matcher are demonstrably engineering. Modern portability does not supply novelty; free-hand failure and honest transaction/resource accounting remain local measurements. |
| Lee et al., *Hand Biometric Recognition Based on Fused Hand Geometry and Vascular Patterns*, Sensors 13(3), 2013, 2895--2910, DOI `10.3390/s130302895` | Full text Secs. 2--4 and literature table | Low-cost one-image hand geometry plus vascular-pattern score fusion; hand/palm/finger geometry and vascular combinations predate this FYP. | Finger ratios/geometry cannot be sold as a new extra biometric. They may serve as pose/scale/ROI witnesses if tested against an equally informed scalar baseline. |
| ISO/IEC 19795-1:2021; ISO/IEC 19795-10:2024 | Official scope plus 19795-1 Secs. 6.4--6.5, 7--8 and 19795-10 factor/uncertainty scope | Mated/non-mated testing, thresholding, error reporting, factor controls, uncertainty, failure-to-acquire and operational variation. | The 3--5-person bring-up cannot support deployment/population claims. These standards define evaluation hygiene, not novelty. |
| ISO/IEC 21472:2021 | Official preview Introduction, Secs. 1 and 3 | Reference/target evaluation conditions and user-interaction influence for biometric capture. | A guided retry study must freeze prompts, attempts and transaction timing. Generic “better UX” is not a contribution. |

## Two-track option matrix

| ID | Mandatory demo deliverable | Optional exact research claim | Natural baselines and smallest kill test | Feasibility / burden |
| --- | --- | --- | --- | --- |
| **O1 `RING-CELL` — accessory/environment blocked robustness** | VIS verifier with explicit ring/accessory field, fixed guide, condition logging, ROI overlay, reason-coded recapture and held-out session replay. IR later becomes another recorded condition, not required for Gate 1. | `[C]` For this named camera/fixture and permitted accessory set, training or calibration that explicitly includes accessory-by-environment cells reduces held-out FNMR/failure-to-acquire at a frozen FMR and retry budget compared with clean-only training, standard geometric/photometric augmentation, score-only gating and fixed recapture. The scientifically safer identity is a **factor-interaction map** showing when ring effects are explained by landmark/ROI failure and when they are not. | Kill if the ring has no repeatable effect; if ordinary augmentation/fixed crop/score-only gate matches; if ring type co-varies with identity/session; or if only frame-level significance appears. Pilot: same people, with/without 2--3 inert ring types, crossed with two lighting/background cells, new session, frozen matcher. | Strong advisor alignment and excellent December compatibility. Moderate ethics; low new hardware; medium collision risk because robustness/augmentation/ROI are crowded. Strong negative-result value. |
| **O2 `IR-INCREMENT` — palmprint/IR incremental-information gate** | Add controlled IR-on capture as a separate logged path; display VIS and IR observations separately; keep single-modality decisions visible; collect matched attempts. Do not label the NoIR feed “palm vein” until vein contrast and repeatability are demonstrated. | `[C]` After VIS ambiguity, one controlled IR observation changes the held-out `(FMR, FNMR, retry, latency, joules)` frontier beyond VIS recapture, always-two-shot, VIS-only, IR-only and fixed equal-score fusion for named low-light/skin-surface/accessory cells. A null establishes that the purchased low-cost path does not provide decision-relevant independent information. | Gate 0: vessel/texture repeatability and sensor/illumination manifest. Kill if IR is merely another exposure/camera response; if no independently repeatable vascular signal exists; if fixed VIS recapture dominates; if equal fusion matches; or if gains vanish under identity/session holdout. | Highest supervisor alignment, but medium December risk until hardware is characterized; moderate ethics; high collision risk for fusion methods; **very high negative-result value** because it prevents a false palm-vein claim. |
| **O3 `GUIDED-RETRY` — interaction policy under weak cooperation** | Portable prompt/guide with live hand-placement feedback, one-recapture budget, timeout and explicit `unable-to-decide`; logs attempts and total transaction time. Works before IR. | `[C]` A fixed, interpretable pre-capture guide based on hand landmarks/coverage lowers failure-to-acquire and p95 transaction time at unchanged held-out FMR versus no guide, static outline, score-triggered recapture and unconditional two-shot capture under named pose/distance/environment cells. This is HCI/edge action research, not a new recognizer. | Kill if a static outline or fixed second capture is non-dominated; if guidance adds delay; if the same image both defines the factor and evaluates success; or if 3--5 users are generalized to a population. Pilot: randomized within-subject prompt order across sessions. | Very high demo value and December feasibility; low hardware burden; highest human-subject/protocol burden; medium-high collision with mobile palm guidance and ISO interaction methodology. Useful null. |
| **O4 `AUX-WITNESS` — same-feed geometry/dorsal auxiliary evidence** | Extract finger lengths/ratios, hand silhouette/flatness and optional dorsal capture as visible diagnostics; use them first for pose/handedness/ROI checks. The core verifier remains palmprint. | `[C]` A same-feed auxiliary feature is useful only if it predicts held-out acquisition/match failure or improves the error/retry frontier beyond palm score, landmark confidence, scale-normalized geometry and fixed recapture at negligible added latency. The preferred endpoint is **witness value**, not identity-feature fusion. | Kill as thesis if concatenating/weighting identity features is the only result; if hand ratios encode scale/pose rather than stable identity; if rings corrupt both witness and ROI; if a landmark-confidence scalar matches; or if dorsal capture is not the same transaction/path. | Easy before IR for geometry; dorsal may require a second gesture and hurts payment-like UX. Highest collision risk due to old palmprint/geometry/vascular/dorsal fusion literature. Retain as control unless unexpectedly decisive. |

## Ranking without a misleading aggregate score

Ordinal scale: 1 is most favorable; burden/risk columns use 1 = lowest.

| Rank / option | Advisor alignment | December-demo feasibility | Evidence / ethics burden | Collision risk | Negative-result value | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| **1. O1 RING-CELL** | 1 | 1 | 2 | 3 | 2 | Best immediate bridge from the professor's “rings/environment” request to a testable physical protocol. Promote the measurement gate, not an augmentation model. |
| **2. O2 IR-INCREMENT** | 1 | 3 | 3 | 4 | 1 | Most directly aligned with the requested multimodality. Hardware truth must precede fusion; a negative IR result is highly useful. |
| **3. O3 GUIDED-RETRY** | 2 | 1 | 4 | 3 | 2 | Best portable-demo improvement and clearest future HCI branch, but needs explicit interaction methodology and enough participants. |
| **4. O4 AUX-WITNESS** | 2 | 2 | 2 | 5 | 3 | Useful low-cost instrumentation/control. Do not reserve the thesis slot for generic hand-feature fusion. |

Pareto view: O1 and O2 are not substitutes. O1 is the first executable physical-factor gate; O2 is the first IR truth gate. O3 can be implemented as demo behavior without claiming research. O4 should be collected cheaply where possible but remains a control until it proves incremental action value.

## Top two formalizations

### O1 `RING-CELL`: accessory-by-environment factor interaction

- **[D] Decision:** after one VIS capture, local verifier chooses `verify now / one guided recapture / unable-to-decide`.
- **[A] Assumptions:** consented participants; non-shared inert rings; ring/no-ring and environment are protocol-assigned before capture; identity, hand, session and condition are logged; development and test sessions are separate; matcher and FMR threshold are frozen; no PAD/payment-security claim.
- **[T] Target:** at a fixed development threshold and one-recapture budget, compare clean-only, standard augmentation, accessory-aware calibration, score-only gate and fixed recapture on held-out accessory-by-light/background cells. Primary endpoint is FNMR plus failure-to-acquire at frozen FMR; secondary endpoints are attempts and p95 transaction time.
- **Observable outcome:** physical condition, ROI/landmark success, score, action, mated/non-mated truth, retry result and timing aggregated by identity/session.
- **Counterexample:** rings are outside the palm ROI and produce no effect; any observed degradation comes entirely from a landmark detector and disappears with a fixed guide; or standard augmentation has the same frontier. Then there is no new robustness mechanism.
- **Negative-result value:** defines whether “rings” are a real system factor in this apparatus, localizes the failure stage, and stops unjustified ring-specific model work. A stable null is useful demo guidance and a bounded report.

### O2 `IR-INCREMENT`: low-cost IR observation value

- **[D] Decision:** after an ambiguous VIS capture, choose `decide from VIS / acquire one IR observation / recapture VIS / unable-to-decide` under a fixed interaction and energy budget.
- **[A] Assumptions:** the same participant/hand/transaction is used; IR wavelength, current, geometry, exposure/gain and capture order are logged; repeated captures establish whether the IR signal is stable; gallery/probe modality rules are frozen; no claim that NoIR+IR equals palm vein before evidence.
- **[T] Target:** test whether IR acquisition gives incremental held-out decision value over an equally costly VIS recapture and always-two-shot policy. Primary endpoint is FNMR at frozen FMR and capture budget; latency/joules and failure-to-acquire are co-primary system costs.
- **Observable outcome:** paired VIS/IR frames and scores, vessel/texture repeatability measure fixed on development data, action, truth, retries, stage timing and measured input energy.
- **Counterexample:** IR enhancement is a monotone transform of VIS quality, equal-weight fusion reproduces all benefit, or apparent gains vanish when identity/session and capture order are blocked. Then adaptive multimodal fusion is unsupported.
- **Negative-result value:** an honest finding that the cheap NoIR/illumination path is not a usable palm-vein modality is more valuable than a confounded fusion gain. It protects the demo wording and redirects IR to illumination assistance or drops it entirely.

## What can be done before IR hardware

- Freeze the payment-like demo transaction, non-security wording, `1:1` claim semantics, one-recapture limit and failure UI.
- Reverify the actual camera(s), board, OS, capture stack and mount; the active state confirms Pi plus Camera NoIR v2, while earlier RGB/illuminator inventory is not reliable.
- Finish the Fast-CC smoke path on deterministic images and live VIS captures; record stage timing, RSS, temperature and capture failure rather than matcher time alone.
- Define the manifest/schema and consent/deletion procedure; resolve `PalmBigDataBase` and CASIA source terms before any publication/training use.
- Run a 3--5-person **protocol pilot only** across at least two sessions; use it to debug enrollment, non-mated pairing, threshold code, retry logic and data leakage. Do not estimate production FAR or population robustness.
- Create the O1 crossed condition sheet: no ring versus protocol-provided inert ring(s), controlled background/light, pose/distance bins, randomized order, and independent condition labels. Verify that accessories do not create safety/hygiene issues.
- Implement transparent controls: fixed crop/manual ROI, no quality gate, score-only gate, static outline, fixed second capture, simple blur/brightness/coverage gate and standard augmentation offline.
- Predefine the IR acceptance test: spectral path, wavelength/current, eye-safety documentation, irradiance or conservative electrical limit, vessel/texture repeatability, VIS-recapture comparator, capture order and energy measurement. This prevents buying hardware that cannot answer the claim.

## Concrete sequence

### Next 2 weeks — demo spine and preregistration-grade logging

1. **Days 1--2:** lock the demo boundary and create a one-page data/ethics checklist. Verify hardware inventory and dataset permissions. Decide whether the current sensor can supply a legitimate VIS control; NoIR under ordinary visible light must not silently be called RGB.
2. **Days 2--5:** make capture/enroll/verify/retry deterministic; add manifest fields and reason codes; validate offline restart and deletion. Keep Fast-CC as baseline.
3. **Days 4--7:** freeze fixed ROI and simple quality controls; build session-blocked pair generation and threshold-freeze script; add stage timing and resource logs.
4. **Week 2:** run a 3--5-person, two-session protocol pilot with controlled pose/light/background and ring/no-ring cells. Analyze failures by stage. This is a feasibility dataset, not the final thesis test.
5. **End-of-week-2 gate:** proceed only if enrollment/verification are repeatable, held-out session data exist, the threshold is not fitted on test, conditions are independently logged, and the portable five-minute transaction works. Otherwise fix the demo substrate; do not add a learned model.

### Next 6 weeks — IR truth gate plus one bounded robustness experiment

1. **Weeks 3--4:** acquire/assemble IR illumination and safe fixture; record wavelength/current/geometry and exposure; test whether the camera observes stable subcutaneous/vascular structure rather than merely brighter palm texture. Repeat across sessions and hands.
2. **Weeks 3--5 in parallel:** expand O1 with preregistered accessory-by-environment cells and held-out sessions/identities. Compare fixed controls before any accessory-specific training.
3. **Weeks 4--5:** add a second lawful matcher only if Fast-CC failure analysis shows the claim is matcher-sensitive and the artifact runs reproducibly. The comparison asks whether the factor conclusion transfers across two frozen matchers, not which model wins.
4. **Weeks 5--6:** run paired VIS, VIS-recapture and IR captures at matched attempt budgets. Start with VIS-only, IR-only, fixed two-shot and equal-score fusion. Do not train adaptive fusion unless simple baselines leave a repeatable residual.
5. **End-of-week-6 gate:** select at most one thesis path. Promote O1 only for a repeatable held-out factor interaction beyond standard controls. Promote O2 only if IR contributes stable independent information and beats matched-cost VIS recapture. If neither survives, retain the polished demo and pivot the thesis to the bounded negative/measurement result rather than inventing a fusion network.

### Research-gate sequence through December and 2027-H1

1. **G0 apparatus truth:** lawful data; consent/deletion; frozen hardware/software; actual spectral/illumination state; repeatable portable transaction. Failure means demo engineering only.
2. **G1 factor existence:** ring/environment or IR condition produces a repeatable session-held-out effect at the stage claimed. Failure yields a useful null and kills specialized modeling.
3. **G2 simple-baseline residual:** effect/action benefit survives fixed crop, standard augmentation, score-only quality, static guide, fixed recapture, single modalities, always-two-shot and equal fusion at matched cost. Failure means the simple baseline becomes the demo design.
4. **G3 identification:** labels are assigned independently; identity/session/capture order are blocked; camera/exposure/ROI/matcher confounds are measured or explicitly unresolved. Failure forbids causal wording.
5. **G4 evidence scale:** expand participants and sessions only after G0--G3. Predeclare the unit of independence and interval/reporting rule. Do not turn frame or pair counts into subject counts.
6. **G5 final contribution:** choose one of: bounded factor-interaction evidence, bounded IR incremental-information evidence, or a preregistered negative result showing that simple controls dominate. Demo accuracy/latency remains a separate engineering result.

## Evidence ledger

| Claim | Label | Primary source and version/date | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| A complete local contactless palm pipeline with ROI, quality rejection and compact templates already exists on mobile. | [K] | Palm-ID, arXiv:2401.08111v1 (2024-01-16), https://arxiv.org/html/2401.08111 ; IEEE TIFS DOI https://doi.org/10.1109/TIFS.2024.3413631 | HTML Secs. II-A--II-G, III-C--III-E, IV-A--IV-B | Mobile/operational datasets, not this Pi. Reported search hardware cannot be transferred to Pi timing. |
| Open-environment FVP-free ROI and recognition are established; lighter deployment is future work, not proof of a gap. | [K] | Chai et al., IEEE TIFS 20 (2025), DOI https://doi.org/10.1109/TIFS.2024.3516539 ; author PDF https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf | Sec. I pp. 421--423; Sec. II pp. 423--425; Sec. III-B pp. 426--427; Sec. IV pp. 429--433; Sec. V p. 433 | GPU/public-dataset result; no Pi transaction or ring-factor study. |
| Hand geometry, flatness, brightness and sharpness are already combined for palm quality assessment and are closely aligned with Bob Zhang. | [K] | Zhang et al., IEEE TIM 73 (2024), DOI https://doi.org/10.1109/TIM.2024.3485454 ; official record https://scholarship.miami.edu/esploro/outputs/journalArticle/HGAIQA-A-Novel-Hand-Geometry-Aware-Image-Quality/991032796016102976 | Official abstract and pp. 1--13 bibliographic record | Full article sections were unavailable; no stronger claim than the abstract is used. Advisor fit is not novelty. |
| Robustness augmentation and identity-disjoint/open-set palm protocols are current method families. | [K] | Jin et al., ICCV 2025, official CVF paper https://openaccess.thecvf.com/content/ICCV2025/papers/Jin_Unified_Adversarial_Augmentation_for_Improving_Palmprint_Recognition_ICCV_2025_paper.pdf | Secs. 1, 3, 4.1--4.3 and experiment tables | Does not specifically establish the proposed physical ring-by-environment endpoint; it is the strong augmentation neighbor. |
| Palmprint+palm-vein adaptive fusion with uncertainty/certainty routing is established. | [K] | Fan et al., IEEE TSMC 54(7), 2024, 4471--4484, DOI https://doi.org/10.1109/TSMC.2023.3346961 | Abstract, method and experiment/result sections recorded in 2026-09-13 validation audit | Exact low-cost Pi observation path is not established, but generic fusion novelty is occupied. |
| Missing-modality palmprint/palm-vein representation and recovery are established. | [K] | Pan et al., *SSFD-Net*, DSP 159 (2025) 105003, DOI https://doi.org/10.1016/j.dsp.2024.105003 | Abstract, proposed method, experiments/missing-rate ablations, conclusion as recorded in validation audit | Does not answer whether this hardware supplies a valid vein modality or useful IR action. |
| VIS-NIR cross-spectral palmprint common-feature learning is established. | [K] | Fei et al., IEEE TIFS 2024, DOI https://doi.org/10.1109/TIFS.2024.3441945 | Official abstract/metadata and archived VIS-NIR boundary notes | Full text/weights were not inspected in this pass; used only to block a broad cross-spectral claim. |
| Embedded palm camera, illumination, UI and local matching existed well before Raspberry Pi. | [K] | Shen et al., Sensors 12(2), 2012, https://doi.org/10.3390/s120201482 ; full text https://pmc.ncbi.nlm.nih.gov/articles/PMC3304123/ | Secs. 2--5, apparatus and timing/results | Fixed positioning and old OMAP/DSP; no modern open-environment or PAD claim. |
| Palm/hand/finger geometry and vascular-pattern fusion from one low-cost image is established. | [K] | Lee et al., Sensors 13(3), 2013, https://doi.org/10.3390/s130302895 ; full text https://pmc.ncbi.nlm.nih.gov/articles/PMC3658721/ | Secs. 2--4 and Table 1 literature comparison | Older datasets/methods, but enough to kill “finger ratios plus palm is new.” |
| Dorsal-hand/palm/hand-feature fusion is a broad, occupied family rather than a fresh thesis identity. | [K] | Zhong et al. works catalogued in Awad et al., *Hand-based multibiometric systems*, 2021, https://pmc.ncbi.nlm.nih.gov/articles/PMC8507475/ | Review modality/fusion tables and discussion | Review is not load-bearing proof of an exact collision; direct-neighbor full texts remain [GAP] before any dorsal claim. |
| Biometric factor controls, threshold uncertainty, failure-to-acquire and interaction conditions must be explicit. | [K] | ISO/IEC 19795-1:2021 https://www.iso.org/standard/73515.html ; ISO/IEC 19795-10:2024 https://www.iso.org/standard/81223.html ; ISO/IEC 21472:2021 https://www.iso.org/standard/70840.html | 19795-1 Secs. 6.4--6.5, 7--8; official 19795-10 scope; 21472 Introduction, Secs. 1, 3 | Standards define evaluation discipline, not a contribution; full paid text was not available for every clause. |
| The local demo currently provides Fast-CC enrollment/verification and profile checks but explicitly disclaims vein, liveness, PAD and security claims. | [E] | Local `code/palm_demo/README.md`, `BASELINES.md`, `palm_demo.py`, inspected 2026-09-13 | README sections “What this demo proves,” “RGB and NoIR setup,” “First demo”; baseline register; CLI/profile enforcement code | Engineering state only; no live test was run in this divergence task. |
| Rings cause a repeatable, recognition-relevant physical effect in this apparatus. | [GAP] | No primary paper/source in the inspected chain establishes this exact factor for this system | Not applicable | Must be tested; it is not justified by supervisor interest alone. |
| The proposed NoIR+IR path captures repeatable palm-vein information. | [GAP] | No local spectral/capture evidence yet; low-cost Pi vein precedents are apparatus-only evidence | Not applicable | Gate 0 requirement. Bright NIR texture is not automatically a vein modality. |

## Queries and failed searches

- `site:ieeexplore.ieee.org palmprint ring occlusion contactless recognition hand accessories paper`
- `"rings" contactless palmprint recognition occlusion`
- `"palmprint" accessories rings robustness`
- `site:openaccess.thecvf.com palmprint palm vein multimodal fusion recognition paper 2024`
- `site:arxiv.org palmprint dorsal hand finger geometry multimodal recognition`
- `"palmprint" "finger geometry" multimodal biometric fusion paper`
- `"palmprint" "dorsal hand" recognition fusion paper`
- `site:ieeexplore.ieee.org palmprint open environment ROI recognition 2025`

The ring/accessory queries did not retrieve a strong primary palmprint paper whose exact task is a controlled ring-by-environment verification/action study. This is only a bounded search result. Nearby open-environment ROI and robustness/augmentation work creates high collision risk, so O1 is framed as a factor-interaction/negative study, not a novelty claim. Finger-geometry and dorsal searches retrieved old and recent multimodal/fusion families, which defeat a generic same-feed fusion claim. IR searches and the existing audit retrieved direct palmprint+palm-vein, missing-modality and VIS-NIR neighbors, but no evidence that this project's NoIR path measures veins.

Uncertainties: exact Pi/camera inventory and whether a true VIS camera is available; IR wavelength, optical power, safety documentation and delivery; whether palm veins are visible/repeatable; team size and participant access; institutional ethics route; ring types and whether participant-owned jewelry may be handled; final December date; dataset licences; stronger matcher availability; energy instrument; whether dorsal capture is acceptable within one payment-like transaction; and whether Bob Zhang prefers a positive algorithm paper over a rigorous bounded negative/evaluation result.

## Decision

Proceed now with the mandatory modular demo and the O1 ring/environment feasibility matrix. In parallel, buy/prepare IR illumination only against the explicit O2 hardware-truth test. Keep O3 guidance in the demo architecture and O4 geometry/dorsal features as logged controls. Do not choose a learned fusion or auxiliary-feature thesis until a held-out residual survives the simple baselines and identification gates.

This resets the practical plan from “find novelty before building” to “deliver the professor's demo while making every optional research claim earn its place.” The demo is promoted as an engineering commitment; the thesis remains conditional. If O1 and O2 both fail, the correct deliverable is the polished verifier plus a bounded negative result, not a new model name.

PIVOT
