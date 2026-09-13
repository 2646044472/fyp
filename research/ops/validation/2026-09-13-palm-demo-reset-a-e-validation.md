# Decision investigated

Whether the professor-requested palm-payment-like FYP should now be executed through one of five likely routes—(A) accuracy/model improvement, (B) robust ROI/recognition under rings, pose, light and background, (C) VIS+IR quality-aware fusion or adaptive acquisition, (D) same-feed hand geometry/dorsal soft biometrics, or (E) edge runtime/portability/HCI—and, for each route, what is ordinary demo engineering, what exact claim could remain falsifiable after direct-neighbor review, and what evidence should kill or promote it before the December 2026 demo.

The 2026-09-04 Bob Zhang supervisor record supplied for this audit is treated as authoritative. It fixes the immediate project intent: build palm recognition; do not pursue cross-device or end-to-end physical-print attacks; prioritize portability, higher accuracy and real-environment robustness including rings; begin IR palmprint/palm-vein multimodality and perhaps same-feed geometry/dorsal features; retain future edge/HCI/security possibilities; and obtain IR illumination hardware plus conduct literature review. The intended sequence is professor-requested demo first, novelty later. This changes execution priority, but it does not turn a demo priority into a research contribution.

## Claim under test

The broad claim—“a portable Pi palm-payment-like system becomes a defensible FYP research contribution by improving accuracy, robustifying ROI, adding NoIR+IR fusion, extracting more same-feed hand traits, or optimizing edge runtime”—is **killed**. Every component is directly occupied, and the current code/data cannot support a field, security, palm-vein, or population-performance claim.

The narrow claim that may remain is:

> **[C] PALM-ROBUST-ACT.** On one frozen Pi/camera/illumination path, for consented participants separated by identity and session, a predeclared capture-quality/ROI rule changes the non-dominated frontier of `match / one guided recapture / abstain` under held-out ring, pose, illumination and background cells, compared with matcher-score-only, fixed-guide, fixed-one-recapture and always-abstain policies at the same false-match operating point and with transaction time/retry cost charged.

This is an end-to-end scenario-evaluation claim, not a new recognizer, ROI detector, fusion network, palm-vein system, liveness mechanism, payment-security result, or global robustness claim. A valid null—simple policies dominate—remains an acceptable evaluation result. With only 3–5 people it is a bring-up pilot, not a promoted thesis result.

## Supervisor constraint reconciliation

| Supervisor priority | Valid immediate interpretation | Invalid research inference |
| --- | --- | --- |
| Palm recognition / payment-like demo | Build a local 1:1 enrol/verify interaction with a non-financial mock decision and visible retry/abstain states. | “Payment-like” does not authorize a payment-security, PAD, liveness or operational FAR claim. |
| Portability | Freeze the Pi, camera, mount, illumination, power and software artifact; measure capture-to-decision time and failure states. | Running on Pi is not novelty. |
| Higher accuracy | Establish a lawful, leakage-resistant baseline and compare only frozen alternatives. | Model replacement, augmentation or EER reduction alone is not a distinct contribution. |
| Rings / real environment | Treat ring, pose, light and background as separately randomized presentation factors with held-out sessions. | A mixed “real-world” bucket cannot identify which factor caused a change. |
| Early IR / palmprint-palm-vein | Build and characterize a logged NoIR+controlled-NIR acquisition path first. Call it NoIR+IR until vascular contrast and repeatability are demonstrated. | Removing an IR-cut filter plus adding IR LEDs does not by itself establish a palm-vein modality. |
| Same-feed geometry / dorsal traits | Log segmentation and geometry as quality or auxiliary measurements; dorsal data requires an explicitly dorsal view. | Palmar feed geometry is not a new modality; a palmar image cannot be relabelled dorsal. |
| Future edge/HCI/security | Instrument transaction time, retries, local retention and resource use so later studies are possible. | Future-work labels are not present contributions. |

## Three-round novelty audit

