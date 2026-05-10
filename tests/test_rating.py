"""Tests for hookdraft.rating and /requests/<id>/rating routes."""

from __future__ import annotations

import pytest

from hookdraft.rating import (
    clear_rating,
    filter_by_min_rating,
    filter_by_rating,
    get_rating,
    has_rating,
    set_rating,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rec() -> dict:
    return {"id": "r1", "meta": {}}


# ---------------------------------------------------------------------------
# Unit tests – rating module
# ---------------------------------------------------------------------------

def test_get_rating_none_by_default():
    r = _rec()
    assert get_rating(r) is None


def test_has_rating_false_by_default():
    assert not has_rating(_rec())


def test_set_rating_basic():
    r = _rec()
    set_rating(r, 3)
    assert get_rating(r) == 3
    assert has_rating(r)


def test_set_rating_boundary_one():
    r = _rec()
    set_rating(r, 1)
    assert get_rating(r) == 1


def test_set_rating_boundary_five():
    r = _rec()
    set_rating(r, 5)
    assert get_rating(r) == 5


def test_set_rating_zero_raises():
    with pytest.raises(ValueError):
        set_rating(_rec(), 0)


def test_set_rating_six_raises():
    with pytest.raises(ValueError):
        set_rating(_rec(), 6)


def test_set_rating_non_int_raises():
    with pytest.raises(TypeError):
        set_rating(_rec(), "3")  # type: ignore[arg-type]


def test_clear_rating_removes_value():
    r = _rec()
    set_rating(r, 4)
    clear_rating(r)
    assert get_rating(r) is None
    assert not has_rating(r)


def test_clear_rating_idempotent():
    r = _rec()
    clear_rating(r)  # should not raise
    assert get_rating(r) is None


def test_filter_by_rating():
    records = [{"rating": 1}, {"rating": 3}, {"rating": 3}, {"rating": 5}]
    result = filter_by_rating(records, 3)
    assert len(result) == 2
    assert all(r["rating"] == 3 for r in result)


def test_filter_by_rating_no_match():
    records = [{"rating": 2}, {"rating": 4}]
    assert filter_by_rating(records, 5) == []


def test_filter_by_min_rating():
    records = [{"rating": 1}, {"rating": 3}, {"rating": 5}, {}]
    result = filter_by_min_rating(records, 3)
    assert len(result) == 2
    assert all(r.get("rating", 0) >= 3 for r in result)


def test_filter_by_min_rating_invalid_raises():
    with pytest.raises(ValueError):
        filter_by_min_rating([], 0)


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

@pytest.fixture()
 def client():
    from hookdraft.app import create_app
    from hookdraft.storage import RequestStore
    from hookdraft.routes.rating_routes import register_rating_routes

    store = RequestStore()
    app = create_app(store=store)
    register_rating_routes(app)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post(
        "/hooks/test",
        json={"event": "ping"},
        headers={"Content-Type": "application/json"},
    )
    return resp.get_json()["id"]


def test_get_rating_unknown_id(client):
    resp = client.get("/requests/nope/rating")
    assert resp.status_code == 404


def test_set_and_get_rating(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/rating", json={"stars": 4})
    assert resp.status_code == 200
    assert resp.get_json()["rating"] == 4

    resp2 = client.get(f"/requests/{rid}/rating")
    assert resp2.status_code == 200
    assert resp2.get_json()["rating"] == 4


def test_set_rating_invalid_value(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/rating", json={"stars": 9})
    assert resp.status_code == 400


def test_set_rating_missing_field(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/rating", json={})
    assert resp.status_code == 400


def test_delete_rating(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/rating", json={"stars": 2})
    resp = client.delete(f"/requests/{rid}/rating")
    assert resp.status_code == 200
    assert resp.get_json()["rating"] is None
