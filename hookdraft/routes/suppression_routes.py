"""HTTP routes for suppressing / unsuppressing request records."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from hookdraft.storage import RequestStore
from hookdraft.suppression import (
    get_suppression_reason,
    is_suppressed,
    suppress_record,
    unsuppress_record,
)


def get_store() -> RequestStore:  # pragma: no cover – replaced in tests
    from hookdraft.app import get_store as _gs

    return _gs()


def register_suppression_routes(app, store: RequestStore | None = None) -> Blueprint:
    bp = Blueprint("suppression", __name__)

    def _store() -> RequestStore:
        return store if store is not None else get_store()

    @bp.route("/requests/<request_id>/suppression", methods=["GET"])
    def suppression_status(request_id: str):
        record = _store().get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(
            {
                "suppressed": is_suppressed(record),
                "reason": get_suppression_reason(record),
            }
        )

    @bp.route("/requests/<request_id>/suppression", methods=["POST"])
    def suppress_request(request_id: str):
        record = _store().get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        reason = body.get("reason", "")
        suppress_record(record, reason=reason)
        return jsonify(
            {
                "suppressed": True,
                "reason": get_suppression_reason(record),
            }
        )

    @bp.route("/requests/<request_id>/suppression", methods=["DELETE"])
    def unsuppress_request(request_id: str):
        record = _store().get(request_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        unsuppress_record(record)
        return jsonify({"suppressed": False, "reason": None})

    app.register_blueprint(bp)
    return bp
