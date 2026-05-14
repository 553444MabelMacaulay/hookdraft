"""Visibility control for request records.

Supports setting a visibility level (public, internal, private) on a record,
allowing consumers to filter or display records based on access context.
"""

from __future__ import annotations

VISIBILITY_LEVELS = ("public", "internal", "private")
_DEFAULT = "public"


def _validate_level(level: str) -> str:
    normalised = level.strip().lower()
    if normalised not in VISIBILITY_LEVELS:
        raise ValueError(
            f"Invalid visibility level {level!r}. Must be one of: {', '.join(VISIBILITY_LEVELS)}"
        )
    return normalised


def set_visibility(record: dict, level: str) -> dict:
    """Set the visibility level on *record*. Returns the record."""
    record["visibility"] = _validate_level(level)
    return record


def clear_visibility(record: dict) -> dict:
    """Remove the visibility field, resetting to the implicit default."""
    record.pop("visibility", None)
    return record


def get_visibility(record: dict) -> str:
    """Return the current visibility level, defaulting to 'public'."""
    return record.get("visibility", _DEFAULT)


def is_visible_to(record: dict, context: str) -> bool:
    """Return True if the record is visible in *context*.

    Hierarchy: public < internal < private
    A 'public' record is visible to all contexts.
    An 'internal' record is visible to 'internal' and 'private' contexts.
    A 'private' record is only visible to 'private' contexts.
    """
    context = _validate_level(context)
    level = get_visibility(record)
    order = {v: i for i, v in enumerate(VISIBILITY_LEVELS)}
    return order[context] >= order[level]


def filter_by_visibility(records: list[dict], level: str) -> list[dict]:
    """Return records whose visibility exactly matches *level*."""
    normalised = _validate_level(level)
    return [r for r in records if get_visibility(r) == normalised]


def filter_visible_to(records: list[dict], context: str) -> list[dict]:
    """Return records that are visible within *context*."""
    return [r for r in records if is_visible_to(r, context)]
