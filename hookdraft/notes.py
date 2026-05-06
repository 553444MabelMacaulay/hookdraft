"""Per-request notes/annotations module."""

from typing import Optional


def set_note(record: dict, note: str) -> dict:
    """Set a free-text note on a request record dict."""
    if not isinstance(note, str):
        raise TypeError("note must be a string")
    note = note.strip()
    if not note:
        raise ValueError("note must not be empty or whitespace")
    record["note"] = note
    return record


def clear_note(record: dict) -> dict:
    """Remove the note from a request record dict."""
    record.pop("note", None)
    return record


def get_note(record: dict) -> Optional[str]:
    """Return the note attached to a record, or None."""
    return record.get("note")


def filter_by_note(records: list, substring: str) -> list:
    """Return records whose note contains *substring* (case-insensitive)."""
    if not substring:
        raise ValueError("substring must not be empty")
    lower = substring.lower()
    return [
        r for r in records
        if r.get("note") and lower in r["note"].lower()
    ]
