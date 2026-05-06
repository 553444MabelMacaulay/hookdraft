import json
import pytest
from flask import Flask

from hookdraft.storage import RequestRecord, RequestStore
from hookdraft.stats import compute_stats
from hookdraft.routes.stats_routes import register_stats_routes


def _make_record(method="POST", path="/hook", body=b"{}", headers=None, status=200):
    return RequestRecord(
        method=method,
        path=path,
        headers=headers or {"Content-Type": "application/json"},
        body=body,
        response_status=status,
    )


# --- Unit tests for compute_stats ---

def test_empty_records():
    result = compute_stats([])
    assert result["total"] == 0
    assert result["methods"] == {}
    assert result["paths"] == {}


def test_single_record():
    record = _make_record()
    result = compute_stats([record])
    assert result["total"] == 1
    assert result["methods"] == {"POST": 1}
    assert result["paths"] == {"/hook": 1}
    assert result["status_codes"] == {"200": 1}
    assert result["content_types"] == {"application/json": 1}


def test_multiple_methods():
    records = [
        _make_record(method="POST"),
        _make_record(method="GET"),
        _make_record(method="POST"),
    ]
    result = compute_stats(records)
    assert result["total"] == 3
    assert result["methods"]["POST"] == 2
    assert result["methods"]["GET"] == 1


def test_content_type_strips_charset():
    record = _make_record(headers={"Content-Type": "application/json; charset=utf-8"})
    result = compute_stats([record])
    assert "application/json" in result["content_types"]


def test_missing_content_type_uses_unknown():
    record = _make_record(headers={})
    result = compute_stats([record])
    assert "unknown" in result["content_types"]


# --- Integration tests for /stats route ---

@pytest.fixture()
def client():
    store = RequestStore()
    app = Flask(__name__)
    app.config["TESTING"] = True
    register_stats_routes(app, store_fn=lambda: store)

    # Pre-populate store
    store.save(_make_record(method="POST", path="/hook"))
    store.save(_make_record(method="GET", path="/ping"))
    store.save(_make_record(method="POST", path="/hook", status=422))

    with app.test_client() as c:
        yield c


def test_stats_route_returns_200(client):
    resp = client.get("/stats")
    assert resp.status_code == 200


def test_stats_route_total(client):
    data = json.loads(client.get("/stats").data)
    assert data["total"] == 3


def test_stats_route_methods(client):
    data = json.loads(client.get("/stats").data)
    assert data["methods"]["POST"] == 2
    assert data["methods"]["GET"] == 1


def test_stats_route_status_codes(client):
    data = json.loads(client.get("/stats").data)
    assert data["status_codes"]["200"] == 2
    assert data["status_codes"]["422"] == 1
