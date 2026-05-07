"""Group and bucket request records by various fields."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from hookdraft.storage import RequestRecord

_VALID_FIELDS = {"method", "path", "status_code", "content_type"}


def _get_field(record: RequestRecord, field: str) -> str:
    """Extract a grouping key from a record."""
    if field == "method":
        return (record.method or "UNKNOWN").upper()
    if field == "path":
        return record.path or "/"
    if field == "status_code":
        return str(record.response_status or "none")
    if field == "content_type":
        raw = (record.headers or {}).get("content-type") or ""
        # strip charset / parameters
        return raw.split(";")[0].strip().lower() or "unknown"
    raise ValueError(f"Unknown grouping field: {field!r}")


def group_records(
    records: List[RequestRecord],
    field: str,
) -> Dict[str, List[RequestRecord]]:
    """Return a dict mapping field values to lists of matching records."""
    if field not in _VALID_FIELDS:
        raise ValueError(
            f"Invalid grouping field {field!r}. "
            f"Must be one of: {sorted(_VALID_FIELDS)}"
        )
    groups: Dict[str, List[RequestRecord]] = defaultdict(list)
    for record in records:
        key = _get_field(record, field)
        groups[key].append(record)
    return dict(groups)


def group_summary(
    records: List[RequestRecord],
    field: str,
) -> Dict[str, int]:
    """Return a dict mapping field values to counts."""
    return {k: len(v) for k, v in group_records(records, field).items()}
