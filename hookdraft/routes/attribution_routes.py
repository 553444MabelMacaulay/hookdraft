"""HTTP routes for attribution management."""

from flask import Blueprint, jsonify, request

from hookdraft import attribution as attr_mod

bp = Blueprint("attribution", __name__)


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_attribution_routes(app):
    app.register_blueprint(bp)


@bp.route("/requests/<req_id>/attribution", methods=["GET"])
def get_attribution_route(req_id):
    store = get_store()
    record = store.get(req_id)
    if record is None:
        return jsonify({"error": "not found"}), 404
    data = attr_mod.get_attribution(record)
    if data is None:
        return jsonify({"attribution": None}), 200
    return jsonify({"attribution": data}), 200


@bp.route("/requests/<req_id>/attribution", methods=["PUT"])
def set_attribution_route(req_id):
    store = get_store()
    record = store.get(req_id)
    if record is None:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    source = body.get("source", "")
    actor = body.get("actor")
    note = body.get("note")
    try:
        attr_mod.set_attribution(record, source, actor=actor, note=note)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    store.save(record)
    return jsonify({"attribution": attr_mod.get_attribution(record)}), 200


@bp.route("/requests/<req_id>/attribution", methods=["DELETE"])
def delete_attribution_route(req_id):
    store = get_store()
    record = store.get(req_id)
    if record is None:
        return jsonify({"error": "not found"}), 404
    attr_mod.clear_attribution(record)
    store.save(record)
    return jsonify({"attribution": None}), 200
