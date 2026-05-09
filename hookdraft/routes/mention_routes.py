"""HTTP routes for mention management on webhook request records."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import mentions as mention_lib


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_mention_routes(app):
    bp = Blueprint("mentions", __name__)

    @bp.route("/requests/<req_id>/mentions", methods=["GET"])
    def list_mentions(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"mentions": mention_lib.get_mentions(record.to_dict())}), 200

    @bp.route("/requests/<req_id>/mentions", methods=["POST"])
    def add_mention(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        data = request.get_json(silent=True) or {}
        handle = data.get("handle", "")
        try:
            d = record.to_dict()
            mention_lib.add_mention(d, handle)
            record.__dict__.update({"_mentions": d.get("mentions", [])})
            record.to_dict = lambda: {**record.__dict__, "mentions": d["mentions"]}
            store._records[req_id] = record
            return jsonify({"mentions": d["mentions"]}), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.route("/requests/<req_id>/mentions/<handle>", methods=["DELETE"])
    def remove_mention(req_id, handle):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        try:
            d = record.to_dict()
            mention_lib.remove_mention(d, handle)
            store._records[req_id] = record
            return jsonify({"mentions": d.get("mentions", [])}), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    app.register_blueprint(bp)
