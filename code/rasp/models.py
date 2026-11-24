from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ROIResult:
    status: Literal["OK", "RETRY"]
    roi: object | None
    reason: str | None
    quality: dict[str, float]
    elapsed_ms: float


@dataclass(frozen=True)
class IdentificationResult:
    status: Literal["MATCH", "UNKNOWN", "RETRY"]
    user_id: str | None
    score: float | None
    second_score: float | None
    search_ms: float
    reason: str | None = None


@dataclass(frozen=True)
class PaymentResult:
    status: Literal["SUCCESS", "INSUFFICIENT_BALANCE", "ERROR"]
    transaction_id: str | None
    balance_cents: int | None


@dataclass(frozen=True)
class CheckoutResult:
    status: Literal["SUCCESS", "RETRY", "UNKNOWN_USER", "INSUFFICIENT_BALANCE", "FAILURE"]
    user_id: str | None
    transaction_id: str | None
    score: float | None
    balance_cents: int | None
    reason: str | None
    timings: dict[str, float]
