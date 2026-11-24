import threading

import numpy as np

from demo_flow import DemoFlow


class Algorithm:
    name = 'concurrency-test'


def test_busy_device_retries_do_not_extend_idle_deadline(tmp_path, monkeypatch):
    import demo_flow
    clock = [10.0]
    monkeypatch.setattr(demo_flow.time, 'monotonic', lambda: clock[0])
    flow = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(4), '', 'mock'))
    flow.enrollment_candidate = lambda: None
    token = flow.enrollment_start('p_left', 'P', 'left')['token']
    assert flow.enrollment_capture_lock.acquire(blocking=False)
    try:
        clock[0] += 590
        busy = flow.enrollment_step(token)
        assert busy['status'] == 'WAIT' and busy['retry_after_ms'] == 1000
        assert busy['timeout_seconds_remaining'] == 10
        clock[0] += 11
        assert flow.enrollment_step(token)['status'] == 'STOPPED'
        assert flow.enrollment_status(token)['status'] == 'EXPIRED'
    finally:
        flow.enrollment_capture_lock.release()


def test_cancel_and_status_during_capture(tmp_path):
    flow = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(4), '', 'mock'))
    token = flow.enrollment_start('p_left', 'P', 'left')['token']
    entered, release, cancelled = threading.Event(), threading.Event(), threading.Event()
    def capture():
        entered.set()
        assert release.wait(3)
        return np.ones(4), 'roi', 'mock', {'contrast': 25, 'sharpness': 8}, np.arange(1024, dtype=np.uint8).reshape(32, 32)
    flow.enrollment_candidate = capture
    worker = threading.Thread(target=lambda: flow.enrollment_step(token), daemon=True)
    worker.start()
    assert entered.wait(1)
    result = {}
    def cancel():
        result['status'] = flow.enrollment_status(token)['status']
        result['cancel'] = flow.enrollment_cancel(token)['status']
        cancelled.set()
    observer = threading.Thread(target=cancel, daemon=True)
    observer.start()
    try:
        assert cancelled.wait(.4)
        assert result == {'status': 'PAUSED', 'cancel': 'CANCELLED'}
    finally:
        release.set()
        worker.join(2)
        observer.join(2)


def test_late_result_cannot_touch_new_session_and_capture_remains_busy(tmp_path):
    import pytest
    from demo_flow import CaptureProcessingFailure
    for failure in (None, CaptureProcessingFailure('LOW_QUALITY'), RuntimeError('late')):
        flow = DemoFlow(tmp_path / str(type(failure).__name__), Algorithm(), lambda: (np.zeros(4), '', 'mock'))
        token = flow.enrollment_start('old_left', 'Old', 'left')['token']
        entered, release = threading.Event(), threading.Event()
        calls, result = [], []
        def capture():
            calls.append(1)
            entered.set()
            assert release.wait(3)
            if failure:
                raise failure
            return np.ones(4), 'roi', 'mock', {'contrast': 25, 'sharpness': 8}, np.arange(1024, dtype=np.uint8).reshape(32, 32)
        flow.enrollment_candidate = capture
        worker = threading.Thread(target=lambda: result.append(flow.enrollment_step(token)), daemon=True)
        worker.start()
        assert entered.wait(1)
        pending = flow.enrollment_step(token)
        assert pending['status'] == 'WAIT' and pending['retry_after_ms'] == 1000
        assert flow.enrollment_step(token, selection_only=True)['status'] == 'WAIT'
        with pytest.raises(ValueError, match='Capture in progress'):
            flow.enrollment_commit(token, 'left')
        assert flow.enrollment_cancel(token)['status'] == 'CANCELLED'
        new = flow.enrollment_start('new_left', 'New', 'left')['token']
        busy = flow.enrollment_step(new)
        assert busy['status'] == 'WAIT' and busy['retry_after_ms'] == 1000
        assert 'Previous frame still processing' in busy['reason']
        assert len(calls) == 1
        release.set()
        worker.join(2)
        assert not worker.is_alive()
        assert result[0]['status'] == 'STOPPED'
        state = flow.enrollment_status(new)
        assert state['attempts'] == state['quality_failures'] == state['candidate_pool_count'] == 0
        flow.enrollment_candidate = lambda: (_ for _ in ()).throw(RuntimeError('retry'))
        assert flow.enrollment_step(new)['capture_failure'] == 'CAPTURE_ERROR'


def test_expired_capture_failure_does_not_change_failure_counts(tmp_path):
    import time
    from demo_flow import CaptureProcessingFailure
    flow = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(4), '', 'mock'))
    token = flow.enrollment_start('p_left', 'P', 'left')['token']
    def capture():
        flow.enrollment_session['last_activity'] = time.monotonic() - 601
        raise CaptureProcessingFailure('LOW_QUALITY')
    flow.enrollment_candidate = capture
    assert flow.enrollment_step(token)['status'] == 'STOPPED'
    assert flow.enrollment_session['quality_failures'] == 0
    assert flow.enrollment_status(token)['status'] == 'EXPIRED'


def test_unexpected_callback_exception_releases_capture_lock(tmp_path):
    import pytest
    flow = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(4), '', 'mock'))
    token = flow.enrollment_start('p_left', 'P', 'left')['token']
    def fail():
        raise OSError('unexpected')
    flow.enrollment_candidate = fail
    with pytest.raises(OSError, match='unexpected'):
        flow.enrollment_step(token)
    assert not flow.enrollment_capture_lock.locked()
    assert not flow.enrollment_session['capture_in_flight']
    flow.enrollment_candidate = lambda: (_ for _ in ()).throw(ValueError('retry'))
    assert flow.enrollment_step(token)['capture_failure'] == 'CAPTURE_ERROR'


