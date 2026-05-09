"""Annotation support for request records.

Annotations are timestamped, authored comments attached to a record,
distinct from the single free-text note already supported.
"""

from __future__ import annotations

import time
from typing import List, Optional


def _validate_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("Annotation text must not be empty or whitespace.")
    return text


def add_annotation(
    record: dict,
    text: str,
    author: str = "anonymous",
) -> dict:
    """Append a new annotation to the record and return it."""
    text = _validate_text(text)
    author = author.strip() or "anonymous"
    annotations = record.setdefault("annotations", [])
    entry = {
        "text": text,
        "author": author,
        "timestamp": time.time(),
    }
    annotations.append(entry)
    return entry


def remove_annotation(record: dict, index: int) -> None:
    """Remove annotation at *index* (0-based). Raises IndexError if out of range."""
    annotations = record.get("annotations", [])
    if index < 0 or index >= len(annotations):
        raise IndexError(f"No annotation at index {index}.")
    annotations.pop(index)


def get_annotations(record: dict) -> List[dict]:
    """Return all annotations attached to the record."""
    return list(record.get("annotations", []))


def has_annotations(record: dict) -> bool:
    """Return True if the record has at least one annotation."""
    return bool(record.get("annotations"))


def filter_by_author(records: List[dict], author: str) -> List[dict]:
    """Return records that have at least one annotation by *author*."""
    author = author.strip().lower()
    return [
        r for r in records
        if any(a["author"].lower() == author for a in r.get("annotations", []))
    ]