| Route | Component collision | Exact-claim collision | Boundary / impossibility | Remaining distinction | Confidence |
| --- | --- | --- | --- | --- | --- |
| A — accuracy/model improvement | Palm-ID combines CNN/ViT multiscale embeddings, enhancement, compact templates and mobile deployment; SYEnet and many open-set/contactless methods already pursue lightweight accuracy. | Palm-ID reports end-to-end mobile capture, quality rejection, cross-database/time-separated evaluation and fixed-FAR verification. BEST and W2ML already target real-world/cross-sensor and open-set matching. | A local EER gain can be caused by identity/session leakage, threshold retuning, ROI changes, or repeated-frame pseudoreplication. With no independent population and session design, “higher accuracy” is not transportable. | Only a bounded reproduction or cost-inclusive comparison of frozen public baselines on the named apparatus. | High collision; high kill confidence. |
| B — robust ROI/recognition | Contactless ROI extraction under free pose/clutter dates at least to Aykut & Ekinci 2015; Chai et al. 2025 explicitly removes finger-valley dependence for open-environment ROI. HGAIQA measures whole-hand flatness, brightness and sharpness before recognition. | The direct task—handle pose, illumination and complex background to improve downstream recognition—is already studied. Ring occlusion is a useful stress cell but not by itself a new task. | If ring/pose/light/background are co-varied, attribution is impossible. If ROI labels come from the same detector under test, ROI robustness is circular. A score-only or fixed recapture rule can absorb much of the benefit. | PALM-ROBUST-ACT: factor-controlled `match / guided recapture / abstain` frontier, with action cost and held-out sessions, not a new ROI network. | High collision; medium confidence on residual until pilot. |
| C — VIS+IR quality-aware fusion / adaptive acquisition | Palmprint+palm-vein score, feature and image fusion are mature; BPFNet jointly handles ROI alignment and fusion; Fan et al. 2024 uses adaptive hybrid fusion; Pan et al. 2025 handles missing modalities; IJCB 2025 uses adaptive early fusion for embedded efficiency. Generic quality-aware fusion is also established. | “Use VIS and IR quality to weight/fuse or decide acquisition” overlaps quality-aware multimodal recognition and adaptive sensing. A Pi implementation changes hardware, not the task/action/endpoint. | The current confirmed NoIR path mixes visible and NIR unless visible light is optically rejected. Unsynchronised auto-exposure/white-balance and sequential capture confound modality with time, pose and gain. Without demonstrable vascular signal, “palm vein” is an unsupported label. | A hardware characterization gate; later, at most, a finite value-of-information test where an independently logged NIR intervention changes `recapture / abstain` at matched time/energy. | Very high collision; high kill confidence for a new fusion method. |
| D — same-feed geometry / dorsal soft biometrics | Single-capture multimodal hand systems already combine geometry, palmprint, knuckle print, palm/finger vein; Zhu & Zhang 2010 fuse geometry, knuckle and palmprint; Kumar et al. 2012 acquire five features in one contactless presentation and include quality-aware fusion. | Same-image geometry-assisted quality is directly occupied by HGAIQA, Bob Zhang's closest relevant paper. Same-feed recognition-score fusion is also old. | Features from the same segmentation/capture are correlated and share failures; calling them separate modalities overstates independence. A palmar view does not observe dorsal texture. Geometry may encode size/shape but may not add stable identity information after scale normalization. | Use geometry first as capture-quality/pose side information. Promote only if it adds held-out action value beyond ROI validity and matcher score; otherwise keep as UI/debug telemetry. | High collision; high kill confidence. |
| E — edge runtime / portability / HCI | Palm-ID embeds a full pipeline on mobile and reports template/search efficiency. ISO/IEC 19795-1 and TS 19795-9 already define technical/mobile performance reporting; ISO/IEC 21472 defines user-interaction scenario evaluation. | Pi latency, RSS, temperature and packaging are deployment characterization. Guided capture/retry HCI is a valid study only if reference/target evaluation conditions, transactions and user actions are explicit. | Faster inference need not shorten transaction time when acquisition and retries dominate. Three to five users cannot establish usability, demographic, operational or payment claims. CPU utilization is not energy. | A later small HCI scenario study comparing one frozen guide/retry policy to a fixed guide/no-guide baseline, with failure-to-acquire, attempts and p95 transaction time. | High collision for runtime novelty; medium residual for bounded HCI. |

## Assumption and identification audit

### Observation and action

The current `code/palm_demo` is a local-only, fixed-stand 1:1 baseline. It uses a default fractional crop `(0.19, 0.15, 0.81, 0.85)`, Fast-CC, a contrast gate, five enrolment samples and a provisional distance threshold of `0.28`. It records separate `rgb` and `noir-ir` profiles and refuses cross-profile matching. This is good engineering hygiene, but it supplies no automatic hand detector, landmark truth, ring label, pose label, illumination measurement, retry policy, liveness/PAD test or payment action.

For research identification, physical conditions must be assigned outside the algorithm. A run sheet or fixture must specify participant pseudonym, hand, session, ring state/type/location, pose bin, distance bin, illuminance/lighting arrangement, background, camera/illuminator state, mount revision and capture order. The policy may see only the frame, frozen ROI/quality features, matcher score and runtime state. It must not see the condition label.

The correct action is not simply `ACCEPT/REJECT`. The potentially defensible endpoint is a transaction policy: `match`, one predeclared guided recapture, or `abstain`. Match errors, failure-to-acquire, attempts and time are jointly reported. If no action/cost is defined, route B reduces to ordinary robustness benchmarking and route E to profiling.

### Ring, pose, light and background

