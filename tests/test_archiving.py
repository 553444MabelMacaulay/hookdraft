"""Unit tests for hookdraft.archiving."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.archiving import (
    archive_record,
    unarchive_record,
    is_archived,
    filter_archived,
    filter_unarchived,
)


def _rec(rid: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=rid,
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        timestamp="2024-01-01T00:00:00",
    )


def test_is_archived_false_by_default():
    r = _rec()
    assert is_archived(r) is False


def test_archive_record_sets_flag():
    r = _rec()
    archive_record(r)
    assert r.meta["archived"] is True


def test_is_archived_true_after_archive():
    r = _rec()
    archive_record(r)
    assert is_archived(r) is True


def test_unarchive_record_removes_flag():
    r = _rec()
    archive_record(r)
    unarchive_record(r)
    assert is_archived(r) is False
    assert "archived" not in r.meta


def test_unarchive_idempotent_when_not_archived():
    r = _rec()
    unarchive_record(r)  # should not raise
    assert is_archived(r) is False


def test_filter_archived_returns_only_archived():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    archive_record(r1)
    archive_record(r3)
    result = filter_archived([r1, r2, r3])
    assert [r.id for r in result] == ["1", "3"]


def test_filter_unarchived_excludes_archived():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    archive_record(r2)
    result = filter_unarchived([r1, r2, r3])
    assert [r.id for r in result] == ["1", "3"]


def test_filter_archived_empty_list():
    assert filter_archived([]) == []


def test_filter_unarchived_empty_list():
    assert filter_unarchived([]) == []
