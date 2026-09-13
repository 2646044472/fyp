#!/usr/bin/env python3
"""Local-only browser surface for the Phase 1 simulated palm payment demo."""

from __future__ import annotations

import argparse
import json
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import palm_demo
from biometric import load_fastcc
from camera import CameraFeed
from gallery import Gallery, load_policy
from payment import PaymentService
from roi import AutomaticPalmROI, FixedGuideROI
from templates import TemplateStore, safe_user_id
from workflow import PalmPaymentWorkflow


HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palm Payment</title><style>body{font:16px system-ui,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#17202a;background:#f5f7fa}main{background:#fff;border:1px solid #dce3ea;border-radius:14px;padding:20px;box-shadow:0 2px 8px #0001}.preview{background:#111;border-radius:10px;overflow:hidden}.preview img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}button{font:inherit;padding:12px 18px;border:0;border-radius:8px;background:#1769aa;color:#fff;cursor:pointer}.notice{white-space:pre-wrap;background:#eef3f7;padding:14px;border-radius:8px;min-height:48px;margin:14px 0}.small{color:#53616d;font-size:.9rem}</style></head><body><main><h1>PALM PAYMENT</h1><div class="preview"><img src="/stream" alt="live camera"></div><p>Place your palm inside the guide</p><p>Item: Demo Purchase<br>Amount: MOP 20.00</p><label class="small"><input id="consent" type="checkbox"> I have approval and participant consent for this local biometric demo.</label><p><button id="pay">PAY WITH PALM</button></p><div id="notice" class="notice">Place your palm</div></main><script>const notice=document.getElementById('notice');document.getElementById('pay').onclick=async()=>{if(!document.getElementById('consent').checked){notice.textContent='Approval/consent is required.';return}notice.textContent='Identifying...';try{const r=await fetch('/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount_cents:2000,request_id:crypto.randomUUID(),consent:true})});const d=await r.json();notice.textContent=d.message||JSON.stringify(d)}catch(e){notice.textContent='Unable to complete payment.'}};</script></body></html>"""

ADMIN_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palm Payment Admin</title></head><body><h1>Palm Payment Admin</h1><p>This local route is for authorized enrollment and account administration.</p><form id="enroll"><input name="user_id" placeholder="user ID" required><input name="display_name" placeholder="display name" required><input name="initial_balance_cents" type="number" value="10000" min="0"><button>Enroll current palm</button></form><form id="topup"><input name="user_id" placeholder="user ID" required><input name="amount_cents" type="number" value="10000" min="1"><button>Top up</button></form><pre id="out"></pre><script>const out=document.getElementById('out');async function send(form,url){const data=Object.fromEntries(new FormData(form));data.consent=true;const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});out.textContent=JSON.stringify(await r.json(),null,2)}document.getElementById('enroll').onsubmit=e=>{e.preventDefault();send(e.target,'/api/admin/enroll')};document.getElementById('topup').onsubmit=e=>{e.preventDefault();send(e.target,'/api/admin/topup')};</script></body></html>"""


class PalmPaymentApp:
    def __init__(self, camera: CameraFeed, workflow: PalmPaymentWorkflow, payments: PaymentService) -> None:
        self.camera = camera
        self.workflow = workflow
        self.payments = payments

    def enroll(self, payload: dict[str, Any]) -> None:
        if not payload.get("consent"):
            raise ValueError("Approval/consent is required.")
        user_id = safe_user_id(str(payload.get("user_id", "")))
        display_name = str(payload.get("display_name", user_id)).strip()
        initial = int(payload.get("initial_balance_cents", 0))
        captures = [self.camera.frame() for _ in range(max(1, int(payload.get("samples", 5))))]
        self.workflow.enroll_user(user_id, display_name, captures, initial)


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, sort_keys=True).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(app: PalmPaymentApp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _payload(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length) or b"{}")

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/":
                body = HTML.encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/admin":
                body = ADMIN_HTML.encode()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/stream":
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
            elif path == "/api/admin/users":
                json_response(self, HTTPStatus.OK, {"users": app.payments.list_users()})
            elif path == "/api/admin/transactions":
                json_response(self, HTTPStatus.OK, {"transactions": app.payments.list_transactions()})
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                payload = self._payload()
                if path == "/api/checkout":
                    if not payload.get("consent"):
                        raise ValueError("Approval/consent is required.")
                    amount = int(payload.get("amount_cents", 2000))
                    result = app.workflow.checkout(None, amount, str(payload.get("request_id") or uuid.uuid4()))
                    display_name = app.payments.display_name_for(result.user_id) if result.user_id else result.user_id
                    messages = {"SUCCESS": f"Payment successful\nWelcome, {display_name}\nMOP {amount / 100:.2f} paid\nBalance: MOP {result.balance_cents / 100:.2f}", "UNKNOWN_USER": "Palm not recognised\nNo payment was made", "RETRY": "Unable to read palm\nPlease reposition your hand and try again", "INSUFFICIENT_BALANCE": "Payment declined\nInsufficient simulated balance", "FAILURE": "Payment failed"}
                    json_response(self, HTTPStatus.OK, {"status": result.status, "message": messages[result.status], "result": result.__dict__})
                elif path == "/api/admin/enroll":
                    app.enroll(payload)
                    json_response(self, HTTPStatus.OK, {"message": "Enrollment complete"})
                elif path == "/api/admin/topup":
                    user_id = safe_user_id(str(payload["user_id"]))
                    amount = int(payload["amount_cents"])
                    current = app.payments.balance_for(user_id)
                    if current is None or amount <= 0:
                        raise ValueError("valid user and positive amount are required")
                    app.payments.top_up(user_id, amount)
                    json_response(self, HTTPStatus.OK, {"message": "Balance updated", "balance_cents": current + amount})
                else:
                    json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})
            except Exception as error:
                json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})

        def do_DELETE(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            prefix = "/api/admin/users/"
            if path.startswith(prefix):
                try:
                    app.workflow.delete_user(safe_user_id(path[len(prefix):]))
                    json_response(self, HTTPStatus.OK, {"message": "User deleted"})
                except Exception as error:
                    json_response(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def build_app(args: argparse.Namespace) -> PalmPaymentApp:
    policy = load_policy(palm_demo.RUNTIME / "identification_policy.json")
    algorithm = load_fastcc(args.baseline_path)
    store = TemplateStore(palm_demo.RUNTIME / "templates")
    gallery = Gallery(store, algorithm, policy["threshold"], policy["min_margin"])
    payments = PaymentService(palm_demo.RUNTIME / "palm_payment.sqlite3")
    roi = FixedGuideROI(palm_demo.DEFAULT_CROP, args.min_contrast) if args.roi_mode == "fixed" else AutomaticPalmROI()
    camera = CameraFeed(args.camera, args.width, args.height)
    workflow = PalmPaymentWorkflow(roi, algorithm, gallery, payments, capture_profile=policy["capture_profile"], logger=palm_demo.write_log, capture=camera.frame)
    return PalmPaymentApp(camera, workflow, payments)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-only simulated palm payment UI")
    parser.add_argument("--baseline-path", type=Path, default=palm_demo.DEFAULT_BASELINE)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--roi-mode", choices=("fixed", "auto"), default="auto")
    parser.add_argument("--min-contrast", type=float, default=12.0)
    args = parser.parse_args()
    app = build_app(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    print(f"Palm payment UI: http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app.camera.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
