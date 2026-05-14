"""Tests for hookdraft.acknowledgement."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.acknowledgement import (
    acknowledge_record,
    unacknowledge_record,
    is_acknowledged,
    get_acknowledgement,
    filter_acknowledged,
    filter_unacknowledged,
)


def _rec():
    return RequestRecord(
        method="POST",
        path="/hook",
        headers={},
        body=None,
        status_code=200,
    )


def test_is_acknowledged_false_by_default():
    assert is_acknowledged(_rec()) is False


def test_get_acknowledgement_none_by_default():
    assert get_acknowledgement(_rec()) is None


def test_acknowledge_record_sets_flag():
    r = _rec()
    acknowledge_record(r)
    assert is_acknowledged(r) is True


def test_acknowledge_record_stores_timestamp():
    r = _rec()
    acknowledge_record(r)
    ack = get_acknowledgement(r)
    assert "acknowledged_at" in ack
    assert ack["acknowledged_at"] is not None


def test_acknowledge_record_with_user():
    r = _rec()
    acknowledge_record(r, acknowledged_by="alice")
    ack = get_acknowledgement(r)
    assert ack["acknowledged_by"] == "alice"


def test_acknowledge_record_normalises_user_case():
    r = _rec()
    acknowledge_record(r, acknowledged_by="  BOB  ")
    ack = get_acknowledgement(r)
    assert ack["acknowledged_by"] == "bob"


def test_acknowledge_record_with_note():
    r = _rec()
    acknowledge_record(r, note="Reviewed and confirmed.")
    ack = get_acknowledgement(r)
    assert ack["note"] == "Reviewed and confirmed."


def test_acknowledge_record_strips_note_whitespace():
    r = _rec()
    acknowledge_record(r, note="  looks good  ")
    assert get_acknowledgement(r)["note"] == "looks good"


def test_acknowledge_empty_user_raises():
    with pytest.raises(ValueError, match="acknowledged_by"):
        acknowledge_record(_rec(), acknowledged_by="   ")


def test_acknowledge_empty_note_raises():
    with pytest.raises(ValueError, match="note"):
        acknowledge_record(_rec(), note="   ")


def test_unacknowledge_removes_flag():
    r = _rec()
    acknowledge_record(r)
    unacknowledge_record(r)
    assert is_acknowledged(r) is False
    assert get_acknowledgement(r) is None


def test_unacknowledge_idempotent_when_not_set():
    r = _rec()
    unacknowledge_record(r)  # should not raise
    assert is_acknowledged(r) is False


def test_filter_acknowledged():
    r1, r2, r3 = _rec(), _rec(), _rec()
    acknowledge_record(r1)
    acknowledge_record(r3)
    result = filter_acknowledged([r1, r2, r3])
    assert result == [r1, r3]


def test_filter_unacknowledged():
    r1, r2, r3 = _rec(), _rec(), _rec()
    acknowledge_record(r2)
    result = filter_unacknowledged([r1, r2, r3])
    assert result == [r1, r3]
