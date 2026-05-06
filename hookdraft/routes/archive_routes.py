"""Routes for archiving and unarchiving webhook request records."""

from flask import Blueprint, jsonify
from hookdraft.storage import RequestStore
from hookdraft.archiving import archive_record, unarchive_record, is_archived


def get_store() -> RequestStore:  # pragma: no cover
    from hookdraft.app import get_store as _gs
    return _gs()


def register_archive_routes(app, store: RequestStore = None) -> None:
    bp = Blueprint("archive", __name__)
    _store = store

    def _get_store() -> RequestStore:
        return _store if _store is not None else get_store()

    @bp.route("/requests/<request_id>/archive", methods=["POST"])
    def archive_request(request_id: str):
        s = _get_store()
        record = s.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        archive_record(record)
        s.save(record)
        return jsonify({"id": record.id, "archived": True}), 200

    @bp.route("/requests/<request_id>/unarchive", methods=["POST"])
    def unarchive_request(request_id: str):
        s = _get_store()
        record = s.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        unarchive_record(record)
        s.save(record)
        return jsonify({"id": record.id, "archived": False}), 200

    @bp.route("/requests/<request_id>/archive", methods=["GET"])
    def archive_status(request_id: str):
        s = _get_store()
        record = s.get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": record.id, "archived": is_archived(record)}), 200

    @bp.route("/requests/archived", methods=["GET"])
    def list_archived():
        from hookdraft.archiving import filter_archived
        s = _get_store()
        records = filter_archived(s.all())
        return jsonify([r.to_dict() for r in records]), 200

    app.register_blueprint(bp)
