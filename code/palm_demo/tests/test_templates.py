from __future__ import annotations

import numpy as np

from templates import TemplateStore


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
