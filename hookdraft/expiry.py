"""Expiry support for request records.

Allows records to be given a TTL (time-to-live) in seconds.
Expired records can be detected and filtered out.
"""

from __future__ import annotations

import time
from typing import List, Optional

from hookdraft.storage import RequestRecord

_EXPIRY_KEY = "expires_at"


def set_expiry(record: RequestRecord, ttl_seconds: int) -> RequestRecord:
    """Set an expiry time on *record* as an epoch timestamp.

    Args:
        record: The request record to modify.
        ttl_seconds: Seconds from now until the record is considered expired.
                     Must be a positive integer.

    Returns:
        The same record (mutated in place) for convenience.
    """
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be a positive integer")
    record.meta[_EXPIRY_KEY] = time.time() + ttl_seconds
    return record


def clear_expiry(record: RequestRecord) -> RequestRecord:
    """Remove any expiry from *record*."""
    record.meta.pop(_EXPIRY_KEY, None)
    return record


def get_expiry(record: RequestRecord) -> Optional[float]:
    """Return the expiry epoch timestamp, or *None* if not set."""
    return record.meta.get(_EXPIRY_KEY)


def is_expired(record: RequestRecord, *, now: Optional[float] = None) -> bool:
    """Return *True* if the record has passed its expiry time.

    Args:
        record: The record to check.
        now: Override the current time (useful in tests).
    """
    expiry = get_expiry(record)
    if expiry is None:
        return False
    return (now if now is not None else time.time()) >= expiry


def filter_expired(
    records: List[RequestRecord], *, now: Optional[float] = None
) -> List[RequestRecord]:
    """Return only records that have expired."""
    return [r for r in records if is_expired(r, now=now)]


def filter_live(
    records: List[RequestRecord], *, now: Optional[float] = None
) -> List[RequestRecord]:
    """Return only records that have *not* expired."""
    return [r for r in records if not is_expired(r, now=now)]
