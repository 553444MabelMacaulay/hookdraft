"""Integration tests for flag HTTP routes."""

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
        json={"event": "ping"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_flag_status_unknown_id(client):
    resp = client.get("/requests/does-not-exist/flag")
    assert resp.status_code == 404


def test_flag_unknown_id(client):
    resp = client.post("/requests/does-not-exist/flag", json={})
    assert resp.status_code == 404


def test_unflag_unknown_id(client):
    resp = client.delete("/requests/does-not-exist/flag")
    assert resp.status_code == 404


def test_flag_and_check_status(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/flag", json={"reason": "suspicious"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flagged"] is True
    assert data["reason"] == "suspicious"

    status = client.get(f"/requests/{rid}/flag").get_json()
    assert status["flagged"] is True
    assert status["reason"] == "suspicious"


def test_unflag_clears_status(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/flag", json={"reason": "check me"})
    resp = client.delete(f"/requests/{rid}/flag")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flagged"] is False
    assert data["reason"] == ""


def test_flag_default_status_unflagged(client):
    rid = _post_hook(client)
    resp = client.get(f"/requests/{rid}/flag")
    assert resp.status_code == 200
    assert resp.get_json()["flagged"] is False