def test_app_enrollment_and_identification_share_device_lock():
    from types import SimpleNamespace
    import pytest
    from demo_flow import CaptureProcessingFailure
    from palm_app.debug_ui import App
    entered, release = threading.Event(), threading.Event()
    def capture():
        entered.set()
        assert release.wait(3)
        raise OSError('fake camera')
    app = object.__new__(App)
    app.collection_lock = threading.Lock()
    app.camera = SimpleNamespace(status=lambda: {'camera_ready': True, 'roi_status_fresh': True, 'quality_status': 'READY', 'quality_consecutive_frames': 5, 'quality_required_frames': 5}, capture_highres=capture)
    errors = []
    def enrollment():
        try:
            app.capture_demo_feature(enrollment=True, include_candidate=True)
        except CaptureProcessingFailure as exc:
            errors.append(exc.reason)
    worker = threading.Thread(target=enrollment, daemon=True)
    worker.start()
    assert entered.wait(1)
    try:
        with pytest.raises(CaptureProcessingFailure) as caught:
            app.capture_demo_feature(require_live_ready=True)
        assert caught.value.reason == 'CAMERA_BUSY'
    finally:
        release.set()
        worker.join(2)
    assert errors == ['CAMERA_UNAVAILABLE']
    assert not app.collection_lock.locked()


def test_expired_session_late_callbacks_leave_new_session_untouched(tmp_path):
    import time
    from demo_flow import CaptureProcessingFailure
    for failure in (None, CaptureProcessingFailure('LOW_QUALITY'), RuntimeError('late')):
        flow = DemoFlow(tmp_path / type(failure).__name__, Algorithm(), lambda: (np.zeros(4), '', 'mock'))
        old = flow.enrollment_start('old_left', 'Old', 'left')['token']
        entered, release = threading.Event(), threading.Event()
        result = []
        def capture():
            entered.set()
            assert release.wait(3)
            if failure is not None:
                raise failure
            return np.ones(4), 'roi', 'mock', {'contrast': 25, 'sharpness': 8}, np.arange(1024, dtype=np.uint8).reshape(32, 32)
        flow.enrollment_candidate = capture
        worker = threading.Thread(target=lambda: result.append(flow.enrollment_step(old)), daemon=True)
        worker.start()
        assert entered.wait(1)
        try:
            with flow.lock:
                flow.enrollment_session['last_activity'] = time.monotonic() - 601
            assert flow.enrollment_status(old)['status'] == 'EXPIRED'
            new = flow.enrollment_start('new_left', 'New', 'left')['token']
            assert flow.enrollment_step(new)['status'] == 'WAIT'
            release.set()
            worker.join(2)
            assert not worker.is_alive()
            assert result[0]['status'] == 'STOPPED'
            assert flow.enrollment_status(old)['status'] == 'EXPIRED'
            state = flow.enrollment_status(new)
            assert state['attempts'] == state['quality_failures'] == state['candidate_pool_count'] == 0
            assert not flow.enrollment_capture_lock.locked()
            flow.enrollment_candidate = lambda: (_ for _ in ()).throw(ValueError('retry'))
            assert flow.enrollment_step(new)['capture_failure'] == 'CAPTURE_ERROR'
        finally:
            release.set()
            worker.join(2)


def test_http_cancel_and_new_session_during_blocked_step(tmp_path):
    import json
    from http.server import ThreadingHTTPServer
    from types import SimpleNamespace
    from urllib.request import Request, urlopen
    from palm_app.debug_ui import make_handler

    flow = DemoFlow(tmp_path, Algorithm(), lambda: (np.zeros(4), '', 'mock'))
    entered, release = threading.Event(), threading.Event()
    def capture():
        entered.set()
        if not release.wait(5):
            raise RuntimeError('test capture timed out')
        return np.ones(4), 'roi', 'mock', {'contrast': 25, 'sharpness': 8}, np.arange(1024, dtype=np.uint8).reshape(32, 32)
    flow.enrollment_candidate = capture
    app = SimpleNamespace(capture_only=False, demo=flow)
    class QuietHandler(make_handler(app)):
        def log_message(self, _format, *_args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    def post(action, payload):
        request = Request(f'http://127.0.0.1:{server.server_port}/api/demo/enroll/{action}',
                          data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=2) as response:
            return json.loads(response.read())
    result, errors = [], []
    def old_step(token):
        try:
            result.append(post('step', {'token': token}))
        except Exception as exc:
            errors.append(exc)
    worker = None
    try:
        old = post('start', {'user_id': 'old_left', 'display_name': 'Old', 'hand': 'left'})['token']
        worker = threading.Thread(target=old_step, args=(old,), daemon=True)
        worker.start()
        assert entered.wait(1)
        assert post('status', {'token': old})['status'] == 'PAUSED'
        assert post('cancel', {'token': old})['status'] == 'CANCELLED'
        new = post('start', {'user_id': 'new_left', 'display_name': 'New', 'hand': 'left'})['token']
        assert post('step', {'token': new})['status'] == 'WAIT'
        release.set()
        worker.join(2)
        assert not worker.is_alive() and not errors
        assert result[0]['status'] == 'STOPPED'
        state = post('status', {'token': new})
        assert state['attempts'] == state['candidate_pool_count'] == state['quality_failures'] == 0
        assert not flow.enrollment_capture_lock.locked()
    finally:
        release.set()
        if worker is not None:
            worker.join(2)
        server.shutdown()
        server.server_close()
        server_thread.join(2)
