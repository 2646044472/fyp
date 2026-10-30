import importlib
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def audit(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('audit_smpd_terminal_boundary')


def test_header_and_version_are_read_without_numpy_array_loading(audit,tmp_path,monkeypatch):
    path=tmp_path/'feature.npz';feature=np.zeros(32,np.uint8)
    feature[:4]=np.asarray([2801066],'<i4').view(np.uint8)
    np.savez_compressed(path,feature=feature)
    monkeypatch.setattr(np,'load',lambda *a,**k:pytest.fail('Array loading/reuse is forbidden in this audit'))
    schema=audit.read_feature_schema(path,expected_shape=(32,))
    assert schema['shape']==[32] and schema['magic']==2801066 and schema['dtype']=='|u1'


def test_wrong_version_shape_or_fields_do_not_pass_as_compatible(audit,tmp_path):
    path=tmp_path/'feature.npz';feature=np.zeros(32,np.uint8)
    np.savez_compressed(path,feature=feature)
    with pytest.raises(ValueError,match='format tag'):audit.read_feature_schema(path)
    feature[:4]=np.asarray([2801066],'<i4').view(np.uint8);np.savez_compressed(path,feature=feature)
    with pytest.raises(ValueError,match='shape'):audit.read_feature_schema(path,expected_shape=(64,))
    np.savez_compressed(path,features=feature)
    with pytest.raises(ValueError,match='container fields'):audit.read_feature_schema(path)
