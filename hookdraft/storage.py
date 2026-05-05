"""In-memory and file-backed storage for webhook request history."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class RequestRecord:
    def __init__(self, method: str, path: str, headers: dict, body: bytes, query: str = ""):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.method = method
        self.path = path
        self.headers = dict(headers)
        self.body = body.decode("utf-8", errors="replace")
        self.query = query

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body,
            "query": self.query,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RequestRecord":
        record = cls.__new__(cls)
        record.id = data["id"]
        record.timestamp = data["timestamp"]
        record.method = data["method"]
        record.path = data["path"]
        record.headers = data["headers"]
        record.body = data["body"]
        record.query = data.get("query", "")
        return record


class RequestStore:
    def __init__(self, persist_path: Optional[Path] = None, max_records: int = 500):
        self._records: list[RequestRecord] = []
        self._persist_path = persist_path
        self._max_records = max_records
        if persist_path and persist_path.exists():
            self._load()

    def save(self, record: RequestRecord) -> RequestRecord:
        self._records.append(record)
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]
        if self._persist_path:
            self._dump()
        return record

    def all(self) -> list[RequestRecord]:
        return list(reversed(self._records))

    def get(self, record_id: str) -> Optional[RequestRecord]:
        return next((r for r in self._records if r.id == record_id), None)

    def clear(self) -> int:
        count = len(self._records)
        self._records.clear()
        if self._persist_path:
            self._dump()
        return count

    def _dump(self):
        self._persist_path.write_text(
            json.dumps([r.to_dict() for r in self._records], indent=2)
        )

    def _load(self):
        try:
            data = json.loads(self._persist_path.read_text())
            self._records = [RequestRecord.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError):
            self._records = []
