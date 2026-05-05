"""Integration tests for Flask webhook routes."""

import json
import pytest

from hookdraft.app import create_app


@pytest.fixture()
def client():
    app = create_app(persist_path=None)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def post_hook(client, path="/hooks/my-service", body=None, content_type="application/json"):
    payload = body or json.dumps({"event": "push"})
    return client.post(path, data=payload, content_type=content_type)


def test_webhook_returns_200(client):
    resp = post_hook(client)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "id" in data
    assert data["status"] == "received"


def test_list_requests(client):
    post_hook(client)
    post_hook(client)
    resp = client.get("/api/requests")
    assert resp.status_code == 200
    records = resp.get_json()
    assert len(records) == 2


def test_list_requests_limit(client):
    for _ in range(10):
        post_hook(client)
    resp = client.get("/api/requests?limit=3")
    assert len(resp.get_json()) == 3


def test_get_single_request(client):
    resp = post_hook(client)
    record_id = resp.get_json()["id"]
    detail = client.get(f"/api/requests/{record_id}")
    assert detail.status_code == 200
    assert detail.get_json()["id"] == record_id


def test_get_missing_request(client):
    resp = client.get("/api/requests/does-not-exist")
    assert resp.status_code == 404


def test_clear_requests(client):
    post_hook(client)
    post_hook(client)
    resp = client.delete("/api/requests")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == 2
    assert client.get("/api/requests").get_json() == []


def test_different_http_methods(client):
    client.put("/hooks/svc", data="{}", content_type="application/json")
    client.patch("/hooks/svc", data="{}", content_type="application/json")
    client.delete("/hooks/svc")
    records = client.get("/api/requests").get_json()
    methods = {r["method"] for r in records}
    assert methods == {"PUT", "PATCH", "DELETE"}
