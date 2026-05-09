"""Record locking — prevent modifications to specific request records."""

from __future__ import annotations

from typing import List

from hookdraft.storage import RequestRecord

_LOCK_KEY = "locked"
_LOCK_REASON_KEY = "lock_reason"


def lock_record(record: RequestRecord, reason: str = "") -> None:
    """Lock a record, optionally storing a reason."""
    reason = reason.strip()
    record.meta[_LOCK_KEY] = True
    record.meta[_LOCK_REASON_KEY] = reason if reason else None


def unlock_record(record: RequestRecord) -> None:
    """Unlock a record, removing any stored reason."""
    record.meta.pop(_LOCK_KEY, None)
    record.meta.pop(_LOCK_REASON_KEY, None)


def is_locked(record: RequestRecord) -> bool:
    """Return True if the record is currently locked."""
    return bool(record.meta.get(_LOCK_KEY, False))


def get_lock_reason(record: RequestRecord) -> str | None:
    """Return the lock reason, or None if not set."""
    return record.meta.get(_LOCK_REASON_KEY)


def filter_locked(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are locked."""
    return [r for r in records if is_locked(r)]


def filter_unlocked(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are not locked."""
    return [r for r in records if not is_locked(r)]
