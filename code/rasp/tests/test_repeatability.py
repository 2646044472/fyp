import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import analyze_repeatability as repeat


def test_fixed_reference_excludes_self_and_reports_threshold():
    class Matcher:
        def extract(self, image):
            return image

        def match(self, a, b):
            return float(abs(a.mean() - b.mean()) / 255)

    images = [np.full((128, 128), x, dtype=np.uint8) for x in (0, 51, 255)]
    rows, summary = repeat.score_samples(images, Matcher(), 0.2)
    assert [r['sample'] for r in rows] == [2, 3]
    assert [r['decision'] for r in rows] == ['ACCEPT', 'REJECT']
    assert summary['probe_count'] == 2
    assert summary['rejected'] == 1
    assert summary['mean'] == pytest.approx(0.6)


def test_rejects_multiple_frames_per_placement(tmp_path):
    for i in (1, 2):
        path = tmp_path / 'placement_001' / f'sample_{i:03d}'
        path.mkdir(parents=True)
        Image.new('L', (128, 128)).save(path / 'roi_128.png')
    with pytest.raises(ValueError, match='one ROI'):
        repeat.load_samples(tmp_path, expected=30)


def test_loads_legacy_debug_capture_samples_without_rearranging_them(tmp_path):
    for i, value in ((1, 30), (2, 60)):
        path = tmp_path / f'sample_{i:03d}'
        path.mkdir()
        Image.new('L', (128, 128), value).save(path / 'roi_128.png')
        Image.new('RGB', (16, 16), value).save(path / 'raw.png')
        (path / 'metadata.json').write_text('{}', encoding='utf-8')

    records = repeat.load_samples(tmp_path, expected=2)

    assert [path.parent.name for path, _ in records] == ['sample_001', 'sample_002']
    assert [int(image[0, 0]) for _, image in records] == [30, 60]
