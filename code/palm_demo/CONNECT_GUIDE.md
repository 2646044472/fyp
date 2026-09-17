# Connect to the FYP Raspberry Pi from Windows

The usual connection is a USB-C data cable from the Windows computer to the Pi 5. It creates a USB network; SSH runs over that network. The current Pi's USB address is **`10.12.194.1`**.

## Quick connection

Open PowerShell on Windows:

```powershell
ssh fyp@10.12.194.1
```

On the first connection, check that this is your Pi and type `yes` to accept its SSH host key. When asked for the password, enter **`fypfypum`**. The password will not appear as you type. This password is for the shared FYP Pi; do not reuse it elsewhere.

## Find the Pi's USB IP address

For this USB setup, Windows normally shows the Pi as the USB adapter's **default gateway**. In PowerShell, run:

```powershell
$piAdapter = Get-NetAdapter | Where-Object InterfaceDescription -match 'Raspberry Pi USB Remote NDIS'
(Get-NetIPConfiguration -InterfaceIndex $piAdapter.ifIndex).IPv4DefaultGateway.NextHop
```

The output on our setup was `10.12.194.1`. Then connect with `ssh fyp@10.12.194.1`, substituting the address shown. If the command gives no address, use the checks below.

### Check the adapter and scan if needed

Confirm Windows detected the USB network device:

```powershell
$piAdapter | Select-Object Name, InterfaceDescription, Status, ifIndex
```

`Status` should be `Up`. The adapter name and interface index can change. Find the **computer's** address on this USB network:

```powershell
Get-NetIPAddress -InterfaceIndex $piAdapter.ifIndex -AddressFamily IPv4 |
  Select-Object IPAddress, PrefixLength
```

On the checked computer it was `10.12.194.4/28`. **That is the Windows address, not the Pi address.** Inspect devices seen on the same adapter:

```powershell
Get-NetNeighbor -InterfaceIndex $piAdapter.ifIndex -AddressFamily IPv4 |
  Where-Object { $_.State -notmatch 'Permanent|Unreachable|Incomplete' } |
  Select-Object IPAddress, LinkLayerAddress, State
```

The Pi appeared as `10.12.194.1`. Verify a candidate before connecting:

```powershell
Test-Connection 10.12.194.1 -Count 2
Test-NetConnection 10.12.194.1 -Port 22
```

`TcpTestSucceeded : True` means SSH is listening. If the neighbor table is empty, check the computer's USB subnet above, then scan that subnet. For the **current `10.12.194.0/28` subnet only**:

```powershell
1..14 | ForEach-Object {
  $address = "10.12.194.$_"
  if (Test-Connection $address -Count 1 -Quiet -TimeoutSeconds 1) {
    if (Test-NetConnection $address -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue) {
      "SSH responds at $address"
    }
  }
}
```

Use the discovered Pi address in `ssh fyp@<Pi-IP>`. On the checked Windows computer, the `.local` hostname did not resolve, so the numeric IP was used.

## Prepare a Pi for USB-C direct connection

These steps are for a fresh **Pi 5 + Windows + USB-C data cable** setup. An already configured Pi does not need to be reflashed.

1. If Windows does not recognize the Pi USB network adapter, install the project's `windows\rpi-usb-gadget-driver-setup.exe`. On the checked computer, Windows already showed `Raspberry Pi USB Remote NDIS Network Device`.
2. In Raspberry Pi Imager, choose **Raspberry Pi OS Lite (64-bit, Trixie)**. Set a hostname (the earlier setup used `palm-pi`), username and password; enable SSH with password authentication; and enable **USB Gadget Mode / USB networking**. If that option is missing, update Imager and the OS image before writing the card. A freshly imaged Pi uses the credentials set in Imager.
3. With the Pi powered off, insert the card. Connect its USB-C port directly to the computer with a data-capable cable. For the first connection test, leave the camera disconnected. Allow about two minutes for first boot and USB enumeration.
4. Find the Pi address using the commands above and connect with SSH.

The USB-C cable may also power the Pi. If it repeatedly disconnects or reboots, the computer's port may not provide enough power; use a supported power and network arrangement for your hardware. Power off before connecting or disconnecting the CSI camera ribbon.

## Connect over Wi-Fi or Ethernet instead

The Pi and computer must be on the same reachable network, and SSH must be enabled. Use the Pi's LAN address, which is separate from its USB address:

```powershell
ssh fyp@<Pi-LAN-IP>
```

If you have a terminal on the Pi, `hostname -I` lists its addresses. A new Pi's username and password are whatever you set in Imager. On first connection, accept the host key after checking that the address belongs to your Pi.

## After login

These commands run **on the Pi** in the SSH session:

```bash
cd ~/palm_demo
./run_palm_demo.sh --help
rpicam-hello --list
```

After building `code\palm_demo\dist\palm_demo_pi.zip`, run `scp` in **Windows PowerShell** from the repository root (the ZIP is not currently included in the repository):

```powershell
scp .\code\palm_demo\dist\palm_demo_pi.zip fyp@10.12.194.1:/home/fyp/
```

An example enrollment command on the Pi is:

```bash
cd ~/palm_demo
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb enroll --user demo-rgb --samples 5 --interactive
```

The camera captures on the Pi. SSH shows terminal text, not camera preview. For first camera setup with a display attached, `rpicam-hello -t 0` gives a preview.

## If it still does not connect

- **No Raspberry Pi USB adapter:** Check Pi power, the USB-C data cable and port, USB gadget setup on the SD card, and the Windows gadget driver.
- **Adapter is up, but no Pi address appears:** Wait for boot, inspect the USB subnet and scan it as above. Check whether the Pi is repeatedly disconnecting because of power.
- **Ping works, port 22 fails:** SSH may not be enabled or running on the Pi.
- **Port 22 works, login fails:** Use `fyp` and the password above for this shared Pi, or the credentials configured when a different card was imaged.
- **Host key changed warning:** Verify that the address still belongs to the intended Pi before accepting a new key. Reimaging the card changes the Pi's host key.

For more detail, see the [Raspberry Pi OS USB gadget mode overview](https://www.raspberrypi.com/news/usb-gadget-mode-in-raspberry-pi-os/).
