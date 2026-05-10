"""Flask routes for record rating management."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify, request

from hookdraft import rating as rating_mod


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_rating_routes(app: Flask) -> None:
    bp = Blueprint("rating", __name__)

    @bp.route("/requests/<req_id>/rating", methods=["GET"])
    def get_rating_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        value = rating_mod.get_rating(record.to_dict())
        return jsonify({"rating": value}), 200

    @bp.route("/requests/<req_id>/rating", methods=["PUT"])
    def set_rating_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        stars = body.get("stars")
        if stars is None:
            return jsonify({"error": "'stars' field required"}), 400
        try:
            rating_mod.set_rating(record.meta, int(stars))
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"rating": rating_mod.get_rating(record.meta)}), 200

    @bp.route("/requests/<req_id>/rating", methods=["DELETE"])
    def delete_rating_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        rating_mod.clear_rating(record.meta)
        store.save(record)
        return jsonify({"rating": None}), 200

    app.register_blueprint(bp)
