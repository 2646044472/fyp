from pathlib import Path
import numpy as np
from biometric import load_algorithm
from fastcc_accelerated import AcceleratedFastCC


def test_codes_and_scores_match_reference_including_numerical_ties():
    base = load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python', 'FastCC')
    fast = AcceleratedFastCC(base)
    rng = np.random.default_rng(20261028)
    images = [rng.integers(0, 256, (128, 128), dtype=np.uint8) for _ in range(20)]
    images += [np.full((128, 128), value, np.uint8) for value in (0, 1, 128, 255)]
    images += [np.tile(np.arange(128, dtype=np.uint8), (128, 1))]
    for image in images:
        np.testing.assert_array_equal(fast.extract(image), base.extract(image))
    codes = [rng.integers(0, 2, (32, 32)).astype(bool) for _ in range(20)]
    codes += [np.zeros((32, 32), bool), np.ones((32, 32), bool)]
    for left, right in zip(codes, codes[::-1]):
        assert fast.match(left, right) == base.match(left, right)
    for dy, dx in [(-4, 3), (2, -4), (4, 4)]:
        left = codes[0]
        right = np.roll(left, (dy, dx), axis=(0, 1))
        assert fast.match(left, right) == base.match(left, right)
