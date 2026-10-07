Decision investigated

# Divergence Packet: 2026-09-16 palm ROI detector and palmprint/vein pipeline bring-up

## Decision investigated

How should the current Windows/Pi palm pipeline be recovered when an obvious palm can still produce `no_hand`, while keeping palmprint extraction runnable and preventing an unsupported palm-vein claim?

This is an engineering bring-up decision, not an FYP novelty claim. Current evidence supports instrumenting and gating the ROI path before changing recognition or adding fusion.

**Recommended recovery:** preserve one fixed-guide Fast-CC path as the runnable palmprint fallback, but make the dynamic path expose six separately testable stages: frame/preprocess, raw detector output, decode, palm geometry, temporal stability, and publication/staleness. Run the live-demo protocol below before any detector replacement. Keep vein work behind a separate NIR apparatus and repeatability gate.

## Search boundary

- Role: divergence; local engineering inspection only.
- Date: 2026-09-16.
- Required files read: `AGENTS.md`, `research/ops/agent-divergence.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`.
- Local project evidence read: `minutes/09-13-palm-payment-roadmap-update.md`, `minutes/08-17.md`, `Biometrics/README.md`, `code/palm_demo/README.md`, `BASELINES.md`, `data/SOURCE_MANIFEST.md`, code and tests under `code/palm_demo/`, the 2026-09-13/15 divergence packets, the 2026-09-13 validation packets, and relevant archived palm ROI/vein/embedded-system logs.
- No new web research was performed. URLs below are source records already present in the workspace.
- No code, active research record, archive, dataset, or `.research/` file was edited.

## Current executable state

| Observation | Label | Consequence |
| --- | --- | --- |
| `python -m pytest -p no:cacheprovider -q` in `code/palm_demo` reports `32 passed`. | [E] | Pure geometry, synthetic foreground ROI, gallery, template, payment, and workflow units are healthy. This does not test a real detector frame or Pi camera. |
| Windows has Python 3.13.9, NumPy 2.3.5, SciPy 1.16.3, Pillow 12.0.0, and OpenCV 5.0.0. Fast-CC extracts a `(32,32)` Boolean feature from a synthetic `(128,128)` ROI and self-distance is `0.0`. | [E] | The palmprint feature core can run after an ROI exists. |
| `code/palm_demo/models/handpose_estimation_mediapipe_2023feb.onnx` exists, but `models/palm_detection_mediapipe_2023feb.onnx` is absent locally. | [E][KILL] | The dynamic tracker cannot be instantiated on Windows until the exact detector artifact is restored and hashed. |
| The four local debug images under `runtime/` contain no visible palm; three display `PALM ROI no_hand`. | [E] | They confirm the symptom display path, but cannot identify the failing stage. |
| The user confirms that an obvious palm can still produce `no_hand`. | [E] | Raw detector and post-detector gates must be separated. |
| `palm_payment_ui.py` uses `AutomaticPalmROI`, a foreground heuristic, while `debug_ui.py` alone uses `HandLandmarkTracker`. CLI defaults to fixed crop. | [K] | There are three different ROI semantics, not one pipeline. |
| `debug_ui.py` publishes the latest image with the most recently processed ROI quad; no shared frame ID proves they came from the same frame. | [K][GAP] | A plausible box or crop can be stale or misregistered. |
| Detector submissions are rate-limited to 800 ms by default; the stored ROI expires after 1500 ms. | [K] | One missed update can quickly produce stale/lost tracking. Measure detector submissions and age, not preview FPS. |
| The deployment ZIP was generated 2026-09-13, differs from the 2026-09-15 ROI/UI code, and its build list omits the modular payment/workflow files. | [E][KILL] | It is not an authoritative current release artifact. |
| Non-interactive SSH to `fyp@10.12.194.1` returned `Permission denied`; current Pi state was not read. | [GAP] | README statements from 2026-09-13 are historical, not current verification. |
| The payment policy defaults to `capture_profile=rgb`; the systemd debug service uses camera 0 with `imx219_noir.json`. | [K][GAP] | Camera identity and modality semantics can diverge unless bound in one manifest. |
| The existing 20 x 10 PalmBigDataBase subset gives FMR `0`, FNMR `0.03` at threshold `0.28`, but permission remains unresolved and images are pre-cropped. | [E][GAP] | It is only a matcher smoke test, not a detector, Pi, vein, or population result. |

## Detector-stage diagnosis map

The next implementation should log one JSON record for every actual detector submission, not every preview frame.

