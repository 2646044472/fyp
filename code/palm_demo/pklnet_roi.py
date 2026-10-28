"""PKLNet-backed palm ROI extraction.

PKLNet is kept behind a lazy loader because the Pi runtime may not have
PyTorch installed yet. Its preprocessing and coordinate unwarping follow the
upstream ``test.py`` and ``roiExtractor.py`` implementation.
"""

from __future__ import annotations

import sys
import threading
import types
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image
from pklnet_policy import MIN_KEYPOINT_SPAN_RATIO, branch_consensus


_APP_ROOT = Path(__file__).resolve().parent
PKLNET_ROOT = _APP_ROOT.parent / "pklnet" if (_APP_ROOT.parent / "pklnet").is_dir() else _APP_ROOT / "pklnet"
PKLNET_WEIGHTS = PKLNET_ROOT / "net_params_500.pth"
PKLNET_ONNX = PKLNET_ROOT / "pklnet-keypoints.onnx"
MODEL_GEOMETRY_VERSION = "pklnet-palmkit-native-v1"
HEATMAP_GEOMETRY_VERSION = "pklnet-heatmap-v3"
ASPECT_GEOMETRY_VERSION = "pklnet-heatmap-aspect-v4"
ROI_GEOMETRY_VERSION = "pklnet-illumination-consistent-v5"
LOCALIZER_GAMMA = 0.6
_LOCALIZER_GAMMA_LUT = np.rint((np.arange(256, dtype=np.float32) / 255) ** LOCALIZER_GAMMA * 255).astype(np.uint8)
MIN_ILLUMINATION_IOU = 0.5


def illumination_pixels(rgb: np.ndarray) -> np.ndarray:
    """Exact byte-domain gamma mapping without full-frame float temporaries."""
    if rgb.dtype != np.uint8:
        raise ValueError("Localizer illumination input must be uint8")
    return cv2.LUT(rgb, _LOCALIZER_GAMMA_LUT)


class PKLNetUnavailable(RuntimeError):
    """Raised when PKLNet cannot be loaded in the current environment."""


