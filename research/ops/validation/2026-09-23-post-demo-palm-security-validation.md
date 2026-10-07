Decision investigated: After the authorized Phase 1 Raspberry Pi 5 VIS palm-payment 1:N demo, can physical presentation attacks, lightweight PAD, and controlled NIR/vein fusion support a separate thesis? Audit date: 2026-09-23.

# Validation Audit: Post-Demo Palm Security and Multimodality

## Decision investigated

[K] The 2026-09-13 roadmap authorizes a VIS local simulated-payment 1:N transaction first, then gated NIR and physical-attack/PAD work. This supersedes the September 4 preference against immediate physical attacks; that is historical, not a current veto. Phase 1 is engineering, not research evidence. Archived PRF-TR printed-code work is not the default direction.

## Claim under test

Story: a customer presents a palm; a printed/displayed copy or mistaken open-set match could cause a simulated debit to the wrong account, while indiscriminate rejection/repeated capture impairs use. Candidate claim [C]: a bounded capture/PAD/NIR decision on Pi 5 reduces attack-accepted and wrong-identity transactions at fixed bona-fide completion/retry/time/resource cost beyond VIS PAD and fixed recapture/fusion. Neither a demonstrated novelty nor real payment security.

## Three-round novelty audit

| Round | Collision | Remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component | [KILL] Palm-ID integrates mobile ROI, quality rejection and open-set 1:N; GBU-Palm physically recaptures print/replay and tests RGB/NIR PAD; PVASD covers NIR vein attacks; Fan et al. cover print/vein fusion. A Pi, small CNN, IR LEDs or weighted sum is not a new component. | Local fixture and sequential intervention differ in apparatus, not necessarily research task. | High broad collision; PVASD/Fan full methods outstanding. |
| Exact task/action/endpoint | [KILL] Palm-ID reports FNIR at FPIR for 4,377 gallery and error-reject curves. GBU-Palm has physical print/replay, RGB/NIR, identity/lineage-disjoint PAD, held-out environments. Fan routes uncertain vein matches to adaptive fusion, measuring recognition/time. | [C] Joint ROI failure, open-set wrong identity/unknown, PAD, retry, debit gate and Pi costs were not established as one experiment in inspected full texts. Concatenated metrics alone are not a mechanism. | High generic kill; medium-low residual. |
| Boundary/identification | [KILL] Cropped ROIs bypass attack-to-ROI; digital overlays are not physical attacks; NoIR is not proof of veins; tiny galleries cannot establish rare-event security; sequential VIS/NIR confounds pose/time/gain. | [C] Authorized, physically presented, paired, held-out person/material/session and controlled-intervention study might identify a finite apparatus-specific effect. | High boundary; feasibility unknown. |

## Assumption and identification audit

- [KILL] PAD label and matcher identity differ. Report PAD by PAI species, plus `attack -> accepted gallery identity -> simulated debit`, `bona fide -> correct / wrong / unknown / retry`, failure to acquire, and denominators over *all* physical attempts. PAD AUC/EER or verification FMR alone misses 1:N harm. ISO/IEC 30107-3:2023 covers PAD, not overall security (official abstract only); Palm-ID Sec. III-C defines gallery/rank-dependent FNIR/FPIR.
- [KILL] Shared people, source images, print/display devices, material batches and sessions leak lineage across training/test. GBU-Palm Sec. 2 blocks identities and lineages; additionally hold out material/display/session. Print/replay does not cover gloves/partial real hands.
- [KILL] `IR helps PAD` differs from `IR sees veins`. Log wavelength/current, filter/sensor response, safety, exposure/gain/AWB, capture order and registration; show repeatable vessel contrast and NIR-only identity beyond brightness/crease/VIS leakage. Otherwise say `NIR-assisted palmprint/PAD`.
- [C] Selective NIR might add information, but if a second VIS capture or VIS score/quality reproduces the decision at matched time/energy, its value is zero here. Compare guided VIS recapture, fixed VIS+NIR two-shot, unimodal PAD, score sum, quality/score reject and conservative rejection. `Unknown` and `retry` are different outcomes.
- [KILL] Zero observed attack accepts in a small pilot is not payment-grade assurance: roughly 3/n is the 95% upper bound after zero events in n *independent* trials. Frames from one person/instrument are correlated. Freeze gallery/thresholds/policy before held-out cells; cluster uncertainty by subject and PAI lineage.

## Direct-neighbor table

