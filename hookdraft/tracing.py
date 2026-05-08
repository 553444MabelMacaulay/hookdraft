"""Request tracing: attach a trace context to a record and query by trace."""

from __future__ import annotations

from typing import List, Optional

TRACE_KEY = "trace_id"
SPAN_KEY = "span_id"
PARENT_SPAN_KEY = "parent_span_id"


def set_trace(
    record,
    trace_id: str,
    span_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
) -> None:
    """Attach trace context to *record*."""
    trace_id = trace_id.strip()
    if not trace_id:
        raise ValueError("trace_id must not be empty")
    record.meta[TRACE_KEY] = trace_id
    if span_id is not None:
        span_id = span_id.strip()
        if not span_id:
            raise ValueError("span_id must not be empty when provided")
        record.meta[SPAN_KEY] = span_id
    if parent_span_id is not None:
        parent_span_id = parent_span_id.strip()
        if not parent_span_id:
            raise ValueError("parent_span_id must not be empty when provided")
        record.meta[PARENT_SPAN_KEY] = parent_span_id


def clear_trace(record) -> None:
    """Remove all trace context from *record*."""
    for key in (TRACE_KEY, SPAN_KEY, PARENT_SPAN_KEY):
        record.meta.pop(key, None)


def get_trace(record) -> dict:
    """Return a dict with the trace context fields present on *record*."""
    result = {}
    for key in (TRACE_KEY, SPAN_KEY, PARENT_SPAN_KEY):
        if key in record.meta:
            result[key] = record.meta[key]
    return result


def has_trace(record) -> bool:
    """Return True if *record* has a trace_id set."""
    return TRACE_KEY in record.meta


def filter_by_trace_id(records: List, trace_id: str) -> List:
    """Return records whose trace_id matches *trace_id* (case-insensitive)."""
    needle = trace_id.strip().lower()
    return [r for r in records if r.meta.get(TRACE_KEY, "").lower() == needle]


def group_by_trace_id(records: List) -> dict:
    """Group *records* by trace_id; records without a trace are omitted."""
    groups: dict = {}
    for r in records:
        tid = r.meta.get(TRACE_KEY)
        if tid:
            groups.setdefault(tid, []).append(r)
    return groups
