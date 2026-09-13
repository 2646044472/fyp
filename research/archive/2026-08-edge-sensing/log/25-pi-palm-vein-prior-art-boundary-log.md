# Raspberry Pi Palm-Vein Prior-Art Boundary Log

Last updated: 2026-08-21. This log separates a hardware feasibility precedent from a reproducible edge biometric baseline. It was added after a targeted search for Raspberry Pi, NIR/NoIR, palmprint/palm-vein, code, and end-to-end metrics.

## What was inspected

| Work | Primary material inspected | What it demonstrates | Why it is not a B0--M benchmark |
| --- | --- | --- | --- |
| [Kumar et al., *An Open Source Contact-Free Palm Vein Recognition System* (IJAAS 2017)](https://ijaas.iaescore.com/index.php/IJAAS/article/download/9470/7878) | Full six-page open PDF | A low-cost, standalone Raspberry Pi + webcam/modified NIR camera + 850 nm illumination + ROI + SIFT/BoVW/SVM palm-**vein** prototype was already described. The paper discusses ROI as a computational trade-off and uses 160x160 ROI. | It is palm vein rather than contactless palmprint; it uses old Raspbian Wheezy/Jessie and OpenCV 2.x-era software; it reports a 100-class recognition output but no subject/session manifest, `1:1` threshold, FMR/FNMR, PAIS, latency, memory, energy, code repository, model artifact, or raw-data terms. Its statements that veins are hard to forge are not a PAD test. |
| [Dhabarde & Kashyap, *Low Cost Palm Vein Recognition using Near Infrared Light and NOIR Camera using Raspberry Pi* (2019)](https://ijsrd.com/articles/IJSRDV7I40667.pdf) | Full three-page PDF | A cardboard-controlled setup with Pi, Raspbian, NoIR camera, approximately 800 nm IR LEDs, image preprocessing, and low-cost hand-vein matching was tested. It records a sub-two-second per-image verification time in that apparatus. | It is palm vein, a closed box, and a tiny same-system sample collection. The paper describes 40 database images and another 40 test images, reports three accuracy values, but does not publish a subject/identity/session protocol, fixed `1:1` matcher threshold, genuine/impostor counts, FAR/FNMR confidence interval, PAIS, source code, model hash, RAM/thermal/energy, or hardware-sync evidence. Its accuracy and time cannot transfer to this Pi or project. |
| [Raspberry Pi `rpicam-apps` TFLite documentation](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/camera/rpicam_apps_post_processing_tflite.adoc) | Current official camera/TFLite documentation | On current Raspberry Pi OS, TFLite C++ support can be installed and camera post-processing can consume a configured model file on low-resolution streams. This is a valid **runtime feasibility route** once an architecture-compatible, legally obtained frozen model exists. | The examples are generic object classification/detection/pose, not palm ROI, `1:1` verification, NIR, PAD, template lifecycle, actual illumination-state logging, or energy/latency evidence. A TFLite package does not make a palm model compatible or a biometric system reliable. |

## Search result and revised inference

The search found several hobby, low-tier, or modality-mismatched Pi palm-vein systems, but no primary artifact that simultaneously provides all of the following:

- contactless **palmprint** `1:1` verification;
- a current Pi/ARM runtime with frozen, accessible model and environment;
- documented RGB/NIR/ToF capture state;
- attack PAIS and blind material/session split;
- final `IAPMR` alongside APCER/BPCER;
- capture-to-decision p95 latency, memory, thermal behavior, and input energy.

This is a bounded search observation, not a “first” claim. It changes the project in two ways:

1. **The physical box is not novel.** Pi, NIR/NoIR, IR LEDs, ROI, and a local matcher have been repeatedly assembled in hand-vein work. A palm lock demonstration remains a demo, not the thesis contribution.
2. **The missing evidence is a measurement obligation, not an empty field.** B0 must publish its own runtime/capture manifest. B2/M can only be studied after Gate 0 establishes actual NIR availability, IR-cut state, LED control, frame sequence, and RGB/NIR alignment on the laboratory hardware.

## Consequences for wording

Use:

> We evaluate a documented low-cost edge palm capture-and-verification pipeline under our own hardware, protocol, and threat boundary.

Do not use:

- “first Raspberry Pi palm-recognition lock”;
- “Pi + NIR palm biometrics proves liveness”;
- a historical closed-box palm-vein accuracy or image time as this prototype's performance;
- “open source” to mean code, data, weights, and environment are all available. In the 2017 paper it describes open-source components; no project repository was located in this review.

## Hardware checklist reinforced by these precedents

- Pi model, architecture, RAM, OS, camera stack, and model/runtime hashes;
- RGB/NIR sensor models, IR-cut position, NIR wavelength/current, exposure/gain and lighting isolation;
- a real `frame id -> requested state -> observed state -> timestamp` trace;
- ROI success/failure and quality/retry reason;
- separate `T_capture`, `T_ROI`, `T_embed`, `T_match`, `T_interaction`, RSS/peak memory, thermal/throttling, and input-energy readings;
- subject/session/claimed-template manifests and, only with approval, PAIS/material/output/capture-chain metadata.
