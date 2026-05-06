from flask import Blueprint, request, jsonify
from hookdraft.storage import RequestStore

_store: RequestStore | None = None


def get_store() -> RequestStore:
    global _store
    if _store is None:
        _store = RequestStore()
    return _store


def register_search_routes(app, store: RequestStore | None = None):
    global _store
    if store is not None:
        _store = store

    bp = Blueprint("search", __name__)

    @bp.route("/requests/search", methods=["GET"])
    def search_requests():
        """Search stored requests by method, path, header key/value, or body substring."""
        method = request.args.get("method", "").upper() or None
        path_contains = request.args.get("path", "") or None
        header_key = request.args.get("header_key", "") or None
        header_value = request.args.get("header_value", "") or None
        body_contains = request.args.get("body", "") or None

        try:
            limit = int(request.args.get("limit", 50))
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400

        results = get_store().search(
            method=method,
            path_contains=path_contains,
            header_key=header_key,
            header_value=header_value,
            body_contains=body_contains,
            limit=limit,
        )

        return jsonify([r.to_dict() for r in results]), 200

    app.register_blueprint(bp)
