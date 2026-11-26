"""Exercise documented development entry points on generated examples, offline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    # No live inputs, CUDA, model downloads, or caller-provided model paths.
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "HF_HUB_OFFLINE": "1",
           "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "PYTHONDONTWRITEBYTECODE": "1"}
    print("+ python", *args, flush=True)
    subprocess.run([sys.executable, *args], cwd=ROOT, env=env, check=True)


def core():
    run("code/evaluation/paired_outcomes.py", "--self-test")
    run("code/experiments/coverage_policy.py")
    run("-m", "unittest", "discover", "-s", "code/evaluation", "-p", "test_rank_features.py")
    run("-m", "pytest", "-q", "-p", "no:cacheprovider", "code/experiments")
    for check in ("best_frame", "review", "ranked_window", "adapter", "render",
                  "fpn_c_e10_shadow", "fpn_c_e10_station"):
        run(f"code/rasp/verify_{check}.py")


def native():
    run("code/rasp/verify_fpn_c_e10_native.py")
    run("code/experiments/train.py", "--device", "cpu", "--mode", "geometry")


def training():
    run("-m", "pytest", "-q", "-p", "no:cacheprovider", "code/training")
    # Use the CLIs, not calls to internal functions. The actual training exports
    # must load through the unchanged station preflight in a new interpreter.
    # Synthetic state files exist only for the lifetime of this directory.
    with tempfile.TemporaryDirectory(prefix="fyp-recovery-") as folder:
        base = Path(folder)
        fpn, c = base / "synthetic-fpn.safetensors", base / "synthetic-c.safetensors"
        # Exercise the same private-input interfaces a developer will use. Never
        # read source images: create small random arrays in a fresh directory.
        inputs = base / "examples"
        run("code/training/synthetic_inputs.py", "--out-dir", str(inputs))
        fit = base / "scheduled.npz"
        run("code/training/make_fit_schedule.py", "--input", str(inputs / "crops.npz"),
            "--output", str(fit), "--epochs", "2", "--width", "2", "--seed", "17")
        run("code/training/fpn_train.py", "--npz", str(inputs / "geometry.npz"), "--epochs", "1",
            "--batch-size", "2", "--save", str(fpn))
        run("code/training/convnext_e10.py", "--data", str(fit), "--save", str(c))
        run("code/training/palmbridge_train.py", "--data", str(fit),
            "--save", str(base / "synthetic-pb.safetensors"))
        assets = {}
        for role, file in (("fpn", fpn), ("c", c)):
            with file.open("rb") as stream:
                assets[role] = {"file": file.name, "sha256": hashlib.file_digest(stream, "sha256").hexdigest()}
        manifest = base / "synthetic-manifest.json"
        manifest.write_text(json.dumps({"schema": 1, "pipeline": "fpn-c-e10-frozen",
                                        "assets": assets}), encoding="utf-8")
        run("code/rasp/fpn_c_e10_shadow.py", "--manifest", str(manifest), "preflight")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("all", "core", "native", "training"), default="all", nargs="?")
    suite = parser.parse_args().suite
    for name, check in (("core", core), ("native", native), ("training", training)):
        if suite in ("all", name):
            check()
    print(f"PASS: {suite} recovery checks (synthetic CPU only)", flush=True)


if __name__ == "__main__":
    main()
