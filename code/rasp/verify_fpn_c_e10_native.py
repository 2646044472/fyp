#!/usr/bin/env python3
"""Exercise the real PyTorch CPU architecture with randomized data/weights only."""

from pathlib import Path
import tempfile

import numpy as np
import torch

import frozen_fpn_c_e10 as model


def test():
    torch.set_num_threads(2)
    torch.manual_seed(2)
    c = model.NativeConvNeXtV2().discard_generic_classifier().eval().requires_grad_(False)
    assert len(c.state_dict()) == 201
    gray = np.random.default_rng(10).integers(0, 255, (3, 128, 128), dtype=np.uint8)
    v = model.encode_c(c, gray)
    assert v.shape == (3, 512) and v.dtype == np.float32 and np.isfinite(v).all()
    assert np.allclose(np.linalg.norm(v, axis=1), 1., atol=1e-6)

    fpn = model.Localizer().eval().requires_grad_(False)
    rgb = np.random.default_rng(12).integers(0, 255, (480, 640, 3), dtype=np.uint8)
    crop, reason, quad = model.crop_gray(fpn, rgb)
    assert quad.shape == (4, 2) and np.isfinite(quad).all()
    assert isinstance(reason, str) and (crop is None or crop.shape == (128, 128))

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "synthetic.safetensors"
        path.write_bytes(b"not a checkpoint")
        for load in (model.load_fpn, model.load_c):
            try:
                load(path, "0" * 64)
            except ValueError as error:
                assert str(error) == "invalid checkpoint size or digest"
            else:
                raise AssertionError("wrong digest accepted")
    print("PASS: actual PyTorch CPU FPN/C architecture, synthetic inputs, strict readers; no real checkpoint or picture")


if __name__ == "__main__":
    test()
