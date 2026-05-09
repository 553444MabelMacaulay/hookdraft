import time
import pytest
from hookdraft.annotation import (
    add_annotation,
    remove_annotation,
    get_annotations,
    has_annotations,
    filter_by_author,
)


def _rec():
    return {"id": "r1", "annotations": []}


def test_get_annotations_empty_by_default():
    r = {"id": "r1"}
    assert get_annotations(r) == []


def test_add_annotation_basic():
    r = _rec()
    entry = add_annotation(r, "hello world")
    assert entry["text"] == "hello world"
    assert entry["author"] == "anonymous"
    assert "timestamp" in entry
    assert len(get_annotations(r)) == 1


def test_add_annotation_with_author():
    r = _rec()
    entry = add_annotation(r, "looks good", author="alice")
    assert entry["author"] == "alice"


def test_add_annotation_strips_whitespace_from_text():
    r = _rec()
    entry = add_annotation(r, "  trimmed  ")
    assert entry["text"] == "trimmed"


def test_add_annotation_empty_text_raises():
    r = _rec()
    with pytest.raises(ValueError):
        add_annotation(r, "   ")


def test_add_annotation_empty_author_defaults_to_anonymous():
    r = _rec()
    entry = add_annotation(r, "note", author="   ")
    assert entry["author"] == "anonymous"


def test_add_annotation_timestamp_is_recent():
    before = time.time()
    r = _rec()
    entry = add_annotation(r, "ts check")
    after = time.time()
    assert before <= entry["timestamp"] <= after


def test_remove_annotation_by_index():
    r = _rec()
    add_annotation(r, "first")
    add_annotation(r, "second")
    remove_annotation(r, 0)
    remaining = get_annotations(r)
    assert len(remaining) == 1
    assert remaining[0]["text"] == "second"


def test_remove_annotation_invalid_index_raises():
    r = _rec()
    add_annotation(r, "only one")
    with pytest.raises(IndexError):
        remove_annotation(r, 5)


def test_has_annotations_false_by_default():
    assert not has_annotations({"id": "r1"})


def test_has_annotations_true_after_add():
    r = _rec()
    add_annotation(r, "present")
    assert has_annotations(r)


def test_filter_by_author():
    r1 = {"id": "r1", "annotations": [{"author": "alice", "text": "a", "timestamp": 0}]}
    r2 = {"id": "r2", "annotations": [{"author": "bob", "text": "b", "timestamp": 0}]}
    r3 = {"id": "r3", "annotations": []}
    result = filter_by_author([r1, r2, r3], "alice")
    assert result == [r1]


def test_filter_by_author_case_insensitive():
    r = {"id": "r1", "annotations": [{"author": "Alice", "text": "x", "timestamp": 0}]}
    assert filter_by_author([r], "alice") == [r]