- **[K] Rings are an occlusion/presentation factor, not automatically an attack.** The scientific question is whether ring presence/location corrupts segmentation, landmarks, ROI normalization, matcher score or interaction. At least “no ring,” one fixed non-reflective ring, and one fixed reflective/wide ring should be predeclared; do not use participants' uncontrolled jewellery as the only condition.
- **[K] Pose must be measured or fixture-assigned.** In-plane rotation, out-of-plane pitch/roll, translation, scale/distance and finger spread should not be collapsed into one label. The minimum December demo may visualize these as guidance tolerances; the thesis pilot should vary one factor at a time before testing combinations.
- **[K] Lighting requires apparatus logs.** Camera auto controls can compensate and erase or entangle intended light cells. Freeze or record exposure, analogue/digital gain, white balance, frame duration and illumination state. “Low light” without a repeatable lamp geometry and logged camera state is not an identified factor.
- **[K] Background robustness must not leak through capture order.** Randomize background within session or block it explicitly. A detector trained/tested on the same few backgrounds measures memorization.

### NoIR+IR and the palm-vein label

NoIR means the camera lacks an IR-cut filter; it does not mean the output contains isolated NIR or that vascular structure is usable. Published palm-vein acquisition systems specify the sensor's NIR sensitivity, active wavelength (commonly 850 or 940 nm), reflection/transmission geometry, visible-light rejection and controlled placement. Wu et al. 2019 used an NIR-sensitive CMOS camera, 850 nm LED array, enclosed black-background box and 1,500 images. Piciucco et al. 2018 used an 850 nm source, a sensor sensitive to 450–900 nm, an 825 nm cut-on optical filter and a docking device. Those controls are materially stronger than “NoIR camera + IR fill.”

Therefore:

1. Call the path **NoIR+IR** during bring-up.
2. Record exact camera revision, sensor, LED peak wavelength/bandwidth, optical power or at least electrical input, distance, angle, diffuser, exposure/gain and ambient-light state.
3. Add a visible-blocking/NIR-pass filter or a dark enclosure if the goal is an NIR observation rather than mixed-spectrum imaging.
4. Before any palm-vein claim, show repeatable subcutaneous vascular contrast on repeated sessions, using a frozen enhancement method, and show that the signal is not reproduced by visible palm creases, shadows or exposure changes.
5. Evaluate NoIR+IR alone before fusion. If it cannot beat or complement VIS under identity/session-held-out verification, stop calling it a recognition modality.
6. Do not infer liveness or anti-spoofing from vein-like appearance. PAD requires a separate threat model and ISO/IEC 30107-style attack evaluation; it is outside this reset.

**IR hardware stop rule:** if, after two controlled bench iterations (fixed 850/940 nm source, geometry, exposure and visible rejection), vascular contrast is not repeatable within person across two sessions or is no more stable than a VIS crease/shadow baseline, stop the palm-vein branch. Retain NoIR+IR only as an alternate illumination/capture profile.

### Same-feed geometry and dorsal features

Palmar silhouette/landmarks can yield hand geometry from the same frame, but this is already a known biometric and a known quality cue. Its first use should be measurement, not score fusion: flatness, finger spread, clipping, rotation and scale. Compare it against ROI-validity and matcher-score baselines. If it adds no held-out decision value, remove it from the research claim while keeping it for UI guidance.

“Dorsal” requires viewing the back of the hand or an additional view/sensor. A palmar camera feed cannot observe dorsal knuckle texture or dorsal veins. If the demo asks the user to flip the hand, this is a second interaction and capture action, not same-feed fusion; charge its time and user burden. Do not pursue dorsal data before the palmar transaction is stable.

### Data, ethics and effective sample size

