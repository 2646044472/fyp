"""Fixed default-ORB pilot on all frozen development ROIs and enrollment splits.

Only local features and their distance metric change. All views, geometry gates,
original pixels, FastCC scoring and best-two aggregation are retained. This is
an offline regression screen, not a latency or independent-accuracy claim.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from biometric import load_algorithm
from demo_matcher import FastCCDemoMatcher
from fastcc_accelerated import AcceleratedFastCC
from pklnet_roi import normalize_roi_pixels
from registered_matcher import MAX_POINTS, DUAL_SIZE
from registration_accelerated import estimate_pairs
from union_matcher import HEADER


def binary_features(pixels, detector='orb'):
    engine = cv2.ORB_create(nfeatures=MAX_POINTS) if detector == 'orb' else cv2.AKAZE_create()
    points, descriptors = engine.detectAndCompute(pixels, None)
    if descriptors is None:
        return np.empty((0, 2), np.float32), np.empty((0, engine.descriptorSize()), np.uint8)
    if detector == 'akaze' and len(points) > MAX_POINTS:
        indices = sorted(range(len(points)), key=lambda i: -points[i].response)[:MAX_POINTS]
        points, descriptors = [points[i] for i in indices], descriptors[indices]
    return np.asarray([p.pt for p in points[:MAX_POINTS]], np.float32), descriptors[:MAX_POINTS]


def binary_registration(left, right):
    pa, a = left
    pb, b = right
    if min(len(a), len(b)) < 4:
        return None
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    forward, reverse = matcher.knnMatch(a, b, k=2), matcher.knnMatch(b, a, k=1)
    pairs = [(m.queryIdx, m.trainIdx) for m, n in forward
             if m.distance < .85*n.distance and reverse[m.trainIdx][0].trainIdx == m.queryIdx]
    return estimate_pairs(pa, pb, pairs)


def convert_query(reference, feature, detector='orb'):
    return extract_binary_geometry(**query_geometry(reference, feature), detector=detector)


def query_geometry(reference, feature):
    _, primary, _, native, _, old_queries = reference._unpack(feature)
    bank, context, source, size, _, _ = primary
    # Retain the exact field bounds stored by the original extractor.
    encoded, nq, ng = map(int, feature[:HEADER].view('<i4')[2:5])
    pos = HEADER + DUAL_SIZE + encoded
    bounds = []
    for index in range(ng+nq):
        _, n, lower, upper = map(int, feature[pos:pos+16].view('<i4'))
        pos += 88+n*520
        if index >= ng:
            bounds.append((lower, upper))
    return dict(bank=bank, context=context, source=source, size=np.asarray(size), native=native,
                sigmas=np.asarray([q[0] for q in old_queries]),
                matrices=np.asarray([q[1] for q in old_queries]), bounds=np.asarray(bounds))


def extract_binary_geometry(bank, context, source, size, native, sigmas, matrices, bounds, detector='orb'):
    """Recompute descriptors from pixels; cached geometry is explicitly excluded."""
    pixels = normalize_roi_pixels(cv2.warpPerspective(native, source, (384, 384)))
    p, d = binary_features(pixels, detector)
    second_pixels = normalize_roi_pixels(context[192:576, 192:576])
    secondary = binary_features(cv2.GaussianBlur(second_pixels, (0, 0), 2.), detector)
    primary = (bank, context, source, size, p, d)
    gallery = [(sigma, np.eye(3), *binary_features(cv2.GaussianBlur(second_pixels, (0, 0), sigma), detector))
               for sigma in (4, 8)]
    queries = []
    for sigma, matrix, (lower, upper) in zip(sigmas, matrices, bounds):
        sigma = int(sigma)
        side = int(upper-lower)
        shift = np.asarray([[1., 0., -lower], [0., 1., -lower], [0., 0., 1.]])
        pixels = normalize_roi_pixels(cv2.warpPerspective(native, shift@matrix, (side, side)))
        p, d = binary_features(cv2.GaussianBlur(pixels, (0, 0), sigma) if sigma else pixels, detector)
        queries.append((sigma, matrix, p+lower, d))
    assert len(queries) == len(sigmas)
    return None, primary, secondary, native, gallery, queries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--detector', choices=['orb', 'akaze'], default='orb')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cv2.setNumThreads(4)
    rows = json.loads((args.source/'stability/records.json').read_text())
    cases = json.loads((args.source/'single-device/runtime-v5/results.json').read_text())
    assert len(rows) == 80 and len(cases) == 224
    plan = dict(detector=args.detector, settings='OpenCV defaults; cap at 1000 points, AKAZE by response',
                descriptor_metric='Hamming, same 0.85 ratio and mutual-nearest test',
                spatial_candidates='Every saved v5 candidate/view; no removal',
                geometry='unchanged RANSAC and spatial-overlap gates',
                recognition='unchanged FastCC pixel scoring and best-two aggregation',
                development_only=True, independent_validation=False, opencv_version=cv2.__version__)
    (args.output/'protocol.json').write_text(json.dumps(plan, indent=2))
    base = load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python', 'FastCC')
    algorithm = FastCCDemoMatcher(AcceleratedFastCC(base))
    algorithm.registration = algorithm.legacy.registration = binary_registration
    queries = []
    for row in rows:
        assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest() == row['sha256']
        with np.load(args.source/'single-device/runtime-v5'/(row['sample']+'.npz'), allow_pickle=False) as saved:
            feature = saved['feature']
        # v5/v6 have identical layout; only the numeric envelope tag differs.
        feature[:4] = np.asarray([algorithm.magic], '<i4').view(np.uint8)
        queries.append(convert_query(algorithm, feature, args.detector))
        print('features', len(queries), flush=True)
    matrix = np.full((len(rows), len(rows)), np.nan)
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as executor:
        for i, row in enumerate(rows):
            indices = [j for j, target in enumerate(rows) if target['cohort'] == row['cohort'] and j != i]
            values = list(executor.map(lambda j: algorithm._match_unpacked(queries[i], queries[j]), indices))
            matrix[i, indices] = values
            matrix[i, i] = 0.
            np.save(args.output/'distances.npy', matrix)
            print('pairs', i+1, round(time.perf_counter()-start, 1), flush=True)
    algorithm.close()
    lookup = {r['sample']: i for i, r in enumerate(rows)}
    results = []
    for case in cases:
        gallery = {user: [lookup[s] for s in samples] for user, samples in case['gallery'].items()}
        trials = []
        for trial in case['trials']:
            i = lookup[trial['sample']]
            assert all(i not in indices for indices in gallery.values())
            scores = {user: float(np.mean(np.sort(matrix[i, indices])[:2])) for user, indices in gallery.items()}
            correct = scores[trial['identity']] < min(v for k, v in scores.items() if k != trial['identity'])
            rank = sorted(scores.values())
            confident = rank[0] <= .32 and rank[1]-rank[0] >= .08
            trials.append(dict(sample=trial['sample'], identity=trial['identity'], scores=scores,
                               correct=bool(correct), confident_wrong=bool(confident and not correct)))
        results.append(dict(case=case['case'], correct=sum(t['correct'] for t in trials), total=len(trials), trials=trials))
    (args.output/'results.json').write_text(json.dumps(results, indent=2))
    summary = {c: dict(cases=len(values), minimum=min(values), maximum=max(values), mean=float(np.mean(values)))
               for c in ('new', 'old') if (values := [r['correct'] for r in results if r['case'].startswith(c+'_')])}
    summary['confident_wrong'] = sum(t['confident_wrong'] for r in results for t in r['trials'])
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
