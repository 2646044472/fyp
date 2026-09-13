#!/usr/bin/env python3
"""Small browser UI for the local palm verification smoke test.

The UI keeps frames in memory, serves an MJPEG preview, and calls the same
Fast-CC feature pipeline as palm_demo.py for explicit local enrollment and
verification. It is a debug/demo surface, not an access-control service.
"""

from __future__ import annotations

import argparse
import io
import json
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

import palm_demo
from camera import CameraFeed as SharedCameraFeed


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palm Reg · Pi debug</title>
<style>
body{font:16px system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#17202a;background:#f5f7fa}
main{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);gap:18px}section{background:white;border:1px solid #dce3ea;border-radius:12px;padding:16px;box-shadow:0 2px 8px #0000000d}
preview{position:relative;width:100%;aspect-ratio:16/9;background:#111;border-radius:8px;overflow:hidden}.preview img{display:block;width:100%;height:100%;object-fit:contain}.roi-guide{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.roi-guide .roi-box{fill:#25d36612;stroke:#25d366;stroke-width:.55;stroke-dasharray:2 1}.roi-guide .roi-point{fill:#25d366;stroke:#fff;stroke-width:.35}.roi-guide .roi-cross{stroke:#fff;stroke-width:.35;opacity:.9}.roi-label{position:absolute;left:19%;top:12%;color:#fff;background:#25d366d9;padding:3px 7px;border-radius:4px;font-size:.76rem;font-weight:700;letter-spacing:.02em;pointer-events:none}.roi-panel{margin-top:12px;padding:10px;border:1px solid #dce3ea;border-radius:8px;background:#f8fafb}.roi-preview{display:block;width:220px;height:220px;margin-top:6px;image-rendering:pixelated;background:#111;border-radius:6px}label{display:block;margin:10px 0 6px;font-weight:600}input,select,button{font:inherit;padding:9px;border:1px solid #b8c2cc;border-radius:7px}input,select{width:100%;box-sizing:border-box}button{cursor:pointer;margin:8px 4px 0 0;background:#1769aa;color:white;border:0}button.secondary{background:#5d6d7e}button:disabled{opacity:.5;cursor:wait}.notice{white-space:pre-wrap;background:#eef3f7;padding:10px;border-radius:7px;min-height:42px;margin-top:14px}.small{font-size:.88rem;color:#53616d}h1{margin-top:0} @media(max-width:760px){main{grid-template-columns:1fr}}
</style></head><body><h1>Palm Reg · Pi debug</h1>
<main><section><div class="preview"><img src="/stream" alt="camera preview"></div><p class="small">Green box = the exact crop used by palm_demo.crop_and_normalize(). Place the palm inside it and align the centre with the white dot.</p><div class="roi-panel"><div class="small"><strong>Processing ROI (128×128 normalized)</strong></div><img class="roi-preview" src="/roi" alt="normalized palm processing ROI"></div></section>
<section><label for="user">Local test identity</label><input id="user" value="demo-noir" pattern="[A-Za-z0-9_-]+">
<label for="profile">Capture profile</label><select id="profile"><option value="noir-ir" selected>NoIR + IR light</option><option value="rgb">RGB</option></select>
<label><input id="consent" type="checkbox"> I have approval and participant consent for this local biometric demo.</label>
<button onclick="runAction('enroll')">Enroll 5 samples</button><button class="secondary" onclick="runAction('verify')">Verify</button>
<button class="secondary" onclick="loadUsers()">List users</button><div id="notice" class="notice">Ready.</div>
<p class="small">This is a same-stand 1:1 baseline. It is not liveness detection, anti-spoofing, access control, or a security claim.</p></section></main>
<script>
const notice=document.getElementById('notice');
async function runAction(action){const consent=document.getElementById('consent').checked;if(!consent){notice.textContent='Tick the approval/consent box before camera enrollment or verification.';return}const user=document.getElementById('user').value.trim();const profile=document.getElementById('profile').value;notice.textContent='Working…';try{const r=await fetch('/api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user,profile,consent:true})});const d=await r.json();notice.textContent=d.message||JSON.stringify(d,null,2)}catch(e){notice.textContent='Request failed: '+e}}
async function loadUsers(){const r=await fetch('/api/users');const d=await r.json();notice.textContent=d.users.length?'Enrolled users: '+d.users.join(', '):'No enrolled users.'}
</script></body></html>"""


class _LegacyCameraFeed:
    def __init__(self, index: int, width: int, height: int) -> None:
        from picamera2 import Picamera2

        self.camera = Picamera2(index)
        config = self.camera.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
        self.camera.configure(config)
        self.camera.start()
        self.lock = threading.Lock()
        self.latest: Image.Image | None = None
        self.jpeg: bytes | None = None
        self.roi_jpeg: bytes | None = None
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self) -> None:
        while self.running:
            try:
                image = Image.fromarray(self.camera.capture_array("main"), mode="RGB")
                preview = self._annotate_roi(image)
                output = io.BytesIO()
                preview.save(output, format="JPEG", quality=82)
                roi, _ = palm_demo.crop_and_normalize(image, palm_demo.DEFAULT_CROP)
                roi_image = Image.fromarray(roi, mode="L").resize((384, 384), Image.Resampling.NEAREST).convert("RGB")
                roi_output = io.BytesIO()
                roi_image.save(roi_output, format="JPEG", quality=88)
                with self.lock:
                    self.latest = image
                    self.jpeg = output.getvalue()
                    self.roi_jpeg = roi_output.getvalue()
            except Exception:
                time.sleep(0.2)

    @staticmethod
    def _annotate_roi(image: Image.Image) -> Image.Image:
        """Render the palm ROI guide into the streamed video frame."""
        from PIL import ImageDraw

        preview = image.copy()
        draw = ImageDraw.Draw(preview)
        width, height = preview.size
        x0, y0 = int(width * 0.19), int(height * 0.15)
        x1, y1 = int(width * 0.81), int(height * 0.85)
        green = (37, 211, 102)
        white = (255, 255, 255)
        radius = max(5, int(min(width, height) * 0.012))
        draw.rectangle((x0, y0, x1, y1), outline=green, width=max(2, radius // 2))
        for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) // 2, (y0 + y1) // 2)):
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=green, outline=white, width=2)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        arm = max(12, int(min(width, height) * 0.035))
        draw.line((cx - arm, cy, cx + arm, cy), fill=white, width=2)
        draw.line((cx, cy - arm, cx, cy + arm), fill=white, width=2)
        top = max(4, y0 - 30)
        draw.rounded_rectangle((x0 + 8, top, x0 + 100, top + 24), radius=5, fill=green)
        draw.text((x0 + 16, top + 4), "PALM ROI", fill=white)
        return preview
    def roi_frame(self) -> bytes:
        with self.lock:
            if self.roi_jpeg is None:
                raise RuntimeError("Waiting for the first processing ROI")
            return self.roi_jpeg

    def frame(self) -> Image.Image:
        with self.lock:
            if self.latest is None:
                raise RuntimeError("Waiting for the first camera frame")
            return self.latest.copy()

    def jpeg_frame(self) -> bytes:
        with self.lock:
            if self.jpeg is None:
                raise RuntimeError("Waiting for the first camera frame")
            return self.jpeg

    def close(self) -> None:
        self.running = False
        self.thread.join(timeout=2)
        self.camera.stop()
        self.camera.close()


CameraFeed = SharedCameraFeed


class App:
    def __init__(self, camera: CameraFeed) -> None:
        self.camera = camera
        self.algorithm = palm_demo.load_fastcc(palm_demo.DEFAULT_BASELINE)
        self.lock = threading.Lock()

    def feature(self, image: Image.Image) -> tuple[np.ndarray, dict[str, float], float]:
        started = time.perf_counter()
        roi, quality = palm_demo.crop_and_normalize(image, palm_demo.DEFAULT_CROP)
        if quality["contrast"] < 12.0:
            raise RuntimeError(f"Low contrast ({quality['contrast']:.1f}); improve lighting or hand position.")
        feature = self.algorithm.extract(roi).astype(bool)
        return feature, quality, (time.perf_counter() - started) * 1000

    def enroll(self, user: str, profile: str) -> str:
        with self.lock:
            features: list[np.ndarray] = []
            qualities: list[dict[str, float]] = []
            timings: list[float] = []
            for _ in range(5):
                feature, quality, timing = self.feature(self.camera.frame())
                features.append(feature)
                qualities.append(quality)
                timings.append(timing)
                time.sleep(0.35)
            data_path, meta_path = palm_demo.template_paths(user)
            data_path.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(data_path, features=np.stack(features))
            metadata = {"user": user, "created_at": palm_demo.utc_now(), "algorithm": "FastCC", "camera": 0,
                        "capture_profile": profile, "threshold": 0.28, "samples": 5,
                        "crop": palm_demo.DEFAULT_CROP, "min_contrast": 12.0, "quality": qualities,
                        "pipeline_ms": {"mean": float(np.mean(timings)), "max": float(np.max(timings))},
                        "warning": "Provisional threshold for same-stand debug only."}
            meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            palm_demo.write_log({"event": "enroll", "user": user, "camera": 0, "capture_profile": profile,
                                 "samples": 5, "pipeline_ms_mean": metadata["pipeline_ms"]["mean"]})
            return f"Enrollment complete: {user} (5 samples, mean pipeline {metadata['pipeline_ms']['mean']:.1f} ms)"

    def verify(self, user: str, profile: str) -> str:
        with self.lock:
            data_path, meta_path = palm_demo.template_paths(user)
            if not data_path.exists() or not meta_path.exists():
                raise RuntimeError(f"No template for {user}; enroll first.")
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            if metadata.get("capture_profile") != profile:
                raise RuntimeError(f"Template profile is {metadata.get('capture_profile')!r}, current profile is {profile!r}.")
            feature, quality, timing = self.feature(self.camera.frame())
            stored = np.load(data_path)["features"]
            scores = [float(self.algorithm.match(feature, candidate)) for candidate in stored]
            score = float(np.median(scores))
            accepted = score <= float(metadata.get("threshold", 0.28))
            palm_demo.write_log({"event": "verify", "user": user, "decision": "ACCEPT" if accepted else "REJECT",
                                 "score": score, "threshold": metadata.get("threshold", 0.28), "camera": 0,
                                 "capture_profile": profile, "quality": quality, "pipeline_ms": timing})
            return f"{'ACCEPT' if accepted else 'REJECT'} · distance={score:.4f} · threshold={metadata.get('threshold', 0.28):.4f} · {timing:.1f} ms"


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(app: App) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/":
                body = HTML.encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/roi":
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.end_headers()
                while True:
                    try:
                        frame = app.camera.roi_frame()
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(frame)).encode() + b"\r\n\r\n" + frame + b"\r\n")
                        self.wfile.flush()
                        time.sleep(0.12)
                    except (BrokenPipeError, ConnectionResetError, RuntimeError):
                        break
            elif self.path == "/stream":
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.end_headers()
                while True:
                    try:
                        frame = app.camera.jpeg_frame()
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(frame)).encode() + b"\r\n\r\n" + frame + b"\r\n")
                        self.wfile.flush()
                        time.sleep(0.08)
                    except (BrokenPipeError, ConnectionResetError, RuntimeError):
                        break
            elif self.path == "/api/users":
                directory = palm_demo.RUNTIME / "templates"
                users = sorted(path.stem for path in directory.glob("*.npz")) if directory.exists() else []
                json_response(self, HTTPStatus.OK, {"users": users})
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path not in ("/api/enroll", "/api/verify"):
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})
                return
            try:
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                if not payload.get("consent"):
                    raise RuntimeError("Approval/consent checkbox is required.")
                user = str(payload.get("user", ""))
                profile = str(payload.get("profile", "noir-ir"))
                palm_demo.template_paths(user)  # validate the identifier
                message = app.enroll(user, profile) if self.path.endswith("enroll") else app.verify(user, profile)
                json_response(self, HTTPStatus.OK, {"message": message})
            except Exception as error:
                json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Palm Reg camera debug UI")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    args = parser.parse_args()
    feed = CameraFeed(args.camera, args.width, args.height)
    app = App(feed)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    print(f"Palm debug UI: http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        feed.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())







