"""HTTP-level enrollment regressions using synthetic captures and temporary stores."""

import json
import threading
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np

from demo_flow import DemoFlow
from palm_app.debug_ui import make_handler


class EnrollmentAlgorithm:
    name = "atomic-http-test"


def synthetic_candidate(index):
    y, x = np.indices((32, 32))
    roi = ((x * (index + 1) + y * (index + 3) + (x * y) % (index + 5)) % 256).astype(np.uint8)
    angle = index * 0.035
    center = np.array([48.0 + index * 1.1, 50.0 - index * 0.7])
    u = np.array([np.cos(angle), np.sin(angle)]) * (18 + index % 3)
    v = np.array([-np.sin(angle), np.cos(angle)]) * (15 + index % 4)
    quad = np.stack([center-u-v, center+u-v, center+u+v, center-u+v]).astype(np.float32)
    feature = np.full((4,), index, dtype=np.float32)
    return feature, f"roi-{index}", "synthetic", {"contrast": 25, "sharpness": 8}, roi, {
        "roi_quad": quad, "frame_size": (100, 100),
    }


def make_flow(root):
    flow = DemoFlow(root, EnrollmentAlgorithm(), lambda: (np.zeros(4), "", "synthetic"))
    flow.gallery.warm_up = lambda **_kwargs: None
    return flow


class HttpFlow:
    def __init__(self, root):
        self.root = root
        self.flow = make_flow(root)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0),
            type("QuietHandler", (make_handler(SimpleNamespace(capture_only=False, demo=self.flow)),),
                 {"log_message": lambda *_args: None}))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def post(self, action, payload):
        request = Request(f"http://127.0.0.1:{self.server.server_port}/api/demo/enroll/{action}",
                          data=json.dumps(payload).encode(),
                          headers={"Content-Type": "application/json"})
        try:
            response = urlopen(request, timeout=3)
        except HTTPError as error:
            return error.code, json.loads(error.read())
        with response:
            return response.status, json.loads(response.read())

    def enroll_candidates(self, user_id, display_name, hand="left"):
        status, started = self.post("start", {"user_id": user_id, "display_name": display_name, "hand": hand})
        assert status == 200, started
        token = started["token"]
        self.flow.enrollment_candidate = iter(synthetic_candidate(i) for i in range(1, 9)).__next__
        states = [self.post("step", {"token": token}) for _ in range(8)]
        assert all(code == 200 for code, _ in states)
        assert states[-1][1]["status"] == "READY"
        return token


def test_http_eight_candidates_commit_and_reopen_template_and_account(tmp_path):
    http = HttpFlow(tmp_path)
    try:
        token = http.enroll_candidates("new_left", "New")
        code, committed = http.post("commit", {"token": token, "confirm_hand": "left"})
        assert code == 200 and committed["user_id"] == "new_left"
        assert committed["reenrolled"] is False
    finally:
        http.close()

    reopened = make_flow(tmp_path)
    features, metadata = reopened.store.load("new_left")
    assert features.shape == (5, 4)
    assert metadata["enrollment_selection"]["candidate_count"] == 8
    assert metadata["enrollment_selection"]["selected_frame_ids"]
    assert reopened.payments.user_exists("new_left")
    assert reopened.payments.balance_for("new_left") == 10000


def test_http_refreshes_legacy_generation_without_changing_legacy_bytes(tmp_path):
    seed = make_flow(tmp_path)
    legacy_npz = seed.store.root / "legacy_left.npz"
    legacy_json = seed.store.root / "legacy_left.json"
    seed.store.root.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(legacy_npz, features=np.zeros((5, 4), dtype=np.float32))
    legacy_json.write_text(json.dumps({
        "user": "legacy_left", "display_name": "Legacy", "algorithm": "old-algorithm",
        "capture_profile": "old-profile", "samples": 5, "hand_declared_by_user": "left",
    }), encoding="utf-8")
    seed.payments.create_account("legacy_left", "Legacy", 10000)
    originals = legacy_npz.read_bytes(), legacy_json.read_bytes()

    http = HttpFlow(tmp_path)
    try:
        token = http.enroll_candidates("legacy_left", "ignored display name")
        code, committed = http.post("commit", {"token": token, "confirm_hand": "left"})
        assert code == 200 and committed["reenrolled"] is True
    finally:
        http.close()

    assert (legacy_npz.read_bytes(), legacy_json.read_bytes()) == originals
    reopened = make_flow(tmp_path)
    features, metadata = reopened.store.load("legacy_left")
    assert features.shape == (5, 4)
    assert metadata["capture_profile"] == reopened.capture_profile
    assert reopened.payments.display_name_for("legacy_left") == "Legacy"
    assert reopened.payments.balance_for("legacy_left") == 10000


def test_http_atomic_replace_failure_keeps_existing_generation(tmp_path, monkeypatch):
    http = HttpFlow(tmp_path)
    try:
        # Seed an incompatible legacy generation with a matching account, so this is a refresh.
        http.flow.store.root.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(http.flow.store.root / "retry_left.npz", features=np.full((5, 4), -1, dtype=np.float32))
        (http.flow.store.root / "retry_left.json").write_text(json.dumps({
            "user": "retry_left", "display_name": "Retry", "algorithm": "old",
            "capture_profile": "old", "hand_declared_by_user": "left",
        }), encoding="utf-8")
        http.flow.payments.create_account("retry_left", "Retry", 10000)
        old_features, old_metadata = http.flow.store.load("retry_left")
        token = http.enroll_candidates("retry_left", "Retry")
        import templates
        monkeypatch.setattr(templates.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError("injected replace failure")))
        code, error = http.post("commit", {"token": token, "confirm_hand": "left"})
        assert code == 400 and "injected replace failure" in error["message"]
        current_features, current_metadata = make_flow(tmp_path).store.load("retry_left")
        np.testing.assert_array_equal(current_features, old_features)
        assert current_metadata == old_metadata
        assert http.flow.payments.user_exists("retry_left")
    finally:
        http.close()


def test_http_account_commit_uncertainty_retains_atomic_template(tmp_path, monkeypatch):
    http = HttpFlow(tmp_path)
    try:
        token = http.enroll_candidates("account_left", "Account")
        create = http.flow.payments.create_account

        def commit_then_raise(*args, **kwargs):
            create(*args, **kwargs)
            raise RuntimeError("injected account response loss")

        monkeypatch.setattr(http.flow.payments, "create_account", commit_then_raise)
        code, error = http.post("commit", {"token": token, "confirm_hand": "left"})
        assert code == 400 and "模板已保留" in error["message"]
        reopened = make_flow(tmp_path)
        features, metadata = reopened.store.load("account_left")
        assert features.shape == (5, 4) and metadata["user"] == "account_left"
        assert reopened.payments.user_exists("account_left")
    finally:
        http.close()


def test_http_cancel_leaves_no_template_or_account(tmp_path):
    http = HttpFlow(tmp_path)
    try:
        code, started = http.post("start", {"user_id": "cancel_left", "display_name": "Cancel", "hand": "left"})
        assert code == 200
        http.flow.enrollment_candidate = iter(synthetic_candidate(i) for i in range(1, 9)).__next__
        for _ in range(3):
            code, _ = http.post("step", {"token": started["token"]})
            assert code == 200
        code, cancelled = http.post("cancel", {"token": started["token"]})
        assert code == 200 and cancelled["status"] == "CANCELLED"
        assert not http.flow.store.exists("cancel_left")
        assert not http.flow.payments.user_exists("cancel_left")
    finally:
        http.close()
