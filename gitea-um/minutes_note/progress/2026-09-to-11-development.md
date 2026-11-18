# September–15 November 2026 | Building and testing the first system

This retrospective combines the dated milestones rather than treating every small change as a separate report. The initial prototype could acquire an image; the next question was whether its crop and nearest match were consistent across distance, pose and session.

## 04 September 2026 | Agreeing the scope
The [4 September minutes](../2026-09-04.md) prioritized a portable demonstration and reliable palm recognition outside tightly controlled conditions. Infrared and possible additional modalities were proposals, not validated features. Cross-device compatibility was outside the initial demo scope. No benchmark or hardware result is claimed for this week.

## 18 September 2026 | First acquisition workflow
The [18 September minutes](../2026-09-18.md) record working acquisition on a Raspberry Pi 4 with a NoIR Camera V2 under ambient light. The landmark pipeline estimated palm orientation and scale and generated a 128 × 128 grayscale region. Even when tracking succeeded, crop position and scale shifted between captures of the same palm. Full system performance had not been validated.

## 22 September 2026 | A pilot without a reliable denominator
The [22 September experiment note](../2026-09-22.md) records that the camera and IR illuminator had been assembled. The pilot reported roughly 66% false rejects, but did not record the trial count, threshold or capture sessions. The team therefore could not use that figure as a performance estimate. Background shielding and a camera comparison were proposed, not demonstrated.

## 06 October 2026 | From live preview to an inspectable crop
The Pi demo work and ROI audit were recorded on 6 October. Rather than trusting a match score alone, the capture view let the operator inspect what the matcher actually saw: the high-resolution frame, selected region and enlarged original-pixel detail. Five enrollment photos and one query were the intended demo workflow. The operator could confirm or cancel a proposed match; this was a simulated payment, not a bank transaction. The record does not establish an end-to-end trial on a fresh user.

Evidence: 6 October project handoff and dated Pi capture setup notes.

## 12 October 2026 | Capture before benchmarking
The 12 October project history records a full-resolution Pi capture interface and a deferred PKLNet benchmark. Capturing a usable image and proving that a model can recognize a hand are different milestones. The capture interface was available; no recognition rate or deployment decision follows from this change.

Evidence: FYP Git history, 12 October, “Add full-resolution Pi capture UI and deferred PKLNet benchmarks”.

## 20 October 2026 | Traceable capture sessions
The project indexed a new Pi capture batch and recorded checksums on 19 October. That made it possible to verify which inputs a local replay used. It did not create an independent test population. The actual captures, identity mappings and session data are not part of this package.

On 55 normal-distance queries, DoN ranked the correct hand first 50 times and FastCC 49 times. On five far-distance queries their counts fell to two and zero. These were small offline cohorts, not a real-time Pi trial.

Meeting record: [20 October](../2026-10-20.md). Evidence for the capture milestone: FYP Git history, 19 October.

## 30 October 2026 | Fast matching and honest failure counts
The team tested single-device ROI matching and a staged matcher with an exhaustive fallback. Regression checks rejected proposed context-search and exact SIMD changes; these were experiments, not default deployment choices. For SMPD the project froze the raw-input pipeline and reported raw outcomes separately from threshold tuning. A threshold can change the number of rejected attempts without improving the matcher.

Meeting record: [30 October](../2026-10-30.md). Evidence: FYP Git history, 28–30 October.

## 03 November 2026 | Experimental matcher configuration
The Pi demo README records an opt-in device-only optimization dated 3 November (FastCCLazyRetained-v28-experimental). It is an experimental option, not evidence that a new matcher improved recognition or passed fresh Pi validation. No new dataset accuracy is attributed to this week.

## 15 November 2026 | Enrollment recovery and dataset comparisons
The 9 November change added recovery to the automatic enrollment flow. The 15 November handoffs separated demo operation, ROI geometry and dataset evaluation. One example is PalmSet: across 1,600 images, the existing PKLNet crop produced 1,546 usable regions and a four-orientation CROI candidate produced 1,542. On 700 planned known queries, the PB matcher ranked the correct hand first 514 times versus 367 with CROI; SF2 gave 531 versus 356. Thus similar crop counts hid a substantial recognition loss. CROI was not promoted.

These were development images already examined by the team. The overlap between author-weight training identities and this cohort was not verified. This is not a claim about accuracy on unseen people.

Evidence: dated enrollment and supervisor handoffs; PalmSet frozen four-direction local comparison (13 November).
