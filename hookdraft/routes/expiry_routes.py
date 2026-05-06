from flask import Blueprint, jsonify, request, current_app
from hookdraft.storage import RequestStore
from hookdraft import expiry as expiry_module

bp = Blueprint("expiry", __name__)


def get_store() -> RequestStore:
    return current_app.config["store"]


def register_expiry_routes(app):
    app.register_blueprint(bp)


@bp.route("/requests/<request_id>/expiry", methods=["GET"])
def get_expiry_route(request_id: str):
    store = get_store()
    record = store.get(request_id)
    if record is None:
        return jsonify({"error": "not found"}), 404
    ts = expiry_module.get_expiry(record)
    expired = expiry_module.is_expired(record)
    return jsonify({"expires_at": ts, "expired": expired}), 200


@bp.route("/requests/<request_id>/expiry", methods=["PUT"])
def set_expiry_route(request_id: str):
    store = get_store()
    record = store.get(request_id)
    if record is None:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    ttl = body.get("ttl")
    if ttl is None:
        return jsonify({"error": "ttl is required"}), 400
    try:
        ttl = int(ttl)
    except (TypeError, ValueError):
        return jsonify({"error": "ttl must be an integer"}), 400
    try:
        expiry_module.set_expiry(record, ttl)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    store.save(record)
    return jsonify({"expires_at": expiry_module.get_expiry(record)}), 200


@bp.route("/requests/<request_id>/expiry", methods=["DELETE"])
def delete_expiry_route(request_id: str):
    store = get_store()
    record = store.get(request_id)
    if record is None:
        return jsonify({"error": "not found"}), 404
    expiry_module.clear_expiry(record)
    store.save(record)
    return jsonify({"expires_at": None}), 200


@bp.route("/requests/expired", methods=["GET"])
def list_expired_route():
    store = get_store()
    records = expiry_module.filter_expired(store.all())
    return jsonify([r.to_dict() for r in records]), 200
