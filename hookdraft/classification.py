"""Classification module — assign a type/class to a request record."""

from __future__ import annotations

from hookdraft.storage import RequestRecord

_VALID_CLASSES = {
    "webhook",
    "ping",
    "heartbeat",
    "event",
    "alert",
    "notification",
    "command",
    "query",
    "other",
}


def _validate_class(name: str) -> str:
    normalised = name.strip().lower()
    if not normalised:
        raise ValueError("Classification name must not be empty.")
    if normalised not in _VALID_CLASSES:
        raise ValueError(
            f"Unknown classification '{normalised}'. "
            f"Valid values: {sorted(_VALID_CLASSES)}"
        )
    return normalised


def set_classification(record: RequestRecord, name: str, *, note: str = "") -> None:
    """Set the classification on *record*."""
    normalised = _validate_class(name)
    record.meta["classification"] = {
        "class": normalised,
        "note": note.strip(),
    }


def clear_classification(record: RequestRecord) -> None:
    """Remove any existing classification from *record*."""
    record.meta.pop("classification", None)


def get_classification(record: RequestRecord) -> dict | None:
    """Return the classification dict, or *None* if not set."""
    return record.meta.get("classification")


def get_class_name(record: RequestRecord) -> str | None:
    """Return just the class name string, or *None*."""
    entry = get_classification(record)
    return entry["class"] if entry else None


def has_classification(record: RequestRecord) -> bool:
    """Return *True* if a classification has been set."""
    return "classification" in record.meta


def filter_by_class(
    records: list[RequestRecord], name: str
) -> list[RequestRecord]:
    """Return records whose classification matches *name* (case-insensitive)."""
    target = name.strip().lower()
    return [
        r for r in records
        if get_class_name(r) == target
    ]


def valid_classes() -> list[str]:
    """Return the sorted list of accepted class names."""
    return sorted(_VALID_CLASSES)
