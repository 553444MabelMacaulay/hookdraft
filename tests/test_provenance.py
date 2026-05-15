"""Tests for hookdraft.provenance and its HTTP routes."""

from __future__ import annotations

import pytest

from hookdraft.storage import RequestRecord
from hookdraft import provenance as prov
from hookdraft.app import create_app
from hookdraft.storage import RequestStore


def _rec():
    r = RequestRecord.__new__(RequestRecord)
    r.id = "test-id"
    r.meta = {}
    return r


# ---------------------------------------------------------------------------
# Unit tests for provenance.py
# ---------------------------------------------------------------------------

def test_has_provenance_false_by_default():
    assert prov.has_provenance(_rec()) is False


def test_get_provenance_none_by_default():
    assert prov.get_provenance(_rec()) is None


def test_set_provenance_basic():
    r = _rec()
    prov.set_provenance(r, "github")
    data = prov.get_provenance(r)
    assert data["source"] == "github"
    assert data["environment"] == "unknown"
    assert data["ref"] is None


def test_set_provenance_normalises_source_case():
    r = _rec()
    prov.set_provenance(r, "  GitHub  ")
    assert prov.get_provenance(r)["source"] == "github"


def test_set_provenance_with_environment_and_ref():
    r = _rec()
    prov.set_provenance(r, "stripe", environment="production", ref="evt_123")
    data = prov.get_provenance(r)
    assert data["environment"] == "production"
    assert data["ref"] == "evt_123"


def test_set_provenance_strips_ref_whitespace():
    r = _rec()
    prov.set_provenance(r, "stripe", ref="  ref-abc  ")
    assert prov.get_provenance(r)["ref"] == "ref-abc"


def test_set_provenance_empty_ref_stored_as_none():
    r = _rec()
    prov.set_provenance(r, "stripe", ref="   ")
    assert prov.get_provenance(r)["ref"] is None


def test_set_provenance_empty_source_raises():
    with pytest.raises(ValueError, match="empty"):
        prov.set_provenance(_rec(), "")


def test_set_provenance_invalid_environment_raises():
    with pytest.raises(ValueError, match="Invalid environment"):
        prov.set_provenance(_rec(), "github", environment="prod")


def test_clear_provenance_removes_data():
    r = _rec()
    prov.set_provenance(r, "github")
    prov.clear_provenance(r)
    assert prov.has_provenance(r) is False


def test_clear_provenance_idempotent():
    r = _rec()
    prov.clear_provenance(r)  # should not raise


def test_filter_by_source():
    r1, r2, r3 = _rec(), _rec(), _rec()
    prov.set_provenance(r1, "github")
    prov.set_provenance(r2, "stripe")
    result = prov.filter_by_source([r1, r2, r3], "github")
    assert result == [r1]


def test_filter_by_environment():
    r1, r2 = _rec(), _rec()
    prov.set_provenance(r1, "github", environment="production")
    prov.set_provenance(r2, "stripe", environment="staging")
    result = prov.filter_by_environment([r1, r2], "production")
    assert result == [r1]


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
    resp = client.post("/hooks/test", json={"x": 1})
    return resp.get_json()["id"]


def test_get_provenance_unknown_id(client):
    resp = client.get("/requests/no-such-id/provenance")
    assert resp.status_code == 404


def test_set_and_get_provenance(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/provenance", json={"source": "github", "environment": "staging"})
    assert resp.status_code == 200
    data = resp.get_json()["provenance"]
    assert data["source"] == "github"
    assert data["environment"] == "staging"


def test_set_provenance_invalid_returns_400(client):
    rid = _post_hook(client)
    resp = client.put(f"/requests/{rid}/provenance", json={"source": ""})
    assert resp.status_code == 400


def test_delete_provenance(client):
    rid = _post_hook(client)
    client.put(f"/requests/{rid}/provenance", json={"source": "stripe"})
    resp = client.delete(f"/requests/{rid}/provenance")
    assert resp.status_code == 200
    resp2 = client.get(f"/requests/{rid}/provenance")
    assert resp2.get_json()["provenance"] is None
