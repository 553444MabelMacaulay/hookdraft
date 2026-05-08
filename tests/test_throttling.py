"""Tests for hookdraft.throttling and /requests/<id>/throttle routes."""

from __future__ import annotations

import pytest

from hookdraft.throttling import (
    clear_throttle,
    filter_by_action,
    filter_throttled,
    filter_unthrottled,
    get_throttle,
    is_throttled,
    set_throttle,
)


def _rec() -> dict:
    return {"id": "abc", "body": {}}


# ---------------------------------------------------------------------------
# Unit tests – throttling.py
# ---------------------------------------------------------------------------

def test_is_throttled_false_by_default():
    assert is_throttled(_rec()) is False


def test_set_throttle_basic():
    r = _rec()
    set_throttle(r, rpm=60)
    assert is_throttled(r) is True
    assert get_throttle(r)["rpm"] == 60
    assert get_throttle(r)["action"] == "drop"
    assert get_throttle(r)["burst"] is None


def test_set_throttle_custom_action():
    r = _rec()
    set_throttle(r, rpm=100, action="reject")
    assert get_throttle(r)["action"] == "reject"


def test_set_throttle_normalises_action_case():
    r = _rec()
    set_throttle(r, rpm=10, action="QUEUE")
    assert get_throttle(r)["action"] == "queue"


def test_set_throttle_with_burst():
    r = _rec()
    set_throttle(r, rpm=50, burst=80)
    assert get_throttle(r)["burst"] == 80


def test_set_throttle_zero_rpm_raises():
    with pytest.raises(ValueError, match="positive integer"):
        set_throttle(_rec(), rpm=0)


def test_set_throttle_negative_rpm_raises():
    with pytest.raises(ValueError):
        set_throttle(_rec(), rpm=-1)


def test_set_throttle_exceeds_max_raises():
    with pytest.raises(ValueError, match="100000"):
        set_throttle(_rec(), rpm=100_001)


def test_set_throttle_invalid_action_raises():
    with pytest.raises(ValueError, match="action"):
        set_throttle(_rec(), rpm=10, action="ignore")


def test_set_throttle_burst_less_than_rpm_raises():
    with pytest.raises(ValueError, match="burst"):
        set_throttle(_rec(), rpm=100, burst=50)


def test_clear_throttle_removes_policy():
    r = _rec()
    set_throttle(r, rpm=30)
    clear_throttle(r)
    assert is_throttled(r) is False
    assert get_throttle(r) is None


def test_clear_throttle_idempotent():
    r = _rec()
    clear_throttle(r)  # should not raise
    assert is_throttled(r) is False


def test_filter_throttled():
    a, b, c = _rec(), _rec(), _rec()
    set_throttle(a, rpm=10)
    set_throttle(c, rpm=20)
    result = filter_throttled([a, b, c])
    assert result == [a, c]


def test_filter_unthrottled():
    a, b = _rec(), _rec()
    set_throttle(a, rpm=10)
    assert filter_unthrottled([a, b]) == [b]


def test_filter_by_action():
    a, b, c = _rec(), _rec(), _rec()
    set_throttle(a, rpm=10, action="drop")
    set_throttle(b, rpm=20, action="reject")
    set_throttle(c, rpm=30, action="drop")
    result = filter_by_action([a, b, c], "drop")
    assert result == [a, c]


# ---------------------------------------------------------------------------
# Integration tests – throttle_routes.py
# ---------------------------------------------------------------------------

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
    resp = client.post("/hooks/test", json={"x": 1})
    return resp.get_json()["id"]


def test_get_throttle_unknown_id(client):
    resp = client.get("/requests/nope/throttle")
    assert resp.status_code == 404


def test_set_and_get_throttle(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/throttle", json={"rpm": 60})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["throttled"] is True
    assert data["rpm"] == 60
    assert data["action"] == "drop"

    resp2 = client.get(f"/requests/{rid}/throttle")
    assert resp2.status_code == 200
    assert resp2.get_json()["rpm"] == 60


def test_set_throttle_missing_rpm(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/throttle", json={"action": "queue"})
    assert resp.status_code == 400


def test_delete_throttle(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/throttle", json={"rpm": 30})
    resp = client.delete(f"/requests/{rid}/throttle")
    assert resp.status_code == 200
    assert resp.get_json()["throttled"] is False

    resp2 = client.get(f"/requests/{rid}/throttle")
    assert resp2.get_json()["throttled"] is False
