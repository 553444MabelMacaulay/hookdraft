"""Tests for hookdraft.versioning."""

import pytest
from hookdraft.versioning import (
    set_version,
    clear_version,
    get_version,
    get_changelog,
    has_version,
    filter_by_version,
)


def _rec() -> dict:
    return {"id": "test-id", "body": {}}


# ---------------------------------------------------------------------------
# get_version / has_version defaults
# ---------------------------------------------------------------------------

def test_get_version_none_by_default():
    assert get_version(_rec()) is None


def test_has_version_false_by_default():
    assert has_version(_rec()) is False


def test_get_changelog_none_by_default():
    assert get_changelog(_rec()) is None


# ---------------------------------------------------------------------------
# set_version
# ---------------------------------------------------------------------------

def test_set_version_basic():
    rec = _rec()
    set_version(rec, "v1")
    assert get_version(rec) == "v1"
    assert has_version(rec) is True


def test_set_version_strips_whitespace():
    rec = _rec()
    set_version(rec, "  v2  ")
    assert get_version(rec) == "v2"


def test_set_version_with_changelog():
    rec = _rec()
    set_version(rec, "v3", changelog="Added new field")
    assert get_version(rec) == "v3"
    assert get_changelog(rec) == "Added new field"


def test_set_version_changelog_strips_whitespace():
    rec = _rec()
    set_version(rec, "v4", changelog="  trimmed  ")
    assert get_changelog(rec) == "trimmed"


def test_set_version_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_version(_rec(), "")


def test_set_version_whitespace_only_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_version(_rec(), "   ")


def test_set_version_too_long_raises():
    with pytest.raises(ValueError, match="must not exceed"):
        set_version(_rec(), "x" * 65)


def test_set_version_empty_changelog_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_version(_rec(), "v1", changelog="")


def test_set_version_changelog_too_long_raises():
    with pytest.raises(ValueError, match="must not exceed"):
        set_version(_rec(), "v1", changelog="c" * 513)


def test_set_version_overwrites_previous():
    rec = _rec()
    set_version(rec, "v1", changelog="first")
    set_version(rec, "v2")  # no changelog this time
    assert get_version(rec) == "v2"
    assert get_changelog(rec) is None  # old changelog removed


# ---------------------------------------------------------------------------
# clear_version
# ---------------------------------------------------------------------------

def test_clear_version_removes_version():
    rec = _rec()
    set_version(rec, "v1", changelog="note")
    clear_version(rec)
    assert get_version(rec) is None
    assert get_changelog(rec) is None
    assert has_version(rec) is False


def test_clear_version_idempotent():
    rec = _rec()
    clear_version(rec)  # should not raise
    assert get_version(rec) is None


# ---------------------------------------------------------------------------
# filter_by_version
# ---------------------------------------------------------------------------

def test_filter_by_version_matches():
    r1 = _rec()
    r2 = _rec()
    r3 = _rec()
    set_version(r1, "v1")
    set_version(r2, "v2")
    set_version(r3, "v1")
    result = filter_by_version([r1, r2, r3], "v1")
    assert result == [r1, r3]


def test_filter_by_version_no_match():
    rec = _rec()
    set_version(rec, "v1")
    assert filter_by_version([rec], "v99") == []


def test_filter_by_version_strips_query_whitespace():
    rec = _rec()
    set_version(rec, "v1")
    assert filter_by_version([rec], "  v1  ") == [rec]


def test_filter_by_version_excludes_unversioned():
    versioned = _rec()
    unversioned = _rec()
    set_version(versioned, "v1")
    result = filter_by_version([versioned, unversioned], "v1")
    assert unversioned not in result
