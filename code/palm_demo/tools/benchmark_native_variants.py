"""Compare exact native neighbours/transforms on synthetic and replay descriptors."""
import argparse
import hashlib
import json
from pathlib import Path
import time

from replay_pi_pipeline import save_json
import cv2
import numpy as np
from biometric import load_algorithm
from native_registration import NativeRegistration
from templates import TemplateStore


def neighbours(native, a, b):
    a, b = np.ascontiguousarray(a), np.ascontiguousarray(b)
    fi, fd = np.empty((len(a), 2), np.int32), np.empty((len(a), 2), np.float32)
    ri, rd = np.empty((len(b), 2), np.int32), np.empty((len(b), 2), np.float32)
    assert native.function(a.ctypes.data, len(a), b.ctypes.data, len(b), native.threads,
                          fi.ctypes.data, fd.ctypes.data, ri.ctypes.data, rd.ctypes.data) == 0
    return fi, fd, ri, rd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('replay', type=Path)
    parser.add_argument('--threads', type=int, choices=(1, 2, 4), default=2)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    cv2.setNumThreads(2)
    kernels = [NativeRegistration(p, args.threads) for p in (args.baseline, args.candidate)]
    rng = np.random.default_rng(20261029)
    synthetic = 0
    for n in (4, 32, 200, 1000):
        for noise in (0., .001, .02, .1):
            a = rng.random((n, 128), dtype=np.float32)
            a = np.sqrt(a / a.sum(axis=1, keepdims=True))
            b = np.maximum(a + rng.normal(0, noise, a.shape).astype(np.float32), 0)
            b /= np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-10)
            b[1] = b[0]
            b[2] = np.nextafter(b[0], np.float32(1))
            values = [neighbours(k, a, b) for k in kernels]
            assert all(np.array_equal(x, y) for x, y in zip(*values))
            assert kernels[0].pairs(a, b) == kernels[1].pairs(a, b)
            synthetic += 1
    summary = json.loads((args.replay / 'summary.json').read_text())
    assert summary['live_camera_tested'] is False
    root = Path(__file__).resolve().parents[1]
    algorithm = load_algorithm(root / 'vendor/palmprint-recognition-python', summary['matcher'])
    store = TemplateStore(args.replay / 'demo_runtime/demo_templates')
    views = []
    for user in store.list_users():
        features, _ = store.load(user)
        for f in features:
            q = algorithm._unpack(f)
            views.extend([(q[1][4], q[1][5]), q[2]])
    trials = []
    for i, a in enumerate(views):
        for offset in (1, 9):
            b = views[(i + offset) % len(views)]
            values = [neighbours(k, a[1], b[1]) for k in kernels]
            exact = all(np.array_equal(x, y) for x, y in zip(*values))
            times = [[], []]
            transforms = [None, None]
            # Alternate execution order to reduce a systematic warm-cache bias.
            for repeat in range(4):
                for index in ((0, 1) if repeat % 2 == 0 else (1, 0)):
                    start = time.perf_counter()
                    transforms[index] = kernels[index](a, b)
                    times[index].append((time.perf_counter() - start) * 1000)
            x, y = transforms
            exact_transform = (x is None and y is None) or (x is not None and y is not None and np.array_equal(x, y))
            trials.append(dict(i=i, offset=offset, exact_neighbours=exact, exact_transform=exact_transform,
                               baseline_ms=float(np.median(times[0])), candidate_ms=float(np.median(times[1]))))
    algorithm.close()
    result = dict(synthetic_cases=synthetic, threads=args.threads, trials=trials,
                  libraries={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.baseline, args.candidate)},
                  median_ms={name: float(np.median([t[name + '_ms'] for t in trials])) for name in ('baseline', 'candidate')})
    save_json(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'trials'}), flush=True)
    assert trials and all(t['exact_neighbours'] and t['exact_transform'] for t in trials)


if __name__ == '__main__':
    main()
