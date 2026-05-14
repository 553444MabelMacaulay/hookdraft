"""Integration tests for resolution HTTP routes."""

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
    resp = client.post("/hooks/test", json={"x": 1})
    return resp.get_json()["id"]


def test_get_resolution_unknown_id(client):
    resp = client.get("/requests/nope/resolution")
    assert resp.status_code == 404


def test_set_resolution_unknown_id(client):
    resp = client.put("/requests/nope/resolution", json={"resolver": "alice"})
    assert resp.status_code == 404


def test_delete_resolution_unknown_id(client):
    resp = client.delete("/requests/nope/resolution")
    assert resp.status_code == 404


def test_set_and_get_resolution(client):
    rid = _post_hook(client)
    put = client.put(f"/requests/{rid}/resolution", json={"resolver": "alice", "note": "all good"})
    assert put.status_code == 200
    data = put.get_json()["resolution"]
    assert data["resolved"] is True
    assert data["resolver"] == "alice"
    assert data["note"] == "all good"

    get = client.get(f"/requests/{rid}/resolution")
    assert get.status_code == 200
    assert get.get_json()["resolution"]["resolver"] == "alice"


def test_set_resolution_empty_resolver_returns_400(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/resolution", json={"resolver": ""})
    assert resp.status_code == 400


def test_delete_resolution(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/resolution", json={"resolver": "bob"})
    delete = client.delete(f"/requests/{rid}/resolution")
    assert delete.status_code == 200
    assert delete.get_json()["resolution"] is None

    get = client.get(f"/requests/{rid}/resolution")
    assert get.get_json()["resolution"] is None
