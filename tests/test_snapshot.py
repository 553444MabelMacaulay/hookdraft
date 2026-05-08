"""Unit tests for hookdraft.snapshot."""

import pytest

from hookdraft.snapshot import (
    save_snapshot,
    delete_snapshot,
    get_snapshot,
    list_snapshots,
    has_snapshot,
)
from hookdraft.storage import RequestRecord


def _rec(body=None):
    r = RequestRecord(
        id="abc",
        method="POST",
        path="/hook",
        headers={},
        body=body or {"key": "value"},
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )
    return r


def test_list_snapshots_empty():
    assert list_snapshots(_rec()) == []


def test_save_snapshot_stores_body():
    r = _rec({"a": 1})
    save_snapshot(r, "v1")
    assert get_snapshot(r, "v1") == {"a": 1}


def test_save_snapshot_overwrites_existing():
    r = _rec({"a": 1})
    save_snapshot(r, "v1")
    r.body = {"a": 2}
    save_snapshot(r, "v1")
    assert get_snapshot(r, "v1") == {"a": 2}


def test_save_snapshot_empty_name_raises():
    r = _rec()
    with pytest.raises(ValueError, match="empty"):
        save_snapshot(r, "   ")


def test_list_snapshots_sorted():
    r = _rec()
    save_snapshot(r, "beta")
    save_snapshot(r, "alpha")
    assert list_snapshots(r) == ["alpha", "beta"]


def test_has_snapshot_false_by_default():
    assert not has_snapshot(_rec(), "v1")


def test_has_snapshot_true_after_save():
    r = _rec()
    save_snapshot(r, "v1")
    assert has_snapshot(r, "v1")


def test_get_snapshot_none_when_missing():
    assert get_snapshot(_rec(), "missing") is None


def test_delete_snapshot_returns_true_when_exists():
    r = _rec()
    save_snapshot(r, "v1")
    assert delete_snapshot(r, "v1") is True
    assert not has_snapshot(r, "v1")


def test_delete_snapshot_returns_false_when_missing():
    assert delete_snapshot(_rec(), "nope") is False


def test_multiple_snapshots_independent():
    r = _rec({"x": 0})
    save_snapshot(r, "s1")
    r.body = {"x": 99}
    save_snapshot(r, "s2")
    assert get_snapshot(r, "s1") == {"x": 0}
    assert get_snapshot(r, "s2") == {"x": 99}
