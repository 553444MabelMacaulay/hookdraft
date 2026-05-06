"""HTTP routes for flagging / unflagging webhook request records."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify, request

from hookdraft.flagging import (
    flag_record,
    get_flag_reason,
    is_flagged,
    unflag_record,
)
from hookdraft.storage import RequestStore


def get_store(app: Flask) -> RequestStore:
    return app.config["STORE"]


def register_flag_routes(app: Flask) -> None:
    bp = Blueprint("flag_routes", __name__)

    @bp.route("/requests/<req_id>/flag", methods=["GET"])
    def flag_status(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"flagged": is_flagged(record), "reason": get_flag_reason(record)})

    @bp.route("/requests/<req_id>/flag", methods=["POST"])
    def flag_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        reason = body.get("reason", "")
        flag_record(record, reason=reason)
        store.save(record)
        return jsonify({"flagged": True, "reason": get_flag_reason(record)}), 200

    @bp.route("/requests/<req_id>/flag", methods=["DELETE"])
    def unflag_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        unflag_record(record)
        store.save(record)
        return jsonify({"flagged": False, "reason": ""}), 200

    app.register_blueprint(bp)
