from flask import Blueprint, jsonify, request

from hookdraft.storage import RequestStore
from hookdraft.timeline import add_event, get_events, clear_events, has_events


def get_store(app) -> RequestStore:
    return app.config["STORE"]


def register_timeline_routes(app) -> None:
    bp = Blueprint("timeline", __name__)

    @bp.route("/requests/<req_id>/timeline", methods=["GET"])
    def list_events(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": req_id, "events": get_events(record)}), 200

    @bp.route("/requests/<req_id>/timeline", methods=["POST"])
    def add_event_route(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        name = body.get("name", "")
        detail = body.get("detail")
        timestamp = body.get("timestamp")
        try:
            event = add_event(record, name, detail=detail, timestamp=timestamp)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(event), 201

    @bp.route("/requests/<req_id>/timeline", methods=["DELETE"])
    def clear_events_route(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        clear_events(record)
        return jsonify({"cleared": True}), 200

    app.register_blueprint(bp)
