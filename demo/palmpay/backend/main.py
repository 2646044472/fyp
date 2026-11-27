import asyncio
import hashlib
import hmac
from io import BytesIO
from urllib.parse import urlsplit
import qrcode
import os
import secrets
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from .authorization.mock import MockAuthorizationProvider
from .authorization.provider import Challenge
from .authorization.station import StationNoMatch, StationProvider, StationUnavailable
from .db import Session
from .models import (AuditEvent, Authorization, LedgerEntry, LoginSession, Order, OrderItem,
                     PalmEnrollment, PaymentIntent, Product, User, Wallet)
from .seed import seed

def new_id():
    return uuid4().hex

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def password_hash(password, salt):
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()

def require(condition, code, detail):
    if not condition:
        raise HTTPException(code, detail)

@contextmanager
def write():
    with Session.begin() as db:
        db.execute(text("BEGIN IMMEDIATE"))
        yield db

@asynccontextmanager
async def lifespan(_):
    seed()
    try:
        yield
    finally:
        if isinstance(provider, StationProvider):
            provider.client.close()

app = FastAPI(title="PalmPay", lifespan=lifespan)
def configured_provider():
    mode = os.getenv("PALMPAY_AUTH_PROVIDER", "mock")
    if mode == "mock":
        return MockAuthorizationProvider()
    if mode == "fpn":
        return StationProvider(os.getenv("PALMPAY_FPN_URL", "http://127.0.0.1:8080"),
                               float(os.getenv("PALMPAY_FPN_THRESHOLD", "nan")))
    raise ValueError("Unknown PALMPAY_AUTH_PROVIDER.")


provider = configured_provider()
OPERATOR_KEY = os.getenv("PALMPAY_OPERATOR_KEY", "")
DEMO = os.getenv("PALMPAY_DEMO", "0") == "1"
TTL = int(os.getenv("PALMPAY_INTENT_TTL", "120"))
TOPUP = 10000
COOKIES = {"wallet": "palm_wallet", "merchant": "palm_merchant"}

class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: str = Field(min_length=8, max_length=128)

class Registration(Credentials):
    name: str = Field(min_length=1, max_length=80)
    consent: bool

class Operator(BaseModel):
    key: str = Field(max_length=256)

class Item(BaseModel):
    product_id: str
    quantity: int = Field(ge=1, le=99)

class OrderInput(BaseModel):
    items: list[Item] = Field(min_length=1, max_length=50)

class IntentInput(BaseModel):
    order_id: str

class PairingInput(BaseModel):
    hand: Literal["left", "right"]
    allow_station_capture: bool = False

class EnrollmentInput(BaseModel):
    code: str

class Simulation(BaseModel):
    email: str = Field(default="", max_length=254)
    outcome: Literal["approve", "decline"] = "approve"

class Preferences(BaseModel):
    locale: Literal["en", "zh-Hant"]
    consent: bool

class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: Literal["Coffee", "Non-coffee"]
    price: int = Field(ge=1, le=1000000)
    available: bool = True

class Line(BaseModel):
    product_id: str
    name: str
    price: int
    quantity: int

class PaymentView(BaseModel):
    id: str
    order_id: str
    merchant: str
    amount: int
    currency: str
    status: str
    reason: str | None
    expires_at: int
    reference: str | None
    paid_at: str | None
    items: list[Line]

class OrderView(BaseModel):
    id: str
    total: int
    status: str
    created_at: str
    items: list[Line]
    payment: PaymentView | None

class RegisterView(BaseModel):
    merchant: str
    terminal: str
    demo: bool
    station: bool

class StationStatus(BaseModel):
    connected: bool
    camera_open: bool = False
    camera_ready: bool = False
    message: str


class WalletView(BaseModel):
    name: str
    email: str
    balance: int
    consent: bool
    locale: str

class PalmView(BaseModel):
    status: str
    method: Literal["mock", "fpn"] = "mock"
    hand: str | None = None
    code: str | None = None
    expires_at: int | None = None

class StationPairing(BaseModel):
    identity: str
    hand: str

class ProductView(ProductInput):
    id: str
    image: str

def session_subject(db, token, role):
    session = db.get(LoginSession, digest(token)) if token else None
    if session and session.role == role and session.expires_at > time.time():
        return session.subject

