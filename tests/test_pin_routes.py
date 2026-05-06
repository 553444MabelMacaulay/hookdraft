"""Integration tests for pin/unpin HTTP routes."""

from __future__ import annotations

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
    resp = client.post("/hooks/test", data=b'{"x": 1}', content_type="application/json")
    assert resp.status_code == 200
    return resp.get_json()["id"]


def test_pin_unknown_id(client):
    resp = client.post("/requests/does-not-exist/pin")
    assert resp.status_code == 404


def test_pin_and_check_status(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/pin")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["pinned"] is True
    assert data["id"] == rid

    status = client.get(f"/requests/{rid}/pin").get_json()
    assert status["pinned"] is True


def test_unpin_request(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/pin")
    resp = client.delete(f"/requests/{rid}/pin")
    assert resp.status_code == 200
    assert resp.get_json()["pinned"] is False

    status = client.get(f"/requests/{rid}/pin").get_json()
    assert status["pinned"] is False


def test_list_pinned_empty(client):
    _post_hook(client)  # not pinned
    resp = client.get("/requests/pinned")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_pinned_returns_only_pinned(client):
    rid1 = _post_hook(client)
    rid2 = _post_hook(client)
    client.post(f"/requests/{rid1}/pin")

    resp = client.get("/requests/pinned")
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.get_json()]
    assert rid1 in ids
    assert rid2 not in ids


def test_pin_status_unknown_id(client):
    resp = client.get("/requests/ghost/pin")
    assert resp.status_code == 404
