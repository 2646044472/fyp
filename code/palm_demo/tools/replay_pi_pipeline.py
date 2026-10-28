"""Audit saved originals and exercise the real HTTP handlers on an isolated runtime.

The camera boundary is replayed, not the ROI, matcher, storage or payment code.
No live captures or production templates/accounts are created by this command.
Every gallery/probe image remains in the offline denominator, including failures.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import hashlib
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import io
import json
from pathlib import Path
import platform
import re
import sys
import threading
import time
from types import SimpleNamespace
import zipfile

import numpy as np
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from palm_app import debug_ui
from palm_app.biometric import load_algorithm
from pklnet_roi import PKLNetROI, normalize_roi, ROI_GEOMETRY_VERSION


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2), encoding="utf-8")


def read_samples(source, output=None):
    archives = sorted(source.glob("*.zip"))
    if archives:
        if output is None:
            raise ValueError("Archive replay needs a fresh output directory")
        staging = output / "archive_inputs"
        provenance = []
        for archive in archives:
            with zipfile.ZipFile(archive) as bundle:
                manifests = [name for name in bundle.namelist() if name.endswith("/manifest.json")]
                if len(manifests) != 1:
                    raise ValueError(f"Expected one session per archive: {archive.name}")
                manifest_name = manifests[0]
                raw_manifest = bundle.read(manifest_name)
                session = json.loads(raw_manifest)
                session_id = session["session_id"]
                sample_ids = session["sample_ids"]
                if not all(re.fullmatch(r"[A-Za-z0-9_-]+", value) for value in [session_id, *sample_ids]):
                    raise ValueError("Invalid session/sample identifier in archive")
                folder = staging / "highres_sessions" / session_id
                folder.mkdir(parents=True, exist_ok=False)
                (folder / "manifest.json").write_bytes(raw_manifest)
                prefix = manifest_name.rsplit("/", 1)[0]
                for index, sample_id in enumerate(sample_ids, 1):
                    target = staging / "highres_capture" / sample_id
                    target.mkdir(parents=True, exist_ok=False)
                    for name in ("full.jpg", "metadata.json"):
                        (target / name).write_bytes(bundle.read(f"{prefix}/sample_{index:03d}/{name}"))
                provenance.append(dict(archive=str(archive), sha256=digest(archive), samples=len(sample_ids)))
        save_json(output / "archive-provenance.json", provenance)
        source = staging
    records = []
    for path in sorted((source / "highres_sessions").glob("*/manifest.json")):
        session = json.loads(path.read_text())
        for index, sample_id in enumerate(session["sample_ids"], 1):
            original = source / "highres_capture" / sample_id / "full.jpg"
            meta = json.loads(original.with_name("metadata.json").read_text())
            if meta.get("sample_id") != sample_id or meta.get("sample_index") != index:
                raise ValueError(f"Manifest/metadata mismatch: {sample_id}")
            records.append(dict(sample=sample_id, identity=session["subject"] + ":" + session["hand"],
                                subject=session["subject"], hand=session["hand"], index=index,
                                original=str(original.resolve()), sha256=digest(original),
                                metadata_index=meta.get("sample_index")))
    if not records:
        raise ValueError("No collection manifests found under source/highres_sessions")
    return records


class ReplayCamera:
    """Explicit file input at the camera boundary; never used by the live service."""

    def __init__(self, capture_only=True, extractor=None):
        self.capture_only = capture_only
        self.roi_mode = "capture" if capture_only else "pklnet"
        self.tracker = SimpleNamespace(extractor=extractor)
        self.queue = []
        self.last = None
        self.size = None

    def select(self, records):
        self.queue = list(records)
        if self.queue:
            with Image.open(self.queue[0]["original"]) as image:
                self.size = list(image.size)

    def capture_highres(self):
        if not self.queue:
            raise RuntimeError("Dataset replay input exhausted")
        self.last = self.queue.pop(0)
        with Image.open(self.last["original"]) as image:
            full = image.convert("RGB")
        return full.resize((640, 360)), full, {"replay_source_sha256": self.last["sha256"]}

    def status(self):
        return dict(camera_ready=True, capture_source="dataset_replay", mode="capture_only" if self.capture_only else "recognition",
                    roi_mode=self.roi_mode, roi_processing=not self.capture_only, quality_status="READY",
                    capture_size=self.size)

    def capture_settings(self):
        return dict(capture_source="dataset_replay", roi_mode=self.roi_mode,
                    roi_processing=not self.capture_only, preview_sensor_output_size=None)


@contextmanager
def http_app(app):
    parent = debug_ui.make_handler(app)

    class QuietHandler(parent):
        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    trace = []

    def request(route, payload=None, expected=None):
        start = time.perf_counter()
        connection = HTTPConnection(*server.server_address, timeout=90)
        body = None if payload is None else json.dumps(payload)
        connection.request("GET" if payload is None else "POST", route, body,
                           {} if body is None else {"Content-Type": "application/json"})
        response = connection.getresponse()
        data = response.read()
        result = json.loads(data) if "application/json" in response.getheader("Content-Type", "") else data
        trace.append(dict(route=route, status=response.status, ms=round((time.perf_counter()-start)*1000, 2),
                          message=result.get("message") if isinstance(result, dict) else None))
        connection.close()
        if expected is not None and response.status != expected:
            raise AssertionError(f"{route}: expected {expected}, got {response.status}: {str(result)[:300]}")
        return response.status, result

    try:
        yield request, trace
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
        if hasattr(app.demo_algorithm,"close"):
            app.demo_algorithm.close()


def collection_roundtrip(records, output):
    debug_ui.common.RUNTIME = output / "collection_runtime"
    camera = ReplayCamera()
    app = debug_ui.App(camera)
    with http_app(app) as (request, trace):
        for route in ("/", "/collect", "/api/status"):
            request(route, expected=200)
        request("/demo", expected=404)
        groups = {}
        for record in records:
            groups.setdefault(record["identity"], []).append(record)
        for identity, samples in groups.items():
            first = samples[0]
            request("/api/collection/start-batch", dict(subject=first["subject"], hand=first["hand"],
                    background="existing", notes="ISOLATED DATASET REPLAY; not a new acquisition"), 200)
            camera.select(samples)
            captured = []
            for original in samples:
                _, result = request("/api/collection/capture-batch", {"client_time": "dataset_replay"}, 200)
                folder = debug_ui.common.RUNTIME / "highres_capture" / result["sample_id"]
                assert {p.name for p in folder.iterdir()} == {"full.jpg", "metadata.json"}
                meta = json.loads((folder / "metadata.json").read_text())
                assert meta["roi_processing"] == "deferred" and not meta["roi_available"]
                captured.append(dict(source=original["sample"], replay=result["sample_id"]))
            _, archive = request("/api/collection/session/" + result["session_id"] + ".zip", expected=200)
            with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
                assert sum(n.endswith("/full.jpg") for n in bundle.namelist()) == len(samples)
            (output / ("collection-" + identity.replace(":", "-") + ".zip")).write_bytes(archive)
            save_json(output / ("collection-" + identity.replace(":", "-") + ".json"), captured)
        request("/api/collection/sessions", expected=200)
    return dict(images=len(records), groups=len(groups), passed=True, http_trace=trace)


def extraction_audit(records, output, policies=("legacy", "heatmap", "aspect", "illumination")):
    algorithms = {name: load_algorithm(debug_ui.common.DEFAULT_BASELINE, name) for name in ("DoN", "FastCC")}
    features = {policy: {name: [] for name in algorithms} for policy in policies}
    extractors = {p: PKLNetROI(policy=p, threads=2) for p in features}
    rows = []
    for index, record in enumerate(records):
        image = Image.open(record["original"]).convert("RGB")
        row = dict(record)
        panel = Image.new("RGB", (600*len(extractors), 480), "white")
        for column, (policy, extractor) in enumerate(extractors.items()):
            started = time.perf_counter()
            raw, quad, detail = extractor.extract(image)
            normal, quality = normalize_roi(raw)
            row[policy] = dict(ms=(time.perf_counter()-started)*1000, details=detail, quality=quality)
            for name, algorithm in algorithms.items():
                features[policy][name].append(algorithm.extract(normal))
            folder = output / "rois" / record["sample"] / policy
            folder.mkdir(parents=True, exist_ok=False)
            Image.fromarray(normal).save(folder / "roi_128.png")
            view = image.copy()
            points = [tuple(map(float, p)) for p in quad]
            draw = ImageDraw.Draw(view)
            draw.line(points+points[:1], fill="lime", width=6)
            view.thumbnail((590, 330))
            panel.paste(view, (column*600, 30))
            panel.paste(Image.fromarray(normal), (column*600, 350))
            ImageDraw.Draw(panel).text((column*600+5, 5), f"{policy} {record['identity']} #{record['index']} geometry={detail['roi_geometry_valid']}", fill="black")
        panel.save(output / "rois" / record["sample"] / "comparison.jpg", quality=91)
        rows.append(row)
        print(f"EXTRACT {index+1}/{len(records)}", flush=True)
    results = []
    identities = sorted({r["identity"] for r in records})
    for policy, algorithms_features in features.items():
        for name, values in algorithms_features.items():
            for strict in (False, True):
                gallery = {key: [i for i, r in enumerate(rows) if r["identity"] == key and r["index"] <= 5
                                and (not strict or r[policy]["details"]["roi_geometry_valid"])] for key in identities}
                trials = []
                for i, row in enumerate(rows):
                    if row["index"] <= 5:
                        continue
                    scores = {}
                    if not strict or row[policy]["details"]["roi_geometry_valid"]:
                        scores = {key: float(np.median([algorithms[name].match(values[i], values[j]) for j in indices]))
                                  for key, indices in gallery.items() if indices}
                    correct = bool(len(scores) == len(identities) and scores[row["identity"]] < min(v for k,v in scores.items() if k != row["identity"]))
                    trials.append(dict(sample=row["sample"], identity=row["identity"], scores=scores, correct=correct,
                                       geometry_valid=row[policy]["details"]["roi_geometry_valid"]))
                results.append(dict(policy=policy, algorithm=name, geometry_guard=strict, correct=sum(t["correct"] for t in trials),
                                    total=len(trials), gallery_sizes={k:len(v) for k,v in gallery.items()}, trials=trials))
    save_json(output / "extraction.json", rows)
    save_json(output / "recognition.json", results)
    return extractors["illumination"], rows, results


def demo_roundtrip(records, extractor, output, demo_matcher="DoN"):
    debug_ui.common.RUNTIME = output / "demo_runtime"
    camera = ReplayCamera(False, extractor)
    app = debug_ui.App(camera, demo_matcher=demo_matcher)
    groups = {key: sorted([r for r in records if r["identity"] == key], key=lambda r:r["index"])
              for key in sorted({r["identity"] for r in records})}
    enrollments, probes, payments = [], [], []
    paid_identities = set()
    with http_app(app) as (request, trace):
        request("/demo", expected=200)
        for identity, samples in groups.items():
            camera.select(samples[:5])
            status, result = request("/api/demo/enroll", dict(user_id=identity.replace(":", "-"), display_name="REPLAY " + identity))
            enrollments.append(dict(identity=identity, http_status=status, result=result))
        _, users = request("/api/demo/users", expected=200)
        for identity, samples in groups.items():
            for record in samples[5:]:
                camera.select([record])
                status, result = request("/api/demo/identify", {}, None)
                result.pop("roi_image", None)
                probes.append(dict(sample=record["sample"], identity=identity, http_status=status, result=result))
                if status == 200 and result.get("token"):
                    confirmation = dict(token=result["token"], user_id=result["user_id"])
                    if result["user_id"] == identity.replace(":", "-") and identity not in paid_identities:
                        _, confirmed = request("/api/demo/confirm", confirmation, 200)
                        assert confirmed["balance_cents"] == 8000
                        request("/api/demo/confirm", confirmation, 400)
                        assert app.demo.payments.balance_for(result["user_id"]) == 8000
                        paid_identities.add(identity)
                        payments.append(dict(identity=identity, heldout_sample=record["sample"], result=confirmed))
                    else:
                        request("/api/demo/cancel", {"token": result["token"]}, 200)
                        request("/api/demo/confirm", confirmation, 400)
        assert app.demo.payments.transaction_count() == len(payments)
        payment = dict(passed=bool(payments), transactions=len(payments), heldout_probes_only=True,
                       repeated_confirmation_blocked=True, cancelled_confirmation_blocked=True, records=payments)
    return dict(enrollments=enrollments, probes=probes, users=users, payment=payment, http_trace=trace,
                warning="HTTP cohort may lack identities whose five-image enrollment failed; use offline recognition.json for full-denominator accuracy.")


def restoration_roundtrip(records, output):
    debug_ui.common.RUNTIME = output / "restoration_runtime"
    camera = ReplayCamera()
    app = debug_ui.App(camera)
    with http_app(app) as (request, trace):
        request("/palmir", expected=200)
        camera.select([records[0]])
        _, first = request("/api/palmir/snapshot", {}, 200)
        selection = dict(snapshot_id=first["snapshot_id"], x=.5, y=.5, size=.5)
        request("/api/palmir/reference", selection, 200)
        camera.select([records[1]])
        _, second = request("/api/palmir/snapshot", {}, 200)
        request("/api/palmir/restore", selection, 400)
        selection["snapshot_id"] = second["snapshot_id"]
        _, result = request("/api/palmir/restore", selection, 200)
        for key in ("original", "restored"):
            (output / ("restoration-" + key + ".png")).write_bytes(base64.b64decode(result.pop(key).split(",", 1)[1]))
        result.pop("source", None)
        assert not result["same_as_reference"]
        assert result["don_comparison"] is not None
    return dict(passed=True, result=result, http_trace=trace,
                warning="HTTP execution check on a fixed central square, not an anatomical ROI or restoration accuracy test.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original runtime or directory of original collection ZIP archives")
    parser.add_argument("output", type=Path, help="New isolated audit directory")
    parser.add_argument("--policies", nargs="+", choices=("legacy", "heatmap", "aspect", "illumination"),
                        default=["legacy", "heatmap", "aspect", "illumination"],
                        help="Policies to compare; must include current illumination policy for HTTP replay")
    parser.add_argument("--demo-matcher", default="DoN", help="Matcher used by real demo HTTP replay")
    args = parser.parse_args()
    if "illumination" not in args.policies or len(set(args.policies)) != len(args.policies):
        parser.error("--policies must include illumination and cannot contain duplicates")
    source, output = args.source.resolve(), args.output.resolve()
    if output == source or source in output.parents:
        raise ValueError("Output must be outside the source runtime to prevent recursive replays")
    output.mkdir(parents=True, exist_ok=False)
    records = read_samples(source, output)
    save_json(output / "input-manifest.json", records)
    original_runtime = debug_ui.common.RUNTIME
    summary = dict(host=platform.node(), platform=platform.platform(), roi_geometry=ROI_GEOMETRY_VERSION,
                   demo_matcher=args.demo_matcher,
                   images=len(records), protocol="Per identity indices 1-5 gallery, 6-10 probe. No identity-based policy selection or sample deletion.",
                   live_camera_tested=False, warning="Historical short bursts are development data, not independent validation.")
    try:
        summary["collection"] = collection_roundtrip(records, output)
        save_json(output / "summary.json", summary)
        extractor, rows, recognition = extraction_audit(records, output, args.policies)
        summary["geometry_pass"] = {p:sum(r[p]["details"]["roi_geometry_valid"] for r in rows) for p in args.policies}
        summary["latency_ms"] = {p:dict(median=float(np.median([r[p]["ms"] for r in rows])), p95=float(np.percentile([r[p]["ms"] for r in rows],95))) for p in args.policies}
        summary["recognition"] = [{k:v for k,v in r.items() if k != "trials"} for r in recognition]
        summary["demo"] = demo_roundtrip(records, extractor, output, args.demo_matcher)
        save_json(output / "summary.json", summary)
        summary["restoration"] = restoration_roundtrip(records, output)
    finally:
        debug_ui.common.RUNTIME = original_runtime
        summary["originals_unchanged"] = all(digest(r["original"]) == r["sha256"] for r in records)
        save_json(output / "summary.json", summary)
    assert summary["originals_unchanged"]
    print(json.dumps({k:summary[k] for k in ("images", "geometry_pass", "latency_ms", "originals_unchanged")}), flush=True)


if __name__ == "__main__":
    main()
