"""Routes for managing severity levels on webhook request records."""

from flask import Blueprint, jsonify, request

from hookdraft import severity as sev_module

bp = Blueprint("severity", __name__)


def get_store():
    from flask import current_app
    return current_app.config["store"]


def register_severity_routes(app):
    app.register_blueprint(bp)


@bp.route("/requests/<request_id>/severity", methods=["GET"])
def get_severity_route(request_id):
    store = get_store()
    record = store.get(request_id)
    if record is None:
        return jsonify({"error": "Not found"}), 404
    level = sev_module.get_severity(record)
    return jsonify({"id": request_id, "severity": level})


@bp.route("/requests/<request_id>/severity", methods=["PUT"])
def set_severity_route(request_id):
    store = get_store()
    record = store.get(request_id)
    if record is None:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    level = data.get("level", "")
    try:
        sev_module.set_severity(record, level)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    store.save(record)
    return jsonify({"id": request_id, "severity": sev_module.get_severity(record)})


@bp.route("/requests/<request_id>/severity", methods=["DELETE"])
def delete_severity_route(request_id):
    store = get_store()
    record = store.get(request_id)
    if record is None:
        return jsonify({"error": "Not found"}), 404
    sev_module.clear_severity(record)
    store.save(record)
    return jsonify({"id": request_id, "severity": None})


@bp.route("/requests/severity/<level>", methods=["GET"])
def list_by_severity(level):
    store = get_store()
    try:
        matched = sev_module.filter_by_severity(store.all(), level)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify([r.to_dict() for r in matched])
