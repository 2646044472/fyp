"""Portable local FIT-only adapter for PalmBridge E10.

Run with --smoke for a data-free optimizer smoke or provide an authorized
native grayscale NPZ. This does not bundle or recreate the historical private
course/roles, and synthetic smoke is not model accuracy or Pi validation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

from checkpoints import load_exact, save_terminal
from objectives import pair_arc_loss, warm_cosine
from paired_data import load_paired, synthetic_paired
from private_paths import outside_git
from palmbridge import EMBED_DIM, PalmBridgeE10, normalize_gray

PEAKS = {"late": 1e-4, "early": 3e-5, "global": 3e-4, "local": 3e-4, "arc": 3e-4}


def fit_objective(
    model: PalmBridgeE10,
    gray: torch.Tensor,
    valid: torch.Tensor,
    labels: torch.Tensor,
    proxies: torch.Tensor,
    use_bridge_for_supervision: bool,
):
    if (
        valid.ndim != 2
        or valid.shape[0] != 2
        or valid.dtype != torch.bool
        or labels.shape != valid.shape
        or gray.shape[0] != int(valid.sum())
    ):
        raise ValueError("expected mask-aligned real pixels and a 2×P source-local batch")
    z, raw_bridge, word, _ = model.components(normalize_gray(gray))
    supervision = F.normalize(raw_bridge, dim=-1) if use_bridge_for_supervision else z
    packed = z.new_zeros((*valid.shape, EMBED_DIM))
    packed[valid] = supervision
    shared, pair, angular = pair_arc_loss(packed, proxies, valid, labels)
    commitment, orthogonal = model.bridge.penalties(z, word)
    return shared + 0.1 * commitment + orthogonal, {
        "pair": pair,
        "angular": angular,
        "commitment": commitment,
        "orthogonal": orthogonal,
    }


def fit(data, *, device: str = "cpu", initialize: Path | None = None, digest: str | None = None):
    """Fit the provided local course in order. Returns model and aggregate diagnostics."""
    model = PalmBridgeE10().to(device)
    if initialize is not None:
        load_exact(model, initialize, digest)
    proxies = nn.ParameterList(
        [nn.Parameter(torch.empty(classes, EMBED_DIM, device=device)) for classes in data.class_counts]
    )
    for proxy in proxies:
        nn.init.xavier_uniform_(proxy)
    groups = model.parameter_groups()
    groups["arc"] = list(proxies.parameters())
    all_parameters = [p for group in groups.values() for p in group]
    if len({id(p) for p in all_parameters}) != len(all_parameters) or len(all_parameters) != (
        len(list(model.parameters())) + len(list(proxies.parameters()))
    ):
        raise RuntimeError("optimizer groups do not cover each trainable parameter exactly once")
    opt = torch.optim.AdamW(
        [{"params": group, "lr": 0.0, "name": name} for name, group in groups.items()],
        weight_decay=0.001,
        foreach=False,
    )
    total = int(data.epoch_start[-1])
    first_epoch_length = int(data.epoch_start[1])
    delay = round(total * 5 / 200)
    loss_mean = 0.0
    singleton_updates = 0
    for epoch, (begin, end) in enumerate(zip(data.epoch_start, data.epoch_start[1:])):
        model.train()
        for group in model.early_modules():
            group.requires_grad_(epoch > 0)
            group.train(mode=epoch > 0)
        for i in range(int(begin), int(end)):
            batch = data.step(i)
            pixels = torch.as_tensor(data.gray[batch.rows], device=device)
            active = torch.as_tensor(batch.valid, dtype=torch.bool, device=device)
            labels = torch.as_tensor(batch.labels, dtype=torch.long, device=device)
            update = i + 1
            for group in opt.param_groups:
                name = group["name"]
                rate = (
                    warm_cosine(max(0, update - first_epoch_length), total - first_epoch_length)
                    if name == "early"
                    else warm_cosine(update, total)
                )
                group["lr"] = PEAKS[name] * rate
            opt.zero_grad(set_to_none=True)
            loss, _ = fit_objective(
                model,
                pixels,
                active,
                labels,
                proxies[batch.source],
                use_bridge_for_supervision=update > delay,
            )
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError("nonfinite training loss")
            loss.backward()
            nn.utils.clip_grad_norm_(all_parameters, max_norm=5.0, error_if_nonfinite=True)
            opt.step()
            loss_mean += float(loss.detach())
            singleton_updates += int(len(batch.rows) == 1)
    return model.eval(), {
        "epochs": len(data.epoch_start) - 1,
        "updates": total,
        "mean_loss": loss_mean / total,
        "singleton_updates": singleton_updates,
        "seeded_from_local_state": initialize is not None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", "--synthetic", dest="smoke", action="store_true", help="train only on generated arrays")
    mode.add_argument("--data", "--fit-npz", dest="data", type=Path, help="authorized local FIT data, with predeclared course")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261120)
    parser.add_argument("--save", "--output", dest="save", type=Path, help="optional new model file, outside the source tree")
    parser.add_argument("--start-encoder", "--initialize", dest="start_encoder", type=Path, help="trusted local model-only initializer; this is not optimizer resume")
    parser.add_argument("--init-sha256", help="independent expected SHA-256 of the initializer")
    args = parser.parse_args(argv)
    if args.threads < 1 or (args.device == "cuda" and not torch.cuda.is_available()):
        parser.error("bad CPU thread count or CUDA unavailable")
    if args.smoke and args.start_encoder is not None:
        parser.error("synthetic smoke does not read an existing checkpoint")
    if args.init_sha256 is not None and args.start_encoder is None:
        parser.error("--init-sha256 requires --start-encoder")
    if args.save is not None:
        output = args.save.parent.resolve(strict=True) / args.save.name
        if (output.suffix.casefold() != ".safetensors" or output.exists() or output.is_symlink()
                or not outside_git(output)):
            parser.error("choose a new .safetensors path outside the source tree")
    if args.data is not None:
        npz = args.data.resolve(strict=True)
        if not outside_git(npz):
            parser.error("FIT arrays must be outside Git checkouts")
    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision("highest")
    if args.device == "cuda":
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
    data = synthetic_paired() if args.smoke else load_paired(args.data)
    model, result = fit(data, device=args.device, initialize=args.start_encoder, digest=args.init_sha256)
    with torch.inference_mode():
        probe = torch.as_tensor(data.gray[:min(2, len(data.gray))], device=args.device)
        vector = model.encode(probe)
        if vector.shape != (len(probe), EMBED_DIM) or not bool(torch.isfinite(vector).all()):
            raise RuntimeError("unexpected PalmBridge inference ABI")
    if args.save is not None:
        save_terminal(model, args.save)
    result.update(synthetic=args.smoke, fit_only=True, inference_shape=list(vector.shape),
                  local_checkpoint_saved=args.save is not None)
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
