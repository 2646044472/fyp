# Frozen generalization checks (2026-10-29)

Algorithm commit: `a1e17f88b1fdd2c959c75539c836d35abf45e2ad`.
The user requested evaluation only. No recognition implementation, model,
threshold or alignment constraint was changed. Labels were unchanged during the
original evaluation; a subsequent collector-confirmed correction is recorded below.
The evaluation tools verify frozen algorithm source hashes before running.

## Reserved local captures: original-label results

Four previously reserved people, eight hand labels, 80 original old-camera
images. Each label uses indices 1–5 for enrollment and 6–10 for query. All 40
queries remain in the denominator, shuffled with seed 20261029. All eight
enrollments succeeded. This tests different people, but still same-session
bursts from the old camera; it does not establish new-camera or new-day accuracy.

Both matchers ran on the Pi with three-core affinity, ORT three threads,
OpenCV/native one thread. v12 performed fresh enrollment. v13 reused identical
enrollment payloads after verified algorithm-tag conversion; fresh v13 enrollment
time was not measured. Each query reloads its original image and recomputes ROI
and features through the real HTTP handler. No query answer cache is used.

| Metric | v12 | v13 |
| --- | ---: | ---: |
| Correct under original labels | 32/40 | 32/40 |
| Correct within 2.5 s | 27/40 | 27/40 |
| Median query seconds | 1.511 | 1.514 |
| P95 query seconds | 9.671 | 9.447 |
| Maximum query seconds | 11.126 | 10.681 |

The same 32 queries were correct and the same eight were incorrect: zero fixes
and zero regressions in identity correctness. One correctly recognized query
changed from exhaustive fallback at 11.126 s to affine rescue at 2.560 s. This is
evidence that the mechanism can help beyond the original two difficult images,
but it is not evidence of a broad accuracy improvement or a worst-case speed bound.

### Label caveat: do not silently correct the score

Five of the eight original-label failures are one subject's left-to-right
confusion. Post-result visual inspection of both labels' first enrollment image
and sixth/query image showed closely matching thumb orientation, wristwatch and
palm appearance, suggesting the same physical hand may have been assigned two
labels. On 2026-10-29 the collector explicitly confirmed that all ten images in
session `20261013T111838871161Z-df3d072b` are right-hand captures. The dataset
index now labels this session `syr:right`; original ZIP metadata is preserved.

No classes were merged, no samples removed and no corrected accuracy calculated.
The recorded result stays 32/40 under original metadata. It must not be treated
as a clean estimate of algorithm-only error. A fresh seven-identity evaluation
is required; do not silently replace these historical scores.
The private HTML report shows the inspected originals alongside the full failure
list. Preserve the original reservation record and its evaluated-status successor.

## CASIA 850 nm domain-shift pilot

Use only subject filenames 001–004, left hands, 850 nm, all six captures per
label: 24 originals, five enrollments and one query per label. Selection and
archive/source hashes were fixed before results. Do not mix wavelengths or
claim cross-device matching.

Both versions enrolled all four labels and scored 4/4, all within 2.5 seconds.
Median/max query times were 1.063/1.500 s for v12 and 1.060/1.574 s for v13.
The sample is far too small to establish population accuracy, and pretrained
localizer exposure to related public data is unknown. This is not evaluation of
the entire 7,200-image archive.

## PalmBigDataBase cropped-ROI supplement

The ZIP contains 7,752 128x128 BMPs. The fixed pilot selects numeric filename IDs
1–20 independently within each F/S prefix (400 images). For each filename class,
the five lowest sample indices enroll and the remainder query. Prefix semantics
are not assumed to prove independent sessions or devices.

The existing normalized FastCC feature and best-two aggregation score 100/100
in each prefix group, 200/200 overall. This Windows test bypasses localization
and geometric rescue because the images already are cropped ROIs. It is not a
v13 end-to-end result, a Pi latency measurement, or a full-archive accuracy claim.
No feature parameters were selected from these results.

## Integrity, scope and reproduction

Original image hashes were unchanged. All Pi power samples were clean (the
reserved-cohort run peaked at 57.6 C); periodic samples do not exclude every
transient. Query tokens were cancelled and simulated transaction counts did not
change. Production v6, model files and real accounts were untouched. Only test
tools and this report were added to version control; biometric data stays private.

The reserved cohort is now evaluated and must not be described as untouched in
future work. If these outcomes guide algorithm changes, another independent
validation cohort is needed. No open-set rejection policy is calibrated here.

Private evidence under `runtime/pi5-under2-20261028/`:

- `reserved-evaluation-20261029/{protocol,results}.json`
- `casia850-validation-20261029/{protocol,results}.json`
- `palmbig-roi-validation-20261029/{protocol,results}.json`
- `generalization-validation-report.html` and `generalization-validation-evidence.json`

Run `tools/evaluate_reserved_cohort.py` with the prepared original-image manifest,
frozen protocol, fresh output directory and explicit native library. Default
cardinality is 80 images/eight labels; the CASIA pilot explicitly passes
`--expected-images 24 --expected-identities 4`. Run `tools/evaluate_roi_archive.py`
on the PalmBig ZIP with a fresh output directory for the feature-only supplement.
These tools report failures rather than requiring perfect accuracy to complete.

The later frozen v26 confirmatory CASIA comparison and PalmBigDataBase61–80
feature-only evaluation are recorded separately in
[FROZEN_PUBLIC_VALIDATION_20261030.md](FROZEN_PUBLIC_VALIDATION_20261030.md).
That inventory also found an old21–60 prepared public bundle and excludes it
conservatively from untouched claims. Do not overwrite the historical results
above or reuse either evaluated range as fresh independent evidence.
