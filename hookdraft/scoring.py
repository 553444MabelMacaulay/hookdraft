"""Request scoring — assign a numeric priority score to a RequestRecord."""

from __future__ import annotations

from typing import Optional

from hookdraft.storage import RequestRecord

_MIN_SCORE = 0
_MAX_SCORE = 100


def _validate_score(score: int) -> None:
    if not isinstance(score, int):
        raise TypeError(f"Score must be an integer, got {type(score).__name__}")
    if score < _MIN_SCORE or score > _MAX_SCORE:
        raise ValueError(
            f"Score must be between {_MIN_SCORE} and {_MAX_SCORE}, got {score}"
        )


def set_score(record: RequestRecord, score: int) -> RequestRecord:
    """Assign a priority score (0–100) to *record*."""
    _validate_score(score)
    record.meta["score"] = score
    return record


def clear_score(record: RequestRecord) -> RequestRecord:
    """Remove the score from *record* if present."""
    record.meta.pop("score", None)
    return record


def get_score(record: RequestRecord) -> Optional[int]:
    """Return the score attached to *record*, or ``None`` if not set."""
    return record.meta.get("score")


def filter_by_min_score(
    records: list[RequestRecord], minimum: int
) -> list[RequestRecord]:
    """Return records whose score is >= *minimum*."""
    _validate_score(minimum)
    return [
        r for r in records if get_score(r) is not None and get_score(r) >= minimum
    ]


def filter_by_max_score(
    records: list[RequestRecord], maximum: int
) -> list[RequestRecord]:
    """Return records whose score is <= *maximum*."""
    _validate_score(maximum)
    return [
        r for r in records if get_score(r) is not None and get_score(r) <= maximum
    ]


def sort_by_score(
    records: list[RequestRecord], descending: bool = True
) -> list[RequestRecord]:
    """Return *records* sorted by score.  Unscored records appear last."""
    scored = [r for r in records if get_score(r) is not None]
    unscored = [r for r in records if get_score(r) is None]
    scored.sort(key=lambda r: get_score(r), reverse=descending)  # type: ignore[arg-type]
    return scored + unscored
