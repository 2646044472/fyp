#!/usr/bin/env python3
"""Local Pi capture station UI overlay; preserve the installed demo engine and stores."""
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit

APP = Path.home() / "palm_demo"
URL = "http://127.0.0.1:8088"
NAV_CSS = """<style>
.station-nav{display:flex;flex-wrap:wrap;gap:9px;align-items:center;padding:12px max(16px,4vw);border-bottom:1px solid #728aa655;background:#122638;color:#e5f3ff;font:600 15px system-ui,sans-serif}
.station-nav a{padding:8px 13px;border-radius:11px;text-decoration:none;color:#bedcf7;border:1px solid #557795}
.station-nav a[aria-current=page]{background:#b9e7ff;color:#102638;border-color:#d4eeff}
.station-nav b{margin-right:12px}.station-nav small{margin-left:auto;font-weight:500;color:#b6c4d1}
.station-nav a:focus-visible{outline:3px solid #81cfff;outline-offset:2px}button[disabled]{cursor:not-allowed}
</style>"""
PAGES = (("/enroll", "① Palm enrollment"), ("/gate", "② Palm verification"), ("/collect", "③ Data management"))
RELEASE = "Palm capture station · Pi-compatible PKLNet + FastCC v6"


def nav(active):
    links = "".join(f'<a href="{p}"{" aria-current=page" if p == active else ""}>{label}</a>' for p, label in PAGES)
    return NAV_CSS + f'<nav class="station-nav" aria-label="Capture station steps"><b>FYP palm capture station</b>{links}<small>This device only · Research demo</small></nav>'


