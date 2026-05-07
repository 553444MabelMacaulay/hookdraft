"""Payload transformation utilities for hookdraft.

Allows attaching a named transformation (jq-style key remapping or
field masking) to a request record so that replayed or exported
payloads can be sent in an alternate shape.
"""

from __future__ import annotations

from typing import Any

_TRANSFORM_KEY = "_transformation"

VALID_OPS = {"rename", "drop", "mask"}


def _validate_steps(steps: list[dict]) -> None:
    if not isinstance(steps, list):
        raise TypeError("steps must be a list")
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            raise TypeError(f"step {i} must be a dict")
        op = step.get("op")
        if op not in VALID_OPS:
            raise ValueError(f"step {i}: unknown op {op!r}; valid ops are {VALID_OPS}")
        if "field" not in step:
            raise ValueError(f"step {i}: 'field' is required")
        if op == "rename" and "to" not in step:
            raise ValueError(f"step {i}: rename op requires 'to'")


def set_transformation(record: dict, steps: list[dict]) -> None:
    """Attach a list of transformation steps to *record*."""
    _validate_steps(steps)
    record[_TRANSFORM_KEY] = list(steps)


def clear_transformation(record: dict) -> None:
    """Remove any transformation attached to *record*."""
    record.pop(_TRANSFORM_KEY, None)


def get_transformation(record: dict) -> list[dict] | None:
    """Return the transformation steps attached to *record*, or None."""
    return record.get(_TRANSFORM_KEY)


def apply_transformation(payload: Any, steps: list[dict]) -> Any:
    """Apply *steps* to *payload* and return the transformed copy.

    Only dict payloads are mutated; non-dict values are returned as-is.
    """
    if not isinstance(payload, dict):
        return payload

    result: dict = dict(payload)
    for step in steps:
        op = step["op"]
        field = step["field"]
        if op == "drop":
            result.pop(field, None)
        elif op == "mask":
            if field in result:
                result[field] = step.get("mask", "***")
        elif op == "rename":
            if field in result:
                result[step["to"]] = result.pop(field)
    return result
