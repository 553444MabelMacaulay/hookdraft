"""Timeline: record a sequence of named events against a request record."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional


_KEY = "_timeline"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_event_name(name: str) -> None:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Event name must be a non-empty string.")


def add_event(
    record,
    name: str,
    *,
    detail: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> dict:
    """Append a named event to the record's timeline. Returns the new event."""
    _validate_event_name(name)
    name = name.strip()
    if detail is not None:
        detail = detail.strip() or None
    event = {
        "name": name,
        "timestamp": timestamp or _now_iso(),
    }
    if detail:
        event["detail"] = detail
    timeline = record.__dict__.setdefault(_KEY, [])
    timeline.append(event)
    return event


def get_events(record) -> List[dict]:
    """Return all events for the record (oldest first)."""
    return list(record.__dict__.get(_KEY, []))


def clear_events(record) -> None:
    """Remove all timeline events from the record."""
    record.__dict__.pop(_KEY, None)


def has_events(record) -> bool:
    """Return True if the record has at least one timeline event."""
    return bool(record.__dict__.get(_KEY))


def filter_by_event_name(records, name: str):
    """Return records that contain at least one event with the given name."""
    name = name.strip().lower()
    return [
        r for r in records
        if any(e["name"].lower() == name for e in r.__dict__.get(_KEY, []))
    ]
