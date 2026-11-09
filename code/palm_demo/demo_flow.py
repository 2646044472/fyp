"""Small, supervised palm-to-simulated-payment flow for the Pi demo."""

from __future__ import annotations

import threading
import time
import uuid
import json
import zipfile
from pathlib import Path
from typing import Any, Callable

import numpy as np

from gallery import Gallery
from acceptance_policy import load_acceptance_policy
from enrollment_photo_selection import PhotoCandidate, select_enrollment_photos
from payment import PaymentService
from templates import TemplateStore, safe_user_id


CAPTURE_FAILURE_MESSAGES = {
    "NO_HAND": "没有检测到手掌，请把手掌放入预览并移到画面中央。",
    "ROI_UNSTABLE": "掌区检测尚未稳定，请展开手掌并保持不动，等状态就绪后继续。",
    "ROI_GEOMETRY_INVALID": "检测到了掌区，但几何范围无效；请把整只手放入画面并调整距离。",
    "CAMERA_BUSY": "相机正在拍摄，请稍候再试。",
    "CAMERA_UNAVAILABLE": "暂时无法读取相机画面，请检查连接后重试。",
    "CAPTURE_TIMEOUT": "相机没有及时提供新画面，请确认预览仍在更新；恢复后可以继续。",
    "ROI_NOT_READY": "掌区状态尚未稳定，请等待预览显示就绪后继续采集。",
}


def classify_camera_capture_error(error: BaseException) -> str:
    message = str(error).casefold()
    waiting_for_frame = "waiting for a fresh" in message
    return "CAPTURE_TIMEOUT" if waiting_for_frame or "timed out" in message or "timeout" in message else "CAMERA_UNAVAILABLE"


def classify_roi_capture_error(error: BaseException) -> str:
    reason = str(error).strip().casefold()
    if reason in {"no_hand", "no_candidate", "tracking_lost", "tracking_stale", "hand_not_detected"}:
        return "NO_HAND"
    geometry_terms = ("span is too small", "outside the frame", "degenerate", "stable axis", "quad", "geometry")
    if any(term in reason for term in geometry_terms):
        return "ROI_GEOMETRY_INVALID"
    return "ROI_UNSTABLE"


class CaptureProcessingFailure(RuntimeError):
    """A frame could not produce a usable ROI or feature."""

    def __init__(self, reason: str, detail: str | None = None) -> None:
        message = detail or CAPTURE_FAILURE_MESSAGES.get(reason, reason)
        super().__init__(message)
        self.reason = reason
        self.detail = message


