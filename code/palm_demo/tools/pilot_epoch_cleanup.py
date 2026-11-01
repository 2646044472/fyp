"""Collect unreachable objects after an isolated HTTP epoch has returned.

The epoch's handler classes/closures can own the App and its gallery until its
stack frame ends. Collection *inside* that frame cannot release those owners.
This helper touches only garbage in the calling process; no process termination,
OS memory setting, allocator trimming or promise of an RSS reduction is involved.
"""
import gc


def collect_finished_epoch():
    import psutil
    process = psutil.Process()
    before = process.memory_info().rss
    collected = gc.collect()
    return dict(scope='unreachable objects in current process after epoch return',
                collected_objects=collected, rss_before=before,
                rss_after=process.memory_info().rss,
                available_after=psutil.virtual_memory().available)
