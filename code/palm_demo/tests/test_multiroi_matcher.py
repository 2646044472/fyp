from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from multiroi_matcher import DUAL_SIZE, HEADER_END, MAGIC
from palm_app.biometric import load_algorithm
from templates import TemplateStore


@pytest.fixture
def matcher():
    return load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python','FastCCMultiROI-v3')


def test_template_roundtrip_and_incompatible_version(matcher,tmp_path):
    roi=np.random.default_rng(50).integers(0,256,(128,128),dtype=np.uint8)
    f=matcher.extract(roi);store=TemplateStore(tmp_path);store.save('test',np.stack([f,f]),{'algorithm':matcher.name})
    saved,_=store.load('test');np.testing.assert_array_equal(saved[0],f);assert matcher.match(f,saved[0])==0
    with pytest.raises(ValueError,match='shape'):matcher.match(f[:DUAL_SIZE],f)


def test_hypotheses_remain_separate_and_native_pixels_are_not_rectified(matcher):
    rng=np.random.default_rng(51);image=Image.fromarray(rng.integers(0,256,(300,400,3),dtype=np.uint8));roi=rng.integers(0,256,(128,128),dtype=np.uint8)
    a=np.array([[100,100],[220,100],[220,220],[100,220]],np.float32);b=a+20
    f=matcher.extract_with_hypotheses(image,a,roi,[{'quad':a,'valid':True},{'quad':b,'valid':True}])
    _,_,native,origin,views=matcher._unpack(f)
    import cv2
    expected=cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2GRAY)
    x,y=origin;np.testing.assert_array_equal(native,expected[y:y+native.shape[0],x:x+native.shape[1]])
    assert len(views)==8
    assert not np.array_equal(views[0][1],views[4][1])


def test_invalid_auxiliary_hypothesis_is_not_promoted(matcher):
    rng=np.random.default_rng(52);image=Image.fromarray(rng.integers(0,256,(200,200,3),dtype=np.uint8));roi=rng.integers(0,256,(128,128),dtype=np.uint8)
    q=np.array([[40,40],[160,40],[160,160],[40,160]],np.float32)
    f=matcher.extract_with_hypotheses(image,q,roi,[{'quad':q,'valid':True},{'quad':q-500,'valid':False}])
    assert len(matcher._unpack(f)[-1])==4
    f[DUAL_SIZE:HEADER_END]=np.asarray([MAGIC,2000,100,0,0,4],'<i4').view(np.uint8)
    with pytest.raises(ValueError,match='header'):matcher._unpack(f)
    f[DUAL_SIZE:HEADER_END]=np.asarray([MAGIC,200,200,1,0,4],'<i4').view(np.uint8)
    with pytest.raises(ValueError,match='outside original'):matcher._unpack(f)
