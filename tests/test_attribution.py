"""Unit tests for hookdraft.attribution."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft import attribution as attr_mod


def _rec():
    r = RequestRecord(
        method="POST",
        path="/hook",
        headers={},
        body=None,
        source_ip="127.0.0.1",
    )
    r.meta = {}
    return r


def test_has_attribution_false_by_default():
    assert attr_mod.has_attribution(_rec()) is False


def test_get_attribution_none_by_default():
    assert attr_mod.get_attribution(_rec()) is None


def test_set_attribution_basic():
    r = _rec()
    attr_mod.set_attribution(r, "manual")
    data = attr_mod.get_attribution(r)
    assert data["source"] == "manual"
    assert data["actor"] is None
    assert data["note"] is None


def test_set_attribution_with_actor_and_note():
    r = _rec()
    attr_mod.set_attribution(r, "automated", actor="Alice", note="Nightly job")
    data = attr_mod.get_attribution(r)
    assert data["actor"] == "alice"
    assert data["note"] == "Nightly job"


def test_set_attribution_normalises_source_case():
    r = _rec()
    attr_mod.set_attribution(r, "EXTERNAL")
    assert attr_mod.get_attribution(r)["source"] == "external"


def test_set_attribution_invalid_source_raises():
    with pytest.raises(ValueError, match="Invalid source"):
        attr_mod.set_attribution(_rec(), "robot")


def test_set_attribution_empty_source_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        attr_mod.set_attribution(_rec(), "   ")


def test_clear_attribution_removes_data():
    r = _rec()
    attr_mod.set_attribution(r, "internal")
    attr_mod.clear_attribution(r)
    assert attr_mod.has_attribution(r) is False


def test_clear_attribution_idempotent():
    r = _rec()
    attr_mod.clear_attribution(r)  # no error


def test_filter_by_source():
    r1, r2, r3 = _rec(), _rec(), _rec()
    attr_mod.set_attribution(r1, "manual")
    attr_mod.set_attribution(r2, "automated")
    result = attr_mod.filter_by_source([r1, r2, r3], "manual")
    assert result == [r1]


def test_filter_by_actor():
    r1, r2 = _rec(), _rec()
    attr_mod.set_attribution(r1, "manual", actor="alice")
    attr_mod.set_attribution(r2, "manual", actor="bob")
    result = attr_mod.filter_by_actor([r1, r2], "Alice")
    assert result == [r1]


def test_filter_by_actor_excludes_unattributed():
    r = _rec()
    assert attr_mod.filter_by_actor([r], "alice") == []
