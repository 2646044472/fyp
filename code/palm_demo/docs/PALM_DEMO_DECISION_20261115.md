# Palmprint demo candidates and dataset results (2026-11-15)

## Decision

**No candidate is currently approved for a live identity-confirmation demo on the Raspberry Pi.** The evidence does not establish usable automatic ROI extraction, reliable recognition, adequate stranger rejection and real-time Pi performance together. The table identifies the most informative offline arm in each cohort to help prioritize further validation. “Best” applies only within a dataset and protocol; it is not a deployment recommendation.

If demo material is needed before the Pi is available, show the capture interface, ROI quality gate and reject/retry flow. Clearly label recognition output as experimental; do not use it to confirm identity. These are presentation limits, not algorithm acceptance criteria.

## Dataset results and limitations

| Dataset / protocol | Most informative ROI + recognizer arm | Rank-1 | EER (genuine / impostor) | ROI/scoring denominators and open-set outcomes | Decision |
|---|---|---|---|---|---|
| PalmSet b16d, exposed | Reference ROI from the authors' formula + SF2e20 | 700/700 (reference arm); 325/374 for automatic PKLNet-v5 ROI on paired common support | Reference .00157 (700/29,300); PKLNet-v5 .09893 (374/12,078) | PKLNet-v5 extracted 1,514/1,600 ROIs; galleries complete for 12/20 hands. The 758 unknown queries contributed to EER only against a shared 11-hand subgallery. Full-gallery open-set false accepts cannot be reported. | The reference is not a live automatic localizer. PKLNet-v5 lagged and many galleries were incomplete. Identity and hand side are unverified filename proxies, and images overlap substantially with training data. |
| 11KHands development20, exposed | D127 21-point + SF2e20 | 185/185 | .04324 (185/9,615) | ROI 590/590; galleries 20/20. The frozen transferred threshold falsely accepted 62/305 unknown queries. | Strong closed-set results do not offset unacceptable stranger acceptance. No frozen dataset-specific threshold; do not deploy. |
| X-Palm dev/test, exposed | Official reference ROI + PB170 (higher Rank-1 on the same reference input) | Dev 122/140; test 117/136 | Dev .08760 (140/4,840); test .10294 (136/4,884) | Reference ROI 813/813. Frozen gate on test unknowns: 1 false accept / 114 rejects. Automatic D127 succeeded on 388/406 test images, but only 8/20 galleries were complete; PB Rank-1 was 39/136 (55 rankable). | The reference is a test upper bound, not a runtime detector. No complete-gallery open-set result for D127. The data were previously exposed. |
| Axon, exposed | D127 21-point + SF2e20 | 53/60 (59 rankable) | .11864 (59/1,121) | ROI 118/120. Only 1/6 folds had a complete gallery for its 10 stranger queries; all were rejected. Of the remaining queries, 49 were unscorable and 1 failed ROI extraction. | No reference ROI. Too little support for a rejection or false acceptance rate (FAR) claim. |
| Recorded self-collected cohort, exposed | PKLNet-v5 ROI + SF2e20 | 63/94 | Not reported for this arm | ROI 196/196. At the fixed transferred threshold: unknown false accepts 0/48 (PB 1/48). Separately, on strict common support for RTM/D127, SF2 Rank-1 was 46/59 and 51/59; EER .22034/.11864 (59/590 each). | The 11 identity/hand labels remain record-based proxies. With only 48 unknown images, 0/48 does not establish low FAR. No independent identity or device evidence or complete field rejection evaluation. |
| TCD/Tongji, fixed PKL ROI | Fixed PKL ROI + SF2e20 | 5,800/6,000 (5,877 rankable) | .016305 (28,914/17,261,220) | Additional automatic RTM extraction succeeded on 11,993/12,000 images. The protocol includes gallery, known and supplemental roles, but no strangers. Identity/hand/device mappings are insufficient. | Component and closed-set evidence only; no open-set or end-to-end automatic-ROI validation claim. |
| BJTU_PalmV2, precropped development set | Authors' precropped ROI + SF2e20 | 380/400 | .08000 (1,000/39,000) | Unknown false accepts 0/200 at the fixed source-development threshold. Images were precropped and the 20-person validation cohort was exposed. F/S denotes acquisition phase, not verified device identity. | Recognizer screening only: no original-image/automatic-ROI comparison, and the cohort was exposed. |

