"""HTTP routes for managing per-request routing rules."""

from flask import Blueprint, jsonify, request, current_app

from hookdraft.routing import set_route, remove_route, get_routes, match_route


def get_store():
    return current_app.config["store"]


def _get_record_or_404(store, req_id):
    """Fetch a record by ID, returning (record, None) or (None, error_response)."""
    record = store.get(req_id)
    if record is None:
        return None, (jsonify({"error": "not found"}), 404)
    return record, None


def register_routing_routes(app):
    bp = Blueprint("routing", __name__)

    @bp.route("/requests/<req_id>/routes", methods=["GET"])
    def list_routes(req_id):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        return jsonify(get_routes(record.to_dict())), 200

    @bp.route("/requests/<req_id>/routes", methods=["POST"])
    def add_route(req_id):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        body = request.get_json(silent=True) or {}
        name = body.get("name", "")
        pattern = body.get("pattern", "")
        method = body.get("method", "*")
        try:
            d = record.to_dict()
            set_route(d, name, pattern, method)
            record._meta = d.get("routing", {})
            record.__dict__.update({"routing": d["routing"]})
            store.save(record)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(get_routes(record.__dict__)), 201

    @bp.route("/requests/<req_id>/routes/<name>", methods=["DELETE"])
    def delete_route(req_id, name):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        d = record.to_dict()
        remove_route(d, name)
        record.__dict__.update({"routing": d.get("routing", {})})
        store.save(record)
        return "", 204

    @bp.route("/requests/<req_id>/routes/match", methods=["GET"])
    def match_route_view(req_id):
        store = get_store()
        record, err = _get_record_or_404(store, req_id)
        if err:
            return err
        matched = match_route(record.to_dict())
        return jsonify({"matched": matched}), 200

    app.register_blueprint(bp)
