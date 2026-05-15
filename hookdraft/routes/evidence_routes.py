from flask import Blueprint, jsonify, request

from hookdraft import evidence as ev


def get_store():
    from hookdraft.app import get_store as _gs
    return _gs()


def register_evidence_routes(app):
    bp = Blueprint("evidence", __name__)

    @bp.route("/requests/<req_id>/evidence", methods=["GET"])
    def list_evidence(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"evidence": ev.get_evidence(record.to_dict())}), 200

    @bp.route("/requests/<req_id>/evidence", methods=["POST"])
    def add_evidence(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        data = request.get_json(silent=True) or {}
        kind = data.get("kind", "")
        content = data.get("content", "")
        label = data.get("label", "")
        try:
            eid = ev.add_evidence(record.meta, kind, content, label)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"id": eid}), 201

    @bp.route("/requests/<req_id>/evidence/<evidence_id>", methods=["DELETE"])
    def delete_evidence(req_id, evidence_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        removed = ev.remove_evidence(record.meta, evidence_id)
        if not removed:
            return jsonify({"error": "evidence item not found"}), 404
        store.save(record)
        return "", 204

    app.register_blueprint(bp)
