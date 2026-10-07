# Pi setup

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
python3 debug_ui.py --help
```

Install unzip through apt if missing. The installer installs system camera and
Python dependencies and checks out the pinned matcher. Verify camera indices
separately. SSH gives a terminal, not preview; rpicam-hello --camera <index> -t 0
needs a usable display. Keep palm framing, distance and light consistent.

The offline installer is archived and is not supported by current deployment
bundles. Use the online installer; keep Picamera2/libcamera as matching OS
components. Bundles exclude templates/logs/datasets. Respect source restrictions.

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
