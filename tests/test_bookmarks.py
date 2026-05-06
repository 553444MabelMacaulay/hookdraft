"""Unit tests for hookdraft/bookmarks.py."""

import pytest

from hookdraft.bookmarks import (
    bookmark_record,
    filter_bookmarked,
    filter_unbookmarked,
    is_bookmarked,
    unbookmark_record,
)
from hookdraft.storage import RequestRecord


def _rec(record_id: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        timestamp="2024-01-01T00:00:00",
    )


def test_bookmark_sets_flag():
    r = _rec()
    bookmark_record(r)
    assert r.meta["bookmarked"] is True


def test_unbookmark_removes_flag():
    r = _rec()
    bookmark_record(r)
    unbookmark_record(r)
    assert "bookmarked" not in r.meta


def test_unbookmark_idempotent_when_not_bookmarked():
    r = _rec()
    unbookmark_record(r)  # should not raise
    assert "bookmarked" not in r.meta


def test_is_bookmarked_false_by_default():
    r = _rec()
    assert is_bookmarked(r) is False


def test_is_bookmarked_true_after_bookmark():
    r = _rec()
    bookmark_record(r)
    assert is_bookmarked(r) is True


def test_is_bookmarked_false_after_unbookmark():
    r = _rec()
    bookmark_record(r)
    unbookmark_record(r)
    assert is_bookmarked(r) is False


def test_filter_bookmarked_returns_only_bookmarked():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    bookmark_record(r1)
    bookmark_record(r3)
    result = filter_bookmarked([r1, r2, r3])
    assert [r.id for r in result] == ["1", "3"]


def test_filter_unbookmarked_returns_only_unbookmarked():
    r1, r2 = _rec("1"), _rec("2")
    bookmark_record(r1)
    result = filter_unbookmarked([r1, r2])
    assert [r.id for r in result] == ["2"]


def test_filter_bookmarked_empty_list():
    assert filter_bookmarked([]) == []
