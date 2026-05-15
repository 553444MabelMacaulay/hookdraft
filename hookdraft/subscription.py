"""Subscription management for webhook records.

Allows associating named subscribers with a record, tracking
which external consumers are interested in a given webhook event.
"""

from __future__ import annotations

from typing import List, Optional


def _normalise_subscriber(subscriber: str) -> str:
    subscriber = subscriber.strip().lower()
    if not subscriber:
        raise ValueError("Subscriber name must not be empty.")
    return subscriber


def subscribe(record: dict, subscriber: str, channel: Optional[str] = None) -> dict:
    """Add a subscriber to the record. Deduplicates by name."""
    name = _normalise_subscriber(subscriber)
    subscriptions = record.setdefault("subscriptions", [])
    for entry in subscriptions:
        if entry["subscriber"] == name:
            return record  # already subscribed
    entry = {"subscriber": name}
    if channel is not None:
        ch = channel.strip()
        if not ch:
            raise ValueError("Channel must not be empty if provided.")
        entry["channel"] = ch.lower()
    subscriptions.append(entry)
    return record


def unsubscribe(record: dict, subscriber: str) -> dict:
    """Remove a subscriber from the record. Idempotent."""
    name = _normalise_subscriber(subscriber)
    record["subscriptions"] = [
        e for e in record.get("subscriptions", []) if e["subscriber"] != name
    ]
    return record


def get_subscriptions(record: dict) -> List[dict]:
    """Return the list of subscription entries."""
    return list(record.get("subscriptions", []))


def is_subscribed(record: dict, subscriber: str) -> bool:
    """Return True if the named subscriber is present."""
    name = _normalise_subscriber(subscriber)
    return any(e["subscriber"] == name for e in record.get("subscriptions", []))


def subscriber_count(record: dict) -> int:
    """Return the number of distinct subscribers."""
    return len(record.get("subscriptions", []))


def filter_by_subscriber(records: list, subscriber: str) -> list:
    """Return records that have the given subscriber."""
    name = _normalise_subscriber(subscriber)
    return [r for r in records if is_subscribed(r, name)]
