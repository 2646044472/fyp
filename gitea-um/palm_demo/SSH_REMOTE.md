# Control the Raspberry Pi Remotely

## Requirements

- Raspberry Pi OS 64-bit is installed on the Pi.
- The Pi and computer are on the same Wi-Fi network or connected to the same router by Ethernet.
- You know the Pi's username and password.
- Windows 10 and 11 usually include `ssh`; no extra software is needed.

## Enable SSH for the First Time

**You do not need a monitor or keyboard.** When writing the SD card with Raspberry Pi Imager, enter the Wi-Fi credentials and a username and password, then enable `SSH`. See [HEADLESS_FIRST_BOOT.md](HEADLESS_FIRST_BOOT.md) for the full setup.

`enable_ssh_remote.sh` is a fallback for a Pi that already has a local terminal. It is not needed for a headless first boot.

## Connect from Windows

Open PowerShell and run:

```powershell
ssh <pi-username>@<pi-address>
```

The first time, confirm that you trust the host by typing `yes`, then enter the Pi password. The password will not appear as you type; this is normal.

After connecting, the terminal is running on the Pi. For example:

```bash
cd ~/palm_demo
./run_palm_demo.sh --help
rpicam-hello --list
```

## Copy Files from the Computer to the Pi

Run this in Windows PowerShell, replacing the username and IP address with your own:

```powershell
scp .\dist\palm_demo_pi.zip <pi-username>@<pi-address>:/home/<pi-username>/
```

For the first deployment, using a USB drive may be simpler. SSH is useful later for updating code, checking logs, and running commands.

## Run the Palm Demo Remotely

```bash
cd ~/palm_demo
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb enroll --user demo-rgb --samples 5 --interactive
```

Image capture still happens on the Pi. The SSH window shows text and cannot replace a camera preview. For initial camera setup, connect a display and run `rpicam-hello -t 0`.

## Security Notes

- Do not put the Pi password in scripts, Git, USB instructions, or chat.
- Do not expose the SSH port through a public router.
- Use SSH only on your own local network. You can disable it after the experiment:

```bash
sudo systemctl disable --now ssh
```

## Troubleshooting

- If the hostname does not resolve, check that both devices are on the same network and try the Pi's IP address.
- If the IP address changes, run `hostname -I` on the Pi to find its current address.
- A USB package cannot connect to your Pi by itself. You must first power on the Pi, connect it to the network, and provide usable local network connection details and authorization in the current environment.
