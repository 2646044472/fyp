# Palm Payment Roadmap Update

**Date:** 2026-09-13  
**Status:** User-confirmed project direction; research novelty remains gated  
**Hardware target:** Raspberry Pi 5  
**Recognition mode:** 1:N identification

## Decision

The project is one staged Palm Payment FYP, not two separate projects.

The immediate commitment is to deliver a stable, portable palm-payment-like
prototype on Raspberry Pi 5. The same system will then become the experimental
platform for multimodal biometric and security research. Demo completion comes
before attack or PAD research.

## Phase 1: Palm Payment MVP

Build a complete local transaction flow:

```text
capture palm
-> extract ROI
-> perform 1:N identification against the enrolled user database
-> apply a frozen acceptance/unknown rule
-> simulate payment or balance deduction
-> write the transaction record
-> display success, retry, unknown-user, or failure
```

Minimum Phase 1 components:

- Raspberry Pi 5 deployment;
- visible-light palmprint capture;
- live preview or hand-placement guidance;
- enrolment and user/template database;
- automatic ROI with an explicit retry/failure path;
- 1:N gallery search and unknown-user handling;
- simulated account balance and transaction history;
- local/offline user interface;
- capture, ROI, search and end-to-end transaction timing logs;
- deterministic deletion of a user's template and simulated account data.

The payment flow is a simulation. Phase 1 makes no production-payment,
presentation-attack-detection, liveness, or commercial-security claim.

## Phase 2: Multimodal Upgrade

Add a controlled 850 nm illumination path and evaluate a NIR observation before
claiming palm-vein recognition. Record camera identity, wavelength, electrical
settings, illumination geometry, exposure/gain, capture order and session.

Progression:

1. verify repeatable NIR capture;
2. test whether vascular structure is visible and stable across sessions;
3. establish VIS-only and NIR-only baselines;
4. compare fixed/simple score fusion and fallback rules;
5. consider a learned fusion method only if a held-out residual remains.

If repeatable vascular evidence is not established, describe the branch as
`NIR-assisted palm recognition`, not palm-vein recognition.

## Phase 3: Security Evaluation

After the MVP and NIR gates, evaluate a declared set of physical presentation
attacks such as print, display/replay, or partial spoof conditions. The attack
protocol must exercise the physical capture and ROI path rather than injecting
a digital ROI directly into the matcher.

This phase reconciles the 2026-09-04 decision to deprioritise end-to-end attacks:
physical attacks remain out of the immediate scope and return only as a later,
gated phase after the required demo is stable and the presentation apparatus is
shown to be feasible. Cross-device research remains ruled out.

## Phase 4: Defence

Add and evaluate a lightweight PAD component on Raspberry Pi 5. Compare the
security and operational trade-off across at least:

- attack acceptance;
- bona-fide false rejection;
- failure to acquire and retry rate;
- 1:N search and total transaction latency;
- CPU, RAM and, when directly measured, energy.

PAD, NIR fusion and the attack benchmark are candidate research components,
not yet novelty claims. Their exact paper identity requires a direct-neighbour
audit and a frozen evaluation protocol.

## Immediate Priority

Work only on the Phase 1 VIS Palm Payment MVP while preserving interfaces for
later NIR, fusion, attack and PAD modules. Do not allow those later modules to
delay the first complete transaction.

The first engineering gate is:

> On Raspberry Pi 5, an unenrolled or enrolled participant can present a palm
> without entering an account identifier; the system performs 1:N search and
> produces a logged simulated-payment success, retry, or unknown-user result.

## Research Boundary

The final FYP story is:

> Build a portable palm-payment prototype, then study how to move it from
> usable to safely usable under NIR multimodality and physical presentation
> attacks, subject to measured accuracy, usability and edge-resource costs.

This record authorises the project roadmap. It does not establish novelty,
dataset permission, ethics approval, a production false-match rate, palm-vein
validity, or PAD effectiveness.

