# Headless Raspberry Pi Setup

You can set up and control the Raspberry Pi remotely without an HDMI cable, monitor, keyboard, or mouse.

## Prepare the SD Card on Your Computer

1. Download and open [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Insert the 64 GB SD card into your computer.
3. Choose `Raspberry Pi OS Lite (64-bit)`.
4. Select the SD card, then open the settings or customization panel.
5. Configure the following:
   - Hostname: `palm-pi`
   - Username: choose one, for example `piuser`
   - Password: set and remember your own password; do not send it in chat
   - Wi-Fi: enter the network name and password used by your computer
   - Country: China
   - Remote Access: enable `SSH` and choose `Use password authentication`
6. Write the image. When it finishes, safely eject the SD card.

## Start the Pi

1. With the Pi powered off, insert the SD card and connect the cooler and camera.
2. Connect power to start the Pi.
3. Wait about two minutes for it to join Wi-Fi.

## Connect from Your Computer

Open Windows PowerShell and run:

```powershell
ssh <your-username>@palm-pi.local
```

For example, if your username is `piuser`:

```powershell
ssh piuser@palm-pi.local
```

The first time, type `yes` when asked to trust the host, then enter the password configured in Imager. The password will not appear as you type; this is normal. Once connected, the terminal is running on the Pi.

If `palm-pi.local` does not connect:

1. Check that the computer and Pi are on the same Wi-Fi network.
2. Wait two minutes and try again.
3. Find the Pi's IP address in your router's device list, then run:

```powershell
ssh <your-username>@192.168.x.x
```

## Install the USB Package

After connecting over SSH, insert the USB drive containing `palm_demo_pi.zip` into the Pi. In the SSH window in PowerShell, run:

```bash
ls /media/$USER
cp /media/$USER/*/palm_demo_pi.zip ~/
unzip ~/palm_demo_pi.zip -d ~/palm_demo
cd ~/palm_demo
chmod +x install_usb_offline.sh
./install_usb_offline.sh
```

If `unzip` is missing, connect the Pi to the internet once and run:

```bash
sudo apt update
sudo apt install -y unzip python3-picamera2
```

## Connect Again Later

Whenever the Pi is powered on and connected to the same Wi-Fi network, run:

```powershell
ssh <your-username>@palm-pi.local
```

Official reference: [Raspberry Pi getting started documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html).
