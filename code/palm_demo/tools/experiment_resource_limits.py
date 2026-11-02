"""Shared byte-exact limits for the bounded CPU diagnostic drivers.

The authorized boundary is available RAM >=12 GiB at startup, >=2 GiB while
running, and worker RSS <=14 GiB. This module samples nothing and starts no work.
"""

GIB = 1024**3
START_AVAILABLE_BYTES = 12 * GIB
RUNNING_AVAILABLE_BYTES = 2 * GIB
MAX_RSS_BYTES = 14 * GIB


def resource_fault(available, rss, *, startup=False):
    minimum = START_AVAILABLE_BYTES if startup else RUNNING_AVAILABLE_BYTES
    if available < minimum:
        return 'startup_available_ram' if startup else 'running_available_ram'
    if rss > MAX_RSS_BYTES:
        return 'rss_above_limit'
    return None
