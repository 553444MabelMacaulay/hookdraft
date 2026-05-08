"""Throttling: rate-limit metadata attached to a RequestRecord."""

from __future__ import annotations

from typing import List, Optional

_MAX_RPM = 100_000
_VALID_ACTIONS = {"drop", "queue", "reject"}


def set_throttle(
    record: dict,
    *,
    rpm: int,
    action: str = "drop",
    burst: Optional[int] = None,
) -> None:
    """Attach throttle policy to *record*.

    Args:
        record: A RequestRecord.to_dict()-compatible dict (mutated in place).
        rpm: Requests-per-minute limit (1 – 100 000).
        action: What to do when the limit is exceeded: 'drop', 'queue', or 'reject'.
        burst: Optional short-burst allowance (must be >= rpm when provided).
    """
    if not isinstance(rpm, int) or rpm < 1:
        raise ValueError("rpm must be a positive integer")
    if rpm > _MAX_RPM:
        raise ValueError(f"rpm must not exceed {_MAX_RPM}")
    action = action.lower().strip()
    if action not in _VALID_ACTIONS:
        raise ValueError(f"action must be one of {sorted(_VALID_ACTIONS)}")
    if burst is not None:
        if not isinstance(burst, int) or burst < rpm:
            raise ValueError("burst must be an integer >= rpm")
    record["throttle"] = {"rpm": rpm, "action": action, "burst": burst}


def clear_throttle(record: dict) -> None:
    """Remove throttle policy from *record*."""
    record.pop("throttle", None)


def get_throttle(record: dict) -> Optional[dict]:
    """Return the throttle policy dict, or *None* if not set."""
    return record.get("throttle")


def is_throttled(record: dict) -> bool:
    """Return *True* if a throttle policy is attached."""
    return "throttle" in record


def filter_throttled(records: List[dict]) -> List[dict]:
    """Return only records that have a throttle policy."""
    return [r for r in records if is_throttled(r)]


def filter_unthrottled(records: List[dict]) -> List[dict]:
    """Return only records without a throttle policy."""
    return [r for r in records if not is_throttled(r)]


def filter_by_action(records: List[dict], action: str) -> List[dict]:
    """Return records whose throttle action matches *action* (case-insensitive)."""
    action = action.lower().strip()
    return [
        r for r in records
        if is_throttled(r) and r["throttle"]["action"] == action
    ]
