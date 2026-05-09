"""Tests for hookdraft.aliasing."""

import pytest

from hookdraft import aliasing


def _rec(**kwargs):
    """Return a minimal record dict, optionally pre-populated."""
    base = {"id": "abc", "method": "POST", "path": "/hook"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# get_alias / has_alias defaults
# ---------------------------------------------------------------------------

def test_get_alias_none_by_default():
    assert aliasing.get_alias(_rec()) is None


def test_has_alias_false_by_default():
    assert aliasing.has_alias(_rec()) is False


# ---------------------------------------------------------------------------
# set_alias
# ---------------------------------------------------------------------------

def test_set_alias_basic():
    rec = _rec()
    aliasing.set_alias(rec, "my-alias")
    assert aliasing.get_alias(rec) == "my-alias"


def test_set_alias_strips_whitespace():
    rec = _rec()
    aliasing.set_alias(rec, "  trimmed  ")
    assert aliasing.get_alias(rec) == "trimmed"


def test_set_alias_overwrites_existing():
    rec = _rec()
    aliasing.set_alias(rec, "first")
    aliasing.set_alias(rec, "second")
    assert aliasing.get_alias(rec) == "second"


def test_set_alias_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        aliasing.set_alias(_rec(), "")


def test_set_alias_whitespace_only_raises():
    with pytest.raises(ValueError, match="empty"):
        aliasing.set_alias(_rec(), "   ")


def test_set_alias_too_long_raises():
    with pytest.raises(ValueError, match="80 characters"):
        aliasing.set_alias(_rec(), "x" * 81)


def test_set_alias_exactly_max_length_ok():
    rec = _rec()
    aliasing.set_alias(rec, "a" * 80)
    assert len(aliasing.get_alias(rec)) == 80


# ---------------------------------------------------------------------------
# clear_alias
# ---------------------------------------------------------------------------

def test_clear_alias_removes_it():
    rec = _rec()
    aliasing.set_alias(rec, "temp")
    aliasing.clear_alias(rec)
    assert aliasing.get_alias(rec) is None


def test_clear_alias_idempotent_when_not_set():
    rec = _rec()
    aliasing.clear_alias(rec)  # should not raise
    assert aliasing.has_alias(rec) is False


# ---------------------------------------------------------------------------
# filter_by_alias / find_by_alias
# ---------------------------------------------------------------------------

def test_filter_by_alias_returns_matches():
    r1, r2, r3 = _rec(), _rec(), _rec()
    aliasing.set_alias(r1, "alpha")
    aliasing.set_alias(r2, "beta")
    result = aliasing.filter_by_alias([r1, r2, r3], "alpha")
    assert result == [r1]


def test_filter_by_alias_case_insensitive():
    rec = _rec()
    aliasing.set_alias(rec, "MyAlias")
    result = aliasing.filter_by_alias([rec], "myalias")
    assert result == [rec]


def test_filter_by_alias_no_match_returns_empty():
    rec = _rec()
    aliasing.set_alias(rec, "something")
    assert aliasing.filter_by_alias([rec], "other") == []


def test_find_by_alias_returns_first_match():
    r1, r2 = _rec(), _rec()
    aliasing.set_alias(r1, "dup")
    aliasing.set_alias(r2, "dup")
    assert aliasing.find_by_alias([r1, r2], "dup") is r1


def test_find_by_alias_returns_none_when_missing():
    assert aliasing.find_by_alias([_rec()], "ghost") is None
