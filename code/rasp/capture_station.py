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
PAGES = (("/enroll", "① 掌纹登记"), ("/gate", "② 放掌验证"), ("/collect", "③ 数据管理"))
RELEASE = "掌纹采集站 · Pi 兼容基线 PKLNet＋FastCC v6"


def nav(active):
    links = "".join(f'<a href="{p}"{" aria-current=page" if p == active else ""}>{label}</a>' for p, label in PAGES)
    return NAV_CSS + f'<nav class="station-nav" aria-label="采集站步骤"><b>FYP 掌纹采集站</b>{links}<small>仅此设备 · 研究演示</small></nav>'


def stand_by(active, msg):
    return f"""<!doctype html><html lang=zh-CN><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>FYP 掌纹采集站</title><style>body{{margin:0;background:#eef4f8;color:#20394b;font:18px/1.7 system-ui,sans-serif}}main{{padding:30px max(20px,8vw)}}button{{font:inherit;padding:8px 15px}}small{{color:#3d5463}}</style>
{nav(active)}<main><small>{RELEASE}</small><h1>等待摄像头与识别服务</h1>
<p role=status>{escape(msg)}</p><p>接好摄像头后，页面会自动打开。若是 CSI 排线，请先关闭树莓派再接线。<br>数据保存在这台树莓派。准备期间不会登记或保存影像。</p>
<button onclick=location.reload()>立即检查</button></main><script>
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


GATE = r'''<!doctype html><html lang=zh-CN><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1">
<title>放掌验证</title><style>
*{box-sizing:border-box}body{margin:0;color:#dae8f8;background:#101c28;font:18px/1.5 system-ui,sans-serif} main{max-width:1150px;margin:auto;padding:28px max(18px,4vw);display:grid;grid-template-columns:1.4fr 1fr;align-items:center;gap:24px}
figure{position:relative;margin:0;aspect-ratio:4/3;background:#090e16;border-radius:17px;overflow:hidden} img{display:block;width:100%;height:100%;object-fit:contain}
.guide{position:absolute;inset:12% 24%;border:2px dashed #bbddf999;border-radius:30%;pointer-events:none} h1{font-size:clamp(28px,4vw,50px);margin:6px 0 10px}small{color:#a6bdd2;letter-spacing:.07em} p{min-height:2.8em} button{background:#26435d;color:#fff;border:1px solid #6e8faa;border-radius:10px;padding:10px 16px;font:inherit;cursor:pointer}.ok h1{color:#73e2bc}.warn h1{color:#ffd393}#timing{font-size:14px;color:#a6bdd2}
@media(max-width:760px){main{grid-template-columns:1fr}figure{max-height:43vh}}
</style><body>
<main><figure><img id="live" alt="相机画面"><div class="guide"></div></figure>
<section id="box"><small>连续预览 · 合格时自动验证一次</small><h1 id="title">正在准备</h1><p id="hint" role="status" aria-live="polite">等待相机和登记资料。</p><p id="timing"></p><button id="pause">暂停识别</button></section></main>
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
 show('正在验证','稳住手掌，直到结果出现。');
 try{const result=await(await req('/api/gate/identify',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'},15000)).json();
 if(id!==epoch)return;const sec=((performance.now()-t)/1000).toFixed(2);
 byId('timing').textContent='本次浏览器请求 '+sec+' 秒（不含等手进入画面）';
 if(result.status==='MATCH')show('验证通过',(result.display_name||'已登记的掌纹')+'。请移开手掌。','ok');
 else if(result.status==='UNKNOWN')show('未通过','未识别到已登记手掌。移开后可重试。','warn');
 else show('本次未完成','请移开手掌、调整距离，再放回重试。','warn');
 }catch(_){if(id===epoch)show('验证未返回','移开手掌后重试；请勿连续点击。','warn')}
 finally{busy=false}
}
async function status(){try{
 if(!document.hidden&&!paused){
  const d=await(await req('/api/status')).json();
  const state=d.demo_quality_status??d.quality_status, fresh=d.camera_ready&&d.roi_status_fresh===true;
  const enough=Number(d.demo_quality_consecutive_frames??d.quality_consecutive_frames??0)>=Number(d.demo_quality_required_frames??d.quality_required_frames??5);
  if(!busy){
   if(!fresh){emptySince=null;seenSince=null;show('等待相机','没有可用的新画面，请检查相机连接。','warn')}
   else if(users===null){show('读取登记资料','正在等待登记信息。')}
   else if(users===0){show('请先登记','从上方选「掌纹登记」，完成五张后再回来。')}
   else if(!armed){if(state==='NO_HAND'){emptySince??=performance.now();if(performance.now()-emptySince>=700){armed=true;emptySince=null;seenSince=null;byId('timing').textContent='';show('请放手掌','手心朝镜头，完整伸进画框。')}}else emptySince=null;}
   else if(state==='READY'&&enough) void identify();
   else if(state==='NO_HAND'){seenSince=null;show('请放手掌','手心朝镜头，完整伸进画框。')}
   else {seenSince??=performance.now();if(performance.now()-seenSince>8000){armed=false;emptySince=null;show('等不到合格掌区','移开手掌，调整光线和距离后再试。','warn')}else show('请稳住手掌','整个手掌放进画面；太近或模糊时稍微后退。')}
  }
 }
}catch(_){if(!busy&&!paused)show('暂时无法读取状态','正在等待本机服务恢复。','warn')}finally{setTimeout(status,300)}}
byId('pause').onclick=()=>{epoch++;paused=!paused;byId('pause').textContent=paused?'继续验证':'暂停识别';armed=!paused;emptySince=null;seenSince=null;
 show(paused?'验证已暂停':'请放手掌',paused?'点击继续后开始。':'手心朝向镜头，完整伸进画框。')};
loadUsers();preview();status();
</script></body></html>'''


def render(html, selected):
    if selected == "/enroll":
        from enrollment_review import PANEL
        html = html.replace("</body>", PANEL + "</body>", 1)
        html = html.replace("继续采集</button>", "继续采集 / 补拍</button>", 1)
        html = html.replace("系统会自动筛选五张合格掌区并保存。", "系统会自动挑选五个有效掌区。放大检查，不合适的可以先删除再补拍，确认后才保存。", 1)
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
        html = html.replace("候选池凑齐后会自动选 ${required} 张保存。", "候选池会自动选出 ${required} 张供预览，确认后才保存。")
        html = html.replace("正在保存。${elapsed}", "请检查原图和 ROI，再确认保存。${elapsed}")
        html = html.replace("正在核实上次自动保存；若服务端仍显示待保存，系统会安全续存。", "请确认是否已保存；本页不会自动提交。")
        html = html.replace("已恢复未完成的录入；预览就绪后将继续自动采集，也可手动继续或取消。", "已恢复本次录入；已选候选会保留，补拍只补缺额。")
        html = html.replace("掌纹支付 · 基础演示", "登记手掌", 1)
        html = html.replace("<h2>2. 模拟支付</h2>", '<h2>登记后</h2><p><a href="/gate">前往放掌验证 →</a></p><h2 hidden>旧版监督演示</h2>', 1)
        html = html.replace('<p>演示商品 · MOP 20.00</p>', "", 1)
        html = html.replace('id="identify"', 'id="identify" hidden', 1)
        html = html.replace("先录入，再拍照识别。", "选择左／右手。全程只放同一只手。最多 60 秒，自动选出最好的五张供检查，不用连按拍照。")
        html = html.replace("const GATE_MODE=new URLSearchParams(location.search).get('mode')==='gate'", "const GATE_MODE=true", 1)
        html = html.replace("async function preview(){", "async function preview(){\n if(document.hidden){setTimeout(preview,400);return;}", 1)
        html = html.replace("收集完成后自动选出 ${required} 张", "目标 ${required} 张；自动挑清晰度较高的有效掌区，不设固定锐度下限", 1)
    elif selected == "/gate":
        html = GATE
    elif selected == "/collect":
        html = html.replace("开始十张采集", "开始一组补拍", 1)
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
                raise failure_class("ROI_NOT_READY", "未等到新的合格帧，请移开手掌后重试。")
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
                        return send(self, '{"message":"仅限本站本次登记。"}', 403, "application/json")
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 1 <= size <= 4096 or self.headers.get_content_type() != "application/json":
                        raise ValueError("请求格式不正确。")
                    payload = json.loads(self.rfile.read(size))
                    if not isinstance(payload, dict) or not isinstance(payload.get("token"), str):
                        raise ValueError("本次登记已失效。")
                    frame = payload.get("frame")
                    if path.endswith("remove") and type(frame) is not int:
                        raise ValueError("请选择这次登记的一张照片。")
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
                    return send(self, json.dumps(enrollment_best_frame.ranking_status(application.status())), mime="application/json")
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
                return send(self, stand_by(selected, "当前没有可用摄像头，或识别服务正在恢复。"))
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
