# Raspberry Pi 5 Safety Checklist

## Eight Essential Rules

1. Use a **5 V / 5 A USB-C power supply**, preferably the official 27 W supply. Avoid unknown phone chargers.
2. Connect power only to the USB-C port marked `POWER IN`. **Do not power the board through GPIO pins.**
3. Before connecting or disconnecting the camera cable, fan, GPIO devices, or SD card, run `sudo poweroff` and unplug the USB-C supply after shutdown.
4. Never connect or disconnect the camera cable while powered. Do not insert it backwards or at an angle, bend it sharply, or crush it.
5. Use a fan or heatsink during long camera or model runs. Keep the fan inlet and outlet clear.
6. Place the board on a dry, insulated surface or in a Pi 5 case. Keep it away from water, metal, loose screws, and drinks.
7. GPIO uses **3.3 V**. Do not connect 5 V signals, relays, motors, or high-power devices directly.
8. Do not shut down by unplugging power, and do not remove the SD card while powered; either can damage the system or lose data.

## When Connecting the Pi Directly to a Computer over USB-C

- On supported system images, the Pi 5 USB-C port can provide power and a USB network connection. Use a C-to-C cable that supports both data and power, not a charge-only cable.
- For the first test, leave the camera disconnected. If the computer's USB-C port cannot provide enough power, the Pi repeatedly restarts, or a low-voltage warning appears, disconnect it. Use the official 5 V / 5 A supply and connect over Wi-Fi or Ethernet instead.
- Do not connect the official supply and the computer to the same USB-C port at the same time. Never connect or disconnect the camera cable while powered.

## NoIR Camera and IR Illuminator

- Treat the RGB camera and NoIR camera as different capture conditions. Do not mix their templates during enrollment or verification.
- The Pi 5 can connect two cameras. Test them one at a time first: use `rpicam-hello --list` to see camera indices, then `rpicam-hello --camera <index> -t 0` to check the image.
- Do not power or drive the IR illuminator directly from GPIO. Use its intended power supply or driver module.
- IR light may not be visible to the eye, but it can still pose a risk. Do not shine it into eyes at close range. Do not modify the illuminator or increase its supply voltage until its specifications are confirmed.

## Before Connecting a Camera

- Shut down the Pi and unplug its USB-C power supply.
- Open the CSI connector latch gently. Insert the cable fully and straight, then close the latch.
- Make sure the camera board cannot touch metal and the cable is not sharply bent.
- On the first boot, check the camera:

```bash
rpicam-hello -t 0
```

If there is no image, a burning smell, unusual heat, or repeated restarts, disconnect power immediately and check the power supply and camera cable orientation.

## Normal Startup and Shutdown

Startup: connect the camera and fan first, then connect USB-C power.

Shutdown:

```bash
sudo poweroff
```

Wait for the Pi to stop completely before unplugging USB-C power.

## Check During the First Long Run

```bash
vcgencmd measure_temp
vcgencmd get_throttled
```

- `get_throttled=0x0` means no low-voltage or overheating event has been recorded.
- If a low-voltage warning, frequent restart, USB disconnection, or high temperature occurs, stop the run and check the power supply, cable, and cooling first.

Official references:

- [Raspberry Pi 5 documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [Raspberry Pi 5 cooling and heating](https://www.raspberrypi.com/news/heating-and-cooling-raspberry-pi-5/)
