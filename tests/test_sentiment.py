"""Tests for hookdraft.sentiment and its HTTP routes."""

from __future__ import annotations

import pytest

from hookdraft.sentiment import (
    set_sentiment,
    clear_sentiment,
    get_sentiment,
    get_sentiment_value,
    has_sentiment,
    filter_by_sentiment,
    filter_positive,
    filter_negative,
)


def _rec(extra=None):
    r = {"id": "r1", "method": "POST", "path": "/hook"}
    if extra:
        r.update(extra)
    return r


# --- unit tests ---

def test_has_sentiment_false_by_default():
    assert has_sentiment(_rec()) is False


def test_get_sentiment_none_by_default():
    assert get_sentiment(_rec()) is None


def test_get_sentiment_value_none_by_default():
    assert get_sentiment_value(_rec()) is None


def test_set_sentiment_positive():
    r = _rec()
    set_sentiment(r, "positive")
    assert get_sentiment_value(r) == "positive"
    assert get_sentiment(r)["score"] == 1


def test_set_sentiment_neutral():
    r = _rec()
    set_sentiment(r, "neutral")
    assert get_sentiment_value(r) == "neutral"
    assert get_sentiment(r)["score"] == 0


def test_set_sentiment_negative():
    r = _rec()
    set_sentiment(r, "negative")
    assert get_sentiment(r)["score"] == -1


def test_set_sentiment_normalises_case():
    r = _rec()
    set_sentiment(r, "POSITIVE")
    assert get_sentiment_value(r) == "positive"


def test_set_sentiment_with_note():
    r = _rec()
    set_sentiment(r, "negative", note="  bad payload  ")
    assert get_sentiment(r)["note"] == "bad payload"


def test_set_sentiment_empty_note_stored_as_none():
    r = _rec()
    set_sentiment(r, "neutral", note="   ")
    assert get_sentiment(r)["note"] is None


def test_set_sentiment_invalid_raises():
    with pytest.raises(ValueError, match="Invalid sentiment"):
        set_sentiment(_rec(), "happy")


def test_set_sentiment_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        set_sentiment(_rec(), "  ")


def test_clear_sentiment_removes_key():
    r = _rec()
    set_sentiment(r, "positive")
    clear_sentiment(r)
    assert has_sentiment(r) is False


def test_clear_sentiment_idempotent():
    r = _rec()
    clear_sentiment(r)  # should not raise
    assert has_sentiment(r) is False


def test_filter_by_sentiment():
    records = [_rec() for _ in range(3)]
    set_sentiment(records[0], "positive")
    set_sentiment(records[1], "negative")
    result = filter_by_sentiment(records, "positive")
    assert len(result) == 1
    assert result[0] is records[0]


def test_filter_positive():
    records = [_rec(), _rec()]
    set_sentiment(records[0], "positive")
    set_sentiment(records[1], "neutral")
    assert filter_positive(records) == [records[0]]


def test_filter_negative():
    records = [_rec(), _rec()]
    set_sentiment(records[0], "negative")
    set_sentiment(records[1], "positive")
    assert filter_negative(records) == [records[0]]


def test_filter_by_sentiment_invalid_raises():
    with pytest.raises(ValueError):
        filter_by_sentiment([], "joyful")
