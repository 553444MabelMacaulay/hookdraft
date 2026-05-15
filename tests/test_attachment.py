"""Unit tests for hookdraft.attachment."""
import base64
import pytest
from hookdraft.attachment import (
    add_attachment,
    remove_attachment,
    get_attachments,
    get_attachment,
    attachment_count,
    has_attachments,
    _MAX_ATTACHMENTS,
    _MAX_SIZE_BYTES,
)


def _rec():
    return {}


def test_has_attachments_false_by_default():
    assert has_attachments(_rec()) is False


def test_attachment_count_zero_by_default():
    assert attachment_count(_rec()) == 0


def test_add_attachment_basic():
    r = _rec()
    aid = add_attachment(r, "file.txt", "text/plain", b"hello")
    assert isinstance(aid, str) and len(aid) == 36  # uuid4
    assert has_attachments(r)
    assert attachment_count(r) == 1


def test_add_attachment_returns_unique_ids():
    r = _rec()
    a1 = add_attachment(r, "a.txt", "text/plain", b"x")
    a2 = add_attachment(r, "b.txt", "text/plain", b"y")
    assert a1 != a2


def test_get_attachments_returns_list():
    r = _rec()
    add_attachment(r, "f.bin", "application/octet-stream", b"\x00\x01")
    items = get_attachments(r)
    assert len(items) == 1
    assert items[0]["name"] == "f.bin"
    assert items[0]["mime_type"] == "application/octet-stream"
    assert items[0]["size"] == 2


def test_get_attachment_by_id():
    r = _rec()
    aid = add_attachment(r, "img.png", "image/png", b"PNG")
    item = get_attachment(r, aid)
    assert item is not None
    assert item["id"] == aid
    assert base64.b64decode(item["data"]) == b"PNG"


def test_get_attachment_unknown_id_returns_none():
    r = _rec()
    assert get_attachment(r, "no-such-id") is None


def test_remove_attachment_returns_true():
    r = _rec()
    aid = add_attachment(r, "x", "text/plain", b"x")
    assert remove_attachment(r, aid) is True
    assert attachment_count(r) == 0


def test_remove_attachment_unknown_returns_false():
    r = _rec()
    assert remove_attachment(r, "ghost") is False


def test_add_attachment_empty_name_raises():
    with pytest.raises(ValueError, match="name"):
        add_attachment(_rec(), "", "text/plain", b"x")


def test_add_attachment_invalid_mime_raises():
    with pytest.raises(ValueError, match="MIME"):
        add_attachment(_rec(), "f", "notamime", b"x")


def test_add_attachment_non_bytes_raises():
    with pytest.raises(TypeError):
        add_attachment(_rec(), "f", "text/plain", "not bytes")


def test_add_attachment_too_large_raises():
    big = b"x" * (_MAX_SIZE_BYTES + 1)
    with pytest.raises(ValueError, match="maximum size"):
        add_attachment(_rec(), "big", "application/octet-stream", big)


def test_add_attachment_max_count_raises():
    r = _rec()
    for i in range(_MAX_ATTACHMENTS):
        add_attachment(r, f"f{i}", "text/plain", b"x")
    with pytest.raises(ValueError, match="maximum"):
        add_attachment(r, "overflow", "text/plain", b"x")


def test_mime_type_normalised_to_lowercase():
    r = _rec()
    add_attachment(r, "f", "Image/PNG", b"x")
    assert get_attachments(r)[0]["mime_type"] == "image/png"