def authenticate(request, role):
    with Session() as db:
        subject = session_subject(db, request.cookies.get(COOKIES[role]), role)
    require(subject, 401, "Sign in to continue.")
    return subject

def customer(request: Request):
    return authenticate(request, "wallet")

def merchant(request: Request):
    return authenticate(request, "merchant")

def key(value: str = Header(alias="Idempotency-Key", min_length=8, max_length=128)):
    return value

def issue(db, response, role, subject):
    token = secrets.token_urlsafe(32)
    duration = 86400
    db.add(LoginSession(token_hash=digest(token), role=role, subject=subject,
                        expires_at=int(time.time()) + duration))
    response.set_cookie(COOKIES[role], token, httponly=True, samesite="strict",
                        secure=os.getenv("PALMPAY_SECURE_COOKIES") == "1", max_age=duration)

def audit(db, action, subject):
    db.add(AuditEvent(action=action, subject=subject, created_at=now()))

def credit(db, wallet, amount, reference):
    wallet.balance += amount
    db.add(LedgerEntry(wallet_id=wallet.id, reference=reference, amount=amount, created_at=now()))

def lines(db, order_id):
    return [Line.model_validate(item, from_attributes=True) for item in db.scalars(
        select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id))]

def payment_view(db, intent):
    return PaymentView(id=intent.id, order_id=intent.order_id, merchant="CKLC Coffee",
                       amount=intent.amount, currency=intent.currency, status=intent.status,
                       reason=intent.reason, expires_at=intent.expires_at, reference=intent.reference,
                       paid_at=intent.paid_at, items=lines(db, intent.order_id))

def active(intent):
    return intent.status == "awaiting_authorization"

def finish(db, intent, state, reason=None):
    intent.status, intent.reason = state, reason
    db.get(Order, intent.order_id).status = "failed" if state in ("failed", "expired") else state
    audit(db, state, intent.id)

def expire(db, intent):
    if active(intent) and intent.expires_at <= time.time():
        finish(db, intent, "expired", "Authorization expired.")
    return intent

def owned_intent(db, intent_id, merchant_id):
    intent = db.get(PaymentIntent, intent_id)
    require(intent and intent.merchant_id == merchant_id, 404, "Payment not found.")
    return expire(db, intent)

def latest(db, order_id):
    return db.scalar(select(PaymentIntent).where(PaymentIntent.order_id == order_id)
                     .order_by(PaymentIntent.created_at.desc()).limit(1))

def demo_enabled():
    require(DEMO and isinstance(provider, MockAuthorizationProvider), 404, "Demo authorization is unavailable.")

@app.post("/api/auth/register", status_code=201)
def register(data: Registration, response: Response):
    require(data.name.strip(), 422, "Enter your name.")
    require(data.consent, 422, "Review and accept the demo terms.")
    salt = secrets.token_hex(16)
    hashed = password_hash(data.password, salt)
    uid = new_id()
    try:
        with write() as db:
            db.add(User(id=uid, email=data.email.lower(), name=data.name.strip(),
                        password=f"{salt}:{hashed}", consent=True))
            db.flush()
            wallet = Wallet(id=uid, user_id=uid, balance=0)
            db.add(wallet)
            db.flush()
            credit(db, wallet, 50000, "WELCOME")
            issue(db, response, "wallet", uid)
    except IntegrityError:
        raise HTTPException(409, "An account already uses this email.")
    return {"id": uid}

@app.post("/api/auth/login")
def login(data: Credentials, response: Response):
    with Session.begin() as db:
        user = db.scalar(select(User).where(User.email == data.email.lower()))
        salt, expected = user.password.split(":") if user else ("00" * 16, "0" * 128)
        valid = hmac.compare_digest(password_hash(data.password, salt), expected)
        require(valid and user, 401, "Incorrect email or password.")
        issue(db, response, "wallet", user.id)
    return {"ok": True}

@app.post("/api/merchant/session")
def operator(data: Operator, response: Response):
    require(OPERATOR_KEY and hmac.compare_digest(digest(data.key), digest(OPERATOR_KEY)), 401,
            "Incorrect operator access key.")
    with Session.begin() as db:
        issue(db, response, "merchant", "cklc")
    return {"ok": True}