See the main ledger D149, D150 and the D166–D168 addendum for full planned denominators, both PB/SF2 arms and their status. EER support sets vary; do not rank across tables. Interpret each result only within its dataset and input arm. Frozen thresholds came from existing source-development data. Unknown queries count as accepts or rejects only when the entire planned gallery is available.

## Recommended validation order

1. **Review ROI usability manually first.** Use the D167 blinded review package to check whether automatic ROIs cover the visible palm region. It includes failures and successful controls but has not been reviewed by a human. It is neither label verification nor model scoring.
2. **Once the Pi has power, run a small end-to-end acceptance check using the existing handoff.** Back up the current configuration and preserve rollback. Use only explicitly enrolled participants and one stranger. Record all quality rejections, retries, failures, mistaken identities/rejections and camera→decision latency. Do not change the deployed runtime before the Pi is connected or present offline timings from X as Pi speed.
3. **For independent data, establish trustworthy person/hand/device groupings and a complete gallery before freezing thresholds and planned denominators.** The available local cohorts are already exposed or lack original images, reference ROIs, reliable labels or a stranger protocol. Do not refit thresholds on these targets.

## Reproduction entry points

These artifacts already exist on X. Use each directory's frozen protocol/manifest, checkpoint SHA and score summary; do not infer historical settings from current source defaults.

- Unified reference vs D127: `runtime/palm-fixed-D127-PB170-SF2e20-unified-D149-X-20261115-001/REPORT.md` and `protocol.json`.
- ROI × recognizer factorial comparison: `runtime/palm-2x2-factorization-D150-X-20261115-001/run-006/APPENDIX.md`; CPU cached scorer: `runtime/palm-2x2-factorization-D150-X-20261115-001/run-006/`.
- TCD RTM and the three PalmSet ROI methods: `runtime/palm-full-evaluation-ledger-X-20261115-001/ADDENDUM-D166-D167-FULL-PALMSET-20261115.md`. Per-image records, runner, protocol and scores are in the D166/D167 directories.
- PalmSet common-support reaggregation: `runtime/reconcile-palmset-D167-3roi-paired.py`. Inputs are only the frozen D164/D165/D167 vectors and b16d manifest; no new inference is needed.
- D167 blinded ROI review: `runtime/palmset-D167-blind-roi-review-20261115-001/README.md`. The sealed mapping is stored separately and kept out of Git.
- Pi demo limits and power/rollback procedure: `runtime/palm-fixed-D127-PB170-SF2e20-unified-D149-X-20261115-001/DEMO-HANDOFF.md`.

## Status

Complete: the main offline ROI/recognizer comparisons possible with existing data, failure accounting against all planned denominators, fixed-candidate cross-dataset evaluation, paired decomposition using cached results, and local demo handoff materials. Outstanding: D167 manual blinded review, any identity-level validation on unexposed participants, reliable transfer validation across physical devices, and Pi deployment, speed and live usability acceptance. The evidence does not support a winner for a live identity demo.

### X-Palm D144 on the exposed test partition (added 2026-11-15)

D144 recovered 5/406 ROIs (3 gallery, 1 registered, 1 unknown), had zero regressions among 388 D127 successes, and increased complete gallery support from 8/20 to 11/20. Native rankable Rank-1 was PB 39/55→51/76 and SF2 33/55→46/76; EER changed .14545→.16974 (55/385→76/760) and .25455→.26316 (55/385→76/760). On identical support (8 hands, 55 probes, 55 genuine/1,265 impostor scores), rank and EER were unchanged for both models. The 21 newly rankable probes were a support gain, not an equal-support recognition improvement. All 115 stranger rows remain unscorable against a complete gallery. This partition was previously exposed; D144 is not promoted. Full report and scripts: `runtime/xpalm-pose-geometry-detector-fallback-D144-test-X-20261115-001/REPORT.md`.


### TCD D168 strict common support (added 2026-11-15)

The cached-vector three-ROI comparison used the same 5,539 queries and 562 complete filename-proxy galleries. PB170 Rank-1 was fixed PKLNet 4,988/5,539 (EER 2.0401%), D127 4,158/5,539 (10.2546%), RTM 4,165/5,539 (7.3298%). SF2e20 was 5,472/5,539 (.6138%), 4,137/5,539 (15.8332%), and 3,442/5,539 (15.6346%). 461/6,000 planned queries were outside paired support. TCD has no unknown queries, so this does not establish stranger rejection; identity groups are filename proxies and data are exposed. This cached comparison does not change the Pi decision. Details: `runtime/tcd-three-roi-common-support-D168-X-20261115-001/REPORT.md`.
