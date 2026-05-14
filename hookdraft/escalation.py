"""Escalation support for request records.

Allows a record to be escalated to a named tier with an optional reason,
tracking when the escalation was created.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

VALID_TIERS = ("low", "medium", "high", "critical")
_TIER_ORDER = {t: i for i, t in enumerate(VALID_TIERS)}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_tier(tier: str) -> str:
    normalised = tier.strip().lower()
    if normalised not in VALID_TIERS:
        raise ValueError(f"Invalid escalation tier {tier!r}; must be one of {VALID_TIERS}")
    return normalised


def escalate_record(record: dict, tier: str, reason: str = "") -> None:
    """Escalate *record* to *tier* with an optional *reason*."""
    normalised = _validate_tier(tier)
    reason = reason.strip()
    record["escalation"] = {
        "tier": normalised,
        "reason": reason or None,
        "escalated_at": _now_iso(),
    }


def deescalate_record(record: dict) -> None:
    """Remove any escalation from *record*."""
    record.pop("escalation", None)


def is_escalated(record: dict) -> bool:
    return "escalation" in record


def get_escalation(record: dict) -> Optional[dict]:
    return record.get("escalation")


def get_escalation_tier(record: dict) -> Optional[str]:
    esc = record.get("escalation")
    return esc["tier"] if esc else None


def filter_escalated(records: list[dict]) -> list[dict]:
    """Return only records that have been escalated."""
    return [r for r in records if is_escalated(r)]


def filter_by_min_tier(records: list[dict], min_tier: str) -> list[dict]:
    """Return records escalated at *min_tier* or above."""
    threshold = _TIER_ORDER[_validate_tier(min_tier)]
    return [
        r for r in records
        if is_escalated(r) and _TIER_ORDER.get(get_escalation_tier(r), -1) >= threshold
    ]
