# Divergence Packet: 2026-09-24 targeted enrollment, action risk, and progressive retention

## Decision investigated

This packet investigates three deliberately narrow directions requested for the 2026-09-24 divergence round:

1. `E-BOUND`: whether an enrollment acceptance/refusal decision made across visits can reduce later full-transaction failure at the same user cost.
2. `PA-CHARGE`: whether a physical presentation to live ROI, open-set 1:N, and mock debit can be evaluated as one action-risk and operational-cost endpoint.
3. `NOIR-SIDEINFO` / `PROG-RET`: whether a constrained link can use an auxiliary observation or progressive transmission to change `retain / unknown / reacquire` decisions.

The decision is intentionally about whether these are defensible research boundaries, not whether the Pi 5 Palm Payment MVP should be delayed. The MVP remains an engineering route. No global novelty claim is made.

## Search boundary

I first read `AGENTS.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, `research/active/39-round-24-cross-mechanism-reconciliation.md`, `research/ops/agent-divergence.md`, and the overlapping archive README. I then read the relevant local historical logs:

- `research/archive/2026-08-edge-sensing/log/27-palm-payment-acceptance-boundary-log.md`
- `research/archive/2026-08-edge-sensing/log/31-palm-id-mobile-system-reading-log.md`
- `research/archive/2026-08-edge-sensing/log/12-pad-protocol-reading-log.md`
- `research/archive/2026-08-edge-sensing/log/15-vis-nir-boundary-log.md`
- `research/archive/2026-08-edge-sensing/log/16-dynamic-terms-boundary-log.md`
- `research/archive/2026-08-edge-sensing/log/24-authentication-boundary-and-release-metrics-log.md`

The current register and prior packets already audit generic retry policy, gallery calibration, quality recapture, active illumination, and adaptive sensing. This packet therefore does not repeat `TRIG-LEAK` or `PART-ACT`.

The web/metadata search was bounded to primary papers and official standards/pages available on 2026-09-24. Queries are listed below. Some newly found arXiv records were only metadata/abstract leads; they are marked `[GAP]` and are not load-bearing evidence.

## Recent-paper limitation map

| Family | Direct work inspected or located | What it actually establishes | Boundary for this round |
| --- | --- | --- | --- |
| Mobile palm recognition and enrollment | Grosz, Godbole and Jain, *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv:2401.08111v1 (2024-01-16), HTML sections on enrollment, 1:1, 1:N and experiments; local reading log | A real mobile pipeline has enrollment, local templates, quality/rejection, time-separated sessions and open-set reporting. Its endpoint is recognition performance and runtime, not a later physical transaction action. | `E-BOUND` must make the enrollment decision occur before a disjoint later transaction test and must report all eligible presentations, not only successful enrollments. “Quality gate improves recognition” is occupied. |
| Enrollment/acquisition control | NIST IR 7544, *Using Quality Metrics to Ensure the Integrity of Biometric Data*, 2008, §§2.1.1-2.1.3 and 4-6 | Acquisition and enrollment quality controls, recapture and rejection are established operational controls. | `E-BOUND` cannot claim a new quality score or acceptance rule. The only possible distinction is a longitudinal decision endpoint: later complete transaction failure at matched enrollment effort. |
| Open-set/template and cross-domain palm recognition | PalmBridge, arXiv:2601.20351v1 (2026-01-28), metadata/abstract lead; X-Palm, arXiv:2606.08437v2 (2026-06-07), metadata/abstract lead; Palm-ID above | Open-set and cross-domain palm matching are active primary topics. Exact paper sections and artifacts were not fully re-read in this bounded round, so these are collision leads rather than proof of a specific endpoint. | A new embedding or cross-domain matcher is out of scope. `E-BOUND` must freeze the matcher and vary only an enrollment policy. |
| Palm presentation attack detection | GBU-Palm, *A Multimodal Video Dataset and Benchmark for Palm Presentation Attack Detection*, arXiv:2608.14389v1 (2026-08-14), §§1-4 and tables as recorded in the prior local audit; ISO/IEC 30107-3:2023 public scope | Recent work evaluates bona-fide/attack presentations, multimodal video and cross-domain PAD, with APCER/BPCER/ACER-style endpoints. ISO limits PAD to presentation attacks at the capture device; it is not a whole transaction authorization standard. | `PA-CHARGE` must report PAD-side errors separately from target-match and final mock-debit errors. A new PAD classifier or a claim of “secure payment” is a collision. |
| End-to-end biometric release boundary | NIST SP 800-63B-4 biometric guidance, current public text; ISO/IEC 30107-3:2023 public abstract | Biometric comparison, PAD, endpoint integrity, fallback and authorization are different layers. A local match does not prove secure authorization or injection resistance. | The endpoint can be a useful evaluation protocol only if it explicitly freezes the claim, matcher threshold, PAD gate and idempotent mock debit. It cannot be presented as production payment security. |
| Progressive inference and communication | *Utility-Aware Progressive Inference over UDP Packet Blocks for Emergency Communications*, arXiv:2605.09933v1 (2026-05-11), abstract/metadata; *Adaptive Early Exiting for Collaborative Inference over Noisy Wireless Channels*, arXiv:2311.18098v1 (2023-11-29), abstract/metadata; recent progressive edge records searched through arXiv API | Progressive packets/early exit optimize task utility, communication and noisy-channel cost. The exact palm ROI action endpoint and a physical auxiliary observation are not established by the metadata leads. | `PROG-RET` cannot claim progressive transmission itself as new. It must beat prefix/no-prefix, fixed-quality, retransmit and always-reacquire controls at equal bytes/energy and use a frozen action rule. |
| VIS/NIR terminology | Fei et al., *Learning Frequency-Aware Common Feature for VIS-NIR Heterogeneous Palmprint Recognition*, DOI 10.1109/TIFS.2024.3441945; local historical reading log | Cross-spectrum matching is an identity-recognition problem, not automatically liveness, PAD or response verification. | `NOIR-SIDEINFO` must define what the NoIR frame observes and how it changes a decision; “RGB+NoIR” or “more channels” is not a contribution. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| `E-BOUND` | A site enrolls a person once, then later accepts a physical palm for a mock transaction. A weak enrollment can cause repeated owner refusal or an unsafe false match; extra enrollment visits cost time and exclude people. | Under a preregistered enrollment budget, an `accept / request second visit / refuse` policy using only prior visits can reduce the later disjoint full-transaction failure rate, or its expected operational loss, relative to best-single-capture, same-session multi-template, fixed-quality, and unconditional-accept controls at matched user effort. Inputs: prior raw captures, ROI/quality/matcher scores, visit/session ID and enrollment cost. Action: enroll, request another visit, or refuse. Later test uses frozen templates and a disjoint session. | NIST IR 7544 quality acquisition/enrollment controls; Palm-ID's enrollment, quality rejection, time-separated sessions and open-set modes. | If best-quality or fixed multi-template controls match the later failure frontier; if the second visit is also used to measure the outcome; if enrollment selection/attrition confounds the effect; or if unknown-person data are absent, kill the positive claim. | Medium. VIS capture, consented repeat visits, frozen matcher, person/session blocked splits and an enrollment-cost log are feasible. Longitudinal availability and enough identities are the hard gates. |
| `PA-CHARGE` | A physical presentation can fail at capture, ROI, recognition, PAD or release. Reporting only classifier accuracy hides whether an attack reaches the consequential mock debit or whether legitimate users are burdened by gates. | For a fixed claim and frozen threshold, the full chain can estimate `IAPMR = PAD/capture gate pass AND target match AND debit`, bona-fide completion, wrong-identity release, unknown rate, retry count and capture-to-action time. A specified risk gate improves the held-out action-cost frontier over matcher-only and PAD-only controls at matched bona-fide cost. | GBU-Palm and ISO 30107-3 occupy PAD measurement; Palm-ID occupies mobile recognition; NIST separates biometric comparison, PAD, fallback and authorization. | If the experiment has no authorized physical attack set, no independent target claim, too few persons/sessions, or a simple stricter threshold matches the frontier, kill the positive method claim. Keep the endpoint as a bounded audit/protocol if denominators are complete. | Medium-low for a positive thesis; high for an evaluation appendix. Requires ethics/attack authorization, material/session holdout, a mock debit ledger and exact stage trace. |
| `NOIR-SIDEINFO` | On a constrained edge link, the first VIS observation may be ambiguous. A low-cost auxiliary NoIR/IR observation could prevent a bad retain or unnecessary reacquire, but an extra frame costs capture energy and link time. | At fixed end-to-end bytes and energy, a frozen policy that requests/uses a named auxiliary observation reduces expected action loss `L(reacquire, unknown, wrong retain)` over VIS-only scalar quality, fixed second capture, and always-reacquire controls on held-out physical cells. The auxiliary frame must have a measurable information condition, not merely a different model input. | Fei et al. cross-spectral recognition; prior workspace adaptive sensing/IR audits; progressive and early-exit communication papers. | If NoIR is only correlated quality, if an equal-cost VIS second frame matches it, if command/actual frame state is unverified, or if the decision is reproduced by a scalar quality threshold, kill the side-information claim and retain a finite null. | Low-medium. Hardware path and actual NoIR/IR state, calibrated timing, power/bytes and independent scene labels are required. The current December VIS MVP does not yet provide this apparatus. |
| `PROG-RET` | A partial ROI or compressed feature arrives before the full payload. The edge should retain, request another packet, or reacquire without waiting for a full image; a wrong early retain could debit the wrong mock account. | Given a fixed packet budget and deadline, a progressive payload policy using prefix observations and an explicit abstain rule improves expected transaction loss and deadline completion over full-payload-only, fixed JPEG-quality, random truncation, and retransmit controls. The claim is about a decision frontier, not reconstruction PSNR. | Utility-aware progressive inference and adaptive early-exit over noisy channels; JPEG/RAW and edge-serving candidates already audited locally. | If the same result is obtained by a fixed quality/size threshold, if prefix packets contain label leakage unavailable in deployment, if late packets are not charged, or if full-payload-only dominates, kill the positive claim. | Medium as a simulation/controlled link pilot; low as the primary Palm thesis because the current local payment path is physical capture first and does not yet have a justified constrained-link owner. |
| `OFFSYNC-RET` (negative path) | With missing packets and no trusted witness, the edge must distinguish “the unseen suffix would change the identity/action” from “the suffix is irrelevant.” An unsafe retain or needless reacquire has opposite harms. | There exist two worlds with identical observed prefix, metadata, bytes, and local state but opposite correct final actions. Therefore no policy using only those observations can guarantee the correct `retain / unknown / reacquire` decision without a side-information or freshness witness. | Standard indistinguishability boundary; progressive inference papers assume a task model and channel observations rather than proving hidden physical truth. | Construct paired worlds with identical prefix and metadata but different suffix/identity/action labels. If a policy claims a guarantee, the pair is a direct counterexample. | High as a small negative-control experiment; useful even if `NOIR-SIDEINFO` and `PROG-RET` are killed. |

## Candidate-specific distinction checks

### `E-BOUND`: not just enrollment quality control

The positive distinction is temporal and endpoint-specific, not algorithmic. A quality-control paper asks whether a capture is acceptable now; this candidate asks whether a decision made before the transaction predicts or changes failure on later, disjoint, full physical transactions under a declared enrollment cost. To make that distinction real:

- enrollment sessions and transaction sessions must be separated by date or controlled visit;
- all eligible enrollment starts, refusals and dropouts must be counted;
- the enrollment policy must not inspect the later test session;
- the matcher, gallery representation and transaction rule must be frozen before the held-out test;
- the primary outcome must include capture/ROI/1:N/unknown/wrong-identity/mock-debit stages, not only TAR/FAR.

The strongest negative result is equally important: if best-quality, same-session multi-template and a second-visit confirmation have indistinguishable later failure at matched effort, then the proposed longitudinal decision is not identifiable as a contribution. A further confound is informative missingness: people who refuse a second visit may be systematically harder to enroll, so a naive enrolled-only comparison can falsely attribute selection to the policy.

### `PA-CHARGE`: not just PAD

The only defensible research object here is a complete, predeclared release-risk evaluation. PAD metrics remain separate. For every presentation, record:

`presentation_id, claimed_identity, person/PAIS/material/session, capture, live_ROI, matcher_score, PAD_gate, open_set_decision, final_action, debit_idempotency_result, retry_count, stage_times, energy/bytes`.

The target endpoint is not “accuracy” but an action ledger. The primary attack quantity is target-match-and-release acceptance, while bona-fide completion and p95 interaction time measure the cost of conservative gating. A simple threshold sweep and matcher-only baseline are mandatory. If no realistic, authorized physical attack population exists, the work is a protocol/measurement audit, not a PAD thesis.

### `NOIR-SIDEINFO` versus `PROG-RET`

These should not be merged prematurely. `NOIR-SIDEINFO` changes the observation model by adding a physically distinct auxiliary observation; `PROG-RET` changes the communication schedule while holding the underlying observation fixed. A NoIR frame that is merely another image in a classifier is not side information. A progressive prefix that is only a smaller JPEG is not a new decision mechanism.

The minimum separation test is a 2x2 design:

| Observation | Delivery | Purpose |
| --- | --- | --- |
| VIS only | full | baseline recognition/action |
| VIS only | progressive prefix/full | communication effect |
| VIS + named NoIR/IR observation | full | observation effect |
| VIS + named NoIR/IR observation | progressive | interaction, only if both main effects survive |

All arms must charge capture, encode, transmit, decode and reacquire cost. The actual illumination/frame state must be logged independently of software commands. Without this design, an apparent gain can be assigned equally to more pixels, more bytes, a second chance, or a different threshold.

## Top two formalizations

### 1. `E-BOUND`

- `[D]` Decision-maker: enrollment service/operator choosing `accept`, `request second visit`, or `refuse` for an identity claim.
- `[A]` Allowed actions: collect one additional consented visit, freeze a template set, or refuse/route to manual fallback. No later test outcome may feed back into enrollment.
- `[T]` Time structure: enrollment visit(s) at `t0/t1`; later transaction sessions at `t2+`, person-blocked and session-blocked. The enrollment budget is fixed before testing.
- Observable outcome: full-transaction failure and its stage attribution; secondary metrics are bona-fide completion, unknown, wrong identity, mock debit, attempts, time and enrollment burden.
- Counterexample: two enrollment policies yield equal quality/score distributions and equal later action outcomes, or a hidden enrollment difficulty variable drives both refusal and later failure. This defeats a causal positive claim.
- Negative-result value: a bounded result that cross-visit enrollment acceptance does not improve later action risk over simple controls, or that the effect cannot be identified under available sessions, is useful for stopping an expensive longitudinal claim.

### 2. `PROG-RET` with `NOIR-SIDEINFO` as an interaction arm

- `[D]` Decision-maker: the edge transaction controller deciding `retain`, `unknown`, or `reacquire` before a hard action deadline.
- `[A]` Allowed actions: accept the current evidence, request/receive a named next packet or auxiliary observation, or terminate to manual fallback. The policy cannot access the hidden suffix or future ground truth.
- `[T]` Time/resource structure: packet arrival times and bytes are logged under a replayable link trace; auxiliary capture and power are charged; the action deadline is fixed.
- Observable outcome: action loss, deadline completion, wrong-identity release, unknown/reacquire burden and energy/bytes. Recognition quality or PSNR is secondary.
- Counterexample: identical prefix/link state and metadata with two different hidden suffixes requiring opposite actions. This proves that a side-information-free guarantee is impossible.
- Negative-result value: a paired-world non-identifiability result or a finding that matched-cost VIS-only second capture dominates NoIR/progressive arms closes the mechanism cleanly.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Mobile palm systems already include enrollment, local templates, quality/rejection, 1:1 and open-set 1:N modes. | [K] | Grosz, Godbole and Jain, *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111 | HTML sections describing system modes, mobile pipeline, datasets and experiments; local reading log `31-palm-id-mobile-system-reading-log.md` | Recognition/runtime endpoint; no later transaction debit endpoint, PAD or Pi profile. |
| Acquisition and enrollment quality/rejection are established biometric controls. | [K] | NIST IR 7544, 2008, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf | §§2.1.1-2.1.3 and 4-6, pp. 2-6 (PDF pagination as cited in local prior packet) | General guidance, not a palm-specific causal result or FYP performance target. |
| Recent palm PAD work evaluates presentation attacks and cross-domain/multimodal PAD metrics, not final mock-debit risk. | [K] | GBU-Palm, *A Multimodal Video Dataset and Benchmark for Palm Presentation Attack Detection*, arXiv:2608.14389v1, 2026-08-14, https://arxiv.org/html/2608.14389 | §§1-4 and tables; prior local validation packet records the binary/canonical-ROI endpoint | Do not infer target-match IAPMR or Pi action risk from PAD numbers. Exact artifact/license and all implementation details remain [GAP]. |
| PAD is a capture-device presentation-attack scope, not a whole authorization or endpoint-integrity result. | [K] | ISO/IEC 30107-3:2023, https://www.iso.org/standard/79520.html | Public abstract/scope only | Full standard is not publicly available in this workspace; do not claim conformance. |
| Biometric comparison, PAD, fallback and authorization are separate layers. | [K] | NIST SP 800-63B-4, current public guidance, https://pages.nist.gov/800-63-4/sp800-63b.html | Biometric, PAD, local-comparison, fallback and endpoint-integrity portions of the public text; exact subsection numbering may vary by rendered page | Digital identity guidance, not a payment deployment approval or local legal requirement. |
| VIS-NIR matching is not automatically liveness or response verification. | [K] | Fei et al., *Learning Frequency-Aware Common Feature for VIS-NIR Heterogeneous Palmprint Recognition*, DOI 10.1109/TIFS.2024.3441945, 2024, https://doi.org/10.1109/TIFS.2024.3441945 | Official abstract and problem definition; local `15-vis-nir-boundary-log.md` | Full text/artifacts were not available in the prior read; no efficiency or deployment numbers are reused. |
| Open-set/cross-domain palm recognition is an active direct-neighbor family. | [K]/[GAP] | PalmBridge, arXiv:2601.20351v1, 2026-01-28, https://arxiv.org/abs/2601.20351; X-Palm, arXiv:2606.08437v2, 2026-06-07, https://arxiv.org/abs/2606.08437 | Metadata/abstract collision scan; full sections not re-read in this bounded round | Leads only; no central claim relies on their uninspected details. |
| Progressive inference/early exit already treats communication and task utility as research endpoints. | [K]/[GAP] | *Utility-Aware Progressive Inference over UDP Packet Blocks for Emergency Communications*, arXiv:2605.09933v1, 2026-05-11, https://arxiv.org/abs/2605.09933; *Adaptive Early Exiting for Collaborative Inference over Noisy Wireless Channels*, arXiv:2311.18098v1, 2023-11-29, https://arxiv.org/abs/2311.18098 | Abstract/metadata collision scan; full PDF sections were not re-read because the bounded round stopped before artifact extraction | Sufficient to reject a generic “progressive edge inference is new” claim; exact palm applicability remains [GAP]. |
| A side-information-free retain guarantee can fail under paired worlds with identical observations but opposite hidden suffix/action truth. | [C]/[KILL] | Formal paired-world construction in this packet, grounded in the observation boundary of progressive inference | Formalization above; no external theorem is needed for the finite counterexample | This is a negative identifiability argument, not evidence that every practical policy fails. |

## Queries and failed searches

Queries run on 2026-09-24 included:

- `palmprint enrollment quality longitudinal session acceptance refusal transaction failure primary paper 2024 2025`
- `biometric enrollment quality control re-enrollment longitudinal verification transaction attempts primary study 2024 2025`
- `palmprint presentation attack detection physical presentation RGB NIR transaction endpoint primary paper 2025 2026`
- `progressive transmission side information edge vision reject unknown reacquire primary paper 2024 2025`
- `site:arxiv.org palmprint enrollment quality recapture open-set 1:N mobile Palm-ID 2024`
- `progressive inference edge vision communication`, `side information edge image`, and arXiv API searches for recent `palmprint`, `enrollment`, `presentation attack`, `progressive`, and `early exit` records.

The search found no directly verified primary paper in the inspected material that measures the exact endpoint “cross-visit enrollment accept/refuse -> later physical palm transaction failure including mock debit.” That absence is `[GAP]`, not a novelty proof. It also found no verified primary paper connecting a physical palm PAD benchmark directly to a target-match-and-release debit endpoint on a Pi. Recent progressive inference work is a direct collision for the generic communication mechanism, but its task and observation model differ from the proposed palm decision endpoint; full-text audit is still required before any stronger statement.

Unresolved uncertainties:

- lawful access to enough independent enrolled and unknown people, repeat visits and session-separated captures;
- whether the actual Pi payment executable has a stable live ROI, open-set 1:N and idempotent mock-debit trace;
- availability and ethics approval for physical PAIS materials and attack sessions;
- actual NoIR/IR hardware state, timing, energy and whether it supplies information beyond a second VIS capture;
- a real link owner and operational reason to impose packet loss/deadline constraints;
- exact full-text sections, code, data and licenses for PalmBridge, X-Palm and the progressive-inference leads.

## Decision

`E-BOUND`: **HOLD**. It is the most distinct of the three only as a longitudinal evaluation question, not as a new enrollment-quality method. It should advance only after the MVP can produce a frozen all-start stage trace and the team can obtain consented repeat visits with enough person/session separation. The primary stopping rule is equality with best-quality, multi-template and refusal controls or a demonstrated selection/identifiability failure.

`PA-CHARGE`: **HOLD as a bounded action-risk audit; KILL as a new PAD method**. The endpoint is valuable because it joins stages that the direct PAD and recognition papers report separately, but the contribution is a protocol/measurement result unless a preregistered risk policy beats strong threshold and PAD controls. No positive security or payment claim is permitted.

`NOIR-SIDEINFO` / `PROG-RET`: **HOLD/PIVOT**. Keep the observation and communication mechanisms separate. `PROG-RET` is likely a replication or application of progressive task communication unless the matched-cost action frontier survives. `NOIR-SIDEINFO` is viable only with independently verified physical side information and a VIS-second-capture control. `OFFSYNC-RET` is the required negative path if the hidden suffix is not identifiable.

Overall: **PIVOT**. No candidate is promoted. The next evidence is the frozen physical transaction trace, followed by a small, preregistered E-BOUND pilot if longitudinal access exists; do not buy NoIR/IR or link hardware for a thesis claim before those gates pass.

PIVOT
