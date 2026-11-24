from types import SimpleNamespace
import pytest
from palm_app import debug_ui
import pklnet_tracker


def test_thread_options_reach_libraries_before_camera_start(monkeypatch):
    events = []
    monkeypatch.setattr('sys.argv', ['debug_ui.py', '--capture-only', '--enable-recognition', '--demo-matcher', 'FastCCDemo-v6', '--opencv-threads', '2', '--pklnet-threads', '2'])
    monkeypatch.setattr(debug_ui.cv2, 'setNumThreads', lambda n: events.append(('cv', n)))
    def camera(*args, **kwargs):
        assert kwargs['capture_only'] is False
        events.append(('camera', kwargs['pklnet_threads']))
        return SimpleNamespace(close=lambda: None)
    monkeypatch.setattr(debug_ui, 'CameraFeed', camera)
    def app(*args, **kwargs):
        assert kwargs['demo_matcher'] == 'FastCCDemo-v6'
        return SimpleNamespace(demo_algorithm=None)
    monkeypatch.setattr(debug_ui, 'App', app)
    monkeypatch.setattr(debug_ui, 'make_handler', lambda app: None)
    def stop():
        raise KeyboardInterrupt
    monkeypatch.setattr(debug_ui, 'ThreadingHTTPServer', lambda *a: SimpleNamespace(serve_forever=stop, server_close=lambda: None))
    assert debug_ui.main() == 0
    assert events == [('cv', 2), ('camera', 2)]


def test_tracker_does_not_pass_onnx_options_to_hand_detector(monkeypatch):
    seen = {}
    def engine(**kwargs):
        seen['engine'] = kwargs
        return SimpleNamespace(_ensure_loaded=lambda: None)
    def detector(*args, **kwargs):
        seen['detector'] = kwargs
    monkeypatch.setattr(pklnet_tracker, 'PKLNetROI', engine)
    monkeypatch.setattr(pklnet_tracker.palm_roi, 'HandLandmarkTracker', detector)
    pklnet_tracker.PKLNetTracker(pklnet_threads=2, input_size=(320, 240))
    assert seen == {'engine': {'threads': 2}, 'detector': {'input_size': (320, 240)}}


@pytest.mark.parametrize('option', ['--opencv-threads', '--pklnet-threads'])
def test_thread_options_reject_zero(monkeypatch, option):
    monkeypatch.setattr('sys.argv', ['debug_ui.py', option, '0'])
    with pytest.raises(SystemExit) as exc:
        debug_ui.main()
    assert exc.value.code == 2


def test_native_cli_is_explicit_and_reaches_the_same_demo_instance(tmp_path, monkeypatch):
    library = tmp_path / "descriptor_match.so"
    library.write_bytes(b"test library placeholder")
    events = []
    algorithm = SimpleNamespace(close=lambda: events.append("algorithm-close"))
    monkeypatch.setattr('sys.argv', ['debug_ui.py', '--enable-recognition',
        '--demo-matcher', 'FastCCRetainedEvidence-v27-experimental',
        '--native-registration', str(library), '--native-threads', '2'])
    monkeypatch.setattr(debug_ui, 'CameraFeed', lambda *a, **k: SimpleNamespace(close=lambda: events.append("camera-close")))
    monkeypatch.setattr(debug_ui, 'App', lambda *a, **k: SimpleNamespace(demo_algorithm=algorithm))
    monkeypatch.setattr('native_registration.enable_native_registration',
        lambda instance, path, threads: events.append((instance is algorithm, path, threads)))
    monkeypatch.setattr(debug_ui, 'make_handler', lambda app: None)
    def stop():
        raise KeyboardInterrupt
    monkeypatch.setattr(debug_ui, 'ThreadingHTTPServer', lambda *a: SimpleNamespace(serve_forever=stop, server_close=lambda: None))
    assert debug_ui.main() == 0
    assert events == [(True, library, 2), "camera-close", "algorithm-close"]


@pytest.mark.parametrize('arguments', [
    ['--native-registration', 'missing.so'],
    ['--enable-recognition', '--native-registration', 'missing.so'],
    ['--native-threads', '3'],
])
def test_invalid_native_cli_fails_before_camera_start(monkeypatch, arguments):
    monkeypatch.setattr('sys.argv', ['debug_ui.py', *arguments])
    monkeypatch.setattr(debug_ui, 'CameraFeed', lambda *a, **k: pytest.fail('Camera must not start'))
    with pytest.raises(SystemExit) as exc:
        debug_ui.main()
    assert exc.value.code == 2
