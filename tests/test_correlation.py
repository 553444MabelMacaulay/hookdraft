"""Tests for hookdraft.correlation."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.correlation import (
    set_correlation_id,
    clear_correlation_id,
    get_correlation_id,
    filter_by_correlation_id,
    group_by_correlation_id,
)


def _rec(record_id: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        timestamp="2024-01-01T00:00:00",
    )


def test_get_correlation_id_none_by_default():
    assert get_correlation_id(_rec()) is None


def test_set_correlation_id_basic():
    r = _rec()
    set_correlation_id(r, "trace-001")
    assert get_correlation_id(r) == "trace-001"


def test_set_correlation_id_strips_whitespace():
    r = _rec()
    set_correlation_id(r, "  trace-002  ")
    assert get_correlation_id(r) == "trace-002"


def test_set_correlation_id_empty_raises():
    r = _rec()
    with pytest.raises(ValueError):
        set_correlation_id(r, "")


def test_set_correlation_id_whitespace_only_raises():
    r = _rec()
    with pytest.raises(ValueError):
        set_correlation_id(r, "   ")


def test_clear_correlation_id_removes_value():
    r = _rec()
    set_correlation_id(r, "trace-003")
    clear_correlation_id(r)
    assert get_correlation_id(r) is None


def test_clear_correlation_id_idempotent():
    r = _rec()
    clear_correlation_id(r)  # should not raise
    assert get_correlation_id(r) is None


def test_filter_by_correlation_id_returns_matching():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_correlation_id(r1, "group-A")
    set_correlation_id(r2, "group-B")
    set_correlation_id(r3, "group-A")
    result = filter_by_correlation_id([r1, r2, r3], "group-A")
    assert result == [r1, r3]


def test_filter_by_correlation_id_no_match():
    r1 = _rec("1")
    set_correlation_id(r1, "group-X")
    result = filter_by_correlation_id([r1], "group-Y")
    assert result == []


def test_group_by_correlation_id_groups_correctly():
    r1, r2, r3, r4 = _rec("1"), _rec("2"), _rec("3"), _rec("4")
    set_correlation_id(r1, "A")
    set_correlation_id(r2, "B")
    set_correlation_id(r3, "A")
    # r4 has no correlation id
    groups = group_by_correlation_id([r1, r2, r3, r4])
    assert set(groups.keys()) == {"A", "B"}
    assert groups["A"] == [r1, r3]
    assert groups["B"] == [r2]


def test_group_by_correlation_id_excludes_unset():
    r1, r2 = _rec("1"), _rec("2")
    set_correlation_id(r1, "only-one")
    groups = group_by_correlation_id([r1, r2])
    assert "only-one" in groups
    assert len(groups) == 1
