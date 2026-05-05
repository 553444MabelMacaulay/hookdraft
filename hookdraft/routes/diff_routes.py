"""Routes for comparing two stored webhook requests."""

from flask import Blueprint, jsonify, abort
from hookdraft.diff import diff_payloads

diff_bp = Blueprint("diff", __name__)


def register_diff_routes(app, get_store_fn):
    """Register diff routes on the given Flask app."""

    @app.route("/requests/<id_a>/diff/<id_b>", methods=["GET"])
    def diff_requests(id_a, id_b):
        """Return a payload diff between two stored webhook requests."""
        store = get_store_fn()

        record_a = store.get(id_a)
        record_b = store.get(id_b)

        if record_a is None:
            abort(404, description=f"Request '{id_a}' not found.")
        if record_b is None:
            abort(404, description=f"Request '{id_b}' not found.")

        payload_a = record_a.body or ""
        payload_b = record_b.body or ""

        result = diff_payloads(payload_a, payload_b)

        return jsonify({
            "request_a": id_a,
            "request_b": id_b,
            "diff": result,
        })
