from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Challenge:
    intent_id: str
    merchant_id: str
    amount: int
    currency: str
    expires_at: int

@dataclass(frozen=True)
class Result:
    challenge: Challenge
    identity: str
    hand: str | None = None

class AuthorizationProvider(Protocol):
    def authorize(self, challenge: Challenge) -> Result:
        ...

