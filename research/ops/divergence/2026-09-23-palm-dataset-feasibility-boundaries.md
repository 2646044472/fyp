# Divergence Packet: 2026-09-23 palm dataset feasibility

## Decision investigated

Can 3-5 distinct questions in the one staged Pi 5 Palm Payment route be minimally falsified without a large consented live cohort? The September 22 note `minutes_note.md/9-22.md` reports assembled IR/camera, deep-learning ROI, `same hand FR 66`, low FA, and proposed background/box and camera changes. [GAP] The apparent ~66% same-hand rejection is unverified: the note gives no raw counts, unit, denominator, threshold, session definition or acquisition-failure accounting; low FA has no independent unknown-person denominator. IR assembly is not stable vein evidence. Proposed interventions are not results. This is an MVP feasibility blocker first. The September 13 user-confirmed roadmap still requires VIS live identifier-free 1:N with a logged idempotent simulated debit before NIR/PAD. Cropped ROI results cannot establish live capture or payment safety.

## Search boundary

Primary full Palm-ID, X-Palm, GBU-Palm and face gallery-consensus papers, official dataset pages and author repository inspected on 2026-09-23. Bob Zhang's official list and CROI abstract checked; CROI/VIS-NIR/SF2Net full texts not obtained. The overlapping palm archive and newest September 23 packets are negative leads, not novelty clearance. No global novelty claim.

[K] IIT Delhi Touchless Palmprint v1.0 offers 800x600 full hands and separate 150x150 automatic crops, but needs application and academic-only/no-redistribution terms. Its detailed page says 230 people and seven images per left/right hand; an official index says 235: verify roster. No documented separate visits or physical retry episodes. PolyU-IITD v3.0 needs institution-signed licence/approval (up to 45 days) and restricts publishing images. X-Palm v2 has 103 persons (81 paired scanner-phone, 22 phone-only), raw and semi-manually annotated ROIs, but requires an approved signed non-commercial EULA and prohibits redistribution/re-identification. GBU-Palm v1 prose says both "released" and "will be released soon"; no verified usage grant. Local CASIA/PalmBigDataBase archives do not prove lawful use; CASIA terms and provenance unverified.

**Proposed exact split conditional on rights and roster:** Hash/manifest person, hand, image, source, real session if supplied, pose, crop provenance. X-Palm: fixed seeded 60/10/11 *persons* for train/development/final among 81 paired people; reserve 22 phone-only from paired spectral tests. All hands/modalities/images of a person travel together. In final, preassign six people enrolled gallery and five never-enrolled unknown probes, rotate gallery membership through predeclared folds without tuning on final people. One declared gallery image per enrolled hand and distinct probe. Scanner VIS/IR may be paired within acquisition; scanner versus phone is not paired VIS/NIR. IITD full-hand: 160/35/remainder people after roster check; one declared numbered image per hand gallery, other images probe, half final people never enrolled. Neither split is session-held-out or live retry. X-Palm's published 80/20 train-identity split and 50/50 gallery/probe sampling are not necessarily mate-absent transaction rejection. Tiny final identity counts cannot certify rare error; report person-clustered uncertainty.

## Recent-paper limitation map

