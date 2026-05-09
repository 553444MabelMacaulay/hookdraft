from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import annotation as ann


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_annotation_routes(app):
    bp = Blueprint("annotations", __name__)

    @bp.route("/requests/<req_id>/annotations", methods=["GET"])
    def list_annotations(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"annotations": ann.get_annotations(record.to_dict())}), 200

    @bp.route("/requests/<req_id>/annotations", methods=["POST"])
    def add_annotation(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        body = request.get_json(silent=True) or {}
        text = body.get("text", "")
        author = body.get("author", "anonymous")
        try:
            entry = ann.add_annotation(record.__dict__, text, author)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify(entry), 201

    @bp.route("/requests/<req_id>/annotations/<int:index>", methods=["DELETE"])
    def delete_annotation(req_id, index):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "Not found"}), 404
        try:
            ann.remove_annotation(record.__dict__, index)
        except IndexError as exc:
            return jsonify({"error": str(exc)}), 404
        store.save(record)
        return "", 204

    app.register_blueprint(bp)
