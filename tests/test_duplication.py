"""Tests for hookdraft.duplication."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.duplication import (
    compute_fingerprint,
    mark_duplicate,
    unmark_duplicate,
    is_duplicate,
    get_original_id,
    filter_duplicates,
    filter_originals,
    find_duplicates_of,
)


def _rec(**kwargs) -> RequestRecord:
    defaults = dict(
        id="abc",
        method="POST",
        path="/hook",
        headers={"content-type": "application/json"},
        body={"event": "ping"},
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )
    defaults.update(kwargs)
    r = RequestRecord(**defaults)
    r.meta = {}
    return r


def test_is_duplicate_false_by_default():
    assert is_duplicate(_rec()) is False


def test_get_original_id_none_by_default():
    assert get_original_id(_rec()) is None


def test_mark_duplicate_sets_flag():
    r = _rec()
    mark_duplicate(r, "orig-001")
    assert is_duplicate(r) is True


def test_mark_duplicate_stores_original_id():
    r = _rec()
    mark_duplicate(r, "orig-001")
    assert get_original_id(r) == "orig-001"


def test_mark_duplicate_strips_whitespace():
    r = _rec()
    mark_duplicate(r, "  orig-002  ")
    assert get_original_id(r) == "orig-002"


def test_mark_duplicate_empty_id_raises():
    with pytest.raises(ValueError):
        mark_duplicate(_rec(), "")


def test_mark_duplicate_whitespace_only_raises():
    with pytest.raises(ValueError):
        mark_duplicate(_rec(), "   ")


def test_unmark_duplicate_removes_flag():
    r = _rec()
    mark_duplicate(r, "orig-001")
    unmark_duplicate(r)
    assert is_duplicate(r) is False


def test_unmark_duplicate_removes_original_id():
    r = _rec()
    mark_duplicate(r, "orig-001")
    unmark_duplicate(r)
    assert get_original_id(r) is None


def test_unmark_duplicate_idempotent():
    r = _rec()
    unmark_duplicate(r)  # should not raise
    assert is_duplicate(r) is False


def test_filter_duplicates():
    r1, r2, r3 = _rec(id="1"), _rec(id="2"), _rec(id="3")
    mark_duplicate(r2, "1")
    result = filter_duplicates([r1, r2, r3])
    assert result == [r2]


def test_filter_originals():
    r1, r2, r3 = _rec(id="1"), _rec(id="2"), _rec(id="3")
    mark_duplicate(r2, "1")
    result = filter_originals([r1, r2, r3])
    assert r1 in result and r3 in result and r2 not in result


def test_find_duplicates_of():
    r1, r2, r3 = _rec(id="1"), _rec(id="2"), _rec(id="3")
    mark_duplicate(r2, "1")
    mark_duplicate(r3, "1")
    result = find_duplicates_of([r1, r2, r3], "1")
    assert set(r.id for r in result) == {"2", "3"}


def test_compute_fingerprint_same_for_identical_records():
    r1 = _rec()
    r2 = _rec()
    assert compute_fingerprint(r1) == compute_fingerprint(r2)


def test_compute_fingerprint_differs_for_different_body():
    r1 = _rec(body={"event": "ping"})
    r2 = _rec(body={"event": "push"})
    assert compute_fingerprint(r1) != compute_fingerprint(r2)


def test_compute_fingerprint_excludes_sensitive_headers():
    r1 = _rec(headers={"authorization": "Bearer token-a", "content-type": "application/json"})
    r2 = _rec(headers={"authorization": "Bearer token-b", "content-type": "application/json"})
    assert compute_fingerprint(r1) == compute_fingerprint(r2)


def test_compute_fingerprint_none_body():
    r = _rec(body=None)
    fp = compute_fingerprint(r)
    assert isinstance(fp, str) and len(fp) == 64
