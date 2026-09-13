# Divergence Packet: 2026-09-13 — VIS-only palm pipeline and ROI-stress pilot

## Decision investigated

對照使用者提供的實踐計劃：今天先完成無 IR 的 VIS pipeline，做 ROI stress test，
以 3--5 人 pilot 建立 genuine/impostor baseline，記錄 quality metrics，並用固定
naming convention 保存資料。問題是：這組工作能支持哪些 sharply different 的 edge
research directions，哪些缺口仍未被計劃覆蓋？

目前判斷不是替任何 active candidate 辯護。這份計劃足以建立一個可審計的
biometric capture/evaluation substrate，但尚未定義一個可稱為新方法的 observation、
action、guarantee 或 evaluation endpoint。最有科學價值的路線是有限的負結果或
識別邊界；正向方向全部保持 conditional。

## Search boundary

- 搜尋日期：2026-09-13；範圍是 contactless palmprint、VIS/ROI、quality assessment、
  genuine/impostor verification、mobile/edge measurement、user-interaction evaluation
  與小樣本 biometric protocol。
- 主要 queries：
  - `site:openaccess.thecvf.com palmprint ROI quality assessment edge device 2024 2025 paper`
  - `"palmprint" "quality assessment" genuine impostor 2024 paper`
  - `site:arxiv.org palmprint recognition cross-device session quality ROI 2025`
  - `palmprint Raspberry Pi visible light genuine impostor ROI`
  - `"3-5 subjects" palmprint pilot false acceptance rate`
- 先查正式論文、作者/會議版本和 ISO 官方頁面；survey 只用來畫 field map，不能作
  load-bearing novelty proof。已讀 active 的 README、project charter、candidate register，
  並因與 palm/ROI/VIS-NIR 重疊而讀 archive README、VIS-NIR boundary、ROI reading、
  Palm-ID protocol 與 evaluation logs。
- No global novelty claim。下面的 [GAP] 僅表示在上述 query、日期、來源鏈中尚未看到
  該精確組合；不表示全域不存在。

## Recent-paper limitation map

