# Validation Audit: 2026-09-24 PALM-STOP

## Decision investigated

**Decision under test:** whether `PALM-STOP` should be promoted as a Palm-only edge-computing research direction.

**Candidate:** Given a real Palm video or continuous VIS capture, stop online and execute open-set 1:N / `unknown` / mock action when the current frame or tracklet has sufficient quality, matcher score/margin, and temporal agreement. The proposed claim is that, at a fixed false-accept/unknown ceiling, equal capture opportunity, and equal energy, the stopping policy completes safe decisions earlier than fixed-N frames, a best-frame oracle, fixed recapture, and always-continue.

**Audit date:** 2026-09-24.

**Current decision:** The positive method claim is **KILL-leaning**. The Palm-specific exact endpoint was not found in the inspected sources, but the mechanism is occupied by Palm quality/frame-selection work and generic sequential video inference. The only defensible residual is `PALM-STOP-NULL`: a finite risk-latency/energy boundary or non-identifiability audit showing when fixed-frame and online-stop policies cannot be distinguished from marginal stage statistics or when safe stopping is not identifiable from present observations.

## Claim under test

Let an episode contain a continuous VIS capture stream \(X_{1:T}\), an enrolled gallery \(G\), an open-set matcher, and a mock action endpoint. At stopping time \(\tau\), the system emits one of `accept(id)`, `unknown`, or `continue`/`recapture`, followed by an action only for an independently authorized accepted identity.

The positive claim would require all of the following:

1. At a predeclared false-accept and unknown operating ceiling, online stopping reduces capture-to-decision time and/or energy.
2. The reduction survives fixed-N, fixed recapture, always-continue, scalar quality, score/margin-only, and best-frame-oracle controls at matched capture opportunity.
3. The policy uses only information available at time \(t\); no future-frame, full-tracklet, post-action, or test-identity information may enter the stop decision.
4. The effect holds on person-held-out and session-held-out episodes, including genuine enrolled users and independently sampled unknown people.
5. The endpoint is not merely matcher accuracy: the final measure includes all eligible starts, stage reachability, `unknown`, correct/wrong identity, action authorization, action result, idempotency, latency, and charged energy.

The negative claim `PALM-STOP-NULL` is narrower: under a declared capture process, show either that (a) two stopping policies have indistinguishable terminal action risk at the available sample size, (b) the current quality/score/margin/temporal observations do not identify future-safe stopping without an additional reference or intervention, or (c) any latency/energy benefit disappears against a matched fixed-recapture policy.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
|---|---|---|---|
| Component collision | The Palm-specific components are already present separately and in near-combination: MPW-180 is collected as complete videos, resamples timestamps, extracts ROIs, and selects one maximum-Laplacian-variance frame per temporal window; Palm-ID includes on-device ROI, a learned quality estimator, and optional rejection/re-capture; a 2025 quality-based context-switching paper dynamically selects a recognition method from image-quality measures. Generic video work already covers dynamic frame selection, conditional early exit, and stop/forward inference. | The inspected Palm papers do not make an online stop decision for open-set 1:N followed by an action endpoint under a fixed false-accept/unknown ceiling. | High for mechanism collision; medium for exact Palm endpoint. |
| Exact-claim collision | FrameExit learns gates that determine the earliest sufficiently reliable point in a video; Stop or Forward sequentially estimates frame usefulness and uses early termination for action recognition; AFNet dynamically selects frames and models temporal redundancy. These occupy the general “use current temporal evidence to spend less compute/frames” claim. Palm-ID and MPW occupy quality-gated capture and frame curation, respectively. | No inspected source combines Palm open-set identification, an online `accept/unknown/continue` decision, an independently authorized mock action, and equal-capture-opportunity risk/energy comparison. This is an application/endpoint distinction, not evidence of a new stopping algorithm. | Medium. Exact absence is not a novelty proof. |
| Boundary and impossibility | Present-frame quality and margin are not sufficient statistics for unseen future motion, blur, hand pose, illumination, or an impostor. Best-frame selection is noncausal unless the entire tracklet is already captured. A stop policy tuned on the same videos can trade away unknown/wrong-action risk while appearing faster. Terminal action risk also depends on reachability and authorization, not just per-frame FAR/FRR. | A finite, preregistered all-start episode study could still establish a useful Palm-specific boundary: when a matched fixed-N or fixed-recapture control dominates, or when marginal frame metrics cannot identify terminal action risk. | High for the negative path; low for a general safe-stopping guarantee. |

