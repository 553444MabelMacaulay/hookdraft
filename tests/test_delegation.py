"""Tests for hookdraft.delegation and its HTTP routes."""

import pytest

from hookdraft.storage import RequestRecord
from hookdraft import delegation as dl


def _rec():
    r = RequestRecord(
        method="POST",
        path="/hook",
        headers={},
        body=None,
        source_ip="127.0.0.1",
    )
    r.metadata = {}
    return r


# --- unit tests ---

def test_is_delegated_false_by_default():
    assert dl.is_delegated(_rec()) is False


def test_delegate_record_sets_flag():
    r = _rec()
    dl.delegate_record(r, "alice")
    assert dl.is_delegated(r) is True


def test_delegate_record_stores_owner_lowercased():
    r = _rec()
    dl.delegate_record(r, "  Bob  ")
    assert dl.get_owner(r) == "bob"


def test_delegate_record_stores_note():
    r = _rec()
    dl.delegate_record(r, "alice", note="please review")
    assert dl.get_delegation(r)["note"] == "please review"


def test_delegate_record_note_none_when_blank():
    r = _rec()
    dl.delegate_record(r, "alice", note="   ")
    assert dl.get_delegation(r)["note"] is None


def test_delegate_record_empty_owner_raises():
    with pytest.raises(ValueError, match="empty"):
        dl.delegate_record(_rec(), "")


def test_delegate_record_long_owner_raises():
    with pytest.raises(ValueError):
        dl.delegate_record(_rec(), "x" * 65)


def test_undelegate_record_removes_flag():
    r = _rec()
    dl.delegate_record(r, "alice")
    dl.undelegate_record(r)
    assert dl.is_delegated(r) is False


def test_undelegate_idempotent():
    r = _rec()
    dl.undelegate_record(r)  # should not raise
    assert dl.is_delegated(r) is False


def test_filter_delegated():
    r1, r2, r3 = _rec(), _rec(), _rec()
    dl.delegate_record(r1, "alice")
    dl.delegate_record(r3, "bob")
    result = dl.filter_delegated([r1, r2, r3])
    assert r1 in result and r3 in result and r2 not in result


def test_filter_by_owner():
    r1, r2 = _rec(), _rec()
    dl.delegate_record(r1, "alice")
    dl.delegate_record(r2, "bob")
    assert dl.filter_by_owner([r1, r2], "Alice") == [r1]


# --- route tests ---

@pytest.fixture()
def store():
    from hookdraft.storage import RequestStore
    return RequestStore()


@pytest.fixture()
def client(store):
    from hookdraft.app import create_app
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    rv = client.post("/hooks/test", json={"x": 1})
    return rv.get_json()["id"]


def test_get_delegation_unknown_id(client):
    rv = client.get("/requests/no-such-id/delegation")
    assert rv.status_code == 404


def test_set_and_get_delegation(client):
    rid = _post_hook(client)
    rv = client.put(f"/requests/{rid}/delegation", json={"owner": "carol", "note": "urgent"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["owner"] == "carol"
    assert data["note"] == "urgent"

    rv2 = client.get(f"/requests/{rid}/delegation")
    assert rv2.status_code == 200
    assert rv2.get_json()["delegated"] is True


def test_set_delegation_empty_owner_returns_400(client):
    rid = _post_hook(client)
    rv = client.put(f"/requests/{rid}/delegation", json={"owner": ""})
    assert rv.status_code == 400


def test_delete_delegation(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/delegation", json={"owner": "dave"})
    rv = client.delete(f"/requests/{rid}/delegation")
    assert rv.status_code == 200
    assert rv.get_json()["delegated"] is False
