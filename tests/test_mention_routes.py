"""Integration tests for mention HTTP routes."""

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


def _post_hook(client, path="/hook"):
    resp = client.post(
        path,
        json={"event": "ping"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def _add_mention(client, rid, handle):
    """Helper to POST a mention and return the response."""
    return client.post(f"/requests/{rid}/mentions", json={"handle": handle})


def test_list_mentions_unknown_id(client):
    resp = client.get("/requests/no-such-id/mentions")
    assert resp.status_code == 404


def test_add_mention_unknown_id(client):
    resp = client.post("/requests/no-such-id/mentions", json={"handle": "alice"})
    assert resp.status_code == 404


def test_add_and_list_mentions(client):
    rid = _post_hook(client)
    resp = _add_mention(client, rid, "@alice")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "alice" in data["mentions"]

    resp2 = client.get(f"/requests/{rid}/mentions")
    assert resp2.status_code == 200
    assert "alice" in resp2.get_json()["mentions"]


def test_add_mention_empty_handle_returns_400(client):
    rid = _post_hook(client)
    resp = _add_mention(client, rid, "")
    assert resp.status_code == 400


def test_add_duplicate_mention(client):
    """Adding the same handle twice should not create duplicate entries."""
    rid = _post_hook(client)
    _add_mention(client, rid, "bob")
    resp = _add_mention(client, rid, "bob")
    assert resp.status_code == 200
    mentions = resp.get_json()["mentions"]
    assert mentions.count("bob") == 1


def test_remove_mention_unknown_id(client):
    resp = client.delete("/requests/no-such-id/mentions/alice")
    assert resp.status_code == 404


def test_remove_mention(client):
    rid = _post_hook(client)
    _add_mention(client, rid, "alice")
    resp = client.delete(f"/requests/{rid}/mentions/alice")
    assert resp.status_code == 200
    assert "alice" not in resp.get_json()["mentions"]
