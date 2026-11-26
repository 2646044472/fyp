import hashlib
import tempfile
import unittest
from pathlib import Path
import numpy as np
import torch
from torch import nn

from checkpoints import load_exact, save_terminal
from convnext_e10 import build, inference_module, parts, run
from objectives import pair_arc_loss, warm_cosine
from paired_data import PairedData, load_paired, synthetic_paired


def fixture():
    data = synthetic_paired()
    return dict(gray=data.gray, source=np.zeros(4, dtype=int),
                person=np.array([0, 0, 1, 1]), palm=np.array([0, 0, 1, 1]), capture=np.arange(4),
                batches=data.batches, pair_count=data.pair_count, epoch_start=data.epoch_start)


class DataContractTests(unittest.TestCase):
    def test_valid_local_npz_and_padded_denominator(self):
        v = fixture()
        v.update(batches=np.array([[[0, 2, -1], [1, -1, -1]], [[1, 3, -1], [0, 2, -1]]]))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "synthetic.npz"
            np.savez(p, **v)
            data = load_paired(p)
        self.assertEqual(data.class_counts, (2,))
        self.assertEqual(data.step(0).valid.shape, (2, 2))
        np.testing.assert_array_equal(data.step(0).rows, [0, 2, 1])
        np.testing.assert_array_equal(data.step(0).labels, [[0, 1], [0, -1]])

    def test_reject_duplicate_and_cross_palm(self):
        for fields in ({"capture": [1, 1, 2, 3]},
                       {"batches": [[[0, 2], [3, 1]], [[1, 3], [0, 2]]]},
                       {"holdout_person": [1]},
                       {"holdout_capture": [0]}):
            with self.subTest(fields=list(fields)):
                data = fixture()
                data.update(fields)
                with self.assertRaises(ValueError):
                    PairedData(**data)

    def test_reject_pickle_payload(self):
        v = fixture()
        v["person"] = np.array([0, 0, 1, 1], dtype=object)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "synthetic.npz"
            np.savez(p, **v)
            with self.assertRaises(ValueError):
                load_paired(p)


class TrainingTests(unittest.TestCase):
    def test_masked_losses_are_finite_with_gradient(self):
        emb = torch.tensor([[[1., 0.], [0., 1.]], [[.9, .1], [0., 0.]]], requires_grad=True)
        proxies = torch.eye(2, requires_grad=True)
        valid = torch.tensor([[True, True], [True, False]])
        labels = torch.tensor([[0, 1], [0, -1]])
        total, pair, arc = pair_arc_loss(emb, proxies, valid, labels)
        self.assertTrue(torch.isfinite(total))
        self.assertAlmostEqual(float(total.detach()), float((.6*pair + .4*arc).detach()), 7)
        total.backward()
        self.assertTrue(torch.isfinite(emb.grad).all() and torch.isfinite(proxies.grad).all())
        self.assertTrue(torch.equal(emb.grad[1, 1], torch.zeros(2)))
        self.assertEqual(warm_cosine(50, 200), .5)
        self.assertAlmostEqual(warm_cosine(200, 200), .1)

    def test_actual_native_cpu_updates_and_thaw(self):
        torch.set_num_threads(1)
        torch.manual_seed(7)
        core = inference_module()
        model = build(core)
        self.assertEqual(len(model.state_dict()), 201)
        data = synthetic_paired()
        groups = parts(model)
        early, local = groups["early"][0], groups["local"][0]
        start = early.detach().clone(), local.detach().clone()
        flags = []
        def signal(epoch):
            flags.append((epoch["early_trainable"], torch.equal(early, start[0]), torch.equal(local, start[1])))
        result = run(data, model, core, "cpu", signal)
        self.assertEqual(flags, [(False, True, False), (True, False, False)])
        self.assertEqual([d["updates"] for d in result], [1,1])
        e = core.encode_c(model, data.gray, "cpu")
        self.assertEqual(e.shape, (4, 512))
        np.testing.assert_allclose(np.linalg.norm(e.reshape(4,2,256), axis=2), 2**-.5, atol=1e-6)

    def test_checkpoint_atomic_roundtrip(self):
        weights = nn.Linear(2,3)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "model.safetensors"
            save_terminal(weights,p)
            self.assertEqual(p.stat().st_mode & 0o777,0o600)
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            other = load_exact(nn.Linear(2,3),p,digest)
            self.assertTrue(all(torch.equal(a,b) for a,b in zip(weights.parameters(),other.parameters())))
            with self.assertRaises(ValueError):
                save_terminal(weights,p)
            with self.assertRaises(ValueError):
                load_exact(nn.Linear(2,3),p,"0"*64)


if __name__ == "__main__":
    unittest.main()
