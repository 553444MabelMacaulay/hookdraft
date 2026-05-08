"""Priority management for request records."""

from __future__ import annotations

LEVELS = ("low", "normal", "high", "critical")
_LEVEL_ORDER = {level: idx for idx, level in enumerate(LEVELS)}


def _validate_level(level: str) -> str:
    normalised = level.strip().lower()
    if normalised not in _LEVEL_ORDER:
        raise ValueError(
            f"Invalid priority level {level!r}. Must be one of: {', '.join(LEVELS)}"
        )
    return normalised


def set_priority(record, level: str) -> None:
    """Set the priority level on a record."""
    record.meta["priority"] = _validate_level(level)


def clear_priority(record) -> None:
    """Remove the priority from a record."""
    record.meta.pop("priority", None)


def get_priority(record) -> str | None:
    """Return the priority level, or None if not set."""
    return record.meta.get("priority")


def filter_by_priority(records, level: str):
    """Return records matching the given priority level exactly."""
    normalised = _validate_level(level)
    return [r for r in records if get_priority(r) == normalised]


def filter_by_min_priority(records, min_level: str):
    """Return records whose priority is >= min_level."""
    min_idx = _LEVEL_ORDER[_validate_level(min_level)]
    return [
        r for r in records
        if get_priority(r) is not None and _LEVEL_ORDER[get_priority(r)] >= min_idx
    ]


def sort_by_priority(records, descending: bool = True):
    """Sort records by priority level. Unset records go last."""
    def _key(r):
        p = get_priority(r)
        return _LEVEL_ORDER.get(p, -1) if p is not None else -1

    return sorted(records, key=_key, reverse=descending)
