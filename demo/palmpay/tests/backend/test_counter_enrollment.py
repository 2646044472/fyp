import httpx

from backend import main, pc_enrollment
from backend.authorization.station import StationProvider
from test_payments import setup


def test_counter_requires_customer_credentials_and_consent(setup):
    operator, customer, _ = setup
    data = {"email":"lena@example.test", "password":"wrong-pass", "hand":"left", "capture_consent":True}
    assert operator.post('/api/merchant/enrollments', json=data).status_code == 401
    data['password'] = 'testing-password'
    data['capture_consent'] = False
    assert operator.post('/api/merchant/enrollments', json=data).status_code == 422
    assert customer.post('/api/merchant/enrollments', json=data).status_code == 401


def test_counter_capture_binds_saved_template_and_scopes_requests(setup, monkeypatch):
    operator, customer, _ = setup
    station = StationProvider('http://127.0.0.1:8080', 0.80)
    monkeypatch.setattr(main, 'provider', station)
    saved = {}
    requests = []

    def upstream(request):
        import json
        requests.append(request.url.path)
        if request.url.path == '/enroll':
            return httpx.Response(200, text="<html><head></head><body><script>const enroll='/api/demo/enroll/';</script></body></html>")
        if request.url.path == '/api/demo/enroll/start':
            saved.update(json.loads(request.content))
            return httpx.Response(200, json={"status":"CAPTURING"})
        if request.url.path == '/api/demo/enroll/commit':
            data = json.loads(request.content)
            assert data['token'] == saved['token']
            assert data['confirm_hand'] == 'left'
            return httpx.Response(200, json={"status":"SAVED"})
        if request.url.path == '/api/demo/users':
            return httpx.Response(200, json={"users":[{"user_id":saved['user_id']}]})
        raise AssertionError(request.url.path)

    original = httpx.AsyncClient
    monkeypatch.setattr(pc_enrollment.httpx, 'AsyncClient',
                        lambda **kwargs: original(**kwargs, transport=httpx.MockTransport(upstream)))
    data = {"email":"lena@example.test", "password":"testing-password", "hand":"left", "capture_consent":True}
    first = operator.post('/api/merchant/enrollments', json=data).json()
    assert operator.post('/api/merchant/enrollments', json=data).json() == first
    base = '/api/merchant/enrollments/' + first['id']
    assert customer.get(base+'/station/').status_code == 401
    assert operator.post(base+'/station/api/library/delete', json={}).status_code == 404
    page = operator.get(base+'/station/')
    assert base+'/station/api/demo/enroll/' in page.text
    response = operator.post(base+'/station/api/demo/enroll/start', json={"token":"client-token", "user_id":"wrong", "hand":"right"})
    assert response.status_code == 200
    assert saved['user_id'].startswith('pp_') and saved['hand'] == 'left'
    assert saved['token'] != 'client-token'
    assert operator.post(base+'/station/api/demo/enroll/commit', json={"confirm_hand":"right"}).status_code == 200
    assert operator.get(base).json()['enrolled']
    assert customer.get('/api/palm/status').json()['status'] == 'enrolled'
    station.client.close()
