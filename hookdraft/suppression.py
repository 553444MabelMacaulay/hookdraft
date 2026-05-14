"""Suppression: mute a request record so it is excluded from normal listings."""

from __future__ import annotations

from typing import List

from hookdraft.storage import RequestRecord

_SUPPRESSION_KEY = "_suppressed"
_REASON_KEY = "_suppression_reason"


def suppress_record(record: RequestRecord, reason: str = "") -> None:
    """Mark *record* as suppressed, optionally recording a reason."""
    reason = reason.strip()
    record.meta[_SUPPRESSION_KEY] = True
    record.meta[_REASON_KEY] = reason if reason else None


def unsuppress_record(record: RequestRecord) -> None:
    """Remove the suppression flag from *record* (idempotent)."""
    record.meta.pop(_SUPPRESSION_KEY, None)
    record.meta.pop(_REASON_KEY, None)


def is_suppressed(record: RequestRecord) -> bool:
    """Return ``True`` if *record* is currently suppressed."""
    return bool(record.meta.get(_SUPPRESSION_KEY, False))


def get_suppression_reason(record: RequestRecord) -> str | None:
    """Return the suppression reason, or ``None`` if not set."""
    return record.meta.get(_REASON_KEY)


def filter_suppressed(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only the records that are suppressed."""
    return [r for r in records if is_suppressed(r)]


def filter_unsuppressed(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only the records that are *not* suppressed."""
    return [r for r in records if not is_suppressed(r)]
