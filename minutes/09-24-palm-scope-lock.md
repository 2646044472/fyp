# Palm Recognition Scope Lock

**Date:** 2026-09-24

## User constraint

The FYP direction remains palmprint recognition. Do not broaden the search to unrelated edge-computing families merely because the Raspberry Pi is an edge device.

## Consequence

Candidate generation and validation must stay inside palm recognition and its directly coupled decisions:

- physical palm capture and ROI;
- closed/open-set 1:N recognition and unknown handling;
- cross-session enrollment and template stability;
- VIS/NIR or missing-modality palm recognition;
- physical presentation attacks only after a full-path, consented apparatus gate.

Pi, latency, energy and offline operation are constraints and evaluation variables, not standalone novelty claims.

## Current research boundary

The existing Palm Payment MVP remains the engineering route. The remaining research candidates are `E-BOUND`, a cross-session enrollment-to-later-transaction evaluation; `VIS-GUIDE`, a frozen-path physical acquisition evaluation; and a gated VIS/NIR missing-modality or full-path PAD study. Generic ROI, retry, gallery calibration, model replacement, template privacy and stage-risk methods remain rejected unless a palm-specific task/action/observation distinction survives direct-neighbor and feasibility audits.