| Work, URL, version/date | Inputs/actions | Target and sections/pages inspected | Overlap and boundary |
| --- | --- | --- | --- |
| Grosz, Godbole and Jain, Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111v1 | Mobile contactless ROI, embedding and quality reject | Secs. II-F/G, III-B/C/D, IV-A/B: open-set FNIR/FPIR, 4,377 gallery, time, error-reject | [KILL] Portable VIS 1:N and simple quality/reject; no physical PAD transaction. CPU/mobile timing is not Pi timing. |
| Ma et al., GBU-Palm, arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389v1 | Physically recaptured print/replay, 16-second video, canonical ROI, synchronized RGB/NIR subset | Secs. 2-4, Tables 2-6: 21,326 videos/105 people, held-out environment and attack lineage, PAD FA/FR and spectral/temporal tests | [KILL] Generic physical RGB/NIR PAD, environment/lineage controls; no 1:N matcher, target account or Pi transaction. Table says public but abstract says release soon: access unconfirmed. |
| Yan et al., PVASD, IEEE TIFS 21:945-959, 2026, DOI https://doi.org/10.1109/TIFS.2025.3650391; author PDF https://hise.hznu.edu.cn/upload/resources/file/2026/04/20/7930880.pdf | NIR palm-vein bona fide, 2D print and 3D PAI | Journal/author abstract only: large multi-attack benchmark; full PDF fetch timed out | [KILL] Adding NIR vein spoof detection as component; [GAP] exact protocol/method not inspected, so do not assert exact transaction collision. |
| Fan et al., IEEE TSMC Systems 54(7):4471-4484, 2024, https://doi.org/10.1109/TSMC.2024.3382877 | Vein first-stage likelihood, uncertain subset adaptive print/vein fusion | Institutional record abstract https://scholarship.miami.edu/esploro/outputs/journalArticle/A-Novel-Hybrid-Fusion-Combining-Palmprint/991032795956602976; full text unavailable | [KILL] Generic uncertainty-routed fusion for large-scale identification/response time. Abstract's aspirational anti-spoofing wording is not PAD evidence. |
| Seyedmohammadi et al., X-Palm, arXiv:2606.08437v1, 2026-06-07, https://arxiv.org/html/2606.08437v1 | Paired scanner/mobile identity, manual ROI | Secs. 2-4 and appendix: 103 subjects, recognition baselines, compound shift | [KILL] Small uncontrolled robustness claim; noncommercial EULA and no PAI labels. |
| Yang et al. including Bob Zhang, PSFed-Palm, arXiv:2308.00451 (2023; exact version/date unresolved), https://arxiv.org/html/2308.00451 | Multispectral federated palmprint verification | Secs. 3.2, 4, 5: CASIA multispectral EER and spectrum heterogeneity | Advisor adjacency, not novelty; no physical PAD/payment endpoint. |
| ISO/IEC 30107-3:2023 ed. 2, https://www.iso.org/standard/79520.html | Biometric capture presentation | Official abstract/scope only: PAD testing/reporting, not overall security | [KILL] Equating PAD score with payment assurance; full standard not read. |

GBU-Palm's reference chain points backward to Bhilare et al., "A study on vulnerability and presentation attack detection in palmprint verification system," Pattern Analysis and Applications 21:769-782 (2018), https://doi.org/10.1007/s10044-017-0606-y, and Tome and Marcel, "On the vulnerability of palm vein recognition to spoofing attacks," ICB 2015, https://doi.org/10.1109/ICB.2015.7139102. These are citation leads, not independently inspected full papers. Later GBU-Palm and PVASD occupy component families; no author's future-work sentence proves an opening.

## Strongest simple baseline

Freeze Phase 1 guided VIS capture, ROI, open-set maximum-gallery-score threshold and `correct / unknown / one guided VIS recapture`. Add cheap VIS-only print/display PAD, reject before debit, include every acquisition failure and elapsed time. Compare (a) no PAD, (b) VIS PAD, (c) fixed VIS+NIR two-shot with NIR-only PAD, (d) simple score sum/fallback, (e) VIS quality/score threshold with one retake, (f) proposed selective NIR/vein action. Match transaction attack acceptance and bona-fide correct completion at equal average/p95 time, CPU/RAM and measured energy *only if instrumented*. If (b), (c) or (e) matches the frontier, kill the policy thesis; preserve a bounded negative study instead of a post-hoc new network.

## Contrarian result

