"""HTTP routes for the narration feature."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft.narration import (
    clear_narration,
    get_narration,
    has_narration,
    set_narration,
)
from hookdraft.storage import RequestStore


def get_store() -> RequestStore:  # pragma: no cover – overridden in tests
    from hookdraft.app import get_store as _gs

    return _gs()


def register_narration_routes(app) -> None:  # noqa: ANN001
    bp = Blueprint("narration", __name__)

    @bp.route("/requests/<req_id>/narration", methods=["GET"])
    def get_narration_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        if not has_narration(record):
            return jsonify({"narration": None}), 200
        return jsonify({"narration": get_narration(record)}), 200

    @bp.route("/requests/<req_id>/narration", methods=["PUT"])
    def set_narration_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        text = body.get("text", "")
        author = body.get("author")
        try:
            set_narration(record, text, author=author)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"narration": get_narration(record)}), 200

    @bp.route("/requests/<req_id>/narration", methods=["DELETE"])
    def delete_narration_route(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        clear_narration(record)
        store.save(record)
        return jsonify({"narration": None}), 200

    app.register_blueprint(bp)
