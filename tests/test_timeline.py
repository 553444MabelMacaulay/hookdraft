"""Unit tests for hookdraft.timeline."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft.timeline import (
    add_event,
    get_events,
    clear_events,
    has_events,
    filter_by_event_name,
)


def _rec():
    return RequestRecord(
        id="r1",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00+00:00",
    )


def test_get_events_empty_by_default():
    assert get_events(_rec()) == []


def test_has_events_false_by_default():
    assert has_events(_rec()) is False


def test_add_event_basic():
    r = _rec()
    event = add_event(r, "received")
    assert event["name"] == "received"
    assert "timestamp" in event
    assert "detail" not in event


def test_add_event_with_detail():
    r = _rec()
    event = add_event(r, "processed", detail="ok")
    assert event["detail"] == "ok"


def test_add_event_strips_whitespace_from_name():
    r = _rec()
    event = add_event(r, "  sent  ")
    assert event["name"] == "sent"


def test_add_event_detail_whitespace_only_is_omitted():
    r = _rec()
    event = add_event(r, "done", detail="   ")
    assert "detail" not in event


def test_add_event_empty_name_raises():
    r = _rec()
    with pytest.raises(ValueError):
        add_event(r, "")


def test_add_event_whitespace_name_raises():
    r = _rec()
    with pytest.raises(ValueError):
        add_event(r, "   ")


def test_add_event_custom_timestamp():
    r = _rec()
    ts = "2024-06-01T12:00:00+00:00"
    event = add_event(r, "queued", timestamp=ts)
    assert event["timestamp"] == ts


def test_get_events_returns_in_order():
    r = _rec()
    add_event(r, "first")
    add_event(r, "second")
    add_event(r, "third")
    names = [e["name"] for e in get_events(r)]
    assert names == ["first", "second", "third"]


def test_has_events_true_after_add():
    r = _rec()
    add_event(r, "start")
    assert has_events(r) is True


def test_clear_events_removes_all():
    r = _rec()
    add_event(r, "a")
    add_event(r, "b")
    clear_events(r)
    assert get_events(r) == []
    assert has_events(r) is False


def test_clear_events_idempotent():
    r = _rec()
    clear_events(r)
    clear_events(r)
    assert get_events(r) == []


def test_filter_by_event_name_match():
    r1, r2 = _rec(), _rec()
    r2.id = "r2"
    add_event(r1, "error")
    add_event(r2, "success")
    result = filter_by_event_name([r1, r2], "error")
    assert result == [r1]


def test_filter_by_event_name_case_insensitive():
    r = _rec()
    add_event(r, "Retry")
    assert filter_by_event_name([r], "retry") == [r]


def test_filter_by_event_name_no_match():
    r = _rec()
    add_event(r, "received")
    assert filter_by_event_name([r], "missing") == []
