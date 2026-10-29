from pathlib import Path
from types import SimpleNamespace
import cv2
import numpy as np
import pytest
from PIL import Image
from palm_app.biometric import load_algorithm
from templates import TemplateStore
from union_matcher import HEADER, MAGIC
from window_roi import window_candidates


@pytest.fixture
def matcher():
    return load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python','FastCCWindowUnion-v4')


def test_numeric_template_roundtrip_and_version_isolation(matcher,tmp_path):
    roi=np.random.default_rng(90).integers(0,256,(128,128),dtype=np.uint8)
    f=matcher.extract(roi);store=TemplateStore(tmp_path)
    store.save('test',np.stack([f,f]),{'algorithm':matcher.name})
    saved,_=store.load('test');np.testing.assert_array_equal(saved[0],f)
    assert matcher.match(f,saved[0])==0
    with pytest.raises(ValueError,match='shape'):matcher.match(f[:200],f)
    f[:4]=np.asarray([MAGIC-1],'<i4').view(np.uint8)
    with pytest.raises(ValueError,match='header'):matcher._unpack(f)


def test_native_pixels_and_branch_set_survive_storage(matcher):
    rgb=np.random.default_rng(91).integers(0,256,(300,400,3),dtype=np.uint8)
    full=Image.fromarray(rgb);q=np.array([[70,50],[240,50],[240,220],[70,220]],np.float32)
    roi=cv2.resize(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),(128,128))
    f=matcher.extract_with_hypotheses(full,q,roi,[dict(quad=q,valid=True),dict(quad=q+10,valid=True,kind='window')])
    _,_,_,native,gallery,queries=matcher._unpack(f)
    np.testing.assert_array_equal(native,cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY))
    assert [v[0] for v in gallery]==[4,8]
    assert len(queries)==2+8+4
    assert [v[0] for v in queries[-4:]]==[0,2,0,2]
    # Payload truncation cannot silently discard the last view.
    header=f[:HEADER].view('<i4');header[1]-=1
    with pytest.raises(ValueError,match='view|layout'):matcher._unpack(f)


def test_window_geometry_and_gamma_do_not_depend_on_identity():
    calls=[]
    def extract(view):
        calls.append(np.asarray(view))
        return None,np.array([[20,20],[100,20],[100,100],[20,100]]),{'pklnet_keypoints':[[20,20],[100,20],[50,50]]}
    engine=SimpleNamespace(extract=extract)
    assert window_candidates(Image.new('RGB',(400,300)),engine)==[]
    rows=window_candidates(Image.new('RGB',(600,300),(64,64,64)),engine)
    assert len(rows)==6 and all(r['valid'] for r in rows)
    assert [r['box'][0] for r in rows]==[0,0,100,100,200,200]
    assert rows[-1]['quad'][0]==[220,20]
    assert calls[1][0,0,0]>calls[0][0,0,0]


def test_bad_valid_candidate_cannot_be_silently_used(matcher):
    rgb=np.random.default_rng(92).integers(0,256,(200,200,3),dtype=np.uint8)
    q=np.array([[20,20],[170,20],[170,170],[20,170]],np.float32)
    with pytest.raises(ValueError,match='geometry'):
        matcher.extract_with_hypotheses(Image.fromarray(rgb),q,rgb[:128,:128,0],[dict(quad=q-500,valid=True)])


def test_parallel_window_map_preserves_order_and_surfaces_failure():
    from concurrent.futures import ThreadPoolExecutor
    image = Image.new('RGB', (600, 300), (64, 64, 64))
    def extract(view):
        return None, np.array([[20,20],[100,20],[100,100],[20,100]]), {'pklnet_keypoints': [[20,20],[100,20],[50,50]]}
    engine = SimpleNamespace(extract=extract)
    expected = window_candidates(image, engine)
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert window_candidates(image, engine, map_jobs=pool.map) == expected
        def fail(view):
            raise RuntimeError('model failed')
        with pytest.raises(RuntimeError, match='model failed'):
            window_candidates(image, SimpleNamespace(extract=fail), map_jobs=pool.map)