- The local `PalmBigDataBase.zip` and CASIA archive have hashes but unresolved source agreements. They may be inventory, not permission. Do not extract, train, publish or show samples until the original licence/agreement and intended use are recorded.
- Palm images and templates are biometric data even when local and even for a classroom demo. Obtain the supervisor/institution's required approval and participant consent before collection. Use pseudonymous IDs, minimize retained frames, document retention/deletion, restrict access and delete raw images/templates together when consent or protocol requires it.
- Three to five participants are sufficient only to debug capture, naming, consent, repeated sessions and analysis code. Pair counts are not independent subjects. A large number of impostor comparisons among five people does not justify a low FMR claim.
- For the research phase, predefine the target population and recruit enough independent hands/sessions to make the chosen operating point meaningful. No universal number follows from the present evidence, but a claim at `FMR = 0.01%` cannot be empirically supported by dozens or hundreds of impostor transactions. Report binomial uncertainty and identity/session-clustered resampling; zero observed errors is not zero risk.
- Separate development and evaluation by identity where model/quality rules learn population features, and by session for any same-person robustness claim. Thresholds, ROI rules, quality rules and fusion weights must be frozen on development data.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Grosz, Godbole & Jain, **Palm-ID**, arXiv v1, 2024-01-16, https://arxiv.org/abs/2401.08111 | Mobile contactless hand image; ROI, enhancement, CNN/ViT features, quality rejection; local pipeline | Verification/identification, fixed FAR, cross-database/time-separated data, template/search latency | A, B and E: end-to-end mobile recognition, quality rejection and efficiency | Kills generic “accurate portable palm recognizer.” Leaves device-specific reproduction and a differently defined action/cost study. |
| Zhang et al., **HGAIQA**, IEEE TIM 73 (2024), DOI https://doi.org/10.1109/TIM.2024.3485454; official record https://scholarship.miami.edu/esploro/outputs/journalArticle/HGAIQA-A-Novel-Hand-Geometry-Aware-Image-Quality/991032796016102976 | Whole hand, segmentation, joint keypoints, flatness, brightness, sharpness; discard low-quality images | EER change after removing lowest-quality images; reports 21.2% EER reduction on COEP | B and D; closest Bob Zhang neighbor | Kills generic geometry-aware quality/robustness. Leaves action-cost scenario evaluation only. Advisor fit is not novelty. |
| Chai et al., **Joint Finger Valley Points-Free ROI Detection and Recurrent Layer Aggregation**, IEEE TIFS 20 (2025), 421–435, author PDF https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf | Open-environment hand segmentation and adaptive FVP-free ROI; recognition network | ROI/recognition on closed/open/cross-dataset protocols | B | Kills “new robust ROI under unconstrained capture” without a sharper distinction. |
| Aykut & Ekinci, **Developing a contactless palmprint authentication system by introducing a novel ROI extraction method**, Image and Vision Computing 40 (2015), 65–74, https://doi.org/10.1016/j.imavis.2015.05.002 | Unrestricted contactless capture, pose/rotation/position variation, cluttered backgrounds; model-based ROI | ROI success and authentication on 1,752 images / 145 subjects | B | Kills the premise that pose/background ROI is an unstudied task. |
| Feng & Kumar, **BEST**, Pattern Recognition 138 (2023), 109422, https://doi.org/10.1016/j.patcog.2023.109422 | Scattered templates, contactless/cross-sensor images | Cross-sensor/cross-dataset matching; >35M scores reported | A and robustness matching | Makes a small local accuracy/model claim especially weak. |
| Li et al., **BPFNet**, arXiv v1 2021-10-04, https://arxiv.org/abs/2110.01179 | Palmprint+palm-vein ROIs; detection, alignment, cross-modal selection and fusion | Recognition on CUHKSZ-v1 and TongJi | C | Kills generic bimodal ROI alignment/fusion. |
| Fan et al., **A Novel Hybrid Fusion Combining Palmprint and Palm Vein for Large-Scale Palm-Based Recognition**, IEEE TSMC 54(7), 2024, 4471–4484, https://doi.org/10.1109/TSMC.2024.3382877 | Palmprint/palm-vein scores and adaptive hybrid fusion | Large-scale recognition; genuine/impostor/uncertainty routing | C | Kills adaptive palmprint/palm-vein weighting as a broad method claim. Full method sections remain access-limited in this audit. |
| Pan et al., **SSFD-Net**, Digital Signal Processing 159 (2025), 105003, https://doi.org/10.1016/j.dsp.2025.105003 | Palmprint/palm-vein with missing modality | Recognition under modality absence | C | Kills “fusion robust to unavailable IR” as a generic contribution. Full text access remains limited. |
| Li et al., **Rethinking Early-Fusion Strategy for Palmprint and Palm Vein Fusion Recognition**, IJCB 2025, DOI https://doi.org/10.1109/IJCB65343.2025.11411526 | Adaptive image-level fusion and modality-aware distillation, single-stream inference | Four multimodal benchmarks; embedded-efficiency motivation | C and E | Kills adaptive early fusion for efficient embedded use as a new route. Publisher record added 2026-03-03. |
| Kumar, Zhang & Wong, **A contactless biometric system using multiple hand features**, Journal of Visual Communication and Image Representation 23(7), 2012, 1068–1082, https://doi.org/10.1016/j.jvcir.2012.07.007 | One hand presentation; hand geometry, palmprint, palmar knuckle, palm vein, finger vein; image quality/fusion | Recognition and modality correlation | C and D | Kills same-capture multi-hand-feature fusion as new. Its finding that a simple sum is reasonable on cleansed data strengthens the simple baseline. |
| Zhu & Zhang, **Multimodal biometric identification system based on finger geometry, knuckle print and palm print**, Pattern Recognition Letters 31(12), 2010, 1641–1649, https://doi.org/10.1016/j.patrec.2010.05.010 | One webcam hand image; geometry, knuckle and palmprint; decision-level AND fusion | Identification/verification on 1,900 images / 190 hands, one session | D | Kills same-feed geometry/texture fusion as a new method. The one-session design is not a model for robustness evidence. |
| Wu et al., **Low-cost biometric recognition system based on NIR palm vein image**, IET Biometrics 8 (2019), 206–214, https://doi.org/10.1049/iet-bmt.2018.5027 | NIR-sensitive CMOS, 850 nm LED array, enclosed reflective box/black background; palm-vein processing | 1,500 acquired images and recognition evaluation | C hardware gate | Shows low-cost vein capture is already occupied and requires controlled optics. Leaves only apparatus-specific validation. |
| Piciucco et al., **Palm vein recognition using a high dynamic range approach**, IET Biometrics 7 (2018), https://doi.org/10.1049/iet-bmt.2017.0192 | 850 nm illumination, 825 nm cut-on filter, NIR camera, docking device; HDR | 86 subjects, repeated exposures; vein-image quality/recognition | C hardware/quality | Kills “IR fill plus quality enhancement” as new and defines a stronger vein-acquisition control. |
| ISO/IEC 19795-1:2021, official preview https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A19795%3A-1%3Aed-2%3Av2%3Aen | Biometric comparison decisions and transactions | Error/throughput, failure-to-enrol/acquire, protocol/reporting, confidence/test size | A, B and E evaluation | Kills informal “accuracy” reporting and separates technology, scenario and operational claims. Explicitly excludes PAD/security testing. |
| ISO/IEC TS 19795-9:2019, official preview https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3Ats%3A19795%3A-9%3Aed-1%3Av1%3Aen | Mobile-device local authentication | Affordable full-system mobile testing/reporting | E | Kills “mobile test protocol” as a contribution; excludes PAD and isolated subsystem claims. |
| ISO/IEC 21472:2021, official preview https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A21472%3Aed-1%3Av1%3Aen | User interaction under reference/target evaluation conditions | Scenario methodology and interaction influence | B and E | Leaves a bounded guide/retry HCI experiment, but only with explicit transaction, conditions and participant protocol. |
| ISO/IEC 29794-1:2024, official preview https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A29794%3A-1%3Aed-3%3Av1%3Aen | Biometric quality scores and aggregation | False-non-match/false-match versus discard frameworks | B and C | Kills ad hoc “quality score improves accuracy” framing; quality must be tied to a declared utility/error endpoint. |

