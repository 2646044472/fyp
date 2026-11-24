#!/usr/bin/env python3
"""HTTP acceptance path against generated non-biometric camera frames and a stub model."""
import base64
import io
import json
from pathlib import Path
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from urllib import error, request

import cv2
import numpy as np
from PIL import Image

import fpn_c_e10_station as sut
from palm_app import debug_ui as camera_contract


def main():
    rng = np.random.default_rng(338)
    images = [Image.fromarray(rng.integers(0, 256, (160, 192, 3), dtype=np.uint8)) for _ in range(41)]
    frame_class = camera_contract.CapturedFrame
    backend = SimpleNamespace(
        crop_gray=lambda m, arr, *, device: (
            arr[:128, :128, 0].copy(), "valid", np.array(((0, 0), (128, 0), (128, 128), (0, 128)), dtype=float)),
        encode_c=lambda m, arr, *, device: np.pad(
            np.asarray(arr[:, 0, :], dtype=np.float32) + 1., ((0, 0), (0, 384))),
    )

    # The FPN route must discard a geometrically valid but stale crop.
    assert sut.classify_frame(np, cv2, backend, object(), np.asarray(images[0]),
                              processed_age=lambda: sut.MAX_FRAME_AGE + .001)[-1] == "fpn_frame_stale"

    class Feed:
        capture_profile = "synthetic-only"
        camera_backend = "synthetic"

        def __init__(self):
            self.running = True
            self.lock = threading.Lock()
            self.frame_condition = threading.Condition(self.lock)
            self.latest = self.pending_frame = self.latest_processed = None
            self.latest_roi_status = {}
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            self.producer = threading.Thread(target=self.stream, daemon=True)
            self.producer.start()

        def stream(self):
            index = 0
            while self.running:
                with self.frame_condition:
                    index += 1
                    self.latest = self.pending_frame = frame_class(index, images[index % len(images)], time.monotonic())
                    self.frame_condition.notify_all()
                time.sleep(.07)

        def status(self):
            return dict(self.latest_roi_status, camera_ready=True, processing_thread_alive=True, roi_status_fresh=True)

        def _camera_frame_state(self):
            return {"camera_ready": True}

        def capture_ready_processed_frame(self):
            raise AssertionError("would reach legacy capture")
        capture_highres = capture_ready_processed_frame

        def close(self):
            with self.frame_condition:
                self.running = False
                self.frame_condition.notify_all()
            self.processing_thread.join(timeout=2)
            self.producer.join(timeout=2)

    base = SimpleNamespace(CameraFeed=Feed, App=object, ProcessedFrame=camera_contract.ProcessedFrame,
                           CaptureProcessingFailure=camera_contract.CaptureProcessingFailure,
                           _capture_readiness_gate_failure=camera_contract._capture_readiness_gate_failure)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "isolated"
        identity = "synthetic-checkpoint-identities"
        with sut.open_workspace(root, identity):
            Camera, App = sut.station_stack(base, backend, object(), object(), root, identity, np, cv2)
            feed = Camera()
            app = App(feed)
            page = sut.render_enrollment()
            assert "FPN + C E10" in page and "60 秒" in page and "station-review" in page
            assert 'id="save" hidden' in page and 'id="verify-start"' in page
            assert 'aria-current=page>② 放掌验证' in sut.render_enrollment("/gate")
            server = ThreadingHTTPServer(("127.0.0.1", 0), sut.build_handler(app, page))
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            origin = f"http://127.0.0.1:{server.server_port}"

            def http(path, data=None, *, status=200, headers=None):
                hdr = {"Content-Type": "application/json", **(headers or {})}
                r = request.Request(origin + path, data=None if data is None else json.dumps(data).encode(),
                                    headers=hdr)
                try:
                    with request.urlopen(r, timeout=6) as f:
                        assert status == f.status, (path, status, f.status)
                        raw = f.read()
                        return json.loads(raw) if f.headers.get_content_type() == "application/json" else raw
                except error.HTTPError as e:
                    assert status == e.code, (path, status, e.code, e.read())
                    return json.loads(e.read())

            try:
                assert http("/station-health")["backend"] == sut.PIPELINE
                for route in ("/api/demo/identify", "/api/demo/confirm", "/api/gate/identify", "/api/demo/cancel",
                              "/api/collection/start"):
                    http(route, {}, status=404)
                http("/api/fpn/score", {}, status=403, headers={"Origin": "http://example.invalid"})
                token = "a" * 32
                t = {"token": token}
                http("/api/demo/enroll/start", dict(t, user_id="synthetic", display_name="Synthetic", hand="left"))
                w = app.demo.enrollment_session["station_window"]
                assert w.absolute_timeout_s == 60 and w.target_count == sut.CAPTURE_COUNT
                for _ in range(sut.CAPTURE_COUNT + 3):
                    assert http("/api/demo/enroll/step", t)["status"] != "READY"
                http("/api/station/enroll-select", t, status=400)
                with app.demo.lock:
                    w.absolute_timeout_s = time.monotonic() - w.started_s
                assert http("/api/station/enroll-review", t)["state"] == "collecting"
                result = http("/api/station/enroll-select", t)
                assert result["kept"] == sut.CAPTURE_COUNT, result["state"]
                assert not list((root / "templates").glob("*"))
                for item in result["items"]:
                    # Prove review image/crop refer to the same accepted exposure.
                    frame = np.asarray(images[item["frame"] % len(images)])[:128, :128, 0]
                    roi = Image.open(io.BytesIO(base64.b64decode(item["roi"])))
                    expected = io.BytesIO()
                    images[item["frame"] % len(images)].save(expected, "JPEG", quality=87)
                    assert base64.b64decode(item["rgb"]) == expected.getvalue()
                    assert np.array_equal(frame, np.asarray(roi))
                drop = result["items"][0]["frame"]
                after_remove = http("/api/station/enroll-remove", dict(t, frame=drop))
                assert after_remove["kept"] == sut.CAPTURE_COUNT - 1 and drop not in [x["frame"] for x in after_remove["items"]]
                http("/api/demo/enroll/commit", dict(t, confirm_hand="left"), status=400)
                http("/api/station/enroll-refill", t)
                for _ in range(2):
                    http("/api/demo/enroll/step", t)
                assert http("/api/station/enroll-select", t)["kept"] == sut.CAPTURE_COUNT
                http("/api/demo/enroll/commit", dict(t, confirm_hand="right"), status=400)
                result = http("/api/demo/enroll/commit", dict(t, confirm_hand="left"))
                assert "token" not in result and "balance_cents" not in result
                data, meta = app.demo.store.load("synthetic")
                assert meta["algorithm"] == sut.PIPELINE and meta["matcher_runtime_identity"] == identity
                assert data.shape == (sut.TEMPLATE_COUNT, 512)
                archive = result["enrollment_archive_id"]
                assert len(http("/api/library/list", {})["archives"][0]["samples"]) == sut.CAPTURE_COUNT
                assert Image.open(io.BytesIO(http("/api/library/image",
                    {"archive": archive, "index": sut.CAPTURE_COUNT, "kind": "model"}))).size == (128, 128)
                verified = sut.score_gallery(np, data[0], app.demo.store, app.demo.gallery.required_metadata,
                                             threshold=sut.DEMO_MATCH_THRESHOLD)
                assert verified["decision"] == "MATCH" and verified["best_match"]["archive_id"] == archive
                assert not list(root.rglob("*.sqlite3"))
                score = http("/api/fpn/score", {})
                assert set(score) == {"mode", "gallery_size", "top_cosines", "tied_top"}
                assert score["gallery_size"] == 1 and len(score["top_cosines"]) == 1
                # Reject a shape-compatible foreign template rather than silently using it.
                data, meta = app.demo.store.load("synthetic")
                app.demo.store.save("test_wrong_version", data, dict(meta, algorithm="legacy"))
                time.sleep(.15)  # no duplicate exposure; fail due to wrong template, not age/ID
                try:
                    sut.score_gallery(np, data[0], app.demo.store, app.demo.gallery.required_metadata)
                except ValueError as e:
                    assert "模板版本" in str(e)
                else:
                    raise AssertionError("shape-compatible legacy template accepted")
                http("/api/fpn/score", {}, status=400)
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=2)
                feed.close()
        legacy = Path(td) / "legacy"
        legacy.mkdir(mode=0o700)
        (legacy / "unrelated").touch()
        try:
            sut.open_workspace(legacy, identity)
        except sut.ShadowFailure as e:
            assert str(e) == "runtime_not_empty_or_legacy" and [f.name for f in legacy.iterdir()] == ["unrelated"]
        else:
            raise AssertionError("legacy runtime accepted")
        try:
            sut.open_workspace(root, "wrong-weights")
        except sut.ShadowFailure as e:
            assert str(e) == "runtime_identity_mismatch"
        else:
            raise AssertionError("foreign runtime accepted")
    print("PASS: actual V3 HTTP enrollment; same-frame pairs, delete/refill, confirmation, private score-only namespace")


if __name__ == "__main__":
    main()
