"""Portable C E10-style fit using the exact native C inference definition."""
import argparse
import importlib.util
import json
from pathlib import Path
import torch
from torch import nn
from checkpoints import load_exact, save_terminal
from objectives import pair_arc_loss, warm_cosine
from paired_data import load_paired, synthetic_paired

PEAK = {"early": 3e-5, "late": 1e-4, "global": 3e-4, "local": 3e-4, "arc": 3e-4}


def inference_module():
    p = Path(__file__).resolve().parents[1] / "rasp" / "frozen_fpn_c_e10.py"
    spec = importlib.util.spec_from_file_location("_fyp_frozen_native", p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parts(model):
    if not isinstance(model.trunk.head.fc, nn.Identity):
        raise ValueError("remove generic classifier before grouping parameters")
    t = model.trunk
    def group(*nodes):
        return [p for n in nodes for p in n.parameters()]
    buckets = {"early": group(t.stem, t.stages[0], t.stages[1]),
               "late": group(t.stages[2], t.stages[3], t.norm_pre, t.head),
               "local": group(model.local_proj, model.local_fc),
               "global": group(model.global_fc)}
    all_ids = [id(p) for ps in buckets.values() for p in ps]
    if len(set(all_ids)) != len(all_ids) or set(all_ids) != {id(p) for p in model.parameters()}:
        raise ValueError("unassigned or duplicate trainable model parameters")
    return buckets


def build(core, init_backbone=None, start_encoder=None, digest=None):
    if init_backbone is not None and start_encoder is not None:
        raise ValueError("generic initialization and encoder warm start are alternatives")
    model = core.NativeConvNeXtV2()
    if init_backbone is not None:
        load_exact(model.trunk, init_backbone, digest)
    model.discard_generic_classifier()
    if start_encoder is not None:
        load_exact(model, start_encoder, digest)
    return model


def run(data, model, core, device, heartbeat=None):
    model.to(device).train()
    groups = parts(model)
    for p in groups["early"]:
        p.requires_grad_(False)
    proxies = nn.ParameterList([nn.Parameter(torch.empty(n, 512, device=device))
                                for n in data.class_counts])
    for p in proxies:
        nn.init.xavier_uniform_(p)
    groups["arc"] = list(proxies)
    optimizer = torch.optim.AdamW([{"params": ps, "part": k, "lr": 0.}
                                    for k, ps in groups.items()],
                                  weight_decay=.001, foreach=False)
    params = [p for ps in groups.values() for p in ps]
    total = len(data.batches)
    first = int(data.epoch_start[1])
    reports = []
    for ep, (begin, end) in enumerate(zip(data.epoch_start[:-1], data.epoch_start[1:])):
        if ep == 1:
            for p in groups["early"]:
                p.requires_grad_(True)
        sum_loss, seen = 0., set()
        for step in range(int(begin), int(end)):
            instant = step + 1
            for g in optimizer.param_groups:
                k = g["part"]
                f = (0. if ep == 0 else warm_cosine(instant - first, total - first)) if k == "early" else warm_cosine(instant, total)
                g["lr"] = PEAK[k] * f
            row = data.step(step)
            px = torch.as_tensor(data.gray[row.rows], device=device).unsqueeze(1).float().div(255.)
            valid = torch.as_tensor(row.valid, device=device)
            labels = torch.as_tensor(row.labels, device=device)
            optimizer.zero_grad(set_to_none=True)
            x = model(core.normalize_channels(px))
            if x.shape != (len(row.rows), 512) or not torch.isfinite(x).all():
                raise ValueError("invalid C encoder train output")
            z = x.new_zeros((2, valid.shape[1], 512))
            z[valid] = x
            loss, _, _ = pair_arc_loss(z, proxies[row.source], valid, labels)
            if not torch.isfinite(loss):
                raise ValueError("nonfinite fitting objective")
            loss.backward()
            nn.utils.clip_grad_norm_(params, 5., error_if_nonfinite=True)
            optimizer.step()
            seen.update(map(int, row.rows))
            sum_loss += float(loss.detach())
        summary = {"epoch": ep + 1, "updates": int(end - begin),
                   "unique_fit_crops_seen": len(seen), "early_trainable": ep > 0,
                   "mean_loss": sum_loss / (end - begin)}
        reports.append(summary)
        if heartbeat is not None:
            heartbeat(summary)
    model.eval()
    return reports


def main(argv=None):
    arg = argparse.ArgumentParser(description=__doc__)
    inputs = arg.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--smoke", action="store_true", help="train two steps on artificial pixels")
    inputs.add_argument("--data", type=Path, help="explicit local-only FIT .npz")
    warm = arg.add_mutually_exclusive_group()
    warm.add_argument("--init-backbone", type=Path, help="local generic timm state (.safetensors)")
    warm.add_argument("--start-encoder", type=Path, help="local C state to warm start; optimizer restarts")
    arg.add_argument("--init-sha256", help="independent expected digest for the input state")
    arg.add_argument("--save", type=Path, help="new local terminal .safetensors path outside this repo")
    arg.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    arg.add_argument("--threads", type=int, default=1)
    arg.add_argument("--seed", type=int, default=20261120)
    a = arg.parse_args(argv)
    if a.threads < 1 or (a.device == "cuda" and not torch.cuda.is_available()):
        arg.error("bad CPU thread count or CUDA unavailable")
    if a.init_sha256 and (a.init_backbone is None and a.start_encoder is None):
        arg.error("--init-sha256 requires a local input state")
    if a.smoke and (a.init_backbone or a.start_encoder):
        arg.error("synthetic smoke must not read existing weights")
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    torch.set_float32_matmul_precision("highest")
    if a.device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
    data = synthetic_paired() if a.smoke else load_paired(a.data)
    core = inference_module()
    model = build(core, a.init_backbone, a.start_encoder, a.init_sha256)
    rows = run(data, model, core, a.device, lambda row: print(json.dumps(row), flush=True))
    # Use the tracked inference entry, not a second implementation.
    check = core.encode_c(model, data.gray[:min(2, len(data.gray))], a.device)
    if check.shape[1] != 512:
        raise RuntimeError("unexpected inference ABI")
    if a.save:
        save_terminal(model, a.save)
    print(json.dumps({"synthetic": a.smoke, "fit_only": True,
                      "steps": sum(x["updates"] for x in rows), "inference_shape": list(check.shape),
                      "local_checkpoint_saved": a.save is not None}))


if __name__ == "__main__":
    main()
