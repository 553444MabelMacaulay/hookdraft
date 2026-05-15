"""Tests for hookdraft.disposition."""

import pytest

from hookdraft.disposition import (
    clear_disposition,
    filter_by_disposition,
    get_disposition,
    get_disposition_value,
    has_disposition,
    set_disposition,
)


def _rec() -> dict:
    return {"id": "abc123", "body": {}}


def test_has_disposition_false_by_default():
    assert has_disposition(_rec()) is False


def test_get_disposition_none_by_default():
    assert get_disposition(_rec()) is None


def test_get_disposition_value_none_by_default():
    assert get_disposition_value(_rec()) is None


def test_set_disposition_accept():
    r = _rec()
    set_disposition(r, "accept")
    assert get_disposition_value(r) == "accept"
    assert has_disposition(r) is True


def test_set_disposition_normalises_case():
    r = _rec()
    set_disposition(r, "REJECT")
    assert get_disposition_value(r) == "reject"


def test_set_disposition_strips_whitespace():
    r = _rec()
    set_disposition(r, "  forward  ")
    assert get_disposition_value(r) == "forward"


def test_set_disposition_with_reason():
    r = _rec()
    set_disposition(r, "ignore", reason="Duplicate event")
    d = get_disposition(r)
    assert d["value"] == "ignore"
    assert d["reason"] == "Duplicate event"


def test_set_disposition_reason_stripped():
    r = _rec()
    set_disposition(r, "accept", reason="  looks good  ")
    assert get_disposition(r)["reason"] == "looks good"


def test_set_disposition_empty_reason_becomes_none():
    r = _rec()
    set_disposition(r, "accept", reason="   ")
    assert get_disposition(r)["reason"] is None


def test_set_disposition_no_reason_is_none():
    r = _rec()
    set_disposition(r, "accept")
    assert get_disposition(r)["reason"] is None


def test_set_disposition_invalid_raises():
    with pytest.raises(ValueError, match="Invalid disposition"):
        set_disposition(_rec(), "maybe")


def test_set_disposition_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_disposition(_rec(), "")


def test_clear_disposition_removes_entry():
    r = _rec()
    set_disposition(r, "forward")
    clear_disposition(r)
    assert has_disposition(r) is False


def test_clear_disposition_idempotent():
    r = _rec()
    clear_disposition(r)  # no-op
    assert has_disposition(r) is False


def test_filter_by_disposition_returns_matching():
    r1 = _rec()
    r2 = _rec()
    r3 = _rec()
    set_disposition(r1, "accept")
    set_disposition(r2, "reject")
    set_disposition(r3, "accept")
    result = filter_by_disposition([r1, r2, r3], "accept")
    assert result == [r1, r3]


def test_filter_by_disposition_empty_list():
    assert filter_by_disposition([], "forward") == []


def test_filter_by_disposition_invalid_raises():
    with pytest.raises(ValueError):
        filter_by_disposition([_rec()], "unknown")
