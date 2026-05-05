"""Unit tests for RequestRecord and RequestStore."""

import json
import tempfile
from pathlib import Path

import pytest

from hookdraft.storage import RequestRecord, RequestStore


def make_record(**kwargs) -> RequestRecord:
    defaults = dict(method="POST", path="/hooks/test", headers={"Content-Type": "application/json"}, body=b'{"key": "value"}')
    defaults.update(kwargs)
    return RequestRecord(**defaults)


def test_record_to_dict():
    record = make_record()
    d = record.to_dict()
    assert d["method"] == "POST"
    assert d["path"] == "/hooks/test"
    assert d["body"] == '{"key": "value"}'
    assert "id" in d
    assert "timestamp" in d


def test_record_roundtrip():
    original = make_record(query="foo=bar")
    restored = RequestRecord.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.query == "foo=bar"
    assert restored.body == original.body


def test_store_save_and_all():
    store = RequestStore()
    r1 = store.save(make_record(method="GET"))
    r2 = store.save(make_record(method="POST"))
    records = store.all()
    assert len(records) == 2
    # most recent first
    assert records[0].id == r2.id
    assert records[1].id == r1.id


def test_store_get():
    store = RequestStore()
    saved = store.save(make_record())
    assert store.get(saved.id) is not None
    assert store.get("nonexistent") is None


def test_store_clear():
    store = RequestStore()
    store.save(make_record())
    store.save(make_record())
    deleted = store.clear()
    assert deleted == 2
    assert store.all() == []


def test_store_max_records():
    store = RequestStore(max_records=3)
    for _ in range(5):
        store.save(make_record())
    assert len(store.all()) == 3


def test_store_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "history.json"
        store = RequestStore(persist_path=path)
        saved = store.save(make_record())
        assert path.exists()

        store2 = RequestStore(persist_path=path)
        assert len(store2.all()) == 1
        assert store2.all()[0].id == saved.id
