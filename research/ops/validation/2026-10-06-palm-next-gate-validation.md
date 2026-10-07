# Validation Audit: 2026-10-06 Pi Palm Next Gate

## Decision investigated

Whether the immediate next step should be (1) low-level/blurred palm preprocessing and ROI tuning, (2) a new matcher or threshold, or (3) the active `E-BOUND-X` cross-session enrollment/action study. The decision is for the present Pi NoIR capture path, not a general Palm novelty claim.

## Claim under test

[C] A camera, preprocessing, ROI, or matcher change could separate the two hands in the 2026-10-06 collection and justify a recognition-method direction. [C] Three-visit enrollment diversity could then improve later mock-transaction completion beyond equal-effort controls.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component | Hong et al. 2014 already extract blur-stable structure/orientation features; Palm-ID 2024 combines mobile ROI, enhancement, quality rejection/recapture, open-set matching and on-device inference. | A physical Pi failure diagnosis with paired full still, preview, ROI and terminal action lineage is apparatus-specific. | High for generic-method collision; medium for exact local endpoint. |
| Exact claim | Palm-ID evaluates time-separated mobile data and quality/enhancement ablations; W2ML 2021 evaluates open-set touchless matching and cross-database shift. Existing 2017/2019 palm template work in the active gate occupies representative/multi-template selection. | `E-BOUND-X` retains only an equal-template-count, three-visit, untouched visit-3 *action* comparison on this apparatus, if feasible. | High for broad claims; medium for bounded action endpoint. |
| Boundary | A 20-image, same-person, continuous left/right burst cannot isolate optical blur from illumination or ROI drift, estimate population FAR, or support an impostor threshold. A threshold cannot repair a wrong rank; selecting preprocessing on these probes leaks the evaluation. | A manual-ROI intervention and controlled capture factors can identify which stage accounts for this *local* failure. A later person/visit-blocked study can test the residual enrollment question. | High. |

## Assumption and identification audit

- [E] The latest 20 stills are 10 left + 10 right, one person, continuous within each batch. Full-still redetection made 20/20 ROIs; old preview-based saved path made 16/20. The two ROI-center estimates differ by median roughly 51.5 full pixels on left and 86.2 on right, with a 638-pixel outlier on right. Thus a localization defect is observed, but this does not establish that localization explains all score overlap. Source: `minutes/10-06-white-labelled-continuous-capture-diagnostic.md`, Findings.
- [E] DoN on full-still ROIs ranked the correct hand in 7/10 held-within-burst probes; genuine/wrong-hand medians 0.1243/0.1251 and all 20 of these comparison distances fell below the deployed 0.15 floor. These are two palms from one person, **not** independent unknown-person impostors or a population false-match rate. The prior 38-still burst gave 11/28 correct ranks; exploratory central cropping improved it to 19/28 there but fell to 5/10 in the new burst. This is direct local evidence against adopting a selected crop factor. Source: same minutes and `minutes/10-06-highres-own-capture-diagnostic.md`.
- [E] The local debug enrollment sets `clip(95th percentile of same-template distances + 0.015, 0.15, 0.20)`, with no nonmate distribution; `debug_ui.py` lines 41–42, 982. A genuine-only rule cannot calibrate open-set false accepts. The `0.15` floor specifically admits both hand comparisons in this local set. Simply lowering it would trade accepts for rejects and cannot fix 3/10 wrong ranks.
- [GAP] No manual anatomical ROI labels, objective focus chart, controlled illumination intervention, image/ROI same-instant linkage for the earlier path, independent identities, or later-session probes are available in these two bursts. The `white` background label conflicts with visible dark/green background, so there is no white-paper contrast here.
- [K] The user removed the stable-wait and hand-removal constraints for `/collect`; this is appropriate for diagnosing a continuous-use presentation but means frame counts are correlated. A later generalization gate can use separate visits without imposing a wait on the product UI.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Hong et al., *PLOS ONE* 9(7), e101866, 2014-07-03, DOI https://doi.org/10.1371/journal.pone.0101866 | Controlled PolyU ROIs; synthetic Gaussian defocus; VO structure plus weighted orientation features. | Blurred-palm EER, clean/blurred comparison, runtime. | Direct on “recognize blurred palm texture”; limited on physical NoIR blur. | Kills generic blur-stable palm feature/preprocessing novelty. Its Gaussian degradation and controlled ROI do **not** validate a Pi photo with unknown focus/illumination/registration causes. |
| Grosz, Godbole & Jain, Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Mobile capture, nine keypoints, 224×224 ROI, enhancement, quality score/rejection, CNN/ViT features, open-set search. | Cross-database and time-separated matching, on-device pipeline, quality/feature ablations. | Very direct on mobile ROI, enhancement, rejection and model-swap family. | Kills “add quality gate,” “enhance faint lines,” or “deploy deep matcher on edge” alone. Leaves exact local Pi capture/action failure attribution. |
| Shao & Zhong, *Pattern Recognition* 121, 108247 (2022 issue; online 2021-08-12), DOI https://doi.org/10.1016/j.patcog.2021.108247, author text https://pmc.ncbi.nlm.nih.gov/articles/PMC8359644/ | Identity-disjoint touchless palm metric learning across constrained/unconstrained databases. | Open-set identification and verification, cross-database scores. | Direct on learning a more discriminative open-set matcher and testing domain shift. | Kills a plain matcher swap as a research claim; its cross-database degradation underscores that public-dataset numbers cannot be transferred to the Pi. |
| Palm-specific template selection/update, Chen et al. 2017, DOI https://doi.org/10.1007/978-3-319-69923-3_27; 2019 follow-up described in active gate | Representative/multiple palm templates under posture and temporal variation. | Authentication/template coverage over sessions. | Direct on enrollment diversity. | Kills generic “select more varied templates” novelty. Full primary text was not obtained in this audit, so no narrow exact-claim conclusion rests on its inaccessible details. |

