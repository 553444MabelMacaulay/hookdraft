import json
import csv
import io
from flask import Blueprint, Response, jsonify, current_app
from hookdraft.storage import RequestStore

export_bp = Blueprint("export", __name__)


def get_store() -> RequestStore:
    return current_app.config["STORE"]


def register_export_routes(app):
    app.register_blueprint(export_bp)


@export_bp.route("/requests/export/json", methods=["GET"])
def export_json():
    """Export all stored requests as a JSON file."""
    store = get_store()
    records = store.all()
    payload = [r.to_dict() for r in records]
    data = json.dumps(payload, indent=2)
    return Response(
        data,
        status=200,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=requests.json"},
    )


@export_bp.route("/requests/export/csv", methods=["GET"])
def export_csv():
    """Export all stored requests as a CSV file (flattened, top-level fields only)."""
    store = get_store()
    records = store.all()

    output = io.StringIO()
    fieldnames = ["id", "timestamp", "method", "path", "headers", "body"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for r in records:
        d = r.to_dict()
        d["headers"] = json.dumps(d.get("headers", {}))
        d["body"] = json.dumps(d.get("body")) if d.get("body") is not None else ""
        writer.writerow(d)

    csv_data = output.getvalue()
    return Response(
        csv_data,
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=requests.csv"},
    )