class DemoFlow:
    def __init__(self, runtime: Path, algorithm: Any, capture_feature: Callable[[], tuple[np.ndarray, str, str]], *, roi_geometry: str | None = None, capture_enrollment_feature: Callable[[], tuple[np.ndarray,str,str]] | None = None, capture_profile: str = "noir-ir", capture_source: str = "3280x2464-full-still") -> None:
        self.algorithm = algorithm
        self.capture_feature = capture_feature
        self.capture_enrollment_feature = capture_enrollment_feature or capture_feature
        self.roi_geometry = roi_geometry
        self.capture_profile = capture_profile
        self.capture_source = capture_source
        acceptance_policy = load_acceptance_policy(runtime / "demo_acceptance_policy.json")
        store_factory = getattr(algorithm, 'template_store_factory', TemplateStore)
        self.store = store_factory(runtime / "demo_templates",
                                   compression_level=getattr(algorithm, 'template_compression_level', None))
        self.payments = PaymentService(runtime / "demo_payment.sqlite3")
        # Ranking-only remains the default. Opt-in rejection is explicit and
        # keeps independent profiles for ordinary, angular and weighted scores.
        required = {"algorithm": algorithm.name}
        if roi_geometry is not None:
            required["roi_geometry"] = roi_geometry
        if getattr(algorithm, 'template_codec', None):
            required.update(template_codec=algorithm.template_codec,
                            template_storage_schema=algorithm.template_storage_schema)
        self.gallery = Gallery(self.store, algorithm, threshold=1.0, required_metadata=required, acceptance_policy=acceptance_policy, strict_integrity=True)
        self._integrity_cache: dict[str, tuple[tuple, dict[str, Any]]] = {}
        self.lock = threading.Lock()
        self.pending: dict[str, tuple[str, int, float]] = {}
        self.enrollment_candidate: Callable[[], tuple] | None = None
        self.enrollment_session: dict[str, Any] | None = None

    def enroll(self, user_id: str, display_name: str) -> dict[str, Any]:
        user_id = safe_user_id(user_id)
        display_name = display_name.strip()
        if not display_name or len(display_name) > 60:
            raise ValueError("请输入 1–60 个字符的姓名。")
        with self.lock:
            has_template = self.store.exists(user_id)
            has_account = self.payments.user_exists(user_id)
            refreshing = False
            if has_template or has_account:
                if not (has_template and has_account):
                    raise ValueError("这个编号的模板或账户不完整，请先检查已有记录。")
                _, metadata = self.store.load(user_id)
                refreshing = any(metadata.get(k) != v for k, v in self.gallery.required_metadata.items())
                if not refreshing:
                    raise ValueError("这个编号已经录入；请换一个编号。")
                display_name = self.payments.display_name_for(user_id)
            features = []
            sources = []
            for _ in range(5):
                feature, _, source = self.capture_enrollment_feature()
                features.append(feature)
                sources.append(source)
            # Persist only after all five captures pass geometry and quality.
            # On failure the old template and account remain usable for rollback.
            batch = getattr(self.store, 'batch_features', np.stack)(features)
            self.store.save(user_id, batch, {
                "user": user_id, "display_name": display_name, "algorithm": self.algorithm.name,
                "capture_profile": self.capture_profile, "samples": 5,
                "source": self.capture_source,
                "roi_geometry": self.roi_geometry,
                "roi_sources": sources,
            })
            if not refreshing:
                try:
                    self.payments.create_account(user_id, display_name, 10000)
                except Exception:
                    self.store.delete(user_id)
                    raise
            self.pending.clear()
            response = {"user_id": user_id, "display_name": display_name,
                        "balance_cents": self.payments.balance_for(user_id), "reenrolled": refreshing}
            if hasattr(self.algorithm, 'prepare_gallery'):
                try:
                    integrity_reason = self._gallery_integrity_reason()
                    if integrity_reason is not None:
                        raise ValueError(integrity_reason)
                    self.gallery.warm_up(capture_profile=self.capture_profile)
                    response['recognition_ready'] = True
                except (ValueError, RuntimeError, OSError) as error:
                    # Enrollment is already committed. Do not falsely report
                    # it as rolled back when optional index preparation fails.
                    response.update(recognition_ready=False, preparation_error=str(error))
            return response

    def enrollment_start(self, user_id: str, display_name: str, hand: str) -> dict[str, Any]:
        user_id = safe_user_id(user_id)
        display_name = display_name.strip()
        if not display_name or len(display_name) > 60 or hand not in ("left", "right"):
            raise ValueError("请输入姓名并选择左手或右手。")
        for suffix in ("left", "right"):
            if user_id.lower().endswith("_" + suffix) and hand != suffix:
                raise ValueError("编号末尾的手别与所选手别不一致。")
        with self.lock:
            if self.enrollment_session is not None and time.monotonic() - self.enrollment_session["started"] > 120:
                self.enrollment_session = None
            if self.enrollment_session is not None:
                raise ValueError("已有录入正在进行，请先取消。")
            has_template, has_account = self.store.exists(user_id), self.payments.user_exists(user_id)
            if has_template != has_account:
                raise ValueError("这个编号的模板或账户不完整，请先检查已有记录。")
            refreshing = False
            if has_template:
                _, metadata = self.store.load(user_id)
                if metadata.get("hand_declared_by_user") not in (None, hand):
                    raise ValueError("原编号的手别与本次选择不一致。")
                refreshing = any(metadata.get(k) != v for k, v in self.gallery.required_metadata.items())
                if not refreshing:
                    raise ValueError("这个编号已经录入；请换一个编号。")
                display_name = self.payments.display_name_for(user_id)
            session = {"token": uuid.uuid4().hex, "user_id": user_id, "display_name": display_name,
                       "refreshing": refreshing, "hand": hand, "features": [], "sources": [],
                       "rois": [], "qualities": [], "attempts": 0, "quality_failures": 0,
                       "duplicate_frames": 0, "photo_candidates": [], "candidate_pool_required": 8,
                       "selected_roi_images": [], "selected_frame_ids": [],
                       "started": time.monotonic()}
            self.enrollment_session = session
            return {"token": session["token"], "kept": 0, "required": 5, "max_quality_failures": 15,
                    "candidate_pool_required": session["candidate_pool_required"],
                    "timeout_seconds": 120,
                    "hand_check": "user_confirmation_required"}

    def _active_enrollment(self, token: str) -> dict[str, Any]:
        session = self.enrollment_session
        if session is None or token != session["token"]:
            raise ValueError("录入会话已失效，请重新开始。")
        return session

    def enrollment_status(self, token: str) -> dict[str, Any]:
        with self.lock:
            session = self._active_enrollment(token)
            elapsed = time.monotonic() - session["started"]
            if elapsed > 120:
                self.enrollment_session = None
                return {"status": "EXPIRED"}
            kept = len(session["features"])
            if kept == 5:
                status = "READY"
            elif session["quality_failures"] >= 15:
                status = "STOPPED"
            else:
                status = "PAUSED"
            return {
                "status": status,
                "user_id": session["user_id"],
                "display_name": session["display_name"],
                "hand": session["hand"],
                "kept": kept,
                "required": 5,
                "attempts": session["attempts"],
                "quality_failures": session["quality_failures"],
                "duplicate_frames": session["duplicate_frames"],
                "candidate_pool_count": len(session["photo_candidates"]),
                "candidate_pool_required": session["candidate_pool_required"],
                "max_quality_failures": 15,
                "timeout_seconds_remaining": max(0, int(120 - elapsed)),
                "selected_roi_images": list(session["selected_roi_images"]),
            }

    def enrollment_step(self, token: str) -> dict[str, Any]:
        with self.lock:
            session = self._active_enrollment(token)
            kept = len(session["features"])
            def progress(status: str, reason: str | None = None, **extra: Any) -> dict[str, Any]:
                result = {"status": status, "kept": len(session["features"]), "required": 5,
                          "attempts": session["attempts"], "quality_failures": session["quality_failures"],
                          "duplicate_frames": session["duplicate_frames"],
                          "candidate_pool_count": len(session["photo_candidates"]),
                          "candidate_pool_required": session["candidate_pool_required"]}
                if reason is not None:
                    result["reason"] = reason
                result.update(extra)
                return result
            if kept == 5:
                return progress("READY")
            if session["quality_failures"] >= 15 or time.monotonic() - session["started"] > 120:
                return progress("STOPPED", "已达质量重试或等待时间上限，请取消后调整手掌位置再试。")
            session["attempts"] += 1
            if self.enrollment_candidate is None:
                raise RuntimeError("录入候选采集器不可用。")
            try:
                captured = self.enrollment_candidate()
                if len(captured) == 5:
                    feature, encoded_roi, source, quality, roi = captured
                    # Compatibility path for existing mock/custom capture callbacks.
                    height, width = np.asarray(roi).shape[:2]
                    roi_quad = np.asarray([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
                    frame_size = (width, height)
                elif len(captured) == 6:
                    feature, encoded_roi, source, quality, roi, candidate_metadata = captured
                    roi_quad = np.asarray(candidate_metadata["roi_quad"], dtype=np.float32)
                    frame_size = tuple(candidate_metadata["frame_size"])
                else:
                    raise RuntimeError("录入候选采集器返回格式不正确。")
            except CaptureProcessingFailure as error:
                if error.reason == "NO_HAND":
                    return progress("NO_HAND",
                                    "未检测到手掌，自动采集已暂停。请把手掌放回画面；掌区连续就绪后会自动继续，也可手动点击“继续采集”或取消。",
                                    capture_failure=error.reason, resume_required=True)
                if error.reason == "ROI_UNSTABLE":
                    session["quality_failures"] += 1
                return progress("WAIT", error.detail or "掌区暂不可用，请调整手掌位置后重试。",
                                capture_failure=error.reason, retry_after_ms=500)
            except (ValueError, RuntimeError):
                session["quality_failures"] += 1
                return progress("WAIT", "掌区暂不可用，请调整手掌位置后重试。", capture_failure="CAPTURE_ERROR")
            contrast, sharpness = float(quality.get("contrast", 0)), float(quality.get("sharpness", 0))
            if not np.isfinite([contrast, sharpness]).all() or sharpness < 2 or contrast < 12:
                session["quality_failures"] += 1
                reason = "画面可能失焦或模糊，请保持手掌稳定并等待清晰画面。" if sharpness < 2 else "掌区对比不足，请调整光线。"
                return progress("WAIT", reason)
            roi = np.asarray(roi, dtype=np.uint8)
            candidate_pool = session["photo_candidates"]
            small_y = np.linspace(0, roi.shape[0] - 1, 16).astype(int)
            small_x = np.linspace(0, roi.shape[1] - 1, 16).astype(int)
            texture = roi[np.ix_(small_y, small_x)].astype(np.float32).reshape(-1)
            texture -= float(texture.mean())
            if float(np.linalg.norm(texture)) <= 1e-12:
                texture = roi[np.ix_(small_y, small_x)].astype(np.float32).reshape(-1)
            payload = {"feature": feature, "encoded_roi": encoded_roi, "source": source,
                       "quality": {"contrast": contrast, "sharpness": sharpness}, "roi": roi.copy()}
            photo = PhotoCandidate(session["attempts"], sharpness, contrast, roi_quad, texture, frame_size, payload)
            for index, old in enumerate(candidate_pool):
                old_roi = old.payload["roi"]
                if old_roi.shape != roi.shape or np.mean(np.abs(old_roi.astype(np.int16) - roi.astype(np.int16))) >= 2.5:
                    continue
                session["duplicate_frames"] += 1
                if sharpness > old.sharpness * 1.1:
                    candidate_pool[index] = photo
                    return progress("COLLECTING", "重复画面已用更清晰的一帧替换，继续采集不同角度。",
                                    retry_after_ms=300)
                return progress("WAIT", "这张与候选画面重复；请让同一只手轻微移动或转动，再保持清晰。",
                                retry_after_ms=700)
            candidate_pool.append(photo)
            if len(candidate_pool) < session["candidate_pool_required"]:
                return progress("COLLECTING", "正在收集清晰且姿态不同的候选画面。", retry_after_ms=250)
            baseline = candidate_pool[:5]
            sharpness_floor = min(item.sharpness for item in baseline)
            contrast_floor = min(item.contrast for item in baseline)
            quality_eligible = [item for item in candidate_pool
                                if item.sharpness >= sharpness_floor and item.contrast >= contrast_floor]
            selected = select_enrollment_photos(quality_eligible,
                capacity=session["candidate_pool_required"], select_count=5)
            if len(selected) != 5:
                raise RuntimeError("录入候选不足五张，无法完成筛选。")
            chosen = [candidate.payload for candidate in selected]
            session["features"] = [item["feature"] for item in chosen]
            session["sources"] = [item["source"] for item in chosen]
            session["rois"] = [item["roi"].copy() for item in chosen]
            session["qualities"] = [item["quality"] for item in chosen]
            session["selected_roi_images"] = [item["encoded_roi"] for item in chosen]
            session["selected_frame_ids"] = [candidate.frame_id for candidate in selected]
            return progress("READY", "已从候选画面中自动选出五张，请核对预览后确认手别。",
                            selected_roi_images=list(session["selected_roi_images"]),
                            selected_frame_ids=list(session["selected_frame_ids"]),
                            selector_quality_floor={"sharpness": sharpness_floor, "contrast": contrast_floor})

    def enrollment_commit(self, token: str, confirm_hand: str) -> dict[str, Any]:
        with self.lock:
            session = self._active_enrollment(token)
            if len(session["features"]) != 5 or confirm_hand != session["hand"]:
                raise ValueError("请确认五张照片均为所选的同一只手。")
            user_id, display_name, refreshing = session["user_id"], session["display_name"], session["refreshing"]
            if self.store.exists(user_id) != refreshing or self.payments.user_exists(user_id) != refreshing:
                raise ValueError("录入期间账户状态已变化，请重新开始。")
            batch = getattr(self.store, 'batch_features', np.stack)(session["features"])
            self.store.save(user_id, batch, {
                "user": user_id, "display_name": display_name, "algorithm": self.algorithm.name,
                "capture_profile": self.capture_profile, "samples": 5, "source": self.capture_source,
                "roi_geometry": self.roi_geometry, "roi_sources": session["sources"],
                "hand_declared_by_user": session["hand"],
            })
            if not refreshing:
                try:
                    self.payments.create_account(user_id, display_name, 10000)
                except Exception:
                    self.store.delete(user_id)
                    raise
            self.pending.clear()
            self.enrollment_session = None
            response = {"user_id": user_id, "display_name": display_name,
                        "balance_cents": self.payments.balance_for(user_id), "reenrolled": refreshing}
            if hasattr(self.algorithm, 'prepare_gallery'):
                try:
                    integrity_reason = self._gallery_integrity_reason()
                    if integrity_reason is not None:
                        raise ValueError(integrity_reason)
                    self.gallery.warm_up(capture_profile=self.capture_profile)
                    response['recognition_ready'] = True
                except (ValueError, RuntimeError, OSError) as error:
                    response.update(recognition_ready=False, preparation_error=str(error))
            return response

    def enrollment_cancel(self, token: str) -> dict[str, str]:
        with self.lock:
            self._active_enrollment(token)
            self.enrollment_session = None
            return {"status": "CANCELLED"}

    def identify(self) -> dict[str, Any]:
        with self.lock:
            self.pending.clear()
            started=time.perf_counter()
            integrity_reason = self._gallery_integrity_reason()
            if integrity_reason is not None:
                elapsed = (time.perf_counter() - started) * 1000
                return {"status": "RETRY", "score": None, "second_score": None,
                        "reason": integrity_reason, "roi_image": None, "roi_source": None,
                        "timing_ms": {"capture_and_extract": 0.0, "gallery": elapsed, "total": elapsed}}
            capture_started = time.perf_counter()
            try:
                feature, roi_image, source = self.capture_feature()
            except CaptureProcessingFailure as error:
                captured = time.perf_counter()
                return {"status": "RETRY", "score": None, "second_score": None,
                        "reason": error.reason, "detail": error.detail,
                        "roi_image": None, "roi_source": None,
                        "timing_ms": {"capture_and_extract": (captured-capture_started)*1000,
                                      "gallery": (capture_started-started)*1000,
                                      "total": (captured-started)*1000}}
            captured=time.perf_counter()
            result = self.gallery.identify(feature, self.capture_profile)
            matched=time.perf_counter()
            response = {"status": result.status, "score": result.score,
                        "second_score": result.second_score, "reason": result.reason,
                        "roi_image": roi_image, "roi_source": source,
                        "timing_ms": {"capture_and_extract": (captured-capture_started)*1000,
                                      "gallery": ((matched-captured)+(capture_started-started))*1000,
                                      "total": (matched-started)*1000}}
            if hasattr(feature, 'route'):
                response['recognition_route'] = feature.route
            if result.status != "MATCH" or result.user_id is None:
                return response
            token = uuid.uuid4().hex
            self.pending[token] = (result.user_id, 2000, time.monotonic() + 120)
            response.update({"token": token, "user_id": result.user_id,
                             "display_name": self.payments.display_name_for(result.user_id),
                             "amount_cents": 2000})
            return response

    def _gallery_integrity_reason(self) -> str | None:
        """Never identify against a silently reduced device enrollment gallery.

        File signatures invalidate validation when an enrollment changes. Heavy
        prepared-template validation shares Gallery's existing cache; unchanged
        enrollments need only file stats and the account list on later queries.
        Complete templates for other capture profiles remain ordinary exclusions.
        """
        account_ids = {user["user_id"] for user in self.payments.list_users()}
        template_ids = set(self.store.list_template_ids())
        for stale in set(self._integrity_cache) - template_ids:
            del self._integrity_cache[stale]
        if account_ids - template_ids:
            return "GALLERY_INCOMPLETE_TEMPLATES"
        prepared_mode = all(hasattr(self.algorithm, name) for name in
                            ("prepare_probe", "prepare_enrollment", "prepared_bytes", "score_prepared"))
        for user_id in sorted(template_ids):
            try:
                signature = self.gallery._signature(user_id)
            except FileNotFoundError:
                return "GALLERY_INCOMPLETE_TEMPLATES"
            except (OSError, ValueError):
                return "GALLERY_INVALID_TEMPLATES"
            cached = self._integrity_cache.get(user_id)
            if cached is not None and cached[0] == signature:
                metadata = cached[1]
            else:
                try:
                    read_metadata = getattr(self.store, 'read_metadata', None)
                    metadata = (read_metadata(user_id) if read_metadata is not None else
                                json.loads(self.store.paths(user_id)[1].read_text(encoding="utf-8")))
                    if not isinstance(metadata, dict):
                        return "GALLERY_INVALID_TEMPLATES"
                    if not isinstance(metadata.get("capture_profile"), str) or not metadata["capture_profile"]:
                        return "GALLERY_INVALID_TEMPLATES"
                    if metadata.get("capture_profile") == self.capture_profile:
                        if any(metadata.get(key) != value for key, value in self.gallery.required_metadata.items()):
                            return "GALLERY_INCOMPATIBLE_TEMPLATES"
                        if prepared_mode:
                            prepared, _ = self.gallery._load_prepared(user_id)
                            if prepared is None or len(prepared) != 5:
                                return "GALLERY_INVALID_TEMPLATES"
                        else:
                            features, _ = self.store.load(user_id)
                            if (len(features) != 5 or any(np.asarray(frame).size == 0 or
                                    not np.isfinite(frame).all() for frame in features)):
                                return "GALLERY_INVALID_TEMPLATES"
                    if signature != self.gallery._signature(user_id):
                        return "GALLERY_CHANGED_DURING_QUERY"
                except (OSError, ValueError, KeyError, EOFError, zipfile.BadZipFile, TypeError, AttributeError, RuntimeError):
                    return "GALLERY_INVALID_TEMPLATES"
                self._integrity_cache[user_id] = (signature, metadata)
            if metadata.get("capture_profile") != self.capture_profile:
                continue
            if user_id not in account_ids:
                return "GALLERY_ACCOUNT_MISMATCH"
        return None

    def _payment_receipt(self, token: str, user_id: str | None = None) -> dict[str, Any] | None:
        transaction = self.payments.transaction_for_request(token)
        if transaction is None:
            return None
        matched_user = transaction["user_id"]
        if user_id is not None and user_id != matched_user:
            raise ValueError("确认的身份与识别结果不一致，没有新增扣款。")
        return {
            "status": transaction["status"],
            "user_id": matched_user,
            "display_name": self.payments.display_name_for(matched_user),
            "amount_cents": transaction["amount_cents"],
            "balance_cents": transaction["balance_after_cents"],
            "transaction_id": transaction["transaction_id"],
        }

    def cancel(self, token: str) -> dict[str, Any]:
        with self.lock:
            receipt = self._payment_receipt(token)
            self.pending.pop(token, None)
            if receipt is not None:
                # A lost confirmation response must not turn a committed
                # transaction into a misleading "cancelled, not charged".
                return {**receipt, "status": "PAID", "payment_status": receipt["status"]}
        return {"status": "CANCELLED"}

    def confirm(self, token: str, user_id: str) -> dict[str, Any]:
        with self.lock:
            receipt = self._payment_receipt(token, user_id)
            if receipt is not None:
                self.pending.pop(token, None)
                return receipt
            pending = self.pending.get(token)
            if pending is None or pending[2] < time.monotonic():
                self.pending.pop(token, None)
                raise ValueError("识别结果已过期，请重新拍摄。")
            matched_user, amount, _ = pending
            if user_id != matched_user:
                raise ValueError("确认的身份与识别结果不一致，没有扣款。")
            payment = self.payments.pay(matched_user, amount, token)
            if payment.transaction_id is None:
                raise ValueError("模拟支付未完成，请检查账户后重试本次确认。")
            receipt = self._payment_receipt(token, matched_user)
            if receipt is None:
                raise RuntimeError("无法读取模拟支付结果，请重试本次确认。")
            self.pending.pop(token, None)
            return receipt

    def users(self) -> list[dict[str, Any]]:
        users = self.payments.list_users()
        for user in users:
            try:
                paths = self.store.paths(user["user_id"])
                # Listing names needs no biometric arrays. Packed five-frame
                # enrollments can be tens of MiB each; validation belongs to
                # the existing identification integrity check, not this UI read.
                if not paths or not paths[0].is_file():
                    raise FileNotFoundError(paths[0] if paths else user["user_id"])
                read_metadata = getattr(self.store, "read_metadata", None)
                if callable(read_metadata):
                    metadata = read_metadata(user["user_id"])
                elif len(paths) == 2 and paths[1].is_file():
                    metadata = json.loads(paths[1].read_text(encoding="utf-8"))
                else:
                    raise FileNotFoundError(user["user_id"])
                if not isinstance(metadata, dict):
                    raise ValueError("Invalid enrollment metadata")
                user["needs_reenrollment"] = any(metadata.get(k) != v for k, v in self.gallery.required_metadata.items())
            except (OSError, KeyError, ValueError):
                user["needs_reenrollment"] = True
        return users
