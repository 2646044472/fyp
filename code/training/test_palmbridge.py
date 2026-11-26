"""Only synthetic tensors and tmp-path model states; no provider assets."""
import hashlib
import json

import pytest
import torch
from torch.nn import functional as F

from checkpoints import load_exact, save_terminal
from palmbridge import CodewordBridge, PalmBridgeE10, RegularBinMean, normalize_gray, slot_dot
from palmbridge_train import main


def test_gray_normalization_zero_and_unbiased():
    gray = torch.zeros((3, 128, 128), dtype=torch.uint8)
    gray[1, 0, 0] = 128
    gray[2, 0, :3] = torch.tensor([32, 64, 96])
    x = normalize_gray(gray)
    assert x.shape == (3, 1, 128, 128)
    assert x[0].count_nonzero().item() == 0
    assert torch.allclose(x[1, 0, 0, 0], torch.tensor(128 / 255))
    assert torch.allclose(x[2, 0, 0, :3], torch.tensor([-1., 0., 1.]), atol=9e-6)
    assert x[2, 0, 0, 3].item() == 0


def test_pool_matches_regular_adaptive_mean():
    x = torch.arange(2 * 3 * 16 * 16, dtype=torch.float32).reshape(2, 3, 16, 16)
    assert torch.equal(RegularBinMean()(x), F.adaptive_avg_pool2d(x, 4))


def test_bridge_unscaled_dot_and_exact_codeword():
    b = CodewordBridge()
    with torch.no_grad():
        b.P.fill_(5)
        b.P[0].zero_()
        b.P[1].zero_()
        b.P[1, 0] = 2
    z = torch.zeros((1, 512))
    z[0, :2] = torch.tensor([1.25, .25])
    y, p, rank = b(z)
    assert rank.item() == 1
    assert torch.equal(p[0], b.P[1])
    assert torch.allclose(y, .7 * z + .3 * p)
    assert slot_dot(y, z).item() == pytest.approx(float((y * z).sum().detach()))
    assert slot_dot(y, z).item() != pytest.approx(float(F.cosine_similarity(y, z).detach()))


def test_native_model_keeps_singleton_bn_guard():
    torch.set_num_threads(1)
    m = PalmBridgeE10().train()
    before = m.trunk.embed[-1].num_batches_tracked.clone()
    gray = torch.arange(128 * 128, dtype=torch.int32).remainder(256).to(torch.uint8).reshape(1, 128, 128)
    y = m.encode(gray)
    assert y.shape == (1, 512) and torch.isfinite(y).all()
    assert m.trunk.embed[-1].training and torch.equal(m.trunk.embed[-1].num_batches_tracked, before)
    assert len(m.state_dict()) == 67


def test_cli_trains_and_strict_local_checkpoint_round_trip(tmp_path, capsys):
    dest = tmp_path / "palmbridge.safetensors"
    assert main(["--smoke", "--threads", "1", "--save", str(dest)]) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["updates"] == 2 and receipt["epochs"] == 2
    assert receipt["inference_shape"] == [2, 512]
    assert receipt["mean_loss"] > 0 and receipt["local_checkpoint_saved"]
    assert dest.stat().st_mode & 0o777 == 0o600
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    loaded = load_exact(PalmBridgeE10(), dest, digest)
    with pytest.raises(ValueError, match="digest"):
        load_exact(loaded, dest, "0" * 64)
    with pytest.raises(ValueError):
        save_terminal(loaded, dest)
