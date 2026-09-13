# Polarization Glare Value-of-Information Pilot (pre-registration draft)

## Scope

This is a finite physical experiment, not a polarization reconstruction, material classifier, or security-defense thesis.

## Decision story

A local bench logger sees a printed code through a transparent cover. It must retain the frame, reacquire with one optical intervention, or mark the episode unknown. False retain contaminates the log; an extra capture costs latency and energy.

## Hardware and fixture

- Pi 5B with the owned RGB/NoIR cameras; static printed QR/AprilTag payload.
- One external linear polarizer in a rotatable holder; no claim of full-Stokes measurement.
- Transparent film/cover with scripted clean, glare and water-deposit states.
- Rigid mount, fixed target distance and controlled lamp. Record lux at the target plane and filter angle before capture.

## Baselines

Compare at the same maximum number of captures and measured energy:

1. no filter, one capture;
2. fixed polarizer angle, one capture;
3. fixed two-shot no-filter then fixed-filter;
4. RGB quality rule using saturation fraction, brightness and Laplacian variance;
5. digital highlight/deglare mask;
6. always-reacquire upper-coverage control.

An adaptive angle policy is allowed only after the controls are implemented and frozen.

## Labels and controls

Assign cover/glare state from the fixture script, not image output. Use manual exposure/white balance where possible; otherwise log all camera controls. Keep the target static because RGB/NoIR capture is sequential. Repeat across at least two lamp/lux cells and one held-out cover placement.

## Outcomes

- exact payload validity and false-retain rate;
- unknown/reacquisition rate;
- joules and latency per valid record;
- conditional action loss under a preregistered cost matrix;
- effect of filter attenuation after exposure controls.

## Kill and pivot rules

Kill POL-GLARE-VOI if fixed-filter, fixed-two-shot, RGB quality or digital masking is Pareto-equivalent, or if remount/held-out-lux repetitions erase the effect. If a difference appears only for one cover/lamp cell, report a configuration-specific boundary. Promote only if the intervention produces a repeatable held-out reduction in false-retain at matched availability and cost, with independent fixture labels.

## Status

**HOLD (Amber).** Tang, PolarFree, Khandaker and Laser Shield are direct neighbors for the optical components; this pilot tests only the residual action/energy endpoint.
