"""HTTP routes for managing record quarantine state."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify, request

from hookdraft.quarantine import (
    get_quarantine_reason,
    get_quarantine_source,
    is_quarantined,
    quarantine_record,
    unquarantine_record,
)
from hookdraft.storage import RequestStore


def get_store(app: Flask) -> RequestStore:
    return app.config["STORE"]


def register_quarantine_routes(app: Flask) -> None:
    bp = Blueprint("quarantine", __name__)

    @bp.route("/requests/<req_id>/quarantine", methods=["GET"])
    def quarantine_status(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(
            {
                "quarantined": is_quarantined(record),
                "reason": get_quarantine_reason(record),
                "source": get_quarantine_source(record),
            }
        )

    @bp.route("/requests/<req_id>/quarantine", methods=["POST"])
    def quarantine_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        reason = body.get("reason", "unspecified")
        source = body.get("source")
        try:
            quarantine_record(record, reason=reason, source=source)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify(
            {
                "quarantined": True,
                "reason": get_quarantine_reason(record),
                "source": get_quarantine_source(record),
            }
        )

    @bp.route("/requests/<req_id>/quarantine", methods=["DELETE"])
    def unquarantine_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        unquarantine_record(record)
        store.save(record)
        return jsonify({"quarantined": False})

    app.register_blueprint(bp)
