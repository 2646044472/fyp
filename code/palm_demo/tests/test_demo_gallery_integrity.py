"""Device queries must not silently lose enrolled identities from their gallery."""

import json

import numpy as np
import pytest

from demo_flow import DemoFlow


class DistanceAlgorithm:
    name = "integrity-test"

    def match(self, probe, candidate):
        return abs(float(probe[0]) - float(candidate[0]))


class PreparedDistance(DistanceAlgorithm):
    def __init__(self):
        self.preparations = 0

    def prepare_probe(self, probe):
        return probe

    def prepare_enrollment(self, features):
        self.preparations += 1
        if features.shape != (5, 1):
            raise ValueError("Invalid packed enrollment")
        return features.copy()

    def prepared_bytes(self, features):
        return features.nbytes

    def score_prepared(self, probe, enrolled):
        return float(np.mean(np.abs(enrolled[:, 0] - probe[0])))


def make_flow(tmp_path, algorithm=None):
    captures = []

    def capture():
        captures.append(True)
        return np.array([0.1]), "roi", "test-camera"

    return DemoFlow(tmp_path, algorithm or DistanceAlgorithm(), capture, roi_geometry="test-roi"), captures


def add_identity(flow, user_id, value, *, profile="noir-ir", account=True, **metadata):
    fields = {"capture_profile": profile, "algorithm": flow.algorithm.name, "roi_geometry": "test-roi"}
    fields.update(metadata)
    data, meta = flow.store._legacy_paths(user_id)
    data.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(data, features=np.full((5, 1), value))
    meta.write_text(json.dumps(fields), encoding="utf-8")
    if account:
        flow.payments.create_account(user_id, user_id, 10000)


def assert_blocked(flow, captures, reason):
    flow.pending["stale-token"] = ("good", 2000, float("inf"))
    result = flow.identify()
    assert result["status"] == "RETRY" and result["reason"] == reason
    assert "token" not in result and "user_id" not in result
    assert not flow.pending and not captures
    assert flow.payments.transaction_count() == 0
    assert flow.payments.balance_for("good") == 10000
    assert result["timing_ms"]["capture_and_extract"] == 0
    assert result["timing_ms"]["total"] == result["timing_ms"]["gallery"]


@pytest.mark.parametrize("missing_suffix", [".npz", ".json"])
def test_incomplete_template_cannot_turn_a_query_into_another_person(tmp_path, missing_suffix):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, "good", 0.1)
    add_identity(flow, "competitor", 0.7)
    data, meta = flow.store.paths("good")
    (data if missing_suffix == ".npz" else meta).unlink()
    assert "good" not in flow.store.list_users()
    assert "good" in flow.store.list_template_ids()
    assert_blocked(flow, captures, "GALLERY_INCOMPLETE_TEMPLATES")


def test_account_with_both_template_files_missing_is_reported(tmp_path):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, "good", 0.1)
    for path in flow.store.paths("good"):
        path.unlink()
    assert_blocked(flow, captures, "GALLERY_INCOMPLETE_TEMPLATES")


@pytest.mark.parametrize("damage", ["npz", "json", "metadata-list", "missing-profile", "nan", "empty", "partial-enrollment"])
def test_corrupt_template_is_reported_instead_of_silently_skipped(tmp_path, damage):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, "good", 0.1)
    add_identity(flow, "competitor", 0.7)
    data, meta = flow.store.paths("good")
    if damage == "npz":
        data.write_bytes(b"broken npz")
    elif damage == "json":
        meta.write_text("{broken", encoding="utf-8")
    elif damage == "metadata-list":
        meta.write_text("[]", encoding="utf-8")
    elif damage == "missing-profile":
        metadata = json.loads(meta.read_text(encoding="utf-8"))
        del metadata["capture_profile"]
        meta.write_text(json.dumps(metadata), encoding="utf-8")
    else:
        features = (np.full((5, 1), float("nan")) if damage == "nan" else
                    np.zeros((2 if damage == "partial-enrollment" else 0, 1)))
        np.savez_compressed(data, features=features)
    assert_blocked(flow, captures, "GALLERY_INVALID_TEMPLATES")


