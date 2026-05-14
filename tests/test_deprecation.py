"""Tests for hookdraft.deprecation."""

import pytest
from hookdraft.deprecation import (
    deprecate_record,
    undeprecate_record,
    is_deprecated,
    get_deprecation,
    filter_deprecated,
    filter_undeprecated,
)


def _rec(extra=None):
    r = {"id": "abc", "method": "POST", "path": "/hook"}
    if extra:
        r.update(extra)
    return r


def test_is_deprecated_false_by_default():
    assert is_deprecated(_rec()) is False


def test_get_deprecation_none_by_default():
    assert get_deprecation(_rec()) is None


def test_deprecate_record_sets_flag():
    r = _rec()
    deprecate_record(r)
    assert is_deprecated(r) is True


def test_deprecate_record_default_reason():
    r = _rec()
    deprecate_record(r)
    assert get_deprecation(r)["reason"] == "other"


def test_deprecate_record_custom_reason():
    r = _rec()
    deprecate_record(r, reason="sunset")
    assert get_deprecation(r)["reason"] == "sunset"


def test_deprecate_record_normalises_reason_case():
    r = _rec()
    deprecate_record(r, reason="REPLACED")
    assert get_deprecation(r)["reason"] == "replaced"


def test_deprecate_record_invalid_reason_raises():
    with pytest.raises(ValueError, match="Invalid reason"):
        deprecate_record(_rec(), reason="unknown")


def test_deprecate_record_empty_reason_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        deprecate_record(_rec(), reason="   ")


def test_deprecate_record_stores_note():
    r = _rec()
    deprecate_record(r, note="Use /v2/hook instead.")
    assert get_deprecation(r)["note"] == "Use /v2/hook instead."


def test_deprecate_record_strips_note_whitespace():
    r = _rec()
    deprecate_record(r, note="  trimmed  ")
    assert get_deprecation(r)["note"] == "trimmed"


def test_deprecate_record_empty_note_stored_as_none():
    r = _rec()
    deprecate_record(r, note="   ")
    assert get_deprecation(r)["note"] is None


def test_undeprecate_record_removes_flag():
    r = _rec()
    deprecate_record(r)
    undeprecate_record(r)
    assert is_deprecated(r) is False


def test_undeprecate_idempotent_when_not_deprecated():
    r = _rec()
    undeprecate_record(r)  # should not raise
    assert is_deprecated(r) is False


def test_filter_deprecated():
    r1 = _rec()
    r2 = _rec()
    deprecate_record(r1)
    result = filter_deprecated([r1, r2])
    assert result == [r1]


def test_filter_undeprecated():
    r1 = _rec()
    r2 = _rec()
    deprecate_record(r1)
    result = filter_undeprecated([r1, r2])
    assert result == [r2]
