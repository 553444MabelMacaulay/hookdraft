"""Quarantine support for request records.

A quarantined record is flagged as potentially unsafe or requiring review
before further processing. An optional reason and quarantine source can
be attached.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from hookdraft.storage import RequestRecord

_QUARANTINE_KEY = "_quarantine"


def _validate_reason(reason: str) -> str:
    stripped = reason.strip()
    if not stripped:
        raise ValueError("Quarantine reason must not be empty or whitespace.")
    return stripped


def quarantine_record(
    record: "RequestRecord",
    reason: str = "unspecified",
    source: str | None = None,
) -> None:
    """Mark a record as quarantined."""
    validated_reason = _validate_reason(reason)
    entry: dict = {"quarantined": True, "reason": validated_reason}
    if source is not None:
        src = source.strip()
        if not src:
            raise ValueError("Quarantine source must not be empty or whitespace.")
        entry["source"] = src.lower()
    record.meta[_QUARANTINE_KEY] = entry


def unquarantine_record(record: "RequestRecord") -> None:
    """Remove quarantine status from a record."""
    record.meta.pop(_QUARANTINE_KEY, None)


def is_quarantined(record: "RequestRecord") -> bool:
    """Return True if the record is currently quarantined."""
    return record.meta.get(_QUARANTINE_KEY, {}).get("quarantined", False)


def get_quarantine_reason(record: "RequestRecord") -> str | None:
    """Return the quarantine reason, or None if not quarantined."""
    entry = record.meta.get(_QUARANTINE_KEY)
    if entry is None:
        return None
    return entry.get("reason")


def get_quarantine_source(record: "RequestRecord") -> str | None:
    """Return the quarantine source, or None if not set."""
    entry = record.meta.get(_QUARANTINE_KEY)
    if entry is None:
        return None
    return entry.get("source")


def filter_quarantined(records: List["RequestRecord"]) -> List["RequestRecord"]:
    """Return only quarantined records."""
    return [r for r in records if is_quarantined(r)]


def filter_unquarantined(records: List["RequestRecord"]) -> List["RequestRecord"]:
    """Return only records that are not quarantined."""
    return [r for r in records if not is_quarantined(r)]
