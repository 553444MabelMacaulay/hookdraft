"""HTTP routes for managing the watchlist on stored requests."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft.storage import RequestStore
from hookdraft import watchlist as wl


def get_store(app) -> RequestStore:
    return app.config["store"]


def register_watchlist_routes(app) -> None:
    bp = Blueprint("watchlist", __name__)

    @bp.route("/requests/<req_id>/watch", methods=["GET"])
    def watch_status(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "watched": wl.is_watched(record),
            "reason": wl.get_watch_reason(record),
        })

    @bp.route("/requests/<req_id>/watch", methods=["POST"])
    def watch_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        reason = body.get("reason", "")
        wl.watch_record(record, reason=reason)
        return jsonify({
            "watched": True,
            "reason": wl.get_watch_reason(record),
        })

    @bp.route("/requests/<req_id>/watch", methods=["DELETE"])
    def unwatch_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        wl.unwatch_record(record)
        return jsonify({"watched": False})

    app.register_blueprint(bp)
