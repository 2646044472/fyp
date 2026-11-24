import numpy as np
import pytest

from block_consensus_fastcc import FastCCBlockConsensusAlgorithm, quadrant_consensus_hamming
from palmprint.algorithms.fastcc import FastCCAlgorithm
from palmprint.core.matching import minimum_shifted_hamming


def test_quadrant_scores_match_best_three_reference_and_are_symmetric():
    rng = np.random.default_rng(20261104)
    left = rng.integers(0, 2, size=(32, 32), dtype=np.uint8).astype(bool)
    right = left.copy()
    right[:16, :16] = ~right[:16, :16]
    scores = [minimum_shifted_hamming(left[r:r + 16, c:c + 16],
                                      right[r:r + 16, c:c + 16], shift=1)
              for r in (0, 16) for c in (0, 16)]
    expected = float(np.mean(sorted(scores)[:3]))
    assert quadrant_consensus_hamming(left, right) == expected
    assert quadrant_consensus_hamming(left, right) == quadrant_consensus_hamming(right, left)
    assert quadrant_consensus_hamming(left, right, drop_worst=0) >= expected


@pytest.mark.parametrize("shape", [(32, 31), (16, 16), (32, 32, 2)])
def test_quadrant_metric_rejects_wrong_shape(shape):
    value = np.zeros(shape, dtype=np.bool_)
    with pytest.raises(ValueError):
        quadrant_consensus_hamming(value, value)


def test_block_metric_is_explicit_and_keeps_fastcc_feature_extractor():
    candidate = FastCCBlockConsensusAlgorithm()
    baseline = FastCCAlgorithm()
    left = np.zeros((32, 32), dtype=np.bool_)
    right = np.ones((32, 32), dtype=np.bool_)
    assert candidate.name == "FastCCBlockConsensus"
    assert candidate.match(left, right) == 1.0
    assert candidate.extract(np.zeros((128, 128), np.uint8)).shape == baseline.extract(np.zeros((128, 128), np.uint8)).shape


def test_acceleration_wrapper_preserves_custom_matcher_metric():
    from fastcc_accelerated import AcceleratedFastCC

    rng = np.random.default_rng(512)
    left = rng.integers(0, 2, (32, 32), dtype=np.uint8).astype(bool)
    right = left.copy()
    right[:16, :16] = ~right[:16, :16]
    reference = FastCCBlockConsensusAlgorithm()
    accelerated = AcceleratedFastCC(reference)
    assert accelerated.match(left, right) == reference.match(left, right)
    assert accelerated.match(left, right) != FastCCAlgorithm().match(left, right)
