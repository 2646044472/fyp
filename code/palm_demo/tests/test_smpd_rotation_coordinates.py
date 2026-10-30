import importlib
from pathlib import Path

import numpy as np
import pytest


@pytest.mark.parametrize('turns',range(4))
def test_quarter_turn_coordinates_match_real_pixel_rotation(monkeypatch,turns):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('audit_smpd_localizer_rotation')
    width,height=19,13
    points=np.asarray([[2,3],[14,3],[14,9],[2,9]],np.float32)
    image=np.zeros((height,width),np.uint8)
    for index,(x,y) in enumerate(points.astype(int),1):image[y,x]=index
    rotated=np.rot90(image,turns)
    expected=[]
    for index in range(1,5):
        y,x=np.argwhere(rotated==index)[0];expected.append((x,y))
    mapped=np.c_[points,np.ones(4)]@module.rotation_matrix(width,height,turns).T
    np.testing.assert_array_equal(mapped[:,:2],expected)
    np.testing.assert_array_equal(module.restore_quad(expected,width,height,turns),points)
