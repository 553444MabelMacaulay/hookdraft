"""Flagging support: mark records for follow-up review."""

from __future__ import annotations

from typing import List

from hookdraft.storage import RequestRecord

FLAG_KEY = "flagged"
FLAG_REASON_KEY = "flag_reason"


def flag_record(record: RequestRecord, reason: str = "") -> RequestRecord:
    """Mark a record as flagged, with an optional reason."""
    reason = reason.strip()
    record.meta[FLAG_KEY] = True
    record.meta[FLAG_REASON_KEY] = reason
    return record


def unflag_record(record: RequestRecord) -> RequestRecord:
    """Remove the flagged status from a record."""
    record.meta.pop(FLAG_KEY, None)
    record.meta.pop(FLAG_REASON_KEY, None)
    return record


def is_flagged(record: RequestRecord) -> bool:
    """Return True if the record is currently flagged."""
    return bool(record.meta.get(FLAG_KEY, False))


def get_flag_reason(record: RequestRecord) -> str:
    """Return the flag reason, or an empty string if not set."""
    return record.meta.get(FLAG_REASON_KEY, "")


def filter_flagged(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only flagged records."""
    return [r for r in records if is_flagged(r)]


def filter_unflagged(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are NOT flagged."""
    return [r for r in records if not is_flagged(r)]
