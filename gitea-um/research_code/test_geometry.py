"""Synthetic contract checks; no biometric inputs or model inference."""
import unittest
import numpy as np
from PIL import Image
from geometry import inverse_square, crop_original

class GeometryTests(unittest.TestCase):
    def test_inverse_pil_cardinal_rotation_and_padding(self):
        for w,h in [(7,11),(13,7),(9,9)]:
            side=max(w,h);left=(side-w)//2;top=(side-h)//2
            src=np.zeros((h,w,3),np.uint8)
            src[2,3]=(23,87,221)
            canvas=Image.new('RGB',(side,side));canvas.paste(Image.fromarray(src),(left,top))
            for angle in [0,90,180,270]:
                arr=np.asarray(canvas.rotate(angle,expand=False))
                y,x=np.argwhere(np.all(arr==[23,87,221],axis=-1))[0]
                recovered=inverse_square([[x,y]],side,left,top,angle)
                np.testing.assert_array_equal(recovered,[[3,2]])

    def test_crop_uses_supplied_original_pixels(self):
        a=np.tile(np.arange(80,dtype=np.uint8),(80,1))*3
        original=Image.fromarray(a)
        quad=[[10,10],[60,10],[60,60],[10,60]]
        result=crop_original(original,quad)
        self.assertEqual(result.size,(128,128))
        self.assertGreater(np.asarray(result).std(),10)
        with self.assertRaises(ValueError):
            crop_original(Image.new('RGB',(80,80),'white'),quad)

if __name__=='__main__':unittest.main()
