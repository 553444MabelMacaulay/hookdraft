"""Unit tests for hookdraft.narration."""

import pytest

from hookdraft.narration import (
    clear_narration,
    filter_narrated,
    get_narration,
    get_narration_text,
    has_narration,
    set_narration,
)
from hookdraft.storage import RequestRecord


def _rec() -> RequestRecord:
    return RequestRecord(
        id="abc",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
    )


def test_has_narration_false_by_default():
    assert has_narration(_rec()) is False


def test_get_narration_none_by_default():
    assert get_narration(_rec()) is None


def test_get_narration_text_none_by_default():
    assert get_narration_text(_rec()) is None


def test_set_narration_basic():
    r = _rec()
    set_narration(r, "This is a test webhook.")
    assert has_narration(r) is True
    assert get_narration_text(r) == "This is a test webhook."


def test_set_narration_strips_whitespace():
    r = _rec()
    set_narration(r, "  hello  ")
    assert get_narration_text(r) == "hello"


def test_set_narration_with_author():
    r = _rec()
    set_narration(r, "Reviewed.", author="Alice")
    entry = get_narration(r)
    assert entry["author"] == "alice"
    assert entry["text"] == "Reviewed."


def test_set_narration_author_lowercased():
    r = _rec()
    set_narration(r, "ok", author="BOB")
    assert get_narration(r)["author"] == "bob"


def test_set_narration_empty_text_raises():
    with pytest.raises(ValueError, match="empty"):
        set_narration(_rec(), "   ")


def test_set_narration_empty_author_raises():
    with pytest.raises(ValueError, match="Author"):
        set_narration(_rec(), "valid text", author="   ")


def test_set_narration_exceeds_max_length_raises():
    with pytest.raises(ValueError, match="2000"):
        set_narration(_rec(), "x" * 2001)


def test_set_narration_exact_max_length_ok():
    r = _rec()
    set_narration(r, "x" * 2000)
    assert len(get_narration_text(r)) == 2000


def test_clear_narration_removes_entry():
    r = _rec()
    set_narration(r, "something")
    clear_narration(r)
    assert has_narration(r) is False


def test_clear_narration_idempotent():
    r = _rec()
    clear_narration(r)  # should not raise
    assert has_narration(r) is False


def test_filter_narrated():
    r1, r2, r3 = _rec(), _rec(), _rec()
    r1.id, r2.id, r3.id = "1", "2", "3"
    set_narration(r1, "yes")
    set_narration(r3, "also yes")
    result = filter_narrated([r1, r2, r3])
    assert result == [r1, r3]
