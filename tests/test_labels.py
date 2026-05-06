"""Unit tests for hookdraft/labels.py."""

import pytest
from hookdraft.labels import (
    set_label,
    remove_label,
    get_labels,
    filter_by_label,
    filter_by_label_colour,
    VALID_COLOURS,
)


def _rec(extra=None):
    d = {"id": "abc", "method": "POST"}
    if extra:
        d.update(extra)
    return d


def test_set_label_basic():
    r = _rec()
    set_label(r, "env", "blue")
    assert r["labels"] == {"env": "blue"}


def test_set_label_default_colour():
    r = _rec()
    set_label(r, "env")
    assert r["labels"]["env"] == "grey"


def test_set_label_normalises_name():
    r = _rec()
    set_label(r, "  ENV  ", "red")
    assert "env" in r["labels"]


def test_set_label_empty_name_raises():
    with pytest.raises(ValueError, match="empty"):
        set_label(_rec(), "  ")


def test_set_label_invalid_colour_raises():
    with pytest.raises(ValueError, match="Colour"):
        set_label(_rec(), "env", "pink")


def test_set_label_overwrites_existing():
    r = _rec()
    set_label(r, "env", "red")
    set_label(r, "env", "blue")
    assert r["labels"]["env"] == "blue"


def test_remove_label_removes():
    r = _rec()
    set_label(r, "env", "green")
    remove_label(r, "env")
    assert "env" not in r["labels"]


def test_remove_label_idempotent():
    r = _rec()
    remove_label(r, "nonexistent")  # should not raise


def test_get_labels_empty():
    assert get_labels(_rec()) == {}


def test_get_labels_returns_copy():
    r = _rec()
    set_label(r, "x", "red")
    result = get_labels(r)
    result["x"] = "blue"
    assert r["labels"]["x"] == "red"


def test_filter_by_label_matches():
    r1 = _rec()
    r2 = _rec()
    set_label(r1, "env", "red")
    assert filter_by_label([r1, r2], "env") == [r1]


def test_filter_by_label_no_match():
    assert filter_by_label([_rec()], "missing") == []


def test_filter_by_label_colour_matches():
    r1 = _rec()
    r2 = _rec()
    set_label(r1, "a", "purple")
    set_label(r2, "b", "red")
    assert filter_by_label_colour([r1, r2], "purple") == [r1]


def test_all_valid_colours_accepted():
    for colour in VALID_COLOURS:
        r = _rec()
        set_label(r, "x", colour)
        assert r["labels"]["x"] == colour
