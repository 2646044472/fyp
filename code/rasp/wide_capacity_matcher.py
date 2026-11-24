"""Explicit larger numeric envelopes for unchanged full-resolution evidence.

The outer payload layout, ROI extraction, view count, distances and gates are
unchanged. More capacity prevents valid high-resolution images from failing
solely because their lossless PNG plus complete descriptors exceed 16 MiB.
This is an engineering compatibility option, not a demonstrated accuracy or
generalization improvement. The default device matcher stays at 16 MiB.
"""

from lazy_cached_matcher import LazyCachedRetainedMatcher
from union_matcher import FEATURE_SIZE, MAX_FEATURE_CAPACITY_BYTES


class WideCapacityLazyMatcher(LazyCachedRetainedMatcher):
    """V28 mathematics/cache with an opt-in 64 MiB packed feature envelope.

    Legacy v26-v28 16 MiB envelopes are accepted only as explicit compatible
    imports. A newly extracted feature is always 64 MiB. Five enrollment
    features must have a uniform length before stacking; never mix imported
    16 MiB and fresh 64 MiB frames in one enrollment array.
    """

    name = 'FastCCWideLazy-v29-experimental'
    magic = LazyCachedRetainedMatcher.magic
    feature_capacity_bytes = MAX_FEATURE_CAPACITY_BYTES
    legacy_feature_capacity_bytes = (FEATURE_SIZE,)
