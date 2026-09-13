# RAW-RETENTION Conditional Direction Lock

**Date:** 2026-09-05  
**Status:** PIVOT / APPENDIX ONLY. This record was initially a conditional
lock, but a subsequent direct-mechanism audit found a collision. It must not
be presented as the primary FYP contribution.

## Decision

Do not use `RAW-RETENTION` as the primary FYP candidate. Retain it only as an
optional capability preflight or a bounded experiment appendix for a future
direction that has an independent research identity.

> **When is a JPEG insufficient to support an edge visual record?**

The project studies whether a low-cost edge camera should discard a raw frame,
retain it and request another capture, or flag the record for review after it
captures a non-personal physical identifier. The local record can represent a
maintenance point, refurbishment intake, or laboratory test coupon; none of
these stories establishes that a repair, shipment, or test itself occurred.

## Real decision and harm

An operator uses a Pi camera to enter a non-personal identifier into a local
record. After capture, the node chooses one of:

1. retain the JPEG-backed record;
2. retain raw evidence and require a fixed re-capture; or
3. mark the episode for a fixed local review procedure.

A false retain associates the record with the wrong identifier. A false review
or re-capture costs operator time, storage, latency, and capture energy. The
claim is about admissibility of the image-backed record, not asset state,
maintenance completion, authentication, or camera health.

## Exact empirical question

Let `R` be a raw Bayer image from one sensor exposure, `J` its processed JPEG,
and `Y` the pre-generated exact identifier payload. A fixed policy observes
either JPEG features or JPEG-plus-RAW features and outputs `retain`,
`reacquire`, or `review`.

The target claim is:

> On declared physical capture cells, does a simple RAW feature set reduce
> held-out false retain beyond JPEG luma, blur, saturation, and decoder
> confidence after bytes, processing time, latency, and measured energy are
> charged?

This is a finite same-device evidence-sufficiency question. It makes no claim
that RAW is generally more robust, that a RAW model is novel, or that the
result transfers to other cameras or tasks.

## Why this remains distinct enough to test

- [K] Chen, Tai and Ma (AAAI 2024) study RAW-domain object detection under
  harsh conditions. Their contribution does not establish whether RAW should
  be retained for a fixed edge record-admission decision.
- [K] Berdan et al. (CVPR 2025) study efficient RAW restoration for mobile
  object detection. This rules out a RAW restoration or generic edge-RAW
  claim, but not the narrow costed evidence-retention endpoint.
- [K] Generic answer/abstain/acquire and adaptive camera-control mechanisms
  are direct neighbors. A new acquisition router, conformal wrapper, or
  adaptive exposure method is therefore out of scope.
- [KILL] US9137417B2 describes caching raw acquisition data, quality analysis,
  virtual re-acquisition/reprocessing, user or automatic quality thresholds,
  and selective high-quality output for digital cameras and video. Its example
  includes retaining raw data to avoid physical reacquisition. This is a
  direct mechanism collision with RAW retention as a quality/re-capture
  contribution, even though it does not report the proposed Pi fixture or
  exact-payload metric.
- [C] A same-exposure RAW-versus-JPEG action-risk table may still be a useful
  finite measurement. It is not a sufficient research identity by itself.

Primary sources previously inspected:

- Chen, Tai and Ma, *RAW Image-Based Object Detection in Harsh Environments*,
  AAAI 2024, DOI: 10.1609/aaai.v38i2.27867.
- Berdan et al., *ReRAW: Efficient RAW Image Restoration for Mobile Object
  Detection*, CVPR 2025.
- Raspberry Pi Camera Software documentation: `rpicam-still --raw` writes a
  JPEG and DNG output.
- Raspberry Pi Picamera2 Manual: a captured request can contain main and RAW
  streams with request metadata.
- US9137417B2, *Systems and methods for processing video data*, especially
  the raw-data cache and virtual reacquisition descriptions.

## Minimal physical experiment

**Target and truth.** Generate a registry of non-personal QR/AprilTag payloads
before capture. Exact registry equality is the outcome; decoder confidence is
not truth.

**Physical cells.** Use a rigid mount and static target. Start with clean/high
light, clean/low light, transparent cover/reflection, and one held-out lamp or
cover lot. Record fixture state before capture. The transparent cover is a
physical difficulty cell, not a separate polarization or glare thesis.

**Policies.** Compare:

- JPEG luma, saturation, blur, and decoder confidence;
- a combined JPEG-only score;
- simple RAW saturation/linear-occupancy/SNR proxies;
- a fixed single capture;
- a fixed two-shot policy;
- always re-capture or review as cost/risk controls.

**Metrics.** False retain is primary. Report review/re-capture frequency,
false unknown, total bytes, wall-clock latency, and episode energy. Freeze
thresholds on source sessions before scoring a held-out lamp/material/session
block.

## Hardware gate

The theoretical camera path is supported by Raspberry Pi documentation, but
the purchased device remains unverified.

1. Run `code/palm_demo/tools/camera_capability_preflight.sh` on the Pi only
   when the user is ready to use the hardware.
2. Confirm the detected sensor identity, actual `rpicam-still --raw` outputs,
   Bayer packing/order, bit depth, exposure, analogue gain, frame duration,
   white-balance metadata, file sizes, and capture timing.
3. Demonstrate that JPEG and RAW belong to one exposure/request or otherwise
   downgrade the study to an engineering note.
4. Measure repeatable storage, processing, and energy cost over repeated
   static captures.

## Kill conditions

Mark the primary candidate KILL/PIVOT if any condition holds:

- the Camera NoIR v2 cannot produce a stable usable RAW/JPEG pair;
- same-exposure or request-level pairing cannot be established;
- JPEG-only evidence, fixed two-shot, or always-reacquire is Pareto-equivalent
  or better on held-out episodes;
- RAW benefit disappears after bytes, latency, and energy are charged;
- the effect is tied to one lamp, one cover, one marker, or post-hoc tuning.

## Non-goals

- no new RAW detector, restoration network, ISP, camera-health monitor,
  adaptive sensor-selection method, or visual-code decoder;
- no claim of field-maintenance completion, identity authentication, safety,
  anti-counterfeit security, or broad camera-family transfer;
- no claim that digital corruption is universally unlike physical failure.

## Decision rationale

The hardware preflight remains useful because it establishes what the owned
camera can record. However, raw caching, reprocessing, quality alerts, and
virtual reacquisition are already an explicit system mechanism. A positive
Pi-specific result would therefore be configuration characterization; a null
would be a limited engineering finding. It cannot carry the FYP research
identity without a distinct task, observation, or guarantee.
