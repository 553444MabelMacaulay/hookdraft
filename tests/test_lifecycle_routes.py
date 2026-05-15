"""Integration tests for lifecycle HTTP routes."""

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
    assert resp.status_code == 200
    return resp.get_json()["id"]


def test_get_lifecycle_unknown_id(client):
    resp = client.get("/requests/nonexistent/lifecycle")
    assert resp.status_code == 404


def test_set_lifecycle_unknown_id(client):
    resp = client.put("/requests/nonexistent/lifecycle", json={"state": "new"})
    assert resp.status_code == 404


def test_delete_lifecycle_unknown_id(client):
    resp = client.delete("/requests/nonexistent/lifecycle")
    assert resp.status_code == 404


def test_get_lifecycle_default_none(client):
    req_id = _post_hook(client)
    resp = client.get(f"/requests/{req_id}/lifecycle")
    assert resp.status_code == 200
    assert resp.get_json()["lifecycle"] is None


def test_set_and_get_lifecycle(client):
    req_id = _post_hook(client)
    resp = client.put(f"/requests/{req_id}/lifecycle", json={"state": "processing"})
    assert resp.status_code == 200
    assert resp.get_json()["state"] == "processing"

    resp = client.get(f"/requests/{req_id}/lifecycle")
    assert resp.status_code == 200
    data = resp.get_json()["lifecycle"]
    assert data["state"] == "processing"


def test_set_lifecycle_with_actor_and_note(client):
    req_id = _post_hook(client)
    client.put(
        f"/requests/{req_id}/lifecycle",
        json={"state": "failed", "actor": "Bob", "note": "Timeout"},
    )
    resp = client.get(f"/requests/{req_id}/lifecycle")
    data = resp.get_json()["lifecycle"]
    assert data["actor"] == "bob"
    assert data["note"] == "Timeout"


def test_set_lifecycle_invalid_state(client):
    req_id = _post_hook(client)
    resp = client.put(f"/requests/{req_id}/lifecycle", json={"state": "bogus"})
    assert resp.status_code == 400


def test_delete_lifecycle(client):
    req_id = _post_hook(client)
    client.put(f"/requests/{req_id}/lifecycle", json={"state": "new"})
    resp = client.delete(f"/requests/{req_id}/lifecycle")
    assert resp.status_code == 200
    assert resp.get_json()["lifecycle"] is None
