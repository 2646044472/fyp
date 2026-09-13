# Validation Audit: 2026-09-13 supplied palm practical plan

## Decision investigated

I audited the supplied four-part practical plan as stated in the newest
divergence packet `research/ops/divergence/2026-09-13-vis-roi-pilot-divergence.md`
and represented by the local implementation artifact `code/palm_demo/`: (1) make a
pilot dataset, (2) run an ROI stress test, (3) compute genuine/impostor scores
and a threshold, and (4) add quality-aware RGB/NoIR fusion. I compared each item
with the current active charter/register, the older PRF-TR divergence packet
for boundary context, and the archived edge-sensing conclusions.

The decision under test is not whether these steps are useful. They are useful
for a lawful smoke test and baseline. The decision is whether they already
constitute a defensible CS research problem for the current FYP. The current
register says the palm branch has no surviving standalone thesis: P2-CTB is
KILL, P5 is generic-uncertainty KILL, P6 is generic/missing-modality KILL, and
BIA-1 is a preflight-only KILL. `PRF-TR` is the only conditional direction, but
it is a non-personal printed-record physical-versus-digital action-risk study,
not a palm-recognition/fusion route.

## Claim under test

The strongest charitable version of the plan is:

> With a small authorised palm pilot, controlled ROI perturbations, genuine and
> impostor score distributions, and quality-aware fusion of RGB and NoIR+IR,
> a Raspberry Pi can demonstrate a robust cross-condition palm verifier.

That sentence contains four different objects, none of which is yet a research
claim:

| Plan item | What it can establish now | What it cannot establish without a new research boundary |
| --- | --- | --- |
| Pilot dataset | A local development subset or a consented Pi smoke-test corpus | A new dataset contribution, device effect, or generalisation result |
| ROI stress test | Sensitivity of a frozen matcher to crop/keypoint perturbations | That synthetic crop shifts represent physical ROI failures, or that a new ROI method is needed |
| Genuine/impostor score | A threshold, FMR/FNMR/EER record under a declared split | Security, PAD, cross-device transfer, or a new decision rule |
| Quality-aware fusion | A baseline comparison between single-modality and combined scores | A new fusion method, because quality weighting/routing and palmprint-palmvein fusion are established |

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Dataset curation, ROI extraction, quality estimation/rejection, score calibration, and multimodal fusion are all established components. Palm-ID combines ROI extraction, enhancement, compact embeddings and a DNN quality estimator; X-Palm provides a paired scanner/smartphone dataset, manual-keypoint ROI extraction and benchmark protocols; Fan et al. provide palmprint/palmvein adaptive weighted fusion; SSFD-Net handles missing modality. | The exact local combination of Fast-CC, the supplied archive, Pi 5, a fixed crop and NoIR+IR was not found as one paper. This is only a configuration gap, not evidence of a new component. | High |
| Exact-claim collision | “Quality score improves accept/reject or reject-low-quality images” collides with Palm-ID and ISO/IEC 29794-1's FNM-EDC/FM-EDC evaluation. “Quality-aware multimodal fusion” collides with the quality-aware biometric fusion literature and Fan et al.'s palmprint/palmvein two-stage adaptive weighted fusion. “ROI stress under localization offset” collides with ROI3Net's random 10% offset, rotation and scale experiments. “Genuine/impostor score and EER” is the standard verification endpoint used by ISO/IEC 19795-1 and X-Palm Sec. 3.2. | A bounded measurement could remain if it changes the observation/action/guarantee: for example, an independently labelled physical missing-modality event changes a local `fuse / reacquire / abstain` action frontier at matched joules. No such event or action is in the current plan. | High for the current claim; medium for an explicitly redesigned boundary |
| Boundary / identification | Public palm images plus crop perturbations cannot identify whether a score change comes from camera sensor, illumination, pose, ROI, normalisation, identity composition or matcher choice. X-Palm explicitly records compound variation and warns that its scale is still limited. A NoIR camera with IR fill is not a palm-vein sensor-equivalence oracle. Score-derived quality is also not independent of the matching endpoint. | A physical, identity-disjoint, repeated protocol with independent ROI landmarks, fixed thresholds, blocked sessions/devices and an independently observed action outcome could test a finite claim. That would be a new protocol boundary, not what the current plan specifies. | High |

