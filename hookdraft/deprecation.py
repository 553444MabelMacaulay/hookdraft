"""Deprecation tracking for request records."""

from __future__ import annotations

from typing import Optional

_VALID_REASONS = {"sunset", "replaced", "obsolete", "experimental", "other"}


def _validate_reason(reason: str) -> str:
    reason = reason.strip().lower()
    if not reason:
        raise ValueError("Deprecation reason must not be empty.")
    if reason not in _VALID_REASONS:
        raise ValueError(
            f"Invalid reason {reason!r}. Must be one of: {sorted(_VALID_REASONS)}."
        )
    return reason


def deprecate_record(
    record,
    reason: str = "other",
    note: Optional[str] = None,
) -> None:
    """Mark a record as deprecated with an optional explanatory note."""
    validated = _validate_reason(reason)
    meta = record.setdefault("deprecation", {})
    meta["deprecated"] = True
    meta["reason"] = validated
    meta["note"] = note.strip() if note and note.strip() else None


def undeprecate_record(record) -> None:
    """Remove deprecation status from a record."""
    record.pop("deprecation", None)


def is_deprecated(record) -> bool:
    """Return True if the record has been marked deprecated."""
    return bool(record.get("deprecation", {}).get("deprecated", False))


def get_deprecation(record) -> Optional[dict]:
    """Return the full deprecation metadata dict, or None."""
    dep = record.get("deprecation")
    return dep if dep and dep.get("deprecated") else None


def filter_deprecated(records: list) -> list:
    """Return only records that are deprecated."""
    return [r for r in records if is_deprecated(r)]


def filter_undeprecated(records: list) -> list:
    """Return only records that are not deprecated."""
    return [r for r in records if not is_deprecated(r)]
