import numpy as np
import pytest
from pklnet_roi import illumination_pixels, LOCALIZER_GAMMA, normalize_roi_pixels, normalize_roi


def test_gamma_lut_preserves_every_byte_value_and_noncontiguous_rgb():
    rgb = np.tile(np.arange(256, dtype=np.uint8)[None, :, None], (5, 1, 3))
    for image in (rgb, rgb[:, ::-1, :]):
        expected = np.rint((image.astype(np.float32) / 255) ** LOCALIZER_GAMMA * 255).astype(np.uint8)
        np.testing.assert_array_equal(illumination_pixels(image), expected)


def test_gamma_lut_rejects_nonbyte_inputs():
    with pytest.raises(ValueError, match='uint8'):
        illumination_pixels(np.zeros((3, 3, 3), dtype=np.float32))


@pytest.mark.parametrize('size', [128, 384, 768])
def test_pixels_only_normalization_matches_original_formula(size):
    pixels = np.random.default_rng(size).integers(0, 256, (size, size), dtype=np.uint8)
    array = pixels.astype(np.float32)
    low, high = np.percentile(array, (1, 99))
    expected = np.clip((array-low)*255/(high-low), 0, 255).astype(np.uint8)
    np.testing.assert_array_equal(normalize_roi_pixels(pixels), expected)
    normalized, quality = normalize_roi(pixels)
    np.testing.assert_array_equal(normalized, expected)
    assert quality == {'contrast': float(array.std()), 'sharpness': float(np.hypot(*np.gradient(array)).var())}


def test_pixels_only_normalization_still_rejects_flat_roi():
    with pytest.raises(ValueError, match='no usable intensity range'):
        normalize_roi_pixels(np.full((128, 128), 100, dtype=np.uint8))
