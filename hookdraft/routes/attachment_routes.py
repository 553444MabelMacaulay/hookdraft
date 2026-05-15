"""HTTP routes for managing record attachments."""
from __future__ import annotations

import base64

from flask import Blueprint, current_app, jsonify, request

from hookdraft import attachment as att_mod


def get_store():
    return current_app.config["store"]


def register_attachment_routes(app):
    bp = Blueprint("attachments", __name__)

    @bp.get("/requests/<req_id>/attachments")
    def list_attachments(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        items = att_mod.get_attachments(record.to_dict())
        # Strip raw data from list view
        summary = [{k: v for k, v in a.items() if k != "data"} for a in items]
        return jsonify({"attachments": summary}), 200

    @bp.post("/requests/<req_id>/attachments")
    def add_attachment(req_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        name = body.get("name", "")
        mime_type = body.get("mime_type", "")
        raw = body.get("data", "")
        try:
            data = base64.b64decode(raw)
        except Exception:
            return jsonify({"error": "data must be valid base64"}), 400
        try:
            attachment_id = att_mod.add_attachment(record.extra, name, mime_type, data)
        except (ValueError, TypeError) as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"id": attachment_id}), 201

    @bp.get("/requests/<req_id>/attachments/<attachment_id>")
    def get_attachment(req_id: str, attachment_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        item = att_mod.get_attachment(record.extra, attachment_id)
        if item is None:
            return jsonify({"error": "attachment not found"}), 404
        return jsonify(item), 200

    @bp.delete("/requests/<req_id>/attachments/<attachment_id>")
    def delete_attachment(req_id: str, attachment_id: str):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        removed = att_mod.remove_attachment(record.extra, attachment_id)
        if not removed:
            return jsonify({"error": "attachment not found"}), 404
        store.save(record)
        return jsonify({"removed": True}), 200

    app.register_blueprint(bp)
