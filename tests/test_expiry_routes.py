import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store(tmp_path):
    return RequestStore(str(tmp_path / "test.json"))


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post(
        "/hooks/test",
        json={"key": "value"},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    return resp.get_json()["id"]


def test_get_expiry_unknown_id(client):
    resp = client.get("/requests/nonexistent/expiry")
    assert resp.status_code == 404


def test_set_expiry_unknown_id(client):
    resp = client.put("/requests/nonexistent/expiry", json={"ttl": 60})
    assert resp.status_code == 404


def test_delete_expiry_unknown_id(client):
    resp = client.delete("/requests/nonexistent/expiry")
    assert resp.status_code == 404


def test_set_and_get_expiry(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/expiry", json={"ttl": 300})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["expires_at"] is not None

    resp2 = client.get(f"/requests/{rid}/expiry")
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2["expires_at"] == data["expires_at"]
    assert data2["expired"] is False


def test_delete_expiry(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/expiry", json={"ttl": 300})
    resp = client.delete(f"/requests/{rid}/expiry")
    assert resp.status_code == 200
    assert resp.get_json()["expires_at"] is None

    resp2 = client.get(f"/requests/{rid}/expiry")
    assert resp2.get_json()["expires_at"] is None


def test_set_expiry_invalid_ttl(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/expiry", json={"ttl": -10})
    assert resp.status_code == 400


def test_set_expiry_missing_ttl(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/expiry", json={})
    assert resp.status_code == 400


def test_list_expired_empty(client):
    _post_hook(client)
    resp = client.get("/requests/expired")
    assert resp.status_code == 200
    assert resp.get_json() == []
