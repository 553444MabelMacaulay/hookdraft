"""Tests for hookdraft.retry module."""

import pytest
from hookdraft.retry import (
    set_retry_policy,
    clear_retry_policy,
    get_retry_policy,
    record_attempt,
    next_delay,
    filter_exhausted,
    filter_retryable,
    MAX_ATTEMPTS,
)


def _rec():
    return {"id": "abc", "meta": {}}


def test_set_retry_policy_defaults():
    r = _rec()
    set_retry_policy(r)
    policy = get_retry_policy(r)
    assert policy["max_attempts"] == 3
    assert policy["backoff_base"] == 2
    assert policy["attempts"] == 0
    assert policy["last_status"] is None
    assert policy["exhausted"] is False


def test_set_retry_policy_custom():
    r = _rec()
    set_retry_policy(r, max_attempts=2, backoff_base=1.5)
    policy = get_retry_policy(r)
    assert policy["max_attempts"] == 2
    assert policy["backoff_base"] == 1.5


def test_set_retry_policy_zero_attempts_raises():
    with pytest.raises(ValueError, match="at least 1"):
        set_retry_policy(_rec(), max_attempts=0)


def test_set_retry_policy_exceeds_max_raises():
    with pytest.raises(ValueError, match="cannot exceed"):
        set_retry_policy(_rec(), max_attempts=MAX_ATTEMPTS + 1)


def test_set_retry_policy_negative_backoff_raises():
    with pytest.raises(ValueError, match="positive"):
        set_retry_policy(_rec(), backoff_base=-1)


def test_clear_retry_policy():
    r = _rec()
    set_retry_policy(r)
    clear_retry_policy(r)
    assert get_retry_policy(r) is None


def test_clear_retry_policy_idempotent():
    r = _rec()
    clear_retry_policy(r)  # no policy set — should not raise
    assert get_retry_policy(r) is None


def test_record_attempt_increments_counter():
    r = _rec()
    set_retry_policy(r, max_attempts=3)
    record_attempt(r, 500)
    policy = get_retry_policy(r)
    assert policy["attempts"] == 1
    assert policy["last_status"] == 500
    assert policy["exhausted"] is False


def test_record_attempt_exhausts_on_max():
    r = _rec()
    set_retry_policy(r, max_attempts=2)
    record_attempt(r, 503)
    record_attempt(r, 503)
    assert get_retry_policy(r)["exhausted"] is True


def test_record_attempt_no_policy_raises():
    r = _rec()
    with pytest.raises(ValueError, match="No retry policy"):
        record_attempt(r, 200)


def test_next_delay_exponential():
    r = _rec()
    set_retry_policy(r, max_attempts=4, backoff_base=2)
    assert next_delay(r) == 1.0  # 2^0
    record_attempt(r, 500)
    assert next_delay(r) == 2.0  # 2^1
    record_attempt(r, 500)
    assert next_delay(r) == 4.0  # 2^2


def test_next_delay_no_policy_raises():
    r = _rec()
    with pytest.raises(ValueError):
        next_delay(r)


def test_filter_exhausted():
    r1 = _rec()
    r2 = _rec()
    set_retry_policy(r1, max_attempts=1)
    set_retry_policy(r2, max_attempts=3)
    record_attempt(r1, 500)  # exhausted
    result = filter_exhausted([r1, r2])
    assert r1 in result
    assert r2 not in result


def test_filter_retryable():
    r1 = _rec()
    r2 = _rec()
    r3 = _rec()  # no policy
    set_retry_policy(r1, max_attempts=1)
    set_retry_policy(r2, max_attempts=3)
    record_attempt(r1, 500)  # exhausted
    result = filter_retryable([r1, r2, r3])
    assert r2 in result
    assert r1 not in result
    assert r3 not in result
