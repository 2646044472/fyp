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
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import numpy as np
from PIL import Image

import palm_demo
import palm_roi
from biometric import load_algorithm
from live_roi import LiveROIOverlay
from roi_quality import DebugDatasetWriter, ROIQualityGate


DEFAULT_HAND_MODEL = palm_demo.ROOT / "models" / "palm_detection_mediapipe_2023feb.onnx"
DEFAULT_HAND_POSE_MODEL = palm_demo.ROOT / "models" / "handpose_estimation_mediapipe_2023feb.onnx"
DEBUG_MATCHER = "DoN"
DEBUG_MIN_THRESHOLD = 0.15
DEBUG_MAX_THRESHOLD = 0.20


@dataclass(frozen=True)
class CapturedFrame:
    frame_id: int
    image: Image.Image
    captured_monotonic: float


@dataclass(frozen=True)
class ProcessedFrame:
    captured: CapturedFrame
    roi_quad: np.ndarray | None
    roi: np.ndarray
    roi_status: dict[str, Any]


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palm Reg · Pi debug</title>
<style>
body{font:16px system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#17202a;background:#f5f7fa}
main{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);gap:18px}section{background:white;border:1px solid #dce3ea;border-radius:12px;padding:16px;box-shadow:0 2px 8px #0000000d}
preview{position:relative;width:100%;aspect-ratio:16/9;background:#111;border-radius:8px;overflow:hidden}.preview img{display:block;width:100%;height:100%;object-fit:contain}.roi-guide{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.roi-guide .roi-box{fill:#25d36612;stroke:#25d366;stroke-width:.55;stroke-dasharray:2 1}.roi-guide .roi-point{fill:#25d366;stroke:#fff;stroke-width:.35}.roi-guide .roi-cross{stroke:#fff;stroke-width:.35;opacity:.9}.roi-label{position:absolute;left:19%;top:12%;color:#fff;background:#25d366d9;padding:3px 7px;border-radius:4px;font-size:.76rem;font-weight:700;letter-spacing:.02em;pointer-events:none}.roi-panel{margin-top:12px;padding:10px;border:1px solid #dce3ea;border-radius:8px;background:#f8fafb}.roi-preview{display:block;width:220px;height:220px;margin-top:6px;image-rendering:pixelated;background:#111;border-radius:6px}label{display:block;margin:10px 0 6px;font-weight:600}input,select,button{font:inherit;padding:9px;border:1px solid #b8c2cc;border-radius:7px}input,select{width:100%;box-sizing:border-box}button{cursor:pointer;margin:8px 4px 0 0;background:#1769aa;color:white;border:0}button.secondary{background:#5d6d7e}button:disabled{opacity:.5;cursor:wait}.notice{white-space:pre-wrap;background:#eef3f7;padding:10px;border-radius:7px;min-height:42px;margin-top:14px}.small{font-size:.88rem;color:#53616d}.status{font-weight:700}.ready{background:#e4f7ea;color:#126b2d}.blocked{background:#fff0ef;color:#9b241c}h1{margin-top:0} @media(max-width:760px){main{grid-template-columns:1fr}}
</style></head><body><h1>Palm Reg · Pi debug</h1>
<main><section><div class="preview"><img id="stream" src="/frame.jpg" alt="camera preview"></div><p class="small">The green quadrilateral follows the tracked palm. Keep one hand visible and wait for the tracking status before enrolling or verifying.</p><div class="roi-panel"><div class="small"><strong>Processing ROI (128×128 normalized)</strong></div><img id="roi" class="roi-preview" src="/roi.jpg" alt="normalized palm processing ROI"></div></section>
<section><div id="roi-status" class="notice status">ROI status: starting</div><label for="user">Local test identity</label><input id="user" value="demo-noir" pattern="[A-Za-z0-9_-]+">
<label for="profile">Capture profile</label><select id="profile"><option value="noir-ir" selected>NoIR + IR light</option><option value="rgb">RGB</option></select>
<button id="enroll" disabled onclick="runAction('enroll')">Enroll 5 samples</button><button id="verify" class="secondary" disabled onclick="runAction('verify')">Verify</button>
<button id="debug-capture" class="secondary" disabled onclick="captureDebugSample()">Capture debug sample</button>
<button class="secondary" onclick="resetRoi()">Reset ROI background</button><button class="secondary" onclick="loadUsers()">List users</button><div id="notice" class="notice">Ready.</div>
<p class="small">This is a same-stand 1:1 baseline. It is not liveness detection, anti-spoofing, access control, or a security claim.</p></section></main>
<script>
const notice=document.getElementById('notice');
const stream=document.getElementById('stream');
const roiPreview=document.getElementById('roi');
const roiStatus=document.getElementById('roi-status');
const actionButtons=['enroll','verify','debug-capture'].map(id=>document.getElementById(id));
const debugCapture=actionButtons[2];
function pollImage(img,path,delay){let previous=null;async function tick(){try{const r=await fetch(path+'?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);const next=URL.createObjectURL(await r.blob());const old=previous;previous=next;img.onload=()=>{if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old)};img.src=next}catch(e){}setTimeout(tick,delay)}tick()}
pollImage(stream,'/frame.jpg',80);
pollImage(roiPreview,'/roi.jpg',300);
async function pollStatus(){try{const r=await fetch('/api/status?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);const d=await r.json();const state=d.quality_status||'NO_HAND';const count=d.quality_consecutive_frames||0;const required=d.quality_required_frames||5;const reason=d.quality_reason?(' · '+d.quality_reason):'';const debug=d.debug_capture||{};const next=debug.next_sample||1;roiStatus.textContent=`ROI status: ${state} (${count}/${required})${reason}`;roiStatus.className='notice status '+(state==='READY'?'ready':'blocked');actionButtons[0].disabled=state!=='READY';actionButtons[1].disabled=state!=='READY';debugCapture.disabled=state!=='READY'||Boolean(debug.requires_removal);debugCapture.textContent=debug.requires_removal?'Remove palm before next sample':`Capture debug sample (${Math.min(next,10)}/10)`}catch(e){roiStatus.textContent='ROI status unavailable';roiStatus.className='notice status blocked';actionButtons.forEach(button=>button.disabled=true)}setTimeout(pollStatus,300)}
pollStatus();
async function runAction(action){const user=document.getElementById('user').value.trim();const profile=document.getElementById('profile').value;notice.textContent='Working…';try{const r=await fetch('/api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user,profile})});const d=await r.json();notice.textContent=d.message||JSON.stringify(d,null,2)}catch(e){notice.textContent='Request failed: '+e}}
async function captureDebugSample(){notice.textContent='Capturing the latest detector frame…';try{const r=await fetch('/api/capture-debug-sample',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});const d=await r.json();notice.textContent=d.message||JSON.stringify(d,null,2)}catch(e){notice.textContent='Request failed: '+e}}
async function resetRoi(){notice.textContent='Remove your hand, then reset the empty-view reference…';try{const r=await fetch('/api/reset-roi',{method:'POST'});const d=await r.json();notice.textContent=d.message||JSON.stringify(d,null,2)}catch(e){notice.textContent='Request failed: '+e}}
async function loadUsers(){const r=await fetch('/api/users');const d=await r.json();notice.textContent=d.users.length?'Enrolled users: '+d.users.join(', '):'No enrolled users.'}
</script></body></html>"""


class CameraFeed:
    def __init__(
        self,
        index: int,
        width: int,
        height: int,
        *,
        roi_mode: str,
        hand_model: Path,
        hand_pose_model: Path,
        refine_pose: bool,
        inference_ms: float,
        input_size: tuple[int, int],
        recovery_pass: bool,
        camera_tuning_file: Path | None,
    ) -> None:
        from picamera2 import Picamera2

        if roi_mode not in ("fixed", "dynamic"):
            raise ValueError(f"unsupported ROI mode: {roi_mode}")
        # A NoIR module needs a separate imaging pipeline tuning file under IR
        # illumination. Passing it to Picamera2 is required; an environment
        # variable alone is ignored by the Pi 4 libcamera build.
        self.camera = Picamera2(index, tuning=None if camera_tuning_file is None else str(camera_tuning_file))
        config = self.camera.create_video_configuration(
            main={"size": (width, height), "format": "RGB888"},
            buffer_count=2,
        )
        self.camera.configure(config)
        self.camera.start()
        self.lock = threading.Lock()
        self.frame_condition = threading.Condition(self.lock)
        self.roi_mode = roi_mode
        self.camera_index = index
        self.capture_size = (width, height)
        self.camera_tuning_file = None if camera_tuning_file is None else str(camera_tuning_file)
        self.inference_ms = float(inference_ms)
        self.input_size = tuple(input_size)
        self.hand_model = hand_model
        self.tracker = (
            palm_roi.HandLandmarkTracker(
                hand_model,
                hand_pose_model,
                input_size=input_size,
                smoothing_alpha=1.0,
                refine_pose=refine_pose,
                submit_interval_ms=inference_ms,
                recovery_pass=recovery_pass,
            )
            if roi_mode == "dynamic"
            else None
        )
        self.latest: CapturedFrame | None = None
        self.jpeg: bytes | None = None
        self.roi_jpeg: bytes | None = None
        self.latest_processed: ProcessedFrame | None = None
        self.quality_gate = ROIQualityGate(required_frames=5, min_contrast=12.0, min_sharpness=2.0)
        self.latest_roi_status: dict[str, Any] = {
            "roi_mode": roi_mode,
            "roi_geometry": palm_roi.ROI_GEOMETRY_VERSION if roi_mode == "dynamic" else "fixed-fraction-v1",
            "roi_status": "starting",
            **self.quality_gate.last_result.as_dict(),
        }
        self.running = True
        self._last_preview_time = 0.0
        self._last_processing_time = 0.0
        self._processing_interval_s = max(0.10, inference_ms / 1000.0)
        self._next_frame_id = 0
        self.pending_frame: CapturedFrame | None = None
        self.preview_overlay = LiveROIOverlay() if roi_mode == "dynamic" else None
        self.latest_preview_status: dict[str, Any] = {}
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.capture_thread.start()
        self.processing_thread.start()

    def _capture_loop(self) -> None:
        """Capture continuously so a slow inference pass cannot freeze video."""
        while self.running:
            try:
                # Picamera2 RGB888 arrays have BGR byte order; PIL expects RGB.
                array = self.camera.capture_array("main")
                image = Image.fromarray(np.ascontiguousarray(array[:, :, ::-1]))
                captured_monotonic = time.monotonic()
                with self.frame_condition:
                    self._next_frame_id += 1
                    captured = CapturedFrame(self._next_frame_id, image, captured_monotonic)
                    self.latest = captured
                    self.pending_frame = captured
                    processed = self.latest_processed
                    status = dict(self.latest_roi_status)
                    self.frame_condition.notify_all()
                if self.jpeg is None or captured_monotonic - self._last_preview_time >= 0.10:
                    quad = None
                    if self.preview_overlay is not None:
                        quad, status = self.preview_overlay.update(
                            image, captured.frame_id, captured_monotonic, processed,
                        )
                    jpeg = self._encode_preview(image, quad, status)
                    with self.lock:
                        self.jpeg = jpeg
                        self.latest_preview_status = status
                        self._last_preview_time = captured_monotonic
            except Exception as error:
                with self.lock:
                    self.latest_roi_status = {
                        "roi_mode": self.roi_mode,
                        "roi_geometry": palm_roi.ROI_GEOMETRY_VERSION if self.roi_mode == "dynamic" else "fixed-fraction-v1",
                        "roi_status": "camera_error",
                        "error": str(error),
                    }
                time.sleep(0.2)

    def _processing_loop(self) -> None:
        """Process the newest frame independently of the live camera stream."""
        while self.running:
            with self.frame_condition:
                while self.running and self.pending_frame is None:
                    self.frame_condition.wait(timeout=0.2)
                if not self.running:
                    return
                captured = self.pending_frame
                self.pending_frame = None
            if captured is None:
                continue
            now = time.monotonic()
            if self.tracker is not None and now - self._last_processing_time < self._processing_interval_s:
                # The capture thread keeps the live preview moving.  Do not
                # spend CPU turning every camera frame into the same ROI.
                time.sleep(0.01)
                continue
            self._last_processing_time = now
            try:
                roi_quad: np.ndarray | None = None
                quality: dict[str, float]
                if self.tracker is not None:
                    self.tracker.submit(captured.image, int(captured.captured_monotonic * 1000))
                    tracker_status = self.tracker.roi_status(
                        captured.image.size,
                        frame_timestamp_ms=int(captured.captured_monotonic * 1000),
                    )
                    roi_quad = tracker_status.quad
                    roi_status = tracker_status.as_dict()
                    candidate_quad = roi_quad
                    if candidate_quad is not None and roi_status["roi_status"] == "tracking":
                        roi, quality = palm_demo.crop_and_normalize(captured.image, roi_quad=candidate_quad)
                    else:
                        candidate_quad = None
                        if roi_quad is not None:
                            roi_status["roi_reason"] = "roi_stale_for_frame"
                        roi = np.full((128, 128), 24, dtype=np.uint8)
                        quality = {"contrast": 0.0, "sharpness": 0.0}
                    quality_result = self.quality_gate.update(
                        frame_id=captured.frame_id,
                        captured_monotonic_ms=captured.captured_monotonic * 1000.0,
                        now_monotonic_ms=time.monotonic() * 1000.0,
                        image_size=captured.image.size,
                        roi_quad=candidate_quad,
                        tracker_status=str(roi_status["roi_status"]),
                        quality=quality,
                    )
                    roi_quad = quality_result.roi_quad
                else:
                    roi_status = {
                        "roi_mode": "fixed",
                        "roi_geometry": "fixed-fraction-v1",
                        "roi_status": "fixed",
                    }
                    roi, _ = palm_demo.crop_and_normalize(captured.image)
                    quality = {"contrast": 0.0, "sharpness": 0.0}
                roi_status.update(
                    {
                        "frame_id": captured.frame_id,
                        "captured_monotonic_ms": round(captured.captured_monotonic * 1000.0, 3),
                        "processed_monotonic_ms": round(time.monotonic() * 1000.0, 3),
                        "quality": quality,
                    }
                )
                if self.tracker is None:
                    roi_status.update({"quality_status": "READY", "quality_consecutive_frames": 1, "quality_required_frames": 1})
                else:
                    roi_status.update(quality_result.as_dict())
                roi_image = Image.fromarray(roi, mode="L").resize((384, 384), Image.Resampling.NEAREST).convert("RGB")
                roi_output = io.BytesIO()
                roi_image.save(roi_output, format="JPEG", quality=88)
                with self.lock:
                    self.roi_jpeg = roi_output.getvalue()
                    self.latest_processed = ProcessedFrame(
                        captured,
                        None if roi_quad is None else roi_quad.copy(),
                        roi.copy(),
                        roi_status,
                    )
                    self.latest_roi_status = roi_status
                    self.frame_condition.notify_all()
            except Exception as error:
                with self.lock:
                    self.latest_roi_status = {
                        "roi_mode": self.roi_mode,
                        "roi_geometry": palm_roi.ROI_GEOMETRY_VERSION if self.roi_mode == "dynamic" else "fixed-fraction-v1",
                        "roi_status": "tracker_error",
                        "error": str(error),
                    }
                    self.frame_condition.notify_all()

    @classmethod
    def _encode_preview(
        cls,
        image: Image.Image,
        roi_quad: np.ndarray | None,
        roi_status: dict[str, Any],
    ) -> bytes:
        output = io.BytesIO()
        cls._annotate_roi(image, roi_quad, roi_status).save(output, format="JPEG", quality=82)
        return output.getvalue()

    @staticmethod
    def _annotate_roi(
        image: Image.Image,
        roi_quad: np.ndarray | None,
        roi_status: dict[str, Any],
    ) -> Image.Image:
        """Render fixed or dynamic ROI state into the streamed video frame."""
        from PIL import ImageDraw

        preview = image.copy()
        draw = ImageDraw.Draw(preview)
        width, height = preview.size
        green = (37, 211, 102)
        white = (255, 255, 255)
        status = str(roi_status.get("roi_status", "unknown"))
        if roi_quad is not None:
            points = [tuple(int(round(value)) for value in point) for point in roi_quad]
            draw.polygon(points, outline=green, width=max(2, int(min(width, height) * 0.004)))
            cx = int(round(float(roi_quad[:, 0].mean())))
            cy = int(round(float(roi_quad[:, 1].mean())))
            radius = max(5, int(min(width, height) * 0.012))
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=green, outline=white, width=2)
            label_color = green
        elif status == "fixed":
            x0, y0 = int(width * 0.19), int(height * 0.15)
            x1, y1 = int(width * 0.81), int(height * 0.85)
            label_color = (220, 150, 40) if status == "fixed" else (210, 55, 55)
            draw.rectangle((x0, y0, x1, y1), outline=label_color, width=max(2, int(min(width, height) * 0.004)))
        else:
            label_color = (210, 55, 55)
        top = 8
        reason = str(roi_status.get("roi_reason") or "")
        suffix = f" · {reason[:28]}" if reason else ""
        label = f"PALM ROI · {status}{suffix}"
        draw.rounded_rectangle((8, top, min(width - 8, 410), top + 26), radius=5, fill=label_color)
        draw.text((16, top + 5), label, fill=white)
        return preview
    def roi_frame(self) -> bytes:
        with self.lock:
            if self.roi_jpeg is None:
                raise RuntimeError("Waiting for the first processing ROI")
            return self.roi_jpeg

    def frame(self) -> Image.Image:
        return self.snapshot()[0]

    def snapshot(
        self,
        *,
        after_frame_id: int | None = None,
        timeout_s: float = 3.0,
    ) -> tuple[Image.Image, np.ndarray, np.ndarray | None, dict[str, Any], int]:
        """Return raw image, exact matcher ROI, quad, status, and frame ID."""

        deadline = time.monotonic() + timeout_s
        with self.frame_condition:
            while True:
                if self.roi_mode == "dynamic":
                    processed = self.latest_processed
                    if processed is not None and (after_frame_id is None or processed.captured.frame_id > after_frame_id):
                        quad = None if processed.roi_quad is None else processed.roi_quad.copy()
                        return (
                            processed.captured.image.copy(),
                            processed.roi.copy(),
                            quad,
                            dict(processed.roi_status),
                            processed.captured.frame_id,
                        )
                elif self.latest is not None and (after_frame_id is None or self.latest.frame_id > after_frame_id):
                    status = dict(self.latest_roi_status)
                    status.update({"frame_id": self.latest.frame_id})
                    roi, _quality = palm_demo.crop_and_normalize(self.latest.image)
                    return self.latest.image.copy(), roi, None, status, self.latest.frame_id
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError("Timed out waiting for a fresh processed camera frame")
                self.frame_condition.wait(timeout=remaining)

    def status(self) -> dict[str, Any]:
        with self.lock:
            status = dict(self.latest_roi_status)
            if self.latest is not None:
                status["latest_frame_id"] = self.latest.frame_id
            if self.latest_processed is not None:
                status["processed_frame_id"] = self.latest_processed.captured.frame_id
            status["processing_thread_alive"] = self.processing_thread.is_alive()
            status["preview"] = dict(self.latest_preview_status)
            if self.latest is not None and self.latest_processed is not None:
                status["processing_lag_frames"] = (
                    self.latest.frame_id - self.latest_processed.captured.frame_id
                )
            return status

    def latest_processed_frame_id(self) -> int | None:
        with self.lock:
            return None if self.latest_processed is None else self.latest_processed.captured.frame_id

    def capture_settings(self) -> dict[str, Any]:
        return {
            "camera": self.camera_index,
            "width": self.capture_size[0],
            "height": self.capture_size[1],
            "format": "RGB888",
            "tuning_file": self.camera_tuning_file,
            "roi_mode": self.roi_mode,
            "roi_geometry": palm_roi.ROI_GEOMETRY_VERSION if self.roi_mode == "dynamic" else "fixed-fraction-v1",
            "roi_quality_version": "roi-quality-v1",
            "roi_quality_config": self.quality_gate.config(),
            "detector_input_size": list(self.input_size),
            "inference_ms": self.inference_ms,
        }

    def reset_quality_gate(self) -> None:
        with self.frame_condition:
            result = self.quality_gate.reset("manual_reset")
            self.latest_roi_status.update(result.as_dict())
            self.frame_condition.notify_all()

    def jpeg_frame(self) -> bytes:
        with self.lock:
            if self.jpeg is None:
                raise RuntimeError("Waiting for the first camera frame")
            return self.jpeg

    def processed_debug_frame(self, *, after_frame_id: int | None = None) -> tuple[Image.Image, np.ndarray, np.ndarray | None, int, dict[str, Any]]:
        """Return the raw frame and exact matcher ROI from one processed frame."""

        with self.lock:
            processed = self.latest_processed
            if processed is None or (after_frame_id is not None and processed.captured.frame_id <= after_frame_id):
                raise RuntimeError("Waiting for the first processed camera frame")
            image = processed.captured.image.copy()
            roi = processed.roi.copy()
            quad = None if processed.roi_quad is None else processed.roi_quad.copy()
            frame_id = processed.captured.frame_id
            status = dict(processed.roi_status)
        return image, roi, quad, frame_id, status

    def close(self) -> None:
        self.running = False
        with self.frame_condition:
            self.frame_condition.notify_all()
        self.capture_thread.join(timeout=2)
        self.processing_thread.join(timeout=2)
        if self.tracker is not None:
            self.tracker.close()
        self.camera.stop()
        self.camera.close()

    def reset_roi_background(self) -> None:
        if self.tracker is None:
            raise RuntimeError("ROI background reset is only available in dynamic mode.")
        self.tracker.reset_background()
        self.reset_quality_gate()


class App:
    def __init__(self, camera: CameraFeed) -> None:
        self.camera = camera
        self.algorithm_name = DEBUG_MATCHER
        self.algorithm = load_algorithm(palm_demo.DEFAULT_BASELINE, self.algorithm_name)
        self.lock = threading.Lock()
        self.debug_writer: DebugDatasetWriter | None = None
        self.debug_sample_index = 1
        self.debug_last_frame_id: int | None = None
        self.debug_requires_removal = False

    def feature(
        self,
        image: Image.Image,
        roi_quad: np.ndarray | None,
        roi_status: dict[str, Any],
    ) -> tuple[np.ndarray, dict[str, Any], float]:
        started = time.perf_counter()
        if self.camera.roi_mode == "dynamic":
            if roi_status.get("quality_status") != "READY":
                reason = str(roi_status.get("quality_reason") or roi_status.get("quality_status") or "NO_HAND")
                raise RuntimeError(f"ROI quality is not READY ({reason}); hold one open palm steady and retry.")
            if roi_quad is None:
                reason = str(roi_status.get("roi_reason") or roi_status.get("roi_status") or "no_hand")
                raise RuntimeError(
                    f"Palm ROI is not ready ({reason}); hold one open palm in the camera view."
                )
            roi, quality = palm_demo.crop_and_normalize(image, roi_quad=roi_quad)
        else:
            roi, quality = palm_demo.crop_and_normalize(image)
        if quality["contrast"] < 12.0:
            raise RuntimeError(f"Low contrast ({quality['contrast']:.1f}); improve lighting or hand position.")
        feature = self.algorithm.extract(roi).astype(bool)
        quality.update(roi_status)
        return feature, quality, (time.perf_counter() - started) * 1000

    def capture_debug_sample(self) -> str:
        if getattr(self, "debug_requires_removal", False):
            raise RuntimeError("Remove the palm and wait for NO_HAND before capturing the next sample.")
        image, roi, roi_quad, status, frame_id = self.camera.snapshot(after_frame_id=self.debug_last_frame_id)
        if status.get("quality_status") != "READY" or roi_quad is None:
            reason = str(status.get("quality_reason") or status.get("quality_status") or "NO_HAND")
            raise RuntimeError(f"ROI quality is not READY ({reason}); hold one open palm steady and retry.")
        if self.debug_writer is None or self.debug_sample_index > 10:
            session = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            self.debug_writer = DebugDatasetWriter(
                palm_demo.RUNTIME / "debug_capture" / session,
                camera_settings=self.camera.capture_settings(),
                roi_algorithm_version=str(status.get("roi_geometry", palm_roi.ROI_GEOMETRY_VERSION)),
            )
            self.debug_sample_index = 1
            self.debug_last_frame_id = None
            image, roi, roi_quad, status, frame_id = self.camera.snapshot()
            if status.get("quality_status") != "READY" or roi_quad is None:
                raise RuntimeError("ROI became unavailable while starting a new debug dataset; retry.")
        sample_dir = self.debug_writer.save(
            sample_index=self.debug_sample_index,
            raw_image=image,
            roi_128=roi,
            metadata={
                "captured_at": palm_demo.utc_now(),
                "frame_id": frame_id,
                "captured_monotonic_ms": status.get("captured_monotonic_ms"),
                "processed_monotonic_ms": status.get("processed_monotonic_ms"),
                "roi_quad": roi_quad.tolist(),
                "tracking_status": status.get("quality_status"),
                "tracker_status": status.get("roi_status"),
                "quality": status.get("quality", {}),
                "roi_status": status,
                "source": "debug_ui_processed_frame",
                "image_color_order": "RGB",
                "camera_array_format": "RGB888_BGR_bytes",
            },
        )
        saved_index = self.debug_sample_index
        self.debug_sample_index += 1
        self.debug_last_frame_id = frame_id
        self.camera.reset_quality_gate()
        self.debug_requires_removal = saved_index < 10
        if saved_index == 10:
            return f"Debug dataset complete: {self.debug_writer.root}"
        return f"Debug sample {saved_index}/10 saved: {sample_dir}. Remove and replace the palm, then wait for READY."

    def status(self) -> dict[str, Any]:
        status = self.camera.status()
        if getattr(self, "debug_requires_removal", False) and status.get("quality_status") == "NO_HAND":
            self.debug_requires_removal = False
        writer = getattr(self, "debug_writer", None)
        next_sample = getattr(self, "debug_sample_index", 1)
        status["debug_capture"] = {
            "session": None if writer is None else str(writer.root),
            "next_sample": next_sample,
            "total_samples": 10,
            "requires_removal": bool(getattr(self, "debug_requires_removal", False)),
        }
        return status

    def enroll(self, user: str, profile: str) -> str:
        with self.lock:
            features: list[np.ndarray] = []
            qualities: list[dict[str, float]] = []
            timings: list[float] = []
            frame_ids: list[int] = []
            previous_frame_id = self.camera.latest_processed_frame_id()
            for _ in range(5):
                image, _roi, roi_quad, roi_status, frame_id = self.camera.snapshot(after_frame_id=previous_frame_id)
                feature, quality, timing = self.feature(image, roi_quad, roi_status)
                features.append(feature)
                qualities.append(quality)
                timings.append(timing)
                frame_ids.append(frame_id)
                previous_frame_id = frame_id
            data_path, meta_path = palm_demo.template_paths(user)
            data_path.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(data_path, features=np.stack(features))
            distances = [
                float(self.algorithm.match(features[index], candidate))
                for index, feature in enumerate(features)
                for candidate in features[index + 1:]
            ]
            threshold = float(np.clip(np.quantile(distances, 0.95) + 0.015, DEBUG_MIN_THRESHOLD, DEBUG_MAX_THRESHOLD))
            metadata = {"user": user, "created_at": palm_demo.utc_now(), "algorithm": self.algorithm_name, "camera": 0,
                        "capture_profile": profile, "threshold": threshold, "samples": 5,
                        "roi_mode": self.camera.roi_mode,
                        "roi_geometry": palm_roi.ROI_GEOMETRY_VERSION if self.camera.roi_mode == "dynamic" else "fixed-fraction-v1",
                        "crop": palm_demo.DEFAULT_CROP if self.camera.roi_mode == "fixed" else None,
                        "min_contrast": 12.0, "quality": qualities,
                        "frame_ids": frame_ids,
                        "pipeline_ms": {"mean": float(np.mean(timings)), "max": float(np.max(timings))},
                        "enrollment_distance_p95": float(np.quantile(distances, 0.95)),
                        "warning": "Same-stand debug threshold only; it has no impostor or liveness validation."}
            meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            palm_demo.write_log({"event": "enroll", "user": user, "camera": 0, "capture_profile": profile,
                                 "samples": 5, "pipeline_ms_mean": metadata["pipeline_ms"]["mean"]})
            return f"Enrollment complete: {user} (DoN, threshold {threshold:.4f}, mean pipeline {metadata['pipeline_ms']['mean']:.1f} ms)"

    def verify(self, user: str, profile: str) -> str:
        with self.lock:
            data_path, meta_path = palm_demo.template_paths(user)
            if not data_path.exists() or not meta_path.exists():
                raise RuntimeError(f"No template for {user}; enroll first.")
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            if metadata.get("capture_profile") != profile:
                raise RuntimeError(f"Template profile is {metadata.get('capture_profile')!r}, current profile is {profile!r}.")
            if metadata.get("algorithm") != self.algorithm_name:
                raise RuntimeError(
                    f"Template matcher is {metadata.get('algorithm')!r}, current matcher is {self.algorithm_name!r}; re-enroll this identity."
                )
            stored_roi_mode = metadata.get("roi_mode", "fixed")
            if stored_roi_mode != self.camera.roi_mode:
                raise RuntimeError(
                    f"Template ROI mode is {stored_roi_mode!r}, current mode is {self.camera.roi_mode!r}; re-enroll this identity."
                )
            previous_frame_id = self.camera.latest_processed_frame_id()
            image, _roi, roi_quad, roi_status, frame_id = self.camera.snapshot(after_frame_id=previous_frame_id)
            feature, quality, timing = self.feature(image, roi_quad, roi_status)
            stored = np.load(data_path)["features"]
            scores = [float(self.algorithm.match(feature, candidate)) for candidate in stored]
            score = float(np.median(scores))
            accepted = score <= float(metadata.get("threshold", 0.28))
            palm_demo.write_log({"event": "verify", "user": user, "decision": "ACCEPT" if accepted else "REJECT",
                                  "score": score, "threshold": metadata.get("threshold", 0.28), "camera": 0,
                                  "capture_profile": profile, "quality": quality, "frame_id": frame_id, "pipeline_ms": timing})
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
            route = urlsplit(self.path).path
            if route == "/":
                body = HTML.encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route == "/roi":
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
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
            elif route == "/frame.jpg":
                frame = app.camera.jpeg_frame()
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(frame)))
                self.end_headers()
                self.wfile.write(frame)
            elif route == "/debug/processed.jpg":
                image, _roi, _quad, frame_id, status = app.camera.processed_debug_frame()
                output = io.BytesIO()
                image.save(output, format="JPEG", quality=95)
                frame = output.getvalue()
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(frame)))
                self.send_header("X-Frame-Id", str(frame_id))
                self.send_header("X-ROI-Status", str(status.get("roi_status", "unknown")))
                self.send_header("X-ROI-Reason", str(status.get("roi_reason") or ""))
                self.end_headers()
                self.wfile.write(frame)
            elif route == "/roi.jpg":
                frame = app.camera.roi_frame()
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(frame)))
                self.end_headers()
                self.wfile.write(frame)
            elif route == "/stream":
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
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
            elif route == "/api/status":
                json_response(self, HTTPStatus.OK, app.status())
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/api/reset-roi":
                try:
                    app.camera.reset_roi_background()
                    json_response(self, HTTPStatus.OK, {"message": "Background reset. Keep the view empty for two seconds, then show your palm."})
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/capture-debug-sample":
                try:
                    self.rfile.read(int(self.headers.get("Content-Length", "0")))
                    json_response(self, HTTPStatus.OK, {"message": app.capture_debug_sample()})
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path not in ("/api/enroll", "/api/verify"):
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})
                return
            try:
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
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
    parser.add_argument("--width", type=int, default=480)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--roi-mode", choices=("dynamic", "fixed"), default="dynamic")
    parser.add_argument("--hand-model", type=Path, default=DEFAULT_HAND_MODEL)
    parser.add_argument("--hand-pose-model", type=Path, default=DEFAULT_HAND_POSE_MODEL)
    parser.add_argument("--refine-pose", action="store_true", help="Enable the slower 21-point pose refinement pass.")
    parser.add_argument("--inference-ms", type=float, default=800.0, help="Minimum interval between detector passes.")
    parser.add_argument("--input-width", type=int, default=320, help="Small live image width used by the detector.")
    parser.add_argument("--input-height", type=int, default=240, help="Small live image height used by the detector.")
    parser.add_argument("--recovery-pass", action="store_true", help="Run a second detector pass when no hand is found; slower.")
    parser.add_argument("--camera-tuning-file", type=Path, help="Optional libcamera tuning JSON, e.g. imx219_noir.json for NoIR + IR.")
    args = parser.parse_args()
    feed = CameraFeed(
        args.camera,
        args.width,
        args.height,
        roi_mode=args.roi_mode,
        hand_model=args.hand_model,
        hand_pose_model=args.hand_pose_model,
        refine_pose=args.refine_pose,
        inference_ms=args.inference_ms,
        input_size=(args.input_width, args.input_height),
        recovery_pass=args.recovery_pass,
        camera_tuning_file=args.camera_tuning_file,
    )
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







