"""Pinning support — mark requests as pinned so they are not pruned."""

from __future__ import annotations

from typing import List

from hookdraft.storage import RequestRecord


def pin_record(record: RequestRecord) -> RequestRecord:
    """Mark a record as pinned. Returns the modified record."""
    record.meta["pinned"] = True
    return record


def unpin_record(record: RequestRecord) -> RequestRecord:
    """Remove the pinned mark from a record. Returns the modified record."""
    record.meta.pop("pinned", None)
    return record


def is_pinned(record: RequestRecord) -> bool:
    """Return True if the record is currently pinned."""
    return bool(record.meta.get("pinned", False))


def filter_pinned(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only the records that are pinned."""
    return [r for r in records if is_pinned(r)]


def filter_unpinned(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only the records that are NOT pinned."""
    return [r for r in records if not is_pinned(r)]
