"""Unit tests for hookdraft.notes module."""

import pytest
from hookdraft.notes import set_note, clear_note, get_note, filter_by_note


def _rec(note=None):
    r = {"id": "abc", "method": "POST"}
    if note is not None:
        r["note"] = note
    return r


def test_set_note_basic():
    r = _rec()
    set_note(r, "hello world")
    assert r["note"] == "hello world"


def test_set_note_strips_whitespace():
    r = _rec()
    set_note(r, "  trimmed  ")
    assert r["note"] == "trimmed"


def test_set_note_empty_raises():
    with pytest.raises(ValueError):
        set_note(_rec(), "")


def test_set_note_whitespace_only_raises():
    with pytest.raises(ValueError):
        set_note(_rec(), "   ")


def test_set_note_non_string_raises():
    with pytest.raises(TypeError):
        set_note(_rec(), 123)


def test_clear_note_removes_key():
    r = _rec(note="to remove")
    clear_note(r)
    assert "note" not in r


def test_clear_note_idempotent():
    r = _rec()
    clear_note(r)  # no key present — should not raise
    assert "note" not in r


def test_get_note_present():
    r = _rec(note="my note")
    assert get_note(r) == "my note"


def test_get_note_absent():
    assert get_note(_rec()) is None


def test_filter_by_note_match():
    records = [
        _rec(note="important webhook"),
        _rec(note="routine ping"),
        _rec(note="IMPORTANT retry"),
    ]
    result = filter_by_note(records, "important")
    assert len(result) == 2


def test_filter_by_note_no_match():
    records = [_rec(note="nothing here"), _rec()]
    result = filter_by_note(records, "xyz")
    assert result == []


def test_filter_by_note_skips_records_without_note():
    records = [_rec(), _rec(note="has a note")]
    result = filter_by_note(records, "has")
    assert len(result) == 1


def test_filter_by_note_empty_substring_raises():
    with pytest.raises(ValueError):
        filter_by_note([], "")
