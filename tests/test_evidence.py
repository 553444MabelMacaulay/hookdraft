import pytest
from hookdraft.evidence import (
    add_evidence,
    remove_evidence,
    get_evidence,
    has_evidence,
    evidence_count,
    filter_by_evidence_kind,
)


def _rec():
    return {"id": "r1"}


def test_get_evidence_empty_by_default():
    assert get_evidence(_rec()) == []


def test_has_evidence_false_by_default():
    assert has_evidence(_rec()) is False


def test_evidence_count_zero_by_default():
    assert evidence_count(_rec()) == 0


def test_add_evidence_basic():
    r = _rec()
    eid = add_evidence(r, "url", "https://example.com")
    assert isinstance(eid, str) and len(eid) > 0
    items = get_evidence(r)
    assert len(items) == 1
    assert items[0]["kind"] == "url"
    assert items[0]["content"] == "https://example.com"


def test_add_evidence_with_label():
    r = _rec()
    add_evidence(r, "hash", "abc123", label="sha256")
    items = get_evidence(r)
    assert items[0]["label"] == "sha256"


def test_add_evidence_no_label_key_when_empty():
    r = _rec()
    add_evidence(r, "text", "some note")
    assert "label" not in get_evidence(r)[0]


def test_add_evidence_normalises_kind_case():
    r = _rec()
    add_evidence(r, "URL", "https://x.com")
    assert get_evidence(r)[0]["kind"] == "url"


def test_add_evidence_strips_content_whitespace():
    r = _rec()
    add_evidence(r, "text", "  hello  ")
    assert get_evidence(r)[0]["content"] == "hello"


def test_add_evidence_invalid_kind_raises():
    with pytest.raises(ValueError, match="kind"):
        add_evidence(_rec(), "image", "data")


def test_add_evidence_empty_content_raises():
    with pytest.raises(ValueError, match="content"):
        add_evidence(_rec(), "text", "   ")


def test_add_evidence_returns_unique_ids():
    r = _rec()
    id1 = add_evidence(r, "text", "a")
    id2 = add_evidence(r, "text", "b")
    assert id1 != id2


def test_remove_evidence_returns_true():
    r = _rec()
    eid = add_evidence(r, "hash", "deadbeef")
    assert remove_evidence(r, eid) is True
    assert get_evidence(r) == []


def test_remove_evidence_unknown_returns_false():
    r = _rec()
    assert remove_evidence(r, "no-such-id") is False


def test_has_evidence_true_after_add():
    r = _rec()
    add_evidence(r, "file", "report.pdf")
    assert has_evidence(r) is True


def test_evidence_count_increments():
    r = _rec()
    add_evidence(r, "url", "https://a.com")
    add_evidence(r, "url", "https://b.com")
    assert evidence_count(r) == 2


def test_filter_by_evidence_kind():
    r1 = _rec()
    r2 = {"id": "r2"}
    add_evidence(r1, "url", "https://a.com")
    add_evidence(r2, "hash", "abc")
    result = filter_by_evidence_kind([r1, r2], "url")
    assert r1 in result
    assert r2 not in result


def test_filter_by_evidence_kind_normalises_case():
    r = _rec()
    add_evidence(r, "hash", "abc")
    assert filter_by_evidence_kind([r], "HASH") == [r]
