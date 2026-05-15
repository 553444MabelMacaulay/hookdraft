"""Integration tests for narration HTTP routes."""

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


def _post_hook(client):
    resp = client.post(
        "/hooks/test",
        json={"event": "ping"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_get_narration_unknown_id(client):
    resp = client.get("/requests/nope/narration")
    assert resp.status_code == 404


def test_set_narration_unknown_id(client):
    resp = client.put("/requests/nope/narration", json={"text": "hello"})
    assert resp.status_code == 404


def test_delete_narration_unknown_id(client):
    resp = client.delete("/requests/nope/narration")
    assert resp.status_code == 404


def test_get_narration_not_set(client):
    req_id = _post_hook(client)
    resp = client.get(f"/requests/{req_id}/narration")
    assert resp.status_code == 200
    assert resp.get_json()["narration"] is None


def test_set_and_get_narration(client):
    req_id = _post_hook(client)
    resp = client.put(
        f"/requests/{req_id}/narration",
        json={"text": "Sent by CI pipeline.", "author": "ci-bot"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["narration"]
    assert data["text"] == "Sent by CI pipeline."
    assert data["author"] == "ci-bot"

    get_resp = client.get(f"/requests/{req_id}/narration")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["narration"]["text"] == "Sent by CI pipeline."


def test_set_narration_invalid_text(client):
    req_id = _post_hook(client)
    resp = client.put(f"/requests/{req_id}/narration", json={"text": "   "})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_delete_narration(client):
    req_id = _post_hook(client)
    client.put(f"/requests/{req_id}/narration", json={"text": "to remove"})
    del_resp = client.delete(f"/requests/{req_id}/narration")
    assert del_resp.status_code == 200
    assert del_resp.get_json()["narration"] is None

    get_resp = client.get(f"/requests/{req_id}/narration")
    assert get_resp.get_json()["narration"] is None
