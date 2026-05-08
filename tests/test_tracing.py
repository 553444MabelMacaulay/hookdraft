"""Tests for hookdraft.tracing and the /requests/<id>/trace routes."""

from __future__ import annotations

import pytest

from hookdraft.storage import RequestRecord, RequestStore
from hookdraft import tracing
from hookdraft.app import create_app


def _rec(req_id="abc"):
    return RequestRecord(
        id=req_id,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
    )


# --- unit tests for tracing module ---

def test_has_trace_false_by_default():
    assert tracing.has_trace(_rec()) is False


def test_set_trace_basic():
    r = _rec()
    tracing.set_trace(r, "trace-1")
    assert tracing.get_trace(r) == {"trace_id": "trace-1"}


def test_set_trace_with_spans():
    r = _rec()
    tracing.set_trace(r, "t1", span_id="s1", parent_span_id="p1")
    ctx = tracing.get_trace(r)
    assert ctx["trace_id"] == "t1"
    assert ctx["span_id"] == "s1"
    assert ctx["parent_span_id"] == "p1"


def test_set_trace_strips_whitespace():
    r = _rec()
    tracing.set_trace(r, "  tid  ")
    assert tracing.get_trace(r)["trace_id"] == "tid"


def test_set_trace_empty_raises():
    with pytest.raises(ValueError):
        tracing.set_trace(_rec(), "")


def test_clear_trace_removes_all_fields():
    r = _rec()
    tracing.set_trace(r, "t1", span_id="s1")
    tracing.clear_trace(r)
    assert tracing.get_trace(r) == {}
    assert not tracing.has_trace(r)


def test_filter_by_trace_id():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    tracing.set_trace(r1, "alpha")
    tracing.set_trace(r2, "beta")
    result = tracing.filter_by_trace_id([r1, r2, r3], "alpha")
    assert result == [r1]


def test_group_by_trace_id():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    tracing.set_trace(r1, "g1")
    tracing.set_trace(r2, "g1")
    tracing.set_trace(r3, "g2")
    groups = tracing.group_by_trace_id([r1, r2, r3])
    assert set(groups.keys()) == {"g1", "g2"}
    assert len(groups["g1"]) == 2


# --- route tests ---

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
    resp = client.post("/hooks/test", json={"x": 1})
    return client.get("/requests").get_json()[0]["id"]


def test_get_trace_unknown_id(client):
    resp = client.get("/requests/nope/trace")
    assert resp.status_code == 404


def test_set_and_get_trace(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/trace", json={"trace_id": "t-99", "span_id": "s-1"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["trace_id"] == "t-99"
    assert data["span_id"] == "s-1"

    resp2 = client.get(f"/requests/{rid}/trace")
    assert resp2.status_code == 200
    assert resp2.get_json()["trace_id"] == "t-99"


def test_set_trace_missing_trace_id(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/trace", json={"span_id": "s1"})
    assert resp.status_code == 400


def test_delete_trace(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/trace", json={"trace_id": "t-del"})
    resp = client.delete(f"/requests/{rid}/trace")
    assert resp.status_code == 204
    assert client.get(f"/requests/{rid}/trace").get_json() == {}


def test_search_by_trace_id(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/trace", json={"trace_id": "search-me"})
    resp = client.get("/requests/trace/search-me")
    assert resp.status_code == 200
    results = resp.get_json()
    assert any(r["id"] == rid for r in results)
