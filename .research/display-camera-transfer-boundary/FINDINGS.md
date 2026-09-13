---
topic: display-camera-transfer-boundary
created: 2026-09-05
last_verified: 2026-09-05
status: superseded
depth: medium
related:
  - physical-failure-synthetic-transfer-boundary
sources:
  - url: https://pi4.informatik.uni-mannheim.de/~schaber/cammark/index.html
    fetched: 2026-09-05
  - url: https://pmc.ncbi.nlm.nih.gov/articles/PMC8470036/
    fetched: 2026-09-05
  - url: https://arxiv.org/abs/2602.01559
    fetched: 2026-09-05
---

# Legacy Display Reading: Synthetic-to-Physical Transfer Boundary

## Decision investigated

Could a Raspberry Pi camera reading a legacy LCD or seven-segment instrument
display support a new FYP around whether software-rendered degradations predict
physical display-camera reading risk under refresh, PWM, rolling shutter,
moiré, angle and glare?

## Real story considered

A low-cost edge camera logs readings from a legacy instrument whose display
has no network/API. A controller-side serial trace could supply independent
ground truth. After a capture, the node could log, recapture or request review.
This is a real class of retrofit problem, and gives unusually clean truth, but
the proposed research mechanism is not open.

## Direct-neighbor audit

- [K] CamMark is an established screen/camcorder simulation framework. Its
  published tool description explicitly models source/capture frame-rate
  differences, display refresh/V-sync, exposure, rolling-shutter readout,
  pixel geometry, and PWM LCD-backlight flicker for evaluations of recaptured
  video.
- [K] SEDIQA evaluates an OCR-oriented image-quality metric on synthetically
  degraded text, real camera-captured SmartDoc images and live capture. It
  explicitly distinguishes isolated synthetic degradations from the combined
  distortions of real camera capture.
- [K] Recent screen-capture work also treats combined physical flicker-banding
  and moiré as a dedicated restoration/dataset problem (CLEAR, arXiv 2026).
- [KILL] Therefore a generic claim that rendered degradations fail to represent
  physical display-camera effects, a new display-reading IQA gate, a rolling-
  shutter/flicker simulator, or edge LCD OCR is already a direct continuation.

## Residual and why it is insufficient

One could still build a clean bench with a microcontroller display and a serial
truth log, then measure a finite `log / recapture / review` frontier. However,
that would reproduce the same physical-versus-digital evaluation identity as
PRF-TR while adding a well-developed screen-camera simulation literature. It
does not supply a stronger publication claim.

## Disposition

**KILL as a primary FYP direction.** A legacy-display demo is useful only as a
truth-source apparatus for another question, not as its own synthetic-to-real,
IQA, OCR or rolling-shutter thesis.
