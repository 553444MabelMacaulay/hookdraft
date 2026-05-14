"""HTTP routes for managing request record aliases."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft import aliasing


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def _get_record_or_404(store, req_id):
    """Fetch a record by ID, returning (record, None) or (None, error_response)."""
    record = store.get(req_id)
    if record is None:
        return None, (jsonify({"error": "not found"}), 404)
    return record, None


def register_alias_routes(app):
    bp = Blueprint("alias", __name__)

    @bp.route("/requests/<req_id>/alias", methods=["GET"])
    def get_alias_route(req_id):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        alias = aliasing.get_alias(record.to_dict())
        return jsonify({"alias": alias}), 200

    @bp.route("/requests/<req_id>/alias", methods=["PUT"])
    def set_alias_route(req_id):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        body = request.get_json(silent=True) or {}
        alias = body.get("alias", "")
        try:
            aliasing.set_alias(record.meta, alias)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"alias": aliasing.get_alias(record.meta)}), 200

    @bp.route("/requests/<req_id>/alias", methods=["DELETE"])
    def delete_alias_route(req_id):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        aliasing.clear_alias(record.meta)
        store.save(record)
        return jsonify({"alias": None}), 200

    @bp.route("/requests/alias/<alias>", methods=["GET"])
    def lookup_by_alias(alias):
        store = get_store()
        records = [r.to_dict() for r in store.all()]
        match = aliasing.find_by_alias(records, alias)
        if match is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(match), 200

    app.register_blueprint(bp)
