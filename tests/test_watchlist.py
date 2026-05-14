"""Tests for hookdraft.watchlist and the watchlist HTTP routes."""

from __future__ import annotations

import pytest

from hookdraft.storage import RequestRecord, RequestStore
from hookdraft import watchlist as wl
from hookdraft.app import create_app


def _rec():
    return RequestRecord(
        id="abc",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
    )


# --- unit tests ---

def test_is_watched_false_by_default():
    assert wl.is_watched(_rec()) is False


def test_watch_record_sets_flag():
    r = _rec()
    wl.watch_record(r)
    assert wl.is_watched(r) is True


def test_watch_record_stores_reason():
    r = _rec()
    wl.watch_record(r, reason="suspicious payload")
    assert wl.get_watch_reason(r) == "suspicious payload"


def test_watch_record_strips_reason_whitespace():
    r = _rec()
    wl.watch_record(r, reason="  check this  ")
    assert wl.get_watch_reason(r) == "check this"


def test_watch_record_empty_reason_stores_none():
    r = _rec()
    wl.watch_record(r, reason="")
    assert wl.get_watch_reason(r) is None


def test_unwatch_record_removes_flag():
    r = _rec()
    wl.watch_record(r, reason="test")
    wl.unwatch_record(r)
    assert wl.is_watched(r) is False
    assert wl.get_watch_reason(r) is None


def test_unwatch_idempotent_when_not_watched():
    r = _rec()
    wl.unwatch_record(r)  # should not raise
    assert wl.is_watched(r) is False


def test_filter_watched():
    r1, r2, r3 = _rec(), _rec(), _rec()
    wl.watch_record(r1)
    wl.watch_record(r3)
    assert wl.filter_watched([r1, r2, r3]) == [r1, r3]


def test_filter_unwatched():
    r1, r2 = _rec(), _rec()
    wl.watch_record(r1)
    assert wl.filter_unwatched([r1, r2]) == [r2]


# --- route tests ---

@pytest.fixture()
 def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post("/hooks/test", json={"x": 1})
    return resp.get_json()["id"]


def test_watch_status_unknown_id(client):
    resp = client.get("/requests/nope/watch")
    assert resp.status_code == 404


def test_watch_and_check_status(client):
    rid = _post_hook(client)
    resp = client.post(f"/requests/{rid}/watch", json={"reason": "looks odd"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["watched"] is True
    assert data["reason"] == "looks odd"

    resp2 = client.get(f"/requests/{rid}/watch")
    assert resp2.get_json()["watched"] is True


def test_unwatch_request(client):
    rid = _post_hook(client)
    client.post(f"/requests/{rid}/watch", json={})
    resp = client.delete(f"/requests/{rid}/watch")
    assert resp.status_code == 200
    assert resp.get_json()["watched"] is False