@app.get("/api/wallet-qr")
def wallet_qr(url: str, request: Request, _: str = Depends(merchant)):
    parsed = urlsplit(url)
    require(parsed.scheme in ("http", "https") and parsed.path == "/wallet"
            and not parsed.query and not parsed.fragment
            and parsed.netloc in (request.headers.get("host"), request.headers.get("x-forwarded-host")),
            422, "Invalid wallet URL.")
    image = BytesIO()
    qrcode.make(url).save(image, format="PNG")
    image.seek(0)
    return StreamingResponse(image, media_type="image/png")

@app.get("/api/merchant/session", response_model=RegisterView)
def operator_status(mid: str = Depends(merchant)):
    return {"merchant": "CKLC Coffee", "terminal": "Register 01",
            "demo": DEMO and isinstance(provider, MockAuthorizationProvider),
            "station": isinstance(provider, StationProvider)}

@app.post("/api/auth/logout/{role}")
def logout(role: Literal["wallet", "merchant"], request: Request, response: Response):
    token = request.cookies.get(COOKIES[role])
    if token:
        with write() as db:
            session = db.get(LoginSession, digest(token))
            if session and session.role == role:
                db.delete(session)
    response.delete_cookie(COOKIES[role])
    return {"ok": True}

@app.get("/api/wallet", response_model=WalletView)
def wallet_view(uid: str = Depends(customer)):
    with Session() as db:
        user = db.get(User, uid)
        return WalletView(name=user.name, email=user.email, consent=user.consent,
                          locale=user.locale, balance=db.get(Wallet, uid).balance)

@app.patch("/api/wallet/preferences")
def preferences(data: Preferences, uid: str = Depends(customer)):
    with write() as db:
        user = db.get(User, uid)
        user.locale, user.consent = data.locale, data.consent
        palm = db.get(PalmEnrollment, uid)
        if palm and not data.consent:
            db.delete(palm)
            audit(db, "enrollment_revoked", uid)
    return {"ok": True}

@app.post("/api/wallet/demo-topup")
def topup(request_key: str = Depends(key), uid: str = Depends(customer)):
    with write() as db:
        reference = f"TOPUP-{request_key}"
        if not db.scalar(select(LedgerEntry).where(LedgerEntry.wallet_id == uid, LedgerEntry.reference == reference)):
            credit(db, db.get(Wallet, uid), TOPUP, reference)
    return wallet_view(uid)

@app.get("/api/wallet/transactions", response_model=list[PaymentView])
def transactions(uid: str = Depends(customer)):
    with Session() as db:
        return [payment_view(db, intent) for intent in db.scalars(select(PaymentIntent)
                .where(PaymentIntent.user_id == uid, PaymentIntent.status == "paid")
                .order_by(PaymentIntent.paid_at.desc()))]

def active_enrollment(palm, station):
    return palm and palm.identity and palm.identity.startswith("pp_") == station


@app.get("/api/palm/status", response_model=PalmView)
def palm_status(uid: str = Depends(customer)):
    with Session() as db:
        palm = db.get(PalmEnrollment, uid)
        station = isinstance(provider, StationProvider)
        method = "fpn" if station else "mock"
        if active_enrollment(palm, station):
            return PalmView(status="enrolled", hand=palm.hand, method=method)
        if palm and palm.expires_at and palm.expires_at > time.time():
            return PalmView(status="pairing", hand=palm.hand, code=palm.pairing_code, expires_at=palm.expires_at, method=method)
        return PalmView(status="unregistered", method=method)

@app.post("/api/palm/pairing", response_model=PalmView)
def pairing(data: PairingInput, uid: str = Depends(customer)):
    with write() as db:
        user = db.get(User, uid)
        require(user.consent, 409, "Enable biometric demo consent in Profile first.")
        palm = db.get(PalmEnrollment, uid)
        station = isinstance(provider, StationProvider)
        require(not station or data.allow_station_capture, 422, "Confirm the FPN station capture notice first.")
        require(not active_enrollment(palm, station), 409, "This wallet already has an enrollment.")
        if not palm:
            palm = PalmEnrollment(user_id=uid, hand=data.hand)
            db.add(palm)
        palm.hand = data.hand
        palm.pending_identity = f"pp_{new_id()}" if station else None
        palm.pairing_code = secrets.token_hex(4).upper()
        palm.expires_at = int(time.time()) + (900 if station else 300)
    return palm_status(uid)

