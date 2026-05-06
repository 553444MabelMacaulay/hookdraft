"""Persistent in-memory storage for captured webhook requests."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class RequestRecord:
    id: str
    timestamp: str
    method: str
    path: str
    headers: Dict[str, str]
    body: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RequestRecord":
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            method=data["method"],
            path=data["path"],
            headers=data["headers"],
            body=data["body"],
            tags=data.get("tags", []),
        )


class RequestStore:
    def __init__(self):
        self._records: Dict[str, RequestRecord] = {}
        self._order: List[str] = []

    def save(self, record: RequestRecord) -> None:
        if record.id not in self._records:
            self._order.append(record.id)
        self._records[record.id] = record

    def all(self, limit: Optional[int] = None) -> List[RequestRecord]:
        records = [self._records[rid] for rid in reversed(self._order)]
        if limit is not None:
            return records[:limit]
        return records

    def get(self, record_id: str) -> Optional[RequestRecord]:
        return self._records.get(record_id)

    def delete(self, record_id: str) -> bool:
        if record_id in self._records:
            del self._records[record_id]
            self._order.remove(record_id)
            return True
        return False

    def clear(self) -> None:
        self._records.clear()
        self._order.clear()


def make_record(
    method: str = "POST",
    path: str = "/hook",
    headers: Optional[Dict[str, str]] = None,
    body: str = "",
    tags: Optional[List[str]] = None,
) -> RequestRecord:
    return RequestRecord(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        method=method,
        path=path,
        headers=headers or {},
        body=body,
        tags=tags or [],
    )
