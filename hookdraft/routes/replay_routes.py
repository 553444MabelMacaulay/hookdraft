from flask import Blueprint, jsonify, request, current_app
from hookdraft.storage import RequestStore


def register_replay_routes(app):
    """Register replay-related routes on the Flask app."""

    @app.route("/replay/<request_id>", methods=["POST"])
    def replay_request(request_id):
        """Replay a previously captured webhook request.

        Optionally accepts a JSON body with an ``override_url`` field to
        redirect the replayed request to a different target endpoint.
        Returns the status code and response body received from the target.
        """
        import requests as http

        store: RequestStore = current_app.config["store"]
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "request not found"}), 404

        body = request.get_json(silent=True) or {}
        target_url = body.get("override_url") or record.headers.get(
            "X-Original-Url", ""
        )

        if not target_url:
            return (
                jsonify(
                    {
                        "error": (
                            "no target URL available; provide override_url in body "
                            "or ensure X-Original-Url header was captured"
                        )
                    }
                ),
                422,
            )

        # Forward the original payload with the original content-type.
        forward_headers = {
            k: v
            for k, v in record.headers.items()
            if k.lower() not in ("host", "content-length")
        }

        try:
            resp = http.request(
                method=record.method,
                url=target_url,
                data=record.body.encode() if isinstance(record.body, str) else record.body,
                headers=forward_headers,
                timeout=10,
            )
        except http.exceptions.RequestException as exc:
            return jsonify({"error": f"replay failed: {exc}"}), 502

        return (
            jsonify(
                {
                    "replayed_id": request_id,
                    "target_url": target_url,
                    "status_code": resp.status_code,
                    "response_body": resp.text[:2000],
                }
            ),
            200,
        )
