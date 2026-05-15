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


def _post_hook(client):
    resp = client.post(
        "/hooks/test",
        json={"key": "value"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_list_evidence_unknown_id(client):
    resp = client.get("/requests/no-such-id/evidence")
    assert resp.status_code == 404


def test_add_evidence_unknown_id(client):
    resp = client.post("/requests/no-such-id/evidence", json={"kind": "url", "content": "https://x.com"})
    assert resp.status_code == 404


def test_add_and_list_evidence(client):
    rid = _post_hook(client)
    resp = client.post(
        f"/requests/{rid}/evidence",
        json={"kind": "url", "content": "https://example.com", "label": "ref"},
    )
    assert resp.status_code == 201
    eid = resp.get_json()["id"]
    assert eid

    resp2 = client.get(f"/requests/{rid}/evidence")
    assert resp2.status_code == 200
    items = resp2.get_json()["evidence"]
    assert len(items) == 1
    assert items[0]["kind"] == "url"
    assert items[0]["label"] == "ref"


def test_add_evidence_invalid_kind(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/evidence", json={"kind": "blob", "content": "data"})
    assert resp.status_code == 400


def test_delete_evidence(client):
    rid = _post_hook(client)
    add_resp = client.post(f"/requests/{rid}/evidence", json={"kind": "hash", "content": "abc123"})
    eid = add_resp.get_json()["id"]

    del_resp = client.delete(f"/requests/{rid}/evidence/{eid}")
    assert del_resp.status_code == 204

    list_resp = client.get(f"/requests/{rid}/evidence")
    assert list_resp.get_json()["evidence"] == []


def test_delete_evidence_unknown_item(client):
    rid = _post_hook(client)
    resp = client.delete(f"/requests/{rid}/evidence/no-such-eid")
    assert resp.status_code == 404
