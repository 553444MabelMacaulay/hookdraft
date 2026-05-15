"""Narration: attach a human-readable summary/description to a request record."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hookdraft.storage import RequestRecord

_KEY = "narration"
_MAX_LENGTH = 2000


def _validate_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("Narration text must not be empty or whitespace.")
    if len(text) > _MAX_LENGTH:
        raise ValueError(
            f"Narration text must not exceed {_MAX_LENGTH} characters "
            f"(got {len(text)})."
        )
    return text


def set_narration(record: "RequestRecord", text: str, author: str | None = None) -> None:
    """Attach a narration to *record*, optionally recording the *author*."""
    text = _validate_text(text)
    entry: dict = {"text": text}
    if author is not None:
        author = author.strip()
        if not author:
            raise ValueError("Author must not be empty or whitespace.")
        entry["author"] = author.lower()
    record.metadata[_KEY] = entry


def clear_narration(record: "RequestRecord") -> None:
    """Remove the narration from *record* if present."""
    record.metadata.pop(_KEY, None)


def get_narration(record: "RequestRecord") -> dict | None:
    """Return the narration dict, or *None* if not set."""
    return record.metadata.get(_KEY)


def has_narration(record: "RequestRecord") -> bool:
    """Return *True* if *record* has a narration attached."""
    return _KEY in record.metadata


def get_narration_text(record: "RequestRecord") -> str | None:
    """Convenience helper – return only the text portion, or *None*."""
    entry = get_narration(record)
    return entry["text"] if entry else None


def filter_narrated(records: list["RequestRecord"]) -> list["RequestRecord"]:
    """Return only records that have a narration."""
    return [r for r in records if has_narration(r)]
