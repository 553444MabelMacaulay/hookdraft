import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def store(tmp_path):
    return RequestStore(storage_dir=str(tmp_path))


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client, path="/hook"):
    resp = client.post(path, json={"key": "value"})
    return resp.get_json()["id"]


def test_list_annotations_unknown_id(client):
    resp = client.get("/requests/no-such-id/annotations")
    assert resp.status_code == 404


def test_add_annotation_unknown_id(client):
    resp = client.post("/requests/no-such-id/annotations", json={"text": "hi"})
    assert resp.status_code == 404


def test_add_and_list_annotations(client):
    rid = _post_hook(client)
    resp = client.post(
        f"/requests/{rid}/annotations",
        json={"text": "first note", "author": "tester"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["text"] == "first note"
    assert data["author"] == "tester"

    list_resp = client.get(f"/requests/{rid}/annotations")
    assert list_resp.status_code == 200
    annotations = list_resp.get_json()["annotations"]
    assert len(annotations) == 1
    assert annotations[0]["text"] == "first note"


def test_add_annotation_empty_text_returns_400(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/annotations", json={"text": "   "})
    assert resp.status_code == 400


def test_delete_annotation(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/annotations", json={"text": "to delete"})
    del_resp = client.delete(f"/requests/{rid}/annotations/0")
    assert del_resp.status_code == 204
    list_resp = client.get(f"/requests/{rid}/annotations")
    assert list_resp.get_json()["annotations"] == []


def test_delete_annotation_invalid_index(client):
    rid = _post_hook(client)
    resp = client.delete(f"/requests/{rid}/annotations/99")
    assert resp.status_code == 404
