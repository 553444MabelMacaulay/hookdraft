"""Tests for hookdraft.redaction."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft.redaction import (
    redact_record,
    is_redacted,
    get_redaction_mask,
    _MASK,
)


def _rec(body=None):
    r = RequestRecord(
        method="POST",
        path="/hook",
        headers={},
        body=body,
        source_ip="127.0.0.1",
    )
    return r


def test_get_redaction_mask_returns_string():
    assert isinstance(get_redaction_mask(), str)
    assert get_redaction_mask() == _MASK


def test_is_redacted_false_by_default():
    assert is_redacted(_rec()) is False


def test_redact_none_body_is_noop():
    r = _rec(body=None)
    redact_record(r)
    assert r.body is None
    # Even with None body the meta flag should NOT be set
    assert is_redacted(r) is False


def test_redact_default_sensitive_keys():
    r = _rec(body={"username": "alice", "password": "s3cr3t", "token": "abc123"})
    redact_record(r)
    assert r.body["username"] == "alice"
    assert r.body["password"] == _MASK
    assert r.body["token"] == _MASK


def test_redact_sets_meta_flag():
    r = _rec(body={"password": "x"})
    redact_record(r)
    assert is_redacted(r) is True


def test_redact_case_insensitive_keys():
    r = _rec(body={"Password": "secret", "TOKEN": "tok", "normal": "keep"})
    redact_record(r)
    assert r.body["Password"] == _MASK
    assert r.body["TOKEN"] == _MASK
    assert r.body["normal"] == "keep"


def test_redact_nested_dict():
    r = _rec(body={"user": {"email": "a@b.com", "api_key": "xyz"}})
    redact_record(r)
    assert r.body["user"]["email"] == "a@b.com"
    assert r.body["user"]["api_key"] == _MASK


def test_redact_list_of_dicts():
    r = _rec(body=[{"token": "t1"}, {"token": "t2", "name": "bob"}])
    redact_record(r)
    assert r.body[0]["token"] == _MASK
    assert r.body[1]["token"] == _MASK
    assert r.body[1]["name"] == "bob"


def test_redact_extra_keys():
    r = _rec(body={"credit_card": "4111111111111111", "cvv": "123", "name": "Alice"})
    redact_record(r, extra_keys=["credit_card", "cvv"])
    assert r.body["credit_card"] == _MASK
    assert r.body["cvv"] == _MASK
    assert r.body["name"] == "Alice"


def test_redact_extra_keys_case_insensitive():
    r = _rec(body={"CreditCard": "4111"})
    redact_record(r, extra_keys=["creditcard"])
    assert r.body["CreditCard"] == _MASK


def test_redact_non_dict_body_unchanged():
    r = _rec(body="plain text body")
    redact_record(r)
    # Strings are not dicts/lists — value unchanged but flag still set
    assert r.body == "plain text body"
    assert is_redacted(r) is True