| Stage | Current boundary | Required diagnostic fields | Acceptance criterion for a centered obvious palm | Failure interpretation |
| --- | --- | --- | --- | --- |
| D0 frame/preprocess | Capture plus `_infer` resize, letterbox, RGB conversion, normalization | `frame_id`, times, source/input size, channel statistics, ratio/padding, detector scale | 25 submitted frames in 25 seconds; palm fully visible; every input finite and non-constant | Camera selection, tuning, exposure, channel order, or preprocessing problem |
| D1 raw ONNX output | Output tensors, sigmoid, threshold `0.42` | output names/shapes, finite check, top-5 logits/scores, winning anchor | Threshold pass on at least 23/25 frames; median top score at least `0.55`; empty scene passes at most 1/25 | Model artifact, preprocessing, camera domain, or detector suitability problem |
| D2 decode | Anchors, deltas, de-letterbox mapping | decoded box/seven points, finite/in-frame flags, area ratio, center | 100% finite among D1 passes; at least 23/25 boxes overlap the visible hand with center inside it | Anchor/order/scale/padding decode problem |
| D3 geometry | `_has_valid_palm_geometry` and `landmarks_to_palm_quad` | pass/fail and explicit span/axis/outside/degenerate reason | At least 90% of plausible D2 candidates pass; at least 18/20 overlays cover central palm | Landmark semantics or ROI geometry problem; threshold tuning cannot fix it |
| D4 temporal gate | Center jump, area ratio, axis similarity | previous/candidate metrics and rejection reason | After first lock, no more than 10% of stationary candidates rejected; reacquire within 2.5 s | Gate too strict or coordinates inconsistent/stale |
| D5 publication/staleness | `_last_seen_monotonic`, `roi_status`, 1500 ms expiry | accepted frame ID, publish time, `age_ms`, submit skip count, status | Tracking available at least 90%; p95 ROI age below 1200 ms; no `no_hand` after an accepted candidate | State/scheduling bug or inadequate detector cadence |
| D6 frame/quad atomicity | `snapshot()` combines latest image and latest quad | image frame ID, quad source frame ID, age delta | Enrollment/matching enabled only when IDs are equal during bring-up | Correct detection can still produce a wrong crop |

### Decision rule after one live run

1. D1 fails: freeze geometry/UI work; verify model file/hash, preprocessing, camera profile, and palm scale.
2. D1 passes but D2 fails: fix output ordering, anchors, or de-letterbox math.
3. D2 passes but D3 fails: fix seven-point semantics and ROI geometry.
4. D3 passes but D4 fails: change temporal gating only from recorded candidate traces.
5. D4 passes but D5 shows `no_hand`: fix tracker state/publication scheduling.
6. D5 passes but crops/matches fail: enforce D6 atomicity before tuning Fast-CC.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| A `TRACE-CURRENT` | An obvious palm is reported as absent; blind model or threshold changes can hide the real fault. | `[E]` Expose D0-D6 for the current detector and identify the first failing stage. | Current local tracker code; OpenCV MediaPipe palm detector artifact. | Kill any causal conclusion without raw scores, decoded coordinates, gate reasons, and ages from the same run. | Highest priority and information value. |
| B `FIXED-GUIDE-SPINE` | The demo still needs a working palmprint transaction while free-hand ROI is repaired. | `[E]` A rigid guide and fixed ROI can keep `capture -> Fast-CC -> 1:N -> simulated payment` runnable as a regression oracle. | Embedded palm systems with constrained hand positioning. | Kill as final architecture if free-hand capture is mandatory; retain as fallback/regression path. | Highest probability of immediate success. |
| C `REPLACE-DETECTOR-ADAPTER` | The current detector may be unsuitable for this NoIR/domain or ARM runtime. | `[C]` Replace only the box/landmark producer while preserving one ROI result contract and Fast-CC. | RDRLA/open-environment ROI and other established ROI model families. | Kill a model with unclear weights/licence, no ARM runtime, or worse ROI-success/latency than A/B. | Medium; start only if A localizes failure to D1/D2. |
| D `REPLAY-FIRST-CONTRACT` | Live debugging is non-repeatable without positive and negative full-hand frames. | `[E]` A consented Windows replay set with expected D0-D6 outcomes must behave identically on Pi. | Standard deterministic regression practice. | Hold if capture/retention is unauthorized. Pre-cropped datasets cannot replace full-hand detector frames. | High after lawful positive captures exist. |
| E `NIR-VEIN-SEPARATE` | A `noir-ir` label may be mistaken for a real vein pipeline. | `[C]` After ROI stability, establish controlled NIR vascular repeatability and an NIR-only baseline before any fusion. | Existing low-cost Pi/NoIR palm-vein prototypes and multimodal fusion work. | Stop palm-vein wording after two controlled iterations if structure is not repeatable or is explained by exposure, creases, shadow, or visible leakage. | Medium/uncertain; no current vein extractor exists. |

