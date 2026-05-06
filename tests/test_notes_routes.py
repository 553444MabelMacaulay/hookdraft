"""Integration tests for notes routes."""

import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore
from hookdraft.routes.notes_routes import register_notes_routes


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    register_notes_routes(app)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client, body=None):
    resp = client.post(
        "/hooks/test",
        json=body or {"event": "ping"},
        content_type="application/json",
    )
    return resp.get_json()["id"]


def test_get_note_unknown_id(client):
    resp = client.get("/requests/unknown-id/note")
    assert resp.status_code == 404


def test_set_and_get_note(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/note", json={"note": "my annotation"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["note"] == "my annotation"

    resp2 = client.get(f"/requests/{rid}/note")
    assert resp2.status_code == 200
    assert resp2.get_json()["note"] == "my annotation"


def test_set_note_empty_returns_400(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/note", json={"note": ""})
    assert resp.status_code == 400


def test_delete_note(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/note", json={"note": "to delete"})
    resp = client.delete(f"/requests/{rid}/note")
    assert resp.status_code == 200
    assert resp.get_json()["note"] is None

    resp2 = client.get(f"/requests/{rid}/note")
    assert resp2.get_json()["note"] is None


def test_search_by_note(client):
    rid1 = _post_hook(client, {"event": "a"})
    rid2 = _post_hook(client, {"event": "b"})
    client.put(f"/requests/{rid1}/note", json={"note": "critical alert"})
    client.put(f"/requests/{rid2}/note", json={"note": "routine check"})

    resp = client.get("/requests/search/note?q=critical")
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["id"] == rid1


def test_search_by_note_missing_q(client):
    resp = client.get("/requests/search/note")
    assert resp.status_code == 400
