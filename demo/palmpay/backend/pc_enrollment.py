"""Operator-controlled enrollment through the existing local camera station."""
import hmac
import json
import time

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from . import main as service
from .models import PalmEnrollment, User

router = APIRouter(prefix="/api/merchant/enrollments", dependencies=[Depends(service.merchant)])


@router.post("/customers", status_code=201)
def create_customer(data: service.Registration):
    return service.register(data, Response())


class EnrollmentStart(service.Credentials):
    hand: str
    capture_consent: bool


def pending(db, uid):
    palm = db.get(PalmEnrollment, uid)
    service.require(palm and palm.pending_identity and palm.pairing_code and palm.expires_at
                    and palm.expires_at > time.time(), 409, "Enrollment expired. Sign in again at the counter.")
    return palm


@router.post("")
def prepare(data: EnrollmentStart):
    if not isinstance(service.provider, service.MockAuthorizationProvider):
        service.station_provider()
    else:
        service.demo_enabled()
    service.require(data.hand in ("left", "right") and data.capture_consent, 422,
                    "Choose a hand and confirm the customer's capture consent.")
    with service.write() as db:
        user = db.scalar(service.select(User).where(User.email == data.email.lower()))
        salt, expected = user.password.split(":") if user else ("00" * 16, "0" * 128)
        valid = hmac.compare_digest(service.password_hash(data.password, salt), expected)
        service.require(user and valid, 401, "Incorrect customer email or password.")
        palm = db.get(PalmEnrollment, user.id)
        service.require(not service.active_enrollment(palm, isinstance(service.provider, service.StationProvider)), 409, "This customer already has a registered palm.")
        if not palm:
            palm = PalmEnrollment(user_id=user.id, hand=data.hand)
            db.add(palm)
        # Preserve an existing capture session on reconnect or a retried request.
        if not (palm.pending_identity and palm.pairing_code and len(palm.pairing_code) == 32
                and palm.expires_at and palm.expires_at > time.time()):
            palm.pending_identity = "pp_" + service.new_id()
            palm.pairing_code = service.new_id()
            palm.expires_at = int(time.time()) + 1800
            palm.hand = data.hand
        service.require(palm.hand == data.hand, 409, "Resume the original hand or cancel that enrollment first.")
        user.consent = True
        service.audit(db, "counter_capture_consent", user.id)
        return {"id": user.id, "name": user.name, "hand": palm.hand}


@router.post("/{uid}/simulate")
def simulated_counter_enrollment(uid: str):
    service.demo_enabled()
    with service.write() as db:
        palm = db.get(PalmEnrollment, uid)
        if service.active_enrollment(palm, False):
            return {"ok": True}
        palm = pending(db, uid)
        palm.identity = service.new_id()
        palm.pending_identity = palm.pairing_code = palm.expires_at = None
        service.audit(db, "simulated_counter_enrollment", uid)
    return {"ok": True}


@router.get("/{uid}")
def enrollment_status(uid: str):
    with service.Session() as db:
        palm = db.get(PalmEnrollment, uid)
        enrolled = bool(service.active_enrollment(palm, isinstance(service.provider, service.StationProvider)))
        identity = palm.pending_identity if palm and palm.expires_at and palm.expires_at > time.time() else None
    if not enrolled and identity and isinstance(service.provider, service.StationProvider):
        try:
            saved = service.provider.enrolled(identity)
        except service.StationUnavailable:
            raise HTTPException(503, "Cannot confirm the saved enrollment. Reconnect to the camera station.")
        if saved:
            with service.write() as db:
                current = pending(db, uid)
                service.require(current.pending_identity == identity, 409, "Enrollment changed. Refresh the counter.")
                current.identity = identity
                current.pending_identity = current.pairing_code = current.expires_at = None
                service.audit(db, "counter_enrollment_recovered", uid)
                enrolled = True
    return {"enrolled": enrolled}


