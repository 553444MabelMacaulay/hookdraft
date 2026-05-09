"""Mention tracking for webhook request records.

Allows tagging a record with @mentions (user or team handles),
enabling filtering and lookup by mentioned party.
"""

from __future__ import annotations

from typing import List


def _normalise_handle(handle: str) -> str:
    handle = handle.strip().lstrip("@").lower()
    if not handle:
        raise ValueError("Mention handle must not be empty.")
    if " " in handle:
        raise ValueError("Mention handle must not contain spaces.")
    return handle


def add_mention(record: dict, handle: str) -> dict:
    """Add a @mention handle to a record (deduplicated)."""
    handle = _normalise_handle(handle)
    mentions: List[str] = record.setdefault("mentions", [])
    if handle not in mentions:
        mentions.append(handle)
    return record


def remove_mention(record: dict, handle: str) -> dict:
    """Remove a @mention handle from a record (idempotent)."""
    handle = _normalise_handle(handle)
    record["mentions"] = [m for m in record.get("mentions", []) if m != handle]
    return record


def get_mentions(record: dict) -> List[str]:
    """Return all mention handles on a record."""
    return list(record.get("mentions", []))


def has_mention(record: dict, handle: str) -> bool:
    """Return True if a record has the given mention handle."""
    handle = _normalise_handle(handle)
    return handle in record.get("mentions", [])


def filter_by_mention(records: List[dict], handle: str) -> List[dict]:
    """Return records that mention the given handle."""
    handle = _normalise_handle(handle)
    return [r for r in records if handle in r.get("mentions", [])]


def all_mentions(records: List[dict]) -> List[str]:
    """Return a sorted, deduplicated list of all handles used across records."""
    seen = set()
    for r in records:
        seen.update(r.get("mentions", []))
    return sorted(seen)
