"""Integration tests for severity routes."""

import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post(
        "/hooks/test",
        json={"event": "push"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_get_severity_unknown_id(client):
    resp = client.get("/requests/doesnotexist/severity")
    assert resp.status_code == 404


def test_set_and_get_severity(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/severity", json={"level": "warning"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["severity"] == "warning"

    resp2 = client.get(f"/requests/{rid}/severity")
    assert resp2.status_code == 200
    assert resp2.get_json()["severity"] == "warning"


def test_set_severity_invalid_level(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/severity", json={"level": "fatal"})
    assert resp.status_code == 400
    assert "Invalid severity" in resp.get_json()["error"]


def test_delete_severity(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/severity", json={"level": "error"})
    resp = client.delete(f"/requests/{rid}/severity")
    assert resp.status_code == 200
    assert resp.get_json()["severity"] is None


def test_list_by_severity(client):
    rid1 = _post_hook(client)
    rid2 = _post_hook(client)
    client.put(f"/requests/{rid1}/severity", json={"level": "error"})
    client.put(f"/requests/{rid2}/severity", json={"level": "info"})
    resp = client.get("/requests/severity/error")
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.get_json()]
    assert rid1 in ids
    assert rid2 not in ids
