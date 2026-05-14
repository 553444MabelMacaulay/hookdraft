"""Integration tests for attribution HTTP routes."""

import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store(tmp_path):
    return RequestStore(str(tmp_path / "store.json"))


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post("/hook", json={"event": "test"})
    return resp.get_json()["id"]


def test_get_attribution_unknown_id(client):
    resp = client.get("/requests/nonexistent/attribution")
    assert resp.status_code == 404


def test_set_attribution_unknown_id(client):
    resp = client.put("/requests/nonexistent/attribution", json={"source": "manual"})
    assert resp.status_code == 404


def test_delete_attribution_unknown_id(client):
    resp = client.delete("/requests/nonexistent/attribution")
    assert resp.status_code == 404


def test_get_attribution_default_none(client):
    rid = _post_hook(client)
    resp = client.get(f"/requests/{rid}/attribution")
    assert resp.status_code == 200
    assert resp.get_json()["attribution"] is None


def test_set_and_get_attribution(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/attribution", json={"source": "scheduled", "actor": "cron"})
    assert resp.status_code == 200
    data = resp.get_json()["attribution"]
    assert data["source"] == "scheduled"
    assert data["actor"] == "cron"


def test_set_attribution_invalid_source(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/attribution", json={"source": "robot"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_delete_attribution(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/attribution", json={"source": "manual"})
    resp = client.delete(f"/requests/{rid}/attribution")
    assert resp.status_code == 200
    assert resp.get_json()["attribution"] is None
    # confirm it's gone
    resp2 = client.get(f"/requests/{rid}/attribution")
    assert resp2.get_json()["attribution"] is None
