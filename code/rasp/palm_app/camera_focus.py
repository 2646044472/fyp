"""Discover UVC autofocus controls without assuming a fixed /dev/video index."""
import os
from pathlib import Path
import re
import subprocess


def command(device, *args):
    try:
        result = subprocess.run(["v4l2-ctl", "-d", str(device), *args],
                                capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Camera focus control timed out") from error
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Camera control unavailable")
    return result.stdout


def find_device():
    explicit = os.environ.get("PALM_FOCUS_DEVICE")
    paths = [Path(explicit)] if explicit else sorted(Path("/dev/v4l/by-id").glob("*-video-index0"))
    candidates = []
    for path in paths:
        if not path.is_char_device():
            continue
        controls = command(path, "--list-ctrls")
        if "focus_automatic_continuous" in controls:
            candidates.append(path)
    if len(candidates) != 1:
        raise RuntimeError("No unique UVC autofocus camera found")
    return candidates[0]


def status():
    try:
        device = find_device()
        text = command(device, "--get-ctrl=focus_automatic_continuous,focus_absolute")
        values = dict(re.findall(r"(focus_\w+):\s*(-?\d+)", text))
        return dict(supported=True, continuous=values.get("focus_automatic_continuous") == "1",
                    position=int(values["focus_absolute"]) if "focus_absolute" in values else None,
                    device=str(device), note="Autofocus enabled does not prove focus has converged")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        return dict(supported=False, continuous=False, message=str(error))


def enable():
    device = find_device()
    command(device, "--set-ctrl=focus_automatic_continuous=1")
    return status()
