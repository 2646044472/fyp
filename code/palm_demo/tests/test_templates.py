from __future__ import annotations

import numpy as np

from templates import TemplateStore


def test_template_store_round_trips_features_and_metadata(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    features = np.array([[True, False], [False, True]])

    store.save("P001", features, {"capture_profile": "rgb", "algorithm": "FastCC"})

    loaded_features, metadata = store.load("P001")
    assert np.array_equal(loaded_features, features)
    assert metadata["capture_profile"] == "rgb"
    assert metadata["algorithm"] == "FastCC"


def test_template_store_rejects_path_traversal_and_can_delete_user(tmp_path):
    store = TemplateStore(tmp_path / "templates")

    try:
        store.save("../escape", np.array([[1]]), {})
    except ValueError:
        pass
    else:
        raise AssertionError("path traversal user id was accepted")

    store.save("P001", np.array([[1]]), {})
    assert store.exists("P001")
    store.delete("P001")
    assert not store.exists("P001")
