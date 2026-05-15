"""Disposition — mark a request record with an action disposition (accept, reject, forward, ignore)."""

from __future__ import annotations

from typing import Optional

VALID_DISPOSITIONS = {"accept", "reject", "forward", "ignore"}


def _validate_disposition(value: str) -> str:
    normalised = value.strip().lower()
    if not normalised:
        raise ValueError("Disposition value must not be empty.")
    if normalised not in VALID_DISPOSITIONS:
        raise ValueError(
            f"Invalid disposition '{normalised}'. "
            f"Must be one of: {', '.join(sorted(VALID_DISPOSITIONS))}."
        )
    return normalised


def set_disposition(record: dict, disposition: str, reason: Optional[str] = None) -> None:
    """Set the disposition on a record, optionally with a reason."""
    normalised = _validate_disposition(disposition)
    stripped_reason = reason.strip() if reason else None
    if stripped_reason == "":
        stripped_reason = None
    record["disposition"] = {
        "value": normalised,
        "reason": stripped_reason,
    }


def clear_disposition(record: dict) -> None:
    """Remove any disposition from the record."""
    record.pop("disposition", None)


def get_disposition(record: dict) -> Optional[dict]:
    """Return the disposition dict or None if not set."""
    return record.get("disposition")


def get_disposition_value(record: dict) -> Optional[str]:
    """Return just the disposition string value, or None."""
    d = record.get("disposition")
    return d["value"] if d else None


def has_disposition(record: dict) -> bool:
    """Return True if the record has a disposition set."""
    return "disposition" in record


def filter_by_disposition(records: list, disposition: str) -> list:
    """Return records whose disposition matches the given value."""
    normalised = _validate_disposition(disposition)
    return [r for r in records if get_disposition_value(r) == normalised]
