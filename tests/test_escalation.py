"""Tests for hookdraft.escalation."""

import pytest
from hookdraft.escalation import (
    escalate_record,
    deescalate_record,
    is_escalated,
    get_escalation,
    get_escalation_tier,
    filter_escalated,
    filter_by_min_tier,
)


def _rec(extra=None):
    d = {"id": "r1", "method": "POST", "path": "/hook", "body": {}}
    if extra:
        d.update(extra)
    return d


def test_is_escalated_false_by_default():
    assert is_escalated(_rec()) is False


def test_get_escalation_none_by_default():
    assert get_escalation(_rec()) is None


def test_escalate_record_sets_flag():
    r = _rec()
    escalate_record(r, "high")
    assert is_escalated(r) is True


def test_escalate_record_stores_tier():
    r = _rec()
    escalate_record(r, "critical")
    assert get_escalation_tier(r) == "critical"


def test_escalate_record_normalises_case():
    r = _rec()
    escalate_record(r, "HIGH")
    assert get_escalation_tier(r) == "high"


def test_escalate_record_strips_whitespace():
    r = _rec()
    escalate_record(r, "  medium  ")
    assert get_escalation_tier(r) == "medium"


def test_escalate_record_stores_reason():
    r = _rec()
    escalate_record(r, "low", reason="needs review")
    assert get_escalation(r)["reason"] == "needs review"


def test_escalate_record_reason_none_when_empty():
    r = _rec()
    escalate_record(r, "low", reason="")
    assert get_escalation(r)["reason"] is None


def test_escalate_record_stores_timestamp():
    r = _rec()
    escalate_record(r, "medium")
    assert "escalated_at" in get_escalation(r)


def test_escalate_invalid_tier_raises():
    with pytest.raises(ValueError, match="Invalid escalation tier"):
        escalate_record(_rec(), "extreme")


def test_deescalate_removes_flag():
    r = _rec()
    escalate_record(r, "high")
    deescalate_record(r)
    assert is_escalated(r) is False


def test_deescalate_idempotent():
    r = _rec()
    deescalate_record(r)  # should not raise
    assert is_escalated(r) is False


def test_filter_escalated():
    r1, r2, r3 = _rec(), _rec(), _rec()
    escalate_record(r1, "low")
    escalate_record(r3, "critical")
    result = filter_escalated([r1, r2, r3])
    assert result == [r1, r3]


def test_filter_by_min_tier_high():
    r1, r2, r3, r4 = _rec(), _rec(), _rec(), _rec()
    escalate_record(r1, "low")
    escalate_record(r2, "medium")
    escalate_record(r3, "high")
    escalate_record(r4, "critical")
    result = filter_by_min_tier([r1, r2, r3, r4], "high")
    assert result == [r3, r4]


def test_filter_by_min_tier_invalid_raises():
    with pytest.raises(ValueError):
        filter_by_min_tier([], "extreme")
