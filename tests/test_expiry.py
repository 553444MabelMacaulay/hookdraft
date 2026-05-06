"""Tests for hookdraft.expiry."""

from __future__ import annotations

import time

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.expiry import (
    clear_expiry,
    filter_expired,
    filter_live,
    get_expiry,
    is_expired,
    set_expiry,
)


def _rec(record_id: str = "abc") -> RequestRecord:
    return RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        timestamp=time.time(),
    )


# ---------------------------------------------------------------------------
# set_expiry / get_expiry
# ---------------------------------------------------------------------------

def test_set_expiry_stores_future_timestamp():
    rec = _rec()
    before = time.time()
    set_expiry(rec, ttl_seconds=60)
    after = time.time()
    expiry = get_expiry(rec)
    assert expiry is not None
    assert before + 60 <= expiry <= after + 60


def test_set_expiry_zero_raises():
    with pytest.raises(ValueError, match="positive"):
        set_expiry(_rec(), ttl_seconds=0)


def test_set_expiry_negative_raises():
    with pytest.raises(ValueError, match="positive"):
        set_expiry(_rec(), ttl_seconds=-10)


def test_get_expiry_none_when_not_set():
    assert get_expiry(_rec()) is None


# ---------------------------------------------------------------------------
# clear_expiry
# ---------------------------------------------------------------------------

def test_clear_expiry_removes_timestamp():
    rec = _rec()
    set_expiry(rec, ttl_seconds=30)
    clear_expiry(rec)
    assert get_expiry(rec) is None


def test_clear_expiry_idempotent_when_not_set():
    rec = _rec()
    clear_expiry(rec)  # should not raise
    assert get_expiry(rec) is None


# ---------------------------------------------------------------------------
# is_expired
# ---------------------------------------------------------------------------

def test_is_expired_false_when_no_expiry():
    assert is_expired(_rec()) is False


def test_is_expired_false_before_expiry():
    rec = _rec()
    future = time.time() + 1000
    set_expiry(rec, ttl_seconds=1000)
    assert is_expired(rec, now=future - 1) is False


def test_is_expired_true_at_expiry_boundary():
    rec = _rec()
    set_expiry(rec, ttl_seconds=10)
    expiry = get_expiry(rec)
    assert is_expired(rec, now=expiry) is True


def test_is_expired_true_after_expiry():
    rec = _rec()
    set_expiry(rec, ttl_seconds=1)
    assert is_expired(rec, now=time.time() + 100) is True


# ---------------------------------------------------------------------------
# filter_expired / filter_live
# ---------------------------------------------------------------------------

def test_filter_expired_returns_only_expired():
    live = _rec("live")
    dead = _rec("dead")
    set_expiry(live, ttl_seconds=1000)
    set_expiry(dead, ttl_seconds=1)
    now = time.time() + 500
    result = filter_expired([live, dead], now=now)
    assert [r.id for r in result] == ["dead"]


def test_filter_live_excludes_expired():
    live = _rec("live")
    dead = _rec("dead")
    set_expiry(live, ttl_seconds=1000)
    set_expiry(dead, ttl_seconds=1)
    now = time.time() + 500
    result = filter_live([live, dead], now=now)
    assert [r.id for r in result] == ["live"]


def test_filter_live_includes_records_with_no_expiry():
    no_expiry = _rec("no_expiry")
    result = filter_live([no_expiry], now=time.time() + 9999)
    assert len(result) == 1
