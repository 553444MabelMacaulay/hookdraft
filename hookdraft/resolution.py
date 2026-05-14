"""Resolution tracking for webhook requests.

Allows marking a request as resolved or unresolved, storing who resolved it
and an optional resolution note.
"""

from __future__ import annotations
from typing import Optional

_RESOLUTION_KEY = "_resolution"


def _validate_resolver(resolver: str) -> str:
    resolver = resolver.strip()
    if not resolver:
        raise ValueError("resolver must not be empty")
    return resolver.lower()


def resolve_record(
    record,
    resolver: str,
    note: Optional[str] = None,
) -> None:
    """Mark a record as resolved by *resolver* with an optional *note*."""
    resolver = _validate_resolver(resolver)
    entry = {"resolved": True, "resolver": resolver, "note": None}
    if note is not None:
        note = note.strip()
        if not note:
            raise ValueError("resolution note must not be empty or whitespace")
        entry["note"] = note
    record.meta[_RESOLUTION_KEY] = entry


def unresolve_record(record) -> None:
    """Remove the resolution status from *record*."""
    record.meta.pop(_RESOLUTION_KEY, None)


def is_resolved(record) -> bool:
    """Return True if *record* has been resolved."""
    return record.meta.get(_RESOLUTION_KEY, {}).get("resolved", False)


def get_resolution(record) -> Optional[dict]:
    """Return the resolution dict or None if not resolved."""
    return record.meta.get(_RESOLUTION_KEY)


def get_resolver(record) -> Optional[str]:
    """Return the resolver username or None."""
    entry = record.meta.get(_RESOLUTION_KEY)
    return entry["resolver"] if entry else None


def filter_resolved(records):
    """Return only resolved records."""
    return [r for r in records if is_resolved(r)]


def filter_unresolved(records):
    """Return only unresolved records."""
    return [r for r in records if not is_resolved(r)]