## Top two formalizations

### A `TRACE-CURRENT`

- **[D] Decision:** retain, repair, or replace the current detector.
- **[A] Assumptions:** exact model hash and launch command are recorded; palm is visibly present and not clipped; detector submissions are counted independently of preview frames.
- **[T] Target:** find the first D-stage that fails the acceptance criteria above.
- **Observable outcome:** per-submission raw score, decoded box/points, geometry result, stability result, publication status, age, and matching frame IDs.
- **Counterexample:** only UI video or final `no_hand` is available; no stage can then be identified.
- **Negative-result value:** a verified D1 failure justifies a detector replacement; a D3-D5 failure prevents an unnecessary model swap.

### B `FIXED-GUIDE-SPINE`

- **[D] Decision:** whether the palmprint transaction can run while dynamic ROI is unresolved.
- **[A] Assumptions:** rigid fixture, frozen crop, distinct capture frame IDs, same camera/profile for enrollment and probes, provisional non-security threshold.
- **[T] Target:** complete enrollment, open-set 1:N search, retry/unknown handling, and idempotent simulated payment with stage timings.
- **Observable outcome:** five distinct enrollment frames, ROI hashes/quality, feature/search timing, score/rank, decision, and transaction result.
- **Counterexample:** copied repeated frames, profile mismatch, missing module in deployment, or crop instability prevents a complete transaction.
- **Negative-result value:** separates recognition/workflow defects from dynamic detector defects and provides a deterministic regression oracle.

## Live-demo capture protocol

The user can provide this later. It is diagnostic, not biometric evaluation.

### Before the demo

Record:

```text
date -Is
uname -a
cat /etc/os-release
python3 --version
rpicam-hello --list
systemctl status palm-debug-ui --no-pager
journalctl -u palm-debug-ui -n 100 --no-pager
sha256sum models/*.onnx palm_roi.py debug_ui.py
```

Also record the exact launch command, camera index, tuning file, capture and detector input sizes, `--inference-ms`, recovery-pass state, OpenCV version, and IR state.

| Trial | Action | Duration / repetitions | Pass condition |
| --- | --- | --- | --- |
| L0 empty | Fixed empty background | 20 s | No accepted tracking; at most 1/25 D1 threshold pass |
| L1 centered | Centered open palm, stationary | 25 s | D1-D5 criteria; tracking at least 90% |
| L2 scale | Near, nominal, far, palm fully in frame | 10 s each | At least two adjacent scales pass, or failure is localized to one stage |
| L3 rotation | Approximately `-15`, `0`, `+15` degrees | 10 s each | Geometry pass at least 80% per angle or supported range documented |
| L4 reacquire | Remove for 3 s, return | 5 cycles | Clears when absent; reacquires within 2.5 s in at least 4/5 |
| L5 slow motion | Slow translation across guide | 20 s | No persistent jump rejection; D6 never feeds mismatched image/quad IDs |

Return to the coordinator: environment/model manifest, exact command, stage-count table, p50/p95 inference and ROI age, reacquisition times, up to 20 approved overlays, screen recording, and consent/retention note. A video showing only `no_hand` is insufficient.

## Palmprint and vein boundaries

Use one `ROIResult` contract across CLI, debug UI, and payment UI: ROI pixels, geometry/version, source frame ID, capture profile, quality, elapsed time, and explicit failure reason. Fast-CC remains the first matcher because it is pinned and deterministic. Threshold `0.28` remains provisional for live Pi capture.

Enrollment must use five distinct frame IDs with a declared minimum interval. The current payment UI can copy the same latest frame repeatedly in a tight list comprehension.

There is no vein enhancement or extractor in the repository. `capture_profile=noir-ir` only isolates template namespaces. A valid first vein branch is:

```text
controlled NIR capture
-> atomic palm ROI
-> exposure normalization
-> one frozen classical vessel-enhancement baseline
-> repeatability and crease/shadow controls
-> NIR-only feature/matching baseline
```

Only after this passes may score-level fusion be tested.

## Data, licence, and safety gates