## Strongest simple baseline

For diagnosis, annotate a small set of palm-core quadrilaterals *without viewing match outcomes*. On identical full stills compare (A) current detector ROI, (B) manual ROI and (C) one fixed anatomical ROI recipe, all passed to the **same frozen DoN**. Report detection failure, overlap/center variation, per-probe correct-hand rank, genuine/opposite-hand score and margin, and reject/accept at a development-only threshold. Add two capture conditions that change **one physical factor at a time**: fixed mount/focus/illumination, then changed lighting or focus with identical placement guidance. A simple fixed-camera/fixed-ROI repair is the adversarial baseline for a new method.

Use a *separate* later session to compare candidate ROI/matcher settings. Keep the later session untouched during selection. An unrelated person set is needed before any open-set threshold or wrong-person claim. Compare current DoN, the existing FastCC baseline, and at most one published matcher with frozen, compatible preprocessing; treat the last as feasibility engineering unless a distinct endpoint survives. Do not tune the 0.15 threshold or choose the center crop on the same 20 shots.

## Contrarian result

`Blurred-palm algorithm` as a broad thesis: **KILL**. The local pictures have faint lines but no measured defocus cause; prior primary work already targets blur-stable structure and mobile enhancement/quality. `New threshold/model` as thesis: **KILL** at this stage. A bad rank is not repaired by an acceptance cutoff, and the two-palm burst cannot set an open-set operating point. `E-BOUND-X`: **HOLD**, but the current input path must pass a much cheaper correctness gate first. If manual ROIs and controlled lighting still leave near-tied DoN scores, it is a matcher/domain problem; benchmark a stronger established matcher before committing to longitudinal enrollment. If manual ROIs separate but automatic do not, fix registration/ROI. If same ROIs separate only under controlled lighting/focus, fix acquisition. These are falsifiable alternatives, not mutually exclusive conclusions from existing photos.

## Feasibility audit

