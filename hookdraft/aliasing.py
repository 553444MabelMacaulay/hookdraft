"""Aliasing — attach a human-friendly alias to a request record."""

from __future__ import annotations

from typing import Optional

_ALIAS_KEY = "_alias"
_MAX_ALIAS_LENGTH = 80


def _validate_alias(alias: str) -> str:
    alias = alias.strip()
    if not alias:
        raise ValueError("Alias must not be empty or whitespace-only.")
    if len(alias) > _MAX_ALIAS_LENGTH:
        raise ValueError(
            f"Alias must be {_MAX_ALIAS_LENGTH} characters or fewer; "
            f"got {len(alias)}."
        )
    return alias


def set_alias(record: dict, alias: str) -> None:
    """Attach *alias* to *record*, overwriting any existing alias."""
    record[_ALIAS_KEY] = _validate_alias(alias)


def clear_alias(record: dict) -> None:
    """Remove the alias from *record* (no-op if not set)."""
    record.pop(_ALIAS_KEY, None)


def get_alias(record: dict) -> Optional[str]:
    """Return the alias for *record*, or ``None`` if not set."""
    return record.get(_ALIAS_KEY)


def has_alias(record: dict) -> bool:
    """Return ``True`` if *record* has an alias."""
    return _ALIAS_KEY in record


def filter_by_alias(records: list[dict], alias: str) -> list[dict]:
    """Return records whose alias equals *alias* (case-insensitive)."""
    needle = alias.strip().lower()
    return [
        r for r in records
        if get_alias(r) is not None and get_alias(r).lower() == needle
    ]


def find_by_alias(records: list[dict], alias: str) -> Optional[dict]:
    """Return the first record matching *alias*, or ``None``."""
    matches = filter_by_alias(records, alias)
    return matches[0] if matches else None
