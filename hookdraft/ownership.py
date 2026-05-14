"""Ownership tracking for webhook request records."""

from __future__ import annotations

from typing import List, Optional

_UNSET = object()


def _validate_owner(owner: str) -> str:
    if not isinstance(owner, str):
        raise TypeError("owner must be a string")
    owner = owner.strip().lower()
    if not owner:
        raise ValueError("owner must not be empty")
    if " " in owner:
        raise ValueError("owner must not contain spaces")
    return owner


def set_owner(record: dict, owner: str, team: Optional[str] = None) -> None:
    """Assign an owner (and optionally a team) to a record."""
    owner = _validate_owner(owner)
    record.setdefault("_ownership", {})
    record["_ownership"]["owner"] = owner
    if team is not None:
        team = team.strip().lower()
        if not team:
            raise ValueError("team must not be empty if provided")
        record["_ownership"]["team"] = team
    else:
        record["_ownership"].setdefault("team", None)


def clear_owner(record: dict) -> None:
    """Remove ownership information from a record."""
    record.pop("_ownership", None)


def get_owner(record: dict) -> Optional[str]:
    """Return the owner of a record, or None."""
    return record.get("_ownership", {}).get("owner")


def get_team(record: dict) -> Optional[str]:
    """Return the team assigned to a record, or None."""
    return record.get("_ownership", {}).get("team")


def is_owned(record: dict) -> bool:
    """Return True if the record has an owner set."""
    return get_owner(record) is not None


def filter_by_owner(records: List[dict], owner: str) -> List[dict]:
    """Return only records owned by the given owner."""
    owner = owner.strip().lower()
    return [r for r in records if get_owner(r) == owner]


def filter_by_team(records: List[dict], team: str) -> List[dict]:
    """Return only records belonging to the given team."""
    team = team.strip().lower()
    return [r for r in records if get_team(r) == team]
