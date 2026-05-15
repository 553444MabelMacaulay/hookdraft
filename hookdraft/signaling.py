"""Signal management for webhook records.

A signal represents a named event or condition that has been raised
against a record (e.g. 'high-latency', 'auth-failure', 'retry-exhausted').
Multiple signals can be attached to a single record.
"""

from __future__ import annotations

from typing import List, Optional


def _normalise_name(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def raise_signal(record: dict, name: str, detail: Optional[str] = None) -> dict:
    """Attach a named signal to the record. Deduplicates by name."""
    name = _normalise_name(name)
    if not name:
        raise ValueError("Signal name must not be empty.")
    signals: List[dict] = record.setdefault("signals", [])
    for sig in signals:
        if sig["name"] == name:
            if detail is not None:
                sig["detail"] = detail.strip()
            return record
    entry: dict = {"name": name}
    if detail is not None:
        entry["detail"] = detail.strip()
    signals.append(entry)
    return record


def clear_signal(record: dict, name: str) -> dict:
    """Remove a named signal from the record."""
    name = _normalise_name(name)
    record["signals"] = [
        s for s in record.get("signals", []) if s["name"] != name
    ]
    return record


def clear_all_signals(record: dict) -> dict:
    """Remove all signals from the record."""
    record["signals"] = []
    return record


def get_signals(record: dict) -> List[dict]:
    """Return all signals attached to the record."""
    return list(record.get("signals", []))


def has_signal(record: dict, name: str) -> bool:
    """Return True if the named signal is present."""
    name = _normalise_name(name)
    return any(s["name"] == name for s in record.get("signals", []))


def signal_count(record: dict) -> int:
    """Return the number of signals on the record."""
    return len(record.get("signals", []))


def filter_by_signal(records: List[dict], name: str) -> List[dict]:
    """Return records that carry the given signal."""
    name = _normalise_name(name)
    return [r for r in records if has_signal(r, name)]
