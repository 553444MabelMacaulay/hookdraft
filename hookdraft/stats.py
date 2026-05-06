from collections import Counter
from typing import Any

from hookdraft.storage import RequestRecord


def compute_stats(records: list[RequestRecord]) -> dict[str, Any]:
    """Compute summary statistics over a list of RequestRecords."""
    if not records:
        return {
            "total": 0,
            "methods": {},
            "paths": {},
            "status_codes": {},
            "content_types": {},
        }

    methods: Counter = Counter()
    paths: Counter = Counter()
    status_codes: Counter = Counter()
    content_types: Counter = Counter()

    for record in records:
        methods[record.method] += 1
        paths[record.path] += 1
        status_codes[str(record.response_status)] += 1
        ct = record.headers.get("Content-Type") or record.headers.get("content-type") or "unknown"
        # Strip parameters like charset
        ct = ct.split(";")[0].strip()
        content_types[ct] += 1

    return {
        "total": len(records),
        "methods": dict(methods.most_common()),
        "paths": dict(paths.most_common()),
        "status_codes": dict(status_codes.most_common()),
        "content_types": dict(content_types.most_common()),
    }
