"""Persistent, bounded stage and resource logs for supervised device debugging."""
from functools import wraps
import json
import logging
import math
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import resource
import threading
import time
import uuid

_logger = logging.getLogger('palm.diagnostics')
_logger.propagate = False
_file_handler = None

_STATUSES = frozenset(('COLLECTING', 'READY', 'WAIT', 'STOPPED', 'NO_HAND', 'PAUSED',
                       'CANCELLED', 'COMPLETED', 'EXPIRED', 'LOST', 'MATCH', 'UNKNOWN',
                       'RETRY', 'DELETED'))
_REASONS = frozenset(('NO_HAND', 'ROI_UNSTABLE', 'LOW_QUALITY', 'ROI_GEOMETRY_INVALID',
                      'CAMERA_BUSY', 'CAMERA_UNAVAILABLE', 'CAPTURE_TIMEOUT', 'ROI_NOT_READY',
                      'CAPTURE_ERROR', 'GALLERY_INVALID_TEMPLATES', 'GALLERY_INCOMPATIBLE_TEMPLATES',
                      'INVALID_MATCH_SCORES', 'INCOMPATIBLE_TEMPLATES', 'NO_ENROLLED_USERS',
                      'SCORE_ABOVE_THRESHOLD', 'TIED_BEST_SCORES', 'AMBIGUOUS_MARGIN',
                      'UNCONFIGURED_SCORE_FAMILY', 'RF_SCORE_ABOVE_THRESHOLD',
                      'INSUFFICIENT_CANDIDATES', 'RF_MARGIN', 'POLICY_SCORE_ABOVE_THRESHOLD',
                      'POLICY_AMBIGUOUS_MARGIN'))


def _code(value, allowed):
    return value if type(value) is str and value in allowed else 'OTHER'


def _stage_details(result, stage_name):
    if type(result) is not dict:
        return {}
    details = {}
    for key, allowed in (('status', _STATUSES), ('reason', _REASONS), ('capture_failure', _REASONS),
                         ('selection_mode', frozenset(('five_candidate_wait', 'full_candidate_pool')))):
        if key in result:
            details[key] = None if result[key] is None else _code(result[key], allowed)
    for key in ('candidate_pool_count', 'attempts', 'duplicate_frames', 'quality_failures'):
        value = result.get(key)
        if type(value) is int and 0 <= value <= 10000000:
            details[key] = value
    timing = result.get('timing_ms')
    if type(timing) is dict:
        details['timing_ms'] = {key: timing[key] for key in ('capture_and_extract', 'gallery', 'total')
                                if key in timing and type(timing[key]) in (int, float)
                                and math.isfinite(timing[key]) and 0 <= timing[key] <= 1e9}
    diagnostic_id = result.get('diagnostic_id')
    if (stage_name in ('DemoFlow.enrollment_start', 'DemoFlow.enrollment_step', 'DemoFlow.enrollment_commit')
            and type(diagnostic_id) is str and len(diagnostic_id) == 32
            and all(c in '0123456789abcdef' for c in diagnostic_id)):
        details['diagnostic_id'] = diagnostic_id
    return details


def event(name, **fields):
    if _file_handler is None:
        return
    pages = int(Path('/proc/self/statm').read_text().split()[1])
    _logger.info(json.dumps({'event': name, 'time_unix': time.time(), 'monotonic': time.monotonic(),
                            'pid': os.getpid(), 'thread': threading.current_thread().name,
                            'rss_bytes': pages * os.sysconf('SC_PAGE_SIZE'),
                            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                            **fields}, ensure_ascii=False))
    for handler in (_file_handler,):
        handler.acquire()
        try:
            handler.flush()
            os.fsync(handler.stream.fileno())
        finally:
            handler.release()


def safe_event(name, **fields):
    """Diagnostics must never change the outcome of the operation being traced."""
    try:
        event(name, **fields)
    except Exception:
        pass


def stage(function):
    @wraps(function)
    def traced(*args, **kwargs):
        if _file_handler is None:
            return function(*args, **kwargs)
        call_id = uuid.uuid4().hex[:12]
        started = time.monotonic()
        safe_event('stage_start', stage=function.__qualname__, call_id=call_id)
        try:
            result = function(*args, **kwargs)
        except BaseException as error:
            try:
                safe_event('stage_error', stage=function.__qualname__, call_id=call_id,
                      elapsed_ms=(time.monotonic() - started) * 1000,
                      error_type=_code(type(error).__name__, frozenset(('CaptureProcessingFailure', 'ValueError',
                                       'RuntimeError', 'OSError', 'TimeoutError'))),
                      reason=_code(getattr(error, 'reason', None), _REASONS))
            except BaseException:
                pass
            raise
        else:
            try:
                details = _stage_details(result, function.__qualname__)
            except Exception:
                details = {}
            safe_event('stage_end', stage=function.__qualname__, call_id=call_id,
                  elapsed_ms=(time.monotonic() - started) * 1000, **details)
            return result
    return traced


def configure(directory):
    global _file_handler
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(directory / 'stages.jsonl', maxBytes=5_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter('%(message)s'))
    _logger.addHandler(handler)
    _file_handler = handler
    _logger.setLevel(logging.INFO)
    event('process_start', host=os.uname().nodename,
          boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
