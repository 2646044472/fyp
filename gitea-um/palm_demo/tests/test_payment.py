from __future__ import annotations

from payment import PaymentService


def test_payment_deducts_integer_minor_units(tmp_path):
    service = PaymentService(tmp_path / "payments.sqlite3")
    service.create_account("alpha", "Alpha", 10000)

    result = service.pay("alpha", 2000, "request-1")

    assert result.status == "SUCCESS"
    assert result.balance_cents == 8000
    assert service.balance_for("alpha") == 8000


def test_insufficient_balance_does_not_deduct(tmp_path):
    service = PaymentService(tmp_path / "payments.sqlite3")
    service.create_account("alpha", "Alpha", 1000)

    result = service.pay("alpha", 2000, "request-1")

    assert result.status == "INSUFFICIENT_BALANCE"
    assert result.balance_cents == 1000
    assert service.balance_for("alpha") == 1000


def test_repeated_request_id_is_idempotent(tmp_path):
    service = PaymentService(tmp_path / "payments.sqlite3")
    service.create_account("alpha", "Alpha", 10000)

    first = service.pay("alpha", 2000, "request-1")
    second = service.pay("alpha", 2000, "request-1")

    assert second == first
    assert service.balance_for("alpha") == 8000
    assert service.transaction_count() == 1
