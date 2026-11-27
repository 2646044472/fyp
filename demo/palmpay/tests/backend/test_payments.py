from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend import main, seed
from backend.db import Base
from backend.models import LedgerEntry, Wallet

def key():
    return {"Idempotency-Key": uuid4().hex}

@pytest.fixture
def setup(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(main, "Session", session)
    monkeypatch.setattr(seed, "Session", session)
    monkeypatch.setattr(main, "DEMO", True)
    monkeypatch.setattr(main, "provider", main.MockAuthorizationProvider())
    monkeypatch.setattr(main, "OPERATOR_KEY", "test-operator")
    with TestClient(main.app) as operator, TestClient(main.app) as customer:
        assert operator.post("/api/merchant/session", json={"key": "test-operator"}).status_code == 200
        assert customer.post("/api/auth/register", json={"name": "Lena", "email": "lena@example.test",
                             "password": "testing-password", "consent": True}).status_code == 201
        pair = customer.post("/api/palm/pairing", json={"hand": "left"}).json()
        assert operator.post("/api/dev/enroll", json={"code": pair["code"]}).status_code == 200
        yield operator, customer, session
    engine.dispose()

def order_and_intent(operator, quantity=1):
    response = operator.post("/api/merchant/orders", headers=key(),
                             json={"items": [{"product_id": "iced-latte", "quantity": quantity}]})
    assert response.status_code == 200, response.text
    order = response.json()
    response = operator.post("/api/payments", headers=key(), json={"order_id": order["id"]})
    assert response.status_code == 200, response.text
    return order, response.json()

def approve(operator, intent):
    return operator.post(f"/api/dev/payments/{intent['id']}/simulate",
                         json={"email": "lena@example.test"}).json()

def test_concurrent_approvals_emit_one_receipt_and_ledger_pair(setup):
    operator, customer, session = setup
    _, intent = order_and_intent(operator)
    assert intent["amount"] == 2500
    with customer.websocket_connect("/ws/events?role=wallet", headers={"origin":"http://testserver"}) as events:
        assert events.receive_json() == {"type": "refresh"}
        with ThreadPoolExecutor(max_workers=2) as pool:
            one, two = list(pool.map(lambda _: approve(operator, intent), range(2)))
        assert events.receive_json() == {"type": "refresh"}
    assert one == two and one["status"] == "paid"
    assert customer.get("/api/wallet").json()["balance"] == 47500
    assert customer.get("/api/wallet/transactions").json() == [one]
    assert operator.get(f"/api/payments/{intent['id']}").json() == one
    with session() as db:
        assert db.get(Wallet, "cklc").balance == 2500
        assert sorted(db.scalars(select(LedgerEntry.amount).where(LedgerEntry.reference == one["reference"]))) == [-2500, 2500]

def test_insufficient_funds_then_retry(setup):
    operator, customer, _ = setup
    order, intent = order_and_intent(operator, 21)
    assert approve(operator, intent)["reason"] == "Insufficient wallet funds."
    assert customer.get("/api/wallet").json()["balance"] == 50000
    topup_key = key()
    for _ in range(2):
        assert customer.post("/api/wallet/demo-topup", headers=topup_key).json()["balance"] == 60000
    retry = operator.post("/api/payments", headers=key(), json={"order_id": order["id"]}).json()
    assert retry["id"] != intent["id"]
    assert approve(operator, retry)["status"] == "paid"
    assert customer.get("/api/wallet").json()["balance"] == 7500

def test_cancel_and_expiry(setup, monkeypatch):
    operator, customer, _ = setup
    order, intent = order_and_intent(operator)
    assert operator.post(f"/api/payments/{intent['id']}/cancel").json()["status"] == "cancelled"
    assert approve(operator, intent)["status"] == "cancelled"
    assert operator.post("/api/payments", headers=key(), json={"order_id": order["id"]}).status_code == 409
    monkeypatch.setattr(main, "TTL", 0)
    _, intent = order_and_intent(operator)
    assert approve(operator, intent)["status"] == "expired"
    assert customer.get("/api/wallet").json()["balance"] == 50000

def test_customer_cannot_authorize_and_mock_is_disabled_outside_demo(setup, monkeypatch):
    operator, customer, _ = setup
    _, intent = order_and_intent(operator)
    endpoint = f"/api/dev/payments/{intent['id']}/simulate"
    assert customer.post(endpoint, json={"email": "lena@example.test"}).status_code == 401
    assert operator.get("/api/wallet").status_code == 401
    monkeypatch.setattr(main, "DEMO", False)
    assert operator.post(endpoint, json={"email": "lena@example.test"}).status_code == 404
    monkeypatch.setattr(main, "DEMO", True)
    monkeypatch.setattr(main, "provider", None)
    assert operator.post(endpoint, json={"email": "lena@example.test"}).status_code == 404

