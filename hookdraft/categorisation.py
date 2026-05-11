"""Categorisation support for request records.

Allows records to be assigned to named categories with optional
descriptions, making it easier to organise and filter large
collections of captured webhooks.
"""

from __future__ import annotations

from typing import List, Optional

# Maximum length for a category name.
_MAX_NAME_LEN = 64

# Maximum length for a category description.
_MAX_DESC_LEN = 256

# Metadata key used to store the category on a record.
_KEY = "category"


def _validate_name(name: str) -> str:
    """Normalise and validate a category name.

    Strips surrounding whitespace, lower-cases, and ensures the result
    is non-empty and within the permitted length.
    """
    name = name.strip().lower()
    if not name:
        raise ValueError("Category name must not be empty.")
    if len(name) > _MAX_NAME_LEN:
        raise ValueError(
            f"Category name must be {_MAX_NAME_LEN} characters or fewer."
        )
    return name


def set_category(
    record,
    name: str,
    description: Optional[str] = None,
) -> None:
    """Assign *record* to the named category.

    Parameters
    ----------
    record:
        A ``RequestRecord`` instance whose ``meta`` dict will be updated.
    name:
        Human-readable category name (case-insensitive, leading/trailing
        whitespace stripped).
    description:
        Optional free-text description of the category.  Whitespace is
        stripped; passing an empty string or ``None`` stores no description.
    """
    name = _validate_name(name)

    desc: Optional[str] = None
    if description is not None:
        description = description.strip()
        if len(description) > _MAX_DESC_LEN:
            raise ValueError(
                f"Category description must be {_MAX_DESC_LEN} characters or fewer."
            )
        desc = description if description else None

    record.meta[_KEY] = {"name": name, "description": desc}


def clear_category(record) -> None:
    """Remove any category assignment from *record*."""
    record.meta.pop(_KEY, None)


def get_category(record) -> Optional[dict]:
    """Return the category dict for *record*, or ``None`` if unset.

    The returned dict has the shape::

        {"name": str, "description": str | None}
    """
    return record.meta.get(_KEY)


def get_category_name(record) -> Optional[str]:
    """Return just the category name for *record*, or ``None`` if unset."""
    cat = get_category(record)
    return cat["name"] if cat else None


def has_category(record) -> bool:
    """Return ``True`` if *record* has been assigned a category."""
    return _KEY in record.meta


def filter_by_category(records: List, name: str) -> List:
    """Return all records whose category name matches *name* (case-insensitive)."""
    name = name.strip().lower()
    return [
        r for r in records
        if get_category_name(r) == name
    ]


def all_categories(records: List) -> List[str]:
    """Return a sorted list of unique category names found across *records*."""
    names = set()
    for r in records:
        name = get_category_name(r)
        if name:
            names.add(name)
    return sorted(names)
