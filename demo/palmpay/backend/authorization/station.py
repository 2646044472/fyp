import math
import secrets
import threading
import time
from urllib.parse import urlsplit

import httpx

from .provider import Result


class StationUnavailable(Exception):
    pass


class StationNoMatch(Exception):
    pass


class StationProvider:
    def __init__(self, url, threshold, timeout=20):
        endpoint = urlsplit(url)
        if (endpoint.scheme != "http" or endpoint.hostname != "127.0.0.1"
                or not endpoint.port or endpoint.netloc != f"127.0.0.1:{endpoint.port}"
                or endpoint.path not in ("", "/") or endpoint.query or endpoint.fragment):
            raise ValueError("Use a local FPN station URL or a loopback SSH tunnel.")
        if not math.isfinite(threshold) or not 0 < threshold <= 1:
            raise ValueError("Set an explicit FPN station match threshold between 0 and 1.")
        self.client = httpx.Client(base_url=url, timeout=3, trust_env=False)
        self.threshold = threshold
        self.timeout = timeout
        self.camera = threading.Lock()

    def request(self, path, payload=None, *, busy=False, retry=False):
        try:
            response = self.client.request("GET" if payload is None else "POST", path, json=payload)
            if (retry or busy) and response.status_code == 409:
                if retry:
                    return None
                raise StationUnavailable("The camera is busy. Close verification or finish enrollment on the station.")
            response.raise_for_status()
            document = response.json()
            if isinstance(document, dict):
                return document
        except (httpx.HTTPError, ValueError):
            pass
        raise StationUnavailable("The FPN station did not respond. Check the station or SSH tunnel.")

    def health(self):
        health = self.request("/station-health")
        if health.get("backend") != "fpn-c-e10-frozen" or health.get("mode") != "scores_only":
            raise StationUnavailable("The configured service is not the FPN + C E10 station.")
        return health

    def enrolled(self, identity):
        self.health()
        users = self.request("/api/demo/users").get("users")
        if not isinstance(users, list):
            raise StationUnavailable("The station enrollment list is unavailable.")
        return any(isinstance(user, dict) and user.get("user_id") == identity
                   and not user.get("needs_reenrollment") for user in users)

    def authorize(self, challenge, should_cancel=lambda: False):
        if not self.camera.acquire(blocking=False):
            raise StationUnavailable("Another payment is using the camera.")
        token = secrets.token_hex(16)
        camera_started = False
        try:
            self.health()
            deadline = time.monotonic() + min(self.timeout, max(0, challenge.expires_at - time.time()))
            if time.monotonic() >= deadline:
                raise StationNoMatch("Authorization expired.")
            camera_started = True
            started = self.request("/api/fpn/camera", {"token": token, "action": "start"}, busy=True)
            if started.get("camera_open") is not True:
                raise StationUnavailable("The FPN camera could not open.")
            next_keepalive = time.monotonic() + 4
            while time.monotonic() < deadline:
                if should_cancel():
                    raise StationNoMatch("Payment was cancelled or expired.")
                if time.monotonic() >= next_keepalive:
                    self.request("/api/fpn/camera", {"token": token, "action": "keepalive"}, busy=True)
                    next_keepalive = time.monotonic() + 4
                result = self.request("/api/fpn/verify", {"token": token, "threshold": self.threshold}, retry=True)
                if result is not None:
                    if result.get("mode") != "demo_verification" or result.get("threshold") != self.threshold:
                        raise StationUnavailable("The station returned an unexpected verification response.")
                    if result.get("decision") in ("BELOW_THRESHOLD", "TIED"):
                        time.sleep(0.25)
                        continue
                    if result.get("decision") == "EMPTY":
                        raise StationNoMatch("No palms are enrolled on this station.")
                    if result.get("decision") != "MATCH" or result.get("tied_top") is not False:
                        raise StationUnavailable("The station returned an unexpected decision.")
                    match = result.get("best_match")
                    scores = result.get("top_cosines")
                    if (not isinstance(match, dict) or not isinstance(match.get("user_id"), str)
                            or match.get("hand") not in ("left", "right") or not isinstance(scores, list)
                            or not scores or type(scores[0]) not in (int, float)
                            or not self.threshold <= scores[0] <= 1):
                        raise StationUnavailable("The station returned an invalid match.")
                    return Result(challenge, match["user_id"], hand=match["hand"])
                time.sleep(0.25)
            raise StationNoMatch("No matching palm detected. Reposition your hand and retry payment.")
        finally:
            try:
                if camera_started:
                    self.request("/api/fpn/camera", {"token": token, "action": "stop"})
            except StationUnavailable:
                pass
            finally:
                self.camera.release()

