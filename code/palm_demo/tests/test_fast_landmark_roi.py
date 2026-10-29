import numpy as np
import pytest
from fast_landmark_roi import unrotate


@pytest.mark.parametrize('angle', [0, 90, 180, 270])
def test_unrotate_preserves_original_pixel_coordinates(angle):
    width, height = 13, 7
    points = np.asarray([[0, 0], [12, 6], [4, 2], [8.25, 3.5]], np.float32)
    x, y = points.T
    rotated = {0: points, 90: np.stack((y, width-1-x), axis=1),
               180: np.stack((width-1-x, height-1-y), axis=1),
               270: np.stack((height-1-y, x), axis=1)}[angle]
    np.testing.assert_array_equal(unrotate(rotated, angle, (width, height)), points)
