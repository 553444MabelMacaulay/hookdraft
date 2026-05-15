"""Workflow state management for request records."""

from __future__ import annotations

from typing import List, Optional

_VALID_STATES = {"pending", "in_review", "approved", "rejected", "closed"}
_TRANSITIONS = {
    "pending": {"in_review", "rejected", "closed"},
    "in_review": {"approved", "rejected", "pending"},
    "approved": {"closed", "in_review"},
    "rejected": {"pending", "closed"},
    "closed": set(),
}


def _validate_state(state: str) -> str:
    normalised = state.strip().lower()
    if normalised not in _VALID_STATES:
        raise ValueError(
            f"Invalid workflow state '{state}'. Must be one of: {sorted(_VALID_STATES)}"
        )
    return normalised


def set_workflow_state(record: dict, state: str, actor: Optional[str] = None, note: Optional[str] = None) -> None:
    """Set the workflow state of a record, enforcing valid transitions."""
    normalised = _validate_state(state)
    current = record.get("_workflow", {}).get("state")
    if current is not None and normalised not in _TRANSITIONS.get(current, set()):
        raise ValueError(
            f"Cannot transition from '{current}' to '{normalised}'."
        )
    entry = {"state": normalised}
    if actor is not None:
        stripped = actor.strip()
        if not stripped:
            raise ValueError("actor must not be empty or whitespace.")
        entry["actor"] = stripped.lower()
    if note is not None:
        stripped_note = note.strip()
        if not stripped_note:
            raise ValueError("note must not be empty or whitespace.")
        entry["note"] = stripped_note
    record["_workflow"] = entry


def clear_workflow_state(record: dict) -> None:
    """Remove workflow state from a record."""
    record.pop("_workflow", None)


def get_workflow_state(record: dict) -> Optional[str]:
    """Return the current workflow state, or None."""
    return record.get("_workflow", {}).get("state")


def get_workflow_actor(record: dict) -> Optional[str]:
    """Return the actor who last changed the workflow state, or None."""
    return record.get("_workflow", {}).get("actor")


def get_workflow_note(record: dict) -> Optional[str]:
    """Return the note attached to the current workflow state, or None."""
    return record.get("_workflow", {}).get("note")


def filter_by_workflow_state(records: List[dict], state: str) -> List[dict]:
    """Return only records matching the given workflow state."""
    normalised = _validate_state(state)
    return [r for r in records if get_workflow_state(r) == normalised]
