"""Retry policy helpers for webhook replay."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

MAX_ATTEMPTS = 5
DEFAULT_BACKOFF_BASE = 2  # seconds


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_base: float = DEFAULT_BACKOFF_BASE
    attempts: int = 0
    last_status: Optional[int] = None
    exhausted: bool = False


def set_retry_policy(record: dict, max_attempts: int = 3, backoff_base: float = DEFAULT_BACKOFF_BASE) -> None:
    """Attach a retry policy to a record's metadata."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if max_attempts > MAX_ATTEMPTS:
        raise ValueError(f"max_attempts cannot exceed {MAX_ATTEMPTS}")
    if backoff_base <= 0:
        raise ValueError("backoff_base must be positive")
    record.setdefault("meta", {})
    record["meta"]["retry"] = {
        "max_attempts": max_attempts,
        "backoff_base": backoff_base,
        "attempts": 0,
        "last_status": None,
        "exhausted": False,
    }


def clear_retry_policy(record: dict) -> None:
    """Remove retry policy from a record."""
    record.setdefault("meta", {})
    record["meta"].pop("retry", None)


def get_retry_policy(record: dict) -> Optional[dict]:
    """Return the retry policy dict or None if not set."""
    return record.get("meta", {}).get("retry")


def record_attempt(record: dict, status_code: int) -> None:
    """Increment the attempt counter and update last status."""
    policy = get_retry_policy(record)
    if policy is None:
        raise ValueError("No retry policy set on this record")
    policy["attempts"] += 1
    policy["last_status"] = status_code
    if policy["attempts"] >= policy["max_attempts"]:
        policy["exhausted"] = True


def next_delay(record: dict) -> float:
    """Return the next backoff delay in seconds based on attempts so far."""
    policy = get_retry_policy(record)
    if policy is None:
        raise ValueError("No retry policy set on this record")
    attempts = policy["attempts"]
    base = policy["backoff_base"]
    return base ** attempts


def filter_exhausted(records: list) -> list:
    """Return records whose retry policy is exhausted."""
    return [
        r for r in records
        if (get_retry_policy(r) or {}).get("exhausted") is True
    ]


def filter_retryable(records: list) -> list:
    """Return records that have a retry policy and are not yet exhausted."""
    return [
        r for r in records
        if get_retry_policy(r) is not None
        and not get_retry_policy(r).get("exhausted", False)
    ]
