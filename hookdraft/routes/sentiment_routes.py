"""HTTP routes for managing sentiment on stored request records."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import sentiment as _sentiment


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_sentiment_routes(app):
    bp = Blueprint("sentiment", __name__)

    @bp.route("/requests/<req_id>/sentiment", methods=["GET"])
    def get_sentiment_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        data = _sentiment.get_sentiment(record.to_dict())
        return jsonify({"sentiment": data}), 200

    @bp.route("/requests/<req_id>/sentiment", methods=["PUT"])
    def set_sentiment_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        value = body.get("sentiment", "")
        note = body.get("note")
        try:
            _sentiment.set_sentiment(record.extra, value, note)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"sentiment": _sentiment.get_sentiment(record.extra)}), 200

    @bp.route("/requests/<req_id>/sentiment", methods=["DELETE"])
    def delete_sentiment_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        _sentiment.clear_sentiment(record.extra)
        store.save(record)
        return jsonify({"sentiment": None}), 200

    app.register_blueprint(bp)
