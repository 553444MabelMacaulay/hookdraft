"""Integration tests for suppression HTTP routes."""

import pytest

from hookdraft.app import create_app
from hookdraft.routes.suppression_routes import register_suppression_routes
from hookdraft.storage import RequestStore


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    register_suppression_routes(app, store=store)
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


def test_suppression_status_unknown_id(client):
    resp = client.get("/requests/does-not-exist/suppression")
    assert resp.status_code == 404


def test_suppress_unknown_id(client):
    resp = client.post("/requests/does-not-exist/suppression", json={})
    assert resp.status_code == 404


def test_unsuppress_unknown_id(client):
    resp = client.delete("/requests/does-not-exist/suppression")
    assert resp.status_code == 404


def test_suppress_and_check_status(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/suppression", json={"reason": "too noisy"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["suppressed"] is True
    assert data["reason"] == "too noisy"

    status = client.get(f"/requests/{rid}/suppression").get_json()
    assert status["suppressed"] is True
    assert status["reason"] == "too noisy"


def test_unsuppress_clears_flag(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/suppression", json={"reason": "spam"})
    resp = client.delete(f"/requests/{rid}/suppression")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["suppressed"] is False
    assert data["reason"] is None


def test_default_status_is_not_suppressed(client):
    rid = _post_hook(client)
    resp = client.get(f"/requests/{rid}/suppression")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["suppressed"] is False
    assert data["reason"] is None
