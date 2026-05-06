"""Unit tests for hookdraft.flagging."""

import pytest

from hookdraft.flagging import (
    filter_flagged,
    filter_unflagged,
    flag_record,
    get_flag_reason,
    is_flagged,
    unflag_record,
)
from hookdraft.storage import RequestRecord


def _rec(rid: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=rid,
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        timestamp="2024-01-01T00:00:00",
    )


def test_is_flagged_false_by_default():
    assert is_flagged(_rec()) is False


def test_flag_record_sets_flag():
    r = _rec()
    flag_record(r)
    assert is_flagged(r) is True


def test_flag_record_stores_reason():
    r = _rec()
    flag_record(r, reason="needs review")
    assert get_flag_reason(r) == "needs review"


def test_flag_record_strips_reason_whitespace():
    r = _rec()
    flag_record(r, reason="  spaces  ")
    assert get_flag_reason(r) == "spaces"


def test_flag_record_empty_reason_by_default():
    r = _rec()
    flag_record(r)
    assert get_flag_reason(r) == ""


def test_unflag_record_removes_flag():
    r = _rec()
    flag_record(r, reason="oops")
    unflag_record(r)
    assert is_flagged(r) is False
    assert get_flag_reason(r) == ""


def test_unflag_idempotent_when_not_flagged():
    r = _rec()
    unflag_record(r)  # should not raise
    assert is_flagged(r) is False


def test_filter_flagged():
    r1, r2, r3 = _rec("1"), _rec("2"), _rec("3")
    flag_record(r1)
    flag_record(r3)
    result = filter_flagged([r1, r2, r3])
    assert [r.id for r in result] == ["1", "3"]


def test_filter_unflagged():
    r1, r2 = _rec("1"), _rec("2")
    flag_record(r1)
    result = filter_unflagged([r1, r2])
    assert [r.id for r in result] == ["2"]