| Primary neighbor | Task/input/endpoint and limitation inspected | Boundary |
| --- | --- | --- |
| Palm-ID, arXiv:2401.08111v1, 2024-01-16, II-F/G, III-B-D, IV-A/B, V | Mobile ROI, quality reject/recapture, enrollment, open-set 1:N FPIR/FNIR and component speed. | Generic ROI, quality retry, open set and edge deployment occupied; CPU search is not Pi transaction. |
| X-Palm, arXiv:2606.08437v2, 2026-06-22, 2.1-2.4, 3.1-3.3, 4, A.5 | Multispectral scanner/phone, curated ROIs, training-identity-disjoint Rank-1/EER; only 103 people. | Generic VIS/NIR/domain benchmark occupied; no acquisition-to-debit denominator. |
| GBU-Palm, arXiv:2608.14389v1, 2026-08-14, 2-4 | Physical print/replay RGB/NIR videos, lineage/environment splits, binary PAD, spectral/temporal tests. | Generic PAD/fusion occupied; canonical ROI is not target-account debit. |
| Pangelinan et al., arXiv:2607.12903v1, 2026-07-14, II-VII-A | Face mate-present/absent gallery consensus, gallery-size and synthetic-quality tests; multi-matcher cost. | Bare gallery-size threshold/consensus not new; strong comparator. |
| Su et al. with Bob Zhang, TIP 33:3662-3675, 2024-06-11, DOI 10.1109/TIP.2024.3407666 | CROI detection/aligned representation on four datasets, abstract only. | ROI method distinction [GAP] pending full-paper audit. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| F-ATTR | Repeated rejection makes checkout unusable. | [C] Frozen-path trace attributes failure to capture, ROI, score/threshold or action; counterbalanced box/background/camera changes a predeclared stage. Research residual only if transferable stage/action ranking survives, not bug fixing. | Palm-ID; Bob Zhang CROI. | Define `FR 66` denominator, hand/account truth, raw frame, ROI status and score. Replay lawful *raw* IITD/X-Palm hands; then small authorized Pi physical pilot. If simple placement/threshold/camera repair solves it, [KILL] thesis, retain MVP fix. | No large cohort for preflight; public data cannot validate Pi optics/IR/full path. |
| G-MATE | Mate-absent person assigned another mock account. | [C] Single-matcher score-tail/margin reject changes false-assignment/correct-completion frontier at matched gallery/compute; negative calibration transport is useful. | Palm-ID open set; face rank consensus; X-Palm train-open set. | Person-disjoint split above; fixed threshold, margin, gallery-specific threshold, quality reject, consensus baselines. [KILL] Baseline dominance or unresolved uncertainty. | Offline falsification conditional on EULA/roster; strong collision risk; no live debit inference. |
| S-PAIR | IR costs power yet may add no distinct information. | [C] Same-pose scanner IR adds held-out recognition over VIS at matched probe availability/cost; null blocks vein inference. | X-Palm multispectral; GBU-Palm; Bob Zhang VIS-NIR [full-text GAP]. | Approved paired scanner subset, fixed pose/bands, VIS/IR/simple fusion and brightness/crease controls. [KILL] VIS dominance or no independent stable vessel evidence. | EULA conditional; scanner result does not validate Pi illuminator, energy, veins or attacks. Likely appendix. |
| R-ID | Curated crops hide acquisition failure and retry dependence. | [C] Transaction retry benefit is non-identifiable from unlinked ROIs: two acquisition processes produce identical crop tables but opposite optimal retry. | Palm-ID; NIST IR 7544; Czajka/Bowyer multi-attempt iris. | Independent-improvement versus correlated/failed-retry worlds share first ROI scores. [KILL] Replay treating file order as attempt history. | No cohort for counterexample; too elementary alone; specifies necessary live logs. |

Pareto: F-ATTR is urgent and feasible but likely engineering; G-MATE is the best offline prospect but collision- and sample-limited; S-PAIR is useful negative optics evidence but occupied; R-ID is a clean boundary but little standalone depth. All preserve the live identifier-free 1:N idempotent mock-debit endpoint.

## Top two formalizations

**F-ATTR.** [D] Independently labelled eligible presentations and stage events `C=capture`, `R=valid ROI`, `M=correct thresholded match`, `A=correct transaction action`, elapsed time. [A] Frozen gallery/threshold, counterbalanced physical background/camera condition, camera/exposure/IR state logs, approved people; repeated frames are clustered, not independent users. [T] Estimate `P(C and R and M and A | eligible)` and conditional stage failures, with person/session uncertainty. Observable outcome: reproducible same-hand rejection denominator and intervention effect on a named stage. Counterexample: cropped recognition improves while live ROI yield is zero. Negative value: an auditable failure taxonomy and MVP repair, not automatically a novel thesis.