## Assumption and identification audit

1. **Pilot dataset is not automatically a research dataset.** The local
   `PalmBigDataBase.zip` manifest records an observed archive and a derived
   20-identity × 10-image development subset, but the source agreement and
   intended-use permission remain `[GAP]`. It is not a test set, not independent
   Pi capture, and not a licence to publish or collect biometric data. X-Palm is
   more suitable for cross-domain analysis, but its academic EULA, identity
   pairing, compound factors and limited per-condition support still impose a
   finite benchmark scope.

2. **ROI stress is not a physical ROI experiment.** Shifting or resizing a
   pre-cropped ROI in the same image measures algorithmic sensitivity to a
   synthetic perturbation. It does not measure keypoint-localisation error from
   the Pi camera, operator placement, background, exposure or hand pose. If the
   ROI is fixed manually, the result is a controlled matcher perturbation. If a
   new ROI extractor is trained, it collides with existing ROI-extraction and
   ROI-robustness work. Independent landmarks or capture-time annotations are
   required to attribute a failure to ROI acquisition.

3. **Genuine/impostor scores are necessary but routine.** A sound protocol
   needs identity-disjoint enrolment/development/test partitions, mated and
   non-mated trials, a threshold frozen before test scoring, and uncertainty at
   the stated operating point. The local calibration script can produce such a
   development record, but the record is a measurement baseline. It cannot turn
   Fast-CC, a Pi board or a new crop into a contribution. It also cannot support
   a PAD, anti-spoofing or access-control claim; the current demo correctly
   labels itself local/offline and non-security.

4. **Quality-aware fusion has a circularity risk.** If quality is the matcher
   score, embedding norm, decoder confidence, or a statistic tuned to maximise
   the same genuine/impostor separation, then it is a decision feature or
   post-hoc score transform, not independent evidence. It must be calibrated on
   development data and evaluated on held-out identities/sessions. ISO/IEC
   29794-1 permits quality components and aggregation, but also defines quality
   evaluation through error-versus-discard characteristics; following that
   framework is compliance/evaluation hygiene, not novelty.

5. **The proposed modalities are not identified as palmprint + palmvein.** The
   current Pi path has an RGB camera and a NoIR camera with IR illumination.
   The local README explicitly forbids treating NoIR+IR as automatic palm-vein
   recognition, liveness, PAD or a CASIA multispectral equivalent. Camera
   index, spectral response, exposure and white balance must be recorded. A
   claimed fusion gain can otherwise be a camera/path substitution or exposure
   confound.

6. **Cross-device inference is underpowered and confounded.** The old P2 plan
   uses genuine/impostor thresholds and cross-cell acceptance, but direct-ROI
   injection bypasses the target camera, target ROI, capture quality and PAD
   path. Yan et al. already occupy the remaining template-to-image matcher
   endpoint. X-Palm's smartphone condition jointly varies hardware, pose,
   illumination, distance, background, occlusion and surface condition; a score
   difference cannot identify a named sensor or ROI cause without support for
   the nuisance cross-classification.

7. **No independent action endpoint exists in the plan.** FMR/FNMR/EER are
   recognition metrics. To become a distinct edge problem, the plan would need
   a declared local action and cost, such as `retain / reacquire / abstain`, plus
   an independent truth source and a matched-cost baseline. The plan currently
   stops at scores and fusion. That is why it maps to D0/P5/P6 controls in the
   register, not to a surviving candidate.

8. **The newest packet's candidate split does not change the result.**
   `VIS-ROI-ACT` is a conditional action audit, not a new ROI method;
   `VIS-QCAL` is a quality-to-risk negative audit until its target is frozen;
   `SMALL-N-OP` is the strongest possible negative-result direction because it
   can expose threshold instability under 3--5 identities; `SPLIT-PROV` is
   data-integrity engineering; `EDGE-RISK` is deployment characterization;
   `USER-INTERACTION` needs an explicit REC/TEC transaction and ethics gate; and
   `VIS-NIR-VOI` is not executable in a no-IR pilot. None converts the four
   supplied groundwork steps into a positive method claim.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Grosz, Godbole & Jain, *Palm-ID*, arXiv v1, 2024-01-16 | Contactless palm images; keypoint ROI, enhancement, ViT/CNN multi-scale features, DNN quality estimation, optional reject-low-quality capture | Authentication/identification, cross-database results, TAR/FAR, latency, ablations, quality error-reject curves; Sections II-A/B/C/G, III-B/D/E, IV-A/B | Full local pipeline, quality gate, ROI, fusion of complementary features, and mobile deployment | Kills “Pi pipeline + quality gate/fusion” as a mechanism. Leaves only a finite hardware/runtime replication or a different physical action endpoint. |
