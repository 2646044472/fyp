"""Backend orchestration for the recognition-to-payment vertical slice."""

from __future__ import annotations

import math
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Callable

import numpy as np

from payment import PaymentResult, PaymentService


@dataclass(frozen=True)
class WorkflowResult:
    status: str
    user_id: str | None
    amount_cents: int
    transaction_id: str
    score: float | None = None
    confirmation_token: str | None = None
    payment: PaymentResult | None = None


@dataclass
class _PaymentIntent:
    user_id: str
    amount_cents: int
    transaction_id: str
    score: float | None
    expires_at: float
    used: bool = False


class PalmPaymentWorkflow:
    """Keep recognition separate from account mutation.

    ``begin_payment`` performs ROI readiness and 1:N identification, then
    creates a short-lived server-side intent. Only ``confirm_payment`` can
    spend it, so a client cannot replace the recognized ``user_id`` in a pay
    request.
    """

    def __init__(
        self,
        recognizer: Any,
        payments: PaymentService,
        *,
        token_ttl_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not math.isfinite(token_ttl_seconds) or token_ttl_seconds <= 0:
            raise ValueError("token_ttl_seconds must be positive and finite")
        self.recognizer = recognizer
        self.payments = payments
        self.token_ttl_seconds = float(token_ttl_seconds)
        self.clock = clock
        self._intents: dict[str, _PaymentIntent] = {}
        self._lock = threading.RLock()

    def begin_payment(
        self,
        roi: np.ndarray,
        amount_cents: int,
        transaction_id: str,
        *,
        roi_status: str = "READY",
    ) -> WorkflowResult:
        if roi_status != "READY":
            return WorkflowResult("RETRY", None, amount_cents, transaction_id)
        if isinstance(amount_cents, bool) or not isinstance(amount_cents, int) or amount_cents <= 0:
            return WorkflowResult("INVALID_AMOUNT", None, amount_cents, transaction_id)
        if not transaction_id:
            return WorkflowResult("INVALID_TRANSACTION_ID", None, amount_cents, transaction_id)

        if hasattr(self.recognizer, "recognize"):
            identification = self.recognizer.recognize(roi, roi_status=roi_status)
        else:
            # Compatibility for the first feature-only skeleton: a Gallery
            # can still be supplied while the capture adapter is being wired.
            identification = self.recognizer.identify(roi)
        if identification.status != "ACCEPT":
            return WorkflowResult(
                identification.status,
                None,
                amount_cents,
                transaction_id,
                score=identification.score,
            )

        token = secrets.token_urlsafe(32)
        with self._lock:
            self._intents[token] = _PaymentIntent(
                user_id=identification.user_id,
                amount_cents=amount_cents,
                transaction_id=transaction_id,
                score=identification.score,
                expires_at=self.clock() + self.token_ttl_seconds,
            )
        return WorkflowResult(
            "PENDING_CONFIRMATION",
            identification.user_id,
            amount_cents,
            transaction_id,
            score=identification.score,
            confirmation_token=token,
        )

    def confirm_payment(self, confirmation_token: str, *, amount_cents: int) -> WorkflowResult:
        with self._lock:
            intent = self._intents.get(confirmation_token)
            if intent is None:
                return WorkflowResult("TOKEN_INVALID", None, amount_cents, "")
            if intent.used:
                return WorkflowResult(
                    "TOKEN_ALREADY_USED", intent.user_id, intent.amount_cents, intent.transaction_id, score=intent.score
                )
            if self.clock() >= intent.expires_at:
                del self._intents[confirmation_token]
                return WorkflowResult(
                    "TOKEN_EXPIRED", intent.user_id, intent.amount_cents, intent.transaction_id, score=intent.score
                )
            if amount_cents != intent.amount_cents:
                return WorkflowResult(
                    "CONFIRMATION_MISMATCH", intent.user_id, intent.amount_cents, intent.transaction_id, score=intent.score
                )

            payment = self.payments.pay(intent.user_id, intent.amount_cents, intent.transaction_id)
            if payment.status == "SUCCESS":
                intent.used = True
            return WorkflowResult(
                payment.status,
                intent.user_id,
                intent.amount_cents,
                intent.transaction_id,
                score=intent.score,
                payment=payment,
            )