[KILL] Physical print/replay plus lightweight PAD plus RGB/NIR on Pi is a combination of known elements, not a paper identity. GBU-Palm finds fusion architecture-dependent and sometimes worse; NIR is not a safety guarantee. Its PAD uses canonical ROIs/long videos, so short transaction-level 1:N is a possible *measurement distinction*, not automatic algorithmic novelty. [C] Selective NIR might change a local security/usability/latency frontier; absent vessel signal, attack lineages or benefit beyond fixed two-shot/VIS retake, kill it. This neither demotes Phase 1 nor revives PRF-TR.

## Feasibility audit

[GAP] Confirm participant and PAI-source consent, institutional ethics, retention/deletion, lawful biometric/print storage, gallery and unknown-user access, and whether targeted impersonation can be staged without exposing someone else's template. No real charges/accounts. Confirm 850-nm LED/current/filter/sensor response, electrical/optical safety, fixture, print/display apparatus and power meter if energy is claimed. GBU-Palm release/license is unconfirmed; its ROI/video cannot substitute for local full-path labels. PVASD use requires license and domain checks.

Minimum falsification gate: preregister two bona-fide sessions, print and display PAI sources/material/devices and order; collect paired VIS, VIS retake and NIR on the local capture/ROI path including failures. Freeze policy on development people/lineages; hold out people, PAI material/device and sessions. Report source matcher score before PAD and cluster uncertainty. If attacks never pass ROI/matcher with PAD disabled, the harm is not shown on this apparatus; do not select only successful attacks. If vessels are not repeatable, say NIR-assisted PAD. If authorized varied data are unavailable, stop the thesis claim while completing Phase 1.

## Evidence ledger

| Claim | Label | Primary source/version and exact read extent | Scope/caveat |
| --- | --- | --- | --- |
| Mobile open-set 1:N and quality rejection exist | [K] | Palm-ID arXiv v1, Secs. II-F/G, III-C/D, IV-B and tables | Not physical PAD/Pi timing. |
| Physical RGB/NIR print/replay PAD, held-out lineage and nonuniform fusion exist | [K] | GBU-Palm arXiv v1, Secs. 2-4, Tables 2-6 | Canonical ROI/16-s video, not local 1:N; access ambiguous. |
| NIR vein spoof and uncertain-subset fusion have neighbors | [K/GAP] | Yan TIFS and Fan TSMC abstracts only; URLs in table | Full methods/later citation chains must be read before exact-claim exclusion. |
| Bob Zhang coauthored multispectral verification | [K] | PSFed-Palm arXiv HTML, Secs. 3.2, 4, 5 | Advisor fit is not novelty. |
| Ethics, optics, population, data access and local outcome unknown | [GAP] | Local roadmap 2026-09-13; X-Palm v1 Sec. 4; ISO official abstract | No approval, vein validity or production error inferred. |

## Queries and failed searches

Searched web 2026-09-23: `2024 2025 2026 mobile palmprint identification Palm-ID X-Palm full paper`; `palmprint presentation attack detection physical print display attack 2024 2025 full paper`; `palmprint palm vein NIR RGB fusion presentation attack detection 2025 2026 paper`; `Bob Zhang palmprint presentation attack detection multispectral palm vein fusion paper`; `2026 TIFS palm vein presentation attack 2D 3D NIR`; `palmprint presentation attack detection PALMspoof Bhilare 2018 full paper`; `site:arxiv.org palmprint palm vein fusion 2025 missing modality full`; `quality palmprint palm vein adaptive weighted fusion Fan 2024`; `X-Palm 2026 cross spectrum smartphone palmprint paper arxiv`; `PVASD comprehensive framework palm vein anti spoofing preprocessing dataset benchmark full pdf 2026`; `palmprint presentation attack detection lightweight mobile edge 2025 2026 full paper`; `ISO IEC 30107-3:2023 presentation attack detection official`; and GBU-Palm/X-Palm references. No exact short-window Pi open-set transaction comparator was established; absence is not originality. Yan PDF timed out; Fan and foundational Bhilare/Tome full texts were unavailable. Later citing-paper chains and dataset releases remain unresolved. This is not a comprehensive 2024-26 census.

## Decision

**KILL** generic physical-attack/PAD-on-Pi, lightweight-model, NIR-is-vein and adaptive-fusion formulations as standalone novelty. **PIVOT** only to a preregistered apparatus-specific physical-PAI open-set transaction decision at matched capture/resource budgets, conditional on ethics/data/optical feasibility and a baseline-beating residual. Phase 1 remains required and unchanged. No thesis is promoted today.

PIVOT
