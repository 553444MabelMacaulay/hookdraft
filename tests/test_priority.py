"""Unit tests for hookdraft.priority."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.priority import (
    set_priority,
    clear_priority,
    get_priority,
    filter_by_priority,
    filter_by_min_priority,
    sort_by_priority,
)


def _rec(rid="r1"):
    return RequestRecord(
        id=rid,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
    )


def test_get_priority_none_by_default():
    assert get_priority(_rec()) is None


def test_set_priority_info():
    r = _rec()
    set_priority(r, "low")
    assert get_priority(r) == "low"


def test_set_priority_normalises_case():
    r = _rec()
    set_priority(r, "HIGH")
    assert get_priority(r) == "high"


def test_set_priority_strips_whitespace():
    r = _rec()
    set_priority(r, "  critical  ")
    assert get_priority(r) == "critical"


def test_set_priority_invalid_raises():
    r = _rec()
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(r, "urgent")


def test_clear_priority_removes_value():
    r = _rec()
    set_priority(r, "high")
    clear_priority(r)
    assert get_priority(r) is None


def test_clear_priority_idempotent():
    r = _rec()
    clear_priority(r)  # should not raise
    assert get_priority(r) is None


def test_filter_by_priority_exact():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_priority(r1, "low")
    set_priority(r2, "high")
    result = filter_by_priority([r1, r2, r3], "high")
    assert result == [r2]


def test_filter_by_min_priority():
    r1, r2, r3, r4 = _rec("1"), _rec("2"), _rec("3"), _rec("4")
    set_priority(r1, "low")
    set_priority(r2, "normal")
    set_priority(r3, "high")
    set_priority(r4, "critical")
    result = filter_by_min_priority([r1, r2, r3, r4], "high")
    assert result == [r3, r4]


def test_filter_by_min_priority_excludes_unset():
    r1, r2 = _rec("1"), _rec("2")
    set_priority(r1, "critical")
    result = filter_by_min_priority([r1, r2], "low")
    assert result == [r1]


def test_sort_by_priority_descending():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_priority(r1, "low")
    set_priority(r2, "critical")
    set_priority(r3, "normal")
    result = sort_by_priority([r1, r2, r3])
    assert [get_priority(r) for r in result] == ["critical", "normal", "low"]


def test_sort_by_priority_ascending():
    r1, r2 = _rec("1"), _rec("2")
    set_priority(r1, "high")
    set_priority(r2, "low")
    result = sort_by_priority([r1, r2], descending=False)
    assert [get_priority(r) for r in result] == ["low", "high"]
