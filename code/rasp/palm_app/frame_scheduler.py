"""Bounded latest-frame scheduling for single-frame palm candidates.

This scheduler owns no threads and performs no recognition or persistence. The
caller runs one inference worker and only publishes results accepted by finish.
"""
from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass(frozen=True)
class Frame:
    frame_id: int
    captured_at: float
    image: Any


@dataclass(frozen=True)
class Claim:
    frame: Frame
    generation: int


class LatestFrameScheduler:
    def __init__(self, *, max_age_seconds: float = 1.5):
        self._lock = Lock()
        self._max_age = max_age_seconds
        self._active = False
        self._generation = 0
        self._last_seen = -1
        self._pending = None
        self._inflight = None
        self._next_at = 0.0

    def start(self):
        with self._lock:
            self._generation += 1
            self._active = True
            self._pending = None
            self._next_at = 0.0

    def cancel(self):
        with self._lock:
            self._generation += 1
            self._active = False
            self._pending = None

    def submit(self, frame: Frame) -> bool:
        with self._lock:
            if not self._active or frame.frame_id <= self._last_seen:
                return False
            self._last_seen = frame.frame_id
            self._pending = frame
            return True

    def claim(self, now: float) -> Claim | None:
        with self._lock:
            if not self._active or self._inflight is not None or now < self._next_at:
                return None
            frame = self._pending
            self._pending = None
            if frame is None or now - frame.captured_at > self._max_age:
                return None
            claim = Claim(frame, self._generation)
            self._inflight = claim
            return claim

    def finish(self, claim: Claim, *, now: float, retry_after: float = 0.0) -> bool:
        """Release the worker; return whether this result may still be delivered."""
        with self._lock:
            if self._inflight is not claim:
                raise ValueError('claim is not in flight')
            self._inflight = None
            if not self._active or claim.generation != self._generation:
                return False
            self._next_at = now + max(0.0, retry_after)
            return True
