"""Exercise lost-response recovery using isolated simulated payment stores."""

import numpy as np
import pytest

from demo_flow import DemoFlow
from payment import PaymentService


class Algorithm:
    name = "payment-recovery-test"


def make_flow(tmp_path, *, balance=10000):
    flow = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(1), "", "test"))
    flow.payments.create_account("p1", "Person One", balance)
    flow.payments.create_account("p2", "Person Two", 10000)
    flow.pending["one-request"] = ("p1", 2000, float("inf"))
    return flow


def test_repeated_confirmation_returns_original_receipt_without_another_charge(tmp_path):
    flow = make_flow(tmp_path)
    receipt = flow.confirm("one-request", "p1")
    assert receipt["status"] == "SUCCESS"
    assert flow.confirm("one-request", "p1") == receipt
    assert not flow.pending
    assert flow.payments.balance_for("p1") == 8000
    assert flow.payments.transaction_count() == 1


def test_committed_receipt_survives_process_restart_and_later_balance_changes(tmp_path):
    flow = make_flow(tmp_path)
    receipt = flow.confirm("one-request", "p1")
    flow.payments.top_up("p1", 500)
    restarted = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(1), "", "test"))
    assert not restarted.pending
    assert restarted.confirm("one-request", "p1") == receipt
    assert restarted.payments.balance_for("p1") == 8500
    assert restarted.payments.transaction_count() == 1


def test_cancel_after_lost_confirmation_reports_committed_payment(tmp_path):
    flow = make_flow(tmp_path)
    receipt = flow.confirm("one-request", "p1")
    cancelled = flow.cancel("one-request")
    assert cancelled == {**receipt, "status": "PAID", "payment_status": "SUCCESS"}
    assert flow.payments.balance_for("p1") == 8000
    assert flow.payments.transaction_count() == 1


def test_cancel_unconfirmed_request_still_blocks_confirmation(tmp_path):
    flow = make_flow(tmp_path)
    assert flow.cancel("one-request") == {"status": "CANCELLED"}
    with pytest.raises(ValueError, match="过期"):
        flow.confirm("one-request", "p1")
    assert flow.payments.transaction_count() == 0
    assert flow.payments.balance_for("p1") == 10000


def test_failure_before_commit_preserves_pending_request_for_safe_retry(tmp_path, monkeypatch):
    flow = make_flow(tmp_path)
    pay = flow.payments.pay
    attempts = []

    def interrupted_pay(*args):
        attempts.append(True)
        if len(attempts) == 1:
            raise OSError("temporary write failure before commit")
        return pay(*args)

    monkeypatch.setattr(flow.payments, "pay", interrupted_pay)
    with pytest.raises(OSError):
        flow.confirm("one-request", "p1")
    assert "one-request" in flow.pending
    assert flow.payments.transaction_count() == 0
    assert flow.confirm("one-request", "p1")["status"] == "SUCCESS"
    assert len(attempts) == 2
    assert flow.payments.balance_for("p1") == 8000
    assert flow.payments.transaction_count() == 1


def test_failure_after_commit_recovers_receipt_without_retrying_payment(tmp_path, monkeypatch):
    flow = make_flow(tmp_path)
    pay = flow.payments.pay
    attempts = []

    def committed_but_interrupted(*args):
        attempts.append(True)
        pay(*args)
        raise OSError("confirmation handler lost its response after commit")

    monkeypatch.setattr(flow.payments, "pay", committed_but_interrupted)
    with pytest.raises(OSError):
        flow.confirm("one-request", "p1")
    receipt = flow.confirm("one-request", "p1")
    assert receipt["status"] == "SUCCESS"
    assert len(attempts) == 1
    assert not flow.pending
    assert flow.payments.balance_for("p1") == 8000
    assert flow.payments.transaction_count() == 1


@pytest.mark.parametrize("completed", [False, True])
def test_wrong_identity_cannot_consume_or_reuse_another_persons_request(tmp_path, completed):
    flow = make_flow(tmp_path)
    if completed:
        flow.confirm("one-request", "p1")
    with pytest.raises(ValueError, match="身份"):
        flow.confirm("one-request", "p2")
    assert flow.confirm("one-request", "p1")["status"] == "SUCCESS"
    assert flow.payments.balance_for("p1") == 8000
    assert flow.payments.balance_for("p2") == 10000
    assert flow.payments.transaction_count() == 1


def test_insufficient_balance_is_a_stable_unpaid_outcome(tmp_path):
    flow = make_flow(tmp_path, balance=1000)
    receipt = flow.confirm("one-request", "p1")
    assert receipt["status"] == "INSUFFICIENT_BALANCE"
    assert flow.confirm("one-request", "p1") == receipt
    result = flow.cancel("one-request")
    assert result["status"] == "PAID"
    assert result["payment_status"] == "INSUFFICIENT_BALANCE"
    assert result["balance_cents"] == 1000
    assert flow.payments.balance_for("p1") == 1000
    assert flow.payments.transaction_count() == 1


@pytest.mark.parametrize("other_user,other_amount", [("p2", 2000), ("p1", 3000)])
def test_request_id_is_bound_to_original_identity_and_amount(tmp_path, other_user, other_amount):
    service = PaymentService(tmp_path / "payment.sqlite3")
    for user in ("p1", "p2"):
        service.create_account(user, user, 10000)
    service.pay("p1", 2000, "one-request")
    with pytest.raises(ValueError, match="bound"):
        service.pay(other_user, other_amount, "one-request")
    assert service.transaction_count() == 1
    assert service.balance_for("p1") == 8000
    assert service.balance_for("p2") == 10000
    assert service.transaction_for_request("one-request")["user_id"] == "p1"
    assert service.transaction_for_request("missing") is None
