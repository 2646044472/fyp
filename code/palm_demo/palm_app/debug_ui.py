#!/usr/bin/env python3
"""Small browser UI for the local palm verification smoke test.

The UI keeps frames in memory, serves a camera preview, and uses the configured
ROI and matcher for explicit local enrollment and verification. Full-resolution
collection and the supervised demo share the same PKLNet extraction path.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import shutil
import threading
import time
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import cv2
import numpy as np
from PIL import Image

from palm_app import common as palm_demo
common = palm_demo
import palm_roi
from biometric import load_algorithm
from collection_page import HTML as COLLECTION_HTML
from capture_page import HTML as CAPTURE_HTML
from demo_flow import DemoFlow
from demo_page import HTML as DEMO_HTML
from live_roi import LiveROIOverlay
from roi_quality import DebugDatasetWriter, ROIQualityGate
from pklnet_tracker import PKLNetTracker
from pklnet_roi import ROI_GEOMETRY_VERSION as PKLNET_GEOMETRY_VERSION, normalize_roi


def _roi_geometry(mode: str) -> str:
    if mode == "capture":
        return "none"
    return PKLNET_GEOMETRY_VERSION if mode == "pklnet" else palm_roi.ROI_GEOMETRY_VERSION if mode == "dynamic" else "fixed-fraction-v1"


DEFAULT_HAND_MODEL = palm_demo.ROOT / "models" / "palm_detection_mediapipe_2023feb.onnx"
DEFAULT_HAND_POSE_MODEL = palm_demo.ROOT / "models" / "handpose_estimation_mediapipe_2023feb.onnx"
DEBUG_MATCHER = "DoN"
DEMO_MATCHER = "DoN"
DEBUG_MIN_THRESHOLD = 0.15
DEBUG_MAX_THRESHOLD = 0.20
REPEATABILITY_TOTAL = 10
HIGHRES_BATCH_TOTAL = 10
CAMERA_FRAME_MAX_AGE_S = 5.0


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
.collect-link{display:block;padding:14px;border-radius:9px;background:#e7f3ff;color:#125e9c;text-decoration:none;font-weight:700;line-height:1.45}.collect-link:hover,.collect-link:focus-visible{background:#d7eaff;text-decoration:underline}.collect-link small{display:block;font-weight:400;color:#415b70;margin-top:3px}
main{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);gap:18px}section{background:white;border:1px solid #dce3ea;border-radius:12px;padding:16px;box-shadow:0 2px 8px #0000000d}
preview{position:relative;width:100%;aspect-ratio:16/9;background:#111;border-radius:8px;overflow:hidden}.preview img{display:block;width:100%;height:100%;object-fit:contain}.roi-guide{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.roi-guide .roi-box{fill:#25d36612;stroke:#25d366;stroke-width:.55;stroke-dasharray:2 1}.roi-guide .roi-point{fill:#25d366;stroke:#fff;stroke-width:.35}.roi-guide .roi-cross{stroke:#fff;stroke-width:.35;opacity:.9}.roi-label{position:absolute;left:19%;top:12%;color:#fff;background:#25d366d9;padding:3px 7px;border-radius:4px;font-size:.76rem;font-weight:700;letter-spacing:.02em;pointer-events:none}.roi-panel{margin-top:12px;padding:10px;border:1px solid #dce3ea;border-radius:8px;background:#f8fafb}.roi-preview{display:block;width:220px;height:220px;margin-top:6px;image-rendering:pixelated;background:#111;border-radius:6px}label{display:block;margin:10px 0 6px;font-weight:600}input,select,button{font:inherit;padding:9px;border:1px solid #b8c2cc;border-radius:7px}input,select{width:100%;box-sizing:border-box}button{cursor:pointer;margin:8px 4px 0 0;background:#1769aa;color:white;border:0}button.secondary{background:#5d6d7e}button:disabled{opacity:.5;cursor:wait}.notice{white-space:pre-wrap;background:#eef3f7;padding:10px;border-radius:7px;min-height:42px;margin-top:14px}.small{font-size:.88rem;color:#53616d}.status{font-weight:700}.ready{background:#e4f7ea;color:#126b2d}.blocked{background:#fff0ef;color:#9b241c}h1{margin-top:0} @media(max-width:760px){main{grid-template-columns:1fr}}
</style></head><body><h1>Palm Reg · Pi debug</h1>
<main><section><div class="preview"><img id="stream" src="/frame.jpg" alt="camera preview"></div><p class="small">The green quadrilateral follows the tracked palm. Keep one hand visible and wait for the tracking status before enrolling or verifying.</p><div class="roi-panel"><div class="small"><strong>Processing ROI (128×128 normalized)</strong></div><img id="roi" class="roi-preview" src="/roi.jpg" alt="normalized palm processing ROI"></div></section>
<section><a class="collect-link" href="/demo">打开基础支付演示 /demo<small>高清录入、掌纹识别、人工确认与模拟扣款</small></a><a class="collect-link" href="/collect">打开专门采集页 /collect<small>每组 10 张高清原图（3280×2464），拍后检查 128×128 掌心裁图与 512×512 原始细节</small></a><div id="roi-status" class="notice status">ROI status: starting</div><label for="user">Local test identity</label><input id="user" value="demo-noir" pattern="[A-Za-z0-9_-]+">
<label for="profile">Capture profile</label><select id="profile"><option value="noir-ir" selected>NoIR + IR light</option><option value="rgb">RGB</option></select>
<button id="enroll" disabled onclick="runAction('enroll')">Enroll 5 samples</button><button id="verify" class="secondary" disabled onclick="runAction('verify')">Verify</button>
<button id="debug-capture" class="secondary" disabled onclick="captureDebugSample()">Capture debug sample</button>
<button class="secondary" onclick="resetRoi()">Reset ROI background</button><button class="secondary" onclick="loadUsers()">List users</button><div id="notice" class="notice">Ready.</div>
<hr><h2>Quick 10-image repeatability test</h2><p class="small">Remove your hand, confirm the empty view, place the same hand, then save one READY frame. Repeat ten times.</p>
<label for="repeat-session">Session name</label><input id="repeat-session" value="test01" pattern="[A-Za-z0-9_-]+">
<button id="repeat-start" onclick="startRepeatability()">Start 10-image test</button><button id="repeat-empty" class="secondary" disabled onclick="confirmRepeatabilityEmpty()">Confirm hand removed</button><button id="repeat-capture" disabled onclick="captureRepeatability()">Save image</button>
<a id="repeat-download" href="/api/download-repeatability" hidden><button type="button">Download ZIP to Windows</button></a>
<div id="repeat-status" class="notice">Repeatability: not started.</div>
<p class="small">This is a same-stand 1:1 baseline. It is not liveness detection, anti-spoofing, access control, or a security claim.</p></section></main>
<script>
const notice=document.getElementById('notice');
const stream=document.getElementById('stream');
const roiPreview=document.getElementById('roi');
const roiStatus=document.getElementById('roi-status');
const actionButtons=['enroll','verify','debug-capture'].map(id=>document.getElementById(id));
const debugCapture=actionButtons[2];
const repeatStart=document.getElementById('repeat-start');
const repeatEmpty=document.getElementById('repeat-empty');
const repeatCapture=document.getElementById('repeat-capture');
const repeatDownload=document.getElementById('repeat-download');
const repeatStatus=document.getElementById('repeat-status');
function pollImage(img,path,delay){let previous=null;async function tick(){try{const r=await fetch(path+'?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);const next=URL.createObjectURL(await r.blob());const old=previous;previous=next;img.onload=()=>{if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old)};img.src=next}catch(e){}setTimeout(tick,delay)}tick()}
pollImage(stream,'/frame.jpg',80);
pollImage(roiPreview,'/roi.jpg',300);
async function pollStatus(){try{const r=await fetch('/api/status?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);const d=await r.json();const state=d.quality_status||'NO_HAND';const count=d.quality_consecutive_frames||0;const required=d.quality_required_frames||5;const reason=d.quality_reason?(' · '+d.quality_reason):'';const debug=d.debug_capture||{};const next=debug.next_sample||1;roiStatus.textContent=`ROI status: ${state} (${count}/${required})${reason}`;roiStatus.className='notice status '+(state==='READY'?'ready':'blocked');actionButtons[0].disabled=state!=='READY';actionButtons[1].disabled=state!=='READY';debugCapture.disabled=state!=='READY'||Boolean(debug.requires_removal);debugCapture.textContent=debug.requires_removal?'Remove palm before next sample':`Capture debug sample (${Math.min(next,10)}/10)`;const repeat=d.repeatability||{};const phase=repeat.phase||'idle';const placement=repeat.next_placement||1;const total=repeat.total_placements||10;const repeatReason=phase==='await_empty'?'Remove your hand, then confirm the empty view.':phase==='await_hand'?'Place the same hand and wait for READY, then save the image.':phase==='complete'?'Collection complete. Download the ZIP to this Windows PC.':'Start a new test session.';repeatStatus.textContent=repeat.active?`Repeatability ${placement>total?total:placement}/${total} · ${phase} · ${repeatReason}`:`Repeatability: ${repeatReason}`;repeatStatus.className='notice '+(phase==='complete'?'ready':'');repeatStart.disabled=repeat.active;repeatEmpty.disabled=!repeat.can_confirm_empty;repeatCapture.disabled=!repeat.can_capture;repeatDownload.hidden=phase!=='complete'}catch(e){roiStatus.textContent='ROI status unavailable';roiStatus.className='notice status blocked';actionButtons.forEach(button=>button.disabled=true);repeatEmpty.disabled=true;repeatCapture.disabled=true}setTimeout(pollStatus,300)}
pollStatus();
async function runAction(action){const user=document.getElementById('user').value.trim();const profile=document.getElementById('profile').value;notice.textContent='Working…';try{const r=await fetch('/api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user,profile})});const d=await r.json();notice.textContent=d.message||JSON.stringify(d,null,2)}catch(e){notice.textContent='Request failed: '+e}}
async function captureDebugSample(){notice.textContent='Capturing the latest detector frame…';try{const r=await fetch('/api/capture-debug-sample',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});const d=await r.json();notice.textContent=d.message||JSON.stringify(d,null,2)}catch(e){notice.textContent='Request failed: '+e}}
async function startRepeatability(){const session=document.getElementById('repeat-session').value.trim();repeatStatus.textContent='Starting…';try{const r=await fetch('/api/start-repeatability',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session,placements:10})});const d=await r.json();repeatStatus.textContent=d.message||JSON.stringify(d,null,2)}catch(e){repeatStatus.textContent='Request failed: '+e}}
async function confirmRepeatabilityEmpty(){repeatStatus.textContent='Checking that the view is empty…';try{const r=await fetch('/api/confirm-repeatability-empty',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});const d=await r.json();repeatStatus.textContent=d.message||JSON.stringify(d,null,2)}catch(e){repeatStatus.textContent='Request failed: '+e}}
async function captureRepeatability(){repeatStatus.textContent='Saving the latest READY placement…';try{const r=await fetch('/api/capture-repeatability',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});const d=await r.json();repeatStatus.textContent=d.message||JSON.stringify(d,null,2)}catch(e){repeatStatus.textContent='Request failed: '+e}}
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
        capture_only: bool = False,
        pklnet_threads: int | None = None,
    ) -> None:
        from picamera2 import Picamera2

        if capture_only:
            roi_mode = "capture"
        if roi_mode not in ("fixed", "dynamic", "pklnet", "capture"):
            raise ValueError(f"unsupported ROI mode: {roi_mode}")
        # A NoIR module needs a separate imaging pipeline tuning file under IR
        # illumination. Passing it to Picamera2 is required; an environment
        # variable alone is ignored by the Pi 4 libcamera build.
        self.camera = Picamera2(index, tuning=None if camera_tuning_file is None else str(camera_tuning_file))
        self.still_size = tuple(self.camera.camera_properties.get("PixelArraySize", (3280, 2464)))
        # A 480x360 stream otherwise selects IMX219's narrow 640x480 crop.
        self.preview_sensor_size = (1640, 1232) if self.still_size == (3280, 2464) else None
        config = self.camera.create_video_configuration(
            main={"size": (width, height), "format": "RGB888"},
            buffer_count=2,
            sensor={"output_size": self.preview_sensor_size, "bit_depth": 10} if self.preview_sensor_size else {},
        )
        self.still_config = self.camera.create_still_configuration(
            main={"size": self.still_size, "format": "RGB888"},
            buffer_count=2,
        )
        self.camera.configure(config)
        self.camera.start()
        self.camera_io_lock = threading.Lock()
        self.lock = threading.Lock()
        self.frame_condition = threading.Condition(self.lock)
        self.roi_mode = roi_mode
        self.capture_only = capture_only
        self.camera_index = index
        self.capture_size = (width, height)
        self.camera_tuning_file = None if camera_tuning_file is None else str(camera_tuning_file)
        self.inference_ms = float(inference_ms)
        self.input_size = tuple(input_size)
        self.hand_model = hand_model
        self.tracker = (
            (PKLNetTracker if roi_mode == "pklnet" else palm_roi.HandLandmarkTracker)(
                hand_model,
                hand_pose_model,
                input_size=input_size,
                smoothing_alpha=1.0,
                refine_pose=refine_pose,
                submit_interval_ms=inference_ms,
                recovery_pass=recovery_pass,
                **({"pklnet_threads": pklnet_threads} if roi_mode == "pklnet" else {}),
            )
            if roi_mode in ("dynamic", "pklnet")
            else None
        )
        self.latest: CapturedFrame | None = None
        self.jpeg: bytes | None = None
        self.roi_jpeg: bytes | None = None
        self.latest_processed: ProcessedFrame | None = None
        # User-selected diagnostic policy: record contrast/sharpness without
        # excluding camera samples. Geometry/freshness are still checked.
        self.quality_gate = ROIQualityGate(required_frames=5, min_contrast=0.0, min_sharpness=0.0, max_age_ms=8000.0 if roi_mode == "pklnet" else 1200.0)
        self.latest_roi_status: dict[str, Any] = {
            "roi_mode": roi_mode,
            "roi_geometry": _roi_geometry(roi_mode),
            "roi_status": "starting",
            **self.quality_gate.last_result.as_dict(),
        }
        self.running = True
        self._last_preview_time = 0.0
        self._last_processing_time = 0.0
        self._processing_interval_s = max(0.10, inference_ms / 1000.0)
        self._next_frame_id = 0
        self.pending_frame: CapturedFrame | None = None
        self.preview_overlay = LiveROIOverlay(max_age_s=8.0 if roi_mode == "pklnet" else 1.5) if roi_mode in ("dynamic", "pklnet") else None
        self.latest_preview_status: dict[str, Any] = {}
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.processing_thread = None if capture_only else threading.Thread(target=self._processing_loop, daemon=True)
        self.capture_thread.start()
        if self.processing_thread is not None:
            self.processing_thread.start()

    def _capture_loop(self) -> None:
        """Capture continuously so a slow inference pass cannot freeze video."""
        while self.running:
            try:
                # Picamera2 RGB888 arrays have BGR byte order; PIL expects RGB.
                with self.camera_io_lock:
                    array = self.camera.capture_array("main")
                image = Image.fromarray(np.ascontiguousarray(array[:, :, ::-1]))
                captured_monotonic = time.monotonic()
                with self.frame_condition:
                    self._next_frame_id += 1
                    captured = CapturedFrame(self._next_frame_id, image, captured_monotonic)
                    self.latest = captured
                    if self.capture_only:
                        self.latest_roi_status.pop("error", None)
                    if not self.capture_only:
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
                        "roi_geometry": _roi_geometry(self.roi_mode),
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
                        if self.roi_mode == "pklnet":
                            roi, quality = self.tracker.processing_roi()
                        else:
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
                        "roi_geometry": _roi_geometry(self.roi_mode),
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
        preview = image if roi_status.get("roi_mode") == "capture" else cls._annotate_roi(image, roi_quad, roi_status)
        preview.save(output, format="JPEG", quality=82)
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

        if self.roi_mode == "pklnet":
            timeout_s = max(timeout_s, 12.0)
        deadline = time.monotonic() + timeout_s
        with self.frame_condition:
            while True:
                if self.roi_mode in ("dynamic", "pklnet"):
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
            camera_state = self._camera_frame_state()
            if self.capture_only:
                return {"mode": "capture_only", "roi_mode": "capture", "roi_processing": False,
                        **camera_state, "capture_size": list(self.still_size),
                        "latest_frame_id": None if self.latest is None else self.latest.frame_id,
                        "processing_thread_alive": False}
            status = dict(self.latest_roi_status)
            status.update(camera_state)
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

    def _camera_frame_state(self) -> dict[str, Any]:
        """Call while holding self.lock; cached JPEGs do not prove a live camera."""
        age = None if self.latest is None else max(0.0, time.monotonic() - self.latest.captured_monotonic)
        error = self.latest_roi_status.get("error")
        if age is not None and age > CAMERA_FRAME_MAX_AGE_S:
            error = error or "Camera frames stopped; check the camera connection and restart the camera service."
        return {"camera_ready": self.jpeg is not None and age is not None and age <= CAMERA_FRAME_MAX_AGE_S and not error,
                "latest_frame_age_ms": None if age is None else round(age * 1000, 1), "error": error}

    def latest_processed_frame_id(self) -> int | None:
        with self.lock:
            return None if self.latest_processed is None else self.latest_processed.captured.frame_id

    def capture_settings(self) -> dict[str, Any]:
        return {
            "camera": self.camera_index,
            "width": self.capture_size[0],
            "height": self.capture_size[1],
            "preview_sensor_output_size": list(self.preview_sensor_size) if self.preview_sensor_size else None,
            "format": "RGB888",
            "tuning_file": self.camera_tuning_file,
            "roi_mode": self.roi_mode,
            "roi_geometry": _roi_geometry(self.roi_mode),
            "roi_processing": not self.capture_only,
            "roi_quality_version": "roi-quality-v1",
            "roi_quality_config": self.quality_gate.config(),
            "detector_input_size": list(self.input_size),
            "inference_ms": self.inference_ms,
        }

    def capture_highres(self) -> tuple[Image.Image, Image.Image, dict[str, Any]]:
        """Pair a preview frame with a full-sensor still, then resume preview."""
        # A disconnected UVC device can leave capture_array waiting while holding
        # camera_io_lock. Reject an already-stale feed before joining that wait.
        with self.lock:
            state = self._camera_frame_state()
            if not state["camera_ready"]:
                raise RuntimeError(state["error"] or "Waiting for a fresh camera frame")
        with self.camera_io_lock:
            preview_array = self.camera.capture_array("main")
            # Switching a UVC camera to full resolution can restart exposure
            # and autofocus. Give it 15 frames to settle before taking a still.
            request = self.camera.switch_mode_and_capture_request(self.still_config, delay=15)
            try:
                full_array = request.make_array("main")
                metadata = request.get_metadata()
            finally:
                request.release()
        preview = Image.fromarray(np.ascontiguousarray(preview_array[:, :, ::-1]))
        full = Image.fromarray(np.ascontiguousarray(full_array[:, :, ::-1]))
        return preview, full, metadata

    def reset_quality_gate(self) -> None:
        with self.frame_condition:
            result = self.quality_gate.reset("manual_reset")
            self.latest_roi_status.update(result.as_dict())
            self.frame_condition.notify_all()

    def jpeg_frame(self) -> bytes:
        with self.lock:
            state = self._camera_frame_state()
            if not state["camera_ready"]:
                raise RuntimeError(state["error"] or "Waiting for the first camera frame")
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
        if self.processing_thread is not None:
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
    def __init__(self, camera: CameraFeed, *, demo_matcher: str = DEMO_MATCHER) -> None:
        self.camera = camera
        self.algorithm_name = DEBUG_MATCHER
        self.capture_only = getattr(camera, "capture_only", False)
        self.algorithm = None if self.capture_only else load_algorithm(palm_demo.DEFAULT_BASELINE, self.algorithm_name)
        self.demo_algorithm = None if self.capture_only else load_algorithm(palm_demo.DEFAULT_BASELINE, demo_matcher)
        self.lock = threading.Lock()
        self.debug_writer: DebugDatasetWriter | None = None
        self.debug_sample_index = 1
        self.debug_last_frame_id: int | None = None
        self.debug_requires_removal = False
        self.repeatability_root: Path | None = None
        self.repeatability_next = 1
        self.repeatability_total = REPEATABILITY_TOTAL
        self.repeatability_phase = "idle"
        self.repeatability_last_frame_id: int | None = None
        self.collection_lock = threading.Lock()
        self.collection_batch_lock = threading.Lock()
        self.collection_batch: dict[str, Any] | None = self._restore_highres_batch()
        if (self.capture_only and self.collection_batch is not None
                and self.collection_batch["phase"] == "complete"
                and self.collection_batch.get("collection_mode") != "full_resolution_only"):
            self.collection_batch = None
        self.demo = None if self.capture_only else DemoFlow(palm_demo.RUNTIME, self.demo_algorithm, self.capture_demo_feature, roi_geometry=_roi_geometry(self.camera.roi_mode))
        if self.demo is not None and hasattr(self.demo_algorithm,"extract_gallery_with_context"):
            self.demo.capture_enrollment_feature = lambda: self.capture_demo_feature(enrollment=True)
        if self.demo is not None and hasattr(self.demo_algorithm, 'prepare_gallery'):
            self.demo.gallery.warm_up()

    def detect_full_still(self, full: Image.Image, preview_size: tuple[int, int], *, demo_core: bool = False, localization_details: dict[str, Any] | None = None) -> tuple[np.ndarray, np.ndarray, float | None, dict[str, float], str]:
        if self.camera.roi_mode == "pklnet":
            raw_roi, quad, details = self.camera.tracker.extractor.extract(full)
            if localization_details is not None:
                localization_details.update(details)
            if not details["roi_geometry_valid"]:
                raise palm_roi.PalmROIError(details["roi_geometry_reason"])
            roi, quality = normalize_roi(raw_roi)
            return roi, quad, None, quality, "pklnet"
        resized = full.resize(preview_size, Image.Resampling.LANCZOS)
        tracker = palm_roi.HandLandmarkTracker(
            DEFAULT_HAND_MODEL, DEFAULT_HAND_POSE_MODEL if demo_core else None,
            input_size=self.camera.input_size, smoothing_alpha=1.0,
            recovery_pass=True, refine_pose=demo_core,
        )
        try:
            timestamp = int(time.monotonic() * 1000)
            tracker.submit(resized, timestamp)
            detection = tracker.roi_status(resized.size, frame_timestamp_ms=timestamp)
            if detection.quad is None:
                raise palm_roi.PalmROIError(detection.reason or detection.status)
            quad = detection.quad
            if demo_core:
                if tracker._landmarks is None:
                    raise palm_roi.PalmROIError("Palm landmarks unavailable")
                quad = palm_roi.landmarks_to_palm_quad(
                    tracker._landmarks, resized.size,
                    width_scale=1.3, height_scale=1.3,
                    min_span_px=32, fit_to_frame=True,
                )
            full_quad = quad * np.array(
                [full.width / resized.width, full.height / resized.height], dtype=np.float32
            )
            roi, quality = palm_demo.crop_and_normalize(full, roi_quad=full_quad)
            return roi, full_quad, detection.hand_score, quality, str(detection.diagnostics.get("tracking_source", "unknown"))
        finally:
            tracker.close()

    def capture_demo_feature(self, *, enrollment: bool = False) -> tuple[np.ndarray, str, str]:
        if not self.collection_lock.acquire(blocking=False):
            raise RuntimeError("相机正在拍摄，请稍后重试。")
        try:
            preview, full, _ = self.camera.capture_highres()
            try:
                localization = {}
                if hasattr(self.demo_algorithm, "extract_with_hypotheses"):
                    roi, quad, _, quality, source = self.detect_full_still(full, preview.size, demo_core=True, localization_details=localization)
                else:
                    roi, quad, _, quality, source = self.detect_full_still(full, preview.size, demo_core=True)
            except palm_roi.PalmROIError as error:
                if str(error).startswith(("pklnet_", "roi_out_of_bounds")):
                    raise RuntimeError("掌心定位不稳定，请展开手掌，调整距离和角度后重拍。") from error
                raise
            if not enrollment and hasattr(self.demo_algorithm, 'extract_probe_with_context'):
                if self.camera.roi_mode != 'pklnet':
                    raise RuntimeError('Indexed demo matching requires PKLNet geometry')
                feature = self.demo_algorithm.extract_probe_with_context(full, quad, roi)
                if getattr(self.demo_algorithm, 'requires_exhaustive_fallback', False):
                    candidates = localization.get('pklnet_roi_candidates')
                    if not candidates:
                        raise RuntimeError('Exhaustive fallback requires original localization diagnostics')
                    def exhaustive():
                        hypotheses = self.demo_algorithm.complete_hypotheses(full, candidates, self.camera.tracker.extractor)
                        return self.demo_algorithm.extract_with_hypotheses(full, quad, roi, hypotheses)
                    feature.exhaustive = exhaustive
            elif hasattr(self.demo_algorithm, "extract_with_hypotheses"):
                if self.camera.roi_mode != "pklnet":
                    raise RuntimeError("Multi-ROI matching requires the PKLNet palm coordinate convention")
                candidates = localization.get("pklnet_roi_candidates")
                if not candidates:
                    raise RuntimeError("Multi-ROI matching requires original/gamma localization diagnostics")
                if (enrollment and hasattr(self.demo_algorithm,"extract_gallery_with_context")
                        and not getattr(self.demo_algorithm, 'enrollment_requires_hypotheses', False)):
                    feature = self.demo_algorithm.extract_gallery_with_context(full,quad,roi)
                else:
                    if hasattr(self.demo_algorithm, "complete_hypotheses"):
                        candidates = self.demo_algorithm.complete_hypotheses(full, candidates, self.camera.tracker.extractor)
                    feature = self.demo_algorithm.extract_with_hypotheses(full, quad, roi, candidates)
            elif hasattr(self.demo_algorithm, "extract_with_context"):
                if self.camera.roi_mode != "pklnet":
                    raise RuntimeError("Pose matching requires the PKLNet palm coordinate convention")
                feature = self.demo_algorithm.extract_with_context(full, quad, roi)
            else:
                feature = self.demo_algorithm.extract(roi)
            output = io.BytesIO()
            Image.fromarray(roi).save(output, format="PNG")
            return feature, base64.b64encode(output.getvalue()).decode("ascii"), source
        finally:
            self.collection_lock.release()

    @staticmethod
    def _highres_labels(payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object.")
        subject = str(payload.get("subject", "")).strip()
        hand = str(payload.get("hand", ""))
        background = str(payload.get("background", ""))
        if re.fullmatch(r"[A-Za-z0-9_-]{1,40}", subject) is None:
            raise ValueError("Subject ID must be 1-40 letters, digits, '_' or '-'.")
        if hand not in ("left", "right") or background not in ("existing", "white", "other"):
            raise ValueError("Choose a hand and background.")
        distance_value = payload.get("distance_cm", "")
        distance_text = "" if distance_value is None else str(distance_value).strip()
        distance = None if not distance_text else float(distance_text)
        if distance is not None and not 5 <= distance <= 100:
            raise ValueError("Distance must be between 5 and 100 cm.")
        notes = str(payload.get("notes", ""))
        if len(notes) > 200:
            raise ValueError("Notes are too long.")
        return {"subject": subject, "hand": hand, "background": background, "distance_cm": distance, "notes": notes}

    def capture_highres(self, payload: dict[str, Any], *, preview_quad: np.ndarray | None = None) -> dict[str, Any]:
        labels = self._highres_labels(payload)
        session_id = str(payload.get("session_id", ""))
        if not session_id:
            with self.collection_batch_lock:
                if self.collection_batch is not None and self.collection_batch["phase"] in ("await_hand", "await_empty"):
                    raise RuntimeError("A ten-image session is active. Reload /collect and use its batch capture button.")
        sample_index = payload.get("sample_index")
        if session_id and re.fullmatch(r"\d{8}T\d{12}Z-[0-9a-f]{8}", session_id) is None:
            raise ValueError("Invalid session ID.")
        if sample_index is not None and (not isinstance(sample_index, int) or not 1 <= sample_index <= HIGHRES_BATCH_TOTAL):
            raise ValueError("Invalid sample index.")
        if not self.collection_lock.acquire(blocking=False):
            raise RuntimeError("A high-resolution capture is already in progress.")
        try:
            preview, full, camera_metadata = self.camera.capture_highres()
            sample_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}-{uuid.uuid4().hex[:8]}"
            root = palm_demo.RUNTIME / "highres_capture" / sample_id
            root.mkdir(parents=True, exist_ok=False)
            if not getattr(self, "capture_only", False):
                preview.save(root / "preview.jpg", format="JPEG", quality=95, subsampling=0)
            full.save(root / "full.jpg", format="JPEG", quality=95, subsampling=0)
            roi_available = False
            roi_quality: dict[str, float] | None = None
            roi_error: str | None = None
            full_quad: np.ndarray | None = None
            roi_detection_score: float | None = None
            if not getattr(self, "capture_only", False):
                try:
                    roi, full_quad, roi_detection_score, roi_quality, _ = self.detect_full_still(full, preview.size)
                    Image.fromarray(roi).save(root / "roi_128.png")
                    center_x, center_y = full_quad.mean(axis=0)
                    x = max(0, min(full.width - 512, round(float(center_x)) - 256))
                    y = max(0, min(full.height - 512, round(float(center_y)) - 256))
                    full.crop((x, y, x + 512, y + 512)).save(
                        root / "palm_detail_512.jpg", format="JPEG", quality=95, subsampling=0
                    )
                    roi_available = True
                except Exception as error:
                    roi_error = str(error)
            record = {
                "sample_id": sample_id,
                "captured_at_pi_utc": datetime.now(timezone.utc).isoformat(),
                "client_time_utc": str(payload.get("client_time", ""))[:50],
                **labels,
                "session_id": session_id or None,
                "sample_index": sample_index,
                "roi_available": roi_available,
                "roi_processing": "deferred" if getattr(self, "capture_only", False) else "at_capture",
                "roi_source": ("pklnet" if self.camera.roi_mode == "pklnet" else "full_still_redetection") if roi_available else None,
                "roi_geometry": _roi_geometry(self.camera.roi_mode),
                "roi_quad_preview": preview_quad.tolist() if preview_quad is not None else None,
                "roi_quad_full": full_quad.tolist() if full_quad is not None else None,
                "roi_detection_score": roi_detection_score,
                "roi_quality": roi_quality,
                "roi_error": roi_error,
                "width": full.width,
                "height": full.height,
                "preview_width": preview.width,
                "preview_height": preview.height,
                "camera_settings": self.camera.capture_settings(),
                "camera_metadata": camera_metadata,
                "exposure_ms": (float(camera_metadata["ExposureTime"]) / 1000.0) if "ExposureTime" in camera_metadata else None,
                "analogue_gain": float(camera_metadata["AnalogueGain"]) if "AnalogueGain" in camera_metadata else None,
                "image_color_order": "RGB",
                "camera_array_format": "RGB888_BGR_bytes",
            }
            (root / "metadata.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
            )
            return {key: record[key] for key in ("sample_id", "subject", "hand", "background", "width", "height", "exposure_ms", "analogue_gain", "roi_available")}
        finally:
            self.collection_lock.release()

    def latest_highres(self) -> dict[str, Any]:
        root = palm_demo.RUNTIME / "highres_capture"
        if not root.exists():
            return {}
        samples = [path for path in root.iterdir() if path.is_dir() and (path / "metadata.json").is_file()]
        if not samples:
            return {}
        record = json.loads(max(samples, key=lambda path: path.stat().st_mtime_ns).joinpath("metadata.json").read_text(encoding="utf-8"))
        return {key: record.get(key) for key in ("sample_id", "subject", "hand", "background", "width", "height", "exposure_ms", "analogue_gain", "roi_available")}

    def list_highres_sessions(self) -> list[dict[str, Any]]:
        """List saved collection folders for the local collection manager."""

        root = palm_demo.RUNTIME / "highres_sessions"
        if not root.exists():
            return []
        sessions: list[dict[str, Any]] = []
        for manifest_path in sorted(root.glob("*/manifest.json"), key=lambda path: path.stat().st_mtime_ns, reverse=True):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                session_id = str(manifest["session_id"])
                self._highres_session_root(session_id)
                sample_ids = [str(sample_id) for sample_id in manifest.get("sample_ids", [])]
                sample_count = sum(
                    (palm_demo.RUNTIME / "highres_capture" / sample_id / "full.jpg").is_file()
                    for sample_id in sample_ids
                )
                sessions.append({
                    "session_id": session_id,
                    "subject": str(manifest.get("subject", "")),
                    "hand": str(manifest.get("hand", "")),
                    "background": str(manifest.get("background", "")),
                    "distance_cm": manifest.get("distance_cm"),
                    "notes": str(manifest.get("notes", "")),
                    "phase": "complete" if len(sample_ids) >= HIGHRES_BATCH_TOTAL else str(manifest.get("phase", "await_hand")),
                    "sample_count": sample_count,
                    "total": HIGHRES_BATCH_TOTAL,
                    "started_at_pi_utc": manifest.get("started_at_pi_utc"),
                })
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return sessions

    def delete_highres_session(self, session_id: str) -> dict[str, Any]:
        """Move a collection and its originals into recoverable local trash."""
        session_root = self._highres_session_root(session_id)
        manifest_path = session_root / "manifest.json"
        with self.collection_batch_lock:
            with self.collection_lock:
                if not manifest_path.is_file():
                    raise FileNotFoundError("Collection session not found.")
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                sample_ids = [str(sample_id) for sample_id in manifest.get("sample_ids", [])]
                roots = [self._owned_highres_sample(session_id, sid) for sid in sample_ids]
                trash = self._highres_trash("session", session_id, sample_ids)
                moved = []
                try:
                    for root in roots:
                        if root.is_dir():
                            target = trash / root.name
                            root.rename(target)
                            moved.append((root, target))
                    session_root.rename(trash / "session")
                except Exception:
                    for root, target in reversed(moved):
                        target.rename(root)
                    raise
                if self.collection_batch is not None and self.collection_batch.get("session_id") == session_id:
                    self.collection_batch = None
        return {"status": "DELETED", "session_id": session_id, "deleted_samples": len(moved), "recoverable": True}

    @staticmethod
    def _owned_highres_sample(session_id: str, sample_id: str) -> Path:
        if re.fullmatch(r"\d{8}T\d{12}Z-[0-9a-f]{8}", sample_id) is None:
            raise ValueError("Invalid sample ID.")
        root = palm_demo.RUNTIME / "highres_capture" / sample_id
        if root.exists():
            metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
            if metadata.get("session_id") != session_id:
                raise ValueError("Photo does not belong to this collection.")
        return root

    @staticmethod
    def _highres_trash(kind: str, session_id: str, sample_ids: list[str]) -> Path:
        trash_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}-{uuid.uuid4().hex[:8]}"
        root = palm_demo.RUNTIME / "collection_trash" / trash_id
        root.mkdir(parents=True, exist_ok=False)
        (root / "recovery.json").write_text(json.dumps({
            "kind": kind, "session_id": session_id, "sample_ids": sample_ids,
            "deleted_at_utc": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return root

    def delete_highres_sample(self, session_id: str, sample_id: str) -> dict[str, Any]:
        """Remove one photo, renumber remaining metadata and allow a replacement."""
        manifest_path = self._highres_session_root(session_id) / "manifest.json"
        with self.collection_batch_lock:
            with self.collection_lock:
                original_manifest = manifest_path.read_bytes()
                batch = json.loads(original_manifest)
                if sample_id not in batch["sample_ids"]:
                    raise ValueError("Photo does not belong to this collection.")
                root = self._owned_highres_sample(session_id, sample_id)
                if not root.is_dir():
                    raise FileNotFoundError("Photo not found.")
                remaining = [sid for sid in batch["sample_ids"] if sid != sample_id]
                metadata_before = {}
                for sid in remaining:
                    path = self._owned_highres_sample(session_id, sid) / "metadata.json"
                    metadata_before[path] = path.read_bytes()
                trash = self._highres_trash("sample", session_id, [sample_id])
                (trash / "manifest_before.json").write_bytes(original_manifest)
                # Preserve prior numbering as well as all original image bytes.
                for path, content in metadata_before.items():
                    (trash / (path.parent.name + "-metadata.json")).write_bytes(content)
                target = trash / sample_id
                root.rename(target)
                try:
                    for index, (path, content) in enumerate(metadata_before.items(), 1):
                        metadata = json.loads(content)
                        metadata.setdefault("original_sample_index", metadata.get("sample_index"))
                        metadata["sample_index"] = index
                        temporary = path.with_suffix(".json.tmp")
                        temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
                        temporary.replace(path)
                    batch["sample_ids"] = remaining
                    if batch["phase"] != "abandoned":
                        batch["phase"] = "await_hand"
                    batch.setdefault("deleted_samples", []).append({
                        "sample_id": sample_id, "trash_id": trash.name,
                        "deleted_at_utc": datetime.now(timezone.utc).isoformat(),
                    })
                    self._write_highres_manifest(batch)
                except Exception:
                    root.parent.mkdir(parents=True, exist_ok=True)
                    target.rename(root)
                    for path, content in metadata_before.items():
                        path.write_bytes(content)
                    manifest_path.write_bytes(original_manifest)
                    raise
                if self.collection_batch is not None and self.collection_batch.get("session_id") == session_id:
                    self.collection_batch = batch
        return {"status": "DELETED", "session_id": session_id, "sample_id": sample_id,
                "captured": len(remaining), "recoverable": True}

    def highres_file(self, sample_id: str, filename: str) -> tuple[bytes, str]:
        if re.fullmatch(r"\d{8}T\d{12}Z-[0-9a-f]{8}", sample_id) is None:
            raise FileNotFoundError(sample_id)
        if filename == "thumbnail.jpg":
            path = palm_demo.RUNTIME / "highres_capture" / sample_id / "full.jpg"
            with Image.open(path) as original:
                original.thumbnail((320, 240))
                output = io.BytesIO()
                original.save(output, format="JPEG", quality=85)
            return output.getvalue(), "image/jpeg"
        if filename not in ("full.jpg", "preview.jpg", "metadata.json", "roi_128.png", "palm_detail_512.jpg"):
            raise FileNotFoundError(filename)
        path = palm_demo.RUNTIME / "highres_capture" / sample_id / filename
        content_type = "application/json; charset=utf-8" if filename.endswith(".json") else "image/png" if filename.endswith(".png") else "image/jpeg"
        return path.read_bytes(), content_type

    @staticmethod
    def _highres_session_root(session_id: str) -> Path:
        if re.fullmatch(r"\d{8}T\d{12}Z-[0-9a-f]{8}", session_id) is None:
            raise ValueError("Invalid session ID.")
        return palm_demo.RUNTIME / "highres_sessions" / session_id

    def _restore_highres_batch(self) -> dict[str, Any] | None:
        root = palm_demo.RUNTIME / "highres_sessions"
        if not root.exists():
            return None
        manifests = sorted(root.glob("*/manifest.json"), key=lambda path: path.stat().st_mtime_ns, reverse=True)
        if not manifests:
            return None
        try:
            batch = json.loads(manifests[0].read_text(encoding="utf-8"))
            if batch.get("phase") == "abandoned":
                return None
            batch["phase"] = "complete" if len(batch["sample_ids"]) >= HIGHRES_BATCH_TOTAL else "await_hand"
            return batch
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _write_highres_manifest(self, batch: dict[str, Any]) -> None:
        root = self._highres_session_root(batch["session_id"])
        root.mkdir(parents=True, exist_ok=True)
        record = {key: batch[key] for key in (
            "session_id", "subject", "hand", "background", "distance_cm", "notes",
            "started_at_pi_utc", "client_time_utc", "sample_ids", "phase",
        )}
        record["collection_mode"] = batch.get("collection_mode", "full_resolution_only" if getattr(self, "capture_only", False) else "full_resolution_with_roi")
        record["roi_processing"] = batch.get("roi_processing", "deferred" if getattr(self, "capture_only", False) else "at_capture")
        record["deleted_samples"] = batch.get("deleted_samples", [])
        temporary = root / "manifest.json.tmp"
        temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(root / "manifest.json")

    def start_highres_batch(self, payload: dict[str, Any]) -> dict[str, Any]:
        labels = self._highres_labels(payload)
        with self.collection_batch_lock:
            if self.collection_batch is not None and self.collection_batch["phase"] != "complete":
                raise RuntimeError("A 10-image session is already active; finish it before starting another.")
            session_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}-{uuid.uuid4().hex[:8]}"
            batch = {
                "session_id": session_id, **labels,
                "started_at_pi_utc": datetime.now(timezone.utc).isoformat(),
                "client_time_utc": str(payload.get("client_time", ""))[:50],
                "sample_ids": [], "phase": "await_hand",
            }
            self._write_highres_manifest(batch)
            self.collection_batch = batch
        return self.highres_batch_status()

    def abandon_highres_batch(self) -> dict[str, Any]:
        with self.collection_batch_lock:
            batch = self.collection_batch
            if batch is None or batch["phase"] == "complete":
                raise RuntimeError("There is no active session to abandon.")
            batch["phase"] = "abandoned"
            self._write_highres_manifest(batch)
            self.collection_batch = None
        return {"phase": "idle", "captured": 0, "total": HIGHRES_BATCH_TOTAL, "can_capture": False}

    def highres_batch_status(self) -> dict[str, Any]:
        with self.collection_batch_lock:
            batch = self.collection_batch
            if batch is None:
                return {"phase": "idle", "captured": 0, "total": HIGHRES_BATCH_TOTAL, "can_capture": False}
            captured = len(batch["sample_ids"])
            return {
                "session_id": batch["session_id"], "subject": batch["subject"], "hand": batch["hand"],
                "background": batch["background"], "distance_cm": batch["distance_cm"], "notes": batch["notes"],
                "phase": batch["phase"], "captured": captured, "total": HIGHRES_BATCH_TOTAL,
                "next_sample": min(captured + 1, HIGHRES_BATCH_TOTAL),
                "sample_ids": list(batch["sample_ids"]),
                "last_sample_id": batch["sample_ids"][-1] if captured else None,
                "can_capture": batch["phase"] == "await_hand",
            }

    def capture_highres_batch(self, client_time: str = "") -> dict[str, Any]:
        with self.collection_batch_lock:
            batch = self.collection_batch
            if batch is None or batch["phase"] != "await_hand":
                raise RuntimeError("Start a session before capturing, or begin a new one after ten images.")
            quad = None
            fresh_quad = False
            if not getattr(self, "capture_only", False):
                _image, _roi, quad, processed_status, _frame_id = self.camera.snapshot()
                captured_ms = processed_status.get("captured_monotonic_ms")
                fresh_quad = (
                    quad is not None
                    and processed_status.get("roi_status") == "tracking"
                    and isinstance(captured_ms, (int, float))
                    and time.monotonic() * 1000 - captured_ms <= 1500
                )
            sample_index = len(batch["sample_ids"]) + 1
            payload = {key: batch[key] for key in ("subject", "hand", "background", "distance_cm", "notes")}
            payload.update({"session_id": batch["session_id"], "sample_index": sample_index, "client_time": client_time})
            result = self.capture_highres(payload, preview_quad=quad if fresh_quad else None)
            batch["sample_ids"].append(result["sample_id"])
            batch["phase"] = "complete" if sample_index == HIGHRES_BATCH_TOTAL else "await_hand"
            self._write_highres_manifest(batch)
            result["sample_index"] = sample_index
            result["session_id"] = batch["session_id"]
            result["phase"] = batch["phase"]
            return result

    def download_highres_batch(self, session_id: str) -> tuple[str, bytes]:
        manifest_path = self._highres_session_root(session_id) / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not manifest["sample_ids"]:
            raise RuntimeError("Capture at least one image before downloading the ZIP.")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.write(manifest_path, f"{session_id}/manifest.json")
            for index, sample_id in enumerate(manifest["sample_ids"], 1):
                for filename in ("full.jpg", "preview.jpg", "metadata.json"):
                    path = palm_demo.RUNTIME / "highres_capture" / sample_id / filename
                    if path.is_file():
                        archive.write(path, f"{session_id}/sample_{index:03d}/{filename}")
                for filename in ("roi_128.png", "palm_detail_512.jpg"):
                    path = palm_demo.RUNTIME / "highres_capture" / sample_id / filename
                    if path.is_file():
                        archive.write(path, f"{session_id}/sample_{index:03d}/{filename}")
        return f"{session_id}.zip", output.getvalue()

    def start_repeatability(self, session_name: str, *, placements: int = REPEATABILITY_TOTAL) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", session_name or ""):
            raise ValueError("session name must contain only letters, numbers, '-' or '_'")
        if not 1 <= placements <= 100:
            raise ValueError("placements must be between 1 and 100")
        root = palm_demo.RUNTIME / "repeatability" / session_name
        if root.exists():
            raise RuntimeError(f"Repeatability session already exists: {root}")
        root.mkdir(parents=True)
        self.repeatability_root = root
        self.repeatability_next = 1
        self.repeatability_total = placements
        self.repeatability_phase = "await_empty"
        self.repeatability_last_frame_id = None
        self.camera.reset_roi_background()
        return f"Repeatability session started: {root}. Remove your hand, then confirm the empty view."

    def confirm_repeatability_empty(self) -> str:
        if self.repeatability_root is None or self.repeatability_phase != "await_empty":
            raise RuntimeError("Start a repeatability session first, or finish the current step.")
        status = self.camera.status()
        if status.get("quality_status") != "NO_HAND":
            reason = status.get("quality_reason") or status.get("quality_status") or "hand detected"
            raise RuntimeError(f"The view is not empty ({reason}); remove your hand and retry.")
        self.camera.reset_roi_background()
        self.repeatability_phase = "await_hand"
        return f"Empty view confirmed. Place the hand for placement {self.repeatability_next}/{self.repeatability_total}, then save when READY."

    def capture_repeatability_placement(self) -> str:
        if self.repeatability_root is None or self.repeatability_phase != "await_hand":
            raise RuntimeError("Confirm an empty view before capturing this placement.")
        image, roi, roi_quad, status, frame_id = self.camera.snapshot(
            after_frame_id=self.repeatability_last_frame_id
        )
        if status.get("quality_status") != "READY" or roi_quad is None:
            reason = status.get("quality_reason") or status.get("quality_status") or "ROI unavailable"
            raise RuntimeError(f"ROI is not READY ({reason}); hold the hand steady and retry.")
        placement = self.repeatability_next
        writer = DebugDatasetWriter(
            self.repeatability_root / f"placement_{placement:03d}",
            camera_settings=self.camera.capture_settings(),
            roi_algorithm_version=str(status.get("roi_geometry", palm_roi.ROI_GEOMETRY_VERSION)),
        )
        writer.save(
            sample_index=1,
            raw_image=image,
            roi_128=roi,
            metadata={
                "placement_index": placement,
                "captured_at": palm_demo.utc_now(),
                "frame_id": frame_id,
                "captured_monotonic_ms": status.get("captured_monotonic_ms"),
                "processed_monotonic_ms": status.get("processed_monotonic_ms"),
                "frame_timestamp_ms": status.get("roi_diagnostics", {}).get("frame_timestamp_ms"),
                "roi_quad": roi_quad.tolist(),
                "tracking_status": status.get("quality_status"),
                "tracker_status": status.get("roi_status"),
                "quality": status.get("quality", {}),
                "roi_geometry_diagnostics": status.get("roi_geometry_diagnostics", {}),
                "roi_status": status,
                "source": "debug_ui_repeatability",
                "image_color_order": "RGB",
                "camera_array_format": "RGB888_BGR_bytes",
            },
        )
        self.repeatability_next += 1
        self.repeatability_last_frame_id = frame_id
        self.camera.reset_quality_gate()
        if placement == self.repeatability_total:
            self.repeatability_phase = "complete"
            return f"Repeatability collection complete: {self.repeatability_root}"
        self.repeatability_phase = "await_empty"
        return f"Placement {placement}/{self.repeatability_total} saved. Remove your hand, then confirm the empty view for the next placement."

    def download_repeatability(self) -> tuple[str, bytes]:
        if self.repeatability_root is None or self.repeatability_phase != "complete":
            raise RuntimeError("Complete the repeatability test before downloading it.")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(self.repeatability_root.rglob("*")):
                if path.is_file():
                    archive.write(path, Path(self.repeatability_root.name) / path.relative_to(self.repeatability_root))
        return f"{self.repeatability_root.name}.zip", output.getvalue()

    def feature(
        self,
        image: Image.Image,
        roi_quad: np.ndarray | None,
        roi_status: dict[str, Any],
        processed_roi: np.ndarray | None = None,
    ) -> tuple[np.ndarray, dict[str, Any], float]:
        started = time.perf_counter()
        if self.camera.roi_mode in ("dynamic", "pklnet"):
            if roi_status.get("quality_status") != "READY":
                reason = str(roi_status.get("quality_reason") or roi_status.get("quality_status") or "NO_HAND")
                raise RuntimeError(f"ROI quality is not READY ({reason}); hold one open palm steady and retry.")
            if roi_quad is None:
                reason = str(roi_status.get("roi_reason") or roi_status.get("roi_status") or "no_hand")
                raise RuntimeError(
                    f"Palm ROI is not ready ({reason}); hold one open palm in the camera view."
                )
            if self.camera.roi_mode == "pklnet":
                if processed_roi is None:
                    raise RuntimeError("PKLNet matching requires the exact processed ROI from this frame")
                roi = processed_roi.copy()
                quality = dict(roi_status["quality"])
            else:
                roi, quality = palm_demo.crop_and_normalize(image, roi_quad=roi_quad)
        else:
            roi, quality = palm_demo.crop_and_normalize(image)
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
                "roi_geometry_diagnostics": status.get("roi_geometry_diagnostics", {}),
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
        if getattr(self, "capture_only", False):
            status["highres_batch"] = self.highres_batch_status()
            return status
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
        repeatability_root = getattr(self, "repeatability_root", None)
        repeatability_phase = getattr(self, "repeatability_phase", "idle")
        repeatability_next = getattr(self, "repeatability_next", 1)
        repeatability_total = getattr(self, "repeatability_total", REPEATABILITY_TOTAL)
        status["repeatability"] = {
            "active": repeatability_root is not None,
            "session": None if repeatability_root is None else str(repeatability_root),
            "phase": repeatability_phase,
            "next_placement": repeatability_next if repeatability_root is not None else None,
            "total_placements": repeatability_total,
            "can_confirm_empty": repeatability_phase == "await_empty" and status.get("quality_status") == "NO_HAND",
            "can_capture": repeatability_phase == "await_hand" and status.get("quality_status") == "READY",
        }
        status["highres_batch"] = self.highres_batch_status()
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
                feature, quality, timing = self.feature(image, roi_quad, roi_status, processed_roi=_roi)
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
                        "preview_sensor_output_size": self.camera.capture_settings()["preview_sensor_output_size"],
                        "roi_mode": self.camera.roi_mode,
                        "roi_geometry": _roi_geometry(self.camera.roi_mode),
                        "crop": palm_demo.DEFAULT_CROP if self.camera.roi_mode == "fixed" else None,
                        "min_contrast": 0.0, "image_quality_policy": "diagnostic_only", "quality": qualities,
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
            if self.camera.roi_mode == "pklnet" and metadata.get("roi_geometry") != PKLNET_GEOMETRY_VERSION:
                raise RuntimeError("Template PKLNet geometry version differs; re-enroll this identity.")
            if metadata.get("preview_sensor_output_size") != self.camera.capture_settings()["preview_sensor_output_size"]:
                raise RuntimeError("Template camera field of view differs from the current preview; re-enroll this identity.")
            previous_frame_id = self.camera.latest_processed_frame_id()
            image, _roi, roi_quad, roi_status, frame_id = self.camera.snapshot(after_frame_id=previous_frame_id)
            feature, quality, timing = self.feature(image, roi_quad, roi_status, processed_roi=_roi)
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
            if route in ("/palmir-report", "/palmir-examples.jpg", "/palmir-scores.csv", "/palmir-blur-examples.jpg", "/palmir-audit-1.jpg", "/palmir-audit-2.jpg", "/palmir-audit-3.jpg", "/palmir-audit-4.jpg"):
                names = {"/palmir-report": ("report.html", "text/html; charset=utf-8"),
                         "/palmir-examples.jpg": ("comparison.jpg", "image/jpeg"),
                         "/palmir-scores.csv": ("scores.csv", "text/csv; charset=utf-8"),
                         "/palmir-blur-examples.jpg": ("audit/blur_probe_pytorch/examples.jpg", "image/jpeg"),
                         "/palmir-audit-1.jpg": ("audit/bankey-10-12_left.jpg", "image/jpeg"),
                         "/palmir-audit-2.jpg": ("audit/bankey-10-12_right.jpg", "image/jpeg"),
                         "/palmir-audit-3.jpg": ("audit/stephen-10-13_left.jpg", "image/jpeg"),
                         "/palmir-audit-4.jpg": ("audit/stephen-10-13_right.jpg", "image/jpeg")}
                name, content_type = names[route]
                path = palm_demo.ROOT / "runtime/palmir_camera_assay" / name
                if not path.is_file():
                    json_response(self, HTTPStatus.NOT_FOUND, {"message": "Comparison report is not available yet"})
                    return
                body = path.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if route == "/api/camera/focus":
                from palm_app import camera_focus
                json_response(self, HTTPStatus.OK, camera_focus.status())
                return
            if route == "/palmir":
                from palmir_page import HTML as PALMIR_HTML
                body = PALMIR_HTML.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if getattr(app, "capture_only", False) and route in ("/demo", "/roi", "/roi.jpg", "/debug/processed.jpg", "/api/demo/users", "/api/users", "/api/download-repeatability"):
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "This service is configured for high-resolution collection."})
                return
            if route == "/":
                body = (CAPTURE_HTML if getattr(app, "capture_only", False) else HTML).encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route == "/collect":
                body = (CAPTURE_HTML if getattr(app, "capture_only", False) else COLLECTION_HTML).encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route == "/demo":
                body = DEMO_HTML.encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route == "/api/demo/users":
                json_response(self, HTTPStatus.OK, {"users": app.demo.users()})
            elif route == "/api/collection/latest":
                json_response(self, HTTPStatus.OK, app.latest_highres())
            elif route == "/api/collection/sessions":
                json_response(self, HTTPStatus.OK, {"sessions": app.list_highres_sessions()})
            elif route.startswith("/api/collection/session/") and route.endswith(".zip"):
                try:
                    session_id = route[len("/api/collection/session/"):-len(".zip")]
                    filename, body = app.download_highres_batch(session_id)
                except (ValueError, RuntimeError, FileNotFoundError, KeyError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                    return
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route.startswith("/api/collection/sample/"):
                try:
                    _, _, _, _, sample_id, filename = route.split("/")
                    body, content_type = app.highres_file(sample_id, filename)
                except (ValueError, FileNotFoundError):
                    json_response(self, HTTPStatus.NOT_FOUND, {"message": "Sample not found"})
                    return
                self.send_response(HTTPStatus.OK)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Type", content_type)
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
                try:
                    frame = app.camera.jpeg_frame()
                except RuntimeError as error:
                    json_response(self, HTTPStatus.SERVICE_UNAVAILABLE, {"message": str(error)})
                    return
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
            elif route == "/api/download-repeatability":
                try:
                    filename, body = app.download_repeatability()
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/zip")
                    self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/api/camera/focus":
                from palm_app import camera_focus
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 <= length <= 4096:
                        raise ValueError("Invalid request size")
                    self.rfile.read(length)
                    json_response(self, HTTPStatus.OK, camera_focus.enable())
                except (ValueError, OSError, RuntimeError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path in ("/api/palmir/snapshot", "/api/palmir/restore", "/api/palmir/reference"):
                try:
                    from palm_app.palmir_restore import RESTORER
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 1 <= length <= 4096:
                        raise ValueError("Invalid request size")
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError("Expected a JSON object")
                    if self.path.endswith("snapshot"):
                        result = RESTORER.capture(app.camera)
                    elif self.path.endswith("reference"):
                        result = RESTORER.enroll_reference(payload)
                    else:
                        result = RESTORER.restore_snapshot(payload)
                    json_response(self, HTTPStatus.OK, result)
                except (ValueError, TypeError, RuntimeError, OSError, ImportError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if getattr(app, "capture_only", False) and not self.path.startswith("/api/collection/"):
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Only collection actions are enabled."})
                return
            if self.path in ("/api/demo/enroll", "/api/demo/identify", "/api/demo/confirm", "/api/demo/cancel"):
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 1 or length > 4096:
                        raise ValueError("Invalid request size")
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError("Expected a JSON object")
                    if self.path.endswith("enroll"):
                        result = app.demo.enroll(str(payload.get("user_id", "")), str(payload.get("display_name", "")))
                    elif self.path.endswith("identify"):
                        result = app.demo.identify()
                    elif self.path.endswith("confirm"):
                        result = app.demo.confirm(str(payload.get("token", "")), str(payload.get("user_id", "")))
                    else:
                        result = app.demo.cancel(str(payload.get("token", "")))
                    json_response(self, HTTPStatus.OK, result)
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/collection/start-batch":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 1 or length > 4096:
                        raise ValueError("Invalid request size")
                    payload = json.loads(self.rfile.read(length))
                    json_response(self, HTTPStatus.OK, app.start_highres_batch(payload))
                except (ValueError, RuntimeError, TypeError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/collection/abandon-batch":
                try:
                    json_response(self, HTTPStatus.OK, app.abandon_highres_batch())
                except RuntimeError as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path in ("/api/collection/delete-session", "/api/collection/delete-sample"):
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 1 or length > 4096:
                        raise ValueError("Invalid request size")
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError("Expected a JSON object.")
                    session_id = str(payload.get("session_id", ""))
                    result = (app.delete_highres_sample(session_id, str(payload.get("sample_id", "")))
                              if self.path.endswith("delete-sample") else app.delete_highres_session(session_id))
                    json_response(self, HTTPStatus.OK, result)
                except (ValueError, RuntimeError, TypeError, OSError, json.JSONDecodeError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/collection/capture-batch":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 1 or length > 4096:
                        raise ValueError("Invalid request size")
                    payload = json.loads(self.rfile.read(length))
                    if not isinstance(payload, dict):
                        raise ValueError("Expected a JSON object.")
                    json_response(self, HTTPStatus.OK, app.capture_highres_batch(str(payload.get("client_time", ""))[:50]))
                except (ValueError, RuntimeError, TypeError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/collection/capture":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 1 or length > 4096:
                        raise ValueError("Invalid request size")
                    payload = json.loads(self.rfile.read(length))
                    json_response(self, HTTPStatus.OK, app.capture_highres(payload))
                except (ValueError, RuntimeError, TypeError) as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/start-repeatability":
                try:
                    payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                    session = str(payload.get("session", "test01"))
                    placements = int(payload.get("placements", REPEATABILITY_TOTAL))
                    json_response(self, HTTPStatus.OK, {"message": app.start_repeatability(session, placements=placements)})
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/confirm-repeatability-empty":
                try:
                    self.rfile.read(int(self.headers.get("Content-Length", "0")))
                    json_response(self, HTTPStatus.OK, {"message": app.confirm_repeatability_empty()})
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
            if self.path == "/api/capture-repeatability":
                try:
                    self.rfile.read(int(self.headers.get("Content-Length", "0")))
                    json_response(self, HTTPStatus.OK, {"message": app.capture_repeatability_placement()})
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return
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
    parser.add_argument("--roi-mode", choices=("dynamic", "fixed", "pklnet"), default="pklnet")
    parser.add_argument("--capture-only", action="store_true", default=True, help="Collect original full-resolution images without ROI or matcher processing (default).")
    parser.add_argument("--enable-recognition", dest="capture_only", action="store_false", help="Explicitly enable the optional ROI/recognition debug routes.")
    parser.add_argument("--demo-matcher", default=DEMO_MATCHER, help="Matcher for optional /demo recognition (default: DoN; alternatives include OC, PC and FastCC).")
    parser.add_argument("--opencv-threads", type=int, choices=range(1, 65), metavar="1..64", help="OpenCV worker limit; omitted keeps the library default.")
    parser.add_argument("--pklnet-threads", type=int, choices=range(1, 65), metavar="1..64", help="ONNX localizer worker limit; omitted keeps the existing default.")
    parser.add_argument("--hand-model", type=Path, default=DEFAULT_HAND_MODEL)
    parser.add_argument("--hand-pose-model", type=Path, default=DEFAULT_HAND_POSE_MODEL)
    parser.add_argument("--refine-pose", action="store_true", help="Enable the slower 21-point pose refinement pass.")
    parser.add_argument("--inference-ms", type=float, default=800.0, help="Minimum interval between detector passes.")
    parser.add_argument("--input-width", type=int, default=320, help="Small live image width used by the detector.")
    parser.add_argument("--input-height", type=int, default=240, help="Small live image height used by the detector.")
    parser.add_argument("--recovery-pass", action="store_true", help="Run a second detector pass when no hand is found; slower.")
    parser.add_argument("--camera-tuning-file", type=Path, help="Optional libcamera tuning JSON, e.g. imx219_noir.json for NoIR + IR.")
    args = parser.parse_args()
    if args.opencv_threads is not None:
        cv2.setNumThreads(args.opencv_threads)
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
        capture_only=args.capture_only,
        pklnet_threads=args.pklnet_threads,
    )
    app = App(feed, demo_matcher=args.demo_matcher)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    print(f"Palm debug UI: http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        feed.close()
        if hasattr(app.demo_algorithm,"close"):
            app.demo_algorithm.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
