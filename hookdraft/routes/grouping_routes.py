"""HTTP routes for grouping / bucketing webhook requests."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from hookdraft.grouping import group_records, group_summary


def get_store():
    return current_app.config["store"]


def register_grouping_routes(app):
    bp = Blueprint("grouping", __name__)

    @bp.route("/requests/group/<field>", methods=["GET"])
    def group_by_field(field: str):
        """Group all stored requests by *field*.

        Query params:
          summary=1  — return counts only (default: full records)
        """
        store = get_store()
        records = store.all()
        summary_only = request.args.get("summary", "0") in ("1", "true", "yes")

        try:
            if summary_only:
                result = group_summary(records, field)
                return jsonify({"field": field, "groups": result})
            else:
                grouped = group_records(records, field)
                serialised = {
                    key: [r.to_dict() for r in recs]
                    for key, recs in grouped.items()
                }
                return jsonify({"field": field, "groups": serialised})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    app.register_blueprint(bp)
