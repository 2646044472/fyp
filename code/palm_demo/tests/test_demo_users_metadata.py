"""The demo user list must not decompress biometric template arrays."""
import json
from types import SimpleNamespace

import numpy as np
import pytest

from demo_flow import DemoFlow


@pytest.mark.parametrize("damage", [None, "missing-npz", "missing-json", "bad-json", "non-object", "old-version"])
def test_user_list_reads_only_small_metadata_and_marks_repairs(tmp_path, monkeypatch, damage):
    algorithm = SimpleNamespace(name="metadata-list-test")
    flow = DemoFlow(tmp_path, algorithm, lambda: (_ for _ in ()).throw(AssertionError("No capture")),
                    roi_geometry="test-roi")
    flow.payments.create_account("person", "Demo person", 10000)
    flow.store.save("person", np.zeros((5, 1024), np.uint8),
                    {"algorithm": algorithm.name, "roi_geometry": "test-roi", "capture_profile": "noir-ir"})
    data, metadata = flow.store.paths("person")
    if damage == "missing-npz": data.unlink()
    elif damage == "missing-json": metadata.unlink()
    elif damage == "bad-json": metadata.write_text("{broken", encoding="utf-8")
    elif damage == "non-object": metadata.write_text("[]", encoding="utf-8")
    elif damage == "old-version": metadata.write_text(json.dumps({"algorithm": "old", "roi_geometry": "test-roi"}), encoding="utf-8")
    before = {p.name: p.read_bytes() for p in (data, metadata) if p.exists()}
    monkeypatch.setattr(flow.store, "load", lambda *a: (_ for _ in ()).throw(AssertionError("No NPZ decompression")))
    users = flow.users()
    assert len(users) == 1 and users[0]["display_name"] == "Demo person"
    assert users[0]["needs_reenrollment"] == (damage is not None)
    assert before == {p.name: p.read_bytes() for p in (data, metadata) if p.exists()}
    assert flow.payments.balance_for("person") == 10000
    assert flow.payments.transaction_count() == 0
