#!/usr/bin/env python3
"""Compare independent placements to the first saved ROI using unchanged Fast-CC."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))
from palm_app.biometric import load_fastcc


def load_samples(root, expected=30):
    records = []
    placements = sorted(root.glob('placement_*'))
    if placements:
        candidates = []
        for placement in placements:
            paths = sorted(placement.glob('sample_*/roi_128.png'))
            if len(paths) != 1:
                raise ValueError(f'{placement}: expected one ROI per independent placement')
            candidates.append(paths[0])
    else:
        candidates = sorted(root.glob('sample_*/roi_128.png'))
    for path in candidates:
        for name in ('raw.png', 'metadata.json'):
            if not (path.parent / name).is_file():
                raise ValueError(f'{path.parent}: missing {name}')
        with Image.open(path) as image:
            if image.size != (128, 128) or image.mode != 'L':
                raise ValueError(f'{path}: expected saved 128x128 grayscale ROI')
            records.append((path, np.asarray(image).copy()))
    if len(records) != expected or expected < 2:
        raise ValueError(f'Expected {expected} placements, found {len(records)}; need at least 2')
    return records


def score_samples(images, algorithm, threshold=None):
    if len(images) < 2:
        raise ValueError('At least two samples required')
    features = [algorithm.extract(image) for image in images]
    rows = []
    for index, feature in enumerate(features[1:], 2):
        distance = float(algorithm.match(feature, features[0]))
        if not math.isfinite(distance):
            raise ValueError('Non-finite Fast-CC distance')
        rows.append(dict(sample=index, reference=1, distance=distance,
                         decision='UNASSESSED' if threshold is None else
                         ('ACCEPT' if distance <= threshold else 'REJECT')))
    values = np.array([row['distance'] for row in rows])
    summary = dict(probe_count=len(rows), mean=float(values.mean()),
                   std=float(values.std()), min=float(values.min()),
                   max=float(values.max()), threshold=threshold,
                   rejected=None if threshold is None else sum(r['decision'] == 'REJECT' for r in rows))
    return rows, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session', type=Path)
    parser.add_argument('--expected', type=int, default=30)
    parser.add_argument('--threshold', type=float, help='Preselected distance threshold; no threshold is fitted here')
    parser.add_argument('--baseline-path', type=Path, default=APP_DIR / 'vendor/palmprint-recognition-python')
    args = parser.parse_args()
    if args.threshold is not None and (not math.isfinite(args.threshold) or not 0 <= args.threshold <= 1):
        parser.error('threshold must be finite and between 0 and 1')
    records = load_samples(args.session, args.expected)
    rows, summary = score_samples([image for _, image in records], load_fastcc(args.baseline_path), args.threshold)
    for row, (path, _) in zip(rows, records[1:]):
        row['roi_path'] = str(path.relative_to(args.session))
    output = args.session / 'repeatability_report'
    output.mkdir(exist_ok=False)
    with (output / 'scores.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary.update(algorithm='FastCC', reference=str(records[0][0].relative_to(args.session)),
                   baseline_path=str(args.baseline_path.resolve()),
                   interpretation='Lower distance is more similar. One palm cannot estimate false accepts or calibrate a threshold.')
    (output / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    # Paginate to keep both original frames and exact saved ROIs readable.
    for start in range(0, len(records), 10):
        page = records[start:start + 10]
        sheet = Image.new('RGB', (800, 180 * math.ceil(len(page) / 2)), 'white')
        draw = ImageDraw.Draw(sheet)
        for offset, (path, roi) in enumerate(page):
            index = start + offset
            x, y = (offset % 2) * 400, (offset // 2) * 180
            with Image.open(path.parent / 'raw.png') as raw:
                thumb = raw.convert('RGB')
                thumb.thumbnail((240, 140))
                sheet.paste(thumb, (x, y + 28))
            sheet.paste(Image.fromarray(roi).convert('RGB'), (x + 250, y + 28))
            label = 'REFERENCE' if index == 0 else f"d={rows[index-1]['distance']:.4f} {rows[index-1]['decision']}"
            draw.text((x + 4, y + 6), f'{index + 1:02d} {label}', fill='black')
        sheet.save(output / f'comparison_{start // 10 + 1:02d}.png')
    print(json.dumps(summary, indent=2))
    print(f'Report: {output.resolve()}')


if __name__ == '__main__':
    main()
