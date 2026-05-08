"""Highlighting — mark records with a highlight colour for visual callouts."""

from __future__ import annotations

from typing import List, Optional

from hookdraft.storage import RequestRecord

_VALID_COLOURS = {"yellow", "green", "blue", "red", "orange", "purple"}
_DEFAULT_COLOUR = "yellow"


def set_highlight(record: RequestRecord, colour: Optional[str] = None) -> None:
    """Highlight *record* with *colour* (default: yellow).

    Raises ValueError for unrecognised colour names.
    """
    chosen = (colour or _DEFAULT_COLOUR).strip().lower()
    if not chosen:
        raise ValueError("Highlight colour must not be empty.")
    if chosen not in _VALID_COLOURS:
        raise ValueError(
            f"Unknown highlight colour {chosen!r}. "
            f"Valid options: {sorted(_VALID_COLOURS)}"
        )
    record.meta["highlight"] = chosen


def clear_highlight(record: RequestRecord) -> None:
    """Remove any highlight from *record*."""
    record.meta.pop("highlight", None)


def get_highlight(record: RequestRecord) -> Optional[str]:
    """Return the highlight colour for *record*, or *None* if not set."""
    return record.meta.get("highlight")


def is_highlighted(record: RequestRecord) -> bool:
    """Return True if *record* has a highlight colour set."""
    return "highlight" in record.meta


def filter_highlighted(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that have a highlight set."""
    return [r for r in records if is_highlighted(r)]


def filter_by_highlight_colour(
    records: List[RequestRecord], colour: str
) -> List[RequestRecord]:
    """Return records whose highlight colour matches *colour* (case-insensitive)."""
    target = colour.strip().lower()
    return [r for r in records if get_highlight(r) == target]
