"""Attribution: track the source/origin of a webhook request."""

from __future__ import annotations

from typing import Optional

_ATTR_KEY = "_attribution"

_VALID_SOURCES = {"manual", "automated", "scheduled", "external", "internal", "unknown"}


def _validate_source(source: str) -> str:
    source = source.strip().lower()
    if not source:
        raise ValueError("Attribution source must not be empty.")
    if source not in _VALID_SOURCES:
        raise ValueError(
            f"Invalid source {source!r}. Must be one of: {sorted(_VALID_SOURCES)}"
        )
    return source


def set_attribution(record, source: str, actor: Optional[str] = None, note: Optional[str] = None) -> None:
    """Attach attribution metadata to a record."""
    source = _validate_source(source)
    actor_val = actor.strip().lower() if actor and actor.strip() else None
    note_val = note.strip() if note and note.strip() else None
    record.meta[_ATTR_KEY] = {
        "source": source,
        "actor": actor_val,
        "note": note_val,
    }


def clear_attribution(record) -> None:
    """Remove attribution metadata from a record."""
    record.meta.pop(_ATTR_KEY, None)


def get_attribution(record) -> Optional[dict]:
    """Return attribution dict or None."""
    return record.meta.get(_ATTR_KEY)


def has_attribution(record) -> bool:
    return _ATTR_KEY in record.meta


def filter_by_source(records, source: str):
    """Return records attributed to the given source."""
    source = source.strip().lower()
    return [
        r for r in records
        if has_attribution(r) and r.meta[_ATTR_KEY]["source"] == source
    ]


def filter_by_actor(records, actor: str):
    """Return records attributed to the given actor."""
    actor = actor.strip().lower()
    return [
        r for r in records
        if has_attribution(r) and r.meta[_ATTR_KEY].get("actor") == actor
    ]
