from pathlib import Path
import importlib
import pytest
from pklnet_roi import PKLNetROI


@pytest.fixture
def factory(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('shared_localizer_session_pilot').shared_heatmap_view


def test_shared_view_keeps_policy_separate_and_shares_only_resources(factory,monkeypatch):
    source=PKLNetROI(threads=3,policy='illumination')
    source._session=object();source._roi_extractor=object();source.backend_used='onnx'
    monkeypatch.setattr(source,'_ensure_loaded',lambda:None)
    child=factory(source)
    assert child is not source and source.policy=='illumination' and child.policy=='heatmap'
    assert child._session is source._session
    assert child._roi_extractor is source._roi_extractor
    assert child._inference_lock is source._inference_lock
    assert child.threads==source.threads==3
    assert child._torch_branch_cache is not source._torch_branch_cache


def test_legacy_graph_cannot_be_borrowed(factory):
    with pytest.raises(ValueError,match='Legacy'):factory(PKLNetROI(policy='legacy'))


def test_torch_or_unloaded_backend_is_rejected(factory,monkeypatch):
    source=PKLNetROI();monkeypatch.setattr(source,'_ensure_loaded',lambda:None)
    with pytest.raises(ValueError,match='ONNX'):factory(source)
    source._session=object();source._model=object();source.backend_used='torch'
    with pytest.raises(ValueError,match='ONNX'):factory(source)
