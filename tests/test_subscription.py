"""Tests for hookdraft.subscription."""

import pytest
from hookdraft.subscription import (
    subscribe,
    unsubscribe,
    get_subscriptions,
    is_subscribed,
    subscriber_count,
    filter_by_subscriber,
)


def _rec(**kwargs):
    return dict(kwargs)


def test_get_subscriptions_empty_by_default():
    assert get_subscriptions(_rec()) == []


def test_subscriber_count_zero_by_default():
    assert subscriber_count(_rec()) == 0


def test_is_subscribed_false_by_default():
    assert is_subscribed(_rec(), "alice") is False


def test_subscribe_basic():
    rec = _rec()
    subscribe(rec, "alice")
    assert is_subscribed(rec, "alice") is True


def test_subscribe_normalises_case():
    rec = _rec()
    subscribe(rec, "Alice")
    assert is_subscribed(rec, "alice") is True


def test_subscribe_strips_whitespace():
    rec = _rec()
    subscribe(rec, "  bob  ")
    assert is_subscribed(rec, "bob") is True


def test_subscribe_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        subscribe(_rec(), "")


def test_subscribe_whitespace_only_raises():
    with pytest.raises(ValueError):
        subscribe(_rec(), "   ")


def test_subscribe_deduplicates():
    rec = _rec()
    subscribe(rec, "carol")
    subscribe(rec, "carol")
    assert subscriber_count(rec) == 1


def test_subscribe_with_channel():
    rec = _rec()
    subscribe(rec, "dave", channel="email")
    subs = get_subscriptions(rec)
    assert subs[0]["channel"] == "email"


def test_subscribe_empty_channel_raises():
    with pytest.raises(ValueError, match="Channel"):
        subscribe(_rec(), "eve", channel="  ")


def test_subscribe_channel_normalised():
    rec = _rec()
    subscribe(rec, "frank", channel="Slack")
    assert get_subscriptions(rec)[0]["channel"] == "slack"


def test_unsubscribe_removes_entry():
    rec = _rec()
    subscribe(rec, "grace")
    unsubscribe(rec, "grace")
    assert is_subscribed(rec, "grace") is False


def test_unsubscribe_idempotent():
    rec = _rec()
    unsubscribe(rec, "heidi")  # no error
    assert subscriber_count(rec) == 0


def test_subscriber_count_multiple():
    rec = _rec()
    subscribe(rec, "ivan")
    subscribe(rec, "judy")
    assert subscriber_count(rec) == 2


def test_filter_by_subscriber():
    r1 = _rec(id="1")
    r2 = _rec(id="2")
    subscribe(r1, "kate")
    result = filter_by_subscriber([r1, r2], "kate")
    assert result == [r1]


def test_filter_by_subscriber_empty_list():
    assert filter_by_subscriber([], "leo") == []
