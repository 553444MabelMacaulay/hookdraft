"""Unit tests for hookdraft.pinning."""

from __future__ import annotations

import pytest

from hookdraft.pinning import (
    add_tag,
    filter_pinned,
    filter_unpinned,
    is_pinned,
    pin_record,
    unpin_record,
)
from hookdraft.storage import RequestRecord


def _rec(rid: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=rid,
        timestamp="2024-01-01T00:00:00",
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        query_string="",
    )


def test_pin_record_sets_flag():
    r = _rec()
    pin_record(r)
    assert r.meta["pinned"] is True


def test_unpin_record_removes_flag():
    r = _rec()
    pin_record(r)
    unpin_record(r)
    assert "pinned" not in r.meta


def test_unpin_idempotent_when_not_pinned():
    r = _rec()
    unpin_record(r)  # should not raise
    assert not is_pinned(r)


def test_is_pinned_false_by_default():
    r = _rec()
    assert is_pinned(r) is False


def test_is_pinned_true_after_pin():
    r = _rec()
    pin_record(r)
    assert is_pinned(r) is True


def test_filter_pinned_returns_only_pinned():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    pin_record(r1)
    pin_record(r3)
    result = filter_pinned([r1, r2, r3])
    assert [x.id for x in result] == ["1", "3"]


def test_filter_unpinned_returns_only_unpinned():
    r1, r2 = _rec("1"), _rec("2")
    pin_record(r1)
    result = filter_unpinned([r1, r2])
    assert [x.id for x in result] == ["2"]


def test_filter_pinned_empty_list():
    assert filter_pinned([]) == []


def test_pin_record_returns_record():
    r = _rec()
    returned = pin_record(r)
    assert returned is r
