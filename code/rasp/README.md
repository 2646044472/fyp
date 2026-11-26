# Raspberry Pi Palmprint Capture Station

This page documents the **legacy Pi 5 capture station on port 8088**. See [60-second enrollment and troubleshooting](capture-60s.md) for capture timing, candidate ranking, and original/ROI review.

The legacy station provides a local capture interface and deployment code; it is not a standalone recognition model. It uses the existing **PKLNet + FastCC v6** engine rather than the **FPN + C E10** build on X. It does not change verification thresholds. Photos, ROIs, enrollment templates, capture records, and models are not distributed in this directory.

| Page | What it does |
| --- | --- |
| `/enroll` | Continuously previews the camera and selects five sharp, complementary photos from valid ROIs. You can enlarge an original image or ROI, remove a pair and its candidate features, and recapture only what is missing. Enrollment is submitted only after you click **Confirm and save** for the same hand. |
| `/gate` | Tries verification once when a palm is presented. Remove the hand to start another attempt. |
| `/collect` | Manages capture records locally on the Pi. |

Legacy enrollment lasts at most 60 seconds after you click **Start capture**. The server's 59-second capture limit includes replacement frames. Once five photos are available, the station briefly checks the existing candidates and can normally finish early. If fewer than five are available, you can review what it captured. After you confirm, the five final original/ROI pairs are written to `runtime/enrollment_pairs/<archive-id>/` on the Pi as a JPEG and PNG per pair. The station does not save the entire video.

To try the new baseline, use the [standalone FPN + C E10 capture station](fpn-c-e10-station.md) on **port 8080**. It runs native PyTorch, uses V3 enrollment and review, stores originals, ROIs, and templates separately, and displays matching scores for demonstration. Use the [standalone command-line tool](fpn-c-e10-shadow.md) for a local preflight. The deployment and rollback instructions below apply to the legacy station on port 8088. Do not let the two stations use the same camera at the same time.

## Develop on another computer

