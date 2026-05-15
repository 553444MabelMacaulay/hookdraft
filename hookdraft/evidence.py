"""Evidence attachment for request records.

Evidence items are named proof artefacts (URLs, hashes, descriptions)
that can be attached to a record to support audit or investigation.
"""

from __future__ import annotations

import uuid
from typing import Any


def _validate_kind(kind: str) -> str:
    kind = kind.strip().lower()
    allowed = {"url", "hash", "text", "file"}
    if kind not in allowed:
        raise ValueError(f"kind must be one of {sorted(allowed)}, got {kind!r}")
    return kind


def _validate_content(content: str) -> str:
    content = content.strip()
    if not content:
        raise ValueError("content must not be empty")
    return content


def add_evidence(record: dict, kind: str, content: str, label: str = "") -> str:
    """Attach an evidence item to *record*. Returns the new evidence id."""
    kind = _validate_kind(kind)
    content = _validate_content(content)
    label = label.strip()

    item: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "kind": kind,
        "content": content,
    }
    if label:
        item["label"] = label

    record.setdefault("evidence", []).append(item)
    return item["id"]


def remove_evidence(record: dict, evidence_id: str) -> bool:
    """Remove an evidence item by id. Returns True if removed, False if not found."""
    items: list = record.get("evidence", [])
    for i, item in enumerate(items):
        if item["id"] == evidence_id:
            items.pop(i)
            return True
    return False


def get_evidence(record: dict) -> list[dict]:
    """Return all evidence items attached to *record*."""
    return list(record.get("evidence", []))


def has_evidence(record: dict) -> bool:
    return bool(record.get("evidence"))


def evidence_count(record: dict) -> int:
    return len(record.get("evidence", []))


def filter_by_evidence_kind(records: list[dict], kind: str) -> list[dict]:
    """Return records that have at least one evidence item of *kind*."""
    kind = kind.strip().lower()
    return [
        r for r in records
        if any(e["kind"] == kind for e in r.get("evidence", []))
    ]
