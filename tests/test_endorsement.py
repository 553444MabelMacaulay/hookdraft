"""Tests for hookdraft.endorsement."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.endorsement import (
    endorse_record,
    unendorse_record,
    get_endorsements,
    endorsement_count,
    has_endorsement,
    filter_endorsed,
    filter_endorsed_by,
)


def _rec():
    return RequestRecord(
        id="abc",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )


def test_get_endorsements_empty_by_default():
    rec = _rec()
    assert get_endorsements(rec) == []


def test_endorsement_count_zero_by_default():
    rec = _rec()
    assert endorsement_count(rec) == 0


def test_has_endorsement_false_by_default():
    rec = _rec()
    assert has_endorsement(rec, "alice") is False


def test_endorse_record_basic():
    rec = _rec()
    endorse_record(rec, "alice")
    assert "alice" in get_endorsements(rec)


def test_endorse_record_normalises_case():
    rec = _rec()
    endorse_record(rec, "Alice")
    assert "alice" in get_endorsements(rec)


def test_endorse_record_strips_whitespace():
    rec = _rec()
    endorse_record(rec, "  bob  ")
    assert "bob" in get_endorsements(rec)


def test_endorse_record_deduped():
    rec = _rec()
    endorse_record(rec, "alice")
    endorse_record(rec, "alice")
    assert get_endorsements(rec).count("alice") == 1


def test_endorse_record_multiple_users():
    rec = _rec()
    endorse_record(rec, "alice")
    endorse_record(rec, "bob")
    assert endorsement_count(rec) == 2


def test_unendorse_record_removes_user():
    rec = _rec()
    endorse_record(rec, "alice")
    unendorse_record(rec, "alice")
    assert "alice" not in get_endorsements(rec)


def test_unendorse_record_idempotent_when_not_present():
    rec = _rec()
    unendorse_record(rec, "alice")  # should not raise
    assert get_endorsements(rec) == []


def test_endorse_empty_name_raises():
    rec = _rec()
    with pytest.raises(ValueError, match="empty"):
        endorse_record(rec, "   ")


def test_endorse_name_too_long_raises():
    rec = _rec()
    with pytest.raises(ValueError, match="64"):
        endorse_record(rec, "x" * 65)


def test_has_endorsement_true_after_endorsing():
    rec = _rec()
    endorse_record(rec, "carol")
    assert has_endorsement(rec, "carol") is True


def test_filter_endorsed_min_count():
    r1, r2, r3 = _rec(), _rec(), _rec()
    endorse_record(r1, "alice")
    endorse_record(r2, "alice")
    endorse_record(r2, "bob")
    result = list(filter_endorsed([r1, r2, r3], min_count=2))
    assert result == [r2]


def test_filter_endorsed_by_user():
    r1, r2, r3 = _rec(), _rec(), _rec()
    endorse_record(r1, "alice")
    endorse_record(r2, "bob")
    endorse_record(r3, "alice")
    result = list(filter_endorsed_by([r1, r2, r3], "alice"))
    assert r1 in result
    assert r3 in result
    assert r2 not in result
