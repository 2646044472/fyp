import cv2
import numpy as np
import pytest
from binary_demo_matcher import akaze_features, binary_bytes, BinaryDemoMatcher
from demo_matcher import FastCCDemoMatcher
from union_matcher import FEATURE_SIZE


def test_binary_envelope_preserves_all_byte_values():
    raw = (np.arange(8*61).reshape(8, 61) % 256).astype(np.uint8)
    packed = np.zeros((8, 128), np.float32)
    packed[:, :61] = raw
    assert np.array_equal(binary_bytes(packed), raw)


@pytest.mark.parametrize('column,value', [(0, .1), (0, 256), (61, 1), (0, np.nan)])
def test_binary_envelope_rejects_invalid_data(column, value):
    packed = np.zeros((4, 128), np.float32)
    packed[0, column] = value
    with pytest.raises(ValueError):
        binary_bytes(packed)


def test_old_template_is_not_accepted():
    matcher = object.__new__(BinaryDemoMatcher)
    template = np.zeros(FEATURE_SIZE, np.uint8)
    template[:4] = np.asarray([FastCCDemoMatcher.magic], '<i4').view(np.uint8)
    with pytest.raises(ValueError):
        matcher._unpack(template)


@pytest.mark.skipif(not hasattr(cv2, 'AKAZE_create'), reason='AKAZE unavailable in this OpenCV build')
def test_default_descriptor_values_survive_adapter():
    pixels = np.random.default_rng(29).integers(0, 256, (384, 384), dtype=np.uint8)
    keys, expected = cv2.AKAZE_create().detectAndCompute(pixels, None)
    indices = sorted(range(len(keys)), key=lambda i: -keys[i].response)[:1000] if len(keys)>1000 else list(range(len(keys)))
    points, packed = akaze_features(pixels)
    assert np.array_equal(binary_bytes(packed), expected[indices])
    assert np.array_equal(points, np.asarray([keys[i].pt for i in indices], np.float32))
