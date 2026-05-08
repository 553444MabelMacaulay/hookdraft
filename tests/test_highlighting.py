"""Tests for hookdraft.highlighting."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.highlighting import (
    set_highlight,
    clear_highlight,
    get_highlight,
    is_highlighted,
    filter_highlighted,
    filter_by_highlight_colour,
)


def _rec(record_id: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
    )


def test_is_highlighted_false_by_default():
    assert is_highlighted(_rec()) is False


def test_get_highlight_none_by_default():
    assert get_highlight(_rec()) is None


def test_set_highlight_default_colour():
    r = _rec()
    set_highlight(r)
    assert get_highlight(r) == "yellow"


def test_set_highlight_custom_colour():
    r = _rec()
    set_highlight(r, "blue")
    assert get_highlight(r) == "blue"


def test_set_highlight_normalises_case():
    r = _rec()
    set_highlight(r, "GREEN")
    assert get_highlight(r) == "green"


def test_set_highlight_strips_whitespace():
    r = _rec()
    set_highlight(r, "  red  ")
    assert get_highlight(r) == "red"


def test_set_highlight_unknown_colour_raises():
    with pytest.raises(ValueError, match="Unknown highlight colour"):
        set_highlight(_rec(), "pink")


def test_set_highlight_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_highlight(_rec(), "   ")


def test_is_highlighted_true_after_set():
    r = _rec()
    set_highlight(r, "orange")
    assert is_highlighted(r) is True


def test_clear_highlight_removes_flag():
    r = _rec()
    set_highlight(r, "purple")
    clear_highlight(r)
    assert is_highlighted(r) is False
    assert get_highlight(r) is None


def test_clear_highlight_idempotent():
    r = _rec()
    clear_highlight(r)  # should not raise
    assert is_highlighted(r) is False


def test_filter_highlighted_returns_only_highlighted():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_highlight(r1, "yellow")
    set_highlight(r3, "red")
    result = filter_highlighted([r1, r2, r3])
    assert result == [r1, r3]


def test_filter_highlighted_empty_list():
    assert filter_highlighted([]) == []


def test_filter_by_highlight_colour():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    set_highlight(r1, "blue")
    set_highlight(r2, "red")
    set_highlight(r3, "blue")
    result = filter_by_highlight_colour([r1, r2, r3], "blue")
    assert result == [r1, r3]


def test_filter_by_highlight_colour_case_insensitive():
    r = _rec()
    set_highlight(r, "green")
    assert filter_by_highlight_colour([r], "GREEN") == [r]
