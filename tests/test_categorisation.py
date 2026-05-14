import pytest
from hookdraft.storage import RequestRecord
from hookdraft.categorisation import (
    set_category,
    clear_category,
    get_category,
    get_category_name,
    get_category_colour,
    filter_by_category,
)


def _rec():
    return RequestRecord(
        id="abc",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )


def test_get_category_none_by_default():
    r = _rec()
    assert get_category(r) is None


def test_get_category_name_none_by_default():
    r = _rec()
    assert get_category_name(r) is None


def test_set_category_basic():
    r = _rec()
    set_category(r, "billing")
    assert get_category_name(r) == "billing"


def test_set_category_normalises_name():
    r = _rec()
    set_category(r, "  Billing  ")
    assert get_category_name(r) == "billing"


def test_set_category_default_colour():
    r = _rec()
    set_category(r, "ops")
    assert get_category_colour(r) == "#888888"


def test_set_category_custom_colour():
    r = _rec()
    set_category(r, "ops", colour="#ff0000")
    assert get_category_colour(r) == "#ff0000"


def test_set_category_empty_name_raises():
    r = _rec()
    with pytest.raises(ValueError, match="name"):
        set_category(r, "")


def test_set_category_whitespace_only_raises():
    r = _rec()
    with pytest.raises(ValueError, match="name"):
        set_category(r, "   ")


def test_clear_category_removes_entry():
    r = _rec()
    set_category(r, "infra")
    clear_category(r)
    assert get_category(r) is None


def test_clear_category_idempotent():
    r = _rec()
    clear_category(r)
    assert get_category(r) is None


def test_filter_by_category_matches():
    r1 = _rec()
    r2 = _rec()
    r2.id = "xyz"
    set_category(r1, "billing")
    set_category(r2, "ops")
    result = filter_by_category([r1, r2], "billing")
    assert result == [r1]


def test_filter_by_category_case_insensitive():
    r = _rec()
    set_category(r, "billing")
    result = filter_by_category([r], "Billing")
    assert result == [r]


def test_filter_by_category_no_match():
    r = _rec()
    set_category(r, "ops")
    assert filter_by_category([r], "billing") == []
