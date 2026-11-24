#!/usr/bin/env python3
"""Synthetic CPU contract checks for the score-only FPN+C E10 CLI."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

import numpy as np
from PIL import Image

import fpn_c_e10_shadow as sut


def invoke(argv, backend):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = sut.main(argv, backend=backend)
    return status, json.loads(out.getvalue() or err.getvalue())


def test():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "fpn.safetensors").write_bytes(b"synthetic fpn")
        (root / "c.safetensors").write_bytes(b"synthetic c")
        p = root / "manifest.json"
        conf = {"schema": 1, "pipeline": sut.PIPELINE, "assets": {
            k: {"file": k + ".safetensors", "sha256": sut.checksum(root / (k + ".safetensors"))}
            for k in sut.ASSETS
        }}
        p.write_text(json.dumps(conf))
        calls = []
        features = np.zeros((6, 512), dtype=np.float32)
        features[0, 0] = 1
        features[1:5, 1] = 1
        features[5, :2] = 1  # last reference wins, cosine 1/sqrt(2) rather than mean.
        backend = SimpleNamespace(
            load_fpn=lambda f, d, *, device: calls.append(("fpn", device)) or "fpn",
            load_c=lambda f, d, *, device: calls.append(("c", device)) or "c",
            crop_gray=lambda m, rgb, *, device: (np.repeat(rgb[0, 0, :1], 128*128).reshape(128, 128), None, None),
            encode_c=lambda m, crops, *, device: features,
        )
        args = ["--manifest", str(p)]
        status, data = invoke([*args, "preflight"], backend)
        assert status == 0 and set(data) == {"mode", "status", "pipeline"}
        assert calls == [("fpn", "cpu"), ("c", "cpu")]

        # Valid config and independent synthetic images, no matte or camera involved.
        files = [root / (str(i) + ".png") for i in range(6)]
        for i, path in enumerate(files):
            Image.fromarray(np.full((128, 128, 3), i + 1, dtype=np.uint8)).save(path)
        scoring = [*args, "shadow-score", "--query", str(files[0]), "--enroll", *map(str,files[1:])]
        status, data = invoke(scoring, backend)
        assert status == 0 and abs(data["max_cosine"] - 2 ** -0.5) < 1e-10
        assert set(data) == {"mode", "status", "pipeline", "max_cosine"} and "decision" not in data

        dup = scoring[:-1] + [str(files[1])]
        status, error = invoke(dup, backend)
        assert status == 2 and error["reason"] == "requires_one_query_and_five_distinct_images"
        assert "max_cosine" not in error

        # Separates lost enrollment from lower match score.
        crop = backend.crop_gray
        backend.crop_gray = lambda m, x, device: (None, "no_roi", None) if int(x[0, 0, 0]) == 4 else crop(m, x, device=device)
        status, error = invoke(scoring, backend)
        assert status == 2 and error["reason"] == "roi_unavailable_enrollment" and "max_cosine" not in error
        backend.crop_gray = crop

        features[-1, 0] = np.nan
        status, error = invoke(scoring, backend)
        assert status == 2 and error["reason"] == "score_nonfinite_or_empty" and "max_cosine" not in error

        # Corrupt checkpoint must fail before our model loader is called.
        (root / "c.safetensors").write_bytes(b"modified")
        calls.clear()
        status, error = invoke([*args, "preflight"], backend)
        assert status == 2 and error["reason"] == "asset_digest_mismatch_c" and not calls
        p.write_text(json.dumps(conf).replace("c.safetensors", "../not-allowed.safetensors"))
        status, error = invoke([*args, "preflight"], backend)
        assert status == 2 and error["reason"] == "asset_contract_mismatch_c" and not calls
        p.write_text('{"schema":1,"schema":1}')
        status, error = invoke([*args, "preflight"], backend)
        assert status == 2 and error["reason"] == "manifest_missing_or_invalid"
    print("PASS: score-only max, five distinct references, missing ROI, nonfinite score, strict manifest; no real model/images")


if __name__ == "__main__":
    test()
