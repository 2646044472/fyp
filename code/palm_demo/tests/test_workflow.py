from __future__ import annotations

import numpy as np

from gallery import Gallery, ScoreDirection
from payment import PaymentService
from recognition import RecognitionEngine
from templates import TemplateStore
from workflow import PalmPaymentWorkflow


class DistanceMatcher:
    def extract(self, roi):
        return np.array([float(np.asarray(roi).mean())])

    def match(self, query, template):
        return abs(float(query[0]) - float(template[0]))


def make_workflow(tmp_path, *, balance=10_000):
    store = TemplateStore(tmp_path / "templates")
    algorithm = DistanceMatcher()
    store.save("P001", np.array([[0.10], [0.12]]), {"capture_profile": "rgb"})
    gallery = Gallery.from_store(
        store,
        algorithm,
        threshold=0.28,
        direction=ScoreDirection.DISTANCE,
        capture_profile="rgb",
    )
    recognizer = RecognitionEngine(algorithm, gallery)
    payments = PaymentService(tmp_path / "payments.sqlite3")
    payments.create_account("P001", "Stephen", balance)
    return PalmPaymentWorkflow(recognizer, payments, token_ttl_seconds=60), payments


def test_identification_requires_confirmation_before_debit(tmp_path):
    workflow, payments = make_workflow(tmp_path)

    pending = workflow.begin_payment(np.array([0.11]), 500, "TX100")

    assert pending.status == "PENDING_CONFIRMATION"
    assert pending.user_id == "P001"
    assert pending.confirmation_token
    assert payments.balance_for("P001") == 10_000
    assert payments.transaction_count() == 0

    success = workflow.confirm_payment(pending.confirmation_token, amount_cents=500)

    assert success.status == "SUCCESS"
    assert success.user_id == "P001"
    assert payments.balance_for("P001") == 9_500


def test_unknown_identity_never_creates_payment_intent(tmp_path):
    workflow, payments = make_workflow(tmp_path)

    result = workflow.begin_payment(np.array([0.90]), 500, "TX101")

    assert result.status == "UNKNOWN"
    assert result.user_id is None
    assert result.confirmation_token is None
    assert payments.transaction_count() == 0


def test_non_ready_roi_returns_retry_without_running_payment(tmp_path):
    workflow, payments = make_workflow(tmp_path)

    result = workflow.begin_payment(np.array([0.11]), 500, "TX102", roi_status="LOW_QUALITY")

    assert result.status == "RETRY"
    assert result.confirmation_token is None
    assert payments.transaction_count() == 0


def test_confirmation_cannot_change_amount_or_user(tmp_path):
    workflow, payments = make_workflow(tmp_path)
    pending = workflow.begin_payment(np.array([0.11]), 500, "TX103")

    mismatch = workflow.confirm_payment(pending.confirmation_token, amount_cents=600)

    assert mismatch.status == "CONFIRMATION_MISMATCH"
    assert payments.balance_for("P001") == 10_000
    assert payments.transaction_count() == 0


def test_confirmation_rejects_non_integer_amount_without_debit(tmp_path):
    workflow, payments = make_workflow(tmp_path)
    pending = workflow.begin_payment(np.array([0.11]), 500, "TX-FLOAT")

    invalid = workflow.confirm_payment(pending.confirmation_token, amount_cents=500.0)

    assert invalid.status == "INVALID_AMOUNT"
    assert payments.balance_for("P001") == 10_000
    assert payments.transaction_count() == 0


def test_confirmation_token_is_one_time_and_repeated_request_does_not_debit_again(tmp_path):
    workflow, payments = make_workflow(tmp_path)
    pending = workflow.begin_payment(np.array([0.11]), 500, "TX104")
    first = workflow.confirm_payment(pending.confirmation_token, amount_cents=500)

    second = workflow.confirm_payment(pending.confirmation_token, amount_cents=500)

    assert first.status == "SUCCESS"
    assert second.status == "TOKEN_ALREADY_USED"
    assert payments.balance_for("P001") == 9_500
    assert payments.transaction_count() == 1


def test_confirmation_token_expires_without_debit(tmp_path):
    now = [100.0]
    workflow, payments = make_workflow(tmp_path)
    workflow = PalmPaymentWorkflow(workflow.recognizer, payments, token_ttl_seconds=5, clock=lambda: now[0])
    pending = workflow.begin_payment(np.array([0.11]), 500, "TX105")
    now[0] = 105.0

    expired = workflow.confirm_payment(pending.confirmation_token, amount_cents=500)

    assert expired.status == "TOKEN_EXPIRED"
    assert payments.balance_for("P001") == 10_000
    assert payments.transaction_count() == 0
