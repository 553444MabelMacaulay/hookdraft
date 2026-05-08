"""Integration tests for routing HTTP routes."""

import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store)
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


def test_list_routes_unknown_id(client):
    resp = client.get("/requests/unknown-id/routes")
    assert resp.status_code == 404


def test_add_route_unknown_id(client):
    resp = client.post("/requests/unknown-id/routes", json={"name": "r", "pattern": "/x"})
    assert resp.status_code == 404


def test_add_and_list_routes(client):
    rid = _post_hook(client)
    resp = client.post(
        f"/requests/{rid}/routes",
        json={"name": "my-rule", "pattern": "/hooks/.*", "method": "POST"},
    )
    assert resp.status_code == 201
    resp2 = client.get(f"/requests/{rid}/routes")
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert "my-rule" in data
    assert data["my-rule"]["method"] == "POST"


def test_add_route_bad_regex(client):
    rid = _post_hook(client)
    resp = client.post(
        f"/requests/{rid}/routes",
        json={"name": "bad", "pattern": "[unclosed"},
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_delete_route(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/routes", json={"name": "r", "pattern": "/x"})
    resp = client.delete(f"/requests/{rid}/routes/r")
    assert resp.status_code == 204
    data = client.get(f"/requests/{rid}/routes").get_json()
    assert "r" not in data


def test_match_route_unknown_id(client):
    resp = client.get("/requests/nope/routes/match")
    assert resp.status_code == 404


def test_match_route_returns_none_when_empty(client):
    rid = _post_hook(client)
    resp = client.get(f"/requests/{rid}/routes/match")
    assert resp.status_code == 200
    assert resp.get_json()["matched"] is None
