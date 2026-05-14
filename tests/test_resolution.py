"""Unit tests for hookdraft.resolution."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.resolution import (
    resolve_record,
    unresolve_record,
    is_resolved,
    get_resolution,
    get_resolver,
    filter_resolved,
    filter_unresolved,
)


def _rec(rid="abc"):
    return RequestRecord(
        id=rid,
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
    )


def test_is_resolved_false_by_default():
    assert is_resolved(_rec()) is False


def test_get_resolution_none_by_default():
    assert get_resolution(_rec()) is None


def test_resolve_record_sets_flag():
    r = _rec()
    resolve_record(r, "alice")
    assert is_resolved(r) is True


def test_resolve_record_stores_resolver_lowercased():
    r = _rec()
    resolve_record(r, "  Alice  ")
    assert get_resolver(r) == "alice"


def test_resolve_record_stores_note():
    r = _rec()
    resolve_record(r, "bob", note="fixed upstream")
    assert get_resolution(r)["note"] == "fixed upstream"


def test_resolve_record_note_none_by_default():
    r = _rec()
    resolve_record(r, "bob")
    assert get_resolution(r)["note"] is None


def test_resolve_record_empty_resolver_raises():
    with pytest.raises(ValueError):
        resolve_record(_rec(), "")


def test_resolve_record_whitespace_resolver_raises():
    with pytest.raises(ValueError):
        resolve_record(_rec(), "   ")


def test_resolve_record_empty_note_raises():
    with pytest.raises(ValueError):
        resolve_record(_rec(), "alice", note="   ")


def test_unresolve_record_removes_flag():
    r = _rec()
    resolve_record(r, "alice")
    unresolve_record(r)
    assert is_resolved(r) is False


def test_unresolve_idempotent_when_not_resolved():
    r = _rec()
    unresolve_record(r)  # should not raise
    assert is_resolved(r) is False


def test_filter_resolved():
    r1, r2 = _rec("1"), _rec("2")
    resolve_record(r1, "alice")
    result = filter_resolved([r1, r2])
    assert result == [r1]


def test_filter_unresolved():
    r1, r2 = _rec("1"), _rec("2")
    resolve_record(r1, "alice")
    result = filter_unresolved([r1, r2])
    assert result == [r2]
