"""Tests for hookdraft.ownership and ownership routes."""

import pytest
from hookdraft.ownership import (
    set_owner, clear_owner, get_owner, get_team,
    is_owned, filter_by_owner, filter_by_team,
)


def _rec():
    return {"id": "r1", "method": "POST", "path": "/hook"}


# --- unit tests for ownership.py ---

def test_get_owner_none_by_default():
    assert get_owner(_rec()) is None


def test_is_owned_false_by_default():
    assert is_owned(_rec()) is False


def test_set_owner_basic():
    r = _rec()
    set_owner(r, "alice")
    assert get_owner(r) == "alice"


def test_set_owner_normalises_case():
    r = _rec()
    set_owner(r, "Alice")
    assert get_owner(r) == "alice"


def test_set_owner_strips_whitespace():
    r = _rec()
    set_owner(r, "  bob  ")
    assert get_owner(r) == "bob"


def test_set_owner_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_owner(_rec(), "")


def test_set_owner_whitespace_only_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_owner(_rec(), "   ")


def test_set_owner_with_spaces_raises():
    with pytest.raises(ValueError, match="must not contain spaces"):
        set_owner(_rec(), "alice bob")


def test_set_owner_with_team():
    r = _rec()
    set_owner(r, "carol", team="backend")
    assert get_owner(r) == "carol"
    assert get_team(r) == "backend"


def test_set_owner_team_normalised():
    r = _rec()
    set_owner(r, "dave", team="  Ops  ")
    assert get_team(r) == "ops"


def test_set_owner_empty_team_raises():
    with pytest.raises(ValueError, match="team must not be empty"):
        set_owner(_rec(), "eve", team="")


def test_get_team_none_when_no_team():
    r = _rec()
    set_owner(r, "frank")
    assert get_team(r) is None


def test_clear_owner_removes_ownership():
    r = _rec()
    set_owner(r, "grace", team="ops")
    clear_owner(r)
    assert get_owner(r) is None
    assert get_team(r) is None
    assert is_owned(r) is False


def test_filter_by_owner():
    r1, r2, r3 = _rec(), _rec(), _rec()
    set_owner(r1, "alice")
    set_owner(r2, "bob")
    result = filter_by_owner([r1, r2, r3], "alice")
    assert result == [r1]


def test_filter_by_team():
    r1, r2, r3 = _rec(), _rec(), _rec()
    set_owner(r1, "alice", team="backend")
    set_owner(r2, "bob", team="frontend")
    set_owner(r3, "carol", team="backend")
    result = filter_by_team([r1, r2, r3], "backend")
    assert result == [r1, r3]
