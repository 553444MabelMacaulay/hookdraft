"""Tests for hookdraft.transformation."""

import pytest

from hookdraft.transformation import (
    apply_transformation,
    clear_transformation,
    get_transformation,
    set_transformation,
)


def _rec() -> dict:
    return {"id": "abc", "body": {"secret": "s3cr3t", "name": "alice"}}


# --- set / get / clear ---

def test_get_transformation_none_by_default():
    assert get_transformation(_rec()) is None


def test_set_transformation_stores_steps():
    rec = _rec()
    steps = [{"op": "drop", "field": "secret"}]
    set_transformation(rec, steps)
    assert get_transformation(rec) == steps


def test_set_transformation_rejects_unknown_op():
    with pytest.raises(ValueError, match="unknown op"):
        set_transformation(_rec(), [{"op": "explode", "field": "x"}])


def test_set_transformation_rejects_missing_field():
    with pytest.raises(ValueError, match="'field' is required"):
        set_transformation(_rec(), [{"op": "drop"}])


def test_set_transformation_rename_requires_to():
    with pytest.raises(ValueError, match="requires 'to'"):
        set_transformation(_rec(), [{"op": "rename", "field": "name"}])


def test_set_transformation_rejects_non_list():
    with pytest.raises(TypeError, match="must be a list"):
        set_transformation(_rec(), {"op": "drop", "field": "x"})  # type: ignore


def test_clear_transformation_removes_steps():
    rec = _rec()
    set_transformation(rec, [{"op": "drop", "field": "name"}])
    clear_transformation(rec)
    assert get_transformation(rec) is None


def test_clear_transformation_idempotent():
    rec = _rec()
    clear_transformation(rec)  # should not raise
    assert get_transformation(rec) is None


# --- apply_transformation ---

def test_apply_drop():
    payload = {"name": "alice", "secret": "s3cr3t"}
    result = apply_transformation(payload, [{"op": "drop", "field": "secret"}])
    assert "secret" not in result
    assert result["name"] == "alice"


def test_apply_mask_default():
    payload = {"token": "abc123", "user": "bob"}
    result = apply_transformation(payload, [{"op": "mask", "field": "token"}])
    assert result["token"] == "***"
    assert result["user"] == "bob"


def test_apply_mask_custom_string():
    payload = {"token": "abc123"}
    result = apply_transformation(payload, [{"op": "mask", "field": "token", "mask": "[REDACTED]"}])
    assert result["token"] == "[REDACTED]"


def test_apply_rename():
    payload = {"old_name": "value"}
    result = apply_transformation(payload, [{"op": "rename", "field": "old_name", "to": "new_name"}])
    assert "old_name" not in result
    assert result["new_name"] == "value"


def test_apply_missing_field_is_noop():
    payload = {"a": 1}
    result = apply_transformation(payload, [{"op": "drop", "field": "nonexistent"}])
    assert result == {"a": 1}


def test_apply_non_dict_payload_returned_as_is():
    assert apply_transformation("plain string", [{"op": "drop", "field": "x"}]) == "plain string"
    assert apply_transformation(None, []) is None


def test_apply_does_not_mutate_original():
    payload = {"secret": "s3cr3t", "name": "alice"}
    apply_transformation(payload, [{"op": "drop", "field": "secret"}])
    assert "secret" in payload
