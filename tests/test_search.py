import pytest
from flask import Flask
from hookdraft.storage import RequestStore, RequestRecord
from hookdraft.routes.search_routes import register_search_routes
from hookdraft.search import filter_records
import datetime


def _make_record(method="POST", path="/hook", headers=None, body="{}"):
    return RequestRecord(
        id="test-id",
        method=method,
        path=path,
        headers=headers or {"Content-Type": "application/json"},
        body=body,
        timestamp=datetime.datetime.utcnow().isoformat(),
    )


@pytest.fixture
def client():
    store = RequestStore()
    app = Flask(__name__)
    app.config["TESTING"] = True
    register_search_routes(app, store=store)

    store.save(_make_record(method="POST", path="/hook/orders", body='{"item": "book"}'))
    store.save(_make_record(method="GET", path="/hook/status", body=""))
    store.save(
        _make_record(
            method="POST",
            path="/hook/payments",
            headers={"X-Signature": "abc123"},
            body='{"amount": 50}',
        )
    )

    with app.test_client() as c:
        yield c


def test_search_by_method(client):
    resp = client.get("/requests/search?method=GET")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["method"] == "GET"


def test_search_by_path(client):
    resp = client.get("/requests/search?path=payments")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert "payments" in data[0]["path"]


def test_search_by_body(client):
    resp = client.get("/requests/search?body=book")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1


def test_search_by_header_key(client):
    resp = client.get("/requests/search?header_key=X-Signature")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1


def test_search_by_header_key_and_value(client):
    resp = client.get("/requests/search?header_key=X-Signature&header_value=abc123")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_search_no_match(client):
    resp = client.get("/requests/search?method=DELETE")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_search_invalid_limit(client):
    resp = client.get("/requests/search?limit=abc")
    assert resp.status_code == 400


def test_filter_records_limit():
    records = [_make_record() for _ in range(10)]
    result = filter_records(records, limit=3)
    assert len(result) == 3
