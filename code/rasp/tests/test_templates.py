from __future__ import annotations

import numpy as np
import pytest

from templates import TemplateStore


@pytest.mark.parametrize('dtype', [np.uint8, np.float32, np.bool_])
def test_fast_lossless_npz_preserves_payload_and_legacy_reader(tmp_path,dtype):
    features=np.arange(120).reshape(5,24).astype(dtype)[:,::2]
    metadata={'algorithm':'experimental','samples':5}
    writer=TemplateStore(tmp_path,compression_level=1)
    writer.save('new',features,metadata)
    restored,loaded=TemplateStore(tmp_path).load('new')
    assert loaded==metadata and restored.dtype==features.dtype
    np.testing.assert_array_equal(restored,features)
    # Existing default-format templates remain readable by the opt-in store.
    TemplateStore(tmp_path).save('old',features,metadata)
    np.testing.assert_array_equal(writer.load('old')[0],features)


@pytest.mark.parametrize('level', [0,10,1.5,True])
def test_invalid_compression_level_rejected(tmp_path,level):
    with pytest.raises(ValueError):TemplateStore(tmp_path,compression_level=level)


def test_store_round_trips_features_and_metadata(tmp_path):
    store = TemplateStore(tmp_path)
    features = np.array([[True, False], [False, True]])
    store.save("stephen", features, {"capture_profile": "rgb", "display_name": "Stephen"})

    loaded_features, metadata = store.load("stephen")
    assert np.array_equal(loaded_features, features)
    assert metadata["capture_profile"] == "rgb"
    assert store.list_users() == ["stephen"]


def test_store_delete_removes_both_files(tmp_path):
    store = TemplateStore(tmp_path)
    store.save("demo", np.ones((1, 2), dtype=bool), {"capture_profile": "rgb"})
    assert store.exists("demo")

    store.delete("demo")

    assert not store.exists("demo")
    assert store.list_users() == []
