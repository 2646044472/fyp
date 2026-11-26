# FPN + C E10: Standalone 60-Second Capture Station

This **native PyTorch** capture and verification demo uses frozen FPN palm cropping and C E10 features. Port **8080** serves the local photo library, the top match candidate, and a demo decision. The recognition threshold for live camera images still needs calibration.

## Before starting

1. Follow the [native dependency and manifest instructions](fpn-c-e10-shadow.md) to prepare a separate Python environment and run preflight. Both models must come from an authorized local source, and their SHA-256 hashes must match the trusted release manifest. The repository does not include models, completed manifests, data, or templates.
2. Free the camera. Make sure the legacy 8088 station is not in the middle of an enrollment and has released the camera. Then run the new station on the Pi or on the Linux development computer connected to the camera. This entry point does not stop other programs. Do not let two processes control the same camera.
3. Choose a **new private directory with mode 0700**. Do not reuse an old capture or template directory. The station binds templates to the model hashes. If you change models, use a new directory and enroll again. Do not commit templates or manifests to Git.

```sh
mkdir -m 700 -p "$HOME/.local/share/fpn-c-e10-v3-local"
python fpn_c_e10_station.py \
  --manifest /PATH/TO/LOCAL/manifest.json \
  --runtime "$HOME/.local/share/fpn-c-e10-v3-local" \
  --uvc-device /dev/v4l/by-id/YOUR-CAMERA-video-index0 \
  --uvc-native-size 2592 1944
```

Run the commands from `code/rasp/`. The UVC options must point to an actual local Video Capture device, and `--uvc-native-size` must match an MJPEG size listed by `v4l2-ctl --list-formats-ext`. With those options set, the station preserves the original JPEG and uses 640×480 for preview and recognition. For CSI, omit both UVC options; if needed, use `--csi-tuning /PATH/TO/LOCAL/tuning.json`. The process loads dependencies and models before opening the camera. It exits with a nonzero status if the device is incompatible; it does not silently fall back to the old models. The station binds only to `127.0.0.1:8080`. Do not expose it to the LAN or public internet.

## Validate enrollment and scoring

- Open the [8080 enrollment page](http://127.0.0.1:8080/enroll) and check for **FPN + C E10**. [`/station-health`](http://127.0.0.1:8080/station-health) reports `backend: fpn-c-e10-frozen`, `mode: scores_only`, and device readiness. A `ready: true` result does not mean just any frame is suitable for enrollment. The camera preview runs independently, and FPN processes only the most recent pending frame. Stale frames are not reused. If you see `fpn_frame_stale`, check actual inference time on the Pi.
- From Yesand, use port 8080 on both the local computer and the Pi. Run `ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:8080 PI_SSH_ALIAS`, replacing `PI_SSH_ALIAS` with your Pi SSH alias. Verify the backend at `/station-health`, then open the same enrollment URL.
- Click **Start capture** to open the camera. Once it is ready, preview for five seconds before starting at least 60 seconds of active capture. Preview and pause time do not count. The capture section shows separate statuses for the current palm crop and the latest frame attempt. You can continue after the timer ends. Once you have 10 usable candidates, click **Select 10 photos**. The final selector checks sharpness, contrast, and exposure. It also compares overall quality and angle diversity when individual photos are replaced. The camera is released when selection is complete, paused, or canceled. Click **Confirm and save** to add the 10 selected groups to the photo library. For first-time enrollment, the five highest-ranked groups build the template. Capturing again with the same participant ID and hand adds photo records and keeps the existing verification template.
- On the capture page and in the [photo library](http://127.0.0.1:8080/collect), each group shows the original camera image, the rectified color ROI cropped from the quadrilateral in that same frame, and the 128×128 grayscale ROI read by the model. In the review dialog you can switch among the three views, zoom, or hide the quadrilateral overlay on the original image. Remove pending candidates and recapture only the missing slots. Once saved, the images are under `enrollment_pairs/<archive-id>/` within the `--runtime` directory, with dimensions and a pairing manifest for each group.
- In the library, search by display name or participant ID. Expand a group to edit its display name, participant ID, or captured hand. These edits apply to the photo record; the verification page still uses the enrollment template information. You can delete a whole session or one photo and both of its ROIs. Deleted files are moved to the device's local trash directory.
- On the [verification page](http://127.0.0.1:8080/gate), click **Start verification** to open the camera. The station compares each fresh, valid palm crop until you click **Stop verification**. Each template's score is the maximum cosine similarity across its five enrollment samples. A unique top score at or above the demo threshold displays **Match**. The service default is **0.80**, configurable with `--match-threshold`. The page's slider and number field override the threshold in that browser and update the decision for the most recent frame. The threshold for real camera use still needs calibration.
- With authorized live samples, validate enrollment, review, deletion and recapture, status refresh, explicit saving, and fresh scores after removing the hand. Measure CPU memory use, sustained frame processing, and latency. The new scoring path cannot load legacy templates, and the old system's threshold must not be reused for deployment.

Synthetic test (no physical camera, checkpoints, or real palmprints):

```sh
python verify_fpn_c_e10_station.py
```

This exercises the actual V3 HTTP enrollment flow with synthetic pixels and replacement models. It checks original/ROI pairs from the same frame, deletion and recapture, manual confirmation, rejection of templates from a different model version, and address and route boundaries. The separate `verify_fpn_c_e10_native.py` test exercises the real PyTorch model architecture with synthetic inputs.
