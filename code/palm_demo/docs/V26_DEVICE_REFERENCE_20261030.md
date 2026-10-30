# Verified v26 Windows device reference — 2026-10-30

The new full reference explicitly executes `CompNetAlternateROIMatcher`, v26 magic 2801066, with opt-in retained FastCC evidence. It uses the original frozen four same-device splits and all 169 source photos, with 168 final-gallery queries. It independently reexecutes all **34 five-frame enrollment requests**, rather than changing the metadata of a prior enrollment. The standard branch/tag, core sources, original photos, labels, thresholds and production services are unchanged.

| Case | Correct | Wrong accepted | Rejected / processing failure | Correct within 2.5 s | P50 / P95 / max s |
|---|---:|---:|---:|---:|---|
| New original | 29/29 | 0 | 0 / 0 | 29 | .554 / 1.211 / 2.149 |
| New reverse | 29/29 | 0 | 0 / 0 | 28 | .564 / 1.983 / 7.946 |
| Old original | 52/55 | 3 | 0 / 0 | 49 | .733 / 5.280 / 6.009 |
| Old reverse | 55/55 | 0 | 0 / 0 | 52 | .727 / 2.320 / 5.598 |
| Overall | **165/168** | **3** | **0 / 0** | **158** | **.724 / 3.270 / 7.946** |

This is Windows timing, with original file read, ROI, features, whole-gallery matching and loopback HTTP included; live acquisition and external upload are excluded. It is neither a Pi acceleration nor an independent generalization result. The independent historical Pi v26 retained-evidence run remains 165 correct, three wrong, zero rejection, 145 correctly within 2.5 seconds, P50 1.517 s, P95 5.907 s, max 15.234 s. Across all 168 queries the new Windows run loses none of that Pi run's correct identities and corrects none of its mistakes; score/time equality across hosts is not claimed.

All 34 enrollments succeeded and returned recognition-ready. Registration HTTP P50/P95/max was **11.740 / 19.802 / 22.106 s**. Last-frame-read end to ready response P50/P95/max was **4.393 / 6.437 / 6.700 s**. Initial model/empty-gallery startup and all 34 immediate-after-enrollment queries are separate in the scalar report. The latter have a growing gallery and must not be confused with the final-gallery 168-query denominator.

All four isolated cases pass confirmation/balance deduction, duplicate-confirmation blocking, cancellation and canceled-confirmation blocking. No production accounts or service were used. All original hashes and frozen standard core sources match their pre-run locks. Actual process command, evaluator/model hashes and per-case instantiated matcher provenance are retained in the private runtime and scalar summary.

Remaining errors, all in old original:

- `61f30739`: true xyt right; returned stephen left.
- `8d6441d2`: true xyt right; returned kss right.
- `37d0c433`: true cyw left; returned kss left.

Saved-coordinate image inspection shows that both xyt primary crops lean toward the wrist/forearm; one includes background. The cyw primary crop is already approximately on the palm. This is an exposed qualitative observation, not an anatomical ground-truth annotation or proof that localization explains every error. The independent contour candidate moved one xyt crop onto the palm and put its true identity first in angular ranking, but did not meet unchanged confidence gates. The other two mistakes have different evidence. The completed fixed 19-query candidate corrected nothing and was [rejected](CONTOUR_COMPNET_PILOT_20261030.md); no threshold/geometry scan or candidate deployment followed.

The [earlier half-turn Windows report's v26 label was erroneous](MATCHER_PROVENANCE_CORRECTION_20261030.md): it actually ran v24. Its observations remain intact with a correction. This new verified v26 reference establishes the correct baseline; it does **not** retroactively turn that historical run into a v26 candidate regression or qualify the half-turn candidate for promotion.

The next accuracy hypothesis should address small-hand/forearm localization with independent image geometry, and distinguish it from genuine texture collisions after a plausible crop. Freeze each proposed rule before scoring; test an isolated bounded pilot, then full168 paired regression only if it genuinely corrects errors without losing correct cases. Do not reinterpret rejection as correct or relax thresholds to fit these three images. New-session and unknown-person evidence is still needed for a generalization claim.

Pi Wi-Fi was verified read-only as `rasp5`; the later check reported `throttled=0x0`, 46.6°C. The actual remote staged-matcher, ARM registration library and original v26 result SHA256 match the historical Pi evidence. No Pi inference candidate was run or deployed in this iteration.

SMPD remains an incomplete **Windows public-data** run at **241/3217**, last `smpd-007-RP-36`. JSON/JSONL, exact fixed-order prefix, source/dependency locks, download/preparation completion and ZIP CRC flags passed read-only preflight; 2,976 queries remain, next `smpd-007-RP-37`. The combined resume-launch/proxy-probe command was automatically rejected with `blocked by policy` before execution; no public inference process was resumed, and no network setting was changed.

Scalar-only artifacts: [HTML report](experiments/v26-device-reference-20261030/report.html), [summary](experiments/v26-device-reference-20261030/summary.json), [168-query ledger](experiments/v26-device-reference-20261030/decisions.csv). Original/primary/contour comparison stays private at `runtime/contour-compnet-pilot-20261030-r3/three-errors-primary-and-contour.jpg`. No raw palm images, templates, features, model weights or public data archives are included in these exports.
