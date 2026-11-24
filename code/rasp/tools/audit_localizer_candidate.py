"""All-development-image ROI and fixed pose-stage audit for an isolated localizer.

This is a screening test, not an end-to-end or independent validation result.
Failures stay in the denominator. Images are never selected by quality/identity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from biometric import load_algorithm
from pklnet_roi import PKLNetROI, normalize_roi
from pose_matcher import FastCCPoseMatcher
from fastcc_accelerated import AcceleratedFastCC


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', type=Path)
    parser.add_argument('model_root', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--landmark-ensemble', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    records = json.loads(args.records.read_text())
    assert len(records) == 80 and {r['cohort'] for r in records} == {'new', 'old'}
    if args.landmark_ensemble:
        from fast_landmark_roi import IlluminatedLandmarkROI
        engine = IlluminatedLandmarkROI(args.model_root)
    else:
        engine = PKLNetROI(root=args.model_root, weights=args.model_root/'net_params_500.pth', threads=4)
        engine._ensure_loaded()
    cv2.setNumThreads(4)
    base = AcceleratedFastCC(load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python', 'FastCC'))
    pose = FastCCPoseMatcher(base)
    results, banks, panels = [], {}, []
    for row in records:
        assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest() == row['sha256']
        image = Image.open(row['original']).convert('RGB')
        entry = {k: row[k] for k in ('sample', 'identity', 'cohort', 'index')}
        started = time.perf_counter()
        panel = image.copy()
        try:
            raw, quad, details = engine.extract(image)
            entry.update(localizer_ms=(time.perf_counter()-started)*1000,
                         valid=bool(details['roi_geometry_valid']), quad=np.asarray(quad).tolist(), details=details,
                         status='ok' if details['roi_geometry_valid'] else 'invalid_geometry')
            baseline = np.asarray(row['illumination']['details']['roi_quad_full'], np.float32)
            intersection = max(0., cv2.intersectConvexConvex(np.asarray(quad, np.float32), baseline)[0])
            entry['baseline_quad_iou'] = intersection / max(1e-8, cv2.contourArea(quad)+cv2.contourArea(baseline)-intersection)
            draw = ImageDraw.Draw(panel)
            for q, color in ((baseline, 'orange'), (quad, 'lime')):
                points = [tuple(p) for p in q]
                draw.line(points + points[:1], fill=color, width=8)
            if entry['valid']:
                roi = normalize_roi(raw)[0]
                banks[row['sample']] = pose.extract_with_context(image, quad, roi)
                np.savez_compressed(args.output/(row['sample']+'.npz'), bank=banks[row['sample']], quad=quad, raw=raw)
        except Exception as error:
            entry.update(valid=False, status='error', error_type=type(error).__name__,
                         error=f'{type(error).__name__}: {error}', localizer_ms=(time.perf_counter()-started)*1000)
        results.append(entry)
        panel.thumbnail((480, 300))
        canvas = Image.new('RGB', (480, 330), 'white')
        canvas.paste(panel, (0, 25))
        ImageDraw.Draw(canvas).text((5, 5), row['sample'] + ' ' + str(entry['valid']), fill='black')
        panels.append(canvas)
        (args.output/'records.json').write_text(json.dumps(results, indent=2))
        print(row['cohort'], row['sample'], entry['valid'], entry.get('baseline_quad_iou'), flush=True)
    for first in range(0, len(panels), 10):
        sheet = Image.new('RGB', (960, 1650), 'white')
        for i, panel in enumerate(panels[first:first+10]):
            sheet.paste(panel, ((i % 2)*480, (i // 2)*330))
        sheet.save(args.output/f'geometry-{first}.jpg', quality=90)
    trials = []
    for cohort in ('new', 'old'):
        for reverse in (False, True):
            subset = [r for r in records if r['cohort'] == cohort]
            gallery = [r for r in subset if (r['index'] <= 5) != reverse]
            queries = [r for r in subset if r not in gallery]
            for query in queries:
                scores = {}
                if query['sample'] in banks:
                    for identity in sorted({r['identity'] for r in gallery}):
                        samples = [r for r in gallery if r['identity'] == identity]
                        if not all(s['sample'] in banks for s in samples):
                            break  # A failed enrollment invalidates the whole gallery.
                        distances = [pose.match(banks[query['sample']], banks[s['sample']]) for s in samples]
                        scores[identity] = float(np.mean(sorted(distances)[:2]))
                complete = len(scores) == len({r['identity'] for r in gallery})
                rank = sorted(scores, key=scores.get)
                correct = complete and scores[query['identity']] < min(v for k, v in scores.items() if k != query['identity'])
                confident = complete and scores[rank[0]] <= .32 and scores[rank[1]]-scores[rank[0]] >= .08
                trials.append(dict(cohort=cohort, reverse=reverse, sample=query['sample'], correct=bool(correct),
                                   ranked=complete, confident=bool(confident), confident_wrong=bool(confident and not correct), scores=scores))
    summary = dict(development_only=True, live_camera_tested=False, end_to_end_tested=False,
                   n=len(results), valid=sum(r['valid'] for r in results), trials=trials,
                   extraction_errors=sum(r['status']=='error' for r in results),
                   warning='Error-call timings are not successful localization latency; missing enrollment invalidates a gallery.',
                   cohorts={c: dict(n=sum(r['cohort']==c for r in results),
                        valid=sum(r['cohort']==c and r['valid'] for r in results),
                        localizer_median_ms=float(np.median([r['localizer_ms'] for r in results if r['cohort']==c])),
                        pose_rank_correct=sum(t['cohort']==c and t['correct'] for t in trials),
                        pose_confident=sum(t['cohort']==c and t['confident'] for t in trials),
                        pose_confident_wrong=sum(t['cohort']==c and t['confident_wrong'] for t in trials)) for c in ('new','old')})
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != 'trials'}), flush=True)
    if hasattr(engine, 'close'):
        engine.close()


if __name__ == '__main__':
    main()