@app.post("/api/dev/enroll")
def enroll(data: EnrollmentInput, _: str = Depends(merchant)):
    demo_enabled()
    with write() as db:
        palm = db.scalar(select(PalmEnrollment).where(PalmEnrollment.pairing_code == data.code.strip().upper()))
        require(palm and palm.expires_at and palm.expires_at > time.time(), 404, "Pairing code expired or invalid.")
        palm.identity, palm.pairing_code, palm.expires_at = new_id(), None, None
        palm.pending_identity = None
        audit(db, "simulated_enrollment", palm.user_id)
    return {"ok": True}

def station_provider():
    require(isinstance(provider, StationProvider), 404, "FPN authorization is disabled.")
    return provider


def pending_station_pairing(db, code):
    palm = db.scalar(select(PalmEnrollment).where(PalmEnrollment.pairing_code == code.strip().upper()))
    require(palm and palm.pending_identity and palm.expires_at and palm.expires_at > time.time()
            and db.get(User, palm.user_id).consent, 404, "Pairing code expired or invalid.")
    return StationPairing(identity=palm.pending_identity, hand=palm.hand)


@app.get("/api/station/status", response_model=StationStatus)
def station_status(_: str = Depends(merchant)):
    station = station_provider()
    try:
        health = station.health()
        ready = health.get("camera_ready") is True
        opened = health.get("camera_open") is True
        return StationStatus(connected=True, camera_open=opened, camera_ready=ready,
                             message="Camera ready" if ready else "Camera starting" if opened else "Station connected · camera on standby")
    except StationUnavailable as error:
        return StationStatus(connected=False, message=str(error))


@app.post("/api/station/pairing", response_model=StationPairing)
def station_pairing(data: EnrollmentInput, _: str = Depends(merchant)):
    station_provider()
    with Session() as db:
        return pending_station_pairing(db, data.code)


@app.post("/api/station/enroll")
def station_enroll(data: EnrollmentInput, _: str = Depends(merchant)):
    station = station_provider()
    with Session() as db:
        pairing = pending_station_pairing(db, data.code)
    try:
        enrolled = station.enrolled(pairing.identity)
    except StationUnavailable as error:
        raise HTTPException(503, str(error)) from error
    require(enrolled, 409, "Save the palm enrollment in FPN + C E10 first.")
    with write() as db:
        current = pending_station_pairing(db, data.code)
        require(current == pairing, 409, "Generate a new pairing code.")
        palm = db.scalar(select(PalmEnrollment).where(PalmEnrollment.pending_identity == pairing.identity))
        palm.identity = pairing.identity
        palm.pending_identity = palm.pairing_code = palm.expires_at = None
        audit(db, "station_enrollment_linked", palm.user_id)
    return {"ok": True}


@app.get("/api/merchant/products", response_model=list[ProductView])
def products(mid: str = Depends(merchant)):
    with Session() as db:
        return db.scalars(select(Product).where(Product.merchant_id == mid).order_by(Product.name)).all()

@app.post("/api/merchant/products", response_model=ProductView)
def add_product(data: ProductInput, mid: str = Depends(merchant)):
    with write() as db:
        product = Product(id=new_id(), merchant_id=mid, **data.model_dump())
        db.add(product)
    return product

@app.put("/api/merchant/products/{product_id}", response_model=ProductView)
def update_product(product_id: str, data: ProductInput, mid: str = Depends(merchant)):
    with write() as db:
        product = db.get(Product, product_id)
        require(product and product.merchant_id == mid, 404, "Product not found.")
        for field, value in data.model_dump().items():
            setattr(product, field, value)
    return product

def order_view(db, order):
    intent = latest(db, order.id)
    payment = payment_view(db, expire(db, intent)) if intent else None
    return OrderView(id=order.id, total=order.total, status=order.status, created_at=order.created_at,
                     items=lines(db, order.id), payment=payment)

