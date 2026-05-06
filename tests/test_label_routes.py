"""Integration tests for label routes."""

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


def _post_hook(client, path="/hook", method="POST", body=None):
    return client.post(
        path,
        json=body or {"key": "value"},
        content_type="application/json",
    )


def test_list_labels_unknown_id(client):
    resp = client.get("/requests/no-such-id/labels")
    assert resp.status_code == 404


def test_add_and_list_labels(client):
    hook_resp = _post_hook(client)
    req_id = hook_resp.get_json()["id"]

    resp = client.post(
        f"/requests/{req_id}/labels",
        json={"name": "env", "colour": "blue"},
    )
    assert resp.status_code == 200
    assert resp.get_json() == {"env": "blue"}

    list_resp = client.get(f"/requests/{req_id}/labels")
    assert list_resp.status_code == 200
    assert list_resp.get_json()["env"] == "blue"


def test_add_label_missing_name(client):
    hook_resp = _post_hook(client)
    req_id = hook_resp.get_json()["id"]
    resp = client.post(f"/requests/{req_id}/labels", json={"colour": "red"})
    assert resp.status_code == 400


def test_add_label_invalid_colour(client):
    hook_resp = _post_hook(client)
    req_id = hook_resp.get_json()["id"]
    resp = client.post(
        f"/requests/{req_id}/labels",
        json={"name": "env", "colour": "pink"},
    )
    assert resp.status_code == 400


def test_delete_label(client):
    hook_resp = _post_hook(client)
    req_id = hook_resp.get_json()["id"]
    client.post(f"/requests/{req_id}/labels", json={"name": "env", "colour": "red"})
    del_resp = client.delete(f"/requests/{req_id}/labels/env")
    assert del_resp.status_code == 200
    assert "env" not in del_resp.get_json()


def test_search_by_label_name(client):
    _post_hook(client)
    hook_resp = _post_hook(client, body={"other": 1})
    req_id = hook_resp.get_json()["id"]
    client.post(f"/requests/{req_id}/labels", json={"name": "env", "colour": "green"})

    search_resp = client.get("/labels?name=env")
    assert search_resp.status_code == 200
    results = search_resp.get_json()
    assert len(results) == 1
    assert results[0]["id"] == req_id
