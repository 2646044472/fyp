"""Synthetic result note: a repeated first-five burst should lose pose/texture coverage.

The sequence below has 5 near-identical early frames followed by 5 more varied
frames. The selector is expected to return five distinct IDs and higher mean
pairwise pose/texture distance than the first-five rule. This only verifies the
selection heuristic on constructed inputs; it says nothing about real hands.
Observed on X (2026-11-09): 2 tests passed; selected IDs were [0, 5, 7, 8, 9],
and mean pairwise combined distance changed from 0.4000 (first five) to 0.9402.
"""

import math

import numpy as np
import pytest

from enrollment_photo_selection import EnrollmentPhotoSelector, PhotoCandidate, select_enrollment_photos


def candidate(frame_id, *, center=(320.0, 240.0), angle=0.0, texture_id=0,
              sharpness=8.0, contrast=30.0):
    side = 80.0
    local = np.asarray([[-side, -side], [side, -side], [side, side], [-side, side]])
    rotation = np.asarray([[math.cos(angle), -math.sin(angle)],
                           [math.sin(angle), math.cos(angle)]])
    quad = local @ rotation.T + np.asarray(center)
    texture = np.eye(8, dtype=np.float64)[texture_id]
    return PhotoCandidate(frame_id, sharpness, contrast, quad, texture, (640, 480), frame_id)


def sequence():
    repeated = [candidate(i, center=(320 + i * 0.1, 240), angle=i * 0.001,
                          texture_id=0, sharpness=10 - i * 0.1, contrast=35)
                for i in range(5)]
    varied = [candidate(5 + i,
                        center=(100 + 100 * i, 100 + 30 * (i % 2)),
                        angle=0.12 * i, texture_id=i + 1,
                        sharpness=7.0 + 0.1 * i, contrast=25)
              for i in range(5)]
    return repeated + varied


def coverage(items):
    pose = np.stack([EnrollmentPhotoSelector._pose(x) for x in items])
    texture = np.stack([EnrollmentPhotoSelector._texture(x.texture) for x in items])
    p = EnrollmentPhotoSelector._scale_distances(EnrollmentPhotoSelector._pairwise_euclidean(pose))
    t = EnrollmentPhotoSelector._scale_distances(EnrollmentPhotoSelector._pairwise_cosine(texture))
    return float(((p + t) * 0.5)[np.triu_indices(len(items), 1)].mean())


def test_selection_beats_first_five_synthetic_burst_for_coverage():
    inputs = sequence()
    selected = select_enrollment_photos(inputs, capacity=10, select_count=5)
    baseline = inputs[:5]
    assert len(selected) == 5
    assert len({item.frame_id for item in selected}) == 5
    assert coverage(selected) > coverage(baseline)
    assert any(item.frame_id >= 5 for item in selected)
    assert selected == select_enrollment_photos(inputs, capacity=10, select_count=5)


def test_quality_gate_capacity_and_bad_geometry_are_explicit():
    assert select_enrollment_photos([candidate(0, sharpness=1.9)], capacity=5) == []
    with pytest.raises(ValueError):
        select_enrollment_photos([candidate(0)], capacity=4, select_count=5)
    selector = EnrollmentPhotoSelector(capacity=1, select_count=1)
    assert not selector.add(PhotoCandidate(0, 8, 30, np.zeros((3, 2)), np.ones(8), (640, 480)))
    assert selector.add(candidate(1))
    with pytest.raises(OverflowError):
        selector.add(candidate(2))