**G-MATE.** [D] Gallery `G`, rostered probe identity `Y`, score vector `s(x,G)`, action `commit top` or `unknown`, fixed compute budget. [A] Person-disjoint calibration/final, gallery membership recorded, no final-label threshold tuning. [T] At preregistered gallery sizes compare `P(commit | Y not in G)` with `P(commit correct | Y in G)`, enrolled wrong identity separately; Pi matcher-only p95 cannot be called transaction p95. Counterexample: conservative fixed threshold dominates margin/score-tail; multi-matcher consensus violates budget. Negative value: bounded non-transport of calibration across gallery/condition cells, not production false-match assurance.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| VIS full transaction first, later NIR/PAD gated. | [K] | Local `minutes/09-13-palm-payment-roadmap-update.md`, 2026-09-13 | Decision, Phases 1-4 | User decision, not research evidence. |
| Undefined same-hand FR and proposed physical changes. | [K]/[GAP] | Local `minutes_note.md/9-22.md`, 2026-09-22 | Entire five-line note | No rate, low-FA or vein proof. |
| Mobile ROI, open-set search, quality recapture exist. | [K] | https://arxiv.org/html/2401.08111 , arXiv:2401.08111v1, 2024-01-16 | II-F/G, III-B-D, IV-A/B, V | Not Pi full transaction. |
| X-Palm identities, open-set protocol and restricted EULA. | [K] | https://arxiv.org/html/2606.08437v2 , arXiv:2606.08437v2, 2026-06-22; https://github.com/X-Palm/X-Palm-2026 | 2.1-2.4, 3.1-3.3, 4, A.5; README Dataset Access/Evaluation Protocols | Signed full terms and approval pending; training-open set differs from mate-absent. |
| Physical multimodal PAD and conflicting release words. | [K]/[GAP] | https://arxiv.org/html/2608.14389v1 , arXiv:2608.14389v1, 2026-08-14 | Abstract, 2-4/tables | No verified data grant; binary ROI endpoint. |
| Gallery consensus direct neighbor. | [K] | https://arxiv.org/html/2607.12903 , arXiv:2607.12903v1, 2026-07-14 | II, III, V-VII-A | Face/synthetic quality; palm novelty unresolved. |
| IITD original hands/crops and academic access terms. | [K] | https://web.comp.polyu.edu.hk/csajaykr/IITD/Database_Palm.htm ; https://www4.comp.polyu.edu.hk/~csajaykr/myhome/database_request/palm/term.htm (accessed 2026-09-23) | Brief Description, Download/Copyright; entire terms | 230/235 discrepancy and approval pending. |
| PolyU-IITD institution licence and image restriction. | [K] | https://www4.comp.polyu.edu.hk/~csajaykr/palmprint3.htm (accessed 2026-09-23) | Brief Description, Download/Copyright | Session roster unverified. |
| Bob Zhang CROI detection/alignment work. | [K]/[GAP] | https://pubmed.ncbi.nlm.nih.gov/38837937/ ; DOI 10.1109/TIP.2024.3407666, 2024-06-11; https://pamigroup.github.io/publications.html | Published abstract/list only, **full text not read** | No exact distinction or advisor-fit novelty inference. |

## Queries and failed searches

2026-09-23: `Palm-ID dataset protocol open set quality recapture`, `GBU-Palm dataset release license protocol`, `CASIA multispectral palmprint database license research use official`, `PolyU palmprint database access terms`, `X-Palm cross device palmprint dataset official github`, `palmprint gallery size open set identification threshold score normalization`, `Rank-1 Identity Consensus Predicts Gallery Enrollment`, `Complete Region of Interest PalmALNet pdf`, `VIS-NIR Bob Zhang palmprint pdf`, `SF2Net Bob Zhang pdf`. CASIA official usage terms, approved IITD/X-Palm access, GBU release/grant, full Bob Zhang CROI/VIS-NIR/SF2Net, and exhaustive newer palm gallery/retry citation chains remain [GAP]. Failed searches do not prove novelty.

## Decision

HOLD thesis selection. First run a small authorized F-ATTR trace to reproduce the note's denominator and attribute capture/ROI/matcher/action failures before changing a model. Request dataset approval and freeze roster-level manifests/splits before G-MATE/S-PAIR. R-ID rules out dataset-only T-RETRY: image file order is not physical attempt history. G-MATE as dataset-only thesis is conditional on a defensible direct-neighbor distinction, lawful access and enough independent identities; otherwise defer thesis choice until the live gate and retain MVP/negative evidence. No low-FA, vein, liveness, physical PAD or real payment safety claim.

HOLD
