"""Tests for payload diffing utilities and the /diff route."""

import json
import pytest
from hookdraft.diff import diff_payloads, _flatten, _normalize
from hookdraft.app import create_app


# --- Unit tests for diff_payloads ---

def test_identical_payloads():
    a = json.dumps({"event": "push", "ref": "main"})
    result = diff_payloads(a, a)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["changed"] == []
    assert "event" in result["same"]
    assert "ref" in result["same"]


def test_added_key():
    a = json.dumps({"event": "push"})
    b = json.dumps({"event": "push", "user": "alice"})
    result = diff_payloads(a, b)
    assert "user" in result["added"]
    assert result["removed"] == []


def test_removed_key():
    a = json.dumps({"event": "push", "user": "alice"})
    b = json.dumps({"event": "push"})
    result = diff_payloads(a, b)
    assert "user" in result["removed"]
    assert result["added"] == []


def test_changed_value():
    a = json.dumps({"status": "pending"})
    b = json.dumps({"status": "complete"})
    result = diff_payloads(a, b)
    assert len(result["changed"]) == 1
    assert result["changed"][0]["key"] == "status"
    assert result["changed"][0]["from"] == "pending"
    assert result["changed"][0]["to"] == "complete"


def test_nested_diff():
    a = json.dumps({"repo": {"name": "hookdraft", "private": False}})
    b = json.dumps({"repo": {"name": "hookdraft", "private": True}})
    result = diff_payloads(a, b)
    changed_keys = [c["key"] for c in result["changed"]]
    assert "repo.private" in changed_keys


def test_non_json_payloads_equal():
    result = diff_payloads("hello", "hello")
    assert result["same"] == ["<body>"]
    assert result["changed"] == []


def test_non_json_payloads_differ():
    result = diff_payloads("hello", "world")
    assert len(result["changed"]) == 1
    assert result["changed"][0]["from"] == "hello"
    assert result["changed"][0]["to"] == "world"


# --- Integration tests for the /diff route ---

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def post_hook(client, payload):
    return client.post(
        "/hooks/test",
        data=json.dumps(payload),
        content_type="application/json",
    )


def test_diff_route(client):
    r1 = post_hook(client, {"status": "pending"})
    r2 = post_hook(client, {"status": "complete"})
    id1 = r1.get_json()["id"]
    id2 = r2.get_json()["id"]

    resp = client.get(f"/requests/{id1}/diff/{id2}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["request_a"] == id1
    assert data["request_b"] == id2
    changed_keys = [c["key"] for c in data["diff"]["changed"]]
    assert "status" in changed_keys


def test_diff_route_missing_id(client):
    post_hook(client, {"x": 1})
    resp = client.get("/requests/nonexistent-a/diff/nonexistent-b")
    assert resp.status_code == 404