| Seyedmohammadi et al., *X-Palm*, arXiv v2, 2026-06-22 | Paired controlled multispectral scanner and unconstrained smartphone images; manual five-keypoint ROI to 112×112; 6,006 images, 103 participants, 81 paired participants | Cross-dataset, closed-set cross-domain and open-set cross-domain authentication; cosine scores and EER/FAR/FRR; Sections 2.1–2.4 and 3.1–3.2 | Pilot dataset idea, paired-device/domain comparison, ROI protocol and genuine/impostor verification endpoint | Kills a new “small paired pilot + cross-device score” identity. Leaves a scoped audit only if a lawful dataset and a new action/guarantee are supplied. |
| Yan et al., *Toward comprehensive and effective palmprint reconstruction attack*, Pattern Recognition 155, 110655, 2024-11 | Black-box palm-template reconstruction for deep and handcrafted palm matchers | Reconstruction quality and attack/security assessment across recognition techniques; publisher Introduction, Methodology, Experiments and Conclusions | The old P2 template-to-image-to-target-score path, especially if the plan adds a Pi target and genuine/impostor calibration | Kills the positive P2 claim; a Pi timing result or larger model matrix is not a new endpoint. A bounded transfer-barrier null remains possible only under a separately controlled protocol. |
| ISO/IEC 19795-1:2021 and ISO/IEC TS 19795-9:2019 (confirmed 2024) | Mated/non-mated comparisons, fixed operating thresholds, test planning, sample-size and mobile-device reporting | FMR/FNMR/FAR/FRR, throughput and full-system mobile biometric testing; 19795-1 Introduction, Sections 1, 6.4–6.5, 7 and 8; TS 19795-9 scope | Genuine/impostor scores, EER/threshold reporting and mobile Pi measurement | Kills metric-calculation novelty. Leaves a protocol-compliance report; TS 19795-9 explicitly excludes PAD and subsystem-only claims. |
| ISO/IEC 29794-1:2024, Edition 3, 2024-05 | Biometric quality scores/components, normalization, aggregation and discard decisions | FNM-EDC, FM-EDC, DET-versus-discard and sample acceptance/discard; Clauses 1, 3.3–3.6, 6, 9 and 11.2–11.5 | Quality score, quality-aware rejection and quality fusion evaluation | Kills a quality score/threshold as the contribution. Leaves an application-specific quality audit if its physical endpoint and calibration are independently new. |
| ROI3Net, *Multi-Scale Region of Interest Feature Fusion for Palmprint Recognition*, accepted 2025-12-30, online 2026-01-08, published 2026-03-10 | Palmprint ROIs at multiple scales; adaptive weighted feature fusion | Six public datasets; random 10% localization offset, ±30° rotation, 0.85–1.15 scale, EER/Rank-1 and efficiency; Objective, Results and Conclusions, Tables 2–7 | ROI stress test and multi-scale/quality-aware ROI fusion | Kills a generic ROI offset stress test or new ROI-fusion module. Leaves only a controlled negative comparison with a frozen matcher. |
| Fan et al., *A Novel Hybrid Fusion Combining Palmprint and Palm Vein for Large-Scale Palm-Based Recognition*, IEEE TSMC 54(7), 2024, pp. 4471–4484 | Palmprint + palmvein; two-stage coarse certainty/uncertainty decision and adaptive weighted fusion | Large-scale recognition, time efficiency, imposter/genuine/uncertainty classes and adaptive weighted fusion | Direct palmprint/palmvein quality-/confidence-aware fusion plus genuine/impostor/uncertain routing | Kills the same multimodal story. A NoIR camera must not be described as palmvein evidence merely because IR illumination is used. |
| Pan et al., *SSFD-Net*, Digital Signal Processing 159, 105003, April 2025 | Palmprint+palmvein with missing modality; shared/specific feature disentanglement and cross-modal transformation | Three multimodal biometric benchmarks, missing-rate ablations and comparisons; Abstract, Proposed method, Experiments and results, Conclusion | Missing-modality fusion and recovery | Kills P6-style fusion/reconstruction. Leaves a physical-missingness audit only if the missing state is independently labelled and the action/cost is new. |
| Soleymani et al., *Quality-Aware Multimodal Biometric Recognition*, arXiv:2112.05827, 2021-12-10 | Multiple biometric modalities/samples with estimated quality; quality-aware and aggregation fusion blocks | TAR at fixed FAR on three multimodal datasets; abstract, method and experiments | Generic quality-weighted multimodal biometric fusion | Kills a new quality-weighting architecture. It does not establish the exact Pi hardware effect, so the purchased configuration remains only a replication setting. |
| Park et al., *Resilient Sensor Fusion Under Adverse Sensor Failures via Multi-Modal Expert Fusion*, CVPR 2025, pp. 6720–6729 | Camera/LiDAR features, quality-conditioned adaptive query router and single-modality/joint experts under sensor failures | nuScenes-R sensor-drop/weather robustness and mAP/NDS; Abstract, Sec. 2.1, method and experiments | Generic quality-aware modality routing under failure | Kills an edge-only “route by quality under missing/degraded modality” claim. It leaves a palm-specific physical observation/action boundary only if that boundary is genuinely different. |

