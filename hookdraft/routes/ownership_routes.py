"""HTTP routes for ownership management."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import ownership as own


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_ownership_routes(app):
    bp = Blueprint("ownership", __name__)

    @bp.route("/requests/<req_id>/ownership", methods=["GET"])
    def get_ownership_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "owner": own.get_owner(record),
            "team": own.get_team(record),
        })

    @bp.route("/requests/<req_id>/ownership", methods=["PUT"])
    def set_ownership_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        owner = body.get("owner", "")
        team = body.get("team") or None
        try:
            own.set_owner(record, owner, team=team)
        except (ValueError, TypeError) as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({
            "owner": own.get_owner(record),
            "team": own.get_team(record),
        })

    @bp.route("/requests/<req_id>/ownership", methods=["DELETE"])
    def delete_ownership_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        own.clear_owner(record)
        store.save(record)
        return jsonify({"ok": True})

    app.register_blueprint(bp)
