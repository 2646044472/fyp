# Frozen v26 public-data evaluation (2026-10-30)

Evaluation only: no algorithm optimization, training, threshold/label change,
sample selection from outcomes or production deployment. Algorithm source
commit frozen before inference: `9cfcab2fa0de4593fa8e9050cfbc9dd9cdf2f189`.
The exact evaluator/core-source/model hashes and fixed protocols are retained
in [protocols/FROZEN_PUBLIC_VALIDATION_20261030.json](protocols/FROZEN_PUBLIC_VALIDATION_20261030.json).
An earlier metadata-only protocol draft was not used for inference; all
reported runs use the final v2 protocol. Its canonical JSON SHA256 is
`e4dc182b48e63b6ddb099c8b269f89a2aa7d5d800c04167498aa71e08c59a231`.

## CASIA850nm: previously exposed confirmatory comparison

Same fixed subject001–004, left-hand850nm subset:24 originals, four filename
identities, indices1–5 enroll and6 queries. These images already ran on v13;
this is one v26 comparison, not independent validation or a rerun of v13.
Only the already present Pi copy was used, after verifying every original SHA.
No raw dataset or image was uploaded/transferred. CASIA archive SHA matches
the prior protocol.

Actual Pi, three-core affinity, ORT3/OpenCV1/native1 threads, frozen v26 and
model hashes. Fresh enrollment followed by real local HTTP identification
recomputes original read, localization, features and gallery scores. Camera
capture, hand placement and external/Wi-Fi image upload are excluded.

| Run | Correct | Correct <=2.5s | P50s | P95s | Maxs |
|---|---:|---:|---:|---:|---:|
| Historical v13, existing result | 4/4 | 4/4 | 1.060 | 1.497 | 1.574 |
| Frozen v26, first pass after enrollment/ready | 4/4 | 4/4 | 1.068 | 1.132 | 1.142 |
| v26 warm repeat of same four queries | 4/4 | 4/4 | 1.064 | 1.071 | 1.072 |

The warm repeat is not four additional independent samples. With only four
queries, these are sample timing quantiles, not a population-tail estimate.
Historical v13 reused v12 enrollment payloads; v26 here enrolls fresh, so do
not attribute all timing differences to one algorithm change.

### Time boundaries and integrity

- Empty-gallery application initialization/main-model priming:1.477s.
- Each identity's five-frame enrollment request:15.448,15.001,15.329,14.721s;
  four-request total60.498s. These replay saved frames and include that
  enrollment API's gallery preparation. They exclude taking five new photos.
- Extra gallery-ready recheck after all four enrollments:0.351ms. Most
  preparation is already inside enrollment; do not call this the whole ready
  wait or imply enrollment completes in query time.
- All four enrollments succeeded and returned ready. Eight query tokens were
  cancelled; no simulated transactions occurred. This exercise does not claim
  a new payment-confirmation/duplicate-payment test.
- All query responses are correct MATCH; zero wrong-identity MATCH and zero
  explicit REJECT in either pass. Inputs are enrolled subjects, so unknown FAR
  and verification FRR are not measured.
- Originals, model binaries, kernel and frozen sources remained unchanged.
  Every recorded power flag is0x0.

## PalmBigDataBase: archive metadata before feature evaluation

The ZIP SHA256 is
`8bdcbc155f43efb4f6e7d4bee66c1794a181e222bee54a956bafae1445552829`.
It has7,752 BMPs, all128x128, plus `Thumbs.db` and a directory entry. There is
no archive README establishing acquisition or identity/session semantics.

| Metadata | Count |
|---|---:|
| F-prefix BMPs | 3889 |
| S-prefix BMPs | 3863 |
| Numeric filename IDs | 386 |
| F-prefix filename classes | 386 |
| S-prefix filename classes | 386 |
| Prefix-specific classes total | 772 |

These are filename-defined classes, not a verified count of physical people.
F/S is not assumed to mean session or device. Class sample counts vary:
730 classes have10 images,28 have11,7 have9,3 have13,2 have12,1 has17 and1
has1. This is not a balanced full-archive evaluation.

### Fixed new range and exposure audit

The old400-image feature test used IDs1–20. Inventory additionally found an
old `public40-fixed-roi.zip` and scaling tool covering21–60 (798 images).
Whether every such old trial finished is not established; conservatively
exclude the entire1–60 range rather than call it untouched.

Before inference select the next20 numeric IDs,61–80, separately in F/S:
400 images,40 prefix-specific labels. Each class has10 images. Enroll its
five lowest numeric sample indices and query all remaining images. No skipped
failures or alternative IDs selected from recognition outcomes. There is no
byte-content or decoded-grayscale-pixel overlap with IDs1–60; the selected400
have400 distinct decoded pixel arrays. Prior result/manifest footprints checked
do not show evaluation of61–80. This does not establish new-device/session
independence or verified physical-identity labels. IDs61–80 are now evaluated;
future work must not call another run on them untouched or independent.

## PalmBigDataBase: frozen feature component only, local Windows

Uses existing128x128 normalization, accelerated FastCC code and best-two of
five enrollment distances per filename class. Each query reads/decodes its
supplied ROI, normalizes, extracts and matches all20 labels within its prefix.
No PKLNet ROI localization, native full-frame geometry, CompNet route, HTTP,
live capture or Pi benchmark. All failures would remain in the denominator.

| Prefix | Images | Classes | Queries | Ranking correct | P50ms | P95ms | Maxms |
|---|---:|---:|---:|---:|---:|---:|---:|
| F | 200 | 20 | 100 | 100/100 | 6.080 | 6.612 | 9.533 |
| S | 200 | 20 | 100 | 100/100 | 6.380 | 7.177 | 9.461 |

No decode/enrollment/query failures. Total200/200 filename-label rankings are
correct. Timings are local Windows ROI-component times with an already
accessed archive, not cold-I/O or Pi end-to-end recognition. Gallery feature
extraction for100 enrollment ROIs takes94.052ms F /60.148ms S; this is not
system enrollment/ready latency. No cross-prefix matching or reject policy
was evaluated. Do not label a ranking result full v26 identification.

### Platform audit

Windows uses NumPy2.3.5/OpenCV5.0.0; Pi uses NumPy2.2.4/OpenCV4.10.0.
FastCC algorithm files and Gabor-generator source match. Fixed generated
coefficients differ in floating-point last bits (maximum1.39e-17 across the
Gabor bank,6.94e-18 in the difference kernel). Each run records its kernel
before processing inputs and verifies it afterward. This is not a claim of
bit-identical coefficients or outputs across platforms; no parameters were
changed to reconcile results. The coefficient audit transfers public model
parameters/metadata only, never raw biometric samples.

## Remaining boundary and saved deliverables

Own-device baseline remains164/168 correct,146/168 correct within2.5s,
P95 6.019s,max15.225s, with four wrong identities retained. Public clean-ROI
success does not repair its localization/texture failures. New-session and
unregistered-person device validation remain blocked by missing independent
inputs. Neither public test estimates unknown-person FAR/verification FRR.

Tools: `tools/evaluate_frozen_public.py` (prepare/roi/casia) and
`tools/report_frozen_public.py`. Three protocol tests cover numeric ordering,
prefix separation, manifest-label fingerprinting and source-freeze rejection.
Committed deliverables are code, tests, frozen metadata protocol and aggregate
report only. No images, dataset archives, biometric templates or weights are
added to Git. Private results/protocol/HTML and environment audits remain at
`runtime/pi5-under2-20261028/frozen-public-validation-20261030-v2/`.
