"""Versioning support for webhook request records.

Allows a record to carry a version string (e.g. "v1", "2024-01") and an
optional changelog note describing what changed in that version.
"""

from __future__ import annotations

_VERSION_KEY = "_version"
_CHANGELOG_KEY = "_version_changelog"

_MAX_VERSION_LEN = 64
_MAX_CHANGELOG_LEN = 512


def _validate_version(version: str) -> str:
    version = version.strip()
    if not version:
        raise ValueError("version must not be empty")
    if len(version) > _MAX_VERSION_LEN:
        raise ValueError(
            f"version must not exceed {_MAX_VERSION_LEN} characters"
        )
    return version


def set_version(record: dict, version: str, changelog: str | None = None) -> dict:
    """Attach a version string (and optional changelog) to *record*."""
    record[_VERSION_KEY] = _validate_version(version)
    if changelog is not None:
        changelog = changelog.strip()
        if not changelog:
            raise ValueError("changelog must not be empty if provided")
        if len(changelog) > _MAX_CHANGELOG_LEN:
            raise ValueError(
                f"changelog must not exceed {_MAX_CHANGELOG_LEN} characters"
            )
        record[_CHANGELOG_KEY] = changelog
    else:
        record.pop(_CHANGELOG_KEY, None)
    return record


def clear_version(record: dict) -> dict:
    """Remove version and changelog from *record*."""
    record.pop(_VERSION_KEY, None)
    record.pop(_CHANGELOG_KEY, None)
    return record


def get_version(record: dict) -> str | None:
    """Return the version string, or *None* if not set."""
    return record.get(_VERSION_KEY)


def get_changelog(record: dict) -> str | None:
    """Return the changelog note, or *None* if not set."""
    return record.get(_CHANGELOG_KEY)


def has_version(record: dict) -> bool:
    """Return *True* if the record has a version set."""
    return _VERSION_KEY in record


def filter_by_version(records: list[dict], version: str) -> list[dict]:
    """Return records whose version exactly matches *version*."""
    version = version.strip()
    return [r for r in records if r.get(_VERSION_KEY) == version]
