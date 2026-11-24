import cv2
import numpy as np
import pytest

from bounded_exact_index import BoundedExactIndex


def test_sharded_exact_matches_full_brute_force_with_global_indices():
    rng = np.random.default_rng(723)
    a, b = rng.random((33, 128), dtype=np.float32), rng.random((29, 128), dtype=np.float32)
    q = rng.random((9, 128), dtype=np.float32)
    expected = cv2.BFMatcher(cv2.NORM_L2).knnMatch(q, np.concatenate([a, b]), k=16)
    actual = BoundedExactIndex([a, b], shard_rows=7, query_rows=3).knnMatch(q, 16)
    assert [[(m.trainIdx, m.distance) for m in row] for row in actual] == [[(m.trainIdx, m.distance) for m in row] for row in expected]


def test_budget_checkpoint_stops_search():
    def stop(): raise RuntimeError('resource stop')
    index = BoundedExactIndex([np.zeros((20, 128), np.float32)], checkpoint=stop)
    with pytest.raises(RuntimeError, match='resource stop'):
        index.knnMatch(np.zeros((1, 128), np.float32), 16)


def test_duplicate_descriptors_keep_distinct_original_indices():
    data = np.zeros((20, 128), np.float32)
    matches = BoundedExactIndex([data[:10], data[10:]], shard_rows=5).knnMatch(data[:1], 16)[0]
    assert [m.trainIdx for m in matches] == list(range(16))


def test_descriptor_budget_counts_all_arrays_and_accepts_exact_limit():
    a = np.zeros((10, 128), np.float32)
    b = np.zeros((7, 128), np.float32)
    budget = a.nbytes + b.nbytes
    assert BoundedExactIndex([a, b], max_descriptor_bytes=budget).descriptor_bytes == budget
    with pytest.raises(ValueError, match='budget exceeded'):
        BoundedExactIndex([a, b], max_descriptor_bytes=budget-1)


@pytest.mark.parametrize('budget', [-1, 1.5, True])
def test_descriptor_budget_rejects_invalid_values(budget):
    with pytest.raises(ValueError, match='Invalid descriptor byte budget'):
        BoundedExactIndex([], max_descriptor_bytes=budget)


def test_opencv_train_matrix_row_limit_is_checked_before_search():
    with pytest.raises(ValueError, match='OpenCV row limit'):
        BoundedExactIndex([], shard_rows=1 << 18)
    assert BoundedExactIndex([], shard_rows=(1 << 18) - 1).shard_rows == (1 << 18) - 1
