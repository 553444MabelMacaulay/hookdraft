"""Correlation ID support for grouping related webhook requests."""

from __future__ import annotations

from typing import List

from hookdraft.storage import RequestRecord

_FIELD = "correlation_id"


def set_correlation_id(record: RequestRecord, correlation_id: str) -> None:
    """Attach a correlation ID to a record."""
    correlation_id = correlation_id.strip()
    if not correlation_id:
        raise ValueError("correlation_id must be a non-empty string")
    record.meta[_FIELD] = correlation_id


def clear_correlation_id(record: RequestRecord) -> None:
    """Remove the correlation ID from a record, if present."""
    record.meta.pop(_FIELD, None)


def get_correlation_id(record: RequestRecord) -> str | None:
    """Return the correlation ID for a record, or None if not set."""
    return record.meta.get(_FIELD)


def filter_by_correlation_id(
    records: List[RequestRecord], correlation_id: str
) -> List[RequestRecord]:
    """Return all records that share the given correlation ID."""
    correlation_id = correlation_id.strip()
    return [r for r in records if r.meta.get(_FIELD) == correlation_id]


def group_by_correlation_id(
    records: List[RequestRecord],
) -> dict[str, List[RequestRecord]]:
    """Group records by correlation ID. Records without one are excluded."""
    groups: dict[str, List[RequestRecord]] = {}
    for record in records:
        cid = record.meta.get(_FIELD)
        if cid is not None:
            groups.setdefault(cid, []).append(record)
    return groups
