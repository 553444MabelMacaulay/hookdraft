"""Delegation: assign a record to a responsible owner/team."""

from __future__ import annotations

from typing import List, Optional

_MAX_OWNER_LEN = 64


def _validate_owner(owner: str) -> str:
    owner = owner.strip()
    if not owner:
        raise ValueError("owner must not be empty")
    if len(owner) > _MAX_OWNER_LEN:
        raise ValueError(f"owner must be {_MAX_OWNER_LEN} characters or fewer")
    return owner.lower()


def delegate_record(record, owner: str, note: Optional[str] = None) -> None:
    """Assign *record* to *owner* with an optional delegation note."""
    owner = _validate_owner(owner)
    note_text = note.strip() if note else None
    if note_text == "":
        note_text = None
    record.metadata["delegation"] = {"owner": owner, "note": note_text}


def undelegate_record(record) -> None:
    """Remove delegation from *record*."""
    record.metadata.pop("delegation", None)


def get_delegation(record) -> Optional[dict]:
    """Return the delegation dict or *None* if not delegated."""
    return record.metadata.get("delegation")


def get_owner(record) -> Optional[str]:
    """Return the owner string or *None*."""
    d = get_delegation(record)
    return d["owner"] if d else None


def is_delegated(record) -> bool:
    return "delegation" in record.metadata


def filter_delegated(records: List) -> List:
    return [r for r in records if is_delegated(r)]


def filter_by_owner(records: List, owner: str) -> List:
    owner = owner.strip().lower()
    return [r for r in records if get_owner(r) == owner]
