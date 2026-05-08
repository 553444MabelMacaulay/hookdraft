"""Snapshot support: capture and compare named snapshots of request payloads."""

from __future__ import annotations

from typing import Optional

from hookdraft.storage import RequestRecord

_SNAPSHOT_KEY = "snapshots"


def save_snapshot(record: RequestRecord, name: str) -> None:
    """Save the current body of *record* under *name*."""
    name = name.strip()
    if not name:
        raise ValueError("Snapshot name must not be empty.")
    snapshots = record.meta.setdefault(_SNAPSHOT_KEY, {})
    snapshots[name] = record.body


def delete_snapshot(record: RequestRecord, name: str) -> bool:
    """Remove snapshot *name* from *record*. Returns True if it existed."""
    snapshots = record.meta.get(_SNAPSHOT_KEY, {})
    if name in snapshots:
        del snapshots[name]
        return True
    return False


def get_snapshot(record: RequestRecord, name: str) -> Optional[object]:
    """Return the stored payload for *name*, or None if absent."""
    return record.meta.get(_SNAPSHOT_KEY, {}).get(name)


def list_snapshots(record: RequestRecord) -> list[str]:
    """Return all snapshot names for *record*, sorted."""
    return sorted(record.meta.get(_SNAPSHOT_KEY, {}).keys())


def has_snapshot(record: RequestRecord, name: str) -> bool:
    """Return True if *name* exists in *record*'s snapshots."""
    return name in record.meta.get(_SNAPSHOT_KEY, {})