- [GAP] The three local archives are inventory, not documented permission. Do not publish, redistribute, or expand processing until terms and provider authorization are recorded.
- [K] The existing PalmBigDataBase subset is pre-cropped and cannot test the full-hand detector.
- [GAP] CASIA was not extracted in this round and must not be treated as equivalent to the Pi optical path.
- [K] Live palms/templates are biometric data. Require authorization, consent, pseudonymous IDs, minimal retention, access control, and deletion behavior.
- [GAP] IR wavelength, current, diffuser/filter, geometry, irradiance, and eye/skin safety documentation remain unverified.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/path read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Threshold, decode, geometry, temporal gate, and staleness are separate code stages. | [K] | Local `code/palm_demo/palm_roi.py`, inspected 2026-09-16 | `_infer`, `_is_stable_candidate`, `_has_valid_palm_geometry`, `submit`, `roi_status` | No positive live trace yet. |
| Debug capture and processing are asynchronous without common frame IDs. | [K] | Local `code/palm_demo/debug_ui.py` | `CameraFeed._capture_loop`, `_processing_loop`, `snapshot` | Concrete integration risk, not proof it caused `no_hand`. |
| Payment UI does not use the dynamic tracker. | [K] | Local `code/palm_demo/palm_payment_ui.py` | `build_app` | `auto` is foreground ROI here. |
| Fast-CC is runnable after a valid ROI. | [E] | Pinned commit `d556f455a6cbdcb4264ec1cd75de2e451cf241b3`, https://github.com/Li-ChengYan/palmprint-recognition-python | `palmprint/algorithms/fastcc.py`; local synthetic diagnostic | Does not validate live ROI or Pi timing. |
| Open-environment palm ROI is established work. | [K] | Chai et al., IEEE TIFS 2025, DOI `10.1109/TIFS.2024.3516539`, https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf | Archived log `29-open-environment-roi-rdrla-reading-log.md` | Does not prove ARM readiness. |
| Low-cost Pi/NoIR palm-vein boxes already exist and require controlled optics. | [K] | Kumar et al. 2017, https://ijaas.iaescore.com/index.php/IJAAS/article/download/9470/7878; Dhabarde & Kashyap 2019, https://ijsrd.com/articles/IJSRDV7I40667.pdf | Archived log `25-pi-palm-vein-prior-art-boundary-log.md` | Historical feasibility only. |
| The local roadmap requires repeatable vascular evidence before palm-vein wording. | [K] | `minutes/09-13-palm-payment-roadmap-update.md` | Phase 2 | Project decision, not novelty evidence. |
| The exact D-stage causing the live `no_hand` symptom is known. | [GAP] | No stage trace exists | Not applicable | The live protocol resolves this. |

## Exact local commands inspected

```text
Get-Content AGENTS.md
Get-Content research/ops/agent-divergence.md
Get-Content research/active/README.md
Get-Content research/active/00-project-charter.md
Get-Content research/active/01-candidate-register.md
rg --files research/ops/divergence research/ops/validation minutes code/palm_demo Biometrics research/archive/2026-08-edge-sensing
python -m pytest -p no:cacheprovider -q
python -c "import sys,numpy,scipy,PIL,cv2; ..."
python -c "... load_fastcc(...); extract_feature(...); ..."
rg -n -i "vein|vascular|nir|noir|roi_mode|AutomaticPalmROI|HandLandmarkTracker|capture_profile" ...
tar -tf code/data/PalmBigDataBase.zip
tar -tf code/data/palmprint-device-intro.zip
tar -tf code/palm_demo/dist/palm_demo_pi.zip
ssh -o BatchMode=yes -o ConnectTimeout=5 fyp@10.12.194.1 "uname -a; cat /etc/os-release; python3 --version; rpicam-hello --list ..."
git -C code/palm_demo/vendor/palmprint-recognition-python rev-parse HEAD
git status --short
```

Additional read-only checks compared ZIP/working-tree hashes in memory, listed model/data manifests, read existing calibration/fixed-split JSON, and visually inspected the four runtime debug images.

## Queries and failed searches

No web queries were run under the timebox.

- No vein enhancement/extractor implementation or test was found.
- No positive full-hand replay frame with an expected detector result was found.
- Windows detector replay failed before inference because the detector ONNX file is absent.
- Pi state retrieval failed because non-interactive SSH authentication was rejected.
- Existing tests expose no raw detector score, decoded points, gate rejection counts, or ROI age.

## Decision

Promote A `TRACE-CURRENT` as the next engineering action and B `FIXED-GUIDE-SPINE` as the runnable fallback. Do not tune Fast-CC, change the threshold, replace the detector, or add vein/fusion code until one L0-L5 live run identifies the failing D-stage. Use C only if D1/D2 proves the current detector artifact or decode unsuitable. Use D after lawful positive frames exist. Keep E behind ROI, optics, safety, repeatability, and NIR-only gates.

The current artifact is a working palmprint feature core surrounded by divergent ROI paths, an unverified deployment package, and a labelled NoIR profile with no vein extractor. Recovery must change the order of work rather than claim a new method.

PIVOT
