"""Integration tests for archive routes."""

import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore
from hookdraft.routes import register_all_routes
from hookdraft.routes.archive_routes import register_archive_routes


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    register_archive_routes(app, store=store)
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


def test_archive_status_unknown_id(client):
    resp = client.get("/requests/missing/archive")
    assert resp.status_code == 404


def test_archive_unknown_id(client):
    resp = client.post("/requests/missing/archive")
    assert resp.status_code == 404


def test_unarchive_unknown_id(client):
    resp = client.post("/requests/missing/unarchive")
    assert resp.status_code == 404


def test_archive_and_check_status(client):
    rid = _post_hook(client)
    resp = client.get(f"/requests/{rid}/archive")
    assert resp.status_code == 200
    assert resp.get_json()["archived"] is False

    resp = client.post(f"/requests/{rid}/archive")
    assert resp.status_code == 200
    assert resp.get_json()["archived"] is True

    resp = client.get(f"/requests/{rid}/archive")
    assert resp.get_json()["archived"] is True


def test_unarchive_clears_flag(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/archive")
    resp = client.post(f"/requests/{rid}/unarchive")
    assert resp.status_code == 200
    assert resp.get_json()["archived"] is False


def test_list_archived(client):
    rid1 = _post_hook(client)
    _post_hook(client)
    client.post(f"/requests/{rid1}/archive")
    resp = client.get("/requests/archived")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["id"] == rid1
