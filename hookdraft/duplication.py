"""Duplication detection and management for request records."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hookdraft.storage import RequestRecord

_SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}


def _body_fingerprint(record: "RequestRecord") -> str:
    """Return a stable string fingerprint for a record's body."""
    body = record.body
    if body is None:
        return ""
    if isinstance(body, dict):
        import json
        return json.dumps(body, sort_keys=True)
    return str(body)


def _header_fingerprint(record: "RequestRecord") -> str:
    """Return a fingerprint of non-sensitive headers."""
    headers = getattr(record, "headers", {}) or {}
    filtered = {
        k.lower(): v
        for k, v in headers.items()
        if k.lower() not in _SENSITIVE_HEADERS
    }
    import json
    return json.dumps(filtered, sort_keys=True)


def compute_fingerprint(record: "RequestRecord") -> str:
    """Compute a deduplication fingerprint for a record."""
    import hashlib
    parts = "|".join([
        (record.method or "").upper(),
        record.path or "",
        _body_fingerprint(record),
        _header_fingerprint(record),
    ])
    return hashlib.sha256(parts.encode()).hexdigest()


def mark_duplicate(record: "RequestRecord", original_id: str) -> None:
    """Mark a record as a duplicate of another record."""
    if not original_id or not original_id.strip():
        raise ValueError("original_id must be a non-empty string")
    record.meta["duplicate_of"] = original_id.strip()
    record.meta["is_duplicate"] = True


def unmark_duplicate(record: "RequestRecord") -> None:
    """Remove duplicate marking from a record."""
    record.meta.pop("duplicate_of", None)
    record.meta.pop("is_duplicate", None)


def is_duplicate(record: "RequestRecord") -> bool:
    """Return True if the record has been marked as a duplicate."""
    return bool(record.meta.get("is_duplicate", False))


def get_original_id(record: "RequestRecord") -> str | None:
    """Return the ID of the original record this is a duplicate of."""
    return record.meta.get("duplicate_of")


def filter_duplicates(records: list) -> list:
    """Return only records that are marked as duplicates."""
    return [r for r in records if is_duplicate(r)]


def filter_originals(records: list) -> list:
    """Return only records that are NOT marked as duplicates."""
    return [r for r in records if not is_duplicate(r)]


def find_duplicates_of(records: list, original_id: str) -> list:
    """Return all records that are duplicates of the given original ID."""
    return [r for r in records if get_original_id(r) == original_id]
