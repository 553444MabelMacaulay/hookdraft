"""Payload diffing utilities for comparing webhook request bodies."""

import json
from typing import Any


def _normalize(payload: str) -> Any:
    """Try to parse payload as JSON, fall back to raw string."""
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return payload


def _flatten(obj: Any, prefix: str = "") -> dict:
    """Recursively flatten a nested dict/list into dot-notation keys."""
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            items.update(_flatten(v, full_key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            full_key = f"{prefix}[{i}]"
            items.update(_flatten(v, full_key))
    else:
        items[prefix] = obj
    return items


def diff_payloads(payload_a: str, payload_b: str) -> dict:
    """
    Compare two webhook payloads and return a structured diff.

    Returns a dict with:
      - added:   keys present in b but not a
      - removed: keys present in a but not b
      - changed: keys present in both but with different values
      - same:    keys with identical values
    """
    norm_a = _normalize(payload_a)
    norm_b = _normalize(payload_b)

    if not isinstance(norm_a, dict) or not isinstance(norm_b, dict):
        # Fall back to simple equality check for non-dict payloads
        return {
            "added": [],
            "removed": [],
            "changed": [{"key": "<body>", "from": norm_a, "to": norm_b}] if norm_a != norm_b else [],
            "same": ["<body>"] if norm_a == norm_b else [],
        }

    flat_a = _flatten(norm_a)
    flat_b = _flatten(norm_b)

    keys_a = set(flat_a.keys())
    keys_b = set(flat_b.keys())

    added = [k for k in keys_b - keys_a]
    removed = [k for k in keys_a - keys_b]
    changed = [
        {"key": k, "from": flat_a[k], "to": flat_b[k]}
        for k in keys_a & keys_b
        if flat_a[k] != flat_b[k]
    ]
    same = [k for k in keys_a & keys_b if flat_a[k] == flat_b[k]]

    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "changed": sorted(changed, key=lambda x: x["key"]),
        "same": sorted(same),
    }
