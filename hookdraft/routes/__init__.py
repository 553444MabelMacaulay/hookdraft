"""Register all route blueprints onto the Flask app."""

from hookdraft.routes.diff_routes import register_diff_routes
from hookdraft.routes.replay_routes import register_replay_routes
from hookdraft.routes.export_routes import register_export_routes
from hookdraft.routes.search_routes import register_search_routes
from hookdraft.routes.stats_routes import register_stats_routes
from hookdraft.routes.tag_routes import register_tag_routes
from hookdraft.routes.notes_routes import register_notes_routes
from hookdraft.routes.pin_routes import register_pin_routes
from hookdraft.routes.bookmark_routes import register_bookmark_routes
from hookdraft.routes.label_routes import register_label_routes


def register_all_routes(app):
    register_diff_routes(app)
    register_replay_routes(app)
    register_export_routes(app)
    register_search_routes(app)
    register_stats_routes(app)
    register_tag_routes(app)
    register_notes_routes(app)
    register_pin_routes(app)
    register_bookmark_routes(app)
    register_label_routes(app)
