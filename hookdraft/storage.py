"""Storage layer for webhook request records."""

import uuid
from datetime import datetime, timezone
from typing import Optional


class RequestRecord:
    def __init__(
        self,
        method: str,
        path: str,
        headers: dict,
        body: str,
        timestamp: Optional[str] = None,
        id: Optional[str] = None,
        tags: Optional[list] = None,
        note: Optional[str] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.tags = tags or []
        self.note = note

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body,
            "timestamp": self.timestamp,
            "tags": list(self.tags),
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RequestRecord":
        return cls(
            id=data.get("id"),
            method=data["method"],
            path=data["path"],
            headers=data.get("headers", {}),
            body=data.get("body", ""),
            timestamp=data.get("timestamp"),
            tags=data.get("tags", []),
            note=data.get("note"),
        )


class RequestStore:
    def __init__(self):
        self._records: dict[str, RequestRecord] = {}

    def save(self, record: RequestRecord) -> RequestRecord:
        self._records[record.id] = record
        return record

    def all(self, limit: Optional[int] = None) -> list:
        records = list(reversed(list(self._records.values())))
        if limit is not None:
            records = records[:limit]
        return records

    def get(self, record_id: str) -> Optional[RequestRecord]:
        return self._records.get(record_id)

    def delete(self, record_id: str) -> bool:
        if record_id in self._records:
            del self._records[record_id]
            return True
        return False

    def clear(self) -> None:
        self._records.clear()

    def count(self) -> int:
        return len(self._records)