@app.post("/api/merchant/orders", response_model=OrderView)
def create_order(data: OrderInput, request_key: str = Depends(key), mid: str = Depends(merchant)):
    with write() as db:
        existing = db.scalar(select(Order).where(Order.request_key == f"{mid}:{request_key}"))
        requested = {item.product_id: item.quantity for item in data.items}
        require(len(requested) == len(data.items), 422, "Send one line per product.")
        if existing:
            require({line.product_id: line.quantity for line in lines(db, existing.id)} == requested,
                    409, "This order key was already used for different items.")
            return order_view(db, existing)
        order = Order(id=new_id(), merchant_id=mid, total=0, created_at=now(),
                      request_key=f"{mid}:{request_key}")
        snapshots = []
        for item in data.items:
            product = db.get(Product, item.product_id)
            require(product and product.merchant_id == mid and product.available, 409, "A product is unavailable.")
            order.total += product.price * item.quantity
            snapshots.append(OrderItem(order_id=order.id, product_id=product.id, name=product.name,
                                       price=product.price, quantity=item.quantity))
        db.add(order)
        db.flush()
        db.add_all(snapshots)
        db.flush()
        return order_view(db, order)

@app.get("/api/merchant/orders", response_model=list[OrderView])
def orders(mid: str = Depends(merchant)):
    with write() as db:
        return [order_view(db, order) for order in db.scalars(select(Order)
                .where(Order.merchant_id == mid).order_by(Order.created_at.desc()))]

@app.post("/api/payments", response_model=PaymentView)
def create_payment(data: IntentInput, request_key: str = Depends(key), mid: str = Depends(merchant)):
    with write() as db:
        existing = db.scalar(select(PaymentIntent).where(PaymentIntent.request_key == f"{mid}:{request_key}"))
        if existing:
            require(existing.order_id == data.order_id, 409, "This payment key belongs to a different order.")
            return payment_view(db, expire(db, existing))
        order = db.get(Order, data.order_id)
        require(order and order.merchant_id == mid, 404, "Order not found.")
        require(order.status not in ("paid", "cancelled"), 409, "This order is already closed.")
        current = latest(db, order.id)
        if current and active(expire(db, current)):
            return payment_view(db, current)
        intent = PaymentIntent(id=new_id(), order_id=order.id, merchant_id=mid, amount=order.total,
                               created_at=now(), expires_at=int(time.time()) + TTL,
                               request_key=f"{mid}:{request_key}")
        order.status = "pending"
        db.add(intent)
        db.flush()
        audit(db, "awaiting_authorization", intent.id)
        return payment_view(db, intent)

@app.get("/api/payments/{intent_id}", response_model=PaymentView)
def payment(intent_id: str, mid: str = Depends(merchant)):
    with write() as db:
        return payment_view(db, owned_intent(db, intent_id, mid))

@app.post("/api/payments/{intent_id}/cancel", response_model=PaymentView)
def cancel(intent_id: str, mid: str = Depends(merchant)):
    with write() as db:
        intent = owned_intent(db, intent_id, mid)
        require(intent.status != "paid", 409, "A paid order cannot be cancelled.")
        if active(intent) or (intent.status in ("failed", "expired") and latest(db, intent.order_id).id == intent.id):
            finish(db, intent, "cancelled", "Cancelled by the operator.")
        return payment_view(db, intent)

def settle(db, intent, result, challenge):
    require(result.challenge == challenge, 409, "Authorization does not match the payment.")
    if not active(expire(db, intent)):
        return
    order = db.get(Order, intent.order_id)
    require(order.status == "pending" and order.total == intent.amount, 409, "Order is no longer payable.")
    palm = db.scalar(select(PalmEnrollment).where(PalmEnrollment.identity == result.identity))
    if not active_enrollment(palm, result.hand is not None) or not db.get(User, palm.user_id).consent or (
            result.hand is not None and result.hand != palm.hand):
        finish(db, intent, "failed", "No linked wallet matches this palm enrollment.")
        return
    db.add(Authorization(intent_id=intent.id, merchant_id=challenge.merchant_id, amount=challenge.amount,
                         currency=challenge.currency, expires_at=challenge.expires_at, identity=result.identity))
    wallet = db.get(Wallet, palm.user_id)
    if wallet.balance < intent.amount:
        finish(db, intent, "failed", "Insufficient wallet funds.")
        return
    intent.user_id, intent.paid_at = palm.user_id, now()
    intent.reference = f"PP-{intent.id.upper()}"
    credit(db, wallet, -intent.amount, intent.reference)
    credit(db, db.get(Wallet, intent.merchant_id), intent.amount, intent.reference)
    finish(db, intent, "paid")