@pytest.mark.parametrize("field", ["algorithm", "roi_geometry"])
def test_mixed_compatible_and_incompatible_templates_block_device_identification(tmp_path, field):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, "good", 0.1, **{field: "old-version"})
    add_identity(flow, "competitor", 0.7)
    assert_blocked(flow, captures, "GALLERY_INCOMPATIBLE_TEMPLATES")


@pytest.mark.parametrize("change", ["different-model", "missing-contract"])
def test_runtime_contract_change_blocks_capture_even_after_cache_warmup(tmp_path, change):
    algorithm = PreparedDistance()
    algorithm.runtime_identity = {"model": "a", "feature_contract": "roi-encoder-v1"}
    flow, captures = make_flow(tmp_path, algorithm)
    add_identity(flow, "good", 0.1, matcher_runtime_identity=algorithm.runtime_identity)
    add_identity(flow, "competitor", 0.7, matcher_runtime_identity=algorithm.runtime_identity)
    assert flow.identify()["status"] == "MATCH"
    assert len(captures) == 1
    captures.clear()
    _, metadata_path = flow.store.paths("good")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if change == "different-model":
        metadata["matcher_runtime_identity"]["model"] = "b"
    else:
        del metadata["matcher_runtime_identity"]
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    assert_blocked(flow, captures, "GALLERY_INCOMPATIBLE_TEMPLATES")
    assert next(x for x in flow.users() if x["user_id"] == "good")["needs_reenrollment"]


def test_usable_device_template_without_account_is_reported(tmp_path):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, "good", 0.1)
    add_identity(flow, "orphan", 0.7, account=False)
    assert_blocked(flow, captures, "GALLERY_ACCOUNT_MISMATCH")


@pytest.mark.parametrize('suffix', ['.npz', '.json'])
@pytest.mark.parametrize('continuous', [False, True])
def test_incomplete_template_is_not_overwritten_by_enrollment(tmp_path, suffix, continuous):
    flow, captures = make_flow(tmp_path)
    paths = flow.store.paths('orphan')
    path = paths[0] if suffix == '.npz' else paths[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    original = b'keep-incomplete-template'
    path.write_bytes(original)
    with pytest.raises(ValueError, match='incomplete'):
        if continuous:
            flow.enrollment_start('orphan', 'Orphan', 'left')
        else:
            flow.enroll('orphan', 'Orphan')
    assert path.read_bytes() == original
    assert not captures and not flow.payments.user_exists('orphan')


def test_incomplete_template_created_during_enrollment_is_not_overwritten(tmp_path):
    flow, _ = make_flow(tmp_path)
    token = flow.enrollment_start('orphan', 'Orphan', 'left')['token']
    flow.enrollment_session['features'] = [np.array([i]) for i in range(5)]
    path, _ = flow.store.paths('orphan')
    path.parent.mkdir(parents=True, exist_ok=True)
    original = b'keep-incomplete-template'
    path.write_bytes(original)
    with pytest.raises(ValueError, match='incomplete'):
        flow.enrollment_commit(token, 'left')
    assert path.read_bytes() == original
    assert not flow.payments.user_exists('orphan')


def test_other_capture_profile_is_an_ordinary_exclusion(tmp_path):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, "good", 0.1)
    add_identity(flow, "rgb-only", 0.1, profile="rgb", account=False, algorithm="other-algorithm")
    result = flow.identify()
    assert result["status"] == "MATCH" and result["user_id"] == "good"
    assert result["score"] == 0.0 and result["second_score"] is None
    assert len(captures) == 1 and result["token"] in flow.pending
    assert flow.payments.transaction_count() == 0


