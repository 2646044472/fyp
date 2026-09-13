---
topic: vibration-sensor-integrity-boundary
created: 2026-08-29
last_verified: 2026-08-29
status: killed
depth: deep
related:
  - edge-selective-observation-audit
sources:
  - url: https://publica-rest.fraunhofer.de/server/api/core/bitstreams/dc6fcb76-e0a2-44fa-b26c-f69d957d9fa0/content
    fetched: 2026-08-29
  - url: https://doi.org/10.1109/SSI65953.2025.11107198
    fetched: 2026-08-29
  - url: https://doi.org/10.3390/vibration8040061
    fetched: 2026-08-29
---

# Vibration-Sensor Mount Integrity Boundary

## Status

**KILL.** A candidate in which a cheap edge accelerometer decides whether a trace indicates mounting degradation, a mechanical condition, or measurement uncertainty cannot claim a new mount-fault classifier, a laser-reference validation protocol, or a real-machine/MCU deployment extension.

## Load-Bearing Evidence

Karumanchi's 2025 official full thesis asks whether a MEMS vibration sensor can detect mounting looseness and whether an SVM generalizes across fixture materials. It tests three bolt-removal classes over four materials with a commercial triaxial MEMS sensor, validates against a laser vibrometer, and trains an SVM. See the abstract (PDF p. II), questions in Sec. 1 (PDF pp. 1-2), DOE and data collection in Sec. 3.6 (PDF pp. 39-41), validation and classifier in Secs. 3.7-3.8 (PDF pp. 41-43), and results in Sec. 4.6 (PDF pp. 57-63).

The same primary source reports setup-dependent weaknesses: natural-frequency-only generalization is poor for one-bolt removal; amplitude-dependent features limit robustness under real-world amplitude variation; fixture shape, orientation, printing parameters, and actual machine profiles are limitations. See Sec. 5 (PDF pp. 64-68) and Sec. 6 (PDF p. 69). It explicitly recommends real-machine vibration profiles and constrained MCU deployment. A future-work sentence is not by itself evidence of an open research problem, but here it follows direct task, hardware, label, and validation overlap.

Hummel et al. independently establish that accelerometer mounting changes frequency response. The exact broad claim that a single accelerometer always identifies mount state separately from unknown plant state is unsupported: with observation `z(r)=H_m(r)S_f(r)+e`, unknown `H_m` and unknown `S_f` can generate the same `z`. This is a [C] observation-model argument, not a cited general theorem.

## Consequence

The mount/plant ambiguity must be measured or controlled before interpreting any vibration FYP result. It is an instrumentation validity condition, not a self-contained FYP contribution. A finite reference-instrumented ambiguity map would be an honest laboratory appendix, but no distinct decision, mechanism, guarantee, or endpoint has yet been identified; it is not promoted.
