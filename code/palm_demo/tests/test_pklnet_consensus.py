import importlib.util
import threading
from types import SimpleNamespace

import numpy as np
from PIL import Image
import pytest

from pklnet_roi import PKLNET_ROOT, PKLNetROI, ROI_GEOMETRY_VERSION
from pklnet_policy import branch_consensus, require_matchable_quality
from palm_app.debug_ui import App
from demo_flow import DemoFlow


@pytest.fixture
def geometry():
    spec = importlib.util.spec_from_file_location('test_geometry', PKLNET_ROOT/'roiExtractor.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def points():
    return np.array([150,150,250,150,200,225],dtype=np.float32)


def test_agreement_preserves_valid_crop(geometry):
    d=branch_consensus(points(),points()+1,(600,600),geometry)
    assert d['pklnet_consensus_valid']
    assert d['pklnet_branch_quad_iou']>.9


def test_opposed_order_cannot_average_to_a_crop(geometry):
    kp=points()
    reversed_order=kp[[2,3,0,1,4,5]]
    d=branch_consensus(kp,reversed_order,(600,600),geometry)
    assert d['pklnet_consensus_reason']=='pklnet_branch_direction_conflict'


def test_same_direction_different_anatomical_region_is_rejected(geometry):
    other=points()+np.tile([80,0],3)
    d=branch_consensus(points(),other,(600,600),geometry)
    assert d['pklnet_consensus_reason']=='pklnet_branch_location_conflict'


def test_same_center_different_scale_is_rejected(geometry):
    kp=points()
    other=(kp.reshape(3,2)-[200,150])*1.8+[200,150]
    d=branch_consensus(kp,other,(600,600),geometry)
    assert d['pklnet_consensus_reason']=='pklnet_branch_scale_conflict'


@pytest.mark.parametrize('bad',[[1,2,3], [1,2,3,4,5,float('nan')], [100,100,101,100,100,110]])
def test_malformed_or_collapsed_branch_rejected(geometry,bad):
    assert not branch_consensus(points(),bad,(600,600),geometry)['pklnet_consensus_valid']


def test_live_extractor_uses_branch_guard_even_when_fused_geometry_is_valid(geometry):
    extractor=PKLNetROI(policy="consensus")
    hm=np.array([80,80,150,80,115,135],np.float32)
    fc=hm+np.tile([60,0],3)
    fused=(hm+fc)/2
    extractor._session=SimpleNamespace(run=lambda names,feed:[p[None] for p in (fused,hm,fc)])
    extractor._roi_extractor=geometry
    _,_,details=extractor.extract(Image.new('RGB',(300,400),(40,60,80)))
    assert details['roi_in_bounds']
    assert details['pklnet_keypoint_span_ratio']>.1
    assert details['roi_geometry_reason']=='pklnet_branch_location_conflict'
    assert not details['roi_geometry_valid']
    assert details['roi_geometry']=='pklnet-consensus-v2'


def test_default_uses_spatial_branch_when_opposing_fusion_collapses(geometry):
    extractor=PKLNetROI()
    hm=np.array([80,80,150,80,115,135],np.float32)
    fc=hm[[2,3,0,1,4,5]]
    fused=(hm+fc)/2
    extractor._session=SimpleNamespace(run=lambda names,feed:[p[None] for p in (fused,hm,fc)])
    extractor._roi_extractor=geometry
    image=Image.fromarray(np.tile(np.arange(300,dtype=np.uint8),(400,1))).convert('RGB')
    raw,quad,details=extractor.extract(image)
    expected_quad=geometry.getROIckp(hm[:2],hm[2:4],geometry.isAntiClock(hm))
    np.testing.assert_allclose(quad,expected_quad)
    assert raw.std()>0
    assert details['roi_geometry_valid']
    assert not details['pklnet_consensus_valid']  # advisory, not a veto
    assert details['roi_geometry']==ROI_GEOMETRY_VERSION
    np.testing.assert_array_equal(details['pklnet_keypoints'],hm)


def test_default_does_not_hide_a_collapsed_heatmap_with_fc_fallback(geometry):
    extractor=PKLNetROI()
    hm=np.array([100,80,101,80,100,135],np.float32)
    fc=np.array([80,80,150,80,115,135],np.float32)
    extractor._session=SimpleNamespace(run=lambda names,feed:[p[None] for p in ((hm+fc)/2,hm,fc)])
    extractor._roi_extractor=geometry
    _,_,details=extractor.extract(Image.new('RGB',(300,400)))
    assert details['roi_geometry_reason']=='pklnet_keypoint_span_too_small'
    assert not details['roi_geometry_valid']


@pytest.mark.parametrize('quality',[{'contrast':5.,'sharpness':10.}, {'contrast':20.,'sharpness':.1}])
def test_still_image_quality_is_advisory_and_releases_camera(quality):
    app=App.__new__(App)
    app.collection_lock=threading.Lock()
    image=Image.new('RGB',(300,400))
    app.camera=SimpleNamespace(capture_highres=lambda:(image,image,{}))
    app.detect_full_still=lambda *a,**kw:(np.ones((128,128),np.uint8),None,None,quality,'pklnet')
    app.demo_algorithm=SimpleNamespace(extract=lambda roi:np.array([roi.mean()]))
    feature,_,source=app.capture_demo_feature()
    np.testing.assert_array_equal(feature,[1.])
    assert source=='pklnet'
    assert not app.collection_lock.locked()


def make_flow(tmp_path,capture):
    algorithm=SimpleNamespace(name='DoN',match=lambda p,c:float(abs(p[0]-c[0])))
    flow=DemoFlow(tmp_path,algorithm,capture,roi_geometry=ROI_GEOMETRY_VERSION)
    flow.store.save('p01',np.array([[42.]]),dict(capture_profile='noir-ir',algorithm='DoN',roi_geometry='pklnet-palmkit-native-v1'))
    flow.payments.create_account('p01','Existing name',8300)
    return flow


def test_old_template_excluded_and_reenrollment_preserves_balance(tmp_path):
    flow=make_flow(tmp_path,lambda:(np.array([1.]),'image','pklnet'))
    assert flow.gallery.identify(np.array([42.]),'noir-ir').reason=='INCOMPATIBLE_TEMPLATES'
    assert flow.users()[0]['needs_reenrollment']
    result=flow.enroll('p01','Do not rename account')
    assert result['reenrolled'] and result['balance_cents']==8300
    assert result['display_name']=='Existing name'
    assert not flow.users()[0]['needs_reenrollment']
    assert flow.store.load('p01')[0].shape==(5,1)


def test_failure_on_fifth_capture_does_not_replace_template_or_reset_account(tmp_path):
    calls=[]
    def capture():
        calls.append(1)
        if len(calls)==5: raise ValueError('Low contrast')
        return np.array([1.]),'image','pklnet'
    flow=make_flow(tmp_path,capture)
    with pytest.raises(ValueError,match='Low contrast'): flow.enroll('p01','Existing name')
    np.testing.assert_array_equal(flow.store.load('p01')[0],[[42.]])
    assert flow.payments.balance_for('p01')==8300


def test_quality_pass_is_immediate_without_temporal_wait():
    require_matchable_quality({'contrast':15.,'sharpness':3.})
