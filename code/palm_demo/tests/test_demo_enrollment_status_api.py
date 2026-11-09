import json
import threading
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from palm_app.debug_ui import make_handler


def test_enrollment_status_api_requires_and_forwards_token():
    seen = []

    def status(token):
        seen.append(token)
        if token != "valid-token":
            raise ValueError("录入会话已失效，请重新开始。")
        return {"status": "PAUSED", "user_id": "p1_left"}

    app = SimpleNamespace(capture_only=False, demo=SimpleNamespace(enrollment_status=status))

    class QuietServer(ThreadingHTTPServer):
        def handle_error(self, request, client_address):
            raise AssertionError("request handler raised unexpectedly")

    class QuietHandler(make_handler(app)):
        def log_message(self, _format, *_args):
            pass

    server = QuietServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f"http://127.0.0.1:{server.server_port}/api/demo/enroll/status"

        def post(token):
            body = json.dumps({"token": token}).encode()
            request = Request(endpoint, data=body, headers={"Content-Type": "application/json"})
            return urlopen(request, timeout=2)

        with post("valid-token") as response:
            assert response.status == 200
            assert json.loads(response.read()) == {"status": "PAUSED", "user_id": "p1_left"}
        try:
            post("invalid-token")
        except HTTPError as error:
            assert error.code == 400
            assert "已失效" in json.loads(error.read())["message"]
        else:
            raise AssertionError("invalid enrollment token was accepted")
        assert seen == ["valid-token", "invalid-token"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
