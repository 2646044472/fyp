import importlib
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def recovery(monkeypatch):
    root=Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root));monkeypatch.syspath_prepend(str(root/'tools'))
    return importlib.import_module('halfturn_roi_recovery')


def result(quad,valid=True,reason=None):
    return np.zeros((16,16),np.uint8),np.asarray(quad,np.float32),dict(
        roi_geometry_valid=valid,roi_geometry_reason=reason,roi_quad_full=quad)


def test_valid_primary_is_same_objects_without_another_inference(recovery):
    primary=result([[1,1],[10,1],[10,10],[1,10]])
    class Engine:
        calls=0
        def extract(self,*a,**kw):self.calls+=1;return primary
    engine=Engine();pilot=recovery.HalfTurnROIRecovery(engine)
    assert pilot.extract(Image.new('RGB',(30,20))) is primary
    assert engine.calls==1 and not pilot.last_trace['retry']
    assert primary[2]==dict(roi_geometry_valid=True,roi_geometry_reason=None,roi_quad_full=[[1,1],[10,1],[10,10],[1,10]])


def test_other_failure_does_not_enter_new_search(recovery):
    primary=result([[1,1],[2,1],[2,2],[1,2]],False,'pklnet_keypoint_span_too_small')
    pilot=recovery.HalfTurnROIRecovery(None)
    assert pilot.recover(Image.new('RGB',(30,20)),primary) is primary
    assert not pilot.last_trace['retry']


def test_recovery_maps_all_points_and_samples_original_pixels(recovery):
    size=(100,80)
    primary=result([[-2,20],[38,20],[38,60],[-2,60]],False,'roi_out_of_bounds')
    mapped=np.asarray([[1,20],[41,20],[41,60],[1,60]],np.float32)
    rotated=recovery.map_points(mapped,size);candidate=result(rotated.tolist())
    candidate[2].update(pklnet_keypoints=[10,11,20,21,30,31],
        pklnet_retry_box=[2,3,90,70],pklnet_roi_candidates=[dict(quad=rotated.tolist(),valid=True)])
    pixels=np.arange(80*100*3,dtype=np.uint8).reshape(80,100,3);image=Image.fromarray(pixels)
    observed={}
    def sample(bgr,quad,side,ratio):
        observed.update(bgr=bgr.copy(),quad=quad.copy(),side=side)
        return np.full((side,side),77,np.uint8)
    engine=SimpleNamespace(extract=lambda *a,**kw:candidate,_roi_extractor=SimpleNamespace(getROIimg=sample))
    pilot=recovery.HalfTurnROIRecovery(engine);raw,quad,details=pilot.recover(image,primary,side=16)
    np.testing.assert_array_equal(quad,mapped)
    np.testing.assert_array_equal(observed['bgr'],cv2.cvtColor(pixels,cv2.COLOR_RGB2BGR))
    np.testing.assert_array_equal(details['pklnet_roi_candidates'][0]['quad'],mapped)
    assert details['pklnet_keypoints']==[89.,68.,79.,58.,69.,48.]
    assert details['pklnet_retry_box']==[10,10,98,77]
    assert pilot.last_trace['recovered'] and np.all(raw==77)
    assert candidate[2]['pklnet_keypoints']==[10,11,20,21,30,31]
    assert primary[2]['roi_geometry_reason']=='roi_out_of_bounds'


def test_spatially_different_valid_retry_is_not_accepted(recovery):
    primary=result([[-2,1],[8,1],[8,11],[-2,11]],False,'roi_out_of_bounds')
    candidate=result(recovery.map_points([[60,40],[70,40],[70,50],[60,50]],(100,80)).tolist())
    engine=SimpleNamespace(extract=lambda *a,**kw:candidate)
    pilot=recovery.HalfTurnROIRecovery(engine)
    assert pilot.recover(Image.new('RGB',(100,80)),primary) is primary
    assert pilot.last_trace['reason']=='orientation_localization_disagreement'
