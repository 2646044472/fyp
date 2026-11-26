import hashlib
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import stat
from tempfile import TemporaryDirectory
import unittest

import numpy as np
import torch

from fpn_train import (
    chart_target, forward_training, geometry_loss, main, make_localizer,
    pack_native, synthetic_rows,
)
from checkpoints import save_terminal
from frozen_fpn_c_e10 import load_fpn


class FpnTrainingTest(unittest.TestCase):
    def test_support_includes_every_corner_and_center(self):
        rgb = np.zeros((320, 256, 3), dtype=np.uint8)
        corners = np.float32(((25, 30), (125, 30), (125, 130), (25, 130)))
        _, chart, support = pack_native(rgb, corners)
        support = support.copy()
        target = chart_target(chart, support)
        np.testing.assert_allclose(target[3:5], (1., 0.))
        self.assertEqual(target[5], 1.)
        x, y = np.rint(chart.mean(axis=0)).astype(int)
        support[y, x] = 0
        self.assertEqual(chart_target(chart, support)[5], 0.)
        self.assertEqual(chart_target(chart - (1000, 1000), support)[5], 0.)
        with self.assertRaises(ValueError):
            chart_target(chart[::-1], support)

    def test_invalid_rows_have_confidence_only_loss(self):
        q = torch.tensor([.4], requires_grad=True)
        c = torch.ones(1, 2, requires_grad=True)
        loss = geometry_loss((c, torch.ones(1), torch.zeros(1, 2), q,
                              torch.zeros(1, 1), torch.zeros(1, 2)), torch.zeros(1, 6))
        loss.backward()
        self.assertIsNone(c.grad)
        self.assertGreater(q.grad.item(), 0.)

    def test_training_taps_match_same_station_forward(self):
        torch.set_num_threads(1)
        model = make_localizer().eval()
        with torch.no_grad():
            d, (quad, score) = forward_training(model, torch.zeros(1, 3, 320, 256))
            ctr, scale, axis, qlogit, logits, cells = d
            perp = torch.stack((-axis[:, 1], axis[:, 0]), dim=1)
            basis = torch.stack((axis, perp), dim=1)
            square = torch.tensor(((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)))
            derived = ctr[:, None] + scale[:, None, None] * (square @ basis)
        torch.testing.assert_close(derived, quad, rtol=0, atol=0)
        torch.testing.assert_close(qlogit.sigmoid(), score, rtol=0, atol=0)
        self.assertEqual(logits.shape, (1, 5120))
        self.assertEqual(cells.shape, (5120, 2))
        self.assertEqual(len(model.heat._forward_hooks) + len(model.reg._forward_hooks), 0)

    def test_synthetic_entry_performs_real_optimizer_update(self):
        save = io.StringIO()
        with redirect_stdout(save):
            main(["--smoke"])
        result = json.loads(save.getvalue())
        self.assertEqual(result["planned"], 2)
        self.assertEqual(result["supported_after_augmentation"], 1)
        self.assertEqual(result["optimizer_steps"], 1)
        self.assertTrue(result["synthetic"])


    def test_saved_synthetic_state_matches_station_loader_and_warm_start(self):
        torch.set_num_threads(1)
        with TemporaryDirectory() as directory:
            local = Path(directory)
            data, checkpoint = local / "artificial.npz", local / "artificial.safetensors"
            rgb, corners, masks = synthetic_rows()
            np.savez(data, canvas_rgb=rgb, canvas_corners=corners, support_mask=masks)
            args = ["--npz", str(data), "--epochs", "1", "--batch-size", "2", "--no-augment"]
            with redirect_stdout(io.StringIO()):
                main([*args, "--save", str(checkpoint)])
            self.assertEqual(stat.S_IMODE(checkpoint.stat().st_mode), 0o600)
            with checkpoint.open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
            station = load_fpn(checkpoint, digest)
            self.assertFalse(station.training)
            warm = make_localizer(digest=digest, start_encoder=checkpoint)
            self.assertTrue(next(warm.parameters()).requires_grad)
            warm.eval()
            self.assertEqual(set(station.state_dict()), set(warm.state_dict()))
            self.assertTrue(all(torch.equal(value, warm.state_dict()[key])
                                for key, value in station.state_dict().items()))
            x = torch.zeros(1, 3, 320, 256)
            with torch.no_grad():
                for st, fit in zip(station(x), warm(x)):
                    torch.testing.assert_close(st, fit, atol=0, rtol=0)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                make_localizer(digest="0" * 64, start_encoder=checkpoint)
            with self.assertRaisesRegex(ValueError, "outside"):
                save_terminal(warm, checkpoint)  # atomic publisher refuses overwrite
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main([*args, "--save", str(checkpoint)])
            del station, warm
            with redirect_stdout(io.StringIO()):
                main([*args, "--start-encoder", str(checkpoint), "--init-sha256", digest])
            with checkpoint.open("rb") as handle:
                self.assertEqual(hashlib.file_digest(handle, "sha256").hexdigest(), digest)
            self.assertEqual(sorted(x.name for x in local.iterdir()), [data.name, checkpoint.name])

if __name__ == "__main__":
    unittest.main()
