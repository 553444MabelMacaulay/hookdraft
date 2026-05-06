"""Routes for tagging webhook requests."""
from flask import Blueprint, jsonify, request, abort
from hookdraft.storage import RequestStore
from hookdraft.tagging import add_tag, remove_tag, all_tags


def get_store() -> RequestStore:  # pragma: no cover
    from hookdraft.app import get_store as _gs
    return _gs()


def register_tag_routes(app, store_fn=None):
    bp = Blueprint("tags", __name__)
    _store_fn = store_fn or get_store

    @bp.route("/requests/<request_id>/tags", methods=["GET"])
    def list_tags(request_id):
        store = _store_fn()
        record = store.get(request_id)
        if record is None:
            abort(404, description="Request not found")
        return jsonify({"id": request_id, "tags": record.tags})

    @bp.route("/requests/<request_id>/tags", methods=["POST"])
    def add_tag_route(request_id):
        store = _store_fn()
        record = store.get(request_id)
        if record is None:
            abort(404, description="Request not found")
        body = request.get_json(silent=True) or {}
        tag = body.get("tag", "")
        try:
            record.tags = add_tag(record.tags, tag)
        except ValueError as exc:
            abort(400, description=str(exc))
        store.save(record)
        return jsonify({"id": request_id, "tags": record.tags}), 201

    @bp.route("/requests/<request_id>/tags/<tag>", methods=["DELETE"])
    def remove_tag_route(request_id, tag):
        store = _store_fn()
        record = store.get(request_id)
        if record is None:
            abort(404, description="Request not found")
        record.tags = remove_tag(record.tags, tag)
        store.save(record)
        return jsonify({"id": request_id, "tags": record.tags})

    @bp.route("/tags", methods=["GET"])
    def list_all_tags():
        store = _store_fn()
        return jsonify({"tags": all_tags(store.all())})

    app.register_blueprint(bp)
