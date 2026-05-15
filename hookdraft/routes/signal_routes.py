"""HTTP routes for managing signals on webhook records."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import signaling


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_signal_routes(app):
    bp = Blueprint("signals", __name__)

    @bp.get("/requests/<req_id>/signals")
    def list_signals(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"signals": signaling.get_signals(record)}), 200

    @bp.post("/requests/<req_id>/signals")
    def add_signal(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        name = body.get("name", "")
        detail = body.get("detail")
        try:
            signaling.raise_signal(record, name, detail)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"signals": signaling.get_signals(record)}), 200

    @bp.delete("/requests/<req_id>/signals/<signal_name>")
    def remove_signal(req_id: str, signal_name: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        signaling.clear_signal(record, signal_name)
        store.save(record)
        return jsonify({"signals": signaling.get_signals(record)}), 200

    @bp.delete("/requests/<req_id>/signals")
    def clear_signals(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        signaling.clear_all_signals(record)
        store.save(record)
        return jsonify({"signals": []}), 200

    app.register_blueprint(bp)
