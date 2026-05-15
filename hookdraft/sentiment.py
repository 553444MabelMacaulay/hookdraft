"""Sentiment scoring for webhook request records."""

from __future__ import annotations

from typing import Optional

_VALID_SENTIMENTS = {"positive", "neutral", "negative"}
_SENTIMENT_SCORES = {"positive": 1, "neutral": 0, "negative": -1}


def _validate_sentiment(value: str) -> str:
    normalised = value.strip().lower()
    if not normalised:
        raise ValueError("Sentiment value must not be empty.")
    if normalised not in _VALID_SENTIMENTS:
        raise ValueError(
            f"Invalid sentiment {value!r}. Must be one of: "
            + ", ".join(sorted(_VALID_SENTIMENTS))
        )
    return normalised


def set_sentiment(record: dict, sentiment: str, note: Optional[str] = None) -> None:
    """Attach a sentiment label (positive / neutral / negative) to *record*."""
    normalised = _validate_sentiment(sentiment)
    record["sentiment"] = {
        "value": normalised,
        "score": _SENTIMENT_SCORES[normalised],
        "note": note.strip() if note and note.strip() else None,
    }


def clear_sentiment(record: dict) -> None:
    """Remove any sentiment data from *record*."""
    record.pop("sentiment", None)


def get_sentiment(record: dict) -> Optional[dict]:
    """Return the sentiment dict or *None* if not set."""
    return record.get("sentiment")


def get_sentiment_value(record: dict) -> Optional[str]:
    """Return just the sentiment label string, or *None*."""
    s = record.get("sentiment")
    return s["value"] if s else None


def has_sentiment(record: dict) -> bool:
    return "sentiment" in record


def filter_by_sentiment(records: list[dict], sentiment: str) -> list[dict]:
    """Return records whose sentiment matches *sentiment* (case-insensitive)."""
    normalised = _validate_sentiment(sentiment)
    return [r for r in records if get_sentiment_value(r) == normalised]


def filter_positive(records: list[dict]) -> list[dict]:
    return filter_by_sentiment(records, "positive")


def filter_negative(records: list[dict]) -> list[dict]:
    return filter_by_sentiment(records, "negative")
