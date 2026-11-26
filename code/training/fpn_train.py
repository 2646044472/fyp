"""Portable FPN geometry trainer; reuses the station localizer and checkpoint ABI.

The historical slot order, source authorization, datasets and trained tensors are
not part of this program. The smoke path creates only artificial geometric input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import cv2
import numpy as np
import torch
from checkpoints import load_exact, save_terminal
from private_paths import outside_git
from torch import nn
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rasp"))
from frozen_fpn_c_e10 import CANVAS_H, CANVAS_W, Localizer, letterbox, normalize_channels

H, W = CANVAS_H, CANVAS_W
WARMUP_STEPS = 120
SEED = 20261120


def apply_affine(points, matrix):
    """Apply the same canvas affine to the chart and the pixels."""
    return np.asarray(points) @ matrix[:, :2].T + matrix[:, 2]


def pack_native(rgb, corners):
    """Convert one EXIF-oriented RGB image and ordered native corners to a canvas row."""
    canvas, back = letterbox(rgb)
    matrix = cv2.invertAffineTransform(back)
    support = cv2.warpAffine(np.ones(rgb.shape[:2], np.uint8), matrix, (W, H),
                             flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
    chart = apply_affine(corners, matrix).astype(np.float32)
    chart_target(chart, support)
    return canvas, chart, support


def chart_target(corners, support):
    """[center_x, center_y, side length, ordered axis_x, axis_y, supported]."""
    p = np.asarray(corners, dtype=np.float64)
    support = np.asarray(support)
    if support.shape != (H, W):
        raise ValueError("expected support mask on the 320x256 canvas")
    if p.shape != (4, 2) or not np.isfinite(p).all() or np.abs(p).max() > 1e6:
        raise ValueError("expected finite ordered chart corners")
    if not cv2.isContourConvex(p.astype(np.float32)) or cv2.contourArea(p.astype(np.float32), oriented=True) <= 1:
        raise ValueError("expected a clockwise nondegenerate chart in image coordinates")
    v = p[1] - p[0]
    side = np.linalg.norm(v)
    if side <= 1:
        raise ValueError("chart first edge is too short")
    center = p.mean(axis=0)
    q = np.rint(np.vstack((p, center))).astype(np.int64)
    x, y = q.T
    in_canvas = (x >= 0) & (x < W) & (y >= 0) & (y < H)
    ok = bool(in_canvas.all() and support[y, x].all())
    return np.asarray([*center, side, *(v / side), ok], dtype=np.float32)


def augment_canvas(rgb, corners, support, rng):
    """Joint affine, distal clipping and exposure perturbation used by the FPN fit."""
    transform = cv2.getRotationMatrix2D((W / 2, H / 2), float(rng.uniform(-24, 24)),
                                        float(np.exp(rng.uniform(-.17, .14))))
    transform[:, 2] += rng.uniform([-.080 * W, -.070 * H], [.080 * W, .070 * H])
    pixels = cv2.warpAffine(rgb, transform, (W, H), flags=cv2.INTER_LINEAR)
    mask = cv2.warpAffine(np.asarray(support, dtype=np.uint8), transform, (W, H),
                          flags=cv2.INTER_NEAREST)
    p = apply_affine(corners, transform)
    if rng.random() < .28:
        side = np.linalg.norm(p[1] - p[0])
        allowance = float(rng.uniform(.07, .22)) * side
        border = (p[0] + p[1]) * .5
        normal = (p[3] - p[0]) / max(side, 1)
        yy, xx = np.ogrid[:H, :W]
        outside = ((xx - border[0]) * normal[0] + (yy - border[1]) * normal[1]) < -allowance
        pixels[outside] = 0
        mask[outside] = 0
    valid = mask.astype(bool)
    pixels[valid] = np.clip(pixels[valid].astype(np.float32) * float(np.exp(rng.uniform(-.24, .24)))
                            + rng.uniform(-7, 7), 0, 255).astype(np.uint8)
    return pixels, p, mask


def make_localizer(backbone=None, digest=None, *, start_encoder=None):
    """Fresh station localizer, optional generic trunk or complete warm start."""
    if start_encoder is not None and backbone is not None:
        raise ValueError("select either a generic backbone or a full FPN checkpoint")
    if (backbone is not None and digest is None) or (backbone is None and start_encoder is None and digest is not None):
        raise ValueError("provide both the local generic backbone and its SHA-256")
    model = Localizer()
    if start_encoder is not None:
        # The full warm start already contains the trained regression-head bias.
        # Checkpoint loading does not restore Adam state, epoch or sample order.
        return load_exact(model, start_encoder, digest)
    if backbone is not None:
        from safetensors.torch import load

        if Path(backbone).suffix.casefold() != ".safetensors" or not Path(backbone).is_file():
            raise ValueError("expected a local generic .safetensors checkpoint")
        with Path(backbone).open("rb") as f:
            data = f.read((256 << 20) + 1)
        if not 0 < len(data) <= (256 << 20) or hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("generic ResNet-50 initialization hash or size mismatch")
        state = load(data)
        if (state.pop("fc.weight", torch.empty(0)).shape != (1000, 2048)
                or state.pop("fc.bias", torch.empty(0)).shape != (1000,)):
            raise ValueError("expected a generic 1000-class ResNet-50 state")
        expected = model.b.state_dict()
        if set(expected) != set(state) or any(
            state[name].dtype != value.dtype or state[name].shape != value.shape
            or not torch.isfinite(state[name]).all()
            for name, value in expected.items()
        ):
            raise ValueError("generic ResNet-50 keys, shape, dtype or values are invalid")
        model.b.load_state_dict(state, strict=True)
    # This training-only regression-head bias does not change the model schema.
    with torch.no_grad():
        last = model.reg[-1].bias
        last.copy_(last.new_tensor((-1.2, 1., 0., 0.)))
    return model


def forward_training(model, image):
    """Expose raw source heads from one shared inference forward; hooks never persist."""
    captures = {}
    heat_hook = model.heat.register_forward_hook(lambda _, args, out: captures.__setitem__("heat", out))
    reg_hook = model.reg.register_forward_hook(lambda _, args, out: captures.__setitem__("reg", out))
    try:
        corners, confidence = model(image)
    finally:
        heat_hook.remove()
        reg_hook.remove()
    heat, raw = captures["heat"], captures["reg"]
    height, width = heat.shape[-2:]
    gy, gx = torch.meshgrid(torch.arange(height, device=image.device, dtype=image.dtype),
                            torch.arange(width, device=image.device, dtype=image.dtype), indexing="ij")
    cells = torch.stack(((gx + .5) * W / width - .5, (gy + .5) * H / height - .5),
                        dim=-1).reshape(-1, 2)
    logits = heat.flatten(1)
    center = logits.softmax(dim=1) @ cells
    side = H * (.01 + 1.25 * raw[:, 0].sigmoid())
    axis = F.normalize(raw[:, 1:3], dim=1, eps=1e-8)
    return (center, side, axis, raw[:, 3], logits, cells), (corners, confidence)


def geometry_loss(intermediates, target):
    """Original supervised center, log-side, oriented axis, heat and quality objective."""
    center, side, axis, quality_logit, heat_logit, cells = intermediates
    ct, st, at, keep = target[:, :2], target[:, 2], target[:, 3:5], target[:, 5] > .5
    quality = F.binary_cross_entropy_with_logits(quality_logit, keep.float())
    if not bool(keep.any()):
        return .25 * quality
    relative = F.smooth_l1_loss((center[keep] - ct[keep]) / st[keep, None],
                                torch.zeros_like(ct[keep]), beta=.10)
    scale = F.smooth_l1_loss(side[keep].log(), st[keep].log(), beta=.12)
    orientation = (1 - (axis[keep] * at[keep]).sum(dim=1)).mean()
    heat_target = (-((ct[keep, None] - cells[None]) ** 2).sum(dim=2) / 32.).softmax(dim=1)
    heat = -(heat_target * heat_logit[keep].log_softmax(dim=1)).sum(dim=1).mean()
    return 1.4 * relative + .55 * scale + .8 * orientation + .22 * heat + .25 * quality


def make_optimizer(model):
    trunk = list(model.b.parameters())
    extra = [value for key, value in model.named_parameters() if not key.startswith("b.")]
    return torch.optim.AdamW([dict(params=trunk, peak=8e-5), dict(params=extra, peak=3e-4)],
                             lr=0., weight_decay=.002, foreach=False)


def fit_step(model, optimizer, canvases, targets, device, *, step, fraction):
    if step < 1 or not 0. <= fraction <= 1.:
        raise ValueError("invalid learning rate progress")
    model.train()
    for module in model.b.modules():
        if isinstance(module, nn.BatchNorm2d):
            module.eval()  # freeze running statistics, not affine parameters
    multiplier = min(1., step / WARMUP_STEPS) * (.1 + .9 * .5 * (1 + math.cos(math.pi * fraction)))
    for group in optimizer.param_groups:
        group["lr"] = group["peak"] * multiplier
    inputs = torch.as_tensor(np.asarray(canvases), device=device).permute(0, 3, 1, 2).float().div(255.)
    targets = torch.as_tensor(np.asarray(targets), device=device)
    optimizer.zero_grad(set_to_none=True)
    intermediates, _ = forward_training(model, normalize_channels(inputs))
    loss = geometry_loss(intermediates, targets)
    if not torch.isfinite(loss):
        raise ValueError("nonfinite geometry training objective")
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 5., error_if_nonfinite=True)
    optimizer.step()
    return float(loss.detach())


def load_course(file):
    with np.load(Path(file), allow_pickle=False) as archive:
        if set(archive.files) != {"canvas_rgb", "canvas_corners", "support_mask"}:
            raise ValueError("explicitly provide only canvas_rgb, canvas_corners, support_mask")
        rgb, corners, support = (archive[name] for name in ("canvas_rgb", "canvas_corners", "support_mask"))
    if rgb.ndim != 4 or rgb.shape[1:] != (H, W, 3) or rgb.dtype != np.uint8 or not len(rgb):
        raise ValueError("canvas_rgb must be a nonempty uint8 [N, 320, 256, 3] array")
    if corners.shape != (len(rgb), 4, 2) or corners.dtype not in (np.float32, np.float64):
        raise ValueError("canvas_corners must be a float [N, 4, 2] array")
    if support.shape != (len(rgb), H, W) or support.dtype not in (np.bool_, np.uint8):
        raise ValueError("support_mask must be bool or uint8 [N, 320, 256]")
    if support.dtype == np.uint8 and support.max() > 1:
        raise ValueError("support_mask values must be 0 or 1")
    for p, mask in zip(corners, support):
        chart_target(p, mask)
    return rgb, corners, support


def synthetic_rows():
    y, x = np.indices((H, W))
    a = np.stack(((x + y) % 256, x % 256, (2 * y) % 256), axis=-1).astype(np.uint8)
    p = np.array(((50, 85), (180, 85), (180, 215), (50, 215)), dtype=np.float32)
    full = np.ones((H, W), dtype=np.uint8)
    partial = full.copy()
    partial[80:90, 45:55] = 0
    return np.stack((a, a.copy())), np.stack((p, p.copy())), np.stack((full, partial))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true", help="perform one synthetic CPU optimizer update")
    mode.add_argument("--npz", type=Path, help="explicit user-authorized local FIT-only canvas archive")
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--no-augment", action="store_true")
    warm = p.add_mutually_exclusive_group()
    warm.add_argument("--init-backbone", "--generic-backbone", type=Path,
                      help="local torchvision ResNet-50 safetensors with generic 1000-way head")
    warm.add_argument("--start-encoder", type=Path,
                      help="local full station FPN checkpoint; optimizer and schedule restart")
    p.add_argument("--init-sha256", "--generic-sha256", help="expected local input digest")
    p.add_argument("--save", "--output", type=Path,
                   help="new local .safetensors file outside the source tree")
    a = p.parse_args(argv)
    if min(a.epochs, a.batch_size, a.threads) < 1:
        p.error("epochs, batch size and thread count must be positive")
    if a.smoke and (a.device != "cpu" or a.save or a.init_backbone or a.start_encoder or a.init_sha256):
        p.error("smoke uses only synthetic CPU input and never reads or writes weights")
    if a.init_backbone is not None and a.init_sha256 is None:
        p.error("--init-backbone requires --init-sha256")
    if a.init_sha256 is not None and a.init_backbone is None and a.start_encoder is None:
        p.error("--init-sha256 requires --init-backbone or --start-encoder")
    if a.device == "cuda" and not torch.cuda.is_available():
        p.error("CUDA requested but not available; use explicit --device cpu")
    if a.save is not None:
        if (not a.save.parent.is_dir() or a.save.suffix.casefold() != ".safetensors"
                or a.save.exists() or a.save.is_symlink()
                or not outside_git(a.save)):
            p.error("--save expects a new .safetensors file outside the source tree")
    if a.npz is not None and not outside_git(a.npz):
        p.error("FIT arrays must be outside Git checkouts")
    torch.set_num_threads(a.threads)
    cv2.setNumThreads(1)
    torch.manual_seed(SEED)
    rgb, corners, support = synthetic_rows() if a.smoke else load_course(a.npz)
    model = make_localizer(a.init_backbone, a.init_sha256, start_encoder=a.start_encoder).to(a.device)
    optimizer = make_optimizer(model)
    step, epochs, batch_size = 0, (1 if a.smoke else a.epochs), (2 if a.smoke else a.batch_size)
    for epoch in range(epochs):
        rng = np.random.default_rng(SEED + 2077 * epoch)
        order = rng.permutation(len(rgb))
        count = 0
        for offset in range(0, len(order), batch_size):
            images, targets = [], []
            for k in order[offset:offset + batch_size]:
                im, c, mask = rgb[k], corners[k], support[k]
                if not a.smoke and not a.no_augment and rng.random() < .80:
                    im, c, mask = augment_canvas(im, c, mask, rng)
                images.append(im)
                targets.append(chart_target(c, mask))
            step += 1
            count += int(np.asarray(targets)[:, 5].sum())
            loss = fit_step(model, optimizer, images, targets, a.device, step=step,
                            fraction=(epoch + (offset + len(images) / 2) / len(order)) / epochs)
            if epoch == 0 and offset == 0 and a.smoke:
                grad = model.b.conv1.weight.grad
                if grad is None or not bool(torch.isfinite(grad).all()) or not bool(grad.abs().sum()):
                    raise RuntimeError("synthetic update did not reach the FPN backbone")
        print(json.dumps({"synthetic": a.smoke, "epoch": epoch + 1, "planned": len(order),
                          "supported_after_augmentation": count, "optimizer_steps": step,
                          "last_geometry_loss": loss}, allow_nan=False))
    if a.save is not None:
        save_terminal(model, a.save)


if __name__ == "__main__":
    main()
