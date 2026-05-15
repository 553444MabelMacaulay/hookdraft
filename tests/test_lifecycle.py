"""Unit tests for hookdraft.lifecycle."""

import pytest
from hookdraft.lifecycle import (
    set_lifecycle_state,
    clear_lifecycle_state,
    get_lifecycle_state,
    get_lifecycle_actor,
    get_lifecycle_note,
    has_lifecycle_state,
    filter_by_lifecycle_state,
    filter_unlifecycled,
)


def _rec(extra=None):
    r = {"id": "abc"}
    if extra:
        r.update(extra)
    return r


def test_get_lifecycle_state_none_by_default():
    assert get_lifecycle_state(_rec()) is None


def test_has_lifecycle_state_false_by_default():
    assert not has_lifecycle_state(_rec())


def test_set_lifecycle_state_basic():
    r = _rec()
    set_lifecycle_state(r, "new")
    assert get_lifecycle_state(r) == "new"
    assert has_lifecycle_state(r)


def test_set_lifecycle_state_normalises_case():
    r = _rec()
    set_lifecycle_state(r, "PROCESSING")
    assert get_lifecycle_state(r) == "processing"


def test_set_lifecycle_state_strips_whitespace():
    r = _rec()
    set_lifecycle_state(r, "  processed  ")
    assert get_lifecycle_state(r) == "processed"


def test_set_lifecycle_state_with_actor():
    r = _rec()
    set_lifecycle_state(r, "failed", actor="Alice")
    assert get_lifecycle_actor(r) == "alice"


def test_set_lifecycle_state_with_note():
    r = _rec()
    set_lifecycle_state(r, "ignored", note="Duplicate event")
    assert get_lifecycle_note(r) == "Duplicate event"


def test_set_lifecycle_state_invalid_raises():
    r = _rec()
    with pytest.raises(ValueError, match="Unknown lifecycle state"):
        set_lifecycle_state(r, "unknown_state")


def test_set_lifecycle_state_empty_raises():
    r = _rec()
    with pytest.raises(ValueError, match="must not be empty"):
        set_lifecycle_state(r, "")


def test_set_lifecycle_state_empty_actor_raises():
    r = _rec()
    with pytest.raises(ValueError, match="Actor must not be empty"):
        set_lifecycle_state(r, "new", actor="   ")


def test_set_lifecycle_state_empty_note_raises():
    r = _rec()
    with pytest.raises(ValueError, match="Note must not be empty"):
        set_lifecycle_state(r, "new", note="   ")


def test_clear_lifecycle_state():
    r = _rec()
    set_lifecycle_state(r, "new")
    clear_lifecycle_state(r)
    assert get_lifecycle_state(r) is None
    assert not has_lifecycle_state(r)


def test_clear_lifecycle_state_idempotent():
    r = _rec()
    clear_lifecycle_state(r)
    assert get_lifecycle_state(r) is None


def test_filter_by_lifecycle_state():
    r1 = _rec()
    r2 = _rec()
    r3 = _rec()
    set_lifecycle_state(r1, "new")
    set_lifecycle_state(r2, "processed")
    set_lifecycle_state(r3, "new")
    result = filter_by_lifecycle_state([r1, r2, r3], "new")
    assert result == [r1, r3]


def test_filter_unlifecycled():
    r1 = _rec()
    r2 = _rec()
    set_lifecycle_state(r1, "new")
    result = filter_unlifecycled([r1, r2])
    assert result == [r2]
