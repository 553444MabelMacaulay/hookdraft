"""HTTP routes for resolution management."""

from flask import Blueprint, jsonify, request, current_app
from hookdraft.resolution import (
    resolve_record,
    unresolve_record,
    is_resolved,
    get_resolution,
)


def get_store():
    return current_app.config["REQUEST_STORE"]


def register_resolution_routes(app):
    bp = Blueprint("resolution", __name__)

    @bp.route("/requests/<request_id>/resolution", methods=["GET"])
    def get_resolution_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"resolution": get_resolution(record)}), 200

    @bp.route("/requests/<request_id>/resolution", methods=["PUT"])
    def set_resolution_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        data = request.get_json(silent=True) or {}
        resolver = data.get("resolver", "")
        note = data.get("note")
        try:
            resolve_record(record, resolver, note=note)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"resolution": get_resolution(record)}), 200

    @bp.route("/requests/<request_id>/resolution", methods=["DELETE"])
    def delete_resolution_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        unresolve_record(record)
        store.save(record)
        return jsonify({"resolution": None}), 200

    app.register_blueprint(bp)
