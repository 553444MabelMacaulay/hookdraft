"""Tests for hookdraft.mentions."""

import pytest
from hookdraft.mentions import (
    add_mention,
    remove_mention,
    get_mentions,
    has_mention,
    filter_by_mention,
    all_mentions,
)


def _rec(**kwargs):
    base = {"id": "abc", "method": "POST", "path": "/hook", "body": {}}
    base.update(kwargs)
    return base


def test_get_mentions_empty_by_default():
    assert get_mentions(_rec()) == []


def test_add_mention_basic():
    r = _rec()
    add_mention(r, "alice")
    assert "alice" in get_mentions(r)


def test_add_mention_strips_at_symbol():
    r = _rec()
    add_mention(r, "@bob")
    assert "bob" in get_mentions(r)


def test_add_mention_normalises_case():
    r = _rec()
    add_mention(r, "Charlie")
    assert "charlie" in get_mentions(r)


def test_add_mention_deduped():
    r = _rec()
    add_mention(r, "alice")
    add_mention(r, "alice")
    assert get_mentions(r).count("alice") == 1


def test_add_mention_empty_raises():
    with pytest.raises(ValueError):
        add_mention(_rec(), "")


def test_add_mention_whitespace_only_raises():
    with pytest.raises(ValueError):
        add_mention(_rec(), "   ")


def test_add_mention_with_space_raises():
    with pytest.raises(ValueError):
        add_mention(_rec(), "alice bob")


def test_remove_mention_basic():
    r = _rec(mentions=["alice", "bob"])
    remove_mention(r, "alice")
    assert "alice" not in get_mentions(r)
    assert "bob" in get_mentions(r)


def test_remove_mention_idempotent():
    r = _rec()
    remove_mention(r, "alice")  # should not raise
    assert get_mentions(r) == []


def test_has_mention_true():
    r = _rec(mentions=["dave"])
    assert has_mention(r, "dave") is True


def test_has_mention_false():
    r = _rec()
    assert has_mention(r, "dave") is False


def test_filter_by_mention():
    r1 = _rec(mentions=["alice"])
    r2 = _rec(mentions=["bob"])
    r3 = _rec(mentions=["alice", "bob"])
    result = filter_by_mention([r1, r2, r3], "alice")
    assert r1 in result
    assert r3 in result
    assert r2 not in result


def test_all_mentions_sorted_unique():
    r1 = _rec(mentions=["charlie", "alice"])
    r2 = _rec(mentions=["alice", "bob"])
    result = all_mentions([r1, r2])
    assert result == ["alice", "bob", "charlie"]


def test_all_mentions_empty():
    assert all_mentions([]) == []
