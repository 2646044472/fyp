# Pi setup

## Pi 5 connection repair and replay verification (2026-10-27)

Verified host: `rasp5`, user `fyp5`, Wi-Fi `192.168.31.55`, USB `10.55.0.1`.
Wi-Fi addresses can change. The USB fault was reproduced with UDC `configured`
and a working Windows RNDIS driver, while `usb0` was down and NetworkManager
reported reason 77 (unmanaged through udev). Debian's
`85-nm-unmanaged.rules` sets `NM_UNMANAGED=1` on USB gadget devices.

The scoped override in `deploy/90-usb-gadget-managed.rules` lets NetworkManager
activate the existing `usb-gadget` profile (`10.55.0.1/24`, IPv4 shared mode).
It was installed in `/etc/udev/rules.d/`, rules reloaded and the `usb0` change
event triggered, then `nmcli device set usb0 managed yes` and
`nmcli connection up usb-gadget` applied. Windows received `10.55.0.27` by DHCP;
SSH and HTTP were verified over USB. No EEPROM change or reboot was needed.

The connected UVC camera delivered a real 2592x1944 still and 640x480 preview.
Unplugging it exposed a stale-status defect: a cached JPEG was still advertised
as a ready camera. The application now marks frames older than five seconds
unavailable, returns HTTP 503 for a stale preview, and rejects an already-stale
full-still request before waiting on the camera lock. This does not implement
automatic UVC hotplug recovery: restart `palm-debug-ui` after a disconnection.
Its startup script waits for the camera to be connected again.

Under concurrent camera and inference load, the kernel recorded undervoltage
and `get_throttled` reached `0x50005`. After reducing the workload it returned
to `0x50000` (historical flags remain set). Resolve the power supply before
using sustained camera/inference load. These observations do not establish the
cause of a previous boot's freeze, whose journal was not retained.

Runtime code and service configuration were backed up on the Pi under
`/home/fyp5/maintenance-20261027/` before the heatmap-v3 deployment. The service
keeps its capture-only mode. Original captures and production account/template
stores were not used as replay outputs.

Reproduce the complete saved-data HTTP workflow on the Pi with:

```bash
cd ~/palm_demo
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 taskset -c 3 .venv/bin/python \
  tools/replay_pi_pipeline.py /path/to/original-runtime-or-zips /path/to/new-audit
```

The tool replays only the camera input. Collection, ZIP export, ROI inference,
matching, five-image enrollment, held-out identification, confirmed simulated
payment, duplicate/cancel protection and restoration use the actual application
code. It binds temporary HTTP servers to loopback, writes isolated stores and
keeps every probe in the offline denominator. A ranking result on these short
historical bursts is not a calibrated acceptance threshold or independent
validation. The original ZIP directory is incomplete locally: four of the
twelve sessions in `sessions.json` are available, giving 40 images for this run.

## Pi 5 deployment (2026-10-20)

Host `rasp5`, user `fyp5`, application `/home/fyp5/palm_demo`. Wi-Fi IP at
deployment: `10.176.249.94` (may change); use `rasp5.local` when available.
The installed USB Ethernet gadget uses `10.55.0.1/24`, with NetworkManager
shared mode assigning a connected computer an address automatically. Connect
a data-capable cable to the Pi's USB-C port. USB enumeration and Windows driver
operation were verified after updating EEPROM from 2026-05-26 to the default
stable 2026-09-25 release: UDC `configured`, Windows DHCP `10.55.0.27`, SSH
from that address to `10.55.0.1`, and HTTP root/status both 200. The same cable
worked after updating. Ensure suitable
Pi 5 power; do not improvise multiple power supplies.

`deploy/palm-debug-ui-pi5.service` is installed as `palm-debug-ui.service`.
It starts `deploy/start_camera_service.sh`, waits for a libcamera camera, then
runs the full-resolution collection UI on port 8080. The attached USB UVC camera
is recognized through libcamera; status reports fresh frames, no error and
1920x1080 capture size. Full still capture is not yet verified. It uses the camera's
default tuning rather than the historical Pi 4 IMX219 NoIR tuning override.
For a different camera index, create `deploy/camera.env` containing
`PALM_CAMERA_INDEX=0` (or the detected index), then restart the service.

