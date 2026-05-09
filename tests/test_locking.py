"""Tests for hookdraft.locking and the lock HTTP routes."""

from __future__ import annotations

import pytest

from hookdraft.locking import (
    lock_record,
    unlock_record,
    is_locked,
    get_lock_reason,
    filter_locked,
    filter_unlocked,
)
from hookdraft.storage import RequestRecord, RequestStore
from hookdraft.app import create_app


def _rec(id_: str = "r1") -> RequestRecord:
    return RequestRecord(
        id=id_,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )


# --- unit tests ---

def test_is_locked_false_by_default():
    assert is_locked(_rec()) is False


def test_lock_record_sets_flag():
    r = _rec()
    lock_record(r)
    assert is_locked(r) is True


def test_lock_record_stores_reason():
    r = _rec()
    lock_record(r, "do not touch")
    assert get_lock_reason(r) == "do not touch"


def test_lock_record_strips_reason_whitespace():
    r = _rec()
    lock_record(r, "  sensitive  ")
    assert get_lock_reason(r) == "sensitive"


def test_lock_record_empty_reason_stores_none():
    r = _rec()
    lock_record(r, "   ")
    assert get_lock_reason(r) is None


def test_unlock_record_removes_flag():
    r = _rec()
    lock_record(r, "reason")
    unlock_record(r)
    assert is_locked(r) is False
    assert get_lock_reason(r) is None


def test_unlock_idempotent_when_not_locked():
    r = _rec()
    unlock_record(r)  # should not raise
    assert is_locked(r) is False


def test_filter_locked():
    a, b, c = _rec("a"), _rec("b"), _rec("c")
    lock_record(a)
    lock_record(c)
    assert filter_locked([a, b, c]) == [a, c]


def test_filter_unlocked():
    a, b = _rec("a"), _rec("b")
    lock_record(a)
    assert filter_unlocked([a, b]) == [b]


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
    resp = client.post("/hook", json={"x": 1})
    return resp.get_json()["id"]


def test_lock_status_unknown_id(client):
    r = client.get("/requests/nope/lock")
    assert r.status_code == 404


def test_lock_unknown_id(client):
    r = client.post("/requests/nope/lock", json={})
    assert r.status_code == 404


def test_lock_and_check_status(client):
    id_ = _post_hook(client)
    r = client.post(f"/requests/{id_}/lock", json={"reason": "freeze"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["locked"] is True
    assert data["reason"] == "freeze"

    r2 = client.get(f"/requests/{id_}/lock")
    assert r2.get_json()["locked"] is True


def test_unlock_request(client):
    id_ = _post_hook(client)
    client.post(f"/requests/{id_}/lock", json={})
    r = client.delete(f"/requests/{id_}/lock")
    assert r.status_code == 200
    assert r.get_json()["locked"] is False
