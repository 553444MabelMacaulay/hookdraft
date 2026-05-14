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


def assert_unlocked(record: RequestRecord) -> None:
    """Raise a RuntimeError if the record is locked.

    Intended as a guard at the start of mutating operations to prevent
    accidental modifications to locked records.

    Raises:
        RuntimeError: If the record is currently locked, with the lock
            reason included in the message when one is set.
    """
    if is_locked(record):
        reason = get_lock_reason(record)
        msg = "Record is locked and cannot be modified."
        if reason:
            msg = f"Record is locked and cannot be modified: {reason}"
        raise RuntimeError(msg)


def filter_locked(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are locked."""
    return [r for r in records if is_locked(r)]


def filter_unlocked(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are not locked."""
    return [r for r in records if not is_locked(r)]