## Strongest simple baseline

The strongest baseline is not another neural fusion model. It is a frozen
single-path verifier plus transparent fixed policies:

1. fixed manual/declared ROI + Fast-CC (or one frozen authorised matcher);
2. threshold frozen from identity-disjoint development genuine/impostor pairs;
3. no quality gate;
4. quality-only discard/reacquire using contrast, blur and ROI-validity;
5. fixed equal-weight or development-frozen weighted score fusion;
6. fixed second capture / always-reacquire / always-review at the same capture
   budget;
7. RGB-only and NoIR+IR-only reported separately.

If the proposed quality-aware fusion cannot beat this matrix on held-out
identities and sessions at the same false-match operating point while charging
capture, latency, RAM and energy, it is unnecessary. If it does beat it, the
result is still a finite configuration measurement unless the plan specifies a
new independently observed action or guarantee. For ROI, the corresponding
strong baseline is a fixed crop plus a declared perturbation sweep; a learned
ROI model must beat it without using test-cell landmarks or threshold tuning.

## Contrarian result

The plan is attractive because each step produces a visible artefact: a dataset
folder, ROI images, score histograms and a fused score. That visibility is
misleading. The first three artefacts are prerequisites for any biometric
experiment, and the fourth is an occupied method family. The plan can therefore
produce a convincing demo while failing the project's research quality bar.

The strongest positive interpretation that survives is not “quality-aware
fusion improves palm recognition on Pi.” It is one of these narrower outcomes:

- `[E]` a reproducible local Fast-CC capture/match demo with latency, retry and
  deterministic-replay logs;
- `[E]` a finite, preregistered score/ROI sensitivity table on a permissioned
  dataset; or
- `[C]/[GAP]` a new action study in which a physically independent witness or
  intervention changes `fuse / reacquire / abstain` risk at matched cost.

The third item is not in the supplied plan and cannot be inferred from a high
or low EER. It would also need a new direct-neighbor search before promotion.

## Feasibility audit

