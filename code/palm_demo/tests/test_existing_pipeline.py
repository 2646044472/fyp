from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

import palm_demo
from templates import safe_user_id


def make_test_image() -> Image.Image:
    values = np.arange(320 * 240, dtype=np.uint32).reshape(240, 320) % 256
    return Image.fromarray(values.astype(np.uint8), mode="L")


def test_parse_crop_accepts_valid_fractional_box():
    assert palm_demo.parse_crop("0.1,0.2,0.8,0.9") == (0.1, 0.2, 0.8, 0.9)


def test_crop_and_normalize_returns_128_square():
    roi, quality = palm_demo.crop_and_normalize(make_test_image(), palm_demo.DEFAULT_CROP)

    assert roi.shape == (128, 128)
    assert roi.dtype.name == "uint8"
    assert "contrast" in quality
    assert "sharpness" in quality


def test_template_filename_sanitization():
    assert safe_user_id("stephen/../../bankey") == "stephenbankey"


def test_zero_range_image_is_rejected():
    with pytest.raises(RuntimeError, match="no usable intensity range"):
        palm_demo.crop_and_normalize(Image.new("L", (320, 240), 100), palm_demo.DEFAULT_CROP)
