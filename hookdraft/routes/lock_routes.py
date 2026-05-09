"""HTTP routes for record locking."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import locking
from hookdraft.storage import RequestStore


def get_store(app):
    return app.config["store"]


def register_lock_routes(app, store: RequestStore) -> None:
    bp = Blueprint("lock", __name__)

    @bp.route("/requests/<req_id>/lock", methods=["GET"])
    def lock_status(req_id: str):
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "locked": locking.is_locked(record),
            "reason": locking.get_lock_reason(record),
        })

    @bp.route("/requests/<req_id>/lock", methods=["POST"])
    def lock_request(req_id: str):
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        reason = body.get("reason", "")
        locking.lock_record(record, reason)
        return jsonify({
            "locked": True,
            "reason": locking.get_lock_reason(record),
        })

    @bp.route("/requests/<req_id>/lock", methods=["DELETE"])
    def unlock_request(req_id: str):
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        locking.unlock_record(record)
        return jsonify({"locked": False})

    app.register_blueprint(bp)
