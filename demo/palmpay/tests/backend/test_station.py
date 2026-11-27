import httpx
import pytest

from backend import main
from backend.authorization.station import StationProvider
from test_payments import order_and_intent, setup


def station_client(expected_identity, decision="MATCH"):
    station = StationProvider("http://127.0.0.1:8080", 0.85)
    station.timeout = 0.05
    calls = []

    def handler(request):
        import json
        path = request.url.path
        body = json.loads(request.content) if request.content else None
        calls.append((path, body))
        if path == "/station-health":
            return httpx.Response(200, json={"backend":"fpn-c-e10-frozen", "mode":"scores_only"})
        if path == "/api/demo/users":
            return httpx.Response(200, json={"users":[{"user_id":expected_identity["id"]}]})
        if path == "/api/fpn/camera":
            return httpx.Response(200, json={"camera_open":body["action"] == "start"})
        if path == "/api/fpn/verify":
            assert body["threshold"] == 0.85
            assert next(payload["token"] for route,payload in calls if route == "/api/fpn/camera") == body["token"]
            return httpx.Response(200, json={"mode":"demo_verification", "threshold":0.85,
                "decision":decision, "tied_top": False, "top_cosines":[0.90],
                "best_match":{"user_id":expected_identity["id"], "hand":"left"}})
        raise AssertionError(path)

    station.client.close()
    station.client = httpx.Client(base_url="http://127.0.0.1:8080", transport=httpx.MockTransport(handler))
    return station, calls


@pytest.mark.parametrize("decision,balance,status", [("MATCH",47500,"paid"),("BELOW_THRESHOLD",50000,"failed")])
def test_station_link_and_authorize(setup, monkeypatch, decision, balance, status):
    operator, customer, _ = setup
    identity = {"id":"not-yet-enrolled"}
    station, calls = station_client(identity, decision)
    monkeypatch.setattr(main, "provider", station)
    register = operator.get("/api/merchant/session").json()
    assert register["station"] and not register["demo"]
    assert customer.get("/api/palm/status").json()["status"] == "unregistered"
    assert customer.post("/api/palm/pairing", json={"hand":"left"}).status_code == 422
    code = customer.post("/api/palm/pairing", json={"hand":"left","allow_station_capture":True}).json()["code"]
    assert customer.post("/api/station/pairing", json={"code":code}).status_code == 401
    pair = operator.post("/api/station/pairing", json={"code":code}).json()
    assert pair["identity"].startswith("pp_") and pair["hand"] == "left"
    assert operator.post("/api/station/enroll", json={"code":code}).status_code == 409
    identity["id"] = pair["identity"]
    assert operator.post("/api/station/enroll", json={"code":code}).status_code == 200
    assert customer.get("/api/palm/status").json()["status"] == "enrolled"
    _, intent = order_and_intent(operator)
    route = f"/api/station/payments/{intent['id']}/authorize"
    assert customer.post(route).status_code == 401
    assert operator.post(f"/api/dev/payments/{intent['id']}/simulate", json={}).status_code == 404
    result = operator.post(route).json()
    assert result["status"] == status
    assert operator.post(route).json() == result
    assert customer.get("/api/wallet").json()["balance"] == balance
    assert [body["action"] for path, body in calls if path == "/api/fpn/camera"] == ["start", "stop"]


def test_station_url_must_be_loopback_and_threshold_explicit():
    for address in ("https://127.0.0.1:8080", "http://example.test:8080", "http://user@127.0.0.1:8080"):
        with pytest.raises(ValueError):
            StationProvider(address, 0.85)
    with pytest.raises(ValueError):
        StationProvider("http://127.0.0.1:8080", float("nan"))



def test_reposition_then_match_and_camera_cleanup(monkeypatch):
    from backend.authorization.provider import Challenge
    import time
    station, calls = station_client({"id":"pp_test"})
    station.timeout = 2
    original = station.client._transport
    checks = 0

    def response(request):
        nonlocal checks
        reply = original.handle_request(request)
        if request.url.path == "/api/fpn/verify":
            checks += 1
            if checks == 1:
                data = reply.json()
                data["decision"] = "BELOW_THRESHOLD"
                return httpx.Response(200, json=data)
        return reply

    station.client._transport = httpx.MockTransport(response)
    challenge = Challenge("intent", "cklc", 2500, "MOP", int(time.time()) + 30)
    result = station.authorize(challenge)
    assert checks == 2 and result.identity == "pp_test"
    assert calls[-1][1]["action"] == "stop"
    station.client.close()


def test_cancel_releases_camera_before_another_frame():
    from backend.authorization.provider import Challenge
    from backend.authorization.station import StationNoMatch
    import time
    station, calls = station_client({"id":"pp_test"})
    with pytest.raises(StationNoMatch):
        station.authorize(Challenge("intent", "cklc", 2500, "MOP", int(time.time()) + 30),
                          should_cancel=lambda: True)
    assert not any(path == "/api/fpn/verify" for path, _ in calls)
    assert calls[-1][1]["action"] == "stop"
    station.client.close()