## Strongest simple baseline

The decisive baseline is not another neural model. It is a frozen transaction matrix:

1. current fixed crop + Fast-CC + frozen threshold;
2. matcher score only;
3. fixed geometric guide/window with deterministic crop;
4. one scalar pre-match quality gate (contrast/blur/ROI-validity), thresholds frozen on development sessions;
5. always take one second capture;
6. fixed `match / one guided recapture / abstain` rule;
7. always abstain at the same claimed false-match ceiling;
8. VIS-only and NoIR+IR-only reported separately;
9. if fusion is reached, unweighted normalized score sum and best-unimodal fallback before any learned weighting;
10. if geometry is reached, matcher score + ROI validity before geometry features.

All policies must use the same enrolment set and held-out transaction stream. Charge captures, retries, p50/p95 transaction time and, only if directly measured, energy. Report failure-to-acquire separately from false non-match. If a proposed model, quality feature, fusion rule or HCI mechanism does not create a non-dominated held-out point over this matrix, it is unnecessary for the FYP claim.

## Contrarian result

The professor's plan is coherent as a build sequence and weak as a novelty sequence. Accuracy, ROI robustness, IR fusion, auxiliary hand features and Pi portability are precisely the features that make the demo persuasive; they are also mature research families. Trying to “find novelty” inside each feature will produce five shallow claims and jeopardize December.

The strongest strategy is to deliberately separate artifacts:

- **Demo artifact:** a stable local 1:1 palm interaction with explicit `match / retry / unable` states, controlled enrolment and transparent limitations.
- **Measurement artifact:** a factorized capture log for ring, pose, light and background, plus session/identity-safe evaluation and Pi transaction timing.
- **Research gate:** only after the demo is stable, test PALM-ROBUST-ACT against the simple baseline matrix. The research object is the action frontier under presentation factors, not the recognizer's brand or architecture.
- **IR branch:** parallel hardware feasibility only. It may improve the demo, but it is not called palm-vein or fused into the research claim until it passes the optical and repeatability gates.

This preserves the supervisor-requested FYP while preventing the project from claiming a novelty that direct papers already own.

## Feasibility audit and December gate

