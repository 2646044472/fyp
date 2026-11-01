import gc
import importlib
from pathlib import Path
from types import SimpleNamespace
import weakref


def test_http_handler_owners_collected_after_epoch_returns(monkeypatch):
    app_root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(app_root)); monkeypatch.syspath_prepend(str(app_root/'tools'))
    from palm_app.debug_ui import make_handler
    from http.server import ThreadingHTTPServer
    cleanup = importlib.import_module('pilot_epoch_cleanup')

    class FakeApp:
        def capture(self):
            raise AssertionError('No capture or inference in a cleanup test')

    def finished_epoch():
        app = FakeApp()
        # A bound capture method creates the same App->demo->App owner cycle.
        app.demo = SimpleNamespace(capture_feature=app.capture)
        ref = weakref.ref(app)
        handler = make_handler(app)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        server.server_close()
        gc.collect()
        assert ref() is not None  # still owned by this live epoch's locals
        return ref

    enabled = gc.isenabled()
    gc.disable()
    try:
        first = finished_epoch()
        assert first() is not None
        receipt = cleanup.collect_finished_epoch()
        assert first() is None
        assert receipt['collected_objects'] > 0
        assert receipt['rss_before'] > 0 and receipt['rss_after'] > 0
        second = finished_epoch()
        cleanup.collect_finished_epoch()
        assert second() is None
    finally:
        if enabled: gc.enable()
