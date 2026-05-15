"""HTTP routes for workflow state management."""

from flask import Blueprint, jsonify, request

from hookdraft.workflow import (
    clear_workflow_state,
    get_workflow_actor,
    get_workflow_note,
    get_workflow_state,
    set_workflow_state,
)


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_workflow_routes(app):
    bp = Blueprint("workflow", __name__)

    @bp.route("/requests/<req_id>/workflow", methods=["GET"])
    def get_workflow_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "state": get_workflow_state(record.data),
            "actor": get_workflow_actor(record.data),
            "note": get_workflow_note(record.data),
        }), 200

    @bp.route("/requests/<req_id>/workflow", methods=["PUT"])
    def set_workflow_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        state = body.get("state")
        if not state:
            return jsonify({"error": "'state' is required"}), 400
        try:
            set_workflow_state(
                record.data,
                state,
                actor=body.get("actor"),
                note=body.get("note"),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({
            "state": get_workflow_state(record.data),
            "actor": get_workflow_actor(record.data),
            "note": get_workflow_note(record.data),
        }), 200

    @bp.route("/requests/<req_id>/workflow", methods=["DELETE"])
    def delete_workflow_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        clear_workflow_state(record.data)
        store.save(record)
        return jsonify({"cleared": True}), 200

    app.register_blueprint(bp)
