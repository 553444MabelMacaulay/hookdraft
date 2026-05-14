"""Acknowledgement tracking for request records."""

from datetime import datetime, timezone

_KEY = "acknowledgement"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def acknowledge_record(record, acknowledged_by: str = None, note: str = None) -> None:
    """Mark a record as acknowledged, optionally with a user and note."""
    if acknowledged_by is not None:
        acknowledged_by = acknowledged_by.strip().lower()
        if not acknowledged_by:
            raise ValueError("acknowledged_by must not be empty or whitespace")

    if note is not None:
        note = note.strip()
        if not note:
            raise ValueError("note must not be empty or whitespace")

    record.meta[_KEY] = {
        "acknowledged": True,
        "acknowledged_at": _now_iso(),
        "acknowledged_by": acknowledged_by,
        "note": note,
    }


def unacknowledge_record(record) -> None:
    """Remove acknowledgement from a record."""
    record.meta.pop(_KEY, None)


def is_acknowledged(record) -> bool:
    """Return True if the record has been acknowledged."""
    return record.meta.get(_KEY, {}).get("acknowledged", False)


def get_acknowledgement(record) -> dict | None:
    """Return the full acknowledgement dict, or None if not set."""
    return record.meta.get(_KEY)


def filter_acknowledged(records) -> list:
    """Return only acknowledged records."""
    return [r for r in records if is_acknowledged(r)]


def filter_unacknowledged(records) -> list:
    """Return only unacknowledged records."""
    return [r for r in records if not is_acknowledged(r)]
