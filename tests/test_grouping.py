"""Tests for hookdraft.grouping and the /requests/group/<field> route."""

from __future__ import annotations

import pytest

from hookdraft.grouping import group_records, group_summary
from hookdraft.storage import RequestRecord


def _rec(**kwargs) -> RequestRecord:
    defaults = dict(
        id="x",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
        response_status=200,
    )
    defaults.update(kwargs)
    return RequestRecord(**defaults)


# --- unit tests ---

def test_group_by_method():
    records = [
        _rec(id="1", method="GET"),
        _rec(id="2", method="POST"),
        _rec(id="3", method="GET"),
    ]
    groups = group_records(records, "method")
    assert set(groups.keys()) == {"GET", "POST"}
    assert len(groups["GET"]) == 2
    assert len(groups["POST"]) == 1


def test_group_by_status_code():
    records = [
        _rec(id="1", response_status=200),
        _rec(id="2", response_status=404),
        _rec(id="3", response_status=200),
    ]
    groups = group_records(records, "status_code")
    assert groups["200"][0].id == "1"
    assert len(groups["404"]) == 1


def test_group_by_content_type_strips_charset():
    records = [
        _rec(id="1", headers={"content-type": "application/json; charset=utf-8"}),
        _rec(id="2", headers={"content-type": "application/json"}),
        _rec(id="3", headers={"content-type": "text/plain"}),
    ]
    groups = group_records(records, "content_type")
    assert "application/json" in groups
    assert len(groups["application/json"]) == 2


def test_group_summary_returns_counts():
    records = [
        _rec(id="1", method="DELETE"),
        _rec(id="2", method="DELETE"),
        _rec(id="3", method="PUT"),
    ]
    summary = group_summary(records, "method")
    assert summary == {"DELETE": 2, "PUT": 1}


def test_group_invalid_field_raises():
    with pytest.raises(ValueError, match="Invalid grouping field"):
        group_records([], "nonexistent")


def test_group_empty_records():
    assert group_records([], "method") == {}


# --- route tests ---

@pytest.fixture()
def client():
    from hookdraft.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client, method="POST", path="/hook"):
    return client.open(path, method=method, json={"k": "v"})


def test_route_group_by_method(client):
    _post_hook(client, method="GET", path="/hook")
    _post_hook(client, method="POST", path="/hook")
    _post_hook(client, method="GET", path="/hook")
    resp = client.get("/requests/group/method")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["field"] == "method"
    assert len(data["groups"]["GET"]) == 2


def test_route_group_summary(client):
    _post_hook(client, method="POST", path="/hook")
    _post_hook(client, method="POST", path="/hook")
    resp = client.get("/requests/group/method?summary=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data["groups"]["POST"], int)


def test_route_group_invalid_field(client):
    resp = client.get("/requests/group/foobar")
    assert resp.status_code == 400
    assert "error" in resp.get_json()
