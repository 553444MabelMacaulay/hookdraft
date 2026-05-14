"""HTTP routes for deprecation management."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import deprecation as dep_module


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_deprecation_routes(app):
    bp = Blueprint("deprecation", __name__)

    @bp.route("/requests/<req_id>/deprecation", methods=["GET"])
    def get_deprecation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        info = dep_module.get_deprecation(record)
        if info is None:
            return jsonify({"deprecated": False}), 200
        return jsonify({"deprecated": True, **info}), 200

    @bp.route("/requests/<req_id>/deprecation", methods=["PUT"])
    def set_deprecation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        body = request.get_json(silent=True) or {}
        reason = body.get("reason", "other")
        note = body.get("note")
        try:
            dep_module.deprecate_record(record, reason=reason, note=note)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify(dep_module.get_deprecation(record)), 200

    @bp.route("/requests/<req_id>/deprecation", methods=["DELETE"])
    def delete_deprecation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        dep_module.undeprecate_record(record)
        store.save(record)
        return jsonify({"deprecated": False}), 200

    app.register_blueprint(bp)
