"""Utility helpers for serialising RequestRecord collections."""
import json
import csv
import io
from typing import List

from hookdraft.storage import RequestRecord


def records_to_json(records: List[RequestRecord], indent: int = 2) -> str:
    """Serialise a list of RequestRecord objects to a JSON string."""
    return json.dumps([r.to_dict() for r in records], indent=indent)


def records_to_csv(records: List[RequestRecord]) -> str:
    """Serialise a list of RequestRecord objects to a CSV string.

    Complex fields (headers, body) are JSON-encoded within each cell.
    """
    fieldnames = ["id", "timestamp", "method", "path", "headers", "body"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for record in records:
        row = record.to_dict()
        row["headers"] = json.dumps(row.get("headers", {}))
        body = row.get("body")
        row["body"] = json.dumps(body) if body is not None else ""
        writer.writerow(row)

    return output.getvalue()