## Assumption and identification audit

### 1. Future information and selection leakage

`PALM-STOP` must distinguish three different operations:

- **Online stop:** decide after frame \(t\) using only frames and matcher state through \(t\).
- **Tracklet selection:** wait for a bounded tracklet, then choose a frame or subset. This is not earlier stopping and charges the full wait/capture cost.
- **Best-frame oracle:** inspect the complete episode and report the best frame. It is a useful upper bound only, not a deployable policy.

The MPW-180 paper's windowed maximum-sharpness rule is explicitly post-hoc dataset curation. Reusing it as an online baseline without charging the window look-ahead would leak future information. The same problem appears if temporal agreement is computed over the eventual full tracklet, if the maximum score over all frames is used to set a stop threshold, or if a test episode is selected because it eventually succeeds.

### 2. Person and session split

Random frame or random-window splits are invalid for this question because adjacent frames share identity, pose, illumination, device, and motion state. At minimum:

- person-disjoint train/validation/test identities;
- session-disjoint test episodes, with the later session untouched until evaluation;
- no frames from one video in multiple partitions;
- unknown people absent from enrollment and held out by person and session;
- threshold and stopping-policy selection frozen before the final test session.

Even a video-level split is insufficient for the intended cross-session claim if the same person appears in enrollment and test through near-duplicate capture conditions. If only one visit is available, the result is a within-session capture study, not cross-session Palm recognition.

### 3. Unknown labels and false-accept ceiling

An open-set `unknown` label needs an independent label: the presented person is not enrolled, and the action authorization is false. A low matcher score is not itself an unknown ground truth. The test set must contain:

- enrolled genuine presentations;
- non-enrolled impostor/unknown presentations;
- repeated genuine and unknown sessions under the same capture opportunity;
- a predeclared operating point or confidence interval for false accept and unknown rate.

If unknown persons are scarce, a statement such as “safe at fixed false accept” will have very wide uncertainty. The study must report exact counts and bounds rather than claiming a meaningful rare-error improvement from zero observed wrong actions.

### 4. Action endpoint and reachability

The action endpoint must be a real executable mock action with an idempotent account transition, not a logged “would accept” bit. Each all-start episode must record whether it reached capture, valid ROI, matcher, `unknown`/identity, authorization, and action. A wrong identity that never reaches an authorized action is not a wrong debit; a matcher error and an action error cannot be multiplied without measured dependence and reachability.

If the action is not independently authorized, the endpoint collapses to matcher evaluation. If the action is simulated only after manually selecting successful frames, it is post-selection and cannot support the claim.

### 5. Energy and capture-opportunity accounting

Equal energy must include camera-on time, preview/stream acquisition, frame transfer, ROI extraction, matcher execution, memory, storage, recapture, and stop-policy overhead. Equal capture opportunity must include the time during which a user is presenting the palm, not only the number of frames eventually passed to the matcher. A policy that stops after one frame but leaves the camera running until UI confirmation has not demonstrated an energy saving.

### 6. Temporal agreement is not an independent oracle

