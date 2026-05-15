"""Tests for hookdraft.signaling."""

import pytest

from hookdraft import signaling


def _rec() -> dict:
    return {"id": "r1", "body": {}}


# --- unit tests ---

def test_get_signals_empty_by_default():
    assert signaling.get_signals(_rec()) == []


def test_signal_count_zero_by_default():
    assert signaling.signal_count(_rec()) == 0


def test_has_signal_false_by_default():
    assert signaling.has_signal(_rec(), "high-latency") is False


def test_raise_signal_basic():
    rec = _rec()
    signaling.raise_signal(rec, "high-latency")
    assert signaling.has_signal(rec, "high-latency") is True
    assert signaling.signal_count(rec) == 1


def test_raise_signal_with_detail():
    rec = _rec()
    signaling.raise_signal(rec, "auth-failure", detail="token expired")
    sigs = signaling.get_signals(rec)
    assert sigs[0]["detail"] == "token expired"


def test_raise_signal_normalises_name():
    rec = _rec()
    signaling.raise_signal(rec, "  High Latency  ")
    assert signaling.has_signal(rec, "high-latency") is True


def test_raise_signal_deduplicates():
    rec = _rec()
    signaling.raise_signal(rec, "retry-exhausted")
    signaling.raise_signal(rec, "retry-exhausted")
    assert signaling.signal_count(rec) == 1


def test_raise_signal_updates_detail_on_duplicate():
    rec = _rec()
    signaling.raise_signal(rec, "retry-exhausted", detail="first")
    signaling.raise_signal(rec, "retry-exhausted", detail="updated")
    sigs = signaling.get_signals(rec)
    assert len(sigs) == 1
    assert sigs[0]["detail"] == "updated"


def test_raise_signal_empty_name_raises():
    rec = _rec()
    with pytest.raises(ValueError):
        signaling.raise_signal(rec, "")


def test_raise_signal_whitespace_only_raises():
    rec = _rec()
    with pytest.raises(ValueError):
        signaling.raise_signal(rec, "   ")


def test_clear_signal_removes_named():
    rec = _rec()
    signaling.raise_signal(rec, "high-latency")
    signaling.raise_signal(rec, "auth-failure")
    signaling.clear_signal(rec, "high-latency")
    assert signaling.has_signal(rec, "high-latency") is False
    assert signaling.has_signal(rec, "auth-failure") is True


def test_clear_signal_idempotent_when_absent():
    rec = _rec()
    signaling.clear_signal(rec, "nonexistent")  # should not raise
    assert signaling.signal_count(rec) == 0


def test_clear_all_signals():
    rec = _rec()
    signaling.raise_signal(rec, "sig-a")
    signaling.raise_signal(rec, "sig-b")
    signaling.clear_all_signals(rec)
    assert signaling.signal_count(rec) == 0


def test_filter_by_signal():
    r1 = _rec()
    r2 = {"id": "r2", "body": {}}
    signaling.raise_signal(r1, "high-latency")
    result = signaling.filter_by_signal([r1, r2], "high-latency")
    assert result == [r1]


def test_filter_by_signal_empty_when_none_match():
    r1 = _rec()
    result = signaling.filter_by_signal([r1], "nonexistent")
    assert result == []
