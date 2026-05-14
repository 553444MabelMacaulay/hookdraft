import pytest
from hookdraft.app import create_app
from hookdraft.storage import RequestStore
from hookdraft.categorisation_routes import register_categorisation_routes


@pytest.fixture()
def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store)
    register_categorisation_routes(app, store_fn=lambda: store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post("/hooks/test", json={"event": "ping"})
    return resp.get_json()["id"]


def test_get_category_unknown_id(client):
    resp = client.get("/requests/missing/category")
    assert resp.status_code == 404


def test_set_category_unknown_id(client):
    resp = client.put("/requests/missing/category", json={"name": "ops"})
    assert resp.status_code == 404


def test_delete_category_unknown_id(client):
    resp = client.delete("/requests/missing/category")
    assert resp.status_code == 404


def test_set_and_get_category(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/category", json={"name": "billing"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["category"]["name"] == "billing"
    assert data["category"]["colour"] == "#888888"

    resp2 = client.get(f"/requests/{rid}/category")
    assert resp2.status_code == 200
    assert resp2.get_json()["category"]["name"] == "billing"


def test_set_category_with_colour(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/category", json={"name": "ops", "colour": "#123456"})
    assert resp.status_code == 200
    assert resp.get_json()["category"]["colour"] == "#123456"


def test_set_category_empty_name_returns_400(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/category", json={"name": ""})
    assert resp.status_code == 400


def test_delete_category(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/category", json={"name": "infra"})
    resp = client.delete(f"/requests/{rid}/category")
    assert resp.status_code == 200
    assert resp.get_json()["category"] is None

    resp2 = client.get(f"/requests/{rid}/category")
    assert resp2.get_json()["category"] is None
