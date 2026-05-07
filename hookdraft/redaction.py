"""Redaction helpers — mask sensitive fields in a request payload."""

from __future__ import annotations

from typing import Any

_MASK = "***REDACTED***"

_DEFAULT_SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "authorization",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "private_key",
    "credentials",
}


def _redact_value(value: Any, keys: set[str]) -> Any:
    """Recursively redact matching keys inside dicts / lists."""
    if isinstance(value, dict):
        return {k: (_MASK if k.lower() in keys else _redact_value(v, keys)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(item, keys) for item in value]
    return value


def redact_record(record, extra_keys: list[str] | None = None) -> None:
    """Redact sensitive fields in *record.body* in-place.

    Args:
        record: A ``RequestRecord`` instance whose ``body`` attribute holds
                the parsed payload (dict, list, or ``None``).
        extra_keys: Additional field names to treat as sensitive (case-
                    insensitive).  Combined with the built-in defaults.
    """
    if record.body is None:
        return

    keys = set(_DEFAULT_SENSITIVE_KEYS)
    if extra_keys:
        keys.update(k.lower() for k in extra_keys if k.strip())

    record.body = _redact_value(record.body, keys)
    record.meta["redacted"] = True


def is_redacted(record) -> bool:
    """Return ``True`` if the record has been redacted at least once."""
    return bool(record.meta.get("redacted", False))


def get_redaction_mask() -> str:
    """Return the string used as the replacement value for redacted fields."""
    return _MASK
