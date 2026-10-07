from __future__ import annotations

import numpy as np

from gallery import Gallery
from models import ROIResult
from payment import PaymentService
from templates import TemplateStore
from workflow import PalmPaymentWorkflow
from tools.summarize_checkout_trace import summarize_events


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


def test_checkout_log_contains_stage_trace(tmp_path):
    events = []
    workflow, _ = make_workflow(tmp_path)
    workflow.logger = events.append
    workflow.capture = lambda: np.full((2, 2), 101.0)
    workflow.capture_context = lambda: {"frame_id": 17, "captured_at": "2026-09-23T00:00:00+00:00", "age_ms": 2.5}

    result = workflow.checkout(None, 2000, "request-trace")

    assert result.status == "SUCCESS"
    event = events[0]
    assert event["frame_id"] == 17
    assert event["roi_status"] == "OK"
    assert event["identification_status"] == "MATCH"
    assert "second_score" in event


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


def test_checkout_trace_summary_keeps_stage_failures_and_timings_separate():
    summary = summarize_events(
        [
            {"event": "checkout", "result": "SUCCESS", "roi_status": "OK", "roi_reason": None, "identification_status": "MATCH", "capture_source": "camera", "frame_id": 1, "total_ms": 10.0},
            {"event": "checkout", "result": "RETRY", "roi_status": "RETRY", "roi_reason": "LOW_CONTRAST", "identification_status": "MISSING", "capture_source": "camera", "frame_id": 2, "total_ms": 20.0},
        ]
    )

    assert summary["total_checkouts"] == 2
    assert summary["results"] == {"SUCCESS": 1, "RETRY": 1}
    assert summary["roi_reasons"] == {"MISSING": 1, "None": 1, "LOW_CONTRAST": 1} or summary["roi_reasons"] == {"None": 1, "LOW_CONTRAST": 1}
    assert summary["frame_id_present"] == 2
    assert summary["timings_ms"]["total_ms"]["p95"] == 19.5
