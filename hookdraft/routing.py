"""Request routing rules: match incoming webhooks to named routes by path/method patterns."""

from __future__ import annotations

import re
from typing import Optional

_VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "*"}


def _normalise_method(method: str) -> str:
    m = method.strip().upper()
    if m not in _VALID_METHODS:
        raise ValueError(f"Unknown HTTP method: {method!r}")
    return m


def set_route(record: dict, name: str, pattern: str, method: str = "*") -> None:
    """Attach a named routing rule to *record*."""
    name = name.strip()
    if not name:
        raise ValueError("Route name must not be empty.")
    pattern = pattern.strip()
    if not pattern:
        raise ValueError("Route pattern must not be empty.")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {exc}") from exc
    method = _normalise_method(method)
    record.setdefault("routing", {})
    record["routing"][name] = {"pattern": pattern, "method": method}


def remove_route(record: dict, name: str) -> None:
    """Remove a named routing rule from *record* (idempotent)."""
    record.get("routing", {}).pop(name.strip(), None)


def get_routes(record: dict) -> dict:
    """Return all routing rules attached to *record* (may be empty)."""
    return dict(record.get("routing", {}))


def match_route(record: dict) -> Optional[str]:
    """Return the first rule name whose pattern matches the record's path and method.

    Rules are checked in insertion order; returns ``None`` if nothing matches.
    """
    path = record.get("path", "")
    rec_method = record.get("method", "").upper()
    for name, rule in record.get("routing", {}).items():
        method_ok = rule["method"] == "*" or rule["method"] == rec_method
        if method_ok and re.search(rule["pattern"], path):
            return name
    return None


def filter_by_route(records: list, name: str) -> list:
    """Return records that have a routing rule with *name* defined."""
    return [r for r in records if name in r.get("routing", {})]