| Dependency | Current evidence | December feasibility | Stop / promotion condition |
| --- | --- | --- | --- |
| Runnable verifier | Current fixed-crop Fast-CC baseline and local logging exist. | High, after camera bring-up and lawful consent. | Stop model work until deterministic replay and same-stand enrol/verify pass on the Pi. |
| Automatic ROI | Not implemented; current crop is fixed. Strong direct neighbors exist. | Moderate for a standard landmark/segmentation implementation; risky for a new network. | Use an existing method or simple guide. Stop “new ROI model” if fixed guide/crop meets demo needs. |
| Ring/pose/light/background cells | No independent labels or repeated capture log found. | High for a small pilot if factors are separated. | Stop robustness claim if condition labels are inferred from the tested images or all factors are mixed. |
| IR illumination | Exact camera revision, LED wavelength/power, filter, geometry and safety remain gaps. | Moderate; hardware bring-up is feasible, palm-vein validation is uncertain. | Two controlled iterations only before the vein stop rule. Do not delay VIS demo for IR. |
| Fusion | No lawful paired Pi VIS/NIR corpus, synchronized path or frozen unimodal baselines. | Low before December as research; moderate as a visual demo after hardware works. | No learned fusion until each modality passes held-out unimodal tests and simple sum/fallback is beaten. |
| Geometry/dorsal | Palmar geometry can be derived; no dorsal view/protocol exists. | Geometry quality cues are feasible; dorsal is schedule risk. | Defer dorsal until palmar demo and robustness logs are stable. Kill recognition fusion if score/ROI baseline ties. |
| Runtime/energy | Pipeline time is logged; no verified energy instrument or complete transaction timing. | Latency/RSS/temperature are feasible; energy only if instrumented. | Do not call CPU load energy. Runtime is characterization unless tied to user/action frontier. |
| Data licence | PalmBigDataBase and CASIA terms unresolved locally. | Blocking for publication/training; not needed for consented bring-up if ethics allows. | No use beyond inventory until source/terms are recorded. |
| Human data | Authorization flag exists, but it is not ethics approval. | Small consented pilot may be feasible subject to institution/supervisor. | No collection before approval/consent/retention plan. Stop any operational/payment claim. |
| Sample size | Proposed 3–5 people is a pilot. | Adequate for plumbing and failure discovery only. | Do not freeze production-like FAR/FMR or promote research from this cohort. Recruit a justified cohort with repeated sessions in 2027. |

## Unambiguous recommended execution sequence

1. **Freeze scope immediately.** The December target is a non-financial, local 1:1 palm-payment-like demonstration. UI states are `match`, `retry`, and `unable`; no PAD, liveness, attack, payment security, palm-vein or operational accuracy language.
2. **Clear data and human-subject gates before capture.** Record approval/consent, pseudonymous schema, retention/deletion and dataset licences. If this is not cleared, use only lawful public/synthetic/non-personal plumbing inputs and do not enrol people.
3. **Bring up the VIS baseline first.** Pin Pi/OS/camera/mount/light/software; run deterministic images; then same-stand live enrol/verify. Log stage and full transaction times, failures and camera controls. Do not change matcher and ROI simultaneously.
4. **Add a standard capture guide/ROI, not a research ROI model.** Begin with fixed guide + deterministic crop/standard landmarks. Compare automatic ROI to this control only after the demo is stable. A failed automatic ROI falls back to guided recapture, not silent matching.
5. **Run the 3–5-person D0 pilot across at least two sessions.** Its purpose is to validate consent, metadata, transaction logic, factor manipulation and analysis—not accuracy. Separate no-ring/ring, pose, light and background cells; randomize or block capture order; retain the smallest data needed.
6. **Freeze the baseline matrix and stop model shopping.** Select a threshold only on development identities/sessions. Report FMR/FNMR, failure-to-acquire, attempts and p95 transaction time with clustered uncertainty. If score-only/fixed-guide/fixed-recapture solves the observed failures, keep it and do not invent a learned method.
7. **In parallel, execute a bounded IR hardware gate.** Buy/verify a specified 850 or 940 nm illuminator with appropriate electrical/optical safety information; record filter and geometry. Characterize NoIR+IR separately. Do not block steps 3–6 on it.
8. **Apply the palm-vein stop rule.** Only after repeatable vascular contrast across sessions and a held-out NoIR+IR recognition baseline may the branch be named palm-vein. Otherwise label it alternate IR illumination and stop fusion work.
9. **Choose one 2027 research gate: PALM-ROBUST-ACT.** Preregister the action, allowed observations, factor cells, development/evaluation split and simple baselines. Recruit a justified larger cohort with repeated sessions. Do not pursue A, C, D and E as simultaneous novelty claims.
10. **Promote only on a held-out action result.** Promotion requires a repeatable non-dominated improvement in the false-match/false-non-match/failure-to-acquire/retry/time frontier over score-only, fixed guide, fixed recapture and abstain controls, with the improvement surviving identity/session-clustered uncertainty. A model-only EER gain, a nicer demo, a Pi speedup, or a fusion ablation does not qualify.

### Route-specific stop rules

- **A stop:** after one classical/lightweight baseline and one strong public embedding baseline, stop if confidence intervals overlap or gains disappear under frozen identity/session splits. Never search architectures indefinitely.
- **B stop:** stop new ROI/quality development if fixed guide + score-only + one recapture is non-dominated on held-out cells, or if condition effects cannot be independently assigned.
- **C stop:** stop palm-vein wording if the optical/repeatability gate fails; stop learned fusion if best unimodal, unweighted sum or fallback ties after cost is charged.
- **D stop:** stop geometry as recognition if matcher score + ROI validity ties; do not start dorsal capture before the palmar protocol is frozen and additional interaction cost is accepted.
- **E stop:** stop novelty claims if results are only latency/RSS/temperature; retain them as demo characterization. Start HCI research only with a predeclared guide/retry comparison and enough participants for the limited claim.
- **Project stop/pivot:** if PALM-ROBUST-ACT produces no non-dominated held-out action effect, submit the palm system as an engineering FYP with an honest robustness evaluation/null result. Do not rescue it by relabelling the same data as adaptive fusion, soft biometrics, edge AI or security.

