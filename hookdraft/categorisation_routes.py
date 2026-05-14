from flask import Blueprint, jsonify, request
from hookdraft.storage import RequestStore
from hookdraft.categorisation import (
    set_category,
    clear_category,
    get_category,
    get_category_name,
    get_category_colour,
    filter_by_category,
)

bp = Blueprint("categorisation", __name__)


def get_store() -> RequestStore:  # pragma: no cover
    from hookdraft.app import get_store as _gs
    return _gs()


def register_categorisation_routes(app, store_fn=None):
    _get_store = store_fn or get_store

    @app.route("/requests/<req_id>/category", methods=["GET"])
    def get_category_route(req_id):
        store = _get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        cat = get_category(record)
        if cat is None:
            return jsonify({"category": None}), 200
        return jsonify({
            "category": {
                "name": get_category_name(record),
                "colour": get_category_colour(record),
            }
        }), 200

    @app.route("/requests/<req_id>/category", methods=["PUT"])
    def set_category_route(req_id):
        store = _get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        name = body.get("name", "")
        colour = body.get("colour", None)
        try:
            kwargs = {"colour": colour} if colour is not None else {}
            set_category(record, name, **kwargs)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({
            "category": {
                "name": get_category_name(record),
                "colour": get_category_colour(record),
            }
        }), 200

    @app.route("/requests/<req_id>/category", methods=["DELETE"])
    def delete_category_route(req_id):
        store = _get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        clear_category(record)
        store.save(record)
        return jsonify({"category": None}), 200
