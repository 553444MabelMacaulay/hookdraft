"""Label (colour-coded category) support for request records."""

from __future__ import annotations

VALID_COLOURS = {"red", "green", "blue", "yellow", "purple", "orange", "grey"}


def set_label(record: dict, name: str, colour: str = "grey") -> dict:
    """Attach a named label with an optional colour to a record."""
    name = name.strip().lower()
    if not name:
        raise ValueError("Label name must not be empty.")
    colour = colour.strip().lower()
    if colour not in VALID_COLOURS:
        raise ValueError(f"Colour must be one of {sorted(VALID_COLOURS)}.")
    labels = record.setdefault("labels", {})
    labels[name] = colour
    return record


def remove_label(record: dict, name: str) -> dict:
    """Remove a label from a record (idempotent)."""
    name = name.strip().lower()
    record.setdefault("labels", {}).pop(name, None)
    return record


def get_labels(record: dict) -> dict:
    """Return the labels dict for a record (may be empty)."""
    return dict(record.get("labels", {}))


def filter_by_label(records: list, name: str) -> list:
    """Return records that have the given label (any colour)."""
    name = name.strip().lower()
    return [r for r in records if name in r.get("labels", {})]


def filter_by_label_colour(records: list, colour: str) -> list:
    """Return records that have at least one label with the given colour."""
    colour = colour.strip().lower()
    return [r for r in records if colour in r.get("labels", {}).values()]
