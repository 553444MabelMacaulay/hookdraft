"""HTTP routes for the delegation feature."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import delegation as dl


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_delegation_routes(app):
    bp = Blueprint("delegation", __name__)

    @bp.route("/requests/<req_id>/delegation", methods=["GET"])
    def get_delegation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        info = dl.get_delegation(record)
        if info is None:
            return jsonify({"delegated": False}), 200
        return jsonify({"delegated": True, **info}), 200

    @bp.route("/requests/<req_id>/delegation", methods=["PUT"])
    def set_delegation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        owner = body.get("owner", "")
        note = body.get("note")
        try:
            dl.delegate_record(record, owner, note)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(dl.get_delegation(record)), 200

    @bp.route("/requests/<req_id>/delegation", methods=["DELETE"])
    def delete_delegation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        dl.undelegate_record(record)
        return jsonify({"delegated": False}), 200

    app.register_blueprint(bp)
