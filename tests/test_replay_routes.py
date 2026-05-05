import json
import pytest
from unittest.mock import patch, MagicMock

from hookdraft.app import create_app
from hookdraft.storage import RequestStore


@pytest.fixture()
def client(tmp_path):
    store = RequestStore(str(tmp_path / "hooks.json"))
    app = create_app(store=store)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_hook(client, body=None, headers=None):
    """Helper: capture a webhook and return its record id."""
    extra = headers or {}
    resp = client.post(
        "/hooks/test",
        data=json.dumps(body or {"event": "ping"}),
        content_type="application/json",
        headers=extra,
    )
    assert resp.status_code == 200
    return resp.get_json()["id"]


def test_replay_unknown_id(client):
    resp = client.post("/replay/nonexistent-id")
    assert resp.status_code == 404
    assert "not found" in resp.get_json()["error"]


def test_replay_no_target_url(client):
    record_id = _post_hook(client)
    resp = client.post("/replay/" + record_id, content_type="application/json")
    assert resp.status_code == 422
    assert "target URL" in resp.get_json()["error"]


def test_replay_with_override_url(client):
    record_id = _post_hook(client)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"ok": true}'

    with patch("hookdraft.routes.replay_routes.http.request", return_value=mock_response) as mock_req:
        resp = client.post(
            "/replay/" + record_id,
            data=json.dumps({"override_url": "http://example.com/webhook"}),
            content_type="application/json",
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["replayed_id"] == record_id
    assert data["status_code"] == 200
    assert data["target_url"] == "http://example.com/webhook"
    mock_req.assert_called_once()


def test_replay_propagates_502_on_network_error(client):
    import requests as real_requests

    record_id = _post_hook(client)

    with patch(
        "hookdraft.routes.replay_routes.http.request",
        side_effect=real_requests.exceptions.ConnectionError("refused"),
    ):
        resp = client.post(
            "/replay/" + record_id,
            data=json.dumps({"override_url": "http://example.com/webhook"}),
            content_type="application/json",
        )

    assert resp.status_code == 502
    assert "replay failed" in resp.get_json()["error"]