Power off and unplug the Pi before changing CSI camera cables. After boot, check
`rpicam-hello --list-cameras` and `journalctl -u palm-debug-ui -n 30`.
This application uses Picamera2/libcamera; an arbitrary USB webcam may need a
different capture backend. The current deployment is capture-only, with ROI
processing deferred; optional PKLNet recognition dependencies are not installed.
USB network/boot configuration backups are in `/home/fyp5/usb-gadget-backup/`
on the Pi. Credentials are not stored in the repository.

Run application commands from ~/palm_demo. Last verified USB connection:
2026-09-13, host rasp4, user fyp, IP 10.12.194.1. Discover the current address
if it changed; obtain the password from the owner and keep it out of Git.

## Hardware and first boot

Use suitable Pi 5 power, cooling and an insulated surface. Before changing CSI
ribbons, SD cards, fans or GPIO, run sudo poweroff, wait and disconnect power.
GPIO signals are 3.3 V. IR lights need a suitable separate driver/supply; avoid
close eye exposure. Check long runs using vcgencmd measure_temp and
vcgencmd get_throttled; investigate undervoltage, overheating and repeated resets.

A configured Pi needs no reflash. For a fresh headless setup, use Raspberry Pi
Imager and Raspberry Pi OS Lite 64-bit; configure username/password, hostname,
SSH and your actual Wi-Fi country/network. For direct USB networking, enable
the supported gadget option in your image/Imager and use a data-capable cable.
Allow first boot to complete. If PC power causes USB drops/resets, disconnect
and use supported Pi power with Wi-Fi/Ethernet instead. Avoid improvised power
connections. The optional driver is archived under
`archive/palm_demo_legacy/deploy/windows/` at the repository root.

## Windows connection

```powershell
ssh fyp@10.12.194.1
$piAdapter = Get-NetAdapter | Where-Object InterfaceDescription -match 'Raspberry Pi USB Remote NDIS'
(Get-NetIPConfiguration -InterfaceIndex $piAdapter.ifIndex).IPv4DefaultGateway.NextHop
Get-NetIPAddress -InterfaceIndex $piAdapter.ifIndex -AddressFamily IPv4
Get-NetNeighbor -InterfaceIndex $piAdapter.ifIndex -AddressFamily IPv4
Test-NetConnection 10.12.194.1 -Port 22
```

The PC adapter address is not the Pi address. If needed, scan only the actual
USB subnet; the historical subnet was 10.12.194.0/28. Over LAN use
ssh <user>@<Pi-LAN-IP> or a resolving .local name; hostname -I lists Pi addresses.
No adapter: check cable/power/gadget setup. Reachable IP but closed port 22:
check SSH. Login failure: check credentials. Verify the device before accepting
a new/changed host key. Enable SSH through Imager or systemctl on the Pi.

## Package and install

From code/palm_demo on Windows:

```powershell
./deploy/make_deploy_bundle.ps1
scp .\dist\palm_demo_pi.zip fyp@10.12.194.1:/home/fyp/
```

On the Pi (or copy the ZIP by USB first):

```bash
unzip ~/palm_demo_pi.zip -d ~/palm_demo
cd ~/palm_demo
chmod +x deploy/install_pi.sh
./deploy/install_pi.sh
rpicam-hello --list
.venv/bin/python debug_ui.py --capture-only
```

Install unzip through apt if missing. The installer installs system camera and
Python dependencies and checks out the pinned matcher. Verify camera indices
separately. SSH gives a terminal, not preview; rpicam-hello --camera <index> -t 0
needs a usable display. Keep palm framing, distance and light consistent.

