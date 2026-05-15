"""Tests for hookdraft.workflow."""

import pytest

from hookdraft.workflow import (
    clear_workflow_state,
    filter_by_workflow_state,
    get_workflow_actor,
    get_workflow_note,
    get_workflow_state,
    set_workflow_state,
)


def _rec():
    return {"id": "test-1"}


def test_get_workflow_state_none_by_default():
    assert get_workflow_state(_rec()) is None


def test_get_workflow_actor_none_by_default():
    assert get_workflow_actor(_rec()) is None


def test_get_workflow_note_none_by_default():
    assert get_workflow_note(_rec()) is None


def test_set_workflow_state_basic():
    r = _rec()
    set_workflow_state(r, "pending")
    assert get_workflow_state(r) == "pending"


def test_set_workflow_state_normalises_case():
    r = _rec()
    set_workflow_state(r, "PENDING")
    assert get_workflow_state(r) == "pending"


def test_set_workflow_state_with_actor():
    r = _rec()
    set_workflow_state(r, "pending", actor="Alice")
    assert get_workflow_actor(r) == "alice"


def test_set_workflow_state_with_note():
    r = _rec()
    set_workflow_state(r, "pending", note="Initial triage")
    assert get_workflow_note(r) == "Initial triage"


def test_set_workflow_state_invalid_raises():
    r = _rec()
    with pytest.raises(ValueError, match="Invalid workflow state"):
        set_workflow_state(r, "flying")


def test_set_workflow_state_invalid_transition_raises():
    r = _rec()
    set_workflow_state(r, "pending")
    with pytest.raises(ValueError, match="Cannot transition"):
        set_workflow_state(r, "approved")


def test_set_workflow_state_valid_transition():
    r = _rec()
    set_workflow_state(r, "pending")
    set_workflow_state(r, "in_review")
    assert get_workflow_state(r) == "in_review"


def test_set_workflow_state_closed_no_transitions():
    r = _rec()
    set_workflow_state(r, "pending")
    set_workflow_state(r, "rejected")
    set_workflow_state(r, "closed")
    with pytest.raises(ValueError, match="Cannot transition"):
        set_workflow_state(r, "pending")


def test_set_workflow_state_empty_actor_raises():
    r = _rec()
    with pytest.raises(ValueError, match="actor"):
        set_workflow_state(r, "pending", actor="   ")


def test_set_workflow_state_empty_note_raises():
    r = _rec()
    with pytest.raises(ValueError, match="note"):
        set_workflow_state(r, "pending", note="")


def test_clear_workflow_state():
    r = _rec()
    set_workflow_state(r, "pending")
    clear_workflow_state(r)
    assert get_workflow_state(r) is None


def test_clear_workflow_state_idempotent():
    r = _rec()
    clear_workflow_state(r)
    assert get_workflow_state(r) is None


def test_filter_by_workflow_state():
    r1, r2, r3 = _rec(), _rec(), _rec()
    set_workflow_state(r1, "pending")
    set_workflow_state(r2, "pending")
    set_workflow_state(r3, "in_review")
    result = filter_by_workflow_state([r1, r2, r3], "pending")
    assert result == [r1, r2]


def test_filter_by_workflow_state_invalid_raises():
    with pytest.raises(ValueError):
        filter_by_workflow_state([], "unknown")
