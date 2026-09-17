# Pi 5 Minimal Palm Demo

This is a local-only, fixed-stand `1:1` palm verification baseline for Raspberry Pi 5. It supports separate RGB and NoIR-plus-IR-light capture profiles. It proves only that the local pipeline can acquire a frame, create a template, compare a probe and log the result. It is not a liveness detector, a door controller, a cross-device result, or a security claim.

Read [Pi 5 Safety Checklist](PI5_SAFETY_CHECKLIST.md) before powering the board or connecting the camera ribbon.

For a board without HDMI/keyboard, use the [connection guide](CONNECT_GUIDE.md) for USB-C direct SSH or Wi-Fi/Ethernet SSH. [HEADLESS_FIRST_BOOT.md](HEADLESS_FIRST_BOOT.md) covers the normal Wi-Fi first boot.

## Current USB-C SSH connection

Verified on 2026-09-13 over the direct USB-C network link:

```text
Host:     rasp4 (10.12.194.1)
Username: fyp
Password: fypfypum
```

Connect from this development PC with:

```powershell
ssh fyp@10.12.194.1
```

This password is stored here only for the private direct USB-C lab link. Change it before exposing the Pi to Wi-Fi or any other LAN.

## Reliable ROI acquisition milestone

The dynamic Pi UI uses the synchronized `palm-detector-mcp-v2` ROI implementation. The UI reports four capture states: `NO_HAND`, `TRACKING`, `LOW_QUALITY` and `READY`. Dynamic Enroll and Verify are enabled only after five fresh, in-bounds, sufficiently contrasted and sufficiently sharp ROI frames pass the current engineering gate. The five-frame requirement and quality thresholds are engineering parameters for this milestone; they are not a validated optimum.

`tracking_lost`, `tracking_stale` and other non-ready tracker states clear the accepted ROI. Enroll and Verify wait for a new processed frame, so they cannot use the previous successful ROI after tracking is lost.

Use **Capture debug sample** for the repeatability check. Each click saves one event under `runtime/debug_capture/<session>/sample_###/`:

```text
raw.png
roi_128.png
metadata.json
```

The saved ROI is the exact 128×128 uint8 array produced by the same normalization path used before the matcher. Metadata records the frame ID, capture times, ROI quadrilateral, tracker and quality states, quality metrics, camera settings, detector geometry version, and artifact hashes. After each saved sample the gate resets and the UI waits for a `NO_HAND` observation; remove and replace the palm before waiting for `READY` and capturing the next sample. Ten samples complete one debug dataset.

## What is included

- `palm_demo.py`: enrollment, 1:1 verification and local JSONL timing logs.
- `install_pi.sh`: Pi OS Bookworm setup plus a pinned Fast-CC baseline checkout.
- `install_usb_offline.sh`: installs the bundled ARM64 Python wheels without PyPI/network access.
- `OFFLINE_RESOURCES.md`: USB copy and offline-install instructions.
- `CONNECT_GUIDE.md`: USB-C and local-network SSH setup, IP discovery, and login.
- `enable_ssh_remote.sh`: enable SSH locally on an already-running Pi.
- `debug_ui.py`, `palm_roi.py`, `live_roi.py`, `roi_quality.py`: dynamic ROI tracking, quality gating, and reproducible ROI capture.
- `windows/rpi-usb-gadget-driver-setup.exe`: Windows driver for direct USB-C networking.
- `tools/prepare_palmbigdata.py`: makes a small development subset from the supplied `../data/PalmBigDataBase.zip` without redistributing it.
- `tools/calibrate_palmbigdata.py`: calculates a development-only threshold and pair-count record.

The demo stores compressed Fast-CC template samples under `runtime/templates/`; it does not store camera frames unless `--save-crop` is explicitly used for local debugging. Delete a user by deleting that user's `.npz` and `.json` files together.

## Pi setup

On the development PC, create the clean deployment archive (it excludes local templates, logs and derived data), transfer `dist/palm_demo_pi.zip` to the Pi, then unzip it:

```powershell
./make_deploy_bundle.ps1
```

```bash
unzip palm_demo_pi.zip -d palm_demo
```

Then run:

```bash
cd palm_demo
chmod +x install_pi.sh run_palm_demo.sh
./install_pi.sh
rpicam-hello -t 0
```

