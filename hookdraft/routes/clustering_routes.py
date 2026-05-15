"""HTTP routes for clustering operations."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app

from hookdraft import clustering as cl


def get_store():
    return current_app.config["store"]


def register_clustering_routes(app):
    bp = Blueprint("clustering", __name__)

    @bp.route("/requests/<req_id>/clusters", methods=["GET"])
    def list_clusters(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        return jsonify({"clusters": cl.get_clusters(record.to_dict())}), 200

    @bp.route("/requests/<req_id>/clusters", methods=["POST"])
    def add_cluster(req_id):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        body = request.get_json(silent=True) or {}
        name = body.get("name", "")
        try:
            cl.add_to_cluster(record.meta, name)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"clusters": cl.get_clusters(record.meta)}), 200

    @bp.route("/requests/<req_id>/clusters/<cluster_name>", methods=["DELETE"])
    def remove_cluster(req_id, cluster_name):
        store = get_store()
        record = store.get(req_id)
        if record is None:
            return jsonify({"error": "not found"}), 404
        try:
            cl.remove_from_cluster(record.meta, cluster_name)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(record)
        return jsonify({"clusters": cl.get_clusters(record.meta)}), 200

    @bp.route("/clusters/<cluster_name>/requests", methods=["GET"])
    def requests_in_cluster(cluster_name):
        store = get_store()
        all_records = store.all()
        try:
            matched = cl.filter_by_cluster(
                [r.meta for r in all_records], cluster_name
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        ids = [r["id"] for r in matched if "id" in r]
        return jsonify({"cluster": cluster_name, "request_ids": ids}), 200

    app.register_blueprint(bp)
