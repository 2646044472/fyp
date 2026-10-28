"""Single-device, full-resolution local-feature alignment development control.

Frozen automatic v5 ROIs, fixed parameters for every palm, no reference points
or labels at feature extraction/matching time. Historical split labels only score.
"""
import argparse
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from pklnet_roi import normalize_roi


def features(row, side=384):
    image = cv2.cvtColor(np.asarray(Image.open(row['original']).convert('RGB')), cv2.COLOR_RGB2GRAY)
    q = np.asarray(row['illumination']['details']['roi_quad_full'], np.float32)
    # Use the runtime's exact winding and corner convention.
    import importlib.util
    from pklnet_roi import PKLNET_ROOT
    spec = importlib.util.spec_from_file_location('local_alignment_geometry', PKLNET_ROOT/'roiExtractor.py')
    geo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geo)
    bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    pixels = normalize_roi(geo.getROIimg(bgr, q, side=side))[0]
    sift = cv2.SIFT_create(nfeatures=1000, contrastThreshold=.02, edgeThreshold=10)
    kp, desc = sift.detectAndCompute(pixels, None)
    points = np.array([p.pt for p in kp], np.float32).reshape(-1, 2)
    if desc is None:
        return pixels, points, np.empty((0, 128), np.float32)
    desc = np.sqrt(desc / np.maximum(desc.sum(axis=1, keepdims=True), 1e-12))
    return pixels, points, desc


def compare(left, right, ratio=.75):
    pa, da = left
    pb, db = right
    empty = dict(inliers=0, matches=0, coverage=0., valid=False)
    if len(da) < 4 or len(db) < 4:
        return empty
    forward = cv2.BFMatcher().knnMatch(da, db, k=2)
    backward = cv2.BFMatcher().knnMatch(db, da, k=1)
    good = [a for a, b in forward if a.distance < ratio*b.distance
            and backward[a.trainIdx][0].trainIdx == a.queryIdx]
    if len(good) < 4:
        return {**empty, 'matches': len(good)}
    p = np.array([pa[m.queryIdx] for m in good], np.float32)
    q = np.array([pb[m.trainIdx] for m in good], np.float32)
    cv2.setRNGSeed(20261028)
    transform, mask = cv2.estimateAffinePartial2D(p, q, method=cv2.RANSAC,
                                               ransacReprojThreshold=3., maxIters=2000,
                                               confidence=.99, refineIters=10)
    if transform is None:
        return {**empty, 'matches': len(good)}
    keep = mask.ravel().astype(bool)
    inliers = int(keep.sum())
    coverage = min(cv2.contourArea(cv2.convexHull(v[keep])) for v in [p, q]) / (384*384)
    scale = float(np.hypot(transform[0, 0], transform[1, 0]))
    angle = float(np.rad2deg(np.arctan2(transform[1, 0], transform[0, 0])))
    valid = inliers >= 4 and coverage >= .02 and .5 <= scale <= 2 and abs(angle) <= 40
    return dict(inliers=inliers, matches=len(good), coverage=coverage, valid=valid,
                scale=scale, angle=angle, transform=transform.tolist())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stability', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    def save(name, value):
        (args.output/name).write_text(json.dumps(value, indent=2), encoding='utf-8')
    save('plan.json', dict(crop='automatic v5 quad, original image, 384 pixels, fixed 1/99 normalization',
                          features='RootSIFT, 1000 features, contrast .02',
                          ratios=[.75, .85], alignment='mutual NN, partial affine RANSAC 3px, minimum4 inliers, hull area .02, scale .5-2, angle±40',
                          score='negative valid inlier count; nearest enrollment; exact ties incorrect',
                          limitation='Exploratory control on previously inspected single-device data; no reference ROI used'))
    records = json.loads((args.stability/'records.json').read_text())
    cases = [r for r in json.loads((args.stability/'results.json').read_text())
             if r['algorithm']=='FastCCPoseNearest-v1' and '_to_' not in r['case']]
    lookup = {r['sample']: i for i, r in enumerate(records)}
    fs = []
    for i, row in enumerate(records):
        pixels, points, desc = features(row)
        fs.append((points, desc))
        cv2.imwrite(str(args.output/(row['sample']+'.png')), pixels)
    np.savez_compressed(args.output/'features.npz', **{f'{i}_{k}': v for i, pair in enumerate(fs) for k, v in zip(['points', 'desc'], pair)})
    save('feature-counts.json', [dict(sample=r['sample'], count=len(f[0])) for r, f in zip(records, fs)])
    started = time.perf_counter()
    results = []
    for ratio in [.75, .85]:
        matrix = np.full((len(records), len(records)), np.nan)
        pairs = []
        for i, left in enumerate(fs):
            for j, right in enumerate(fs):
                if records[i]['cohort'] != records[j]['cohort']:
                    continue
                if i == j:
                    matrix[i, j] = 0
                    continue
                result = compare(left, right, ratio)
                matrix[i, j] = -result['inliers'] if result['valid'] else 0.
                pairs.append(dict(query=i, gallery=j, **result))
            if (i+1) % 10 == 0:
                print(f'ratio={ratio} {i+1}/80 {time.perf_counter()-started:.1f}s', flush=True)
        np.save(args.output/f'distances-{ratio}.npy', matrix)
        save(f'pairs-{ratio}.json', pairs)
        for case in cases:
            gallery = {k: [lookup[s] for s in ids] for k, ids in case['gallery'].items()}
            trials = []
            for trial in case['trials']:
                i = lookup[trial['sample']]
                scores = {k: float(matrix[i, ids].min()) for k, ids in gallery.items()}
                true = trial['identity']
                trials.append(dict(sample=trial['sample'], identity=true, scores=scores,
                                   correct=scores[true] < min(v for k, v in scores.items() if k != true)))
            results.append(dict(case=case['case'], ratio=ratio, correct=sum(t['correct'] for t in trials), total=len(trials), trials=trials))
        save('results.json', results)
        print([(r['case'], r['correct']) for r in results if r['ratio']==ratio], flush=True)


if __name__ == '__main__':
    main()
