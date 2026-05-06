"""Bookmark (favourite) management for request records."""

from __future__ import annotations

from typing import List

from hookdraft.storage import RequestRecord

_BOOKMARK_KEY = "bookmarked"


def bookmark_record(record: RequestRecord) -> RequestRecord:
    """Mark a record as bookmarked."""
    record.meta[_BOOKMARK_KEY] = True
    return record


def unbookmark_record(record: RequestRecord) -> RequestRecord:
    """Remove the bookmark flag from a record."""
    record.meta.pop(_BOOKMARK_KEY, None)
    return record


def is_bookmarked(record: RequestRecord) -> bool:
    """Return True if the record is bookmarked."""
    return bool(record.meta.get(_BOOKMARK_KEY, False))


def filter_bookmarked(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only bookmarked records."""
    return [r for r in records if is_bookmarked(r)]


def filter_unbookmarked(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are NOT bookmarked."""
    return [r for r in records if not is_bookmarked(r)]
