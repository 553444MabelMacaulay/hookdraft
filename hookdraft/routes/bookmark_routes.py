"""Flask routes for bookmark management."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify

from hookdraft import bookmarks as bm
from hookdraft.storage import RequestStore


def get_store(app: Flask) -> RequestStore:
    return app.config["STORE"]


def register_bookmark_routes(app: Flask) -> None:
    bp = Blueprint("bookmarks", __name__)

    @bp.post("/requests/<req_id>/bookmark")
    def bookmark_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        bm.bookmark_record(record)
        store.save(record)
        return jsonify({"id": req_id, "bookmarked": True}), 200

    @bp.delete("/requests/<req_id>/bookmark")
    def unbookmark_request(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        bm.unbookmark_record(record)
        store.save(record)
        return jsonify({"id": req_id, "bookmarked": False}), 200

    @bp.get("/requests/<req_id>/bookmark")
    def bookmark_status(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": req_id, "bookmarked": bm.is_bookmarked(record)}), 200

    @bp.get("/bookmarks")
    def list_bookmarks():
        store = get_store(app)
        records = bm.filter_bookmarked(store.all())
        return jsonify([r.to_dict() for r in records]), 200

    app.register_blueprint(bp)
