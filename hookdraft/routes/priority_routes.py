"""HTTP routes for request priority management."""

from flask import Blueprint, jsonify, request

from hookdraft.priority import (
    set_priority,
    clear_priority,
    get_priority,
    LEVELS,
)


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_priority_routes(app):
    bp = Blueprint("priority", __name__)

    @bp.route("/requests/<request_id>/priority", methods=["GET"])
    def get_priority_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"priority": get_priority(record)})

    @bp.route("/requests/<request_id>/priority", methods=["PUT"])
    def set_priority_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        level = body.get("level", "")
        if not level:
            return jsonify({"error": "'level' is required"}), 400
        try:
            set_priority(record, level)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"priority": get_priority(record)})

    @bp.route("/requests/<request_id>/priority", methods=["DELETE"])
    def delete_priority_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        clear_priority(record)
        store.save(record)
        return jsonify({"priority": None})

    @bp.route("/priority/levels", methods=["GET"])
    def list_levels():
        return jsonify({"levels": list(LEVELS)})

    app.register_blueprint(bp)
