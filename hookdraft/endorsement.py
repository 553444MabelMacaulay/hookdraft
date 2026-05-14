"""Endorsement module — allow records to be endorsed (upvoted) by named users."""

from __future__ import annotations

from typing import List


def _normalise_user(user: str) -> str:
    user = user.strip().lower()
    if not user:
        raise ValueError("Endorser name must not be empty.")
    if len(user) > 64:
        raise ValueError("Endorser name must not exceed 64 characters.")
    return user


def endorse_record(record, user: str) -> None:
    """Add *user* as an endorser of *record*. Duplicate endorsements are ignored."""
    user = _normalise_user(user)
    endorsements: List[str] = record.meta.setdefault("endorsements", [])
    if user not in endorsements:
        endorsements.append(user)


def unendorse_record(record, user: str) -> None:
    """Remove *user* from the endorsers of *record*. No-op if not present."""
    user = _normalise_user(user)
    endorsements: List[str] = record.meta.get("endorsements", [])
    record.meta["endorsements"] = [e for e in endorsements if e != user]


def get_endorsements(record) -> List[str]:
    """Return the list of endorsers for *record*."""
    return list(record.meta.get("endorsements", []))


def endorsement_count(record) -> int:
    """Return the number of endorsements on *record*."""
    return len(record.meta.get("endorsements", []))


def has_endorsement(record, user: str) -> bool:
    """Return True if *user* has endorsed *record*."""
    user = _normalise_user(user)
    return user in record.meta.get("endorsements", [])


def filter_endorsed(records, min_count: int = 1):
    """Yield records that have at least *min_count* endorsements."""
    for rec in records:
        if endorsement_count(rec) >= min_count:
            yield rec


def filter_endorsed_by(records, user: str):
    """Yield records endorsed by *user*."""
    user = _normalise_user(user)
    for rec in records:
        if user in rec.meta.get("endorsements", []):
            yield rec
