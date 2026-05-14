import pytest
from hookdraft.visibility import (
    set_visibility,
    clear_visibility,
    get_visibility,
    is_visible_to,
    filter_by_visibility,
    filter_visible_to,
)


def _rec():
    return {"id": "abc", "body": {}}


# --- get / set / clear ---

def test_get_visibility_default():
    assert get_visibility(_rec()) == "public"


def test_set_visibility_public():
    r = _rec()
    set_visibility(r, "public")
    assert r["visibility"] == "public"


def test_set_visibility_internal():
    r = _rec()
    set_visibility(r, "internal")
    assert r["visibility"] == "internal"


def test_set_visibility_private():
    r = _rec()
    set_visibility(r, "private")
    assert r["visibility"] == "private"


def test_set_visibility_normalises_case():
    r = _rec()
    set_visibility(r, "INTERNAL")
    assert r["visibility"] == "internal"


def test_set_visibility_strips_whitespace():
    r = _rec()
    set_visibility(r, "  private  ")
    assert r["visibility"] == "private"


def test_set_visibility_invalid_raises():
    with pytest.raises(ValueError, match="Invalid visibility level"):
        set_visibility(_rec(), "secret")


def test_clear_visibility_removes_field():
    r = _rec()
    set_visibility(r, "private")
    clear_visibility(r)
    assert "visibility" not in r


def test_clear_visibility_idempotent():
    r = _rec()
    clear_visibility(r)  # no key present — should not raise
    assert get_visibility(r) == "public"


# --- is_visible_to ---

def test_public_visible_to_public():
    r = set_visibility(_rec(), "public")
    assert is_visible_to(r, "public") is True


def test_public_visible_to_internal():
    r = set_visibility(_rec(), "public")
    assert is_visible_to(r, "internal") is True


def test_public_visible_to_private():
    r = set_visibility(_rec(), "public")
    assert is_visible_to(r, "private") is True


def test_internal_not_visible_to_public():
    r = set_visibility(_rec(), "internal")
    assert is_visible_to(r, "public") is False


def test_internal_visible_to_internal():
    r = set_visibility(_rec(), "internal")
    assert is_visible_to(r, "internal") is True


def test_private_not_visible_to_internal():
    r = set_visibility(_rec(), "private")
    assert is_visible_to(r, "internal") is False


def test_private_visible_to_private():
    r = set_visibility(_rec(), "private")
    assert is_visible_to(r, "private") is True


# --- filter helpers ---

def test_filter_by_visibility_exact():
    records = [
        set_visibility(_rec(), "public"),
        set_visibility(_rec(), "internal"),
        set_visibility(_rec(), "private"),
    ]
    result = filter_by_visibility(records, "internal")
    assert len(result) == 1
    assert result[0]["visibility"] == "internal"


def test_filter_visible_to_public_context():
    records = [
        set_visibility(_rec(), "public"),
        set_visibility(_rec(), "internal"),
        set_visibility(_rec(), "private"),
    ]
    result = filter_visible_to(records, "public")
    assert len(result) == 1


def test_filter_visible_to_private_context_returns_all():
    records = [
        set_visibility(_rec(), "public"),
        set_visibility(_rec(), "internal"),
        set_visibility(_rec(), "private"),
    ]
    result = filter_visible_to(records, "private")
    assert len(result) == 3
