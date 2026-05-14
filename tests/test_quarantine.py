"""Tests for hookdraft.quarantine and quarantine routes."""

import pytest

from hookdraft.quarantine import (
    filter_quarantined,
    filter_unquarantined,
    get_quarantine_reason,
    get_quarantine_source,
    is_quarantined,
    quarantine_record,
    unquarantine_record,
)
from hookdraft.storage import RequestRecord, RequestStore
from hookdraft.app import create_app


def _rec() -> RequestRecord:
    return RequestRecord(
        id="test-1",
        method="POST",
        path="/hook",
        headers={},
        body=None,
        timestamp="2024-01-01T00:00:00",
        status_code=200,
    )


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_is_quarantined_false_by_default():
    assert is_quarantined(_rec()) is False


def test_quarantine_record_sets_flag():
    r = _rec()
    quarantine_record(r)
    assert is_quarantined(r) is True


def test_quarantine_record_default_reason():
    r = _rec()
    quarantine_record(r)
    assert get_quarantine_reason(r) == "unspecified"


def test_quarantine_record_custom_reason():
    r = _rec()
    quarantine_record(r, reason="suspicious payload")
    assert get_quarantine_reason(r) == "suspicious payload"


def test_quarantine_record_strips_reason_whitespace():
    r = _rec()
    quarantine_record(r, reason="  bad data  ")
    assert get_quarantine_reason(r) == "bad data"


def test_quarantine_empty_reason_raises():
    r = _rec()
    with pytest.raises(ValueError):
        quarantine_record(r, reason="   ")


def test_quarantine_record_with_source():
    r = _rec()
    quarantine_record(r, reason="scan failed", source="AutoScanner")
    assert get_quarantine_source(r) == "autoscanner"


def test_quarantine_empty_source_raises():
    r = _rec()
    with pytest.raises(ValueError):
        quarantine_record(r, reason="bad", source="   ")


def test_get_quarantine_reason_none_when_not_quarantined():
    assert get_quarantine_reason(_rec()) is None


def test_get_quarantine_source_none_when_not_quarantined():
    assert get_quarantine_source(_rec()) is None


def test_unquarantine_removes_flag():
    r = _rec()
    quarantine_record(r, reason="test")
    unquarantine_record(r)
    assert is_quarantined(r) is False
    assert get_quarantine_reason(r) is None


def test_unquarantine_idempotent():
    r = _rec()
    unquarantine_record(r)  # should not raise
    assert is_quarantined(r) is False


def test_filter_quarantined():
    r1, r2, r3 = _rec(), _rec(), _rec()
    quarantine_record(r1, reason="x")
    quarantine_record(r3, reason="y")
    result = filter_quarantined([r1, r2, r3])
    assert result == [r1, r3]


def test_filter_unquarantined():
    r1, r2 = _rec(), _rec()
    quarantine_record(r1, reason="x")
    result = filter_unquarantined([r1, r2])
    assert result == [r2]


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

@pytest.fixture()
 def store():
    return RequestStore()


@pytest.fixture()
def client(store):
    app = create_app(store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client):
    resp = client.post("/hook", json={"event": "test"})
    return client.get("/requests").get_json()["requests"][0]["id"]


def test_quarantine_status_unknown_id(client):
    resp = client.get("/requests/nope/quarantine")
    assert resp.status_code == 404


def test_quarantine_unknown_id(client):
    resp = client.post("/requests/nope/quarantine", json={"reason": "bad"})
    assert resp.status_code == 404


def test_set_and_get_quarantine(client):
    req_id = _post_hook(client)
    resp = client.post(
        f"/requests/{req_id}/quarantine",
        json={"reason": "malformed body", "source": "RuleEngine"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["quarantined"] is True
    assert data["reason"] == "malformed body"
    assert data["source"] == "ruleengine"

    status = client.get(f"/requests/{req_id}/quarantine").get_json()
    assert status["quarantined"] is True


def test_delete_quarantine(client):
    req_id = _post_hook(client)
    client.post(f"/requests/{req_id}/quarantine", json={"reason": "test"})
    resp = client.delete(f"/requests/{req_id}/quarantine")
    assert resp.status_code == 200
    assert resp.get_json()["quarantined"] is False


def test_quarantine_bad_reason_returns_400(client):
    req_id = _post_hook(client)
    resp = client.post(f"/requests/{req_id}/quarantine", json={"reason": "   "})
    assert resp.status_code == 400