| Dependency | Finding | Consequence |
| --- | --- | --- |
| Data permission | Local PalmBigDataBase/CASIA archives have observed hashes and filenames, but the original agreement and intended use are not recorded. X-Palm requires a signed academic EULA and time-limited access. | No extraction, publication, training or biometric collection can be treated as cleared. The pilot dataset is currently a data gate, not evidence. |
| Identity/sample design | A 20×10 development subset is a smoke-test subset, not independent sessions or a population sample. Genuine/impostor pair counts can be large while the number of independent identities/devices/sessions is small. | Do not report generalisation, cross-device robustness or security from frame/pair counts. Freeze identity-disjoint splits and report uncertainty. |
| Hardware/modality | Confirmed core inventory is Raspberry Pi + Camera NoIR v2. Earlier RGB/IR inventory and exact camera revision are not fully reverified in active state. Even with RGB + NoIR+IR, NIR/palmvein equivalence is not established. | Quality-aware fusion may not be executable as claimed; modality/path identity and exposure/WB must be logged first. |
| ROI labels | The current demo uses a fixed crop/debug ROI; no independent Pi capture-time landmark truth or repeated remount set is present. | ROI stress can be a synthetic perturbation only. A physical attribution claim is unidentifiable. |
| Matcher/runtime | Fast-CC is a useful MIT-licensed baseline pinned in the local README, but its public benchmark is not a Pi-camera result and the repository is an independent reimplementation. | Runtime smoke test is feasible; it does not validate recognition or security. |
| Threshold/security | Genuine/impostor calibration is feasible offline. PAD, presentation-attack resistance, target-device acquisition and protected-template claims are not supplied. | Keep the UI local/offline and non-security, as the current demo does. Never call EER/FMR a PAD result. |
| Fusion training | Learned quality-aware fusion requires paired modalities, training/development/test separation, a fixed modality-missing protocol and enough repeated identities. | Current hardware/data do not justify a learned fusion model. A fixed score average is the first control. |
| Timeline | A D0 smoke test and deterministic baseline can fit the one-year FYP; a lawful, repeated, cross-device/multimodal study with independent labels is not cleared by the present plan. | Continue only as engineering groundwork or redesign around a new observable action/truth source. |
| Ethics/privacy | Palm images/templates are biometric data even when used locally. The current README's authorisation switch is a safeguard, not ethics approval. | Obtain supervisor/institution approval before consented capture; retain the minimum local artefacts and delete them together. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| The local plan is a fixed Pi 1:1 palm demo with separate RGB and NoIR+IR profiles, provisional thresholding, and no liveness/PAD/security claim. | [K] | Local `code/palm_demo/README.md`, `BASELINES.md`, and `data/SOURCE_MANIFEST.md`, version present 2026-09-13 | README opening scope, RGB/NoIR setup, First demo, Development-data check, Baseline choices; manifest derived-subset and permission notes | Project-local engineering evidence, not external research evidence. |
| The supplied archive-derived subset is 20 identities × 10 images and is explicitly a development smoke-test subset. | [E][GAP] | Local `code/palm_demo/data/SOURCE_MANIFEST.md`, current manifest | `Derived development subset`; source-archive permission table | Hashes and filenames do not establish licence or representativeness. |
| X-Palm contains 6,006 images from 103 participants/206 hands, 81 paired participants, compound smartphone variability and manually keyed 112×112 ROIs. | [K] | Seyedmohammadi et al., *X-Palm*, arXiv v2, 2026-06-22, https://arxiv.org/html/2606.08437v2 | Abstract; Secs. 2.1–2.4; Sec. 3.2; Appendix A.5; limitations Sec. 4 | Access is restricted by academic EULA; compound factors limit named-cause attribution. |
| X-Palm's verification endpoint uses cosine similarity, a threshold and EER/FAR/FRR under cross-dataset/cross-domain protocols. | [K] | Same X-Palm v2 URL above | Secs. 3.1–3.3, especially Sec. 3.2 | This is direct evidence that score/EER reporting is a standard benchmark endpoint, not a new contribution. |
| Palm-ID already combines contactless ROI extraction, enhancement, multi-scale CNN/ViT features, mobile deployment and quality rejection. | [K] | Grosz, Godbole & Jain, *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv v1, 2024-01-16, https://arxiv.org/abs/2401.08111 | HTML Sections II-A/B/C/G; III-B/D/E; IV-A/B; Tables III–VIII | Reported 18 ms/0.33 ms numbers are on a Samsung S22/AMD EPYC setup, not Pi timing. |
| Palm-ID uses embedding L2 norm as a quality value and evaluates an error-reject trade-off against other quality measures. | [K] | Same Palm-ID URL above | HTML Sec. IV-B, lines corresponding to quality prediction and Fig. 10 discussion | The quality method is not claimed as universally optimal, but it directly occupies quality-aware rejection. |
| ROI localization stress and multi-scale ROI feature fusion are already evaluated on palmprint datasets. | [K] | *Multi-Scale Region of Interest Feature Fusion for Palmprint Recognition* (ROI3Net), online 2026-01-08, published 2026-03-10, https://jeit.ac.cn/en/article/doi/10.11999/JEIT250940 | Objective; Results and Discussions; Conclusions; Tables 2–7; random 10% offset, rotation and scale experiments | Exact architecture/dataset differs; the collision is with generic ROI stress/fusion, not every Pi setting. |
| FMR/FNMR/EER and fixed-threshold testing are standard biometric performance reporting objects. | [K] | ISO/IEC 19795-1:2021, official preview, https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A19795%3A-1%3Aed-2%3Av2%3Aen | Introduction; Sec. 1 Scope; TOC for Secs. 6.4–6.5, 7.1–7.6 and 8.3–8.4 | Public preview does not expose every page; it establishes the standard scope and required protocol concepts. |
| Mobile biometric testing guidance does not cover PAD or isolated acquisition/comparison subsystem claims. | [K] | ISO/IEC TS 19795-9:2019, confirmed current 2024, https://www.iso.org/standard/78101.html | Official abstract, scope and exclusions; 26 pages | This is a reporting boundary, not a claim that the demo is security-tested. |
| Quality score normalization, aggregation and false-match/false-non-match versus discard are established framework objects. | [K] | ISO/IEC 29794-1:2024, Edition 3, 2024-05, https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A29794%3A-1%3Aed-3%3Av1%3Aen | Clauses 1; 3.3–3.6; 3.11–3.18; 6; 9; 11.2–11.5; 26 pages | Full standard is paywalled; official preview supplies the framework and public definitions. |
| Palmprint/palmvein adaptive weighted fusion with genuine/impostor/uncertainty routing is directly published. | [K] | Fan et al., *A Novel Hybrid Fusion Combining Palmprint and Palm Vein for Large-Scale Palm-Based Recognition*, IEEE TSMC 54(7), 2024, pp. 4471–4484, https://doi.org/10.1109/TSMC.2024.3382877 | Publisher abstract and bibliographic record; method/endpoint summary | Detailed PDF sections were not available in this retrieval; abstract is sufficient for the direct task/component collision. |
| Missing-modality palmprint/palmvein fusion is directly published. | [K] | Pan et al., *SSFD-Net*, Digital Signal Processing 159, 105003, April 2025, https://doi.org/10.1016/j.dsp.2025.105003 | Publisher abstract; Proposed method; Experiments and results; Conclusion | Detailed full text is access-restricted; it directly establishes the task family and benchmark endpoint. |
| Quality-aware multimodal biometric fusion is an established method family. | [K] | Soleymani et al., *Quality-Aware Multimodal Biometric Recognition*, arXiv v1, 2021-12-10, https://arxiv.org/abs/2112.05827 | Abstract, framework description and three-dataset evaluation | Modality mix is face/iris/fingerprint rather than palm; it kills generic quality-weighting, not every palm-specific physical protocol. |
| Quality-conditioned sensor routing under sensor failures is established beyond biometrics. | [K] | Park et al., *Resilient Sensor Fusion Under Adverse Sensor Failures via Multi-Modal Expert Fusion*, CVPR 2025, pp. 6720–6729, https://openaccess.thecvf.com/content/CVPR2025/html/Park_Resilient_Sensor_Fusion_Under_Adverse_Sensor_Failures_via_Multi-Modal_Expert_CVPR_2025_paper.html | Abstract; Sec. 2.1; method and experiments; official CVF pages 6720–6729 | Camera/LiDAR and autonomous-driving setting differs, but the generic quality-aware routing component is occupied. |
| Template-to-image palm reconstruction already occupies the old P2 endpoint. | [KILL] | Yan et al., *Toward comprehensive and effective palmprint reconstruction attack*, Pattern Recognition 155, 110655, 2024-11, https://doi.org/10.1016/j.patcog.2024.110655 | Publisher Introduction, Methodology, Experiments and Conclusions as recorded in active gate; publisher abstract/record also inspected | Exact cross-device physical acquisition is not established by this source; it still kills the remaining direct matcher-input positive claim. |
| The newest divergence packet identifies the supplied work as a VIS-only palm/ROI pilot and keeps all resulting candidates conditional. | [K] | Local `research/ops/divergence/2026-09-13-vis-roi-pilot-divergence.md`, version/date 2026-09-13 | Decision investigated; Search boundary; Recent-paper limitation map; Candidate matrix; Groundwork versus research boundary; SMALL-N-OP and VIS-ROI-ACT formalizations; Decision | It is a divergence proposal, not a novelty proof; its candidate labels are independently audited here. |
| The archived common-cause/quality-aware-fusion ideas were already marked collision-prone. | [KILL] | Local `research/archive/2026-08-edge-sensing/README.md` and `log/46-edge-sensing-alternatives-audit.md`, 2026-08-27 archive | Archive README; log Section 1 and E3 validation/kill conditions | Historical evidence only; it prevents re-proposing the same family and does not promote the archive. |

