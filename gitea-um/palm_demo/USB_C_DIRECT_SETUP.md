# Headless SSH over a Direct USB-C Connection

This setup is for a Raspberry Pi 5, a Windows computer, and a USB-C to USB-C cable that supports data. The computer detects the Pi as a USB network device, allowing an SSH connection without HDMI, a keyboard, or a router.

## Prepare the Computer Once

Run the official driver installer in this directory:

```text
windows/rpi-usb-gadget-driver-setup.exe
```

Follow the Windows installer. The new network adapter appears only when a correctly imaged Pi is connected.

## Write the SD Card

1. Install or update **Raspberry Pi Imager** on the computer.
2. Choose the latest **Raspberry Pi OS Lite (64-bit, Trixie)**. Do not use an older Bookworm image for this procedure.
3. Open the settings, set the hostname to `palm-pi`, and configure a username and password. Enable SSH with password authentication. You may also configure Wi-Fi, but the direct USB-C connection does not depend on it.
4. In the same settings, enable **USB Gadget Mode** (USB networking). This option is available only in sufficiently recent Trixie images. If it is missing, update Imager and the OS image before writing the card.
5. When writing is complete, safely eject the SD card.

## Connect and Sign In

1. With the Pi powered off, insert the SD card. For the first test, leave the camera disconnected.
2. Use a C-to-C cable to connect the computer and the Pi's USB-C port. This connection also powers the Pi, so do not connect the official supply at the same time.
3. Wait about two minutes, then run this in Windows PowerShell:

```powershell
ssh <your-username>@palm-pi.local
```

For example, if the username is `pi`:

```powershell
ssh pi@palm-pi.local
```

The first time, confirm the host fingerprint by typing `yes`, then enter the password configured in Imager.

After signing in, insert the USB drive into a regular USB-A port on the Pi and deploy `palm_demo_pi.zip`. Once SSH is stable, run `sudo poweroff` and wait for shutdown before connecting the camera cable.

## If the Connection Fails

- Check that the cable supports data and is not charge-only. Try another data cable.
- Confirm that the OS is Trixie and USB Gadget Mode was enabled when the SD card was written. An older image will not become a USB network device just by connecting a cable.
- Repeated restarts, an abnormal red LED, or USB disconnect messages may indicate that the computer cannot provide enough power. Disconnect the cable, use the official supply, and connect over Wi-Fi or Ethernet instead.
- Never connect or disconnect the CSI camera cable while the Pi is powered.

Official reference: [USB Gadget Mode in Raspberry Pi OS](https://www.raspberrypi.com/news/usb-gadget-mode-in-raspberry-pi-os/).
