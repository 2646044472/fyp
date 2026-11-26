"""Source-local pair supervision and angular proxy loss."""
import math
import torch
from torch.nn import functional as F


def pair_arc_loss(embeddings, proxies, valid, labels):
    """Exact .60 pair/.40 ArcFace recipe; divide summed losses by planned 2P."""
    if (embeddings.ndim != 3 or embeddings.shape[0] != 2 or valid.dtype != torch.bool
            or valid.shape != labels.shape or valid.shape != embeddings.shape[:2]
            or proxies.ndim != 2 or proxies.shape[1] != embeddings.shape[-1]):
        raise ValueError("incompatible paired loss inputs")
    width = embeddings.shape[1]
    features, target = embeddings[valid], labels[valid].long()
    if (width < 1 or len(features) < 1 or torch.any(target < 0)
            or torch.any(target >= proxies.shape[0])):
        raise ValueError("empty loss update or invalid labels")
    a, b = valid
    paired = torch.nonzero(a & b, as_tuple=True)[0]
    if paired.numel():
        x, y = embeddings[0, a], embeddings[1, b]
        ix = a.long().cumsum(0)[paired] - 1
        iy = b.long().cumsum(0)[paired] - 1
        pair = (F.cross_entropy(x[ix] @ y.T / .07, iy, reduction="sum")
                + F.cross_entropy(y[iy] @ x.T / .07, ix, reduction="sum")) / (2 * width)
    else:
        pair = embeddings.new_zeros(())
    similarities = features @ F.normalize(proxies, dim=1).T
    match = similarities.gather(1, target[:, None]).clamp(-.999999, .999999)
    phi = match * math.cos(.3) - (1 - match.square()).sqrt() * math.sin(.3)
    arc = F.cross_entropy(similarities.scatter(1, target[:, None], phi) * 30,
                          target, reduction="sum") / (2 * width)
    return .6 * pair + .4 * arc, pair, arc


def warm_cosine(step, total):
    """Historical 100-update warmup, then cosine with a 0.1 floor."""
    if not 0 <= step <= total:
        raise ValueError("step outside schedule")
    if step <= 100:
        return step / 100.
    return .1 + .9 * .5 * (1 + math.cos(math.pi * (step - 100) / max(total - 100, 1)))
