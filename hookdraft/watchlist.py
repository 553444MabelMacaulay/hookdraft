"""Watchlist: mark records as watched/unwatched and filter by watch status."""

from __future__ import annotations

from typing import List

_WATCHED_KEY = "_watched"
_WATCH_REASON_KEY = "_watch_reason"


def watch_record(record, reason: str = "") -> None:
    """Mark a record as watched, with an optional reason."""
    reason = reason.strip()
    record.meta[_WATCHED_KEY] = True
    record.meta[_WATCH_REASON_KEY] = reason if reason else None


def unwatch_record(record) -> None:
    """Remove the watched flag and reason from a record."""
    record.meta.pop(_WATCHED_KEY, None)
    record.meta.pop(_WATCH_REASON_KEY, None)


def is_watched(record) -> bool:
    """Return True if the record is currently watched."""
    return bool(record.meta.get(_WATCHED_KEY, False))


def get_watch_reason(record) -> str | None:
    """Return the watch reason, or None if not set."""
    return record.meta.get(_WATCH_REASON_KEY)


def filter_watched(records: List) -> List:
    """Return only watched records."""
    return [r for r in records if is_watched(r)]


def filter_unwatched(records: List) -> List:
    """Return only unwatched records."""
    return [r for r in records if not is_watched(r)]
