import unittest
import numpy as np
from PIL import Image
from geometry_metrics import make_hand_mask, geometry_metrics


class DiagnosticsTests(unittest.TestCase):
    def test_synthetic_foreground_and_area(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[20:80, 20:80] = 200
        mask = make_hand_mask(Image.fromarray(img))
        self.assertEqual(mask[50,50], 255)
        self.assertEqual(mask[0,0], 0)
        quad = np.array([[20,20],[80,20],[80,80],[20,80]])
        result = geometry_metrics(mask, quad, (100,100))
        self.assertAlmostEqual(result['roi_quad_area_pct_of_image'], 36.0)