Consecutive agreement may reflect temporal redundancy rather than independent evidence. If the same hand pose produces three nearly identical frames, a two-of-three agreement rule can appear confident without adding independent information. The audit must report effective temporal separation, frame timestamps, motion/blur conditions, and whether agreement is computed before or after ROI normalization. A temporal feature learned from labels or future frames also creates a policy-specific leakage channel.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
|---|---|---|---|---|
| Sünnetci et al., *A Video-Based Mobile Palmprint Dataset and an Illumination-Robust Deep Learning Architecture for Unconstrained Environments*, Applied Sciences 15(21):11368, published 2025-10-23, [official article](https://www.mdpi.com/2076-3417/15/21/11368) | Complete smartphone palm videos; timestamp-aware resampling; ROI extraction; windowed maximum Laplacian-variance selection; manual quality curation; PalmWildNet | Mobile unconstrained Palm recognition on MPW-180; quality and generalization evaluation | Direct Palm video, temporal redundancy, quality-based frame selection, and device/illumination variation. Selection is offline and dataset-oriented, not online action stopping. | Kills “Palm video plus quality/frame selection is itself new.” Leaves open only a strictly causal stopping/action endpoint, if raw uncurated video and action labels are available. |
| Grosz et al., *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv:2401.08111v1, 2024-01-16, [official preprint](https://arxiv.org/abs/2401.08111) | Single mobile Palm image; ROI/keypoints, enhancement, quality estimation, matching; optional rejection/re-capture; on-device pipeline | Cross-database and time-separated Palm verification/identification, latency and template size | Directly occupies Palm quality gating, mobile deployment, rejection and re-capture. It does not test a continuous online stop policy or action endpoint. | Kills a claim that score/quality-gated mobile recapture is a new mechanism. Leaves a bounded causal sequential evaluation only. |
| Guerrache & Haddadou, *A Quality-Based Context-Switching Framework for Palmprint Recognition*, Multimedia Tools and Applications 84, 21991-22008, online 2024-08-01 / issue 2025, DOI `10.1007/s11042-024-19867-5`, [publisher record](https://doi.org/10.1007/s11042-024-19867-5) | Palm image quality measures; SVM context-switching among recognition methods | Accuracy/computational-cost trade-off on PolyU-II | Direct quality-conditioned compute/action selection within Palm recognition. | Kills generic “quality selects the cheaper/safe path” novelty. Leaves only a different sequential observation/action endpoint, which must beat a fixed recapture rule. |
| Ghodrati et al., *FrameExit: Conditional Early Exiting for Efficient Video Recognition*, CVPR 2021, pp. 15608-15618, [CVF page](https://openaccess.thecvf.com/content/CVPR2021/html/Ghodrati_FrameExit_Conditional_Early_Exiting_for_Efficient_Video_Recognition_CVPR_2021_paper.html), [arXiv v1](https://arxiv.org/abs/2104.13400) | Sampled video frames; cascade of gates; learned earliest reliable exit | Video recognition accuracy versus GFLOPs on ActivityNet1.3, mini-Kinetics and HVU | Directly occupies learned conditional early exit based on sufficient reliability. | Kills the general early-exit mechanism claim. Leaves a Palm open-set/action-specific finite evaluation, not a new gate family. |
| Seon et al., *Stop or Forward: Dynamic Layer Skipping for Efficient Action Recognition*, WACV 2023, pp. 3361-3370, [CVF page](https://openaccess.thecvf.com/content/WACV2023/html/Seon_Stop_or_Forward_Dynamic_Layer_Skipping_for_Efficient_Action_Recognition_WACV_2023_paper.html) | Sequential frame representations; policy estimates frame usefulness; stop/forward and early termination | Efficient action recognition under compute cost | Direct sequential “continue versus terminate” decision over video evidence. | Kills a generic stop/forward contribution. Leaves the need to test Palm identity/action risk under a different observation and error contract. |
| Zhang et al., *Look More but Care Less in Video Recognition*, NeurIPS 2022, pp. 24304-24315, [official PDF](https://proceedings.neurips.cc/paper_files/paper/2022/file/c6e954799a0218f6d341ad5cbfb58999-Paper-Conference.pdf) | All-frame lightweight branch plus dynamic focal frame selection | Accuracy/compute trade-off on five video datasets | Occupies dynamic temporal redundancy reduction and frame-wise importance selection. | Kills the claim that temporal agreement/frame importance is a novel efficiency mechanism. Leaves only the Palm endpoint and a causal all-start protocol. |
| ISO/IEC 19795-1:2021 and the project’s prior sequential-biometrics audit | Biometric operating points and transaction-style measurement; accept/reject/continue framing | FAR/FRR/FTE/FTX and operational performance | The metric and sequential-decision vocabulary is established; prior project audit records Murakami/Takahashi as a direct sequential open-set neighbor. | Kills relabeling standard metrics or `accept/reject/continue` as the contribution. Leaves a finite Palm experiment or negative identifiability result. |

## Strongest simple baseline

The strongest baseline is a **pre-registered fixed two-shot or fixed three-shot policy with the same causal matcher and the same capture opportunity**, followed by a conservative `unknown` rule. It should be paired with:

1. first-frame quality threshold;
2. running score/margin threshold;
3. two-consecutive-agreement rule;
4. fixed recapture after a failed quality gate;
5. always-continue to the declared capture bound;
6. offline best-frame oracle, clearly labelled noncausal upper bound.

The proposed feature set `quality + score/margin + temporal agreement` is likely reducible to a small fixed rule or a calibrated sequential test. If a learned policy is used, it must beat these controls at the same FAR/unknown operating point, equal capture opportunity, equal total energy, and equal action reachability. Otherwise the result is configuration-specific policy tuning rather than a defensible mechanism.

## Contrarian result

The positive claim is vulnerable for three independent reasons:

- **Causal limitation:** current quality and margin can estimate present evidence but cannot certify that no later frame would be needed; a future blur/pose or impostor presentation can make an early stop unsafe.
- **Endpoint limitation:** frame-level recognition statistics do not identify terminal action risk unless every start is linked through ROI, matcher, unknown, authorization and action labels. A stop policy can improve latency by increasing unreachable or unreported failures.
- **Baseline limitation:** Palm-specific quality rejection/recapture and general video early-exit/frame-selection already provide the natural mechanism and baselines. A small score/margin rule with two consecutive agreements may remove any need for a new model.

Therefore `PALM-STOP` should not be promoted as a new stopping algorithm. A useful result remains possible if the study is explicitly a finite evaluation or null audit: measure the full risk-latency-energy frontier and report when online stopping is indistinguishable from fixed-N or when marginal observations cannot support a safe action decision.

## Feasibility audit

### Required data and labels

- Raw continuous VIS streams, not only curated best frames.
- Person-disjoint and session-disjoint genuine episodes.
- Enrolled and non-enrolled people with independent unknown labels.
- At least one untouched later session if a cross-session claim is made.
- A frozen gallery, matcher, threshold, ROI path, and action authorization rule.
- Per-start logs for frame timestamps, ROI status/reason/quality, scores and second scores, temporal state, stop time, identity/unknown, authorization, mock action, idempotency, and energy.

### Hardware and compute

The existing Palm capture path may be sufficient for a finite study, but the camera must expose a continuous stream and timestamps, and the Pi path must measure camera-on and inference energy. A wall-clock latency comparison alone cannot establish equal energy. The system must retain enough raw/derived information to replay the causal policy without using future frames.

### Ethics and permissions

Unknown-person and repeated-session data require explicit consent and a plan for storing or deleting raw Palm video. A mock action must be clearly non-production and idempotent. The study should avoid claiming payment security or real financial protection.

### Minimum falsification experiment

Freeze one VIS executable and run all eligible starts under a counterbalanced policy assignment. Compare fixed-2, fixed-3, fixed recapture, causal stop, and always-continue on the same capture opportunity. Hold out people and sessions. Use an independent set of non-enrolled presenters. Report terminal action risk, `unknown`, completion, p95 capture-to-action time, and measured energy with confidence intervals. If the causal stop policy does not dominate fixed-2/fixed-3 or if the action labels are incomplete, stop the positive claim and report `PALM-STOP-NULL`.

### Feasibility kill conditions

- Raw continuous video or timestamps are unavailable.
- Unknown people or an independent authorization label cannot be collected.
- The matcher/ROI/threshold changes during the comparison.
- The best-frame or full-tracklet selection is used in the stop policy.
- Unknown/wrong-action counts are too sparse to bound the claimed operating point.
- Capture opportunity, camera-on time, recapture cost, or energy cannot be matched.
- The observed effect is explained by fixing ROI, exposure, background, or threshold rather than stopping.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
|---|---|---|---|---|
| MPW-180 uses complete mobile videos, timestamp-aware temporal sampling, and windowed maximum-sharpness ROI selection. | [K] | Sünnetci et al., Applied Sciences 15(21):11368, published 2025-10-23, https://www.mdpi.com/2076-3417/15/21/11368 | Sec. 3 “Dataset: MPW-180”; Sec. 4.2.1 “Temporal Sampling and Frame Extraction”; Sec. 4.2.4 “ROI Sampling”; Sec. 4.2.5 “Quality Control and Data Curation” | Post-hoc curation/training data, not an online stopping policy; raw-video access and exact release conditions remain to verify. |
| Palm-ID is mobile, on-device, and includes quality estimation with optional rejection/re-capture plus time-separated evaluation. | [K] | Grosz et al., arXiv:2401.08111v1, submitted 2024-01-16, https://arxiv.org/abs/2401.08111 | Abstract; Sec. II, lines/pages describing the end-to-end pipeline and quality estimator; Sec. III-C identification and III-D computational efficiency | Single-image pipeline; does not establish sequential stop or action endpoint. |
| Palm quality can drive context-dependent compute/method selection. | [K] | Guerrache & Haddadou, DOI `10.1007/s11042-024-19867-5`, online 2024-08-01 / 2025 issue, https://doi.org/10.1007/s11042-024-19867-5 | Abstract and method description; publisher record | Publisher page was not fully retrievable in this audit; use the DOI/full text for final page-level checking. |
| Conditional early exit for video recognition already learns an earliest reliable exit and trades compute for accuracy. | [K] | Ghodrati et al., CVPR 2021; arXiv:2104.13400v1, 2021-04-27, https://arxiv.org/abs/2104.13400 | Abstract; CVPR paper Sec. 1 and method sections; CVPR pp. 15608-15618 | Action/video recognition, not Palm biometrics; direct collision is mechanism-level. |
| Sequential video policies already estimate frame usefulness and terminate early. | [K] | Seon et al., WACV 2023, https://openaccess.thecvf.com/content/WACV2023/html/Seon_Stop_or_Forward_Dynamic_Layer_Skipping_for_Efficient_Action_Recognition_WACV_2023_paper.html | Abstract; Sec. 1 and method description | Exact page retrieval was blocked by CVF in this browser pass; paper version and official URL are recorded for local PDF verification. |
| Dynamic frame selection and temporal redundancy reduction are established video mechanisms. | [K] | Zhang et al., NeurIPS 2022, https://proceedings.neurips.cc/paper_files/paper/2022/file/c6e954799a0218f6d341ad5cbfb58999-Paper-Conference.pdf | pp. 24304-24315; PDF pp. 0-2, Secs. 1-3 | General video recognition, not Palm; directly weakens a generic frame-selection contribution. |
| A Palm-specific exact claim combining causal stopping, open-set 1:N, independent unknown labels, authorized action, and matched energy was not found in the inspected sources. | [GAP] | Search chain: MPW-180; Palm-ID; Palm quality/context switching; FrameExit; Stop or Forward; AFNet; sequential biometric references | Queries listed below; exact absence is not evidence of novelty | Requires a broader database/citation-chain audit before any novelty wording. |
| Terminal action risk cannot be inferred from frame-level or marginal matcher rates without episode linkage and reachability assumptions. | [C]/[KILL] | Project charter, Round-27 reconciliation, and current candidate protocol | `research/active/00-project-charter.md`; `research/active/42-round-27-palm-only-reconciliation.md` | This is the retained negative-result boundary; it requires a complete all-start trace and independent action labels. |

## Queries and failed searches

Searches run on 2026-09-24:

- `palmprint video temporal frame selection recognition paper 2024 2025`
- `palmprint video sequence recognition temporal aggregation paper`
- `palmprint quality frame selection video recognition paper`
- `site:arxiv.org palmprint video recognition temporal 2024 2025`
- `"palmprint video" recognition 2023 OR 2024 OR 2025`
- `"video-based palmprint" recognition`
- `"palmprint" "frame selection"`
- `palmprint sequential biometric verification early stopping video frames`
- `sequential biometric verification accept reject continue frame selection paper`
- `site:openaccess.thecvf.com early exit video recognition frame selection paper 2024 2025`
- `site:arxiv.org video recognition adaptive frame selection early exit 2024 2025`
- `"PALM-STOP" palmprint`

Failed or inconclusive searches:

- No exact paper titled or indexed as `PALM-STOP` was found.
- Searches for Palm-specific “early stopping” mostly returned quality rejection, recapture, frame curation, or generic Palm recognition rather than a causal open-set action policy.
- Several CVF HTML pages returned 403 in the browser pass; official paper URLs were retained, and the available arXiv/NeurIPS/MDPI records were used for the load-bearing claims.
- No source inspected supplied an independently labelled terminal payment/action endpoint for Palm video stopping.

## Decision

**PIVOT**

`PALM-STOP` is **KILL** as a new stopping algorithm or a generic quality/temporal-selection method. It may be retained only as `PALM-STOP-NULL`: a preregistered, Palm-specific full-path audit of the risk-latency-energy frontier and the identifiability of safe online stopping under fixed capture opportunity, person/session-held-out episodes, independent unknown labels, and an idempotent mock action. A positive result must be treated as a finite empirical evaluation, not a global novelty claim; a matched fixed-N or fixed-recapture policy, incomplete action labels, future-frame leakage, or unbounded uncertainty is sufficient to close the positive claim.
