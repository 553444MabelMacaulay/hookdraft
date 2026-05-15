"""HTTP routes for managing webhook record subscriptions."""

from flask import Blueprint, jsonify, request, current_app

from hookdraft.subscription import (
    subscribe,
    unsubscribe,
    get_subscriptions,
    subscriber_count,
)


def get_store():
    return current_app.config["store"]


def register_subscription_routes(app):
    bp = Blueprint("subscriptions", __name__)

    @bp.route("/requests/<req_id>/subscriptions", methods=["GET"])
    def list_subscriptions(req_id):
        record = get_store().get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        subs = get_subscriptions(record.to_dict())
        return jsonify({"subscriptions": subs, "count": len(subs)}), 200

    @bp.route("/requests/<req_id>/subscriptions", methods=["POST"])
    def add_subscription(req_id):
        record = get_store().get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        subscriber = body.get("subscriber", "").strip()
        if not subscriber:
            return jsonify({"error": "subscriber is required"}), 400
        channel = body.get("channel")
        try:
            subscribe(record.meta, subscriber, channel=channel)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        get_store().save(record)
        return jsonify({"subscriptions": get_subscriptions(record.meta)}), 201

    @bp.route("/requests/<req_id>/subscriptions/<subscriber>", methods=["DELETE"])
    def remove_subscription(req_id, subscriber):
        record = get_store().get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        unsubscribe(record.meta, subscriber)
        get_store().save(record)
        return jsonify({"subscriptions": get_subscriptions(record.meta)}), 200

    app.register_blueprint(bp)
