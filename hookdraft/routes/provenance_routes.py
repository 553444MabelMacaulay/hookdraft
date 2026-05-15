"""HTTP routes for provenance management."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app

from hookdraft import provenance as prov_module


def get_store():
    return current_app.config["store"]


def register_provenance_routes(app):
    bp = Blueprint("provenance", __name__)

    @bp.route("/requests/<req_id>/provenance", methods=["GET"])
    def get_provenance_route(req_id):
        record = get_store().get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        data = prov_module.get_provenance(record)
        if data is None:
            return jsonify({"provenance": None}), 200
        return jsonify({"provenance": data}), 200

    @bp.route("/requests/<req_id>/provenance", methods=["PUT"])
    def set_provenance_route(req_id):
        record = get_store().get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        body = request.get_json(silent=True) or {}
        source = body.get("source", "")
        environment = body.get("environment", "unknown")
        ref = body.get("ref")
        try:
            prov_module.set_provenance(record, source, environment, ref)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"provenance": prov_module.get_provenance(record)}), 200

    @bp.route("/requests/<req_id>/provenance", methods=["DELETE"])
    def delete_provenance_route(req_id):
        record = get_store().get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        prov_module.clear_provenance(record)
        return jsonify({"status": "cleared"}), 200

    app.register_blueprint(bp)
