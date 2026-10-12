"""Small, supervised palm-to-simulated-payment flow for the Pi demo."""

from __future__ import annotations

import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import numpy as np

from gallery import Gallery
from payment import PaymentService
from templates import TemplateStore, safe_user_id


class DemoFlow:
    def __init__(self, runtime: Path, algorithm: Any, capture_feature: Callable[[], tuple[np.ndarray, str, str]], *, roi_geometry: str | None = None) -> None:
        self.algorithm = algorithm
        self.capture_feature = capture_feature
        self.roi_geometry = roi_geometry
        self.store = TemplateStore(runtime / "demo_templates")
        self.payments = PaymentService(runtime / "demo_payment.sqlite3")
        # Ranking only; no open-set threshold can be calibrated from one person's two hands.
        required = {"roi_geometry": roi_geometry, "algorithm": algorithm.name} if roi_geometry is not None else None
        self.gallery = Gallery(self.store, algorithm, threshold=1.0, required_metadata=required)
        self.lock = threading.Lock()
        self.pending: dict[str, tuple[str, int, float]] = {}

    def enroll(self, user_id: str, display_name: str) -> dict[str, Any]:
        user_id = safe_user_id(user_id)
        display_name = display_name.strip()
        if not display_name or len(display_name) > 60:
            raise ValueError("请输入 1–60 个字符的姓名。")
        with self.lock:
            if self.store.exists(user_id) or self.payments.user_exists(user_id):
                raise ValueError("这个编号已经录入；请换一个编号。")
            features = []
            sources = []
            for _ in range(5):
                feature, _, source = self.capture_feature()
                features.append(feature)
                sources.append(source)
            self.store.save(user_id, np.stack(features), {
                "user": user_id, "display_name": display_name, "algorithm": self.algorithm.name,
                "capture_profile": "noir-ir", "samples": 5,
                "source": "3280x2464-full-still",
                "roi_geometry": self.roi_geometry,
                "roi_sources": sources,
            })
            try:
                self.payments.create_account(user_id, display_name, 10000)
            except Exception:
                self.store.delete(user_id)
                raise
            return {"user_id": user_id, "display_name": display_name, "balance_cents": 10000}

    def identify(self) -> dict[str, Any]:
        with self.lock:
            self.pending.clear()
            feature, roi_image, source = self.capture_feature()
            result = self.gallery.identify(feature, "noir-ir")
            response = {"status": result.status, "score": result.score,
                        "second_score": result.second_score, "reason": result.reason,
                        "roi_image": roi_image, "roi_source": source}
            if result.status != "MATCH" or result.user_id is None:
                return response
            token = uuid.uuid4().hex
            self.pending[token] = (result.user_id, 2000, time.monotonic() + 120)
            response.update({"token": token, "user_id": result.user_id,
                             "display_name": self.payments.display_name_for(result.user_id),
                             "amount_cents": 2000})
            return response

    def cancel(self, token: str) -> dict[str, str]:
        with self.lock:
            self.pending.pop(token, None)
        return {"status": "CANCELLED"}

    def confirm(self, token: str, user_id: str) -> dict[str, Any]:
        with self.lock:
            pending = self.pending.pop(token, None)
            if pending is None or pending[2] < time.monotonic():
                raise ValueError("识别结果已过期，请重新拍摄。")
            matched_user, amount, _ = pending
            if user_id != matched_user:
                raise ValueError("确认的身份与识别结果不一致，没有扣款。")
            payment = self.payments.pay(matched_user, amount, token)
            return {"status": payment.status, "user_id": matched_user,
                    "display_name": self.payments.display_name_for(matched_user),
                    "amount_cents": amount, "balance_cents": payment.balance_cents,
                    "transaction_id": payment.transaction_id}

    def users(self) -> list[dict[str, Any]]:
        return self.payments.list_users()
