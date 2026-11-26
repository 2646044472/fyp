"""Person-disjoint roles and cosine top-1 accounting on every planned probe."""
from collections import Counter
import numpy as np


def check_people(train, validation, evaluation):
    groups = [set(train), set(validation), set(evaluation)]
    if any(not g for g in groups) or any(groups[i] & groups[j] for i, j in ((0, 1), (0, 2), (1, 2))):
        raise ValueError("Empty or overlapping subject split")


def evaluate(gallery, probes):
    """Rows are (hand_class, vector_or_None). Do not discard failed probes."""
    def unit(x):
        if x is None:
            return None
        x = np.asarray(x, dtype=float)
        if x.ndim != 1 or not np.isfinite(x).all() or np.linalg.norm(x) == 0:
            return None
        return x / np.linalg.norm(x)
    valid = [(c, unit(x)) for c, x in gallery]
    valid = [(c, x) for c, x in valid if x is not None]
    labels = [c for c, x in valid]
    scores = np.stack([x for c, x in valid]) if valid else None
    counts = Counter()
    for label, x in probes:
        x = unit(x)
        if x is None:
            counts['query_failed'] += 1
        elif label not in labels:
            counts['true_gallery_missing'] += 1
        else:
            pred = labels[int(np.argmax(scores @ x))]
            counts['correct' if pred == label else 'incorrect'] += 1
    return dict(planned=sum(counts.values()), **counts)