## Evidence ledger

| Claim | Label | Primary source and version/date | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| The authoritative supervisor direction prioritizes palm recognition, portability, accuracy, ring/real-environment robustness, early IR/palm-vein exploration, possible geometry/dorsal traits and later edge/HCI/security, while excluding cross-device and physical-print attacks. | [K] | User-supplied record of Bob Zhang meeting, 2026-09-04 | Entire supplied record in task statement | Authoritative project constraint, not external novelty evidence. |
| Current project charter says palm candidates are killed as standalone research and the Pi matcher is an engineering/runtime demo unless a distinct authorized task/action/endpoint appears. | [K] | Local `research/active/README.md`, `00-project-charter.md`, `01-candidate-register.md`, state read 2026-09-13 | README Current state and historical Pi gate; charter Current biometric gate; register P1–P6/BIA/IR entries | Active state may later be reconciled only by coordinator. This file does not edit it. |
| Current code is fixed-stand 1:1 Fast-CC with fixed crop, contrast gate, provisional threshold and separate RGB/NoIR+IR profiles; it disclaims PAD/security/cross-device claims. | [E] | Local `code/palm_demo/README.md`, `BASELINES.md`, `palm_demo.py`, state read 2026-09-13 | README scope, RGB/NoIR setup, first demo, authorization; BASELINES table; code lines around constants, crop, capture, enrol and verify | Engineering artifact, not a validation dataset. |
| Local PalmBigDataBase/CASIA permissions are unresolved; 20×10 PalmBigData development subset is smoke-test only. | [GAP] | Local `code/palm_demo/data/SOURCE_MANIFEST.md`, state read 2026-09-13 | Source table and Derived development subset | Hash/file presence does not grant licence or representativeness. |
| Palm-ID already provides mobile end-to-end contactless palmprint capture/ROI/matching, quality rejection and fixed-FAR/time-separated evaluation. | [K] | Grosz et al., arXiv v1, 2024-01-16, https://arxiv.org/abs/2401.08111 | Abstract; paper Secs. II-A–G, III-C–E, IV-A–B; tables/quality-reject discussion as inspected in newest packets | Reported extraction/search timing is not Pi timing. |
| Whole-hand geometry, flatness, brightness and sharpness quality are already linked to palm-recognition EER; Bob Zhang is a coauthor. | [K] | Zhang et al., IEEE TIM 73 (2024), DOI https://doi.org/10.1109/TIM.2024.3485454; University of Miami record above | Official abstract and 13-page bibliographic record | Full publisher PDF was not accessible; enough for component/task collision, not detailed reproduction. |
| Open-environment/FVP-free ROI and pose/background-robust contactless ROI are established. | [K] | Chai et al., TIFS 20 (2025), author PDF above; Aykut & Ekinci 2015 DOI above | Chai Sec. I, II-A/B, III-B pp. 426–427, IV pp. 429–433, V p. 433; Aykut publisher highlights, abstract, acquisition/database and conclusions | Ring-specific effect remains a stress-cell question, not proof of an open method family. |
| Palmprint/palm-vein alignment, adaptive fusion, missing-modality fusion and embedded-efficient adaptive early fusion are occupied. | [K] | BPFNet arXiv v1 2021-10-04; Fan et al. TSMC 2024 DOI; Pan et al. DSP 2025 DOI; Li et al. IJCB 2025 DOI, records above | BPFNet abstract/method overview; publisher abstracts/records for Fan/Pan/Li; IJCB abstract and contribution description | Full Fan/Pan/IJCB PDFs were not all accessible. This establishes direct component/task collision, not line-by-line equivalence. |
| Single-presentation multi-hand-feature systems already combine geometry, palmprint, knuckle and vein traits, including quality-aware/simple fusion. | [K] | Kumar et al., JVCIR 23(7), 2012, https://doi.org/10.1016/j.jvcir.2012.07.007; Zhu & Zhang, PRL 31(12), 2010 DOI above | Publisher highlights, abstract, acquisition, experiments and conclusions | Old work still kills generic component novelty; modern implementation differences need a distinct endpoint. |
| Palm-vein systems specify controlled NIR wavelength, sensor/filter and acquisition geometry rather than relying on a NoIR label. | [K] | Wu et al., IET Biometrics 8 (2019), pp. 206–214, DOI above; Piciucco et al., IET Biometrics 7 (2018), DOI above | Wu Sec. 2 system design and Table 1; Piciucco Sec. 3 quality and Sec. 5.1 setup | A NoIR Pi may be NIR-sensitive, but exact sensor response and usable vascular contrast remain apparatus-specific gaps. |
| Biometric evaluation must report transaction errors/throughput, failure to acquire, test protocol and uncertainty; technical performance is separate from PAD/security. | [K] | ISO/IEC 19795-1:2021 official preview above | Introduction; Scope; definitions 3.10–3.22; annex headings on confidence/test size and zero numerators | Standard preview is partial/paywalled; no operational claim is inferred. |
| Mobile testing and user-interaction scenario methods are already standardized. | [K] | ISO/IEC TS 19795-9:2019 and ISO/IEC 21472:2021 official previews above | TS 19795-9 Scope and Secs. 4–6/Annex A TOC; ISO 21472 Introduction, Scope, Sec. 3 REC/TEC definitions | Standards block novelty-by-protocol but permit a scoped compliant empirical study. |
| Quality-score discard/error analysis is an established framework. | [K] | ISO/IEC 29794-1:2024, Edition 3, official preview above | Clauses 1, 3.3–3.18, 6, 9, 11.2–11.5 | Palm-specific quality details are not standardized here; the general evaluation object is. |
| Newest divergence treats VIS/ROI work as groundwork and identifies small-N and ROI-to-action boundaries; newest validation kills quality-aware fusion as a contribution and rejects automatic palm-vein equivalence. | [K] | Local `research/ops/divergence/2026-09-13-vis-roi-pilot-divergence.md`; `research/ops/validation/2026-09-13-user-palm-practical-plan-validation.md` | Both: Decision, candidate/direct-neighbor matrices, feasibility, evidence ledger and Decision | Prior packets are inputs, not independent primary evidence; this audit reconciles them with the supervisor reset. |

