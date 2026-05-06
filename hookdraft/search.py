from __future__ import annotations
from typing import List, Optional
from hookdraft.storage import RequestRecord


def filter_records(
    records: List[RequestRecord],
    method: Optional[str] = None,
    path_contains: Optional[str] = None,
    header_key: Optional[str] = None,
    header_value: Optional[str] = None,
    body_contains: Optional[str] = None,
    limit: int = 50,
) -> List[RequestRecord]:
    """
    Filter a list of RequestRecord objects based on optional criteria.

    Args:
        records: Full list of records to search through.
        method: Exact HTTP method match (case-insensitive).
        path_contains: Substring to look for in the request path.
        header_key: Header name that must be present (case-insensitive).
        header_value: Header value that must match the given header_key.
        body_contains: Substring to look for in the raw body.
        limit: Maximum number of results to return.

    Returns:
        Filtered list of records, most recent first, up to `limit` items.
    """
    results = []
    for record in records:
        if method and record.method.upper() != method.upper():
            continue

        if path_contains and path_contains.lower() not in record.path.lower():
            continue

        if header_key:
            lowered = {k.lower(): v for k, v in record.headers.items()}
            key_lower = header_key.lower()
            if key_lower not in lowered:
                continue
            if header_value and lowered[key_lower] != header_value:
                continue

        if body_contains:
            body_str = record.body if isinstance(record.body, str) else ""
            if body_contains.lower() not in body_str.lower():
                continue

        results.append(record)

        if len(results) >= limit:
            break

    return results
