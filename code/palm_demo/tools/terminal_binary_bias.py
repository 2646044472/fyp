"""Fixed RF binary-marginal ablation; no labels, ROI or identity routing.

A is RF Hamming, B only removes the signed-code mean product, and C (the
sole candidate) also normalizes variance. All use the same 81 overlaps and
28x28 fully supported filter grid. Constant C comparisons have distance one.
"""
import numpy as np
from fastcc_valid_support import ReceptiveFieldFastCC

POLICY = 'terminal-rf-binary-marginal-correlation-v1'
ARMS = ('A', 'B', 'C')


class BinaryMarginalRF(ReceptiveFieldFastCC):
    def counts(self, left, right):
        left, right = np.asarray(left), np.asarray(right)
        if left.shape != (32, 32) or right.shape != (32, 32):
            raise ValueError('Expected two 32x32 codes')
        left = left.astype(bool).astype(np.float32) * self.mask
        right = right.astype(bool).astype(np.float32) * self.mask
        a = self._correlate(left, self.mask)
        b = self._correlate(self.mask, right)
        c = self._correlate(left, right)
        result = np.stack((self.denominator, a, b, c), axis=-1).reshape(81, 4)
        if not np.array_equal(result, np.rint(result)):
            raise ValueError('Nonintegral binary counts')
        return result.astype(np.uint16)


def distances(counts):
    counts = np.asarray(counts)
    if counts.ndim != 2 or counts.shape[1] != 4:
        raise ValueError('Expected rows of n,a,b,c')
    if not np.isfinite(counts).all() or not np.array_equal(counts, np.rint(counts)):
        raise ValueError('Counts must be finite integers')
    n, a, b, c = counts.astype(np.float64).T
    if (np.any(n <= 0) or np.any(a < 0) or np.any(b < 0) or
        np.any(a > n) or np.any(b > n) or np.any(c < np.maximum(0, a+b-n)) or
        np.any(c > np.minimum(a, b))):
        raise ValueError('Invalid binary contingency table')
    raw = (a+b-2*c)/n
    mean_product = (2*a/n-1)*(2*b/n-1)
    centered = raw + .5*mean_product
    denominator = np.sqrt(a*(n-a)*b*(n-b))
    constant = denominator == 0
    rho = np.zeros_like(denominator)
    np.divide(n*c-a*b, denominator, out=rho, where=~constant)
    if np.any(np.abs(rho) > 1+1e-12):
        raise ArithmeticError('Binary correlation outside numerical bounds')
    normalized = np.where(constant, 1., .5*(1-np.clip(rho, -1, 1)))
    return dict(A=raw, B=centered, C=normalized,
                signed_mean_product=mean_product, constant=constant)


def paired_scores(counts):
    result = distances(counts)
    return {arm: float(result[arm].min()) for arm in ARMS}


def aggregate_frames(values):
    if len(values) != 5:
        raise ValueError('Exactly five original enrollment frames required')
    return float(np.mean(sorted(values)[:2]))


def classify(scores, truth, order):
    """Frozen ranking-only Gallery decision plus separate strict tie accounting.

    Truth is used only by this evaluation function, after all scores exist.
    Stable order matches Gallery; ties never count as a correct identification.
    """
    if set(scores) != set(order) or len(order) != len(set(order)):
        raise ValueError('Incomplete full-gallery ranking')
    if any(not np.isfinite(v) for v in scores.values()):
        return dict(status='RETRY', user_id=None, score=None, second_score=None,
                    outcome='processing_failure', tied=None)
    ranked = sorted(((scores[u], u) for u in order), key=lambda v: v[0])
    best, user = ranked[0]; second = ranked[1][0]
    tied = best == second
    status = 'UNKNOWN' if best > 1 else 'MATCH'
    outcome = ('rejected' if status != 'MATCH' else
               'true_identity_nonunique' if tied else
               'correct' if user == truth else 'wrong_identity_accepted')
    return dict(status=status, user_id=user if status == 'MATCH' else None,
                score=float(best), second_score=float(second), outcome=outcome, tied=tied)
