"""Integration tests for snapshot HTTP routes."""

import pytest

from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store(tmp_path):
    return RequestStore(str(tmp_path / "store.json"))


@pytest.fixture()
def client(store):
    app = create_app(store)
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


def test_list_snapshots_unknown_id(client):
    resp = client.get("/requests/nope/snapshots")
    assert resp.status_code == 404


def test_save_snapshot_unknown_id(client):
    resp = client.post("/requests/nope/snapshots/v1")
    assert resp.status_code == 404


def test_save_and_list_snapshots(client):
    rid = _post_hook(client, {"val": 1})
    resp = client.post(f"/requests/{rid}/snapshots/v1")
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["snapshot"] == "v1"
    assert data["body"]["val"] == 1

    list_resp = client.get(f"/requests/{rid}/snapshots")
    assert list_resp.status_code == 200
    assert "v1" in list_resp.get_json()["snapshots"]


def test_get_snapshot(client):
    rid = _post_hook(client, {"z": 42})
    client.post(f"/requests/{rid}/snapshots/snap1")
    resp = client.get(f"/requests/{rid}/snapshots/snap1")
    assert resp.status_code == 200
    assert resp.get_json()["body"]["z"] == 42


def test_get_snapshot_missing(client):
    rid = _post_hook(client)
    resp = client.get(f"/requests/{rid}/snapshots/ghost")
    assert resp.status_code == 404


def test_delete_snapshot(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/snapshots/to_del")
    resp = client.delete(f"/requests/{rid}/snapshots/to_del")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == "to_del"

    check = client.get(f"/requests/{rid}/snapshots/to_del")
    assert check.status_code == 404


def test_delete_snapshot_missing(client):
    rid = _post_hook(client)
    resp = client.delete(f"/requests/{rid}/snapshots/ghost")
    assert resp.status_code == 404
