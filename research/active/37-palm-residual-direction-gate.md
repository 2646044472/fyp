# Palm Residual Direction Gate (2026-09-23)

## Gate result

No Palm Payment thesis is promoted. `G-ADMIT` is KILL as an offline novel gallery-calibration method. `VIS-GUIDE` is HOLD/PIVOT only as a bounded prospective physical acquisition evaluation after the actual payment executable is stable. `S-SELECT` and `P-DELETE` are engineering controls unless a separate endpoint and threat model survive audit.

## Current executable boundary

The payment UI (`code/palm_demo/palm_payment_ui.py`, `build_app`) maps default `--roi-mode auto` to `roi.AutomaticPalmROI`, whose implementation in `roi.py` is background differencing, morphology and contrast/sharpness gating. The deep-learning `palm_roi.HandLandmarkTracker` is constructed by `debug_ui.py` only for its dynamic debug path. A note saying `ROI deeplearning` therefore cannot be assigned to the payment transaction path without a recorded executable/configuration and source-frame linkage. Existing unit tests and August logs do not prove the September 22 path.

## Candidate decisions

### G-ADMIT: KILL as thesis

The proposed observation is a matcher score vector and gallery provenance; the action is `commit top / unknown`. Gallery-relative palm scoring, fixed/global/per-gallery thresholds, quality and margin controls, open-set biometric evaluation, and gallery-size effects have direct neighbors. A Pi or simulated account does not change the mechanism. Cropped public images omit capture failure, ROI provenance, user guidance, payment action, and local latency. Person-blocked calibration may be a useful appendix after lawful access, but cannot be called live transaction security or a new edge method.

### VIS-GUIDE: HOLD/PIVOT, likely evaluation-only

The only residual is a local causal evaluation question: on the *actual* payment path, does one preassigned placement prompt or one guided VIS retake change all-start enrolled completion and p95 capture-to-terminal-action time against fixed guide, fixed quality/margin retake and conservative unknown at matched physical opportunities? A 2015 mobile palmprint study already describes a guided capture window/hand localization workflow, and Palm-ID 2024 covers mobile ROI, quality rejection and recapture; therefore this is not a new guidance or sequential policy mechanism. It is at most an apparatus-specific evaluation or negative result, and does not claim lower rare wrong-debit risk. It requires consent/permission, stable camera/ROI/matcher/threshold, source-frame to ROI linkage, all eligible starts, counterbalanced prompts, and person/session clustered reporting.

## Minimum gate

1. Run the actual payment executable with one frozen camera, profile, ROI mode, matcher commit, gallery and threshold.
2. The payment workflow now records optional capture context (`frame_id`, capture timestamp/age), ROI status/reason/quality, identification status/second score, terminal result and all stage timings in checkout JSONL events. The camera feed assigns a monotonic frame ID and exposes the context for the frame returned to checkout. `tools/summarize_checkout_trace.py` produces descriptive result/ROI/reason/status counts and timing distributions while explicitly making no FAR/FRR or security claim. This is instrumentation, not research evidence; the Pi deployment must still be run and configuration recorded.
3. Log every eligible start, including no capture, ROI retry reason, score/margin, unknown, wrong identity, correct identity, mock debit, idempotency, stage times and source frame/ROI IDs.
4. Reproduce the 2026-09-22 observation with numerator, denominator, modality, session, threshold and configuration. Treat `FR 66` as [GAP] until this exists.
5. Vary one factor only on development episodes. Compare fixed guide, current auto ROI, dynamic debug ROI only after integrating it into the payment path, and one fixed quality/margin retake. Do not mix camera swap, background box, IR state and ROI change.
6. Only if a stable stage-specific failure remains and authorized prospective prompts are feasible, run `VIS-GUIDE`; otherwise report an engineering repair or bounded null.

## Kill conditions

- A fixed exposure/ROI/threshold or fixture correction removes the reported failure.
- The payment path never uses the allegedly improved dynamic ROI.
- Prompt assignment cannot be randomized/counterbalanced, or the effect is measured only on successful retakes.
- Fixed quality/margin retake or conservative unknown matches the held-out completion/time frontier.
- Independent people/sessions are insufficient for a meaningful person-level estimate.

## Evidence boundary

Palm-ID (arXiv:2401.08111v1, 2024-01-16, https://arxiv.org/html/2401.08111), X-Palm (arXiv:2606.08437v2, 2026-06-22, https://arxiv.org/html/2606.08437), Pangelinan et al. (arXiv:2607.12903v1, 2026-07-14, https://arxiv.org/html/2607.12903), NIST IR 7544 (2008, https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7544.pdf), and Murakami/Takahashi WIFS 2009 (https://doi.org/10.1109/WIFS.2009.5386482) supply direct component and boundary constraints. A 2015 mobile palmprint paper's official record describes a guided capture window and hand localization (https://yonsei.elsevierpure.com/en/publications/an-empirical-study-of-palmprint-recognition-for-mobile-phones/); its full text/pages were not obtained in this round, so exact overlap remains [K/GAP], not a full-paper clearance. Bob Zhang's CROI/VIS-NIR/SF2Net full-paper chain remains [GAP]. Dataset permissions for local archives, IITD and X-Palm remain [GAP].

The authoritative supporting packets are `research/ops/divergence/2026-09-23-palm-direction-next-gate-divergence.md` and `research/ops/validation/2026-09-23-palm-residual-direction-audit.md`. The logging instrumentation and summarizer were added to `code/palm_demo/camera.py`, `workflow.py`, `palm_payment_ui.py`, `tools/summarize_checkout_trace.py` and tests; the project test suite passes 48 tests when run from `code/palm_demo`. The single next research-gate artifact is still an all-start stage-count table from the actual payment executable plus one complete physical VIS capture-to-1:N mock transaction.

PIVOT
