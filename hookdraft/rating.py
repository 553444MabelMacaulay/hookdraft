"""Rating support for request records.

Allows assigning a numeric star rating (1–5) to a record,
clear it, retrieve it, and filter records by rating.
"""

from __future__ import annotations

from typing import List, Optional

_MIN_RATING = 1
_MAX_RATING = 5


def _validate_rating(value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Rating must be an integer, got {type(value).__name__}")
    if value < _MIN_RATING or value > _MAX_RATING:
        raise ValueError(
            f"Rating must be between {_MIN_RATING} and {_MAX_RATING}, got {value}"
        )


def set_rating(record: dict, stars: int) -> None:
    """Assign a star rating (1–5) to *record*."""
    _validate_rating(stars)
    record["rating"] = stars


def clear_rating(record: dict) -> None:
    """Remove the rating from *record* if present."""
    record.pop("rating", None)


def get_rating(record: dict) -> Optional[int]:
    """Return the rating for *record*, or ``None`` if unset."""
    return record.get("rating")


def has_rating(record: dict) -> bool:
    """Return ``True`` if *record* has a rating."""
    return "rating" in record


def filter_by_rating(records: List[dict], stars: int) -> List[dict]:
    """Return records whose rating equals *stars*."""
    _validate_rating(stars)
    return [r for r in records if r.get("rating") == stars]


def filter_by_min_rating(records: List[dict], min_stars: int) -> List[dict]:
    """Return records whose rating is >= *min_stars*."""
    _validate_rating(min_stars)
    return [r for r in records if r.get("rating", 0) >= min_stars]