## Queries and failed searches

Search date: 2026-09-13. Primary/official sources were preferred; search snippets and abstracts generated leads but did not establish central novelty.

Queries run:

- `site:openaccess.thecvf.com contactless palmprint recognition occlusion rings pose illumination ROI paper`
- `palmprint recognition rings jewelry occlusion pose illumination robust ROI primary paper`
- `palm vein recognition near infrared wavelength reflective imaging low cost camera primary paper`
- `palmprint palm vein multimodal quality aware fusion adaptive acquisition paper`
- `site:ieeexplore.ieee.org contactless palmprint hand geometry multimodal recognition ring occlusion`
- `site:sciencedirect.com palmprint recognition hand geometry dorsal hand multimodal contactless`
- `site:arxiv.org mobile contactless palmprint recognition quality rejection Palm-ID`
- `site:liru0126.github.io palmprint ROI open environment TIFS 2025`
- `HGAIQA hand geometry aware image quality assessment palmprint 2024 PDF Bob Zhang`
- `site:scholarship.miami.edu HGAIQA 2024 palmprint quality`
- `site:ieeexplore.ieee.org HGAIQA palmprint 2024 3485454`
- `site:iso.org biometric sample size performance testing uncertainty FMR zero errors rule of three ISO 19795`
- Local `rg` searches across `research/active`, newest divergence/validation packets, `minutes` and `code/palm_demo` for palm, ROI, IR, quality, fusion, rings, threshold, enrolment, verification, PAD, runtime and permissions.

Failed or insufficient searches / unresolved uncertainties:

- No strong primary paper isolated “ring presence” as the exact sole independent variable in the same Pi palm transaction/action setting. This is a bounded stress-cell gap, not evidence of novelty; occlusion, unconstrained ROI, geometry-aware quality and complex-background recognition are already occupied.
- The full publisher PDFs for HGAIQA, Fan et al. 2024 and SSFD-Net were not accessible in this pass. Official records establish component/task collisions, but exact ablation and limitation details should be read before any implementation claims direct superiority.
- Exact Pi camera revision/sensor spectral response, IR LED wavelength/bandwidth/power, optical filter, geometry, eye/skin safety documentation and procurement timing remain unknown.
- No local evidence shows repeatable vascular contrast from the planned NoIR+IR setup, so palm-vein remains unearned terminology.
- No institutional decision, consent form, target cohort or retention period was found. Ethics feasibility cannot be assumed from a command-line authorization flag.
- No sample-size calculation is possible until the claim fixes a target FMR/FNMR, desired interval width, number of independent identities/hands/sessions and scenario. Three to five participants remain a D0 pilot by construction.
- No primary source found an exact `match / one guided recapture / abstain` study for rings on this hardware. That residual remains [GAP], not novelty; it must survive a fresh citation-chain audit once its protocol is frozen.

## Decision

**Recommended outcome:** build the professor-requested VIS palm demo now; treat IR, geometry and edge instrumentation as gated engineering branches; reserve only PALM-ROBUST-ACT as the single post-demo research hypothesis. Routes A, C and D are **KILL as standalone novelty claims**; E is **KILL as runtime novelty and HOLD only as a later bounded HCI scenario**; B is **PIVOT** from “robust ROI model” to a factor-controlled, action-and-cost evaluation. Do not let IR or new models delay the December VIS transaction. Promote no thesis claim from the 3–5-person pilot.

PIVOT