@app.post("/api/dev/payments/{intent_id}/simulate", response_model=PaymentView)
def simulate(intent_id: str, data: Simulation, mid: str = Depends(merchant)):
    demo_enabled()
    with write() as db:
        intent = owned_intent(db, intent_id, mid)
        if active(intent):
            user = db.scalar(select(User).where(User.email == data.email.strip().lower()))
            palm = db.get(PalmEnrollment, user.id) if user else None
            if data.outcome == "decline":
                finish(db, intent, "failed", "Demo authorization declined.")
            elif not palm or not palm.identity or not user.consent:
                finish(db, intent, "failed", "No simulated enrollment matches this wallet.")
            else:
                challenge = Challenge(intent.id, mid, intent.amount, intent.currency, intent.expires_at)
                settle(db, intent, provider.authorize(challenge, palm.identity), challenge)
        return payment_view(db, intent)

@app.post("/api/station/payments/{intent_id}/authorize", response_model=PaymentView)
def station_authorize(intent_id: str, mid: str = Depends(merchant)):
    station = station_provider()
    with write() as db:
        intent = owned_intent(db, intent_id, mid)
        if not active(intent):
            return payment_view(db, intent)
        challenge = Challenge(intent.id, mid, intent.amount, intent.currency, intent.expires_at)
    def should_cancel():
        with Session() as db:
            current = db.get(PaymentIntent, intent_id)
            return not current or not active(current) or current.expires_at <= time.time()

    result, reason = None, None
    try:
        result = station.authorize(challenge, should_cancel)
    except StationUnavailable as error:
        raise HTTPException(503, str(error)) from error
    except StationNoMatch as error:
        reason = str(error)
    with write() as db:
        intent = owned_intent(db, intent_id, mid)
        if active(intent):
            if result:
                settle(db, intent, result, challenge)
            else:
                finish(db, intent, "failed", reason)
        return payment_view(db, intent)


def event_cursor(token, role):
    with Session() as db:
        subject = session_subject(db, token, role)
        if not subject:
            return None
        if role == "wallet":
            ledger = db.scalar(select(LedgerEntry.id).where(LedgerEntry.wallet_id == subject)
                               .order_by(LedgerEntry.id.desc()).limit(1))
            palm = db.get(PalmEnrollment, subject)
            return (ledger, palm.identity if palm else None)
        return db.scalar(select(AuditEvent.id).order_by(AuditEvent.id.desc()).limit(1)) or 0

@app.websocket("/ws/events")
async def events(socket: WebSocket):
    role = socket.query_params.get("role")
    origin = socket.headers.get("origin")
    host = socket.headers.get("host")
    forwarded = socket.headers.get("x-forwarded-host", host)
    if role not in COOKIES or origin not in {f"{scheme}://{name}" for scheme in ("http", "https") for name in (host, forwarded)}:
        await socket.close(code=1008)
        return
    token = socket.cookies.get(COOKIES[role])
    if await asyncio.to_thread(event_cursor, token, role) is None:
        await socket.close(code=1008)
        return
    await socket.accept()
    previous = object()
    try:
        while True:
            cursor = await asyncio.to_thread(event_cursor, token, role)
            if cursor is None:
                await socket.close(code=1008)
                return
            if cursor != previous:
                await socket.send_json({"type": "refresh"})
                previous = cursor
            try:
                await asyncio.wait_for(socket.receive_text(), timeout=0.65)
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        pass

from .pc_enrollment import router as enrollment_router
app.include_router(enrollment_router)

dist = Path(__file__).resolve().parents[1] / "dist"
if dist.is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")
    if (dist / "drinks").is_dir():
        app.mount("/drinks", StaticFiles(directory=dist / "drinks"), name="drinks")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        file = dist / path
        if file.is_file() and file.resolve().is_relative_to(dist):
            return FileResponse(file)
        if path == "" or path.split("/")[0] in ("wallet", "merchant"):
            return FileResponse(dist / "index.html")
        raise HTTPException(404)

