"""Archive and unarchive request records."""

from typing import List
from hookdraft.storage import RequestRecord


def archive_record(record: RequestRecord) -> RequestRecord:
    """Mark a record as archived."""
    record.meta["archived"] = True
    return record


def unarchive_record(record: RequestRecord) -> RequestRecord:
    """Remove the archived flag from a record."""
    record.meta.pop("archived", None)
    return record


def is_archived(record: RequestRecord) -> bool:
    """Return True if the record is archived."""
    return bool(record.meta.get("archived", False))


def filter_archived(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only archived records."""
    return [r for r in records if is_archived(r)]


def filter_unarchived(records: List[RequestRecord]) -> List[RequestRecord]:
    """Return only records that are NOT archived."""
    return [r for r in records if not is_archived(r)]
