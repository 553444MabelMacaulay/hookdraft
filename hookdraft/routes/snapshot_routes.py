"""HTTP routes for snapshot management."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify, request

from hookdraft import snapshot as snap
from hookdraft.storage import RequestStore


def get_store(app: Flask) -> RequestStore:
    return app.config["STORE"]


def register_snapshot_routes(app: Flask) -> None:
    bp = Blueprint("snapshots", __name__)

    @bp.get("/requests/<req_id>/snapshots")
    def list_snapshots(req_id: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"snapshots": snap.list_snapshots(record)}), 200

    @bp.post("/requests/<req_id>/snapshots/<name>")
    def save_snapshot(req_id: str, name: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        try:
            snap.save_snapshot(record, name)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"snapshot": name, "body": snap.get_snapshot(record, name)}), 201

    @bp.get("/requests/<req_id>/snapshots/<name>")
    def get_snapshot(req_id: str, name: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        if not snap.has_snapshot(record, name):
            return jsonify({"error": "snapshot not found"}), 404
        return jsonify({"snapshot": name, "body": snap.get_snapshot(record, name)}), 200

    @bp.delete("/requests/<req_id>/snapshots/<name>")
    def delete_snapshot(req_id: str, name: str):
        store = get_store(app)
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        removed = snap.delete_snapshot(record, name)
        if not removed:
            return jsonify({"error": "snapshot not found"}), 404
        store.save(record)
        return jsonify({"deleted": name}), 200

    app.register_blueprint(bp)