@router.get("/{uid}/station/{path:path}", include_in_schema=False)
@router.post("/{uid}/station/{path:path}", include_in_schema=False)
async def station_proxy(uid: str, path: str, request: Request):
    station = service.station_provider()
    allowed_get = {"", "frame.jpg", "api/station/enroll-status"}
    allowed_post = {"api/demo/enroll/" + action for action in ("start", "status", "step", "commit", "cancel")}
    allowed_post |= {"api/station/" + action for action in (
        "enroll-review", "enroll-remove", "enroll-refill", "enroll-stop", "enroll-select", "enroll-image", "camera-sleep")}
    service.require(path in (allowed_get if request.method == "GET" else allowed_post), 404, "Unknown enrollment action.")
    with service.Session() as db:
        palm = pending(db, uid)
        token, identity, hand = palm.pairing_code, palm.pending_identity, palm.hand
    payload = None
    if request.method == "POST":
        body = await request.body()
        service.require(len(body) <= 4096, 413, "Request too large.")
        try:
            payload = json.loads(body)
        except ValueError:
            raise HTTPException(422, "Invalid enrollment request.")
        service.require(isinstance(payload, dict), 422, "Invalid enrollment request.")
        payload["token"] = token
        if path.endswith("/start"):
            payload.update(user_id=identity, display_name=identity, hand=hand)
        if path.endswith("/commit"):
            payload["confirm_hand"] = hand
    try:
        async with httpx.AsyncClient(base_url=str(station.client.base_url), timeout=45, trust_env=False) as client:
            result = await client.request(request.method, "/enroll" if not path else "/" + path, json=payload)
            if path.endswith("/commit") and result.is_success:
                # Saving may have completed even if the previous HTTP reply was lost.
                users = await client.get("/api/demo/users")
                users.raise_for_status()
                exists = any(user.get("user_id") == identity and not user.get("needs_reenrollment")
                             for user in users.json().get("users", []))
                service.require(exists, 409, "The station has not saved a valid template yet.")
                with service.write() as db:
                    current = pending(db, uid)
                    service.require(current.pending_identity == identity, 409, "Enrollment changed. Refresh the counter.")
                    current.identity = identity
                    current.pending_identity = current.pairing_code = current.expires_at = None
                    service.audit(db, "counter_enrollment_linked", uid)
            if path.endswith("/cancel") and result.is_success:
                with service.write() as db:
                    current = pending(db, uid)
                    current.pending_identity = current.pairing_code = current.expires_at = None
    except httpx.HTTPError:
        raise HTTPException(503, "Camera station unavailable. Check the connection and retry.")
    if not path and result.is_success:
        prefix = f"/api/merchant/enrollments/{uid}/station"
        html = result.text.replace("'/api/", "'" + prefix + "/api/")
        html = html.replace("'/frame.jpg'", "'" + prefix + "/frame.jpg'")
        html = html.replace("'fypFpnEnrollment'", json.dumps("counterPalm_" + uid))
        setup = """<style>
nav{display:none!important}#form label:has(input){display:none!important}
body{margin:0;background:#f7f8f5!important;color:#111513!important;font-family:Arial,sans-serif!important}
button{background:#08734f!important;border-color:#08734f!important;border-radius:10px!important}
button.secondary{background:white!important;color:#08734f!important}
.panel,.card{border-color:#dde4dc!important}
</style>
<script>window.addEventListener('DOMContentLoaded',()=>{const f=document.getElementById('form');
const values=VALUES;for(const [key,value] of Object.entries(values)){f.elements[key].value=value;}
f.elements.hand.disabled=true;
});</script>""".replace("VALUES", json.dumps({"user_id": identity, "display_name": identity, "hand": hand}))
        html = html.replace("</head>", setup + "</head>")
        return Response(html, media_type="text/html", headers={"Cache-Control": "no-store"})
    return Response(result.content, status_code=result.status_code,
                    media_type=result.headers.get("content-type", "application/json"),
                    headers={"Cache-Control": "no-store"})