### Additional primary records

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Single-source device/environment domain generalisation for palmprint recognition is already an explicit task family. | [K] | PalmRSS, Pattern Recognition 165, 111620, 2025, https://doi.org/10.1016/j.patcog.2025.111620; official repository https://github.com/yocii/PalmRSS | Publisher record/abstract and repository README/inference materials as recorded in the active/archive audit | Exact method reproduction and ARM packaging remain [GAP]; a new camera-mismatch model would still need a distinct observation/action/endpoint. |
| Fast-CC is a runnable lightweight matcher baseline, but its public benchmark is not a Pi-camera result. | [K] | Li-ChengYan, `palmprint-recognition-python`, pinned commit `d556f455a6cbdcb4264ec1cd75de2e451cf241b3`, https://github.com/Li-ChengYan/palmprint-recognition-python and MIT licence https://github.com/Li-ChengYan/palmprint-recognition-python/blob/main/LICENSE | README Baseline/Benchmark; `baseline.py` and `run.py` as recorded in the local baseline register; commit dated 2026-04-19 | Independent reimplementation; no camera/ROI/PAD or ARM benchmark is thereby established. |
| Standard RGB Camera Module 3 and NoIR are distinct optical paths; NoIR is not a palm-vein ground-truth sensor. | [K] | Raspberry Pi Camera Module 3 product page https://www.raspberrypi.com/products/camera-module-3/; product brief https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | Official specification and product brief pp. 1–3; accessed 2026-09-13 | Applies to Camera Module 3 variants; the purchased exact revision and illuminator remain [GAP]. |
| Hand geometry, flatness, brightness and sharpness quality assessment has already been evaluated against EER on palmprint data. | [K] | Zhang et al., HGAIQA, IEEE TIM 73 (2024), https://doi.org/10.1109/TIM.2024.3485454; official record https://scholarship.miami.edu/esploro/outputs/journalArticle/HGAIQA-A-Novel-Hand-Geometry-Aware-Image-Quality/991032796016102976 | Official abstract and 13-page publication record | Full publisher PDF sections were not retrieved; this is enough to establish the quality-to-EER collision, not every implementation detail. |
| Adaptive ROI extraction and open-environment palm recognition are already published. | [K] | Chai et al., *Joint Finger Valley Points-Free ROI Detection and Recurrent Layer Aggregation for Palmprint Recognition in Open Environment*, IEEE TIFS 20 (2025), pp. 421–435, https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf | Sec. I; Sec. II-A/B; Sec. III-B pp. 426–427; Sec. IV pp. 429–433; Sec. V p. 433 | No Pi or 3–5-person protocol; generic ROI stress remains a collision-prone component family. |
| Lightweight palm recognition and learned ROI extraction are already paired with a large contactless dataset. | [K] | Li et al., SYEnet, Information Sciences 669 (2024) 120518, https://doi.org/10.1016/j.ins.2024.120518 | Official abstract and Sections 1–5 outline | Full article was not available in the retrieval; no ARM result is inferred. |
| A 3–5-person pilot cannot be treated as a population/demographic performance study without an explicit factor and uncertainty design. | [K] | ISO/IEC 19795-10:2024, Edition 1, published 2024-10, https://www.iso.org/standard/81223.html | Official abstract/scope; 25-page standard record | This standard is about variation across demographic groups; it blocks overclaiming rather than supplying a novel method. |
| User-interaction influence requires explicit reference/target evaluation conditions and transaction definitions. | [K] | ISO/IEC 21472:2021, official preview, https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:21472:ed-1:v1:en | Introduction; Sec. 1; Sec. 3 terms, especially REC/TEC and interaction influence | The supplied plan does not yet define prompt, retry, transaction, or user-action endpoint. |