If you have not cloned the repository, you can check out only the app code and skip the repository's historical data directory:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --sparse https://github.com/2646044472/fyp.git
cd fyp
GIT_LFS_SKIP_SMUDGE=1 git sparse-checkout set code/rasp
cd code/rasp
```

If you already have a clone, update `main`. The logic and regression checks run on a regular computer with Python 3; they do not need a Pi, model files, a camera, or real samples:

```sh
python3 verify_best_frame.py
python3 verify_review.py
python3 verify_ranked_window.py
python3 verify_adapter.py
bash -n install-on-pi.sh && bash -n rollback-on-pi.sh
```

- `capture_station.py` serves the three pages, provides the user service entry point, and handles capture station requests.
- `enrollment_best_frame.py` connects to the base recognition engine; `ranked_window.py` selects frames; `enrollment_window_adapter.py` manages starting, stopping, timeouts, and recapture; `enrollment_review.py` manages originals and ROIs pending confirmation.
- `palm-capture-station.service` is a **user** systemd unit. `palm-capture-station.env.example` is a camera configuration template without machine-specific settings.

## Deploy to Pi 5

See the [recognition engine guide](ENGINE-README.md) for the base app's configuration, dependencies, and rollback steps. The legacy station expects `${HOME}/palm_demo`, a working `.venv/bin/python` in that directory, and local PKLNet/FastCC v6 models. The base engine source is also in this directory. When preparing a new Pi, deploy the source here to the runtime directory without overwriting any local models, settings, or capture data. The capture station does not install the base models or system dependencies. Before deploying, verify imports in the Pi's base app virtual environment. This command does not open the camera:

```sh
(cd "$HOME/palm_demo" && .venv/bin/python -c 'from palm_app import debug_ui; from demo_flow import enrollment_quality_issue; assert "enrollment_quad" in debug_ui.ProcessedFrame.__dataclass_fields__, "sync compatible camera module before v3 install"')
```

**Updating an installed station:** The base runtime directory needs compatible camera code first. Back up the local base app and capture station, update the complete base app from a compatible source revision as described above, and verify the import check. Do not overwrite a single base module with one from another version. Save or finish any enrollment in progress, then run `bash install-on-pi.sh` from this directory on the Pi. The script runs checks, backs up the code, and restarts the user service. It rolls back if the page does not recover. A responsive page does not prove that the camera is ready; do the hardware checks below. The script does not modify enrollment data or models. Restarting discards unsaved candidates. To roll back manually, run `bash rollback-on-pi.sh <backup-directory-printed-by-the-installer>`.

**Fresh Pi (cloning alone is not enough):** Set up the base engine, camera dependencies, and authorized models first. Confirm the following before installing the station as a user service:

1. The service uses `$HOME/palm_demo/.venv/bin/python`, not `.venv-pklnet`. The environment must be able to import `onnxruntime` and the base engine's OpenCV, NumPy, Pillow, and camera dependencies. The old `deploy/install_pi.sh --with-pklnet` command installs PKLNet dependencies into a different environment and does not replace this check.
2. Obtain the matching three files from an authorized local source: `net_params_500.pth`, `pklnet-keypoints-diagnostics.onnx`, and `pklnet-keypoints-diagnostics.json`. Put them in the `pklnet/` directory next to `$HOME/palm_demo` (preferred if present) or in `pklnet/` inside the app directory. The engine checks the original weights and ONNX hashes listed in the JSON file. The older export guide's `pklnet-keypoints.onnx` is not the diagnostic version used by the current default crop policy. Do not distribute model files through Git or shared attachments without permission.

Once the base app and dependencies are ready, install the code and service from this directory on the Pi. User permissions are sufficient:

```sh
install -d -m 700 "$HOME/.local/share/palm-capture-station" "$HOME/.config/systemd/user"
install -m 600 capture_station.py enrollment_archive.py enrollment_best_frame.py enrollment_review.py ranked_window.py enrollment_window_adapter.py "$HOME/.local/share/palm-capture-station/"
install -m 644 palm-capture-station.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
```

For a USB camera, use `v4l2-ctl --list-devices` to find the actual Video Capture node. Set its stable device path in `~/.config/palm-capture-station.env` on the Pi using the provided template. Do not copy a device path from a different machine. Check supported MJPEG modes with `v4l2-ctl --list-formats-ext`, then set a supported size such as `PALM_STATION_UVC_NATIVE_SIZE=1600x1200`. Preview and matching use smaller images, while the archive keeps the camera's original JPEG. Changing format or resolution may require re-enrolling legacy templates.

Power off before connecting a CSI ribbon cable. The existing high-resolution capture path is the default; enable the optional continuous CSI mode only after validating it on the device. If the old `palm-debug-ui.service` is using the same camera, stop it on the Pi before starting the station. The two services must not compete for the camera. When ready, run `systemctl --user start palm-capture-station.service`. Boot behavior and startup order depend on the deployment; this directory does not change old services or user login policies automatically.

An older base app may lack `enrollment_quality_issue` or use different status fields. If the import fails, or the page loads but never keeps candidates, check the compatibility of the base app and capture station first. Do not relax verification thresholds. Local USB camera settings and temporary compatibility patches on the field Pi are not synchronized here. This directory is not an exact backup of that Pi.

## On-site validation and access

On the Pi, open the [enrollment page](http://127.0.0.1:8088/enroll). If your computer can reach the Pi over SSH, run `ssh -N -L 127.0.0.1:8089:127.0.0.1:8088 <user>@<pi-host>` and open [local port 8089](http://127.0.0.1:8089/enroll). Leave the station bound to the loopback interface; do not expose it to the public internet.

Check that `systemctl --user is-active palm-capture-station.service` returns `active` and that the preview updates rather than staying on the waiting screen. With a consenting participant's test ID, preview an enrollment, inspect the original and ROI, remove and replace one pair, save manually, and remove the hand. Verify the same palm, then confirm that an unenrolled palm is not accepted. The request time shown in the browser excludes the time to present the hand and obtain a usable ROI, so it is not end-to-end latency. Repository tests cover software flow; they do not prove live capture, recognition accuracy, or hardware speed.

Do not commit original images, ROIs, templates, runtime logs, models, private keys, or device-specific camera settings.
