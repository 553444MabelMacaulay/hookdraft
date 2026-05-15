"""Attachment support for request records.

Allows small metadata attachments (name + mime type + base64 content)
to be associated with a record for documentation purposes.
"""
from __future__ import annotations

import base64
import uuid
from typing import Any

_KEY = "attachments"
_MAX_SIZE_BYTES = 65_536  # 64 KiB per attachment
_MAX_ATTACHMENTS = 20


def _validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("attachment name must not be empty")
    if len(name) > 128:
        raise ValueError("attachment name must be 128 characters or fewer")
    return name


def _validate_mime(mime: str) -> str:
    mime = mime.strip().lower()
    if not mime or "/" not in mime:
        raise ValueError("mime_type must be a valid MIME type string (e.g. 'image/png')")
    return mime


def add_attachment(record: dict[str, Any], name: str, mime_type: str, data: bytes) -> str:
    """Attach *data* to *record*. Returns the generated attachment ID."""
    name = _validate_name(name)
    mime_type = _validate_mime(mime_type)
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes")
    if len(data) > _MAX_SIZE_BYTES:
        raise ValueError(f"attachment exceeds maximum size of {_MAX_SIZE_BYTES} bytes")
    attachments: list[dict[str, Any]] = record.setdefault(_KEY, [])
    if len(attachments) >= _MAX_ATTACHMENTS:
        raise ValueError(f"record already has the maximum of {_MAX_ATTACHMENTS} attachments")
    attachment_id = str(uuid.uuid4())
    attachments.append({
        "id": attachment_id,
        "name": name,
        "mime_type": mime_type,
        "data": base64.b64encode(data).decode("ascii"),
        "size": len(data),
    })
    return attachment_id


def remove_attachment(record: dict[str, Any], attachment_id: str) -> bool:
    """Remove attachment by ID. Returns True if removed, False if not found."""
    attachments: list[dict[str, Any]] = record.get(_KEY, [])
    before = len(attachments)
    record[_KEY] = [a for a in attachments if a["id"] != attachment_id]
    return len(record[_KEY]) < before


def get_attachments(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all attachments (without raw data decoded)."""
    return list(record.get(_KEY, []))


def get_attachment(record: dict[str, Any], attachment_id: str) -> dict[str, Any] | None:
    """Return a single attachment dict or None."""
    for a in record.get(_KEY, []):
        if a["id"] == attachment_id:
            return a
    return None


def attachment_count(record: dict[str, Any]) -> int:
    return len(record.get(_KEY, []))


def has_attachments(record: dict[str, Any]) -> bool:
    return attachment_count(record) > 0