## Queries and failed searches

Queries run on 2026-09-13:

- `site:arxiv.org X-Palm v2 palmprint 2606.08437`
- `Yan 2024 palm template reconstruction Pattern Recognition 110655`
- `site:iso.org ISO/IEC 19795-10:2024 biometric performance testing reporting`
- `site:iso.org ISO/IEC 29794-1:2024 biometric sample quality`
- `SSFD-Net missing modality palmprint palmvein 2025 Digital Signal Processing 105003`
- `PalmRSS Pattern Recognition 2025 111620 official repository`
- `MoME multimodal sensor quality degradation CVPR 2025`
- `CAFuser condition-aware multimodal fusion 2024 official paper`
- `palmprint ROI localization robustness localization errors 2025 2026`
- `Palm-ID contactless palmprint recognition ROI localization 2024 arxiv`
- `palmprint palmvein modality information evaluation strategy quality-aware fusion`
- `quality-aware multimodal biometric fusion palmprint palmvein official paper`
- `site:openaccess.thecvf.com palmprint ROI quality assessment edge device 2024 2025 paper`
- `"palmprint" "quality assessment" genuine impostor 2024 paper`
- `site:arxiv.org palmprint recognition cross-device session quality ROI 2025`
- `palmprint Raspberry Pi visible light genuine impostor ROI`
- `"3-5 subjects" palmprint pilot false acceptance rate`
- local `rg` searches over `research/active`, `research/archive`, `research/ops`,
  `minutes` and `code/palm_demo` for `pilot`, `dataset`, `ROI`, `genuine`,
  `impostor`, `quality`, `fusion`, `stress` and `plan`.

