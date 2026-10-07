# Validation Audit: 2026-09-24 residual candidates

## Decision investigated

Audit the newest divergence packets available before 2026-09-24:

- `2026-09-23-palm-direction-next-gate-divergence.md`: `G-ADMIT`, `VIS-GUIDE`, `S-SELECT`, `P-DELETE`.
- `2026-09-23-raw-ir-direction-recheck.md`: `RAW-JPEG-GATE`, `IR-CAUSE`.
- `2026-09-23-p1-cross-device-privacy-divergence.md`: P1-A/D frontier or negative-boundary audit.
- `2026-09-23-beyond-palm-residual-divergence.md`: `VIS-GUIDE`, `AUDIT-GAP`, `PROBE-BOUND`, `SPLIT-LEAK`, `ENERGY-CONFIG`.

Required local files were read first: `AGENTS.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, and `research/ops/agent-validation.md`. This packet writes only to `research/ops/validation/`.

The current user-confirmed route remains the staged Pi 5 Palm Payment MVP: physical VIS capture, live ROI, identifier-free open-set 1:N, simulated debit and logging. That route is an engineering commitment, not evidence of thesis novelty.

## Claim under test

The strongest remaining claims were tested in their narrowest defensible form:

1. `VIS-GUIDE`: on the frozen physical payment executable, one prospective prompt plus one retake improves all-start enrolled completion or capture-to-action p95 beyond fixed retake/quality/margin/unknown controls at matched opportunities.
2. `AUDIT-GAP`: with an independently recorded full-support reference, an adaptive cheap-sentinel/expensive-verifier policy improves a held-out episode-level missed-event, latency, energy and `unknown` frontier over periodic, random and always-verify controls.
3. `RAW-JPEG-GATE`: a same-exposure RAW scalar improves exact-code `retain / unknown / reacquire` decisions over JPEG quality controls at matched end-to-end cost.
4. `IR-CAUSE`: an IR-on intervention identifies a named low-visible-light versus transparent-cover pair and improves the same action frontier beyond passive quality, IR ratio, fixed two-shot and always-reacquire.
5. `P1-A/D`: a fixed palm extractor and service-keyed representation produce a reproducible cross-device utility versus cross-service-linkability frontier or a bounded negative result under a declared attacker and edge budget.
6. `G-ADMIT`, `S-SELECT`, `P-DELETE`, `PROBE-BOUND`, `SPLIT-LEAK` and `ENERGY-CONFIG`: test whether their proposed endpoint survives direct-neighbor, baseline and feasibility checks.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Palm ROI, quality rejection/recapture, open-set 1:N and sequential accept/reject/continue are occupied by Palm-ID, NIST IR 7544 and Murakami/Takahashi. Cross-device palm recognition and protected-template/linkability metrics are occupied by Shen, AdaptPFL, X-Palm, ISO/IEC 24745 and Gomez-Barrero. Adaptive sensing/probing, active fault diagnosis, screen/confirm escalation, RAW processing and adaptive exposure are occupied by iAirGuard, Han, Talli, Bian, ReRAW, Lens and AdaptiveAE. | The candidates name narrower endpoints: Pi transaction p95, exact printed-code action loss, an independently recorded reference, or a two-service palm protocol. These are apparatus/protocol distinctions, not unoccupied components. | **High collision** for any new method, model, generic policy, or deployment-only claim. |
| Exact-claim collision | `VIS-GUIDE` still has the same decision family as guided acquisition and sequential biometric retry. `AUDIT-GAP` has the same adaptive observation/probe action family and most of the same delay/cost endpoints. `RAW-JPEG-GATE` and `IR-CAUSE` are retain/reacquire policies under resource cost, which is the same action family as screen/confirm/escalate sensing. P1-A/D combines two occupied evaluation families: cross-device recognition and protected-template unlinkability. | No inspected primary source was verified to join every named condition in one paper: physical Pi payment executable; independently powered reference; exact marker oracle; or cross-device palm plus multi-service attacker plus Pi cost. This is a bounded retrieval gap, not a novelty result. | **Medium for exact duplication; weak residual distinction.** |
| Boundary / impossibility | `AUDIT-GAP` has blind intervals: two physical worlds can share the same sentinel history while differing in a short event between verifier samples. A periodic maximum-gap policy can dominate when event timing is independent of the sentinel. `IR-CAUSE` can have visible observations identical across two worlds with different optimal actions; RAW may expose no information beyond JPEG quality. P1 utility/linkability cannot be identified without fixed attacker artifacts, crossed identities/devices/sessions and key states. `VIS-GUIDE` cannot estimate a prompt counterfactual from replay-only data. | A finite negative/boundary result remains possible if labels, clocks, physical cells, action costs, identities and permissions are fixed before collection. The result must be scoped to the stated observation model and cannot become a general theorem or deployment guarantee. | **High for conditional kill; low for positive separation.** |

## Assumption and identification audit

### `VIS-GUIDE`

- The unit of analysis must be an eligible physical presentation, not a selected successful frame. Count every all-start presentation, including capture failure, ROI failure, matcher unknown, wrong match and action failure.
- Random prompt assignment must occur before the relevant capture and be counterbalanced by person, session, order and fixture cell. Replay cannot identify the prompt counterfactual.
- `FR 66` in `minutes_note.md/9-22.md` has no denominator, modality, threshold, session count or stage trace. It cannot support FRR/FAR, policy superiority or a direct collision claim.
- The payment default `AutomaticPalmROI` and debug deep-learning `HandLandmarkTracker` are separate local paths. A debug-path result cannot be attributed to the payment executable without a trace.
- A fixed retake, quality/margin threshold, conservative `unknown`, fixture repair, exposure correction or background change is the strongest baseline. If it matches, the remaining result is MVP diagnosis, not a method contribution.

### `AUDIT-GAP`

- The reference is an evaluation oracle, not online evidence. It needs independent sensor, clock, power, calibration and resolution finer than the shortest event claimed detectable.
- If event occurrence is software-triggered by the monitor clock, the reference labels are circular. If the reference shares the target sensor or blind spot, independence is unproven.
- With a fixed verifier budget, a short event between samples can be unobservable. `unknown` may be the only honest output; it cannot be counted as a miss or a success without a predeclared contract.
- A real sentinel-event dependency must be measured on source cells and frozen before held-out evaluation. Otherwise an adaptive policy is merely exploiting a designed testbed.
- Periodic, uniform-random, always-verify and abstain controls must be charged for equal verifier-on cost, latency, storage and energy.

### `RAW-JPEG-GATE` and `IR-CAUSE`

- RAW/JPEG pairing requires a request/frame witness, not merely adjacent timestamps. Exposure, gain, white balance, sensor mode, storage, unpacking, decode and energy must be charged.
- IR causal language is invalid unless low-visible-light and transparent-cover worlds are independently assigned and held out. A lux reading or passive image score is not an independent cause label.
- Fixed two-shot and always-reacquire can dominate an adaptive intervention. A scalar IR ratio or JPEG decoder confidence can also tie the proposed endpoint.
- A static marker is not independent truth for the capture path; payload truth must be verified separately.

### `P1-A/D`

- A privacy result requires a service owner, attacker vantage, exposed templates/scores/metadata, key-compromise state, renewal semantics and a defined linkage function. “Salted” is a baseline, not a security claim.
- Identity-by-device-by-session crossings are required. Image-pair counts do not replace independent people, and public biometric access does not imply permission for cross-service reidentification analysis.
- Device normalization, identity, session, key and gallery effects must be separated. The current local one-service Palm Payment app has no cross-service protocol or confidentiality owner.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Grosz, Godbole & Jain, *Palm-ID*, arXiv:2401.08111v1 (2024-01-16), https://arxiv.org/html/2401.08111 | Mobile contactless palm images; ROI, quality, recapture, embedding search and open-set 1:N | FNIR/FPIR, rank, quality and component timing; Secs. II-F/G, III-B-D, IV-A/B, V | Palm ROI, quality retry and open-set components | Kills a new mobile palm pipeline or generic retry method; leaves only the local physical transaction endpoint. |
| Tabassi & Grother, *NIST IR 7544* (2008-11), https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Biometric acquisition/enrollment quality and recapture controls | Failure-to-acquire/enroll and acquisition guidance; Secs. 2.1.1-2.1.3, 4-6 | Quality gating, enrollment and reacquisition | Kills “quality-aware capture” as a standalone thesis; leaves a finite apparatus evaluation. |
| Murakami & Takahashi, WIFS 2009, DOI https://doi.org/10.1109/WIFS.2009.5386482 | Sequential biometric scores with accept/reject/continue and non-enrollees | Sequential open-set decision behavior; Secs. 2-4 | Retry/continue/open-set policy family | Kills positive generic `T-RETRY`; any local prompt study is an evaluation, not sequential-policy novelty. |
| Su, Fei, Zhang et al., *Complete Region of Interest for Unconstrained Palmprint Recognition*, IEEE TIP 33 (2024), DOI https://doi.org/10.1109/TIP.2024.3407666; https://pubmed.ncbi.nlm.nih.gov/38837937/ | Unconstrained palm image and learned complete ROI/alignment | Palm ROI quality and recognition; official abstract/bibliography inspected | Bob Zhang direct ROI neighbor | Kills superficial advisor-fit/ROI novelty. Full method/limitations remain [GAP], so it cannot by itself establish exact prompt overlap. |
| Mondal et al., *iAirGuard*, COMSNETS SysAI 2026, DOI https://doi.org/10.1109/COMSNETS67989.2026.11418151; author PDF https://cse.iitm.ac.in/~cs25d002/assets/iairguard_paper.pdf | Low-cost sentinel, dynamic sampling and secondary sensing | Event detection, data/transmission reduction and latency; Secs. II-A/B, III, pp. 3-6 | Cheap-sentinel/adaptive-verifier component family | Kills generic adaptive sensing; leaves only the independently labelled episode endpoint, which is not itself a mechanism. |
| Zhang & Mei, *Bandit Change-Point Detection for Real-Time Monitoring High-Dimensional Data Under Sampling Control*, Technometrics 65 (2023), https://pmc.ncbi.nlm.nih.gov/articles/PMC10027391/ | Controlled observations under sampling cost | Detection delay, false alarms and observation cost; Secs. 1, 3.1, 4 | Sampling-budget trade-off | Kills broad “sampling under edge budget” novelty; physical event/oracle scope remains different. |
| Talli, Popovski & Simeone, *Risk-Aware Online Conformal State Probing*, arXiv:2609.25889v1 (2026-09-22), https://arxiv.org/html/2609.25889v1 | State predictor and actions `probe / act / defer` | Missed-query error, probing rate and risk; Secs. 1-4 | Same action/probe/risk mechanism as `AUDIT-GAP` and `PROBE-BOUND` | Kills generic risk-aware probing; a Pi tabletop implementation would be a replication unless the physical endpoint itself is the contribution. |
| Han et al., *Active Counterfactual Perception Fault Diagnosis*, arXiv:2509.18460v1 (2025-09-22), https://arxiv.org/abs/2509.18460 | Active physical interventions and perception-fault hypotheses | Diagnosis through action-conditioned observations; Secs. I-VII | IR intervention/active diagnosis family | Kills broad `IR-CAUSE` causal-diagnosis framing; leaves only a finite two-world identifiability test. |
| Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065 (2026-08-10), https://doi.org/10.3390/s26165065 | Cheap screening, confirmation, uncertainty/OOD escalation and watchdog | Resource-aware screen/confirm/escalate under device/condition shift; Secs. 1, 3.1, 5.1, 6, 8 | Same adaptive acquisition/action family as `IR-CAUSE` | Kills generic resource-aware modality selection; a named Pi optical cell may remain only as replication/null. |
| Berdan et al., *ReRAW*, CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_RGB-to-RAW_Image_Reconstruction_via_Stratified_Sampling_for_Efficient_Object_CVPR_2025_paper.html | RGB/RAW representations and mobile object detection | Reconstruction and detection efficiency; Secs. 1-5, pp. 11833-11843 | RAW edge robustness/representation family | Kills broad RAW robustness or RAW-at-edge claims; exact-code retain/reacquire remains only a finite endpoint. |
| Baek et al., *Lens*, arXiv:2503.02170v3 (2026-05-19), https://arxiv.org/abs/2503.02170; Xu et al., *AdaptiveAE*, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | Camera action/exposure selection | Adaptive capture and exposure; Lens Secs. 3.1-3.2, 4-5; AdaptiveAE Secs. 3.3-3.4, pp. 25176-25185 | Adaptive camera intervention | Kills generic adaptive exposure/action selection; does not prove exact printed-marker collision. |
| Shen et al., *Distribution alignment for cross-device palmprint recognition*, Pattern Recognition 132 (2022) 108942, https://doi.org/10.1016/j.patcog.2022.108942; author PDF https://kaiz.net/publications/pr2022distribution.pdf | Cross-device palm images and alignment | Cross-device palm recognition; abstract, dataset, method and conclusion | P1 utility/device-shift half | Kills generic device-invariant palm representation; no linkability endpoint. |
| Gomez-Barrero et al., *General Framework to Evaluate Unlinkability in Biometric Template Protection Systems*, arXiv:2311.04633 (2023-11-08), https://arxiv.org/html/2311.04633 | Protected templates and declared linkage protocol | Linkability measures and protocol; Secs. II-VI | P1 threat/evaluation half | Kills vague “privacy-preserving template” claims; leaves a finite palm instantiation only after attacker/data authorization. |
| Otroshi Shahreza, Shkel & Marcel, *On Measuring Linkability of Multiple Protected Biometric Templates Using Maximal Leakage*, IEEE Access 12 (2024), https://doi.org/10.1109/ACCESS.2024.3433536 | Multiple protected templates, keys and scores | Maximal linkability under multi-score/key conditions; Secs. III, IV-B3-IV-B5, IV-D, V, pp. 3-10 | P1 multi-service/key attack condition | Kills one-key/one-score privacy evaluation; leaves no current Pi protocol or lawful crossed dataset. |

## Strongest simple baseline

The strongest baseline differs by candidate:

- `VIS-GUIDE`: fixed placement prompt plus one fixed quality/margin retake, then conservative `unknown`; repair camera/ROI/exposure/background before policy comparison.
- `AUDIT-GAP`: periodic maximum-gap verification at equal verifier-on cost, plus always-verify, uniform-random and abstain. Under schedule-independent events, adaptation has no reason to beat the periodic gap bound.
- `RAW-JPEG-GATE`: JPEG luma/blur/saturation plus decoder confidence, then fixed reacquisition; charge RAW request, storage, unpacking, decode and energy.
- `IR-CAUSE`: fixed two-shot RGB then IR, scalar IR ratio and always-reacquire; charge joules, latency and operator time.
- `P1-A/D`: raw template, standard per-service salted transform, published cancelable palm baseline, and no-normalization control at matched bytes/latency; evaluate one- and multi-score attackers.
- `S-SELECT`, `P-DELETE`, `ENERGY-CONFIG`: fixed cascade, transactional delete/restart test and static resource profile. If these pass, the candidate is ordinary engineering conformance/profiling.

## Contrarian result

The residual distinction in every candidate is mostly a measurement contract, not a technical mechanism. The most favorable reading is that a finite null or non-identifiability result could still be scientifically useful. The contrarian test rejects promotion for three reasons:

1. The proposed positive claim is not separable from a strong fixed baseline until the actual apparatus, data, labels and costs exist.
2. The proposed “independent truth” is often only an evaluation oracle; it cannot repair online blind intervals, confounding, or a missing action owner.
3. Bob Zhang adjacency is real for palm ROI, cross-spectral and sequence work, but it is advisor fit and a direct-neighbor warning. It does not make guidance, ROI, recognition, or template privacy novel. The full CROI, VIS-NIR and SF2Net papers were not available for complete method/limitation reading in this pass, so exact non-overlap remains [GAP].

## Feasibility audit

| Candidate | Data/labels/permission | Hardware/compute/time | Kill condition before implementation | Status after this audit |
| --- | --- | --- | --- | --- |
| `VIS-GUIDE` | Consented people, person/session IDs, all-start stage labels, authorized mock transaction | Uses committed Pi path; feasible only after MVP is frozen by 2026-12 | No stable payment executable, no randomized prompt assignment, fixture/ROI repair dominates, or insufficient independent sessions | **HOLD/PIVOT evaluation-only** |
| `AUDIT-GAP` | Independently powered/clocked reference, physically assigned event labels, workflow owner; no safety/medical claim | Cheap hardware but nontrivial reference and energy instrumentation; six-month pilot possible only after protocol lock | Reference not independent, event shorter than resolution, periodic baseline ties/dominates, or no real review endpoint | **PIVOT** |
| `RAW-JPEG-GATE` | Exact payload oracle and paired RAW/JPEG frames; no permission issue if inert marker, but still needs reproducible source | Camera Module 3/Pi capability is nominal only; same-exposure pairing and charged overhead are unverified | No request/frame witness, RAW overhead erases gain, or JPEG/fixed retry ties | **KILL positive / PIVOT appendix** |
| `IR-CAUSE` | Independent cover/light labels, held-out physical cells, exact payload truth | Requires NoIR/IR path, power meter, manual AE/WB/timing and remount repetitions | Two worlds overlap, fixed two-shot dominates, or intervention effect is not repeatable | **KILL broad / PIVOT finite pilot** |
| `P1-A/D` | Lawful same-identity crossed devices/sessions, service owner, attacker model and key states | High data/ethics burden; current app has one local service and no split protocol | No crossed lawful data, no realistic attacker, or salted baseline dominates | **KILL positive / HOLD only as data-gated audit** |
| `G-ADMIT` | Mate-present/absent roster, person-disjoint sessions and lawful gallery | Offline computation feasible; live transaction endpoint not yet measured | Gallery-relative or global threshold controls match, or independent unknowns unavailable | **KILL as thesis / appendix** |
| `S-SELECT`, `P-DELETE`, `ENERGY-CONFIG` | Local traces only | Easy on Pi | Fixed cascade/storage contract/static profile fully explains result | **KILL as thesis / engineering controls** |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Current Palm route is VIS physical capture, live ROI, identifier-free open-set 1:N and simulated debit | [K] | Local `minutes/09-13-palm-payment-roadmap-update.md`, 2026-09-13 | Decision, Phase 1-4 and Immediate Priority | User/project decision, not literature evidence |
| Current `FR 66` note lacks denominators and stage trace | [K]/[GAP] | Local `minutes_note.md/9-22.md`, 2026-09-22 | Entire note | Cannot support error rates or policy comparison |
| Palm ROI/quality/open-set components are occupied | [KILL] | Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | Secs. II-F/G, III-B-D, IV-A/B, V | Not Pi full transaction |
| Acquisition quality and recapture controls are established | [K] | NIST IR 7544, 2008-11, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Secs. 2.1.1-2.1.3, 4-6 | General biometric guidance |
| Sequential open-set accept/reject/continue is a direct neighbor | [KILL] | Murakami & Takahashi, WIFS 2009, https://doi.org/10.1109/WIFS.2009.5386482 | Secs. 2-4, read in the 2026-09-23 validation chain | Full text was not re-read on 2026-09-24 |
| Cheap-sentinel dynamic sampling and event/energy trade-offs are occupied | [KILL] | Mondal et al., iAirGuard, COMSNETS SysAI 2026, https://doi.org/10.1109/COMSNETS67989.2026.11418151 | Secs. II-A/B, III, pp. 3-6 | Exact independent-reference endpoint not established |
| Sampling control already trades delay, false alarms and observation cost | [K] | Zhang & Mei, Technometrics 65 (2023), https://pmc.ncbi.nlm.nih.gov/articles/PMC10027391/ | Secs. 1, 3.1, 4; pp. 34, 36-37, 39 | Different statistical model |
| Risk-aware action/probe/defer is directly formulated | [KILL] | Talli et al., arXiv:2609.25889v1, 2026-09-22, https://arxiv.org/html/2609.25889v1 | Abstract; Secs. 1-4 | Generic mechanism, not the proposed physical apparatus |
| Active diagnosis and screen/confirm acquisition occupy IR action families | [KILL] | Han et al., arXiv:2509.18460v1, 2025-09-22, https://arxiv.org/abs/2509.18460; Bian et al., Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Han Secs. I-VII; Bian Secs. 1, 3.1, 5.1, 6, 8 | Different domains, same mechanism family |
| RAW/edge perception and adaptive camera control are occupied | [KILL] | ReRAW CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Berdan_ReRAW_RGB-to-RAW_Image_Reconstruction_via_Stratified_Sampling_for_Efficient_Object_CVPR_2025_paper.html; Lens arXiv:2503.02170v3, https://arxiv.org/abs/2503.02170; AdaptiveAE ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/papers/Xu_AdaptiveAE_An_Adaptive_Exposure_Strategy_for_HDR_Capturing_in_Dynamic_ICCV2025_paper.pdf | ReRAW Secs. 1-5, pp. 11833-11843; Lens Secs. 3.1-3.2, 4-5; AdaptiveAE Secs. 3.3-3.4, pp. 25176-25185 | Exact marker endpoint remains finite and unverified |
| Cross-device palm recognition is occupied | [KILL] | Shen et al., Pattern Recognition 132 (2022) 108942, https://doi.org/10.1016/j.patcog.2022.108942 | Abstract, cross-device dataset, proposed method, conclusion | No linkability endpoint |
| Linkability requires explicit attacker and multi-score/key protocol | [K] | Gomez-Barrero et al., arXiv:2311.04633, 2023-11-08, https://arxiv.org/html/2311.04633; Otroshi Shahreza et al., IEEE Access 12 (2024), https://doi.org/10.1109/ACCESS.2024.3433536 | Gomez Secs. II-VI; Shahreza Secs. III, IV-B3-IV-B5, IV-D, V, pp. 3-10 | Face/voice experiments do not supply palm data or permission |
| Bob Zhang has a direct palm ROI neighbor | [K] / [GAP] | Su, Fei, Zhang et al., IEEE TIP 33 (2024), https://doi.org/10.1109/TIP.2024.3407666; https://pubmed.ncbi.nlm.nih.gov/38837937/ | Official abstract/bibliography only | Full CROI method, limits and citations unresolved |

## Queries and failed searches

Queries run or rechecked on 2026-09-24:

- `adaptive sensing independent reference trace missed event verifier budget edge physical event`
- `cheap sentinel expensive verifier periodic sampling energy event coverage primary paper`
- `palmprint guided capture prompt recapture open-set sequential accept reject continue primary paper`
- `Pi Camera Module 3 RAW JPEG same exposure request frame witness Picamera2`
- `active infrared intervention transparent cover low light camera exact payload action cost`
- `cross-device palmprint unlinkability multi-service protected template maximal linkability`
- `Bob Zhang palmprint ROI CROI VIS NIR SF2Net full paper`
- `edge configuration selection fixed cascade latency energy downstream decision baseline`

The search retrieved the primary URLs already recorded above and did not verify a single paper containing every narrow apparatus condition. This is [GAP], not novelty evidence. Failed or incomplete retrievals: full Bob Zhang CROI/VIS-NIR/SF2Net texts and complete citation chains; paid ISO/IEC 24745 normative clauses; current lawful access and permissions for crossed palm identities/devices; an actual Pi RAW/JPEG frame-pair run; the payment executable's all-start trace; and an independent physical reference/event apparatus.

## Decision

**PIVOT.** Kill all broad positive method claims:

- `G-ADMIT`: **KILL** as an offline gallery-calibration thesis; keep only a lawful matcher preflight.
- `S-SELECT`, `P-DELETE`, `ENERGY-CONFIG`: **KILL** as thesis directions; retain as engineering controls.
- `RAW-JPEG-GATE`: **KILL** as a positive RAW thesis; retain a capability/null appendix only.
- `IR-CAUSE`: **KILL** as causal diagnosis, passive camera health or generic adaptive sensing; retain only a finite active-IR action/identifiability pilot.
- `P1-A/D`: **KILL** the positive privacy/robustness method or monotone frontier; retain only a data-, attacker- and permission-gated finite audit.
- `AUDIT-GAP`: **KILL** the positive adaptive-sampling claim; retain only a bounded independent-reference reliability audit, with periodic dominance or blind-interval non-identifiability as expected outcomes.
- `VIS-GUIDE`: **HOLD/PIVOT evaluation-only**, after the actual payment executable is frozen and the all-start stage trace exists. It is the best route-compatible measurement, but no thesis mechanism or superiority claim is established.

No candidate is promoted. The current FYP should continue the Palm Payment MVP as engineering work, then re-open only `VIS-GUIDE` after the feasibility gate; every other residual requires a new owner, data/permission package, or apparatus-specific pilot before it can be considered research.

PIVOT
