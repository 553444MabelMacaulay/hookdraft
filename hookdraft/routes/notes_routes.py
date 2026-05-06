"""Flask blueprint for per-request notes endpoints."""

from flask import Blueprint, jsonify, request, current_app

from hookdraft import notes as notes_mod


def get_store():
    return current_app.config["store"]


def register_notes_routes(app):
    bp = Blueprint("notes", __name__)

    @bp.route("/requests/<request_id>/note", methods=["GET"])
    def get_note_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        note = notes_mod.get_note(record.to_dict())
        return jsonify({"id": request_id, "note": note})

    @bp.route("/requests/<request_id>/note", methods=["PUT"])
    def set_note_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        note_text = body.get("note", "")
        try:
            rec_dict = record.to_dict()
            notes_mod.set_note(rec_dict, note_text)
            record.note = rec_dict["note"]
            store.save(record)
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"id": request_id, "note": record.note})

    @bp.route("/requests/<request_id>/note", methods=["DELETE"])
    def delete_note_route(request_id):
        store = get_store()
        record = store.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        record.note = None
        store.save(record)
        return jsonify({"id": request_id, "note": None})

    @bp.route("/requests/search/note", methods=["GET"])
    def search_by_note():
        substring = request.args.get("q", "")
        if not substring:
            return jsonify({"error": "query param 'q' is required"}), 400
        store = get_store()
        all_records = store.all()
        try:
            matched = notes_mod.filter_by_note(
                [r.to_dict() for r in all_records], substring
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(matched)

    app.register_blueprint(bp)