| Primary work | What was read | What it already covers | Gap left by the user plan |
| --- | --- | --- | --- |
| Grosz, Godbole & Jain, *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv entry dated 2024-01-16, [arXiv:2401.08111](https://arxiv.org/abs/2401.08111) | HTML Sections II-A, II-G, III-C/III-D/III-E, IV-A/IV-B; the entry reports mobile end-to-end capture/ROI/matching and a quality-reject arm. | Mobile on-device palmprint recognition, ROI extraction, quality estimation, open/closed evaluation, fixed-FAR verification, latency/template-size reporting. | No Raspberry Pi result, no 3--5-person adequacy result, and its quality score is not independent truth or PAD. VIS-only local capture is therefore a baseline, not a new method. |
| Zhang et al., *HGAIQA*, IEEE TIM 73 (2024), pp. 1--13, DOI [10.1109/TIM.2024.3485454](https://doi.org/10.1109/TIM.2024.3485454) | Official University of Miami record: abstract, 13-page bibliographic record and contribution description. Full publisher PDF sections were not retrieved in this pass. | Whole-image hand geometry, flatness, brightness and sharpness quality assessment; the reported experiment removes the lowest 10% and measures EER change. This is also the closest public Bob Zhang paper. | Its quality-to-EER result does not define a VIS-only Pi operating point, user action, independent quality truth, or threshold uncertainty for a 3--5-person pilot. Advisor fit is context only. |
| Chai et al., *Joint Finger Valley Points-Free ROI Detection and Recurrent Layer Aggregation for Palmprint Recognition in Open Environment*, IEEE TIFS 20 (2025), pp. 421--435, [PDF](https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf) | Sec. I, Sec. II-A/B, Sec. III-B pp. 426--427, Sec. IV pp. 429--433, Sec. V p. 433; PDF pages are marked P0--P12 in the retrieved copy. | FVP-free adaptive ROI, hand segmentation, open-set/closed-set recognition and cross-dataset evaluation. The paper explicitly treats ROI extraction as a recognition-critical component and calls lighter optimization future work. | No ARM/Pi capture-to-decision measurement, no user retry policy, no small-pilot operating-point analysis, and no claim that ROI quality predicts impostor risk. “ROI stress test” alone collides with this method family. |
| Li et al., *SYEnet: Simple yet effective network for palmprint recognition*, Information Sciences 669 (2024) 120518, DOI [10.1016/j.ins.2024.120518](https://doi.org/10.1016/j.ins.2024.120518) | Official ScienceDirect abstract and Introduction/Section 1--5 outline. Full article text was not available in the retrieved view. | Lightweight palm recognition, a dedicated PREnet ROI extractor, a 12,800-image/400-palm contactless dataset, and evaluation across multiple databases/noisy conditions. | “Lightweight” and “edge” are already a model/system family. The user plan has no fixed model artifact, Pi runtime, thermal/energy endpoint or blocked cross-session evaluation. |
| Jin et al., *Unified Adversarial Augmentation for Improving Palmprint Recognition*, ICCV 2025, official [PDF](https://openaccess.thecvf.com/content/ICCV2025/papers/Jin_Unified_Adversarial_Augmentation_for_Improving_Palmprint_Recognition_ICCV_2025_paper.pdf) | Sec. 4.2 evaluation-metrics extract: genuine/impostor scores, FAR-fixed threshold, TAR@FAR; open-set identity split description. | Correct verification vocabulary and the reason identity-disjoint/open-set splits matter. A random frame split is not an adequate genuine/impostor baseline for a new person. | It does not answer whether 3--5 identities can estimate a stable threshold, nor whether a naming convention actually prevents leakage. Those are protocol/negative-result questions, not a new recognition model. |
| Zou et al., *Unsupervised Palmprint Image Quality Assessment via Pseudo-Label Generation and Ranking Guidance*, IEEE TIM 72 (2023), pp. 1--11, DOI [10.1109/TIM.2023.3288259](https://doi.org/10.1109/TIM.2023.3288259); summarized with section context in Gao et al., [arXiv:2501.01166v2](https://arxiv.org/pdf/2501.01166) | Survey v2 dated 2025-10-21, Sec. III-B pp. 4--5 / lines 371--402; the primary DOI metadata was checked. | Label-free/pseudo-label quality assessment is already a named problem; quality is not an empty field waiting for a blur/luminance score. | The plan does not predeclare which quality target is being measured: acquisition success, genuine FNMR, impostor FMR, ROI validity, or user burden. Without that target, “quality metrics” are logging only. |
| ISO/IEC 19795-10:2024, Edition 1 (2024-10), [official record](https://www.iso.org/standard/81223.html) | Official abstract/scope, 25-page standard record: performance variation includes failure-to-enrol/acquire, score shifts, recognition errors, processing time, uncertainty and operational thresholds. | Requires explicit factor controls, uncertainty, threshold reporting and performance-variation framing. | The 3--5-person plan cannot support demographic or population claims; no cohort/factor scope, confidence target or operating threshold is yet frozen. This standard blocks overclaiming rather than opening a novel method. |
| ISO/IEC 21472:2021, [official preview](https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:21472:ed-1:v1:en) | Introduction, Scope Sec. 1, Terms Sec. 3, especially REC/TEC and user-interaction-influence definitions. | A formal scenario methodology for capture-device condition, user factors and interaction factors, including reference/target evaluation conditions. | The plan says “3--5 people” but specifies no REC/TEC, prompt/UI, transaction, retry action, time origin or subjective endpoint. Therefore a human-interaction direction is only a gap, not yet supported. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| `VIS-ROI-ACT` | A local verifier must decide `accept / one recapture / abstain`; a bad accept corrupts an identity decision and a bad reject costs another interaction. | On the named VIS path, pre-match ROI validity/coverage/geometry plus the frozen match score changes the FNMR/FMR-versus-retry frontier on held-out pose/blur/illumination cells relative to score-only, blur-only, fixed-recapture and always-review. [C] | HGAIQA; RDRLA; Palm-ID; Kim et al., mobile guide-window and retry protocol, DOI [10.1109/TCE.2015.7298090](https://doi.org/10.1109/TCE.2015.7298090), pp. 311--319. | A score-only or fixed-recapture policy is non-dominated; ROI quality is just a re-expression of the score; or the stress labels were inferred from the same image/policy. | `3--5` people can supply a pilot only. Requires consent, repeated sessions, identity/session blocking and one predeclared recapture action. **HOLD, bounded audit only.** |
| `VIS-QCAL` | The operator wants to know whether a “good-looking” frame is safe to match or should be retried. | Sharpness, brightness, ROI coverage, hand flatness and decoder confidence are evaluated as fixed, identity-independent predictors of acquisition failure and genuine/impostor score error across blocked sessions. No new quality metric is claimed. | HGAIQA; Palm-ID IV-B; PGRG; older EAV quality work. | Quality predicts only blur/ROI failure but not impostor FMR; thresholds selected on the test set; or one scalar/decoder confidence dominates every metric. **PIVOT to a negative audit.** | Low hardware burden, but 3--5 people make calibration unstable. Primary endpoint must be fixed before collecting labels. |
| `SMALL-N-OP` | A student or deployer asks whether a 3--5-person pilot can freeze a genuine/impostor threshold and report a credible operating point. | Under identity/session-blocked hierarchical resampling, quantify threshold instability, confidence-interval width and decision reversals; test whether the proposed pilot can support any stated FAR/FNMR claim. A useful result may be that it cannot. | ISO/IEC 19795-10:2024; UAA Sec. 4.2; Palm-ID fixed-FAR reporting. | If threshold and uncertainty remain stable under leave-one-identity-out and session-blocked resampling, the local negative claim weakens. If only frame-level bootstrap is stable, kill the conclusion as pseudoreplication. | **Highest negative-result value.** Can run with 3--5 participants plus simulation/external public data; it is a protocol/evaluation contribution, not a biometric algorithm. |
| `SPLIT-PROV` | A dataset curator needs to distinguish a real person/session result from filename or capture-order leakage; leakage can inflate genuine/impostor performance and invalidate the demo. | A manifest/naming-convention checker using identity, hand, session, device, condition, ROI status and content hash blocks illegal train/dev/test assignments and reports the metric delta between random-frame and blocked splits. | UAA open-set split; RDRLA open-set/cross-dataset protocol; Palm-ID time-separated protocol. | No illegal assignment exists, or the checker only restates a hand-written folder layout and has no measurable leak-detection/metric-delta endpoint. **KILL as thesis; retain as engineering groundwork.** | Easy and immediately useful. Naming convention is metadata hygiene unless `accept/quarantine` semantics and a falsifiable leakage endpoint are defined. |
| `EDGE-RISK` | A local device must finish capture-to-decision within a bounded wait and memory/energy budget; quality rejection may reduce errors while increasing retries. | The same frozen VIS pipeline has a different Pareto frontier when ROI/quality gating is enabled, measured jointly by FMR/FNMR, failure-to-acquire, attempts, p50/p95 interaction time, peak RSS, temperature and input energy. | Palm-ID on mobile; SYEnet lightweight recognition; older embedded palm/vein prototypes; MLPerf-style stage accounting is a measurement precedent, not a contribution. | No non-dominated frontier appears over matcher-only, fixed retry and always-process controls; energy is inferred from CPU utilization; or the Pi model/OS/runtime is not fixed. **PIVOT to a deployment characterization.** | Medium. Requires Pi instrumentation and a frozen artifact. Without a decision frontier, it is only performance engineering. |
| `USER-INTERACTION` | A participant may misplace/rotate the hand; repeated prompts and quality rejects create delay or unequal burden even when matching is accurate. | Under explicit REC/TEC conditions, a defined prompt/retry policy changes failure-to-acquire, attempts, p95 transaction time and FNMR relative to no guidance/fixed guide-window control. | ISO/IEC 21472:2021; Kim et al. 2015, pp. 311--319; Giełczyk et al., JIFS 39 (2020), DOI [10.3233/JIFS-189142](https://doi.org/10.3233/JIFS-189142). | No UI/action is frozen; participants do not repeat the same transaction; or the result is reported as population usability from 3--5 people. **HOLD pending ethics and protocol.** | Pilot-feasible as a usability-influence study, not as a general demographic/fairness claim. Current plan leaves observation, action and endpoint undefined. |
| `VIS-NIR-VOI` | After a VIS frame is ambiguous, the node may later decide whether an IR/NIR observation is worth its latency, energy and privacy cost. | A named physical stress cell yields a lower error/cost frontier with one IR/NIR intervention than VIS-only, fixed recapture or conservative abstention. | Palm-ID notes visible-only versus IR cost; Fei et al., VIS-NIR heterogeneous palmprint recognition, DOI [10.1109/TIFS.2024.3441945](https://doi.org/10.1109/TIFS.2024.3441945); active acquisition literature. | Fixed VIS recapture or always-two-shot dominates; no independent physical condition label; IR path is not synchronized/logged; or the result is ordinary cross-spectral matching. **PIVOT, future gate only.** | **Not supported today.** The no-IR plan can establish a VIS baseline, but it supplies no IR observation, intervention, power budget or matched-cost endpoint. |

## Groundwork versus research boundary

| Plan item | What it proves now | What is still missing for research |
| --- | --- | --- |
| No-IR VIS pipeline | A reproducible capture path and a baseline modality. | Fixed camera/OS/runtime/model hash, capture-to-decision boundary, thermal state, failure policy and a held-out factor. VIS-only is not a contribution by itself. |
| ROI stress test | It can expose ROI failure modes and create nuisance cells. | Independent physical labels, allowed pre-action observations, an allowed action, and an endpoint beyond ROI accuracy. Automatic/adaptive ROI is already occupied. |
| 3--5-person pilot | Bring-up, protocol debugging, repeated-session smoke test. | Population target, identity/session split, uncertainty target, power justification and a claim limited to pilot scope. It cannot establish a production FAR or fairness result. |
| Genuine/impostor baseline | Basic verification score distributions and threshold plumbing. | Identity-disjoint enrollment/probe design, fixed operating point, pair-count accounting, confidence intervals and a non-random split. “Accuracy” is not enough. |
| Quality metrics | Candidate covariates such as sharpness, luminance, ROI coverage and hand geometry. | A quality target and action semantics: does the score predict acquisition, genuine FNMR, impostor FMR, retry burden, or only visual appearance? Quality is not independent truth. |
| Naming convention | Traceability and a possible split/provenance linter. | A machine-checkable schema, illegal-assignment rules, quarantine action and metric-delta endpoint. Naming alone is engineering hygiene. |
| No IR today | A clean VIS control for any later modality comparison. | IR/NIR hardware state, wavelength/illumination log, matched joules/latency, independent stress labels and a value-of-information action. |

## Top two formalizations

### `SMALL-N-OP`: small-pilot operating-point boundary

- **[D] Decision:** Given a VIS enrollment/probe score and metadata `(identity, hand,
  session, ROI status, quality features)`, freeze `accept / reject / collect-more` at a
  declared operating point. The practical question is whether 3--5 people can justify the
  threshold, not whether a classifier can fit them.
- **[A] Assumptions:** Identity is the independence unit; repeated frames from one person and
  session are clustered, not independent Bernoulli trials. Threshold fitting uses development
  identities/sessions only. Any external public set is a calibration/reference arm, not silent
  evidence for the local Pi.
- **[T] Target:** Report threshold movement, leave-one-identity-out decision flips, interval
  width/coverage and the gap between frame-bootstrap and identity/session-bootstrap estimates.
  The positive claim would be a stable, auditable pilot operating point; the more likely useful
  result is that the plan cannot support a stated population FAR/FNMR claim.
- **Observable outcome:** genuine/impostor score distributions; FMR/FNMR or TAR@fixed FAR;
  failure-to-acquire; number of independent identities/sessions; threshold CI; p50/p95
  capture-to-decision time; and whether quality gating changes the operating point.
- **Counterexample:** Five people produce many repeated frames, including zero observed false
  accepts. A frame-level interval looks narrow, while a leave-one-person-out threshold moves
  enough to reverse accept/reject decisions. Repeated captures do not create five independent
  population samples.
- **Negative-result value:** A preregistered demonstration of what the small pilot can and
  cannot identify would prevent overclaiming and give later VIS/IR/ROI studies a defensible
  minimum evidence gate. It is a protocol boundary, not a new biometric model.

### `VIS-ROI-ACT`: ROI-stress-to-action frontier

- **[D] Decision:** For one VIS frame, a local verifier chooses `accept`, `one recapture`, or
  `abstain/review`. `Accept` is allowed only for a claimed identity comparison; a false accept
  is the primary harm, while recapture/review costs time and user effort.
- **[A] Assumptions:** Physical stress labels (pose, distance, occlusion/blur or lighting)
  are assigned by the fixture/protocol before policy scoring; the policy sees only the frame,
  ROI features, quality metrics, matcher score and runtime telemetry. The decoder/model,
  threshold, one-recapture budget and held-out session are frozen before target scoring.
- **[T] Target:** On held-out stress cells, test whether a fixed ROI-aware rule changes the
  non-dominated frontier of `(FMR, FNMR, failure-to-acquire, recaptures, p95 time, energy)`
  relative to score-only, blur-only, fixed-recapture, no-gate and always-review controls.
  This is a finite evaluation claim; it is not a new ROI detector or guarantee.
- **Observable outcome:** exact identity decision, ROI success/failure, quality values,
  matcher score, action, retries, stage timestamps, peak RSS, temperature and input energy
  where measured. Aggregate over identity/session, not frames.
- **Counterexample:** ROI coverage, sharpness and matcher confidence are nearly the same
  statistic, so the score-only rule is equally informed and dominates. Alternatively, two
  physical states have overlapping permitted observations but opposite best actions; a larger
  selector cannot identify the correct action without another observation or conservative
  abstention.
- **Negative-result value:** A fixed recapture or score-only rule being Pareto-optimal is a
  useful finite result. A stable held-out inversion would justify only a bounded ROI/action
  audit for the named VIS setup, not a general quality gate or cross-device guarantee.

## Evidence ledger

| Claim | Label | Primary source and version/date | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Contactless palmprint recognition has a complete mobile pipeline including capture, ROI, feature extraction, matching and quality rejection; the system reports fixed-FAR verification and resource quantities. | [K] | Grosz, Godbole & Jain, *Mobile Contactless Palmprint Recognition*, arXiv entry 2024-01-16, [https://arxiv.org/abs/2401.08111](https://arxiv.org/abs/2401.08111) | HTML Secs. II-A, II-G, III-C--III-E, IV-A--IV-B; retrieved lines describe ROI, mobile app, efficiency and quality prediction. | Samsung Galaxy S22/Qualcomm, not Pi. The exact arXiv version number was not exposed in the retrieved HTML; do not treat its numbers as local targets. |
| Whole-image hand geometry, flatness, brightness and sharpness can be fused for palmprint quality assessment; removing low-quality images is evaluated through EER. | [K] | Zhang et al., HGAIQA, IEEE TIM 73 (2024), [DOI](https://doi.org/10.1109/TIM.2024.3485454), official record [https://scholarship.miami.edu/esploro/outputs/journalArticle/HGAIQA-A-Novel-Hand-Geometry-Aware-Image-Quality/991032796016102976](https://scholarship.miami.edu/esploro/outputs/journalArticle/HGAIQA-A-Novel-Hand-Geometry-Aware-Image-Quality/991032796016102976) | Official abstract and publication record, pp. 1--13 metadata. | Full paper sections/limitations were not retrievable here; load-bearing claims are limited to the abstract. Bob Zhang adjacency is not novelty evidence. |
| FVP-free adaptive ROI and open-set/closed-set recognition are already a 2025 TIFS method family. | [K] | Chai et al., IEEE TIFS 20 (2025), [PDF](https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf), DOI `10.1109/TIFS.2024.3516539` | Sec. I pp. 421--423; Sec. II-A/B pp. 423--425; Sec. III-B pp. 426--427; Sec. IV pp. 429--433; conclusion/future work p. 433. | GPU/public-dataset recognition study; no Raspberry Pi capture-to-decision or 3--5-person protocol. A future-work sentence is not proof of an open problem. |
| Lightweight palmprint recognition and learned ROI extraction are established, including a 400-palm contactless dataset. | [K] | Li et al., SYEnet, Information Sciences 669 (2024) 120518, [DOI](https://doi.org/10.1016/j.ins.2024.120518) | Official abstract and Sections 1--5 outline on ScienceDirect. | Full article text was not available in this pass; no ARM/Pi result was inferred. |
| Verification evaluation should compare genuine and impostor pairs at a fixed FAR, and open-set splits should avoid identity overlap. | [K] | Jin et al., UAA, ICCV 2025, official [PDF](https://openaccess.thecvf.com/content/ICCV2025/papers/Jin_Unified_Adversarial_Augmentation_for_Improving_Palmprint_Recognition_ICCV_2025_paper.pdf) | Sec. 4.2, evaluation-metrics extract; open-set protocol paragraph in the same section. | The official PDF endpoint returned an access error in the browser pass, so this entry relies on the indexed PDF extract; exact printed page number remains [GAP]. |
| Label-free/pseudo-label palmprint image-quality assessment already exists as a named problem. | [K] | Zou et al., IEEE TIM 72 (2023), DOI [10.1109/TIM.2023.3288259](https://doi.org/10.1109/TIM.2023.3288259); cross-checked in Gao et al., arXiv v2 2025-10-21, [PDF](https://arxiv.org/pdf/2501.01166) | Gao et al. Sec. III-B, PDF p. 4, lines 371--402; citation details p. 14. | Survey is not used as proof of performance; it establishes that “quality metric” is already a research family. |
| Biometric performance reporting includes failure-to-enrol/acquire, score shifts, recognition errors, processing time, uncertainty and operating thresholds. | [K] | ISO/IEC 19795-10:2024, Edition 1, published 2024-10, [official record](https://www.iso.org/standard/81223.html) | Official abstract/scope preview, 25-page record. | This part addresses variation across demographic groups; a 3--5-person non-demographic pilot cannot be presented as a fairness or population study. |
| User interaction influence should be tested with reference and target evaluation conditions, separate from generic usability testing. | [K] | ISO/IEC 21472:2021, [official preview](https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:21472:ed-1:v1:en) | Introduction; Sec. 1 Scope; Sec. 3 terms, especially REC/TEC, lines 65--145 in the retrieved preview. | The plan has no defined UI/action/transaction, so this is a required protocol input rather than evidence that a human-factor method is novel. |
| Mobile palmprint guidance, ROI/retry handling and practical verification under constrained processing are established. | [K] | Kim et al., *An empirical study of palmprint recognition for mobile phones*, IEEE TCE 61(3) (2015), pp. 311--319, [DOI](https://doi.org/10.1109/TCE.2015.7298090) | Sec. III/E and experimental discussion, pp. 316--319, as available from the author/institution record. | Older method, but it is enough to kill “first guide-window/retry idea”; it does not provide Pi measurements or current quality metrics. |
| VIS-only is a baseline for later VIS/NIR comparison, not evidence that IR has no value. | [K] / [GAP] | Fei et al., *Learning Frequency-Aware Common Feature for VIS-NIR Heterogeneous Palmprint Recognition*, IEEE TIFS 2024, DOI [10.1109/TIFS.2024.3441945](https://doi.org/10.1109/TIFS.2024.3441945) | Archive reading log read on 2026-09-13; source abstract/metadata and boundary notes. | Full paper/code/weights were not available in the archive pass. The later IR value-of-information direction requires a new physical intervention and matched-cost endpoint. |

## Queries and failed searches

Successful query families found the papers and standards listed above. The following did not produce a primary source establishing the exact user plan as an already-defined research endpoint:

- `"3-5 subjects" palmprint pilot false acceptance rate`: no exact palmprint primary study found; retrieved work uses substantially larger datasets or does not report identity-level uncertainty. This is not evidence that no such study exists.
- `"VIS-only ROI stress test palmprint"`: no exact paper found in the inspected results; nearby work is adaptive/open-environment ROI or quality assessment, so the residual is only a scoped protocol gap.
- `"naming convention" palmprint benchmark genuine impostor`: no primary paper found where filename convention itself is the contribution. The observed role is reproducibility/data hygiene; a research claim needs a leakage-detection or metric-delta endpoint.
- `palmprint Raspberry Pi visible light genuine impostor ROI 2024 2025`: retrieved older embedded/palm-vein prototypes and mobile/desktop palmprint papers, but no verified modern Pi VIS-only paper with a complete identity/session split, fixed threshold, ROI-failure log and stage-level resource report.

Uncertainties remaining after the search: exact camera model and VIS spectral path; whether the proposed pipeline is palmprint recognition or merely a generic ROI demo; the frozen matcher and threshold rule; whether the 3--5 people are participants, identities, or repeated sessions; whether “impostor” means non-mated pairs or presentation attacks; exact quality formulas; the UI/retry action; and whether a future IR path is permitted by ethics and budget.

## Decision

The plan supports a **VIS baseline + protocol audit**, not a positive biometric method claim. The sharply different directions are `VIS-ROI-ACT` (conditional sensing/action), `VIS-QCAL` (quality-to-risk audit), `SMALL-N-OP` (small-sample identification boundary), `SPLIT-PROV` (data-integrity groundwork), `EDGE-RISK` (systems resource frontier), `USER-INTERACTION` (REC/TEC human-factor study), and `VIS-NIR-VOI` (future modality intervention). Only `SMALL-N-OP` has a strong useful negative-result path before purchasing more hardware; `VIS-ROI-ACT` is the strongest conditional experiment but is heavily occupied at the mechanism level.

Do not call the following research contributions without extra definitions and evidence: no-IR VIS bring-up, ROI crops, quality logging, genuine/impostor pair generation, naming convention, Pi latency, or a 3--5-person accuracy number. Before any promotion, freeze identity/session splits, matcher/threshold, quality target, allowed action, independent truth, uncertainty rule, and the endpoint that can falsify the claim.

PIVOT
