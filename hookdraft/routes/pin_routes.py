"""Flask routes for pinning / unpinning captured webhook requests."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify

from hookdraft import pinning
from hookdraft.storage import RequestStore


def get_store(app: Flask) -> RequestStore:
    return app.config["STORE"]


def register_pin_routes(app: Flask) -> None:
    bp = Blueprint("pin", __name__)

    @bp.route("/requests/<request_id>/pin", methods=["POST"])
    def pin_request(request_id: str):
        store = get_store(app)
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        pinning.pin_record(record)
        store.save(record)
        return jsonify({"id": record.id, "pinned": True}), 200

    @bp.route("/requests/<request_id>/pin", methods=["DELETE"])
    def unpin_request(request_id: str):
        store = get_store(app)
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        pinning.unpin_record(record)
        store.save(record)
        return jsonify({"id": record.id, "pinned": False}), 200

    @bp.route("/requests/<request_id>/pin", methods=["GET"])
    def pin_status(request_id: str):
        store = get_store(app)
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": record.id, "pinned": pinning.is_pinned(record)}), 200

    @bp.route("/requests/pinned", methods=["GET"])
    def list_pinned():
        store = get_store(app)
        records = pinning.filter_pinned(store.all())
        return jsonify([r.to_dict() for r in records]), 200

    app.register_blueprint(bp)
