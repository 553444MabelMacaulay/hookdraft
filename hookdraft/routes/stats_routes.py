from flask import Blueprint, jsonify

from hookdraft.stats import compute_stats
from hookdraft.storage import RequestStore


def get_store() -> RequestStore:  # pragma: no cover
    from hookdraft.app import get_store as _get_store
    return _get_store()


def register_stats_routes(app, store_fn=None):
    bp = Blueprint("stats", __name__)

    _store_fn = store_fn or get_store

    @bp.route("/stats", methods=["GET"])
    def request_stats():
        """Return aggregate statistics about all captured webhook requests."""
        store = _store_fn()
        records = store.all()
        stats = compute_stats(records)
        return jsonify(stats), 200

    app.register_blueprint(bp)
