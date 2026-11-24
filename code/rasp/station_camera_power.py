"""Keep the physical camera open only while a station page is using it."""
import threading
import time


class CameraPower:
    def __init__(self, create_feed, idle_seconds=15, *, on_idle=None):
        self.create_feed = create_feed
        self.idle_seconds = idle_seconds
        self.on_idle = on_idle
        self.lock = threading.RLock()
        self.feed = None
        self.owner = None
        self.last_frame_id = 0
        self.deadline = 0
        self.timer = None

    def use(self, owner):
        with self.lock:
            if self.feed is None:
                self.feed = self.create_feed(self.last_frame_id)
            self.owner = owner
            self.deadline = time.monotonic() + self.idle_seconds
            if self.timer is None:
                self._schedule_expiry(self.idle_seconds)
            return self.feed

    def _schedule_expiry(self, delay):
        self.timer = threading.Timer(delay, self._expire)
        self.timer.daemon = True
        self.timer.start()

    def _expire(self):
        with self.lock:
            if self.timer is not threading.current_thread():
                return
            self.timer = None
            remaining = self.deadline - time.monotonic()
            if remaining > 0:
                self._schedule_expiry(remaining)
            else:
                try:
                    if self.on_idle is not None and self.owner is not None:
                        self.on_idle(self.owner)
                finally:
                    self.close()

    def close(self, owner=None):
        with self.lock:
            if owner is not None and owner != self.owner:
                return
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            feed = self.feed
            self.feed = self.owner = None
            if feed is not None:
                try:
                    feed.close()
                finally:
                    self.last_frame_id = feed._next_frame_id