- The first gate uses existing 20 full stills for blinded manual ROI labels and current code; it requires no new camera, real payment, or extra algorithm training. Because manual ROIs may be chosen after seeing images, their comparison is diagnostic and needs a later untouched batch for confirmation.
- Controlled focus/lighting comparison needs a fixed mount, exposure/gain logs and the same hand distance. “White paper” needs an actual white-background arm; a metadata label is insufficient. The user can capture continuously through the current UI; analytical units are sessions/presentations, not frames.
- `E-BOUND-X` readiness requires atomic image/frame/session/template lineage, frozen VIS matcher/gallery/threshold, independent identity and mock-action labels, approvals/consent and three visits. `research/active/47-e-bound-x-sample-size-and-estimand-gate.md` calculates that roughly 50–70 complete independent people only targets a very large 20-point paired difference under illustrative discordance. Twenty photos from one person add no person-level power.
- The method distinction for `E-BOUND-X` remains protocol/action endpoint, not a new enrollment algorithm. If equal-count same-visit diverse templates perform similarly, if visit 3 leaks into selection, or if participants/trace are infeasible, stop that claim.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Blur-stable structure/orientation palm matching already studied. | [K] | Hong et al., 2014-07-03, https://doi.org/10.1371/journal.pone.0101866 | Secs. 2.1, 3, 4.2, 4.4, 5; full publisher HTML. | PolyU with modelled Gaussian blur and controlled preprocessing; not evidence about Pi physical defocus. |
| Mobile ROI, enhancement, quality rejection, open-set and time-separated evaluation already combined. | [K] | Palm-ID arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Secs. I-B, II-A/B/F/G, III-A/E, IV-A; full HTML. | 224×224 input in their method, not a mandate for current DoN; model and camera differ. |
| Open-set palm metric learning and domain-shift evaluation exist. | [K] | Shao & Zhong, *Pattern Recognition* 121, 108247, DOI https://doi.org/10.1016/j.patcog.2021.108247 | Author-hosted PMC full text Secs. 2, 3, 4.2–4.3, 5–6. | Not a matched local Pi baseline; no claim about its performance on these stills. |
| Local 20-shot score overlap and ROI misses. | [E] | `minutes/10-06-white-labelled-continuous-capture-diagnostic.md`, 2026-10-06; corresponding local ignored full-still report/images | Inputs/protocol, Findings, Interpretation. | One person/two palms/continuous burst; cannot estimate FAR or cross-session performance. |
| Exploratory central-crop reversal between batches. | [E] | `minutes/10-06-highres-own-capture-diagnostic.md` and 20-shot diagnostic, 2026-10-06 | Results and Findings. | Same-day selected recipe; not held out. |
| Longitudinal matched-template gate needs independent people and untouched third visit. | [K]/[C] | `research/active/47-e-bound-x-sample-size-and-estimand-gate.md`, 2026-09-27 | Estimands, sensitivity table, recommended route. | Local planning calculation, not observed effect. |

## Queries and failed searches

- `Palm-ID mobile open set palmprint recognition quality recapture arxiv 2401.08111 full paper`
- `contactless palmprint recognition low quality blurred ROI alignment 2024 2025 paper author`
- `Blurred Palmprint Recognition Based on Stable-Feature Extraction later 2020 2024 cited paper`
- `site:arxiv.org palmprint image restoration blur low quality recognition 2024 2025`
- `long term palmprint template selection multiple sessions Chen 2019 representative palmprint`
- `open set palmprint recognition threshold gallery impostor score Palm-ID paper quality recapture`
- Later citation-chain spot checks found ICCV 2025 augmentation and other low-quality work but no reason to promote generic blur or quality enhancement. The 2017 Chen template-selection full text and Nature Communications 2025 dynamic-registration full text were not inspectable here; their inaccessible details are not used as exact-claim proof. No global novelty inference is made from these searches.

## Decision

PIVOT — perform the manual-ROI plus controlled acquisition failure-localization gate first; retain `E-BOUND-X` only behind that gate and its existing three-visit/person-count requirements. KILL a generic blurred-palm filter, matcher swap, or threshold adjustment as the thesis claim.
