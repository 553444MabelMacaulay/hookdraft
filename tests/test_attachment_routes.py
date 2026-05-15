"""Integration tests for attachment HTTP routes."""
import base64
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


def test_list_attachments_unknown_id(client):
    resp = client.get("/requests/no-such-id/attachments")
    assert resp.status_code == 404


def test_add_attachment_unknown_id(client):
    payload = {
        "name": "file.txt",
        "mime_type": "text/plain",
        "data": base64.b64encode(b"hello").decode(),
    }
    resp = client.post("/requests/no-such-id/attachments", json=payload)
    assert resp.status_code == 404


def test_add_and_list_attachments(client):
    req_id = _post_hook(client)
    payload = {
        "name": "notes.txt",
        "mime_type": "text/plain",
        "data": base64.b64encode(b"some notes").decode(),
    }
    resp = client.post(f"/requests/{req_id}/attachments", json=payload)
    assert resp.status_code == 201
    att_id = resp.get_json()["id"]

    resp = client.get(f"/requests/{req_id}/attachments")
    assert resp.status_code == 200
    items = resp.get_json()["attachments"]
    assert len(items) == 1
    assert items[0]["id"] == att_id
    assert items[0]["name"] == "notes.txt"
    assert "data" not in items[0]  # list view strips raw data


def test_get_single_attachment(client):
    req_id = _post_hook(client)
    encoded = base64.b64encode(b"binary").decode()
    resp = client.post(
        f"/requests/{req_id}/attachments",
        json={"name": "blob", "mime_type": "application/octet-stream", "data": encoded},
    )
    att_id = resp.get_json()["id"]

    resp = client.get(f"/requests/{req_id}/attachments/{att_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == att_id
    assert base64.b64decode(data["data"]) == b"binary"


def test_delete_attachment(client):
    req_id = _post_hook(client)
    encoded = base64.b64encode(b"x").decode()
    resp = client.post(
        f"/requests/{req_id}/attachments",
        json={"name": "tmp", "mime_type": "text/plain", "data": encoded},
    )
    att_id = resp.get_json()["id"]

    resp = client.delete(f"/requests/{req_id}/attachments/{att_id}")
    assert resp.status_code == 200
    assert resp.get_json()["removed"] is True

    resp = client.get(f"/requests/{req_id}/attachments")
    assert resp.get_json()["attachments"] == []


def test_delete_unknown_attachment(client):
    req_id = _post_hook(client)
    resp = client.delete(f"/requests/{req_id}/attachments/ghost-id")
    assert resp.status_code == 404


def test_add_attachment_invalid_base64(client):
    req_id = _post_hook(client)
    resp = client.post(
        f"/requests/{req_id}/attachments",
        json={"name": "f", "mime_type": "text/plain", "data": "!!!not-base64!!!"},
    )
    assert resp.status_code == 400
