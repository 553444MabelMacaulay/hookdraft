"""HTTP routes for lifecycle state management."""

from flask import Blueprint, jsonify, request

from hookdraft import lifecycle as lc


def get_store():
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_lifecycle_routes(app):
    bp = Blueprint("lifecycle", __name__)

    @bp.route("/requests/<req_id>/lifecycle", methods=["GET"])
    def get_lifecycle_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        state = lc.get_lifecycle_state(record.meta)
        if state is None:
            return jsonify({"lifecycle": None}), 200
        return jsonify({
            "lifecycle": {
                "state": state,
                "actor": lc.get_lifecycle_actor(record.meta),
                "note": lc.get_lifecycle_note(record.meta),
            }
        }), 200

    @bp.route("/requests/<req_id>/lifecycle", methods=["PUT"])
    def set_lifecycle_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        body = request.get_json(silent=True) or {}
        state = body.get("state", "")
        actor = body.get("actor")
        note = body.get("note")
        try:
            lc.set_lifecycle_state(record.meta, state, actor=actor, note=note)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"state": lc.get_lifecycle_state(record.meta)}), 200

    @bp.route("/requests/<req_id>/lifecycle", methods=["DELETE"])
    def delete_lifecycle_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        lc.clear_lifecycle_state(record.meta)
        store.save(record)
        return jsonify({"lifecycle": None}), 200

    app.register_blueprint(bp)
