"""HTTP routes for managing trace context on stored webhook requests."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from hookdraft import tracing


def get_store():
    return current_app.config["REQUEST_STORE"]


def register_trace_routes(app):
    bp = Blueprint("trace", __name__)

    @bp.route("/requests/<req_id>/trace", methods=["GET"])
    def get_trace_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(tracing.get_trace(record)), 200

    @bp.route("/requests/<req_id>/trace", methods=["PUT"])
    def set_trace_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        trace_id = body.get("trace_id", "")
        if not trace_id or not trace_id.strip():
            return jsonify({"error": "trace_id is required"}), 400
        try:
            tracing.set_trace(
                record,
                trace_id,
                span_id=body.get("span_id"),
                parent_span_id=body.get("parent_span_id"),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify(tracing.get_trace(record)), 200

    @bp.route("/requests/<req_id>/trace", methods=["DELETE"])
    def delete_trace_route(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        tracing.clear_trace(record)
        store.save(record)
        return "", 204

    @bp.route("/requests/trace/<trace_id>", methods=["GET"])
    def search_by_trace_route(trace_id):
        store = get_store()
        matched = tracing.filter_by_trace_id(store.all(), trace_id)
        return jsonify([r.to_dict() for r in matched]), 200

    app.register_blueprint(bp)
