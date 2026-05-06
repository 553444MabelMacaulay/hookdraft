"""Flask routes for managing record labels."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import labels as label_lib


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_label_routes(app):
    bp = Blueprint("labels", __name__)

    @bp.route("/requests/<req_id>/labels", methods=["GET"])
    def list_labels(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(label_lib.get_labels(record.to_dict())), 200

    @bp.route("/requests/<req_id>/labels", methods=["POST"])
    def add_label(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(force=True, silent=True) or {}
        name = (body.get("name") or "").strip()
        colour = (body.get("colour") or "grey").strip()
        if not name:
            return jsonify({"error": "'name' is required"}), 400
        try:
            label_lib.set_label(record.__dict__, name, colour)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify(label_lib.get_labels(record.__dict__)), 200

    @bp.route("/requests/<req_id>/labels/<label_name>", methods=["DELETE"])
    def delete_label(req_id, label_name):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        label_lib.remove_label(record.__dict__, label_name)
        store.save(record)
        return jsonify(label_lib.get_labels(record.__dict__)), 200

    @bp.route("/labels", methods=["GET"])
    def search_by_label():
        store = get_store()
        name = request.args.get("name", "").strip()
        colour = request.args.get("colour", "").strip()
        all_records = [r.__dict__ for r in store.all()]
        if name:
            all_records = label_lib.filter_by_label(all_records, name)
        if colour:
            all_records = label_lib.filter_by_label_colour(all_records, colour)
        return jsonify(all_records), 200

    app.register_blueprint(bp)