Failed or insufficient searches:

- No primary paper was found that combines this exact Fast-CC commit, supplied
  archive subset, Pi camera, fixed crop and NoIR+IR score fusion as one artifact.
  This is a configuration search gap, not evidence of novelty.
- No source or local agreement was found that clears the supplied
  `PalmBigDataBase.zip` or CASIA archive for extraction, publication, or new
  biometric collection. Filenames and hashes are not permissions.
- No source was found that makes a standard Pi NoIR+IR capture equivalent to a
  palmvein or CASIA multispectral acquisition path. This remains a hardware and
  observation-model gap.
- No independent Pi ROI landmark set, repeated remount session, or physical
  capture outcome log exists in the workspace as of 2026-09-13. A synthetic ROI
  perturbation therefore cannot validate a physical ROI claim.
- No exact paper was found for a new local `fuse / reacquire / abstain` action
  on this hardware. That residual is only `[GAP]`; it is not a promotion basis,
  because the current plan does not define the action, independent truth, or
  matched-cost endpoint.

## Decision

The pilot dataset, ROI stress test and genuine/impostor score are **baseline
groundwork**. Quality-aware fusion is an established method family and is
further invalid as a palmprint–palmvein claim on the currently confirmed
RGB/NoIR+IR hardware. The current architecture therefore cannot be validated
as a research contribution by reporting better EER, a lower retry rate, or a
Pi runtime number.

Keep the plan only as a permissioned D0 engineering gate and transparent
negative-control package. To reopen a research claim, add all of the following
before implementation expands: a distinct local action, an independently
observed outcome, paired/blocked repeated episodes, frozen threshold and
quality rules, and a direct-neighbor audit for the exact observation/action/
endpoint. If that new boundary is the non-personal printed-record physical
versus digital action study, it belongs to `PRF-TR` and must use its exact
payload oracle and matched-cost controls, not palm scores.

KILL
