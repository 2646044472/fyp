"""Portable native implementations of the frozen research inference interfaces.

PyTorch only. Registered parameter names match the project's checkpoint schemas.
The caller supplies release identities through an independently trusted local manifest.
No camera, data store, network, or matcher/threshold is opened here.
"""

import hashlib
import math
from pathlib import Path
import re

import cv2
import numpy as np
from PIL import Image
import timm
import torch
from torch import nn
from torch.nn import functional as F
from torchvision.models import resnet50


CANVAS_H = 320
CANVAS_W = 256
CROP_PX = 128
MAX_CHECKPOINT_BYTES = 256 << 20
MEAN = (.485, .456, .406)
STD = (.229, .224, .225)


def normalize_channels(x):
    mean = x.new_tensor(MEAN).reshape(1, 3, 1, 1)
    std = x.new_tensor(STD).reshape(1, 3, 1, 1)
    return (x - mean) / std


class Localizer(nn.Module):
    """Single chart predicted on a stride-4 FPN from ResNet-50 stages."""

    def __init__(self):
        super().__init__()
        self.b = resnet50(weights=None)
        self.b.fc = nn.Identity()
        self.lat = nn.ModuleList([
            nn.Sequential(nn.Conv2d(channels, 64, 1, bias=False), nn.GroupNorm(8, 64))
            for channels in (256, 512, 1024, 2048)
        ])
        self.finish = nn.Sequential(
            nn.Conv2d(64, 64, 3, padding=1, bias=False),
            nn.GroupNorm(8, 64),
            nn.SiLU(),
        )
        self.heat = nn.Conv2d(64, 1, 1)
        self.reg = nn.Sequential(nn.Linear(128, 96), nn.LayerNorm(96), nn.SiLU(), nn.Linear(96, 4))

    def forward(self, pixels):
        net = self.b
        stage = net.maxpool(net.relu(net.bn1(net.conv1(pixels))))
        pyramid = []
        for layer, lateral in zip((net.layer1, net.layer2, net.layer3, net.layer4), self.lat):
            stage = layer(stage)
            pyramid.append(lateral(stage))

        fused = pyramid[-1]
        for level in reversed(pyramid[:-1]):
            fused = level + F.interpolate(fused, size=level.shape[-2:], mode="bilinear", align_corners=False)
        fused = self.finish(fused)
        logits = self.heat(fused).flatten(1)
        height, width = fused.shape[-2:]
        gy, gx = torch.meshgrid(
            torch.arange(height, device=pixels.device, dtype=pixels.dtype),
            torch.arange(width, device=pixels.device, dtype=pixels.dtype),
            indexing="ij",
        )
        cells = torch.stack(((gx + .5) * CANVAS_W / width - .5,
                             (gy + .5) * CANVAS_H / height - .5), dim=-1).reshape(-1, 2)
        attention = logits.softmax(dim=1)
        center = attention @ cells
        local = (attention[:, None] * fused.flatten(2)).sum(dim=2)
        deep = pyramid[-1].mean(dim=(2, 3))
        side_axis_conf = self.reg(torch.cat((local, deep), dim=1))

        side = CANVAS_H * (.01 + 1.25 * side_axis_conf[:, 0].sigmoid())
        axis = F.normalize(side_axis_conf[:, 1:3], dim=1, eps=1e-8)
        perpendicular = torch.stack((-axis[:, 1], axis[:, 0]), dim=1)
        basis = torch.stack((axis, perpendicular), dim=1)
        square = pixels.new_tensor(((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)))
        corners = center[:, None] + side[:, None, None] * (square @ basis)
        return corners, side_axis_conf[:, 3].sigmoid()


