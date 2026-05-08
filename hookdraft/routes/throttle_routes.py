"""HTTP routes for managing per-request throttle policies."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify, request

from hookdraft.throttling import (
    clear_throttle,
    get_throttle,
    is_throttled,
    set_throttle,
)


def get_store(app: Flask):
    return app.config["REQUEST_STORE"]


def register_throttle_routes(app: Flask) -> None:
    bp = Blueprint("throttle", __name__)

    @bp.route("/requests/<req_id>/throttle", methods=["GET"])
    def get_throttle_route(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        policy = get_throttle(record.__dict__)
        if policy is None:
            return jsonify({"throttled": False}), 200
        return jsonify({"throttled": True, **policy}), 200

    @bp.route("/requests/<req_id>/throttle", methods=["PUT"])
    def set_throttle_route(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        rpm = body.get("rpm")
        action = body.get("action", "drop")
        burst = body.get("burst")
        if rpm is None:
            return jsonify({"error": "rpm is required"}), 400
        try:
            set_throttle(record.__dict__, rpm=rpm, action=action, burst=burst)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"throttled": True, **get_throttle(record.__dict__)}), 200

    @bp.route("/requests/<req_id>/throttle", methods=["DELETE"])
    def delete_throttle_route(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        clear_throttle(record.__dict__)
        store.save(record)
        return jsonify({"throttled": False}), 200

    app.register_blueprint(bp)
