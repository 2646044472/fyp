from __future__ import annotations

import numpy as np

from gallery import Gallery
from models import ROIResult
from payment import PaymentService
from templates import TemplateStore
from workflow import PalmPaymentWorkflow


class FeatureAlgorithm:
    def extract(self, roi):
        return np.array([float(np.asarray(roi).mean())])

    def match(self, probe, candidate):
        return abs(float(probe[0]) - float(candidate[0]))


class StaticROI:
    def __init__(self, status="OK"):
        self.status = status

    def extract(self, image):
        if self.status != "OK":
            return ROIResult("RETRY", None, "HAND_CLIPPED", {}, 0.1)
        return ROIResult("OK", image, None, {"contrast": 20.0, "sharpness": 20.0}, 0.1)


def make_workflow(tmp_path, balance=10000, threshold=0.28, roi=None):
    store = TemplateStore(tmp_path / "templates")
    algorithm = FeatureAlgorithm()
    store.save("stephen", np.array([[101.0], [101.1]]), {"capture_profile": "rgb"})
    gallery = Gallery(store, algorithm, threshold=threshold)
    payments = PaymentService(tmp_path / "payments.sqlite3")
    payments.create_account("stephen", "Stephen", balance)
    return PalmPaymentWorkflow(roi or StaticROI(), algorithm, gallery, payments), payments


def test_successful_checkout_commits_once(tmp_path):
    workflow, payments = make_workflow(tmp_path)

    result = workflow.checkout(np.full((2, 2), 101.0), 2000, "request-1")

    assert result.status == "SUCCESS"
    assert result.user_id == "stephen"
    assert result.transaction_id is not None
    assert payments.balance_for("stephen") == 8000
    assert set(result.timings) == {"capture_ms", "roi_ms", "feature_ms", "search_ms", "payment_ms", "total_ms"}


def test_unknown_checkout_does_not_create_transaction(tmp_path):
    workflow, payments = make_workflow(tmp_path)

    result = workflow.checkout(np.full((2, 2), 200.0), 2000, "request-1")

    assert result.status == "UNKNOWN_USER"
    assert payments.transaction_count() == 0


def test_roi_failure_returns_retry_without_payment(tmp_path):
    workflow, payments = make_workflow(tmp_path, roi=StaticROI("RETRY"))

    result = workflow.checkout(np.full((2, 2), 101.0), 2000, "request-1")

    assert result.status == "RETRY"
    assert payments.transaction_count() == 0


def test_insufficient_funds_is_reported(tmp_path):
    workflow, payments = make_workflow(tmp_path, balance=1000)

    result = workflow.checkout(np.full((2, 2), 101.0), 2000, "request-1")

    assert result.status == "INSUFFICIENT_BALANCE"
    assert payments.balance_for("stephen") == 1000


def test_enrollment_and_deletion_remove_biometric_and_account_state(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    algorithm = FeatureAlgorithm()
    payments = PaymentService(tmp_path / "payments.sqlite3")
    workflow = PalmPaymentWorkflow(StaticROI(), algorithm, Gallery(store, algorithm), payments)

    workflow.enroll_user("stephen", "Stephen", [np.full((2, 2), 101.0)], 10000)
    assert store.exists("stephen")
    assert payments.user_exists("stephen")

    workflow.delete_user("stephen")

    assert not store.exists("stephen")
    assert not payments.user_exists("stephen")
    assert not payments.account_exists("stephen")
    assert payments.transactions_for("stephen") == []
