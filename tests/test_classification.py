"""Tests for hookdraft.classification."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.classification import (
    set_classification,
    clear_classification,
    get_classification,
    get_class_name,
    has_classification,
    filter_by_class,
    valid_classes,
)


def _rec() -> RequestRecord:
    return RequestRecord(
        id="rec-1",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00Z",
    )


def test_get_classification_none_by_default():
    assert get_classification(_rec()) is None


def test_has_classification_false_by_default():
    assert has_classification(_rec()) is False


def test_get_class_name_none_by_default():
    assert get_class_name(_rec()) is None


def test_set_classification_basic():
    r = _rec()
    set_classification(r, "webhook")
    assert has_classification(r) is True
    assert get_class_name(r) == "webhook"


def test_set_classification_normalises_case():
    r = _rec()
    set_classification(r, "PING")
    assert get_class_name(r) == "ping"


def test_set_classification_strips_whitespace():
    r = _rec()
    set_classification(r, "  alert  ")
    assert get_class_name(r) == "alert"


def test_set_classification_with_note():
    r = _rec()
    set_classification(r, "event", note="Stripe payment event")
    entry = get_classification(r)
    assert entry["note"] == "Stripe payment event"


def test_set_classification_note_stripped():
    r = _rec()
    set_classification(r, "command", note="  do something  ")
    assert get_classification(r)["note"] == "do something"


def test_set_classification_empty_name_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_classification(_rec(), "")


def test_set_classification_unknown_raises():
    with pytest.raises(ValueError, match="Unknown classification"):
        set_classification(_rec(), "mystery")


def test_clear_classification_removes_entry():
    r = _rec()
    set_classification(r, "heartbeat")
    clear_classification(r)
    assert has_classification(r) is False
    assert get_classification(r) is None


def test_clear_classification_idempotent():
    r = _rec()
    clear_classification(r)  # no error when not set
    assert has_classification(r) is False


def test_filter_by_class_returns_matching():
    r1, r2, r3 = _rec(), _rec(), _rec()
    r1.id, r2.id, r3.id = "a", "b", "c"
    set_classification(r1, "webhook")
    set_classification(r2, "ping")
    set_classification(r3, "webhook")
    result = filter_by_class([r1, r2, r3], "webhook")
    assert [r.id for r in result] == ["a", "c"]


def test_filter_by_class_case_insensitive():
    r = _rec()
    set_classification(r, "alert")
    assert filter_by_class([r], "ALERT") == [r]


def test_filter_by_class_excludes_unclassified():
    r = _rec()
    assert filter_by_class([r], "event") == []


def test_valid_classes_returns_sorted_list():
    classes = valid_classes()
    assert isinstance(classes, list)
    assert classes == sorted(classes)
    assert "webhook" in classes
    assert "other" in classes
