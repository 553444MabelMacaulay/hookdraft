"""Integration tests for bookmark routes."""

import pytest

from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store(tmp_path):
    return RequestStore(str(tmp_path / "store.json"))


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client, path="/hook", body=b'{"x": 1}'):
    resp = client.post(
        path,
        data=body,
        content_type="application/json",
    )
    return resp.get_json()["id"]


def test_bookmark_unknown_id(client):
    resp = client.post("/requests/nope/bookmark")
    assert resp.status_code == 404


def test_unbookmark_unknown_id(client):
    resp = client.delete("/requests/nope/bookmark")
    assert resp.status_code == 404


def test_status_unknown_id(client):
    resp = client.get("/requests/nope/bookmark")
    assert resp.status_code == 404


def test_bookmark_and_check_status(client):
    req_id = _post_hook(client)
    resp = client.post(f"/requests/{req_id}/bookmark")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["bookmarked"] is True

    status = client.get(f"/requests/{req_id}/bookmark").get_json()
    assert status["bookmarked"] is True


def test_unbookmark_clears_status(client):
    req_id = _post_hook(client)
    client.post(f"/requests/{req_id}/bookmark")
    client.delete(f"/requests/{req_id}/bookmark")
    status = client.get(f"/requests/{req_id}/bookmark").get_json()
    assert status["bookmarked"] is False


def test_list_bookmarks_returns_only_bookmarked(client):
    id1 = _post_hook(client, body=b'{"a": 1}')
    id2 = _post_hook(client, body=b'{"b": 2}')
    client.post(f"/requests/{id1}/bookmark")

    resp = client.get("/bookmarks")
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.get_json()]
    assert id1 in ids
    assert id2 not in ids


def test_list_bookmarks_empty(client):
    _post_hook(client)
    resp = client.get("/bookmarks")
    assert resp.status_code == 200
    assert resp.get_json() == []
