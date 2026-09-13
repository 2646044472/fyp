# START-WIT Direct-Neighbor Contrast

> **Superseded (KILL, 2026-09-03):** a later audit added direct tachometer
> runtime and ETSC/reject collisions; the prior residual distinction no longer
> survives as a thesis mechanism.

## Decision investigated

Whether `START-WIT` differs from the closest motor-monitoring work in a way a
direct baseline or paper could refute.

## Comparison dimensions

| Work / candidate | Observation model | Task / action | Main endpoint | Implication for START-WIT |
|---|---|---|---|---|
| de las Morenas et al., Sensors 23(5):2649 (2023) | Motor-current signature analysis; Arduino acquires current, computes FFT/features and runs a classifier | Broken-rotor-bar and other motor fault classes | Public-dataset training plus a different-machine/real-case check; resource feasibility | [K] Occupies current-based edge motor diagnosis. It also exposes a sampling-resolution limitation that is useful as a START-WIT instrumentation warning. |
| Zhou et al., Sensors 25(1):9 (2025 issue; published 2024-12-24) | MCC118 voltage acquisition with an accelerometer for vibration, FFT/RMS features, cloud teacher and Pi 4B student | Servo-motor fault-status classes | Accuracy, confusion/t-SNE, quantized model size, inference time/memory and a Pi GUI deployment | [K] Occupies Pi motor-diagnosis deployment and the cloud-edge diagnosis workflow; Pi use is not a contribution. |
| Baddou et al., Sensors 26(16):5239 (2026-08-19) | Multi-sensor vibration/current under six bidirectional speed/torque/radial-force shifts | Early warning, fault classification and deployability/escalation | Paderborn KAT cross-condition robustness plus PCI, SDI and ECR indicators | [K] Occupies broad multi-sensor health classification and confidence/deployability assessment; do not use this endpoint. |
| `START-WIT` | First 2-5 seconds after a commanded start; current/acceleration only at decision time; independent optical rotation truth withheld | Record `running / failed-to-start / inspect` before the next maintenance action | Action loss versus latency, inspection cost, bytes and energy, with held-out load/mount cells | [C]/[GAP] Survives only as a command-outcome/run-proof decision study, not a motor-health classifier. |

## Allowed difference

The proposed distinction is a change in the decision object, not a claim that
the sensors or model family are new:

- **Task:** verify whether a commanded action took effect, rather than name a
  motor fault class.
- **Time:** decide from a short post-command prefix before a local deadline,
  rather than classify a collected diagnostic window.
- **Action:** `running / failed-to-start / inspect`, with asymmetric maintenance
  loss, rather than output a fault label only.
- **Label discipline:** the independent truth is binary by a fixed mechanical
  deadline; `inspect` is an action and must not be counted as a third physical
  class.
- **Truth:** use an independent mechanical witness for evaluation while
  withholding it from the policy, rather than treating a sensor-derived class
  as ground truth.
- **Generalisation test:** hold out a load and a sensor remount, rather than
  randomly splitting nearby windows.

Any one of these differences can be removed by a simple control. If removing
the proposed sequential policy or replacing it with fixed fusion leaves the
same action frontier, there is no positive mechanism claim.

## Prohibited framing

Do not use these as the title or central claim:

- “motor fault diagnosis on Raspberry Pi”;
- “multi-sensor motor fault classification”;
- “predictive maintenance using current and vibration”;
- “a novel edge AI model for motor monitoring”;
- “network-aware safety control”.

## Search record

Searches run on 2026-09-03:

- `"actuation verification" motor current sensor edge`
- `"command outcome" actuator verification sensor current vibration`
- `"motor startup" "success" current sensor accelerometer verification`
- `"run verification" actuator edge computing sensor`
- `site:mdpi.com/1424-8220 Raspberry Pi motor fault diagnosis deployment 2025 vibration`

The exact command-outcome/run-proof wording was not established as absent by
these searches. This is a search boundary, not a novelty claim.

## What the full-text audit changes

- The closest papers confirm that “edge + current/vibration + motor health” is
  already a complete application family, including real-time deployment and
  cross-condition reliability analysis.
- They do not, in the inspected task/action descriptions, use a post-command
  three-way maintenance action with an independent mechanical witness. This is
  a scoped remaining distinction, not evidence of global novelty.
- Their future-work statements point toward broader machines, devices and
  operating conditions. Those statements do not prove that `START-WIT` is
  open; the direct endpoint still needs citation-chain checking and a physical
  baseline.

## Unresolved checks before promotion

- Read the complete Abo-Khalil, Zhou and Baddou papers and record task splits,
  failure staging, timing, labels, baselines, limitations and future work.
- Search citation chains for “actuator success verification”, “start-up
  transient detection” and “command execution confirmation” in industrial
  CPS/robotics venues.
- Run the physical pilot and test whether fixed fusion already dominates.
- Measure local deadline and upload delay before retaining “intermittent
  connectivity” in the title.

## Status

**HOLD (Amber), high collision risk.** The distinction is precise enough for a
conditional pilot, but not yet strong enough for a thesis-lock or novelty
statement.

## Sources

- https://www.mdpi.com/1424-8220/23/5/2649
- https://www.mdpi.com/1424-8220/25/1/9
- https://www.mdpi.com/1424-8220/26/16/5239