The online installer creates `.venv` with OS camera libraries. The default service
collects full-resolution originals and metadata without ROI or recognition.
PKLNet is optional for offline extraction: `install_pi.sh --with-pklnet` creates
`.venv-pklnet` with the PyTorch and ONNX Runtime dependencies. ONNX is the default
ROI backend and needs the exported model and JSON manifest beside the weights.
For an offline Pi, download matching ARM64/Python wheels on
the PC and install using `--no-index --find-links <wheel-directory>` in this venv.
Keep Picamera2/libcamera as matching OS components. ROI is deferred until analysis;
preserve the previous venv and service configuration when migrating. Bundles
include model weights and exclude templates/logs/datasets.

## Web service

Inspect deploy/palm-debug-ui.service before installing:

```bash
sudo cp deploy/palm-debug-ui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now palm-debug-ui
sudo systemctl status palm-debug-ui
```

The unit assumes user fyp, /home/fyp/palm_demo/.venv/bin/python, camera 0 and the
two ONNX models. Online installation does not create .venv: create it with
system-site packages and required dependencies or set ExecStart to your verified
interpreter. Adjust the unit for another user/path. Open http://<Pi-IP>:8080 on
the local network. Keep credentials and biometric data private.

The historical RAW capability probe is in archive/palm_demo_legacy/tools/.

References: [getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html),
[camera software](https://www.raspberrypi.com/documentation/computers/camera_software.html),
[hardware](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html),
[USB gadget](https://www.raspberrypi.com/news/usb-gadget-mode-in-raspberry-pi-os/).
# PKLNet heatmap policy deployment

For current `pklnet-illumination-consistent-v5` (and historical v4/v3), include `pklnet_policy.py` and the diagnostic ONNX
export `pklnet-keypoints-diagnostics.onnx` with its JSON manifest. The bundle
builder includes both when invoked with `-IncludePKLNet`. Before deploying,
back up the affected code, model files and service configuration on the Pi.
Keep capture-only service settings when the camera is being used for acquisition;
do not switch service modes as a side effect of updating extraction code.

After uploading, instantiate `PKLNetROI(threads=1)` in the Pi's existing venv
and replay at least one saved image. Verify the new geometry version and branch
diagnostics before restarting a recognition service. An offline full replay is
provided by `tools/evaluate_heatmap_policy.py`. Old templates require explicit
re-enrollment; the application retains accounts and balances.

The explicit aspect policy first uses full-frame heatmap output; only invalid
geometry retries on a centered 4:3 inference view, mapping back to original
pixels. Explicit `policy="heatmap"` reproduces v3. Branch disagreement,
contrast and sharpness are diagnostics; bounds and minimum span remain geometry
checks. V4 evidence is `runtime/pi5-roi-v4-20261027/report.html`.
Local replay does not validate Pi latency or camera operation.

V4 was separately validated on Pi using a single CPU core (`taskset -c 3`,
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`) before deployment. On all 40 saved
new-camera images: geometry 40/40, enrollment 4/4, HTTP DoN 13/20, four isolated
simulated payments. Median ROI 1.52 s, p95 3.06 s; no undervoltage flags in this
run. This is historical replay, not a live-camera acceptance test. Source backup:
`/home/fyp5/maintenance-20261027/pre-aspect-v4-231905/`. Deployed file hashes are
in the local evidence directory's `deployment.json`. Service mode stayed
capture-only; originals and production account data were not changed. Geometry
version migration requires re-enrollment before recognition with old templates.

Current v5 (2026-10-28) evaluates original and fixed gamma 0.6 input with that
same aspect routine, using gamma only if it is valid and agrees with an otherwise
valid original quad (IoU >= 0.5). It warps original pixels. Pi replay gives DoN
14/20, FastCC 15/20, 40 valid ROIs, four enrollments and four isolated simulated
payments. Local DoN 15/20 is not identical to Pi: exact Pi pixels also score
14/20 with the local matcher. Median/p95 single-core ROI latency is 3.16/6.22 s.
43 related tests pass. New evidence is `runtime/roi-palmir-20261028/report.html`;
`deployment.json` records the exact backup location, deployed hashes and service
verification. The capture-only service stays unchanged and waits for a camera.
Old templates require re-enrollment, preserving accounts/balances. Existing
PalmIR-style restoration remains optional: complete final-ROI trials showed no
recognition benefit. The scheduled continuation is in this chat (ID `roi-palmir`).
