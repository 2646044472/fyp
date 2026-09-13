from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from biometric import extract_feature
from models import CheckoutResult, ROIResult
from payment import PaymentService
from templates import TemplateStore, safe_user_id


class PalmPaymentWorkflow:
    def __init__(
        self,
        roi,
        algorithm: Any,
        gallery,
        payment_service: PaymentService,
        *,
        capture_profile: str = "rgb",
        logger: Callable[[dict], None] | None = None,
        capture: Callable[[], Any] | None = None,
    ) -> None:
        self.roi = roi
        self.algorithm = algorithm
        self.gallery = gallery
        self.payment_service = payment_service
        self.capture_profile = capture_profile
        self.logger = logger
        self.capture = capture

    def checkout(self, image, amount_cents: int, request_id: str) -> CheckoutResult:
        total_started = time.perf_counter()
        timings = {key: 0.0 for key in ("capture_ms", "roi_ms", "feature_ms", "search_ms", "payment_ms", "total_ms")}
        capture_started = time.perf_counter()
        if image is None and self.capture is not None:
            try:
                image = self.capture()
            except Exception as error:
                return self._result("RETRY", None, None, None, None, str(error), timings, total_started)
        if image is None:
            return self._result("RETRY", None, None, None, None, "NO_CAPTURE", timings, total_started)
        timings["capture_ms"] = (time.perf_counter() - capture_started) * 1000
        roi_started = time.perf_counter()
        try:
            roi_result: ROIResult = self.roi.extract(image)
        except Exception as error:
            return self._result("RETRY", None, None, None, None, str(error), timings, total_started)
        timings["roi_ms"] = (time.perf_counter() - roi_started) * 1000
        if roi_result.status != "OK" or roi_result.roi is None:
            return self._result("RETRY", None, None, None, None, roi_result.reason or "ROI_FAILED", timings, total_started)
        feature_started = time.perf_counter()
        try:
            feature = extract_feature(self.algorithm, roi_result.roi)
        except Exception as error:
            return self._result("RETRY", None, None, None, None, str(error), timings, total_started)
        timings["feature_ms"] = (time.perf_counter() - feature_started) * 1000
        identification = self.gallery.identify(feature, self.capture_profile)
        timings["search_ms"] = identification.search_ms
        if identification.status == "RETRY":
            return self._result("RETRY", None, identification.score, None, None, identification.reason, timings, total_started)
        if identification.status == "UNKNOWN":
            return self._result("UNKNOWN_USER", None, identification.score, None, None, identification.reason, timings, total_started)
        payment_started = time.perf_counter()
        payment = self.payment_service.pay(identification.user_id, amount_cents, request_id)
        timings["payment_ms"] = (time.perf_counter() - payment_started) * 1000
        result_status = payment.status if payment.status != "ERROR" else "FAILURE"
        return self._result(result_status, identification.user_id, identification.score, payment.transaction_id, payment.balance_cents, None, timings, total_started)

    def _result(self, status, user_id, score, transaction_id, balance_cents, reason, timings, total_started):
        timings["total_ms"] = (time.perf_counter() - total_started) * 1000
        result = CheckoutResult(status, user_id, transaction_id, score, balance_cents, reason, dict(timings))
        event = {"event": "checkout", "result": result.status, "user_id": result.user_id, "score": result.score, "gallery_size": self.gallery.size, "capture_profile": self.capture_profile, **result.timings}
        if result.reason:
            event["retry_reason"] = result.reason
        if self.logger:
            self.logger(event)
        return result

    def enroll_user(self, user_id: str, display_name: str, captures, initial_balance_cents: int) -> None:
        user_id = safe_user_id(user_id)
        store: TemplateStore = self.gallery.store
        if store.exists(user_id) or self.payment_service.user_exists(user_id):
            raise ValueError(f"user {user_id} already exists")
        features = []
        for image in captures:
            result = self.roi.extract(image)
            if result.status != "OK" or result.roi is None:
                raise ValueError(f"enrollment rejected: {result.reason or 'ROI_FAILED'}")
            features.append(extract_feature(self.algorithm, result.roi))
        if not features:
            raise ValueError("at least one capture is required")
        metadata = {"user": user_id, "display_name": display_name, "algorithm": "FastCC", "capture_profile": self.capture_profile, "samples": len(features), "warning": "Threshold must be frozen using development data before evaluation."}
        store.save(user_id, np.stack(features), metadata)
        try:
            self.payment_service.create_account(user_id, display_name, initial_balance_cents)
        except Exception:
            store.delete(user_id)
            raise

    def delete_user(self, user_id: str) -> None:
        user_id = safe_user_id(user_id)
        self.gallery.store.delete(user_id)
        self.payment_service.delete_user(user_id)
