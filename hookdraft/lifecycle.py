"""Lifecycle state tracking for webhook request records."""

from __future__ import annotations

from typing import Optional

_VALID_STATES = {"new", "processing", "processed", "failed", "ignored"}
_STATE_ORDER = ["new", "processing", "processed", "failed", "ignored"]


def _validate_state(state: str) -> str:
    normalised = state.strip().lower()
    if not normalised:
        raise ValueError("Lifecycle state must not be empty.")
    if normalised not in _VALID_STATES:
        raise ValueError(
            f"Unknown lifecycle state '{normalised}'. "
            f"Valid states: {sorted(_VALID_STATES)}"
        )
    return normalised


def set_lifecycle_state(record: dict, state: str, *, actor: Optional[str] = None, note: Optional[str] = None) -> None:
    """Set the lifecycle state of a record."""
    normalised = _validate_state(state)
    entry: dict = {"state": normalised}
    if actor is not None:
        cleaned = actor.strip().lower()
        if not cleaned:
            raise ValueError("Actor must not be empty if provided.")
        entry["actor"] = cleaned
    if note is not None:
        cleaned_note = note.strip()
        if not cleaned_note:
            raise ValueError("Note must not be empty if provided.")
        entry["note"] = cleaned_note
    record["lifecycle"] = entry


def clear_lifecycle_state(record: dict) -> None:
    """Remove lifecycle state from a record."""
    record.pop("lifecycle", None)


def get_lifecycle_state(record: dict) -> Optional[str]:
    """Return the current lifecycle state, or None."""
    lc = record.get("lifecycle")
    return lc["state"] if lc else None


def get_lifecycle_actor(record: dict) -> Optional[str]:
    """Return the actor who set the lifecycle state, or None."""
    lc = record.get("lifecycle")
    return lc.get("actor") if lc else None


def get_lifecycle_note(record: dict) -> Optional[str]:
    """Return the note attached to the lifecycle state, or None."""
    lc = record.get("lifecycle")
    return lc.get("note") if lc else None


def has_lifecycle_state(record: dict) -> bool:
    """Return True if a lifecycle state has been set."""
    return "lifecycle" in record


def filter_by_lifecycle_state(records: list, state: str) -> list:
    """Return records matching the given lifecycle state."""
    normalised = _validate_state(state)
    return [r for r in records if get_lifecycle_state(r) == normalised]


def filter_unlifecycled(records: list) -> list:
    """Return records with no lifecycle state set."""
    return [r for r in records if not has_lifecycle_state(r)]
