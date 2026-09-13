from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

from roi import AutomaticPalmROI, FixedGuideROI


def image_with_hand(size=(200, 160), box=(70, 40, 130, 120), value=180, background=30, textured=True):
    image = np.full((size[1], size[0]), background, dtype=np.uint8)
    left, top, right, bottom = box
    hand = np.linspace(value - 20, value + 20, max(1, right - left), dtype=np.float32)
    patch = np.broadcast_to(hand[np.newaxis, :], (max(1, bottom - top), max(1, right - left))).copy()
    if textured:
        patch += (np.indices(patch.shape).sum(axis=0) % 2) * 40
    image[top:bottom, left:right] = np.clip(patch, 0, 255).astype(np.uint8)
    return Image.fromarray(image, mode="L")


def test_fixed_guide_roi_returns_normalized_square():
    result = FixedGuideROI().extract(image_with_hand())

    assert result.status == "OK"
    assert result.roi.shape == (128, 128)


def test_automatic_roi_accepts_centred_foreground(tmp_path):
    background = Image.new("L", (200, 160), 30)
    result = AutomaticPalmROI(background=background, min_area_ratio=0.03).extract(image_with_hand())

    assert result.status == "OK"
    assert result.roi.shape == (128, 128)


def test_automatic_roi_retries_empty_frame():
    background = Image.new("L", (200, 160), 30)
    result = AutomaticPalmROI(background=background).extract(background)

    assert result.status == "RETRY"
    assert result.reason == "NO_FOREGROUND"


def test_automatic_roi_retries_small_object():
    background = Image.new("L", (200, 160), 30)
    result = AutomaticPalmROI(background=background, min_area_ratio=0.03).extract(
        image_with_hand(box=(98, 78, 102, 82))
    )

    assert result.status == "RETRY"
    assert result.reason == "HAND_TOO_SMALL"


def test_automatic_roi_retries_clipped_object():
    background = Image.new("L", (200, 160), 30)
    result = AutomaticPalmROI(background=background).extract(image_with_hand(box=(0, 40, 80, 120)))

    assert result.status == "RETRY"
    assert result.reason == "HAND_CLIPPED"


def test_automatic_roi_retries_low_contrast_and_blur():
    background = Image.new("L", (200, 160), 100)
    low_contrast = image_with_hand(value=105, background=100, textured=False)
    result = AutomaticPalmROI(background=background, min_area_ratio=0.03, difference_threshold=1, min_contrast=12).extract(low_contrast)
    assert result.status == "RETRY"
    assert result.reason in {"LOW_CONTRAST", "NO_FOREGROUND"}

    blurred = image_with_hand().filter(ImageFilter.GaussianBlur(8))
    result = AutomaticPalmROI(background=Image.new("L", (200, 160), 30), min_area_ratio=0.03, min_sharpness=8).extract(blurred)
    assert result.status == "RETRY"
    assert result.reason == "LOW_SHARPNESS"
