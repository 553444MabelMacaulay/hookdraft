"""Unit tests for hookdraft.routing."""

import pytest
from hookdraft.routing import (
    set_route,
    remove_route,
    get_routes,
    match_route,
    filter_by_route,
)


def _rec(path="/hooks/test", method="POST"):
    return {"path": path, "method": method}


def test_set_route_basic():
    r = _rec()
    set_route(r, "my-rule", r"/hooks/.*")
    assert "my-rule" in r["routing"]
    assert r["routing"]["my-rule"]["pattern"] == r"/hooks/.*"
    assert r["routing"]["my-rule"]["method"] == "*"


def test_set_route_with_method():
    r = _rec()
    set_route(r, "post-only", r"/hooks/.*", method="POST")
    assert r["routing"]["post-only"]["method"] == "POST"


def test_set_route_normalises_method_case():
    r = _rec()
    set_route(r, "rule", r"/x", method="post")
    assert r["routing"]["rule"]["method"] == "POST"


def test_set_route_empty_name_raises():
    with pytest.raises(ValueError, match="name"):
        set_route(_rec(), "", r"/x")


def test_set_route_empty_pattern_raises():
    with pytest.raises(ValueError, match="pattern"):
        set_route(_rec(), "rule", "")


def test_set_route_invalid_regex_raises():
    with pytest.raises(ValueError, match="Invalid regex"):
        set_route(_rec(), "bad", "[unclosed")


def test_set_route_unknown_method_raises():
    with pytest.raises(ValueError, match="Unknown HTTP method"):
        set_route(_rec(), "rule", r"/x", method="BREW")


def test_remove_route_removes_entry():
    r = _rec()
    set_route(r, "rule", r"/x")
    remove_route(r, "rule")
    assert "rule" not in r.get("routing", {})


def test_remove_route_idempotent():
    r = _rec()
    remove_route(r, "nonexistent")  # should not raise


def test_get_routes_empty():
    assert get_routes(_rec()) == {}


def test_get_routes_returns_copy():
    r = _rec()
    set_route(r, "rule", r"/x")
    routes = get_routes(r)
    routes["extra"] = {}
    assert "extra" not in r["routing"]


def test_match_route_matches_path():
    r = _rec(path="/webhooks/github")
    set_route(r, "github", r"/webhooks/github")
    assert match_route(r) == "github"


def test_match_route_respects_method():
    r = _rec(path="/hooks/x", method="GET")
    set_route(r, "post-rule", r"/hooks/.*", method="POST")
    assert match_route(r) is None


def test_match_route_wildcard_method():
    r = _rec(path="/hooks/x", method="DELETE")
    set_route(r, "any", r"/hooks/.*", method="*")
    assert match_route(r) == "any"


def test_match_route_returns_none_when_no_match():
    r = _rec(path="/other")
    set_route(r, "rule", r"/hooks/.*")
    assert match_route(r) is None


def test_filter_by_route():
    r1 = _rec()
    r2 = _rec()
    set_route(r1, "rule", r"/x")
    result = filter_by_route([r1, r2], "rule")
    assert result == [r1]
