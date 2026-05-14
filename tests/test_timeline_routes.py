"""Integration tests for timeline HTTP routes."""

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
        json={"key": "value"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_list_events_unknown_id(client):
    resp = client.get("/requests/nope/timeline")
    assert resp.status_code == 404


def test_add_event_unknown_id(client):
    resp = client.post("/requests/nope/timeline", json={"name": "start"})
    assert resp.status_code == 404


def test_clear_events_unknown_id(client):
    resp = client.delete("/requests/nope/timeline")
    assert resp.status_code == 404


def test_add_and_list_events(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/timeline", json={"name": "received"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "received"

    resp2 = client.get(f"/requests/{rid}/timeline")
    assert resp2.status_code == 200
    body = resp2.get_json()
    assert body["id"] == rid
    assert len(body["events"]) == 1
    assert body["events"][0]["name"] == "received"


def test_add_event_with_detail(client):
    rid = _post_hook(client)
    resp = client.post(
        f"/requests/{rid}/timeline",
        json={"name": "processed", "detail": "all good"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["detail"] == "all good"


def test_add_event_empty_name_returns_400(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/timeline", json={"name": ""})
    assert resp.status_code == 400


def test_clear_events(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/timeline", json={"name": "a"})
    client.post(f"/requests/{rid}/timeline", json={"name": "b"})
    resp = client.delete(f"/requests/{rid}/timeline")
    assert resp.status_code == 200
    assert resp.get_json()["cleared"] is True
    events = client.get(f"/requests/{rid}/timeline").get_json()["events"]
    assert events == []