def test_unchanged_prepared_templates_are_validated_once_and_replacement_is_rechecked(tmp_path):
    algorithm = PreparedDistance()
    flow, captures = make_flow(tmp_path, algorithm)
    add_identity(flow, "good", 0.1)
    add_identity(flow, "competitor", 0.7)
    for _ in range(2):
        result = flow.identify()
        assert result["status"] == "MATCH" and result["user_id"] == "good"
    assert algorithm.preparations == 2
    data, _ = flow.store.paths("good")
    np.savez_compressed(data, features=np.zeros((2, 1)))
    result = flow.identify()
    assert result["status"] == "RETRY" and result["reason"] == "GALLERY_INVALID_TEMPLATES"
    assert "token" not in result and not flow.pending
    assert len(captures) == 2 and algorithm.preparations == 3


def test_exact_tie_does_not_create_a_payment_token(tmp_path):
    flow, _ = make_flow(tmp_path)
    add_identity(flow, "a", 0.1)
    add_identity(flow, "z", 0.1)
    result = flow.identify()
    assert result["status"] == "RETRY" and result["reason"] == "TIED_BEST_SCORES"
    assert "token" not in result and not flow.pending
    assert flow.payments.transaction_count() == 0


def test_new_incomplete_account_invalidates_a_previously_healthy_gallery(tmp_path):
    flow, captures = make_flow(tmp_path, PreparedDistance())
    add_identity(flow, "good", 0.1)
    assert flow.identify()["status"] == "MATCH"
    flow.payments.create_account("missing", "Missing", 10000)
    captures.clear()
    assert_blocked(flow, captures, "GALLERY_INCOMPLETE_TEMPLATES")


def test_enrollment_ready_does_not_hide_an_existing_incomplete_gallery(tmp_path):
    class WarmPrepared(PreparedDistance):
        def __init__(self):
            super().__init__()
            self.warm_calls = 0
        def prepare_gallery(self, groups):
            self.warm_calls += 1
    algorithm = WarmPrepared()
    flow, _ = make_flow(tmp_path, algorithm)
    add_identity(flow, 'old', 0.1)
    flow.store.paths('old')[0].unlink()
    result = flow.enroll('new', 'New')
    assert result['recognition_ready'] is False
    assert result['preparation_error'] == 'GALLERY_INCOMPLETE_TEMPLATES'
    assert algorithm.warm_calls == 0
    assert flow.store.exists('new') and flow.payments.user_exists('new')


def test_enrollment_ready_after_integrity_and_warmup_succeed(tmp_path):
    class WarmPrepared(PreparedDistance):
        def __init__(self):
            super().__init__()
            self.warm_calls = 0
        def prepare_gallery(self, groups):
            self.warm_calls += 1
            assert set(groups) == {'new'}
    algorithm = WarmPrepared()
    flow, _ = make_flow(tmp_path, algorithm)
    result = flow.enroll('new', 'New')
    assert result['recognition_ready'] is True and algorithm.warm_calls == 1


def test_automatic_commit_preserves_template_when_gallery_warmup_fails(tmp_path):
    class WarmFailure(PreparedDistance):
        def prepare_gallery(self, groups):
            raise RuntimeError('injected warmup failure')

    flow, _ = make_flow(tmp_path, WarmFailure())
    token = flow.enrollment_start('new_left', 'New', 'left')['token']
    flow.enrollment_session['features'] = [np.array([0.1]) for _ in range(5)]
    result = flow.enrollment_commit(token, 'left')
    assert result['recognition_ready'] is False
    assert result['preparation_error'] == 'injected warmup failure'
    assert flow.store.exists('new_left') and flow.payments.user_exists('new_left')
    assert flow.enrollment_status(token) == {'status': 'COMPLETED'}


def test_only_other_capture_profile_returns_no_enrolled_users(tmp_path):
    flow, captures = make_flow(tmp_path)
    add_identity(flow, 'existing', 0.1, profile='rgb')
    result = flow.identify()
    assert result['status'] == 'UNKNOWN'
    assert result['reason'] == 'NO_ENROLLED_USERS'
    assert len(captures) == 1 and len(flow.payments.list_users()) == 1
    assert 'token' not in result and not flow.pending
