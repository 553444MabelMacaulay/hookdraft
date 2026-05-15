"""Provenance tracking for webhook request records.

Allows recording where a request originated from, including source system,
environment, and an optional reference identifier.
"""

from __future__ import annotations

from typing import Optional


_VALID_ENVIRONMENTS = {"production", "staging", "development", "test", "unknown"}


def _validate_source(source: str) -> str:
    source = source.strip()
    if not source:
        raise ValueError("Provenance source must not be empty.")
    if len(source) > 128:
        raise ValueError("Provenance source must not exceed 128 characters.")
    return source.lower()


def _validate_environment(env: str) -> str:
    env = env.strip().lower()
    if env not in _VALID_ENVIRONMENTS:
        raise ValueError(
            f"Invalid environment '{env}'. Must be one of: {sorted(_VALID_ENVIRONMENTS)}."
        )
    return env


def set_provenance(
    record,
    source: str,
    environment: str = "unknown",
    ref: Optional[str] = None,
) -> None:
    """Attach provenance metadata to a record."""
    source = _validate_source(source)
    environment = _validate_environment(environment)
    ref_value = ref.strip() if ref and ref.strip() else None

    record.meta["provenance"] = {
        "source": source,
        "environment": environment,
        "ref": ref_value,
    }


def clear_provenance(record) -> None:
    """Remove provenance metadata from a record."""
    record.meta.pop("provenance", None)


def get_provenance(record) -> Optional[dict]:
    """Return the provenance dict, or None if not set."""
    return record.meta.get("provenance")


def has_provenance(record) -> bool:
    """Return True if provenance has been set on the record."""
    return "provenance" in record.meta


def filter_by_source(records, source: str):
    """Return records whose provenance source matches (case-insensitive)."""
    target = source.strip().lower()
    return [
        r for r in records
        if has_provenance(r) and get_provenance(r)["source"] == target
    ]


def filter_by_environment(records, environment: str):
    """Return records whose provenance environment matches."""
    target = environment.strip().lower()
    return [
        r for r in records
        if has_provenance(r) and get_provenance(r)["environment"] == target
    ]
