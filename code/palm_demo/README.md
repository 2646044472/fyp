# Pi 5 Minimal Palm Demo

This is a local-only, fixed-stand `1:1` palm verification baseline for Raspberry Pi 5. It supports separate RGB and NoIR-plus-IR-light capture profiles. It proves only that the local pipeline can acquire a frame, create a template, compare a probe and log the result. It is not a liveness detector, a door controller, a cross-device result, or a security claim.

Read [Pi 5 Safety Checklist](PI5_SAFETY_CHECKLIST.md) before powering the board or connecting the camera ribbon.

For a board without HDMI/keyboard, use [USB-C direct connection](USB_C_DIRECT_SETUP.md) first. It gives the Pi a USB network connection to this PC for SSH; Wi-Fi is only a fallback. [HEADLESS_FIRST_BOOT.md](HEADLESS_FIRST_BOOT.md) has the normal Wi-Fi route.

## What is included

- `palm_demo.py`: enrollment, 1:1 verification and local JSONL timing logs.
- `install_pi.sh`: Pi OS Bookworm setup plus a pinned Fast-CC baseline checkout.
- `install_usb_offline.sh`: installs the bundled ARM64 Python wheels without PyPI/network access.
- `OFFLINE_RESOURCES.md`: USB copy and offline-install instructions.
- `enable_ssh_remote.sh` and `SSH_REMOTE.md`: enable and use local-network SSH after the Pi is online.
- `USB_C_DIRECT_SETUP.md` and `windows/rpi-usb-gadget-driver-setup.exe`: direct USB-C SSH setup for Windows and Pi OS Trixie.
- `tools/prepare_palmbigdata.py`: makes a small development subset from the supplied `../data/PalmBigDataBase.zip` without redistributing it.
- `tools/calibrate_palmbigdata.py`: calculates a development-only threshold and pair-count record.

The command-line demo stores compressed Fast-CC template samples under `runtime/templates/`; it stores camera frames only when `--save-crop` is explicitly used for local debugging. The collection page below explicitly saves diagnostic images. Delete a user by deleting that user's `.npz` and `.json` files together.

## Basic simulated-payment page

On the connected Pi, open `http://10.12.194.1:8080/demo`. Enroll a named test account with five consecutive 3280×2464 stills, then capture one still to search the small local gallery. The page displays the actual 128×128 palm ROI sent to DoN. Because the present same-person left/right scores overlap, the result is explicitly a **candidate**. A person must confirm the displayed name before MOP 20 is deducted from the simulated balance. A wrong name can be cancelled and re-shot. The page does not require a stability wait or hand removal. Its templates and SQLite balance are isolated under `runtime/demo_templates/` and `runtime/demo_payment.sqlite3`; the capture images are not retained by this flow. This is an end-to-end interaction demo, not a validated automatic biometric payment decision.

## Full-resolution collection page

On the USB-connected Pi, open `http://10.12.194.1:8080/collect` while `palm-debug-ui.service` is running. The page shows a live 480x360 preview and captures 3280x2464 stills from the current IMX219 camera. The preview now explicitly uses the sensor's 1640x1232 full-field binned mode; the previous automatic 640x480 mode cropped the sensor and gave a misleading zoomed view. Enter a participant code, left or right hand, and background once per 10-image batch; distance and notes are optional. After starting a batch, capture immediately when the hand is in view: this collection route does not wait for the five-frame quality gate or reject a still solely because no palm ROI was detected. The hand can remain in view while taking all ten images. A batch can be abandoned and restarted; previously captured files remain on the Pi. A finished batch downloads as one ZIP.

Each image is saved under `runtime/highres_capture/<sample_id>/` as `full.jpg`, `preview.jpg`, and `metadata.json`. The still is independently downsampled for hand detection after capture; when that succeeds, the page also saves `roi_128.png`, a 128x128 crop from the full still, and `palm_detail_512.jpg`, a 512x512 native-pixel patch around it. The collection page displays both and includes them in the ZIP. If still-image detection fails, the full still is kept and the page reports that no automatic crop was generated. These are capture diagnostics: the live verifier still extracts its feature from the preview frame. Its session manifest is in `runtime/highres_sessions/<session_id>/manifest.json`. Metadata includes camera exposure and gain, plus browser time because the Pi clock may drift when offline. Inspect the diagnostic crop and native detail after each shot. Click the full image for another 512-pixel native crop.

Templates enrolled with the old cropped preview cannot be verified under the full-field preview and must be re-enrolled. Existing images and templates are retained.

For a focus check, keep the palm at the intended use distance and compare original line detail before deciding whether a larger algorithm ROI or a camera change is useful. This page saves diagnostic images; template enrollment remains a separate action.

## Pi setup

### SSH deployment credential

The current Raspberry Pi SSH username is `fyp`. Before using SSH or SCP, ask the user for the current password. The password is intentionally not stored in this README, scripts, Git, deployment archives, or logs.

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
chmod +x install_pi.sh
./install_pi.sh
rpicam-hello -t 0
```

If you want to prepare everything on a USB first, use `install_usb_offline.sh` on the Pi instead of `install_pi.sh`. The USB package includes NumPy/SciPy/Pillow wheels and the baseline source. Picamera2/libcamera remains a Raspberry Pi OS system component; install it once with `sudo apt install -y python3-picamera2` if it is not already present.

Use `rpicam-hello --list` to identify the camera index, then preview each camera separately, for example `rpicam-hello --camera 0 -t 0`. Keep the palm centred and parallel to the camera, with consistent light. The default crop assumes that physical setup; adjust `--crop left,top,right,bottom` after checking a local debug crop.

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