class PKLNetROI:
    """Load PKLNet once and turn its two keypoints into a 128x128 ROI."""

    _load_lock = threading.Lock()

    def __init__(self, root: Path = PKLNET_ROOT, weights: Path = PKLNET_WEIGHTS, *, backend: str = "onnx", threads: int | None = None, policy: str = "illumination") -> None:
        if backend not in ("auto", "torch", "onnx"):
            raise ValueError("PKLNet backend must be auto, torch or onnx")
        if threads is not None and (not isinstance(threads, int) or not 1 <= threads <= 64):
            raise ValueError("PKLNet CPU threads must be between 1 and 64")
        if policy not in ("illumination", "aspect", "heatmap", "consensus", "legacy"):
            raise ValueError("PKLNet policy must be illumination, aspect, heatmap, consensus or legacy")
        self.root = Path(root)
        self.weights = Path(weights)
        self.backend = backend
        self.threads = threads
        self.policy = policy
        self.roi_geometry = {"illumination": ROI_GEOMETRY_VERSION, "aspect": ASPECT_GEOMETRY_VERSION, "heatmap": HEATMAP_GEOMETRY_VERSION,
                             "consensus": "pklnet-consensus-v2", "legacy": MODEL_GEOMETRY_VERSION}[policy]
        self._torch_branch_cache: dict[str, Any] = {}
        self.backend_used = "unloaded"
        self._session: Any | None = None
        self._torch: Any | None = None
        self._model: Any | None = None
        self._roi_extractor: Any | None = None
        self._inference_lock = threading.Lock()

    @property
    def available(self) -> bool:
        try:
            self._ensure_loaded()
        except PKLNetUnavailable:
            return False
        return True

    def _ensure_loaded(self) -> None:
        if self._session is not None or self._model is not None:
            return
        onnx_path = self.root / ("pklnet-keypoints-diagnostics.onnx" if self.policy != "legacy" else "pklnet-keypoints.onnx")
        if self.backend == "onnx" or (self.backend == "auto" and onnx_path.is_file()):
            try:
                import onnxruntime as ort
            except ImportError as error:
                if self.backend == "onnx":
                    raise PKLNetUnavailable("ONNX Runtime is not installed for PKLNet") from error
            else:
                with self._load_lock:
                    if self._session is not None:
                        return
                    try:
                        metadata = json.loads(onnx_path.with_suffix(".json").read_text(encoding="utf-8"))
                        if metadata["roi_geometry"] != MODEL_GEOMETRY_VERSION or metadata["input_shape"] != [1, 3, 400, 300]:
                            raise ValueError("Incompatible PKLNet ONNX geometry or input shape")
                        if self.policy != "legacy" and metadata.get("diagnostic_schema") != "pklnet-branches-v1":
                            raise ValueError("Branch diagnostics required; run tools/expose_pklnet_branches.py")
                        for path, key in ((self.weights, "weights_sha256"), (onnx_path, "onnx_sha256")):
                            if hashlib.sha256(path.read_bytes()).hexdigest() != metadata[key]:
                                raise ValueError(f"PKLNet artifact hash mismatch: {path.name}")
                        options = ort.SessionOptions()
                        options.intra_op_num_threads = self.threads or 4
                        options.inter_op_num_threads = 1
                        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                        session = ort.InferenceSession(str(onnx_path), sess_options=options, providers=["CPUExecutionProvider"])
                        if self.policy != "legacy" and not {"keypoints", "heatmap_keypoints", "fc_keypoints"}.issubset({o.name for o in session.get_outputs()}):
                            raise ValueError("PKLNet branch outputs are missing")
                        spec = importlib.util.spec_from_file_location("pklnet_roi_geometry", self.root / "roiExtractor.py")
                        geometry = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(geometry)
                        self._roi_extractor = geometry
                        self._session = session
                        self.backend_used = "onnx"
                    except Exception as error:
                        raise PKLNetUnavailable(f"PKLNet ONNX failed to load: {error}") from error
                return
        self._ensure_torch_loaded()

    def _ensure_torch_loaded(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:
                return
            if not self.root.is_dir() or not self.weights.is_file():
                raise PKLNetUnavailable(f"PKLNet files are missing under {self.root}")
            try:
                import torch
            except Exception as error:  # pragma: no cover - depends on deployment image
                raise PKLNetUnavailable("PyTorch is not installed for PKLNet") from error

            root_text = str(self.root)
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
            try:
                # Upstream targets the old torchvision.models.utils location.
                from torch.hub import load_state_dict_from_url
                compatibility = types.ModuleType("torchvision.models.utils")
                compatibility.load_state_dict_from_url = load_state_dict_from_url
                sys.modules.setdefault("torchvision.models.utils", compatibility)
                from lib.models.nets.pklnet import pklnet
                import roiExtractor

                model = pklnet()
                try:
                    state = torch.load(self.weights, map_location="cpu", weights_only=False)
                except TypeError:  # PyTorch versions before weights_only
                    state = torch.load(self.weights, map_location="cpu")
                model.load_state_dict(state)
                model.eval()
                torch.set_num_threads(self.threads or 2)
                if self.policy != "legacy":
                    model.kcr.fc_loc.register_forward_hook(lambda _m, _i, out: self._torch_branch_cache.__setitem__("theta", out.detach()))
                    model.kcr.kp_head.register_forward_hook(lambda _m, _i, out: self._torch_branch_cache.__setitem__("fc", out.detach()))
            except Exception as error:  # pragma: no cover - model environment dependent
                raise PKLNetUnavailable(f"PKLNet failed to load: {error}") from error
            self._torch = torch
            self._model = model
            self._roi_extractor = roiExtractor
            self.backend_used = "torch"

    @staticmethod
    def _prepare(image: Image.Image) -> tuple[Any, tuple[int, int], tuple[int, int], tuple[float, float]]:
        """Match PKLNet's TestLoader: rotate landscape input and pad to 400x300."""

        rgb = np.asarray(image if image.mode == "RGB" else image.convert("RGB"), dtype=np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        original_h, original_w = bgr.shape[:2]
        rotated = cv2.rotate(bgr, cv2.ROTATE_90_CLOCKWISE) if original_w > original_h else bgr
        h, w = rotated.shape[:2]
        standard = np.zeros((400, 300, 3), dtype=np.uint8)
        if float(h / w) > 4 / 3:
            converted_w = int(400.0 * w / h)
            converted_h = 400
            ratio = float(h) / 400.0
        else:
            converted_w = 300
            converted_h = int(300.0 * h / w)
            ratio = float(w) / 300.0
        resized = cv2.resize(rotated, (converted_w, converted_h), interpolation=cv2.INTER_LINEAR)
        standard[:converted_h, :converted_w] = resized

        tensor = standard.transpose(2, 0, 1).astype(np.float32) / 255.0
        tensor = (tensor - np.array([0.485, 0.456, 0.406], dtype=np.float32)[:, None, None]) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )[:, None, None]
        return tensor[None, ...], (original_h, original_w), (h, w), (w / converted_w, h / converted_h)

    @staticmethod
    def _unrotate_keypoints(kp: np.ndarray, original_size: tuple[int, int], rotated_size: tuple[int, int], ratio: tuple[float, float]) -> np.ndarray:
        scaled = (kp.reshape(-1, 2) * np.asarray(ratio)).reshape(-1).astype(np.float32)
        original_h, original_w = original_size
        if original_w > original_h:
            # Inverse of cv2.ROTATE_90_CLOCKWISE, matching PKLNet test.py.
            x = scaled[1::2].copy()
            y = original_h - 1 - scaled[0::2]
            out = np.empty_like(scaled)
            out[0::2] = x
            out[1::2] = y
            return out
        return scaled

    def extract(self, image: Image.Image, *, side: int = 128) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        if self.policy != "illumination":
            return self._extract_aspect(image, side=side)
        rgb = np.asarray(image.convert("RGB"))
        adjusted = illumination_pixels(rgb)
        original = None
        try:
            original = self._extract_aspect(image, side=side)
        except PKLNetUnavailable:
            # A degenerate original prediction may still have a usable adjusted
            # prediction. Model load failures propagate from the second attempt.
            pass
        failure = None
        overlap = None
        candidates = []
        if original is not None and original[2]["roi_geometry_valid"]:
            candidates.append({"view": "original", "quad": np.asarray(original[1]).tolist(), "valid": True})
        try:
            result = self._extract_aspect(Image.fromarray(adjusted), side=side)
            if result[2]["roi_geometry_valid"]:
                candidates.append({"view": "gamma", "quad": np.asarray(result[1]).tolist(), "valid": True})
            if not result[2]["roi_geometry_valid"]:
                failure = result[2]["roi_geometry_reason"]
            elif original is not None and original[2]["roi_geometry_valid"]:
                a = np.asarray(original[1], np.float32)
                b = np.asarray(result[1], np.float32)
                intersection = max(0.0, float(cv2.intersectConvexConvex(a, b)[0]))
                overlap = intersection / max(1e-8, cv2.contourArea(a) + cv2.contourArea(b) - intersection)
                if overlap < MIN_ILLUMINATION_IOU:
                    failure = "illumination_localization_disagreement"
        except PKLNetUnavailable as error:
            if original is None:
                raise
            failure = str(error)
        if failure is not None:
            # Keep the previous localization when enhancement jumps to a
            # different palm region. Never use identity scores to choose a view.
            raw, quad, details = original if original is not None else result
            details.update(pklnet_illumination_gamma=LOCALIZER_GAMMA,
                           pklnet_illumination_view="original_fallback" if original is not None else "gamma_invalid",
                           pklnet_illumination_failure=failure, pklnet_illumination_iou=overlap,
                           pklnet_illumination_min_iou=MIN_ILLUMINATION_IOU,
                           pklnet_roi_candidates=candidates)
            return raw, quad, details
        _, quad, details = result
        # Enhancement is only for landmark inference; biometric texture remains
        # the original exposure and passes through the existing normalization.
        raw = self._roi_extractor.getROIimg(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), quad, side=side, ratio=1.0)
        if raw is None or raw.shape != (side, side):
            raise PKLNetUnavailable("PKLNet illumination perspective transform failed")
        details.update(pklnet_illumination_gamma=LOCALIZER_GAMMA, pklnet_illumination_view="gamma",
                       pklnet_roi_pixels="original", pklnet_illumination_iou=overlap,
                       pklnet_illumination_min_iou=MIN_ILLUMINATION_IOU,
                       pklnet_roi_candidates=candidates)
        return raw.astype(np.uint8), quad, details

    def _extract_aspect(self, image: Image.Image, *, side: int = 128) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        result = self._extract_once(image, side=side)
        if self.policy not in ("aspect", "illumination"):
            return result
        raw, quad, details = result
        details.update(pklnet_aspect_retry=False, pklnet_roi_view="full",
                       pklnet_full_frame_reason=details["roi_geometry_reason"])
        if details["roi_geometry_valid"]:
            return raw, quad, details
        box = self._aspect_retry_box(image.size)
        if box == (0, 0, image.width, image.height):
            return raw, quad, details
        # Keep the original orientation. A square crop changes _prepare's
        # landscape rotation and was a failed historical localization control.
        # This second inference uses no identity, template, or previous frame.
        try:
            _candidate_raw, candidate_quad, candidate = self._extract_once(image.crop(box), side=side)
        except PKLNetUnavailable as error:
            details.update(pklnet_aspect_retry=True, pklnet_retry_box=list(box), pklnet_retry_error=str(error))
            return raw, quad, details
        offset = np.array(box[:2], np.float32)
        candidate_quad = candidate_quad + offset
        for key in ("pklnet_keypoints", "pklnet_heatmap_keypoints", "pklnet_fc_keypoints"):
            if key in candidate:
                candidate[key] = (np.asarray(candidate[key]).reshape(-1, 2) + offset).reshape(-1).tolist()
        for key in ("pklnet_heatmap_quad", "pklnet_fc_quad"):
            if key in candidate:
                candidate[key] = (np.asarray(candidate[key]) + offset).tolist()
        kp = np.asarray(candidate["pklnet_keypoints"])
        span_ratio = float(np.linalg.norm(kp[:2]-kp[2:4]) / min(image.size))
        in_bounds = bool((candidate_quad >= 0).all() and (candidate_quad[:, 0] < image.width).all()
                         and (candidate_quad[:, 1] < image.height).all())
        reason = "roi_out_of_bounds" if not in_bounds else "pklnet_keypoint_span_too_small" if span_ratio < MIN_KEYPOINT_SPAN_RATIO else None
        details.update(pklnet_aspect_retry=True, pklnet_retry_box=list(box), pklnet_retry_reason=reason)
        if reason is not None:
            return raw, quad, details
        # Warp the original pixels, not the reduced field of view. A valid
        # quadrilateral can extend outside the inference crop but inside the
        # original; cropping it again would introduce artificial black borders.
        bgr = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        candidate_raw = self._roi_extractor.getROIimg(bgr, candidate_quad, side=side, ratio=1.0)
        if candidate_raw is None or candidate_raw.shape != (side, side):
            raise PKLNetUnavailable("PKLNet aspect retry perspective transform failed")
        candidate.update(roi_quad_full=candidate_quad.tolist(), roi_in_bounds=in_bounds,
                         pklnet_keypoint_span_ratio=span_ratio, roi_geometry_valid=True, roi_geometry_reason=None,
                         pklnet_aspect_retry=True, pklnet_roi_view="center_4x3", pklnet_retry_box=list(box),
                         pklnet_full_frame_reason=details["pklnet_full_frame_reason"],
                         pklnet_full_frame_keypoints=details["pklnet_keypoints"],
                         pklnet_full_frame_quad=details["roi_quad_full"])
        return candidate_raw.astype(np.uint8), candidate_quad, candidate

    @staticmethod
    def _aspect_retry_box(size: tuple[int, int]) -> tuple[int, int, int, int]:
        width, height = size
        if width > height and width / height > 4 / 3:
            kept = round(height * 4 / 3)
            left = (width - kept) // 2
            return left, 0, left + kept, height
        if height > width and height / width > 4 / 3:
            kept = round(width * 4 / 3)
            top = (height - kept) // 2
            return 0, top, width, top + kept
        return 0, 0, width, height

    def _extract_once(self, image: Image.Image, *, side: int = 128) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        self._ensure_loaded()
        assert self._roi_extractor is not None
        tensor, original_size, rotated_size, ratio = self._prepare(image)
        branches = None
        with self._inference_lock:
            if self._session is not None:
                names = ["keypoints", "heatmap_keypoints", "fc_keypoints"] if self.policy != "legacy" else ["keypoints"]
                output = self._session.run(names, {"image": tensor})
                kp = output[0][0].astype(np.float32)
                if self.policy != "legacy":
                    branches = [value[0].astype(np.float32) for value in output[1:]]
            else:
                torch = self._torch
                assert torch is not None and self._model is not None
                with torch.inference_mode():
                    self._torch_branch_cache.clear()
                    output = self._model(torch.from_numpy(tensor))
                    if self.policy != "legacy":
                        dsntnn = sys.modules["lib.models.nets.dsntnn"]
                        heatmaps = output[5]
                        coords = dsntnn.dsnt(heatmaps)
                        coords[:, :, 0] /= 1 - 1 / heatmaps.size(2)
                        coords[:, :, 1] /= 1 - 1 / heatmaps.size(3)
                        theta = self._torch_branch_cache["theta"].reshape(1, 2, 3)
                        hm = self._model.kcr.kp_coord(coords.reshape(1, -1), theta, 300, 400)
                        fc = self._model.kcr.kp_coord(self._torch_branch_cache["fc"], theta, 300, 400)
                        branches = [v[0].cpu().numpy().astype(np.float32) for v in (hm, fc)]
                kp = output[0][0].detach().cpu().numpy().astype(np.float32)
        if self.policy in ("heatmap", "aspect", "illumination"):
            if branches is None or len(branches) != 2:
                raise PKLNetUnavailable("PKLNet heatmap output missing")
            # Fixed spatial branch for every image. Never pick a branch using
            # identity scores, and never average incompatible endpoint orders.
            kp = branches[0]
        if kp.size != 6 or not np.isfinite(kp).all():
            raise PKLNetUnavailable(f"PKLNet returned only {kp.size} keypoint values")
        kp = self._unrotate_keypoints(kp, original_size, rotated_size, ratio)
        p1 = kp[0:2]
        p2 = kp[2:4]
        anticlock = self._roi_extractor.isAntiClock(np.r_[p1, p2, kp[4:6]])
        roi_points = self._roi_extractor.getROIckp(p1, p2, anticlock)
        if roi_points is None:
            raise PKLNetUnavailable("PKLNet returned degenerate ROI keypoints")
        rgb = np.asarray(image if image.mode == "RGB" else image.convert("RGB"), dtype=np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        roi = self._roi_extractor.getROIimg(bgr, roi_points, side=side, ratio=1.0)
        if roi is None or roi.shape != (side, side):
            raise PKLNetUnavailable("PKLNet ROI perspective transform failed")
        quad = np.asarray(roi_points, dtype=np.float32)
        in_bounds = bool((quad[:, 0] >= 0).all() and (quad[:, 0] < image.width).all() and (quad[:, 1] >= 0).all() and (quad[:, 1] < image.height).all())
        span_ratio = float(np.linalg.norm(p2 - p1) / min(image.size))
        geometry_reason = "roi_out_of_bounds" if not in_bounds else "pklnet_keypoint_span_too_small" if span_ratio < MIN_KEYPOINT_SPAN_RATIO else None
        consensus = {}
        if self.policy != "legacy":
            if branches is None or len(branches) != 2:
                raise PKLNetUnavailable("PKLNet branch diagnostics missing; refusing unvalidated crop")
            native_branches = [self._unrotate_keypoints(v, original_size, rotated_size, ratio) for v in branches]
            consensus = branch_consensus(*native_branches, image.size, self._roi_extractor)
            if self.policy == "consensus" and not consensus["pklnet_consensus_valid"] and geometry_reason is None:
                geometry_reason = consensus["pklnet_consensus_reason"]
        diagnostics = {
            "roi_source": "pklnet",
            "pklnet_backend": self.backend_used,
            "pklnet_cpu_threads": self.threads or (4 if self.backend_used == "onnx" else 2),
            "roi_geometry": self.roi_geometry,
            "pklnet_policy": self.policy,
            "pklnet_preprocessing": "BGR, clockwise landscape rotation, 400x300 top-left padding, ImageNet channel normalization",
            "pklnet_keypoints": kp.tolist(),
            "roi_quad_full": quad.tolist(),
            "roi_in_bounds": in_bounds,
            "pklnet_keypoint_span_ratio": span_ratio,
            "roi_geometry_valid": geometry_reason is None,
            "roi_geometry_reason": geometry_reason,
            "min_keypoint_span_ratio": MIN_KEYPOINT_SPAN_RATIO,
            **consensus,
        }
        return roi.astype(np.uint8), quad, diagnostics


def normalize_roi_pixels(roi: np.ndarray) -> np.ndarray:
    """Normalize matcher pixels without computing unused display diagnostics."""
    array = np.asarray(roi, dtype=np.float32)
    low, high = np.percentile(array, (1, 99))
    if high - low < 1:
        raise ValueError("PKLNet crop has no usable intensity range")
    return np.clip((array - low) * 255 / (high - low), 0, 255).astype(np.uint8)


def normalize_roi(roi: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    """Apply normalization and include quality diagnostics for camera/UI callers."""
    array = np.asarray(roi, dtype=np.float32)
    quality = {"contrast": float(array.std()), "sharpness": float(np.hypot(*np.gradient(array)).var())}
    return normalize_roi_pixels(array), quality
