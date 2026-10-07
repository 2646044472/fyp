---
topic: palm-roi-following-pipeline
created: 2026-09-13
last_verified: 2026-09-13
status: active
depth: quick
related: [edge-palm-baselines]
sources:
  - url: https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/hand_landmarker/raspberry_pi/README.md
    fetched: 2026-09-13
  - url: https://raw.githubusercontent.com/google-ai-edge/mediapipe-samples/main/examples/hand_landmarker/raspberry_pi/detect.py
    fetched: 2026-09-13
  - url: https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/HandLandmarker
    fetched: 2026-09-13
  - url: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307822
    fetched: 2026-09-13
  - url: https://pypi.org/project/mediapipe/
    fetched: 2026-09-13
---

# Following palm ROI on the Raspberry Pi

## Summary

The fixed fractional ROI can be replaced by a tracked hand-landmark ROI. The
best first implementation is MediaPipe Hand Landmarker on the existing
Picamera2 stream, followed by a geometry-based affine crop using wrist and MCP
landmarks. Google's maintained Raspberry Pi example uses Python, 64-bit Pi OS,
live-stream landmark inference, and configurable tracking confidence.

The palm-recognition literature generally uses hand keypoints to correct
orientation and derive a palm coordinate system before extracting the ROI;
whole-hand bounding boxes alone are not enough for a stable palmprint crop.

The current Pi inspection found no installed `mediapipe` or `cv2` module, so
dependency installation and a measured latency/CPU gate are required first.

## Findings

Google's Raspberry Pi Hand Landmarker example explicitly supports a 64-bit
Raspberry Pi OS setup and processes camera-stream images for real-time hand
landmarks. Its reference code uses live-stream mode, sends monotonically
timestamped frames asynchronously, and allows the detector, presence, and
tracking confidence thresholds to be configured. The official Python API notes
that live-stream inference may drop input frames to reduce latency, so the
capture loop must tolerate skipped landmark results.

For the existing application, the practical pipeline is: Picamera2 frame,
downscaled RGB copy for hand landmarks, landmark result smoothing, a palm
coordinate frame from wrist and index/middle/ring/pinky MCP points, affine or
perspective warp into a fixed-size palm image, then the existing grayscale,
percentile normalization, quality check, and FastCC matcher. A missing or low-
confidence hand result should produce an explicit unknown/error state rather
than silently reusing a stale ROI indefinitely.

Palmprint ROI work describes keypoint-based extraction as a common route for
orientation correction and faster localization. The PLOS One method builds a
coordinate system from two finger-valley keypoints and extracts a square ROI
relative to their distance; the exact center and scale are application-
dependent. This supports using landmarks to normalize position, scale, and
rotation, but it does not prove that MediaPipe MCP landmarks will preserve
Fast-CC accuracy on this Pi camera setup.

The first implementation should therefore use a conservative landmark-derived
quadrilateral rather than a learned palm segmentation network. A segmentation
or lightweight detector/keypoint model is a later option if landmarks fail on
the actual hand pose, lighting, or NoIR image. The current Pi has no MediaPipe
or OpenCV Python module installed, so the installation path, Python ABI, model
asset, and runtime cost remain an empirical gate.

## Insights

- A landmark-derived affine crop solves translation, scale, and rotation
  together; merely following a bounding box solves translation and scale but
  leaves palm orientation and finger inclusion unstable.
- Landmark inference should be decoupled from Fast-CC processing: run it on a
  reduced-resolution copy or asynchronously, while the matcher receives the
  full-resolution frame warped by the latest valid pose.
- The correct failure behavior is `UNKNOWN` when tracking confidence or
  geometry quality is insufficient; a stale ROI can turn a hand movement into
  an apparently valid biometric match.

## Strongest objection

MediaPipe's official Pi example establishes a runnable hand-landmark path, not
the latency or recognition benefit of a dynamic palmprint ROI on this exact
Camera NoIR/Picamera2/Fast-CC stack. A landmark model may also be less reliable
under near-infrared illumination or unusual hand poses, so the fixed ROI must
remain as a comparison and fallback during the preflight.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| Whole-hand bounding box only | Does not normalize palm orientation or define a stable palmprint region | 2026-09-13 |
| Immediate learned YOLO/UNet palm detector | Adds model/weight/training complexity before the lightweight landmark path is tested | 2026-09-13 |

## Open questions

- Which Python version is active on the Pi, and which MediaPipe ARM64 wheel is
  compatible with it?
- What FPS and end-to-end latency does Hand Landmarker achieve alongside the
  existing Picamera2 preview and Fast-CC matcher?
- Should the dynamic ROI replace the fixed ROI, or should the first pilot run
  both paths on the same frames?
- Which landmark-derived crop dimensions preserve the enrolled Fast-CC
  template quality across repeated hand placement?

## Timeline

- 2026-09-13 - Compared official MediaPipe Raspberry Pi hand tracking with
  landmark-based palm ROI extraction and checked the current Pi dependencies.
