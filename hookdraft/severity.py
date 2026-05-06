"""Severity levels for webhook requests (info, warning, error)."""

from __future__ import annotations

VALID_LEVELS = {"info", "warning", "error"}


def set_severity(record, level: str) -> None:
    """Assign a severity level to a request record."""
    level = level.strip().lower()
    if not level:
        raise ValueError("Severity level must not be empty.")
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid severity level '{level}'. Must be one of: {sorted(VALID_LEVELS)}"
        )
    record.meta["severity"] = level


def clear_severity(record) -> None:
    """Remove the severity level from a request record."""
    record.meta.pop("severity", None)


def get_severity(record) -> str | None:
    """Return the severity level of a record, or None if not set."""
    return record.meta.get("severity")


def filter_by_severity(records, level: str):
    """Return records that match the given severity level."""
    level = level.strip().lower()
    return [r for r in records if r.meta.get("severity") == level]


def filter_by_min_severity(records, min_level: str):
    """Return records at or above the given minimum severity level."""
    order = ["info", "warning", "error"]
    if min_level not in order:
        raise ValueError(f"Invalid min_level '{min_level}'.")
    threshold = order.index(min_level)
    return [
        r for r in records
        if r.meta.get("severity") in order[threshold:]
    ]