def letterbox(native_rgb):
    if native_rgb.dtype != np.uint8 or native_rgb.ndim != 3 or native_rgb.shape[-1] != 3:
        raise ValueError("expected uint8 HWC RGB")
    height, width = native_rgb.shape[:2]
    if min(height, width) <= 12:
        raise ValueError("image too small")
    scale = min((CANVAS_W - 2) / width, (CANVAS_H - 2) / height)
    offset_x = (CANVAS_W - scale * width) / 2 + (scale - 1) / 2
    offset_y = (CANVAS_H - scale * height) / 2 + (scale - 1) / 2
    forward = np.asarray(((scale, 0., offset_x), (0., scale, offset_y)), dtype=np.float64)
    canvas = cv2.warpAffine(native_rgb, forward, (CANVAS_W, CANVAS_H),
                            flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return canvas, cv2.invertAffineTransform(forward)


@torch.inference_mode()
def crop_gray(fpn, rgb, device="cpu"):
    """Return uint8 (128,128) or None, a stage code, and ordered native corners."""
    canvas, back = letterbox(rgb)
    x = torch.as_tensor(canvas[None], device=device).permute(0, 3, 1, 2).float() / 255.
    corners, confidence = fpn(normalize_channels(x))
    chart = corners[0].cpu().numpy() @ back[:, :2].T + back[:, 2]
    if confidence[0].item() < .5:
        return None, "low_chart_confidence", chart

    p = np.asarray(chart, dtype=np.float32)
    height, width = rgb.shape[:2]
    if (p.shape != (4, 2) or not np.isfinite(p).all() or (p < 0).any()
            or (p > [width - 1, height - 1]).any()
            or not cv2.isContourConvex(p) or cv2.contourArea(p, oriented=True) <= 1):
        return None, "invalid_original_geometry", chart

    target = np.float32(((0, 0), (CROP_PX, 0), (CROP_PX, CROP_PX), (0, CROP_PX)))
    matrix = cv2.getPerspectiveTransform(p, target)
    crop = cv2.warpPerspective(rgb, matrix, (CROP_PX, CROP_PX), flags=cv2.INTER_LINEAR)
    direction = Image.Resampling.BILINEAR
    author_style = Image.fromarray(crop).resize((112, 112), direction).convert("L")
    gray = np.array(author_style.resize((CROP_PX, CROP_PX), direction))
    return (gray, "valid", chart) if np.ptp(gray) else (None, "constant_native_gray", chart)


class NativeConvNeXtV2(nn.Module):
    """One 256-dimensional global and one 256-dimensional local descriptor."""

    def __init__(self):
        super().__init__()
        if timm.__version__ != "0.9.16":
            raise RuntimeError("expected timm 0.9.16")
        self.trunk = timm.create_model("convnextv2_tiny", pretrained=False, num_classes=1000,
                                       drop_path_rate=0., drop_rate=0.)
        self.global_fc = nn.Linear(768, 256, bias=False)
        self.local_proj = nn.Conv2d(192, 32, 1, bias=False)
        self.local_fc = nn.Linear(512, 256, bias=False)

    def discard_generic_classifier(self):
        self.trunk.reset_classifier(num_classes=0)
        if not isinstance(self.trunk.head.fc, nn.Identity):
            raise ValueError("could not remove classifier")
        return self

    def forward(self, x):
        if x.ndim != 4 or x.shape[1:] != (3, CROP_PX, CROP_PX):
            raise ValueError("expected normalized gray NCHW with 3 channels")
        trunk = self.trunk
        stage0 = trunk.stages[0](trunk.stem(x))
        middle = trunk.stages[1](stage0)
        top = trunk.stages[3](trunk.stages[2](middle))
        deep = trunk.forward_head(trunk.norm_pre(top))
        local_pooled = F.avg_pool2d(self.local_proj(middle), kernel_size=4, stride=4).flatten(1)
        global_vector = F.normalize(self.global_fc(deep), dim=1, eps=1e-6)
        local_vector = F.normalize(self.local_fc(local_pooled), dim=1, eps=1e-6)
        return torch.cat((global_vector, local_vector), dim=1) * math.sqrt(.5)


@torch.inference_mode()
def encode_c(model, batch_nhw_u8, device="cpu"):
    gray = np.asarray(batch_nhw_u8)
    if gray.dtype != np.uint8 or gray.ndim != 3 or gray.shape[1:] != (CROP_PX, CROP_PX):
        raise ValueError("expected uint8[N,128,128] grayscale")
    if not len(gray):
        return np.empty((0, 512), dtype=np.float32)
    x = torch.as_tensor(gray, device=device).unsqueeze(1).float().div(255)
    return model(normalize_channels(x)).detach().cpu().numpy()


def _load(model, local_path, digest, device, expected_size=None):
    from safetensors.torch import load

    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("expected full local SHA256")
    path = Path(local_path)
    if not path.is_file():
        raise ValueError("expected local file")
    with path.open("rb") as handle:
        data = handle.read(MAX_CHECKPOINT_BYTES + 1)
    if not 0 < len(data) <= MAX_CHECKPOINT_BYTES or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("invalid checkpoint size or digest")

    actual = load(data)
    expected = model.state_dict()
    if actual.keys() != expected.keys() or (expected_size is not None and len(actual) != expected_size):
        raise ValueError("unexpected tensor layout")
    for key, parameter in expected.items():
        tensor = actual[key]
        if tensor.shape != parameter.shape or tensor.dtype != parameter.dtype:
            raise ValueError("unexpected tensor layout")
    model.load_state_dict(actual, strict=True)
    return model.requires_grad_(False).eval().to(device)


def load_fpn(path, sha256, device="cpu"):
    return _load(Localizer(), path, sha256, device)


def load_c(path, sha256, device="cpu"):
    return _load(NativeConvNeXtV2().discard_generic_classifier(), path, sha256, device, expected_size=201)
