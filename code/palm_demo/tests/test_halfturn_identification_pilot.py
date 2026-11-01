import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('fixed_pilot_driver',Path(__file__).resolve().parents[1]/'tools/pilot_halfturn_identification.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
driver.QUERIES=[f'fixture-001-Q-{i}' for i in range(8)]


def test_fixed_selection_rejects_replacement():
    driver.validate_selection(driver.QUERIES)
    changed=list(driver.QUERIES);changed[0]='fixture-001-Q-replacement'
    with pytest.raises(ValueError):driver.validate_selection(changed)


def test_fixed_selection_rejects_duplicate():
    changed=list(driver.QUERIES);changed[0]=changed[1]
    with pytest.raises(ValueError):driver.validate_selection(changed)


def fixture():
    old={'payload':{'result':{'recognition_route':'pose_confident'},'scores':{'a':.1,'b':.4}}}
    new={'outcome':'correct','result':{'recognition_route':'pose_confident'},'scores':{'a':.1,'b':.4,'new':.6},
         'primary_historical_exact':True,'selected_primary_verbatim':True}
    return old,new


def test_control_projection_allows_added_identity_only():
    old,new=fixture();assert all(driver.control_comparison(new,old,['a','b']).values())


def test_control_changed_route_or_original_score_rejected():
    old,new=fixture();new['scores']['a']=.100001
    assert not driver.control_comparison(new,old,['a','b'])['original86_scores_exact']
    new['result']['recognition_route']='exhaustive'
    assert not driver.control_comparison(new,old,['a','b'])['route_unchanged']


def test_control_identity_or_roi_loss_rejected():
    old,new=fixture();new['outcome']='wrong_identity_accepted';new['selected_primary_verbatim']=False
    result=driver.control_comparison(new,old,['a','b'])
    assert not result['correct_preserved'] and not result['original_roi_exact']
