"""Integration tests for tag routes."""
import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore
from hookdraft.routes.tag_routes import register_tag_routes


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store)
    register_tag_routes(app, store_fn=lambda: store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client, body="{}"):
    resp = client.post("/hook", data=body, content_type="application/json")
    return client.get("/requests").get_json()["requests"][0]["id"]


def test_list_tags_unknown_id(client):
    resp = client.get("/requests/does-not-exist/tags")
    assert resp.status_code == 404


def test_add_and_list_tags(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/tags", json={"tag": "smoke"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "smoke" in data["tags"]

    resp2 = client.get(f"/requests/{rid}/tags")
    assert resp2.status_code == 200
    assert "smoke" in resp2.get_json()["tags"]


def test_add_tag_empty_returns_400(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/tags", json={"tag": ""})
    assert resp.status_code == 400


def test_remove_tag(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/tags", json={"tag": "alpha"})
    client.post(f"/requests/{rid}/tags", json={"tag": "beta"})
    resp = client.delete(f"/requests/{rid}/tags/alpha")
    assert resp.status_code == 200
    assert "alpha" not in resp.get_json()["tags"]
    assert "beta" in resp.get_json()["tags"]


def test_list_all_tags(client):
    rid1 = _post_hook(client)
    rid2 = _post_hook(client)
    client.post(f"/requests/{rid1}/tags", json={"tag": "foo"})
    client.post(f"/requests/{rid2}/tags", json={"tag": "bar"})
    resp = client.get("/tags")
    assert resp.status_code == 200
    tags = resp.get_json()["tags"]
    assert "foo" in tags
    assert "bar" in tags
    assert tags == sorted(tags)


def test_list_all_tags_empty(client):
    resp = client.get("/tags")
    assert resp.status_code == 200
    assert resp.get_json()["tags"] == []
