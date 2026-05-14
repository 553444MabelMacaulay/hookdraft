"""Unit tests for hookdraft.suppression."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.suppression import (
    filter_suppressed,
    filter_unsuppressed,
    get_suppression_reason,
    is_suppressed,
    suppress_record,
    unsuppress_record,
)


def _rec(record_id: str = "r1") -> RequestRecord:
    return RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00Z",
    )


def test_is_suppressed_false_by_default():
    assert is_suppressed(_rec()) is False


def test_get_suppression_reason_none_by_default():
    assert get_suppression_reason(_rec()) is None


def test_suppress_record_sets_flag():
    r = _rec()
    suppress_record(r)
    assert is_suppressed(r) is True


def test_suppress_record_stores_reason():
    r = _rec()
    suppress_record(r, reason="noisy endpoint")
    assert get_suppression_reason(r) == "noisy endpoint"


def test_suppress_record_strips_reason_whitespace():
    r = _rec()
    suppress_record(r, reason="  spammy  ")
    assert get_suppression_reason(r) == "spammy"


def test_suppress_record_empty_reason_stores_none():
    r = _rec()
    suppress_record(r, reason="   ")
    assert get_suppression_reason(r) is None


def test_unsuppress_record_removes_flag():
    r = _rec()
    suppress_record(r, reason="test")
    unsuppress_record(r)
    assert is_suppressed(r) is False
    assert get_suppression_reason(r) is None


def test_unsuppress_idempotent_when_not_suppressed():
    r = _rec()
    unsuppress_record(r)  # should not raise
    assert is_suppressed(r) is False


def test_filter_suppressed_returns_only_suppressed():
    r1, r2, r3 = _rec("a"), _rec("b"), _rec("c")
    suppress_record(r1)
    suppress_record(r3)
    result = filter_suppressed([r1, r2, r3])
    assert [r.id for r in result] == ["a", "c"]


def test_filter_unsuppressed_excludes_suppressed():
    r1, r2, r3 = _rec("a"), _rec("b"), _rec("c")
    suppress_record(r2)
    result = filter_unsuppressed([r1, r2, r3])
    assert [r.id for r in result] == ["a", "c"]


def test_filter_suppressed_empty_list():
    assert filter_suppressed([]) == []


def test_filter_unsuppressed_empty_list():
    assert filter_unsuppressed([]) == []
