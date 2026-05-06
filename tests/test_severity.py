"""Unit tests for hookdraft/severity.py."""

import pytest
from hookdraft.storage import RequestRecord
from hookdraft import severity as sev


def _rec(record_id="abc"):
    r = RequestRecord(
        id=record_id,
        method="POST",
        path="/hook",
        headers={},
        body="{}",
        timestamp="2024-01-01T00:00:00",
    )
    r.meta = {}
    return r


def test_set_severity_info():
    r = _rec()
    sev.set_severity(r, "info")
    assert r.meta["severity"] == "info"


def test_set_severity_warning():
    r = _rec()
    sev.set_severity(r, "warning")
    assert r.meta["severity"] == "warning"


def test_set_severity_error():
    r = _rec()
    sev.set_severity(r, "error")
    assert r.meta["severity"] == "error"


def test_set_severity_normalises_case():
    r = _rec()
    sev.set_severity(r, "  WARNING  ")
    assert r.meta["severity"] == "warning"


def test_set_severity_invalid_raises():
    r = _rec()
    with pytest.raises(ValueError, match="Invalid severity"):
        sev.set_severity(r, "critical")


def test_set_severity_empty_raises():
    r = _rec()
    with pytest.raises(ValueError, match="must not be empty"):
        sev.set_severity(r, "")


def test_clear_severity():
    r = _rec()
    sev.set_severity(r, "error")
    sev.clear_severity(r)
    assert r.meta.get("severity") is None


def test_clear_severity_idempotent():
    r = _rec()
    sev.clear_severity(r)  # no error when not set
    assert r.meta.get("severity") is None


def test_get_severity_none_by_default():
    r = _rec()
    assert sev.get_severity(r) is None


def test_filter_by_severity():
    records = [_rec("a"), _rec("b"), _rec("c")]
    sev.set_severity(records[0], "info")
    sev.set_severity(records[1], "error")
    result = sev.filter_by_severity(records, "info")
    assert len(result) == 1
    assert result[0].id == "a"


def test_filter_by_min_severity():
    records = [_rec("a"), _rec("b"), _rec("c")]
    sev.set_severity(records[0], "info")
    sev.set_severity(records[1], "warning")
    sev.set_severity(records[2], "error")
    result = sev.filter_by_min_severity(records, "warning")
    ids = {r.id for r in result}
    assert ids == {"b", "c"}


def test_filter_by_min_severity_invalid_raises():
    with pytest.raises(ValueError, match="Invalid min_level"):
        sev.filter_by_min_severity([], "critical")
