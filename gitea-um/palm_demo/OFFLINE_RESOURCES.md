# Offline USB Resources

Copy this directory to a USB drive, then copy it to the Raspberry Pi.

## Included Resources

- Fast-CC source, pinned in `vendor/palmprint-recognition-python`.
- ARM64 wheels for Python 3.11 (NumPy 2.2.6, SciPy 1.16.3, Pillow 12.2.0) and Python 3.13 (NumPy 2.3.5, SciPy 1.17.1, Pillow 12.2.0).
- A Picamera2 0.3.37 wheel for fallback use; it does not replace the system camera libraries.
- `install_usb_offline.sh`, which installs Python dependencies and creates a local virtual environment.

## Use on the Pi

Raspberry Pi OS 64-bit Bookworm is recommended. Copy the complete `palm_demo` directory to the Pi, then run:

```bash
cd ~/palm_demo
chmod +x install_usb_offline.sh
./install_usb_offline.sh
rpicam-hello --list
```

If the system reports that Picamera2 is missing, connect to the internet once and install the system package:

```bash
sudo apt update
sudo apt install -y python3-picamera2
```

NumPy, SciPy, Pillow, and Fast-CC can then be used offline from the USB package. Raspberry Pi recommends installing Picamera2 and `libcamera` with the matching Raspberry Pi OS `apt` packages. Do not replace the system Picamera2 installation with pip without a specific need.

## Run

```bash
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb enroll --user demo-rgb --samples 5 --interactive
./run_palm_demo.sh --authorized-local-biometric --camera 0 --capture-profile rgb verify --user demo-rgb
```

For NoIR capture with IR illumination, use a separate profile and user:

```bash
./run_palm_demo.sh --authorized-local-biometric --camera 1 --capture-profile noir-ir enroll --user demo-noir --samples 5 --interactive
```

## Limitations

- The wheels require `aarch64` and Python 3.11 or 3.13. Do not force-install them on a 32-bit system or another Python version.
- The Picamera2 wheel is not a complete `libcamera` driver. If the camera is not detected, the matching system `apt` packages are still required.
- This package does not contain research data, personal templates, or runtime logs. Those are created on the Pi when the software runs.
- Before sharing the package, check that its data, videos, and models are permitted for redistribution.

## References

- [Raspberry Pi Camera Software](https://www.raspberrypi.com/documentation/computers/camera_software.html)
- [Picamera2 on PyPI](https://pypi.org/project/picamera2/)
