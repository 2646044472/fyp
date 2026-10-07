# Validation Audit: 2026-09-24 targeted E-BOUND, PA-CHARGE, NOIR-SIDEINFO and PROG-RET

## Decision investigated

This audit tests four residual candidates in the 2026-09-24 targeted validation round:

- `E-BOUND`: whether a charged cross-pose or later confirmation visit at enrollment improves a later open-set palm transaction outcome beyond best-quality, same-session, multi-template and refusal controls.
- `PA-CHARGE`: whether a physical print/display presentation attack can be evaluated from physical presentation through ROI, open-set identification and simulated debit, with a bounded PAD/action/resource frontier.
- `NOIR-SIDEINFO`: whether a sequential NoIR image can act as decoder-side side information for a transmitted RGB maintenance marker at lower total cost and the same exact-code false-retain level.
- `PROG-RET`: whether a base-layer/enhancement protocol can stop after an early layer or request more data at lower expected bytes/latency than fixed full JPEG and fixed two-quality controls at a fixed false-retain ceiling.

Required local files were read first: `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, `research/active/39-round-24-cross-mechanism-reconciliation.md`, and `research/ops/agent-validation.md`. This packet writes only to `research/ops/validation/`. It does not promote a claim and does not modify `research/active/`, `research/archive/`, or `.research/`.

The current user-confirmed route remains the staged Pi 5 Palm Payment MVP: consented physical VIS capture, live ROI, identifier-free open-set 1:N, frozen unknown handling, idempotent simulated debit, and complete stage logging. That route is an engineering commitment, not evidence that any candidate below is novel.

## Claim under test

### E-BOUND [C]

At a fixed total enrollment effort, storage/search cost and revisit burden, a protocol that may request an additional pose or a separately charged confirmation visit improves later full-transaction outcomes over best-quality single-frame selection, same-session consistency, diverse/multi-template enrollment and conservative refusal. The intended endpoint is not merely FNIR/FPIR; it is original eligible-person denominators for failure-to-enroll, later correct completion, unknown, wrong identity, mock debit and time.

### PA-CHARGE [C]

For a locally staged simulated transaction, physical print/display PAIs can be evaluated from presentation through capture, ROI, PAD, open-set 1:N identity and mock debit. A bounded policy could reduce attack-accepted or wrong-identity debits at matched bona-fide completion, retry/time and edge-resource cost beyond no-PAD, simple VIS quality/score rejection, fixed VIS recapture and fixed VIS+NIR controls. This is not a production payment-security claim.

### NOIR-SIDEINFO [C]

For a static printed maintenance indicator, a sequential RGB/NoIR pair and a decoder-side residual/side-information representation can lower total transmitted bytes or latency at the same exact-code false-retain and energy cost compared with independent JPEG/WebP, ROI JPEG, RGB+NoIR concatenation and code-only transmission.

### PROG-RET [C]

A deterministic progressive transmission protocol can decide `retain`, `request enhancement` or `unknown` from a base layer and one or more enhancements, reducing expected bytes/latency at a predeclared false-retain ceiling compared with fixed full JPEG, fixed low/high JPEG, progressive JPEG/WebP and fixed two-shot capture/transmit controls.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision: `E-BOUND` | [KILL] NIST IR 7544 describes supervised quality acquisition, failure-to-enroll, recapture and the danger of unrealistically high same-session results. Palm-ID already combines mobile acquisition/ROI, quality rejection/recapture, enrollment and open-set 1:N. Chen et al. 2019 already select/update representative palmprint/palm-vein templates using longer-term samples. | A separately charged enrollment decision with a later transaction endpoint and refusal/revisit accounting is narrower than those components. That is a protocol/evaluation distinction, not a new enrollment mechanism. | High for a method claim; medium-low for the exact longitudinal endpoint. |
| Exact-claim collision: `E-BOUND` | [KILL-leaning] The proposed inputs and actions are quality/template selection, extra samples and refusal; the direct literature already evaluates representative templates and long-term intra-class variation. A different Pi and account simulator does not establish a new task. | [GAP] The inspected direct neighbors do not jointly establish the exact three-stage protocol: initial enrollment, optional charged confirmation/selection, and an untouched later live open-set transaction with original-eligible-person denominators. | Medium-low. This is a bounded measurement gap, not novelty evidence. |
| Boundary/impossibility: `E-BOUND` | [KILL] If the confirmation visit is also the outcome test, selection and test are contaminated. Restricting analysis to people who successfully enrolled rewards refusal. Adding templates changes gallery size and impostor opportunity. Repeated frames from one session do not identify cross-visit robustness. A later transaction risk cannot be inferred by multiplying FNIR, FPIR, FTE and latency from different populations or endpoints. | A finite longitudinal audit is identifiable if the three stages are disjoint, identity/account binding is externally supervised, refused and never-enrolled people remain in the denominator, and template/search cost is matched. A null or refusal-dominance result is useful. | High. |
| Component collision: `PA-CHARGE` | [KILL] Palm-ID covers mobile 1:N, ROI and quality rejection; GBU-Palm covers physical print/replay, RGB/NIR, attack/environment/lineage splits and PAD; prior palm-spoofing work and ISO/IEC 30107-3 occupy presentation-attack testing/reporting. A small CNN, NIR LED or score fusion is not a new component. | A full physical `presentation -> ROI -> PAD -> open-set identity -> simulated debit` trace on the local apparatus is narrower than the inspected benchmarks. It may support an apparatus-specific audit only. | High for generic PAD/NIR/fusion; medium for full-path endpoint. |
| Exact-claim collision: `PA-CHARGE` | [KILL-leaning] Physical PAI detection, RGB/NIR fusion and attack-lineage controls are already evaluated. PAD metrics alone are not transaction risk, but adding a debit endpoint does not create a method unless the decision/action policy changes and beats fixed controls. | [GAP] No inspected source was verified to measure the exact Pi full-path 1:N mock-debit endpoint with the proposed local optics, attack materials and matched bona-fide cost. | Medium. |
| Boundary/impossibility: `PA-CHARGE` | [KILL] A cropped ROI or digital ROI injection bypasses physical capture and cannot support a physical attack claim. If attacks never pass the local ROI/matcher with PAD disabled, the local attack-debit harm is absent rather than solved. Zero attack accepts in a small correlated pilot is not a meaningful assurance bound. NIR brightness or crease cues cannot be called vein sensing without independent vessel evidence. | A finite study is testable with authorized attack sources, people/material/device/session holdouts, a frozen gallery and threshold, and full denominators for acquisition, ROI, PAD, identity, unknown, wrong identity, debit and time. | High. |
| Component collision: `NOIR-SIDEINFO` | [KILL-leaning] Decoder-side information for multi-view compression, task-guided communication and compressed-domain/task-aware machine vision are established. A sequential NoIR frame is another side-information source; a residual codec or small model is not the contribution by itself. | The exact endpoint can be a finite physical RGB/NoIR marker audit with a non-personal payload oracle and charged bytes/latency/energy. The distinction is apparatus and endpoint, not a new distributed-compression family. | High for generic method; medium for finite benchmark. |
| Exact-claim collision: `NOIR-SIDEINFO` | [KILL-leaning] The claim has the same rate/task-success structure as task-aware communication and side-information compression. Replacing PSNR with exact-code success is a task endpoint change, not automatically a new mechanism. | [GAP] The inspected sources do not jointly test Pi 5 RGB/NoIR sequential capture, physical registration, exact printed-code success and matched total edge cost. | Medium-low. |
| Boundary/impossibility: `NOIR-SIDEINFO` | [KILL] If NoIR must be transmitted to the receiver, its bytes and capture/registration cost can erase the saving. A sequential pair has motion/timing misregistration; a static marker avoids motion but narrows the claim. If the exact code or a decoded hash is sent, the image task is bypassed. If the receiver uses ground-truth NoIR, the result is oracle leakage. | A finite result remains identifiable with a static target, independent payload truth, logged frame pairing/timing, receiver-side available data, and end-to-end byte/latency/energy accounting. A Pareto null against ROI JPEG is a valid result. | High. |
| Component collision: `PROG-RET` | [KILL-leaning] Progressive learned transmission, task-guided source-channel coding, OCR/task-aware compression and progressive quality/latency trade-offs are established. A hand-written stop rule is a policy over a known progressive representation, not a new codec. | A finite exact-code `retain/request/unknown` protocol under a shaped local link could expose a useful endpoint if it survives standard progressive JPEG/WebP and fixed-quality controls. | High for a codec/method claim; medium for evaluation-only protocol. |
| Exact-claim collision: `PROG-RET` | [KILL-leaning] The target is the standard early-decision rate-versus-task-risk problem. The endpoint changes to exact marker false-retain and local Pi latency, but the same action family is already present in task-oriented/progressive communication work. | [GAP] No inspected paper was verified to combine the exact marker, Pi encode/decode cost, shaped local link, full-image false-retain and an oracle-independent stopping rule. | Medium-low. |
| Boundary/impossibility: `PROG-RET` | [KILL] A base layer may produce a plausible but wrong code before enhancement; stopping on decoder confidence calibrated with the true code is oracle leakage. If the receiver waits for a full payload before checking the code, early stopping is impossible. A fixed high-quality JPEG or code-only message may dominate. | A finite study is identifiable if the stopping features are computed only from received bytes and prior calibration, exact truth is held out and used only for evaluation, and all representation/capture/transmission costs are charged. | High. |

## Assumption and identification audit

### Cross-visit enrollment and selection bias (`E-BOUND`)

1. **Three disjoint stages are mandatory.** Stage A collects the initial enrollment candidates. Stage B is the optional confirmation/selection/refusal decision. Stage C is an untouched later visit used only for outcome. Using Stage B as Stage C turns the proposed benefit into post-selection evaluation.
2. **The denominator is the original eligible roster.** Include people who are refused, fail to enroll, do not return, and return but fail capture. Reporting only successfully enrolled people makes refusal look like improved security and is a selection-bias error.
3. **Template count and gallery exposure must be matched.** A diverse-template arm can improve a later score simply by storing more templates or increasing impostor comparisons. Match template count, search rule, storage, enrollment minutes and later search cost, or report these as separate costs.
4. **No multiplicative transaction-risk shortcut.** `FNIR x FPIR x ACER x latency` is not an end-to-end transaction probability: these metrics use different populations, conditioning events and often different denominators. Estimate episode-level outcomes directly: `eligible person -> capture -> ROI -> identity/unknown -> policy -> mock debit`, with cluster uncertainty by person and session.
5. **Longitudinal dependence must be preserved.** Frames are nested in presentations, presentations in sessions and sessions in people. A large frame count from a few volunteers cannot stand in for independent later visits or unknown people.

### Physical PAI and transaction endpoint (`PA-CHARGE`)

1. Keep bona fide, unknown-to-gallery people and PAIs as separate strata. An unknown person is not a presentation attack, and a successful PAI is not automatically a wrong identity.
2. Record the full path for every physical start, including acquisition failure, ROI failure, PAD decision, matcher score/rank, correct identity, wrong identity, unknown, retry and mock debit. Do not condition on attacks that reached the matcher.
3. Hold out person, PAI lineage/source, print/display material, device and session. A frame-level random split leaks physical lineage and can make a PAD result look stronger than the transaction policy.
4. A transaction-risk endpoint is not established by multiplying `ACER`, `FNIR`, `FPIR` and latency. The joint event depends on policy ordering, gallery membership, PAI source and conditional reachability. Report direct episode counts and confidence intervals, with zero-event bounds stated honestly.
5. NIR must be named according to evidence. Without repeatable vessel-specific signal and a controlled wavelength/illumination protocol, use `NIR-assisted palm/PAD`, not `palm-vein sensing`.

### Side information and progressive stopping (`NOIR-SIDEINFO/PROG-RET`)

1. The receiver may use only data actually received. Supplying the exact decoded code, a truth-derived quality label, a ground-truth NoIR image or a post-hoc oracle confidence invalidates the stopping claim.
2. Log capture request ID, frame timestamps, camera settings, registration, raw payload bytes, encoded bytes, retransmissions, packet loss, decode time, marker decoder state, decision time and energy if energy is claimed.
3. Charge both cameras and all transmitted streams. For `NOIR-SIDEINFO`, compare sending NoIR, not sending NoIR, ROI-only and code-only. For `PROG-RET`, compare standard progressive JPEG/WebP with the proposed layer schedule at matched image quality and byte budget.
4. The stopping threshold must be frozen on development payloads and evaluated on held-out payloads/scenes. A threshold selected to make the exact-code oracle pass on the test set is not evidence.
5. A static printed target is a legitimate bounded task but cannot support claims about moving maintenance scenes, general image compression, or arbitrary wireless channels.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Tabassi and Grother, *Biometric Quality*, NIST IR 7544, 2008-11, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Quality-controlled enrollment/acquisition, recapture, failure-to-enroll and same-session controls | Secs. 2.1.1-2.1.3, printed pp. 18-21/PDF pp. 19-22; Sec. 5.1, printed pp. 37-40 | Best-quality enrollment and ordinary quality/reacquisition controls | Kills E-BOUND as generic quality/enrollment mechanism; leaves only a charged later-visit endpoint. |
| Grosz, Godbole and Jain, *Mobile Contactless Palmprint Recognition*, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111v1 | Mobile palm capture/ROI, quality rejection/recapture, enrollment and 1:N search | Secs. II-F/G, III-B/C/D, IV-A/B, V | Same acquisition and open-set palm components | Kills app/quality/matcher novelty in E-BOUND and part of PA-CHARGE; does not establish the Pi full transaction. |
| Chen et al., *A Generic Template Update Framework*, IEEE Access 7:145082-145094, 2019-10-02/current 2019-10-17, https://doi.org/10.1109/ACCESS.2019.2945064 | Long-term palmprint/palm-vein samples, representative template selection/update | Secs. II-III and IV, pp. 145083-145094 | Diverse/representative longitudinal templates | Kills multi-template/representative-selection method claim; leaves charged pre-enrollment confirmation plus later open-set endpoint unresolved. |
| Czajka and Bowyer, *Statistical evaluation of up-to-three-attempt iris recognition*, BTAS 2015, https://doi.org/10.1109/BTAS.2015.7358797 | Up to three attempts, selected score/quality distributions and a return visit | Secs. 1-4.3 and 5, pp. 1-6 | Correlated multi-attempt biometric transaction behavior | Kills the assumption that attempts are iid and that a simple retry policy is new; modality/1:1 endpoint differs. |
| Ma et al., *GBU-Palm*, arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389v1 | Physical print/replay, synchronized RGB/NIR, canonical ROI, held-out environment and attack lineage | Secs. 2-4 and Tables 2-6; reported 21,326 videos/105 people | Physical PAI, RGB/NIR and lineage-controlled PAD | Kills generic physical PAD/NIR/fusion claim; leaves local full-path transaction audit only. Dataset access/release status remains to be confirmed before use. |
| ISO/IEC 30107-3:2023 ed. 2, https://www.iso.org/standard/79520.html | Presentation attack capture/testing/reporting | Official scope/abstract | PAD testing is not overall payment/transaction security | Kills the inference from PAD metric to mock-debit assurance; the paid normative text was not read. |
| Bhilare et al., *A study on vulnerability and presentation attack detection in palmprint verification system*, Pattern Analysis and Applications 21:769-782, 2018, https://doi.org/10.1007/s10044-017-0606-y | Palmprint spoofing and PAD vulnerability | DOI record and GBU-Palm citation chain; full text not independently read in this round | Earlier physical palm PAD neighbor | Supports component collision only; exact full-path overlap remains unresolved. |
| Yin et al., *Learned distributed image compression with decoder side information*, Digital Communications and Networks 11(2):349-358, online 2025-05-08, https://doi.org/10.1016/j.dcan.2024.06.001 | Multi-view images, decoder-side cross-attention/side information | Abstract and bibliographic record; publisher record https://journal.hep.com.cn/dcn/EN/1160605518106517579 | Decoder-side side information and synchronization cost | Kills generic side-information novelty; full methods/failure cases were not accessible, so exact marker endpoint remains open. |
| Diao et al., *TAGIC: Task-Guided Image Communication Framework for Seamless Teleoperation*, INFOCOM Workshops 2024, https://eprints.gla.ac.uk/323353/ | Task-guided source-channel coding under constrained communication | Accepted-version abstract/record | Optimizing task performance rather than image fidelity | Kills generic task-aware communication claim; CARLA simulation does not settle a physical Pi marker audit. |
| *Deep learning-based image compression for wireless communications*, npj Wireless Technology 2025, https://www.nature.com/articles/s44459-025-00019-6 | Progressive learned transmission over a modeled wireless channel | Introduction/contributions, Results, Conclusion and Methods codebook discussion; limitations at the cited conclusion/methods passages | Progressive layers, waiting time and channel-dependent task/quality trade-off | Kills generic progressive-transmission novelty; leaves exact-code, physical-link and full edge-cost evaluation as a bounded endpoint. |
| Guo et al., *Image Compression for Perception and Vision Tasks 3*, ECCV 2024, https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/09009.pdf | Task-aware compression for detection, segmentation, VQA and related tasks | Sec. 1, pp. 1-4; Secs. 4.2-4.3, pp. 10-13 | Task endpoint and rate/performance frontier | Kills generic task-aware compression; large learned systems are not a feasibility baseline for the Pi marker, so simple codec controls remain important. |
| Della Fiore et al., *TFIC: End-to-End Text-Focused Image Compression for Coding for Machines*, EUSIPCO 2025, https://eusipco2025.org/wp-content/uploads/pdfs/0001382.pdf | OCR-aware text-focused compression | Sec. I, pp. 1382-1383; Secs. III-IV, pp. 1384-1385; Sec. V, p. 1386 | Machine-readable text as a compression endpoint and application tuning | Kills text/marker compression as an unoccupied problem; exact-code and physical NoIR side information remain narrower. |
| Raspberry Pi Camera Module 3 product brief and camera software documentation, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief and https://www.raspberrypi.com/documentation/computers/camera_software.html | Camera modes, multi-camera operation and timing/synchronization constraints | Product brief p. 3; camera documentation multi-camera/synchronization sections | Sequential two-camera capture is a physical systems constraint | Leaves exact purchased revisions, pairing witness, registration error, raw mode and timing as feasibility gaps; it does not prove a side-information gain. |

## Strongest simple baseline

### E-BOUND

Use the same frozen matcher, gallery and decision threshold in every arm. Compare: (1) best-quality single frame, (2) random frame, (3) same-session pair consistency, (4) fixed `k` diverse templates at equal storage/search cost, (5) fixed two-session enrollment without adaptive refusal, and (6) conservative refusal/unknown. The proposed charged confirmation policy must be evaluated at equal enrollment minutes, revisit burden, template count, search cost and original eligible-person coverage. Include a third untouched visit for the outcome. A result that only improves conditional accuracy among successfully enrolled people is not sufficient.

### PA-CHARGE

Compare: no PAD; simple VIS quality/score threshold; one fixed VIS recapture; fixed two-shot VIS; fixed VIS+NIR; a simple VIS-only print/display gate; and any proposed selective PAD/NIR action. Freeze gallery, threshold and policy on development people/materials/sessions. Match bona-fide completion, mean/p95 time and measured edge cost. Count every physical start, not only samples that enter PAD. If fixed recapture or fixed two-shot matches the attack/completion frontier, kill the positive policy claim.

### NOIR-SIDEINFO / PROG-RET

The minimum matrix is: full RGB JPEG at fixed qualities, ROI JPEG, WebP if supported, progressive JPEG, fixed low/high two-quality transmission, RGB+NoIR independent transmission, NoIR-as-side-information, and code-only/hash-only transmission as an explicit upper-bound control. Add local-only decode and no-transmission controls. Shape the link with predeclared rate/loss/latency cells. Charge capture, encode, transfer, retransmission, decode, decision and energy. The proposed method must be evaluated using only received bytes and a calibration-frozen decoder; exact payload truth is for scoring, never an input.

## Contrarian result

The strongest contrarian result is that all four candidates can lose without any implementation mistake:

- `E-BOUND` can be dominated by best-quality or fixed multi-template enrollment once revisit cost and refusal coverage are counted. Its positive story can disappear through selection bias before the matcher is compared.
- `PA-CHARGE` can produce no local attack harm because the physical PAI fails capture or ROI, or because simple VIS recapture rejects it. In that case the correct result is a bounded apparatus finding, not a stronger PAD model.
- `NOIR-SIDEINFO` can be dominated by ROI JPEG or code-only transmission after charging the NoIR frame and registration overhead. A static target makes the pilot feasible but also limits external validity.
- `PROG-RET` can be dominated by fixed high-quality JPEG or standard progressive JPEG. Any early layer that appears decisive only because the true code, a post-hoc decoder result or test-set confidence was available is invalid.

The endpoint changes in transaction risk, exact-code success or local latency do not by themselves create a contribution. A method must alter the observation/action mechanism and survive the simple fixed controls at a matched cost.

## Feasibility audit

### Participants, sessions and ethics

- `E-BOUND` needs consenting participants who can attend at least three distinct stages: initial enrollment, optional confirmation/refusal, and untouched later test. It also needs supervised account binding and never-enrolled unknowns. No roster, return rate, ethics approval, retention/deletion policy or minimum session count is confirmed.
- `PA-CHARGE` needs authorization for biometric capture, print/display source creation, storage and deletion, and a safe procedure for targeted presentation attacks. Do not use another person's biometric image/template or claim a realistic victim attack without explicit approval. No real charges or production accounts are permitted.
- All biometric and PAI material must have a lawful dataset/consent basis. Public GBU-Palm access/licensing and suitability for local full-path labels remain unconfirmed; its cropped/video benchmark cannot substitute for local capture-to-debit data.

### Hardware, link and power

- `PA-CHARGE` needs a confirmed camera/illuminator/filter path, safe NIR current and wavelength characterization, stable mount, print/display apparatus and a calibrated power instrument if energy is an endpoint. A NoIR image is not automatically a vein observation.
- `NOIR-SIDEINFO` needs a verified pairing/timing witness for the two cameras, registration calibration, static-target geometry and a receiver that can actually access the side information. Sequential captures are not synchronized merely because they are taken close together.
- `NOIR-SIDEINFO/PROG-RET` need a reproducible local link shaper, packet-loss/retransmission logging and a receiver-side implementation that charges all bytes and computation. A simulated link is acceptable for a bounded benchmark only if its rates/losses and limitations are declared.
- Pi CPU/RAM/storage/thermal behavior and actual codec support must be measured before selecting a learned model. The endpoint should not assume that a codec is cheaper because its transmitted bytes are lower.

### Data and experiment scale

- E-BOUND's later-visit claim is unlikely to be supported by a handful of same-day volunteers. A high frame count does not create independent people or sessions. If later wrong debits are zero, report a clustered upper bound rather than payment assurance.
- PA-CHARGE requires person-, PAI-lineage-, material/device- and session-disjoint held-out cells. A small zero-attack-accept pilot cannot establish a low attack probability; the effective sample size is the number of independent attack episodes, not frames.
- NOIR/PROG can avoid personal data with printed non-personal markers, but must hold out marker content, print/material condition, scene, camera pairing and link cell. A single static marker can only support a finite marker result.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Same-session quality and recapture are established acquisition controls, and FTE/coverage matter. | [K] | Tabassi and Grother, NIST IR 7544, 2008-11, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | Secs. 2.1.1-2.1.3, printed pp. 18-21/PDF pp. 19-22; Sec. 5.1, printed pp. 37-40 | NIST report is not a palm-specific transaction study. |
| Mobile palm ROI, quality reject/recapture, enrollment and open-set 1:N are established. | [K] | Palm-ID, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111v1 | Secs. II-F/G, III-B/C/D, IV-A/B, V | Its timing/platform and endpoint differ from Pi mock debit. |
| Long-term representative palm templates/update are established. | [K] | Chen et al., IEEE Access 7:145082-145094, 2019, https://doi.org/10.1109/ACCESS.2019.2945064 | Secs. II-III and IV, pp. 145083-145094 | Post-enrollment updating is not the exact charged confirmation protocol. |
| Multi-attempt biometric transactions are non-iid and have a later-session component. | [K] | Czajka and Bowyer, BTAS 2015, https://doi.org/10.1109/BTAS.2015.7358797 | Secs. 1-4.3 and 5, pp. 1-6 | Iris 1:1, not unknown-gallery palm debit. |
| Physical RGB/NIR print/replay PAD and lineage/environment controls are established. | [K] | Ma et al., GBU-Palm, arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389v1 | Secs. 2-4; Tables 2-6 | Dataset access/release and local full-path transfer remain [GAP]. |
| PAD testing scope is distinct from overall transaction/payment assurance. | [K] | ISO/IEC 30107-3:2023 ed. 2, official record, https://www.iso.org/standard/79520.html | Official scope/abstract only | Normative full text was not obtained. |
| Decoder-side side information and synchronization costs are established. | [K] | Yin et al., D-CAN 2025, https://doi.org/10.1016/j.dcan.2024.06.001 | Abstract; Vol. 11(2), pp. 349-358 | Full methods/failure analysis not accessible in this round. |
| Task-guided communication is established. | [K] | Diao et al., TAGIC, INFOCOM Workshops 2024, https://eprints.gla.ac.uk/323353/ | Accepted-version abstract/record | CARLA simulation, not physical Pi marker. |
| Progressive transmission and waiting-time trade-offs are established. | [K] | *Deep learning-based image compression for wireless communications*, npj Wireless Technology 2025, https://www.nature.com/articles/s44459-025-00019-6 | Introduction/contributions; Results; Conclusion; Methods codebook discussion | Kodak/Rayleigh setting; edge timing and broader channel limitations remain. |
| Task-aware/OCR-aware compression has already used task endpoints. | [K] | Guo et al., ECCV 2024, https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/09009.pdf; Della Fiore et al., EUSIPCO 2025, https://eusipco2025.org/wp-content/uploads/pdfs/0001382.pdf | Guo Sec. 1 pp. 1-4 and Secs. 4.2-4.3 pp. 10-13; Della Fiore Secs. I, III-V, pp. 1382-1386 | Exact marker/NoIR endpoint remains a finite evaluation gap only. |
| Camera pairing/timing and multi-camera constraints are real feasibility variables. | [K] | Raspberry Pi Camera Module 3 product brief, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief; camera software docs, https://www.raspberrypi.com/documentation/computers/camera_software.html | Product brief p. 3; multi-camera/synchronization sections | Exact purchased revision and timing witness are unresolved. |
| Direct full-path Pi transaction effects and lawful local data access are available. | [GAP] | Local charter and candidate register, 2026-09-24 | `00-project-charter.md` current route and `01-candidate-register.md` rows 12-13, 95-96 | No measured all-start transaction trace, longitudinal roster, attack authorization or side-information pilot was supplied here. |

## Queries and failed searches

Queries run/rechecked on 2026-09-24:

- `biometric enrollment best quality multiple templates longitudinal palmprint later session open set transaction`
- `palmprint template selection multiple sessions representative template 2019 full paper`
- `biometric multi-attempt transaction correlated attempts later session retry Bowyer Czajka`
- `physical palmprint presentation attack detection print replay RGB NIR 2026 GBU-Palm`
- `palmprint PAD physical print display transaction open set 1:N mock debit`
- `palmprint NIR vein presentation attack detection 2024 2025 full paper`
- `decoder-side side information image compression multi-view constrained devices 2025`
- `task-guided image communication exact task endpoint bandwidth 2024`
- `progressive image transmission early stopping machine vision latency bytes 2024 2025`
- `OCR-aware image compression coding for machines exact text endpoint 2025`
- `Pi Camera Module 3 dual camera synchronization request frame timestamp raw JPEG pairing`

No search verified a single primary paper containing the exact combination of: (a) charged cross-visit enrollment, later live open-set palm mock debit and original-eligible-person denominator; (b) physical PAI through Pi ROI/1:N/mock debit; or (c) Pi RGB/NoIR side information or progressive exact-code stopping with matched end-to-end cost. These are retrieval gaps, not evidence of novelty.

Unresolved or incomplete sources: full GBU-Palm release/license and local transferability; full PVASD and Fan et al. methods; paid ISO/IEC 30107-3 normative clauses; complete citation chains after the 2025/2026 side-information and progressive-transmission papers; exact purchased Camera Module 3 revision/raw-mode/timing behavior; lawful local participant/PAI access; and a real Pi frame-pair/link/power trace.

## Decision

- `E-BOUND`: **HOLD/PIVOT** as a three-stage longitudinal audit only. Do not promote an enrollment method or transaction-risk improvement until a third untouched visit, original eligible-person denominator and equal-cost baselines are feasible. Kill the positive claim if best-quality, fixed multi-template or refusal dominates.
- `PA-CHARGE`: **HOLD/PIVOT** after the Phase 1 MVP and ethics/apparatus gate. Do not call it a PAD method, palm-vein method or payment-security result. Kill the positive claim if attacks do not reach the path, fixed VIS recapture/two-shot matches, or lineage/permission controls fail.
- `NOIR-SIDEINFO`: **PIVOT** to a finite non-personal benchmark only. Kill the side-information claim if NoIR overhead, registration or ROI/code-only controls dominate.
- `PROG-RET`: **PIVOT** to a stopping/control experiment only. Kill the positive protocol claim if standard progressive JPEG, fixed high-quality JPEG, code-only or oracle-free confidence cannot meet the same false-retain constraint.

No candidate is promoted. The current Palm Payment MVP should proceed as engineering work; these candidates require their stated feasibility gates before any thesis framing.

PIVOT
