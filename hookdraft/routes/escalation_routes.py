"""HTTP routes for escalation management."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import escalation as esc_module


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_escalation_routes(app):
    bp = Blueprint("escalation", __name__)

    @bp.route("/requests/<req_id>/escalation", methods=["GET"])
    def get_escalation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        esc = esc_module.get_escalation(record.to_dict())
        if esc is None:
            return jsonify({"escalated": False}), 200
        return jsonify({"escalated": True, **esc}), 200

    @bp.route("/requests/<req_id>/escalation", methods=["PUT"])
    def set_escalation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        tier = body.get("tier", "")
        reason = body.get("reason", "")
        try:
            d = record.to_dict()
            esc_module.escalate_record(d, tier, reason)
            record.__dict__.update(d)
            store.save(record)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"escalated": True, **esc_module.get_escalation(d)}), 200

    @bp.route("/requests/<req_id>/escalation", methods=["DELETE"])
    def delete_escalation_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        d = record.to_dict()
        esc_module.deescalate_record(d)
        record.__dict__.update(d)
        store.save(record)
        return jsonify({"escalated": False}), 200

    app.register_blueprint(bp)
