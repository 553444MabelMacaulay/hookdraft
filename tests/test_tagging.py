"""Unit tests for hookdraft.tagging module."""
import pytest
from hookdraft.tagging import add_tag, remove_tag, filter_by_tag, filter_by_any_tag, all_tags
from hookdraft.storage import RequestRecord


def _rec(tags):
    return RequestRecord(
        id="x", timestamp="t", method="POST",
        path="/hook", headers={}, body="", tags=list(tags)
    )


def test_add_tag_new():
    result = add_tag(["alpha"], "beta")
    assert result == ["alpha", "beta"]


def test_add_tag_deduped():
    result = add_tag(["alpha"], "alpha")
    assert result == ["alpha"]


def test_add_tag_normalised():
    result = add_tag([], "  Beta  ")
    assert result == ["beta"]


def test_add_tag_empty_raises():
    with pytest.raises(ValueError):
        add_tag([], "")


def test_remove_tag_present():
    result = remove_tag(["alpha", "beta"], "alpha")
    assert result == ["beta"]


def test_remove_tag_absent():
    result = remove_tag(["alpha"], "gamma")
    assert result == ["alpha"]


def test_filter_by_tag():
    records = [_rec(["a", "b"]), _rec(["b"]), _rec(["c"])]
    assert filter_by_tag(records, "a") == [records[0]]
    assert filter_by_tag(records, "b") == [records[0], records[1]]
    assert filter_by_tag(records, "z") == []


def test_filter_by_any_tag():
    records = [_rec(["a"]), _rec(["b"]), _rec(["c"])]
    result = filter_by_any_tag(records, ["a", "c"])
    assert result == [records[0], records[2]]


def test_all_tags_sorted():
    records = [_rec(["banana", "apple"]), _rec(["cherry", "apple"])]
    assert all_tags(records) == ["apple", "banana", "cherry"]


def test_all_tags_empty():
    assert all_tags([]) == []
