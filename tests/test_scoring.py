"""Tests for hookdraft.scoring."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.scoring import (
    set_score,
    clear_score,
    get_score,
    filter_by_min_score,
    filter_by_max_score,
    sort_by_score,
)


def _rec(record_id: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )


def test_get_score_none_by_default():
    assert get_score(_rec()) is None


def test_set_score_basic():
    r = _rec()
    set_score(r, 42)
    assert get_score(r) == 42


def test_set_score_boundary_zero():
    r = _rec()
    set_score(r, 0)
    assert get_score(r) == 0


def test_set_score_boundary_hundred():
    r = _rec()
    set_score(r, 100)
    assert get_score(r) == 100


def test_set_score_below_min_raises():
    with pytest.raises(ValueError, match="between"):
        set_score(_rec(), -1)


def test_set_score_above_max_raises():
    with pytest.raises(ValueError, match="between"):
        set_score(_rec(), 101)


def test_set_score_non_integer_raises():
    with pytest.raises(TypeError):
        set_score(_rec(), 7.5)  # type: ignore[arg-type]


def test_set_score_overwrites_existing():
    """Setting a score on a record that already has one replaces the old value."""
    r = _rec()
    set_score(r, 20)
    set_score(r, 80)
    assert get_score(r) == 80


def test_clear_score_removes_value():
    r = _rec()
    set_score(r, 55)
    clear_score(r)
    assert get_score(r) is None


def test_clear_score_idempotent():
    r = _rec()
    clear_score(r)  # no error when score not set
    assert get_score(r) is None


def test_filter_by_min_score():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_score(r1, 10)
    set_score(r2, 50)
    set_score(r3, 90)
    result = filter_by_min_score([r1, r2, r3], 50)
    assert r1 not in result
    assert r2 in result
    assert r3 in result


def test_filter_by_min_score_excludes_unscored():
    r1, r2 = _rec("1"), _rec("2")
    set_score(r1, 80)
    result = filter_by_min_score([r1, r2], 0)
    assert r2 not in result


def test_filter_by_max_score():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_score(r1, 10)
    set_score(r2, 50)
    set_score(r3, 90)
    result = filter_by_max_score([r1, r2, r3], 50)
    assert r1 in result
    assert r2 in result
    assert r3 not in result


def test_filter_by_max_score_excludes_unscored():
    """Unscored records should be excluded from filter_by_max_score results."""
    r1, r2 = _rec("1"), _rec("2")
    set_score(r1, 30)
    result = filter_by_max_score([r1, r2], 100)
    assert r2 not in result


def test_sort_by_score_descending():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_score(r1, 30)
    set_score(r2, 70)
    set_score(r3, 10)
    result = sort_by_score([r1, r2, r3])
    assert [get_score(r) for r in result] == [70, 30, 10]


def test_sort_by_score_ascending():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_score(r1, 30)
    set_score(r2, 70)
    set_score(r3, 10)
    result = sort_by_score([r1, r2, r3], descending=False)
    assert [get_score(r) for r in result] == [10, 30, 70]


def test_sort_by_score_unscored_last():
    r1, r2 = _rec("1"), _rec("2")
    set_score(r1, 50)
    result = sort_by_score([r2, r1])
    assert result[0] is r1
    assert result[1] is r2