def stand_by(active, msg):
    return f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>FYP palm capture station</title><style>body{{margin:0;background:#eef4f8;color:#20394b;font:18px/1.7 system-ui,sans-serif}}main{{padding:30px max(20px,8vw)}}button{{font:inherit;padding:8px 15px}}small{{color:#3d5463}}</style>
{nav(active)}<main><small>{RELEASE}</small><h1>Waiting for the camera and recognition service</h1>
<p role=status>{escape(msg)}</p><p>The page will open automatically when the camera is connected. For a CSI ribbon cable, shut down the Raspberry Pi before connecting it.<br>Data stays on this Raspberry Pi. The station does not enroll or save images while starting up.</p>
<button onclick=location.reload()>Check now</button></main><script>
async function ready(){{try{{const r=await fetch('/station-health',{{cache:'no-store'}});const d=await r.json();if(d.ready)location.reload();}}catch(_){{}}setTimeout(ready,2000)}}ready();
</script></html>"""


def send(handler, body, status=200, mime="text/html; charset=utf-8"):
    data = body.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Type", mime)
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    try:
        handler.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError):
        pass


GATE = r'''<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1">
<title>Palm verification</title><style>
*{box-sizing:border-box}body{margin:0;color:#dae8f8;background:#101c28;font:18px/1.5 system-ui,sans-serif} main{max-width:1150px;margin:auto;padding:28px max(18px,4vw);display:grid;grid-template-columns:1.4fr 1fr;align-items:center;gap:24px}
figure{position:relative;margin:0;aspect-ratio:4/3;background:#090e16;border-radius:17px;overflow:hidden} img{display:block;width:100%;height:100%;object-fit:contain}
.guide{position:absolute;inset:12% 24%;border:2px dashed #bbddf999;border-radius:30%;pointer-events:none} h1{font-size:clamp(28px,4vw,50px);margin:6px 0 10px}small{color:#a6bdd2;letter-spacing:.07em} p{min-height:2.8em} button{background:#26435d;color:#fff;border:1px solid #6e8faa;border-radius:10px;padding:10px 16px;font:inherit;cursor:pointer}.ok h1{color:#73e2bc}.warn h1{color:#ffd393}#timing{font-size:14px;color:#a6bdd2}
@media(max-width:760px){main{grid-template-columns:1fr}figure{max-height:43vh}}
</style><body>
<main><figure><img id="live" alt="Camera feed"><div class="guide"></div></figure>
<section id="box"><small>Live preview · One check when the palm is ready</small><h1 id="title">Starting up</h1><p id="hint" role="status" aria-live="polite">Waiting for the camera and enrollment records.</p><p id="timing"></p><button id="pause">Pause verification</button></section></main>
<script>
const byId = name => document.getElementById(name);
let paused=false,busy=false,armed=true,emptySince=null,seenSince=null,epoch=0,users=null,previewUrl=null;
function show(title,hint,cls=''){byId('title').textContent=title;byId('hint').textContent=hint;byId('box').className=cls}
async function req(path,options={},timeout=2800){
 const c=new AbortController(),timer=setTimeout(()=>c.abort(),timeout);
 try {const r=await fetch(path,{...options,cache:'no-store',signal:c.signal});if(!r.ok)throw Error('HTTP '+r.status);return r}
 finally{clearTimeout(timer)}
}
async function loadUsers(){try{if(!document.hidden){const v=await(await req('/api/demo/users')).json();users=v.users.filter(x=>!x.needs_reenrollment).length;}}catch(_){users=null}finally{setTimeout(loadUsers,4000)}}
async function preview(){try{if(!document.hidden){const r=await req('/frame.jpg?fresh='+Date.now());const next=URL.createObjectURL(await r.blob());byId('live').src=next;if(previewUrl)URL.revokeObjectURL(previewUrl);previewUrl=next;}}
catch(_){byId('live').removeAttribute('src');if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null}}finally{setTimeout(preview,240)}}
async function identify(){if(!armed||busy||paused||document.hidden)return;const id=epoch,t=performance.now();armed=false;busy=true;emptySince=null;seenSince=null;byId('timing').textContent='';
 show('Verifying','Hold your palm steady until the result appears.');
 try{const result=await(await req('/api/gate/identify',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'},15000)).json();
 if(id!==epoch)return;const sec=((performance.now()-t)/1000).toFixed(2);
 byId('timing').textContent='Browser request: '+sec+' s (excluding time to present the palm)';
 if(result.status==='MATCH')show('Verification passed',(result.display_name||'Enrolled palm')+'. Remove your hand.','ok');
 else if(result.status==='UNKNOWN')show('Verification failed','No enrolled palm recognized. Remove your hand before trying again.','warn');
 else show('Verification incomplete','Remove your hand, adjust the distance, and try again.','warn');
 }catch(_){if(id===epoch)show('No verification result','Remove your hand and try again. Avoid clicking repeatedly.','warn')}
 finally{busy=false}
}
async function status(){try{
 if(!document.hidden&&!paused){
  const d=await(await req('/api/status')).json();
  const state=d.demo_quality_status??d.quality_status, fresh=d.camera_ready&&d.roi_status_fresh===true;
  const enough=Number(d.demo_quality_consecutive_frames??d.quality_consecutive_frames??0)>=Number(d.demo_quality_required_frames??d.quality_required_frames??5);
  if(!busy){
   if(!fresh){emptySince=null;seenSince=null;show('Waiting for the camera','No new camera feed. Check the camera connection.','warn')}
   else if(users===null){show('Loading enrollment records','Waiting for enrollment records.')}
   else if(users===0){show('Enrollment required','Choose Palm enrollment above and complete the five-photo enrollment first.')}
   else if(!armed){if(state==='NO_HAND'){emptySince??=performance.now();if(performance.now()-emptySince>=700){armed=true;emptySince=null;seenSince=null;byId('timing').textContent='';show('Present your palm','Face your palm toward the camera and keep your whole hand in the guide.')}}else emptySince=null;}
   else if(state==='READY'&&enough) void identify();
   else if(state==='NO_HAND'){seenSince=null;show('Present your palm','Face your palm toward the camera and keep your whole hand in the guide.')}
   else {seenSince??=performance.now();if(performance.now()-seenSince>8000){armed=false;emptySince=null;show('No usable palm region','Remove your hand, adjust the light and distance, then try again.','warn')}else show('Hold your palm steady','Keep your whole palm in frame. Move back a little if it is too close or blurry.')}
  }
 }
}catch(_){if(!busy&&!paused)show('Status temporarily unavailable','Waiting for the local service to recover.','warn')}finally{setTimeout(status,300)}}
byId('pause').onclick=()=>{epoch++;paused=!paused;byId('pause').textContent=paused?'Resume verification':'Pause verification';armed=!paused;emptySince=null;seenSince=null;
 show(paused?'Verification paused':'Present your palm',paused?'Select Resume verification when ready.':'Face your palm toward the camera and keep your whole hand in the guide.')};
loadUsers();preview();status();
</script></body></html>'''


def replace_label(html, current, legacy, new, *, count=-1):
    """Update the English base page, or a compatible pre-English installation."""
    return html.replace(current if current in html else legacy, new, count)


def render(html, selected):
    if selected == "/enroll":
        from enrollment_review import PANEL
        html = html.replace("</body>", PANEL + "</body>", 1)
        html = replace_label(html, "Continue capture</button>", "\u7ee7\u7eed\u91c7\u96c6</button>", "Continue capture / Retake</button>", count=1)
        html = replace_label(html, "Five qualified palm regions are selected and saved automatically.", "\u7cfb\u7edf\u4f1a\u81ea\u52a8\u7b5b\u9009\u4e94\u5f20\u5408\u683c\u638c\u533a\u5e76\u4fdd\u5b58\u3002", "The system selects five original/ROI pairs. Enlarge, remove, or retake them before you confirm and save.", count=1)
        html = html.replace("/api/status?t=", "/api/station/enroll-status?t=")
        html = html.replace("if(last.status==='READY'||last.status==='STOPPED'", "if(last.status==='STATION_PARTIAL'||last.status==='READY'||last.status==='STOPPED'")
        html = html.replace("if(last.status==='READY'){$('enroll-commit')", "if(last.status==='STATION_PARTIAL'){stationPartial=true;enrollmentPaused=true;enrollmentSawNotReady=false;notice.textContent=last.reason;controls()}else if(last.status==='READY'){$('enroll-commit')")
        html = html.replace("function scheduleEnrollmentCommit(token,retries=0){", "function scheduleEnrollmentCommit(token,retries=0){return;", 1)
        html = html.replace("enrollmentToken=saved;enrollmentSettings=state;", "enrollmentToken=saved;stationPartial=Boolean(state.station_partial);stationResumeAllowed=state.resume_allowed!==false;enrollmentSettings=state;", 1)
        html = html.replace("if(enrollmentPaused&&enrollmentSawNotReady&&roiReady", "if(!stationPartial&&enrollmentPaused&&enrollmentSawNotReady&&roiReady")
        html = html.replace("$('enroll-resume').onclick=()=>resumeEnrollment(true);", """
let stationPartial=false,stationResumeAllowed=true;
async function stationResume(){if(!stationResumeAllowed)return;const t=enrollmentToken;if(stationPartial){try{await post('/api/station/enroll-refill',{token:t});if(enrollmentToken!==t)return;stationPartial=false}catch(e){notice.textContent=e.message;return}}
return resumeEnrollment(true)}
$('enroll-resume').onclick=stationResume;
""")
        html = html.replace("enrollmentToken=requestToken;controls();", "enrollmentToken=requestToken;stationPartial=false;stationResumeAllowed=true;controls();", 1)
        html = html.replace("$('enroll-resume').disabled=", "$('enroll-resume').disabled=!stationResumeAllowed||", 1)
        html = replace_label(html, "Once the pool is full, automatically select ${required} to save.", "\u5019\u9009\u6c60\u51d1\u9f50\u540e\u4f1a\u81ea\u52a8\u9009 ${required} \u5f20\u4fdd\u5b58\u3002", "Once the pool is full, the system selects ${required} photos for review. Nothing is saved until you confirm.")
        html = replace_label(html, "Saving.${elapsed}", "\u6b63\u5728\u4fdd\u5b58\u3002${elapsed}", "Review the originals and ROIs, then confirm to save.${elapsed}")
        html = html.replace("clearStoredEnrollment();enrollmentCommitUncertain=false;enrollmentToken='';enrollmentPaused=false;enrollmentSettings=null;$('enroll-commit').hidden=true;$('enroll-progress').textContent=", "clearStoredEnrollment();enrollmentCommitUncertain=false;enrollmentToken='';enrollmentPaused=false;enrollmentSettings=null;$('enroll-commit').hidden=true;$('enroll-progress').textContent=d.enrollment_archive_id?'The original photos, ROIs, and enrollment templates were saved.':", 1)
        html = replace_label(html, "Verifying the previous auto-save. If the server still reports a pending save, it will resume safely.", "\u6b63\u5728\u6838\u5b9e\u4e0a\u6b21\u81ea\u52a8\u4fdd\u5b58\uff1b\u82e5\u670d\u52a1\u7aef\u4ecd\u663e\u793a\u5f85\u4fdd\u5b58\uff0c\u7cfb\u7edf\u4f1a\u5b89\u5168\u7eed\u5b58\u3002", "Check whether your last save completed. This page will not submit another save automatically.")
        html = replace_label(html, "Incomplete enrollment restored. Auto-capture resumes when the preview is ready; you may also continue manually or cancel.", "\u5df2\u6062\u590d\u672a\u5b8c\u6210\u7684\u5f55\u5165\uff1b\u9884\u89c8\u5c31\u7eea\u540e\u5c06\u7ee7\u7eed\u81ea\u52a8\u91c7\u96c6\uff0c\u4e5f\u53ef\u624b\u52a8\u7ee7\u7eed\u6216\u53d6\u6d88\u3002", "Enrollment restored. The selection is retained; retakes fill only the missing slots.")
        html = replace_label(html, "Palmprint payment · Basic demo", "\u638c\u7eb9\u652f\u4ed8 \u00b7 \u57fa\u7840\u6f14\u793a", "Palm enrollment", count=1)
        html = replace_label(html, "<h2>2. Simulated payment</h2>", "<h2>2. \u6a21\u62df\u652f\u4ed8</h2>", "<h2>After enrollment</h2><p><a href=\"/gate\">Go to Palm verification →</a></p><h2 hidden>Legacy supervised demo</h2>", count=1)
        html = replace_label(html, "<p>Demo item · MOP 20.00</p>", "<p>\u6f14\u793a\u5546\u54c1 \u00b7 MOP 20.00</p>", "", count=1)
        html = html.replace("<title>Palmprint payment demo</title>", "<title>Palm enrollment</title>", 1)
        html = html.replace("Palmprint enrollment · Access demo", "Palm enrollment")
        html = html.replace("The system automatically selects and saves five frames.",
                            "Review the five selected photos and confirm before saving.")
        html = html.replace('id="identify"', 'id="identify" hidden', 1)
        html = replace_label(html, "Enroll first, then capture to identify.", "\u5148\u5f55\u5165\uff0c\u518d\u62cd\u7167\u8bc6\u522b\u3002", "Choose the left or right hand and use that hand throughout. The station selects the best five photos for review within 60 seconds. No need to press capture repeatedly.")
        html = html.replace("const GATE_MODE=new URLSearchParams(location.search).get('mode')==='gate'", "const GATE_MODE=true", 1)
        html = html.replace("async function preview(){", "async function preview(){\n if(document.hidden){setTimeout(preview,400);return;}", 1)
        html = replace_label(html, "Once collection finishes, automatically select ${required} photos", "\u6536\u96c6\u5b8c\u6210\u540e\u81ea\u52a8\u9009\u51fa ${required} \u5f20", "Target: ${required} photos. The station ranks usable palm regions by image quality; there is no fixed sharpness cutoff.", count=1)
    elif selected == "/gate":
        html = GATE
    elif selected == "/collect":
        html = replace_label(html, "Start ten-photo session", "\u5f00\u59cb\u5341\u5f20\u91c7\u96c6", "Start a set of retakes", count=1)
    return html.replace("<body>", "<body>" + nav(selected), 1)


def fresh_csi_frame(feed, check_ready, failure_class, *, clock=time.monotonic):
    """Return a distinct, live-validated CSI image and its exact existing ROI."""
    deadline = clock() + 1.7
    with feed.frame_condition:
        while True:
            processed = feed.latest_processed
            if processed is not None:
                captured = processed.captured
                age = clock() - captured.captured_monotonic
                if (captured.frame_id > feed.station_last_used
                        and 0 <= age <= min(1.25, feed.quality_gate.max_age_ms / 1000.0)):
                    status = dict(processed.roi_status)
                    status.update(feed._camera_frame_state())
                    status.update(roi_status_fresh=feed.processing_thread.is_alive(),
                                  processed_frame_id=captured.frame_id,
                                  latest_frame_id=None if feed.latest is None else feed.latest.frame_id)
                    failure = check_ready(status)
                    if not failure and processed.roi is not None and processed.roi_quad is not None:
                        image = captured.image.copy()
                        roi, quad = processed.roi.copy(), processed.roi_quad.copy()
                        feed.station_last_used = captured.frame_id
                        return image.copy(), image, {
                            "capture_backend": "picamera2",
                            "capture_kind": "same_fresh_ready_processed_csi_video_frame",
                            "capture_frame_id": captured.frame_id,
                            "capture_resolution": list(image.size),
                            "color_order": "RGB",
                            "capture_profile": feed.capture_profile,
                            "processed_roi": roi,
                            "processed_roi_quad": quad,
                            "processed_roi_quality": dict(processed.roi_status.get("quality", {})),
                            "processed_roi_mode": processed.roi_status.get("roi_mode"),
                        }
            remaining = deadline - clock()
            if not feed.running or remaining <= 0:
                raise failure_class("ROI_NOT_READY", "No new usable frame. Remove your hand before trying again.")
            feed.frame_condition.wait(timeout=remaining)


def install_optional_csi_stream(app):
    base_camera, base_app = app.CameraFeed, app.App
    local = threading.local()

    class StationCamera(base_camera):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.station_last_used = -1
            if self.camera_backend == "picamera2":
                # Tag separately: do not call these new inputs the old full stills.
                self.capture_source = "csi-video-640x480-exact-roi-v1"

        def capture_highres(self):
            if self.camera_backend == "picamera2" and getattr(local, "recognition", False):
                return fresh_csi_frame(self, app._capture_readiness_gate_failure,
                                       app.CaptureProcessingFailure)
            return super().capture_highres()

    class StationApp(base_app):
        def capture_demo_feature(self, *args, **kwargs):
            local.recognition = True
            try:
                return super().capture_demo_feature(*args, **kwargs)
            finally:
                local.recognition = False

    app.CameraFeed, app.App = StationCamera, StationApp


def engine():
    sys.path.insert(0, str(APP))
    os.chdir(APP)
    from palm_app import debug_ui as app
    if os.environ.get("PALM_STATION_CSI_STREAM") == "1":
        install_optional_csi_stream(app)
    import enrollment_best_frame
    import enrollment_review
    from enrollment_window_adapter import start_refill
    enrollment_best_frame.install(app)
    original = app.make_handler
    pages = {p: render(html, p) for p, html in zip((x[0] for x in PAGES), (app.DEMO_HTML,app.GATE_HTML,app.COLLECTION_HTML))}
    def overlay(application):
        application.demo.enrollment_archive_root = app.palm_demo.RUNTIME / "enrollment_pairs"
        base = original(application)
        class Handler(base):
            def do_POST(self):
                path = urlsplit(self.path).path
                if path not in ("/api/station/enroll-review", "/api/station/enroll-remove", "/api/station/enroll-refill", "/api/station/enroll-stop"):
                    return super().do_POST()
                try:
                    host = self.headers.get("Host", "")
                    hostname = host.rsplit(":", 1)[0] if ":" in host else host
                    if (hostname not in {"127.0.0.1", "localhost"}
                            or self.headers.get("Origin") not in {None, "http://" + host}):
                        return send(self, '{"message":"This request is only available for the current enrollment on this station."}', 403, "application/json")
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 1 <= size <= 4096 or self.headers.get_content_type() != "application/json":
                        raise ValueError("Invalid request format.")
                    payload = json.loads(self.rfile.read(size))
                    if not isinstance(payload, dict) or not isinstance(payload.get("token"), str):
                        raise ValueError("This enrollment session is no longer valid.")
                    frame = payload.get("frame")
                    if path.endswith("remove") and type(frame) is not int:
                        raise ValueError("Select a photo from this enrollment session.")
                    if path.endswith("refill"):
                        return send(self, json.dumps(start_refill(application.demo,payload["token"])), mime="application/json")
                    result = enrollment_review.mutate(application.demo, payload["token"],
                                                      frame if path.endswith("remove") else None,
                                                      stop=path.endswith("stop"))
                    return send(self, json.dumps(result), mime="application/json")
                except (TypeError, ValueError) as exc:
                    return send(self, json.dumps({"message": str(exc)}), 400, "application/json")

            def do_GET(self):
                path = urlsplit(self.path).path
                if path in ("/", "/enroll", "/gate", "/collect"):
                    return send(self, pages["/enroll" if path == "/" else path])
                if path == "/api/station/enroll-status":
                    status = enrollment_best_frame.ranking_status(application.status())
                    status["original_capture_size"] = list(application.camera.uvc_native_size or application.camera.capture_size)
                    return send(self, json.dumps(status), mime="application/json")
                if path == "/station-health":
                    return send(self, '{"ready":true}', mime="application/json")
                return super().do_GET()
        return Handler
    app.make_handler = overlay
    sys.argv = [sys.argv[0], "--host", "127.0.0.1", "--port", "8088", "--enable-recognition",
                "--demo-matcher", "FastCCDemo-v6", "--roi-mode", "pklnet", "--opencv-threads", "4",
                "--pklnet-threads", "2", "--width", "640", "--height", "480"]
    uvc = os.environ.get("PALM_STATION_UVC")
    if uvc:
        sys.argv += ["--camera-backend", "uvc", "--uvc-device", uvc]
        native = os.environ.get("PALM_STATION_UVC_NATIVE_SIZE")
        if native:
            sys.argv += ["--uvc-native-size", *native.split("x")]
    tuning = os.environ.get("PALM_STATION_TUNING")
    if tuning and not uvc:
        sys.argv += ["--camera-tuning-file", tuning]
    app.main()


def camera_available():
    uvc = os.environ.get("PALM_STATION_UVC")
    if uvc:
        return Path(uvc).is_char_device()
    try:
        from picamera2 import Picamera2
        return bool(Picamera2.global_camera_info())
    except Exception as e:
        print(f"Camera check failed: {type(e).__name__}", flush=True)
        return False


def supervisor():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/station-health":
                return send(self, '{"ready":false}', mime="application/json")
            if path in ("/", "/enroll", "/gate", "/collect"):
                selected = "/enroll" if path == "/" else path
                return send(self, stand_by(selected, "The camera is unavailable or the recognition service is recovering."))
            return send(self, "Not available before the local engine starts", HTTPStatus.SERVICE_UNAVAILABLE, "text/plain")
        def log_message(self, *_):
            pass
    while True:
        with ThreadingHTTPServer(("127.0.0.1",8088), Handler) as server:
            while not camera_available():
                server.timeout = 0.6
                server.handle_request()
        # The engine serves the same loopback port; no competing camera workers.
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--engine"], check=False)
        if result.returncode == 0:
            return
        print(f"Engine exited {result.returncode}; rechecking hardware.", flush=True)
        with ThreadingHTTPServer(("127.0.0.1",8088), Handler) as server:
            deadline=time.monotonic()+8
            while time.monotonic() < deadline:
                server.timeout=1
                server.handle_request()


if __name__ == "__main__":
    engine() if "--engine" in sys.argv else supervisor()
