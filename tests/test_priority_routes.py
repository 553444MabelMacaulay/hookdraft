"""Integration tests for priority HTTP routes."""

import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store(tmp_path):
    return RequestStore(storage_dir=str(tmp_path))


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post(
        "/hooks/test",
        json={"event": "ping"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_get_priority_unknown_id(client):
    resp = client.get("/requests/unknown/priority")
    assert resp.status_code == 404


def test_set_priority_unknown_id(client):
    resp = client.put("/requests/unknown/priority", json={"level": "high"})
    assert resp.status_code == 404


def test_set_and_get_priority(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/priority", json={"level": "critical"})
    assert resp.status_code == 200
    assert resp.get_json()["priority"] == "critical"

    resp = client.get(f"/requests/{rid}/priority")
    assert resp.status_code == 200
    assert resp.get_json()["priority"] == "critical"


def test_set_priority_invalid_level(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/priority", json={"level": "extreme"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_set_priority_missing_level(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/priority", json={})
    assert resp.status_code == 400


def test_delete_priority(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/priority", json={"level": "low"})
    resp = client.delete(f"/requests/{rid}/priority")
    assert resp.status_code == 200
    assert resp.get_json()["priority"] is None


def test_list_levels(client):
    resp = client.get("/priority/levels")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "levels" in data
    assert "low" in data["levels"]
    assert "critical" in data["levels"]
