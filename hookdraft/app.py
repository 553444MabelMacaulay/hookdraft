"""Flask application factory and webhook catch-all route."""

from pathlib import Path

from flask import Flask, jsonify, request

from hookdraft.storage import RequestRecord, RequestStore

_store: RequestStore | None = None


def get_store() -> RequestStore:
    if _store is None:
        raise RuntimeError("Store not initialised — call create_app() first.")
    return _store


def create_app(persist_path: Path | None = None, max_records: int = 500) -> Flask:
    global _store
    _store = RequestStore(persist_path=persist_path, max_records=max_records)

    app = Flask(__name__)

    @app.route("/hooks/<path:hook_path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def catch_webhook(hook_path: str):
        record = RequestRecord(
            method=request.method,
            path=f"/{hook_path}",
            headers=dict(request.headers),
            body=request.get_data(),
            query=request.query_string.decode(),
        )
        _store.save(record)
        return jsonify({"id": record.id, "status": "received"}), 200

    @app.route("/api/requests", methods=["GET"])
    def list_requests():
        limit = min(int(request.args.get("limit", 50)), 200)
        records = _store.all()[:limit]
        return jsonify([r.to_dict() for r in records])

    @app.route("/api/requests/<record_id>", methods=["GET"])
    def get_request(record_id: str):
        record = _store.get(record_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(record.to_dict())

    @app.route("/api/requests", methods=["DELETE"])
    def clear_requests():
        count = _store.clear()
        return jsonify({"deleted": count})

    return app
