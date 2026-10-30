# SMPD preparation results and prospective optimization — 2026-10-30

Status: **raw preparation complete; full recognition still running**. This document is not a completed 3,217-query accuracy result or an algorithm-improvement claim.

The user authorized Windows testing now, followed by real Pi testing when the Pi is connected. Public-data experiments may inform general algorithm mechanisms; own-device regression and real device latency remain required. The public images, archive, templates and models are private runtime inputs and are not included in Git.

## Verified complete preparation

| Item | Result |
|---|---:|
| Actual released original JPEG files / right-palm identities | 3,677 / 92 |
| Full archive CRC | Passed |
| Original images processed | 3,677 / 3,677 |
| Programmatic ROI geometry pass / failure | 3,247 / 430 |
| Geometry failure: keypoint span too small / out of bounds | 376 / 54 |
| Fixed F0–F4 enrollment frames: feature success / failure | 417 / 43 |
| Complete five-frame identities registered in one gallery | 76 / 92 |
| Failed identity enrollments, without replacement frames | 16 |
| Required remaining query files | 3,217 |
| Unique original byte contents | 3,591 |
| Redundant files / duplicate-content groups | 86 / 62 |
| Cross-identity exact-byte conflicts | 0 |
| Query files byte-identical to an enrollment image | 2 |
| Unique query byte contents | 3,137 |

Archive SHA256: `747df91abb1e0449777ad95d1627fbcc4e651b223d8a155c450d709dab1932ab`.

These are geometry checks, not anatomical ROI annotations. Pixel-equivalent re-encodings and near-duplicates have not been audited. Failed registrations and every remaining query stay in the primary end-to-end denominator. The failed-registration group is a naturally unregistered diagnostic cohort, not a representative random stranger sample or calibrated FAR estimate.

## Specific visible mechanism

Source-image review of development subject 001 found that `smpd-001-RP-30` is a strongly side-on hand and its geometry-passing crop covers the thumb-root region rather than the central palm. The frozen full-gallery pipeline searched for 21.579 seconds on Windows and accepted identity 086 instead of 001. Adjacent `smpd-001-RP-31` was rejected by localization geometry before matching. This demonstrates that passing existing geometric guards does not establish correct anatomical coverage; it does not establish that every perspective failure has this cause or can be reconstructed from a nearly invisible palm surface.

The same subject's frontal and perspective examples have visibly larger central-palm coverage. Original/ROI comparisons are saved privately in `runtime/smpd-full-20261030/report-images/`. Images were selected in fixed filename order by diagnostic category, not removed from scoring or used as manual replacement query ROIs.

The user subsequently narrowed optimization to captures with the required finger valleys visible. The side-on 001 RP30 and finger-cropped 002 RF10 are therefore not targets that must be repaired. They remain in the original full-run accounting. A complete release-wide visibility annotation does not exist, so the all-file geometry/recognition figures must not be described as conditional on usable finger valleys.

A targeted manual development review found a relevant pair, 008 F00/F03: both required reference valleys appear visible in the original images, but F03 fails the existing ROI bounds guard while F00 passes. Quarter-turn observation, using no identity scores, produced validity `[true,true,true,true]` for F00 and `[false,false,true,true]` for F03 after mapping every result back. This is a possible localization-recovery lead, not a correct identification, a speed improvement, anatomical ground truth or an adopted fixed-rotation strategy. Existing evidence against rotating every device image remains applicable.

These short localization observations ran in a low-priority process alongside baseline queries; exact overlapping query-index intervals are retained in the private concurrency JSON and final scalar summary. Primary timings keep those queries and do not claim exclusive CPU or a paired acceleration effect. [Scalar orientation/visibility observations](protocols/SMPD_LOCALIZER_ORIENTATION_OBSERVATIONS_20261030.json) preserve the narrow scope and source hashes.

No claim is made that these early subjects represent the entire release. Recognition remains in progress. In particular, neither early latency nor a partial accuracy fraction is a full-dataset result.

## Prospective protection from target-specific fixes

The fixed [person split](protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json) reserves numeric subject IDs divisible by five: **18 people / 629 query files**. The other **74 people / 2,588 queries** form development. The manually reviewed 001 and partially observed 002 are both development identities. The rule is fixed before any new candidate and is not reselected after failure inspection.

The existing full baseline still evaluates everyone in one eligible gallery. Future candidate selection may use development failures, but reserved query images/results must not guide new mechanisms or parameters. Candidate source/model hashes and acceptance rules must be fixed before a reserved-query comparison. The complete fixed enrollment gallery may include reserved identities as ordinary references; their query images are not training data.

This is prospective protection against subsequent optimization, not a claim that the baseline has never evaluated the reserved cohort or that the localizer's original training exposure is established. Do not repeatedly relabel this same reserve as independent after it has informed further changes. A subsequent independent device session remains necessary for demo-domain robustness.

## Candidate requirements and failed routes not to recycle

Prior device experiments already found that simple fixed-rotation substitution, the tested MediaPipe hand replacement, neighborhood expansion, and the tested PPNet checkpoint did not meet the fixed accuracy/confidence requirements. Another arbitrary crop offset or more of the same search is not a demonstrated repair. The [prior stage evidence](PI5_V26_STAGE_BLOCKERS_20261030.md) and [lazy/shared assessment](PI5_LAZY_SHARED_ARCHITECTURE_ASSESSMENT.md) document these limitations.

A substantive candidate needs independent anatomical evidence or a genuinely more robust representation; its objective is correct identification with less search. A quality/rejection mechanism must separately report wrong accepts prevented and previously correct cases lost. A new threshold alone is not a claim of improved recognition or reduced matching work. No candidate has yet been shown to fix this public cohort, and the running sources/models/gates remain frozen.

The already existing `.02` development rejection example is checked once in saved-score shadow using the actual `AcceptancePolicy` code. Its FastCC distance cap stays 1.0; CompNet/quality retain separate .32/.08 profiles. No threshold is fitted or swept on SMPD. This checks transfer of the earlier mechanism, not a new source of recognition evidence; it cannot convert a wrong identity into the correct one and cannot establish a speed gain. It is not enabled in the full baseline or production.

## Completion and automatic report dependency

The existing single recognition process continues all 3,217 original-image HTTP requests. A one-shot current-experiment report dependency, `tools/follow_smpd_report.py`, periodically updates the private HTML with a prominent incomplete label. It starts no inference, retries nothing, changes no algorithm sources and schedules no future experiments. If inference exits early, it records the failure and retains partial evidence.

Only after the complete query count and final integrity/payment flags pass does it export owned scalar diagnostics under `docs/experiments/smpd-full-20261030/` and replace the private HTML with a completed report. `tools/report_raw_smpd.py` separately accounts for true-ID ties, wrong accepted identities, rejection, processing failures, registration coverage, every capture view, byte overlap, deterministic content-level diagnostics and repeated-byte decision conflicts. Final results are not present until that condition is met.

Windows uses OpenCV reference registration and larger isolated memory allowances. All-image startup/gallery preparation was 134.255 seconds; that is not per-query latency or live enrollment time. Private HTML: `runtime/smpd-full-20261030/report.html`. No result from this computer is labeled as Pi speed or proof of Pi capacity.