If you want to prepare everything on a USB first, use `install_usb_offline.sh` on the Pi instead of `install_pi.sh`. The USB package includes NumPy/SciPy/Pillow wheels and the baseline source. Picamera2/libcamera remains a Raspberry Pi OS system component; install it once with `sudo apt install -y python3-picamera2` if it is not already present.

Use `rpicam-hello --list` to identify the camera index, then preview each camera separately, for example `rpicam-hello --camera 0 -t 0`. Keep the palm centred and parallel to the camera, with consistent light. The default crop assumes that physical setup; adjust `--crop left,top,right,bottom` after checking a local debug crop.

For the research camera capability gate, run `tools/camera_capability_preflight.sh` on the Pi. It writes a timestamped manifest and sample files; inspect the help/output logs before treating RAW or RAW/JPEG pairing as available.

## RGB and NoIR setup

The Pi 5 can connect both cameras directly. Start with one camera at a time, not simultaneous capture. Record the physical mapping once with `rpicam-hello --list`; do not assume connector order equals camera index.

| Setup | Example command | Rule |
| --- | --- | --- |
| RGB camera + visible light | `--camera 0 --capture-profile rgb` | Enroll and verify only against RGB templates. |
| NoIR camera + IR fill light | `--camera 1 --capture-profile noir-ir` | Enroll and verify only against NoIR+IR templates. |

The program refuses a profile mismatch during verification. NoIR+IR is a different observation condition, **not** automatic palm-vein recognition, liveness detection, anti-spoofing or a CASIA multispectral equivalent. If both cameras run together later, their auto-exposure/white-balance operations are not synchronised; treat each capture as a separate logged observation.

## First demo

Enroll five samples, then run a separate verification capture:

```bash
python3 palm_demo.py --authorized-local-biometric --camera 0 --capture-profile rgb enroll --user demo-rgb --samples 5 --interactive
python3 palm_demo.py --authorized-local-biometric --camera 0 --capture-profile rgb verify --user demo-rgb
python3 palm_demo.py users
```

For NoIR+IR, use a separate identifier and profile, for example `--camera 1 --capture-profile noir-ir --user demo-noir`.

`ACCEPT`/`REJECT` is reported with the Fast-CC distance, threshold and local pipeline time. An exit status of `2` means a normal rejection. The default threshold is deliberately labelled provisional. It exists for a same-stand smoke test only.

The authorization switch is intentionally mandatory for camera enrollment and verification. Use it only after the supervisor/institution permits this local test and the participant has consented. It is a safeguard in the demo, not a substitute for ethics approval.

## Development-data check

On the development PC, install the lightweight dependencies and create a 20-identity subset from the archive supplied by the PhD student:

```powershell
python -m pip install -r requirements-dev.txt
git clone https://github.com/Li-ChengYan/palmprint-recognition-python.git .\vendor\palmprint-recognition-python
git -C .\vendor\palmprint-recognition-python checkout d556f455a6cbdcb4264ec1cd75de2e451cf241b3
python tools/prepare_palmbigdata.py --confirm-authorized-dataset
python tools/calibrate_palmbigdata.py
```

The calibration script treats the `P_F_<identity>_<sample>.bmp` naming convention as an identity label. It creates a manifest and threshold record, but it does **not** establish accuracy on the Pi camera. Do not publish or move the supplied archive or derived images unless its source terms permit it.

## Baseline choices

The current runtime baseline is Fast-CC from `Li-ChengYan/palmprint-recognition-python`, pinned to commit `d556f455a6cbdcb4264ec1cd75de2e451cf241b3` (2026-04-19, MIT). It uses two Gabor directions and shifted Hamming distance, so it needs neither a GPU nor opaque pretrained weights. The project itself says it is an independent implementation rather than an official reproduction; its benchmark numbers must not be treated as ours.

PPNet remains a useful research comparison rather than the initial Pi dependency: its repository has a Pi guide and pretrained-model links, but its tested stack is Python 3.7-3.8/PyTorch 1.2-1.7 and the released workflow is not the current camera demo. X-Palm is the preferred later dataset/protocol route for the actual cross-domain research question, after its academic EULA is accepted; its training benchmarks use an RTX A6000 and are not a Pi runtime baseline.

Sources: [Fast-CC implementation](https://github.com/Li-ChengYan/palmprint-recognition-python), [PPNet](https://github.com/xuliangcs/ppnet), [X-Palm](https://github.com/X-Palm/X-Palm-2026), [Raspberry Pi camera documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html).
